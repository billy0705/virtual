from __future__ import annotations

import multiprocessing as mp
import queue
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Iterable

import duckdb
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from .models import (
    ROW_ID_COLUMN,
    SUPPORTED_CODECS,
    CandidateEvaluation,
    CandidateSpec,
)
from .profiler import DatasetSamples
from .sandbox import SQLValidationError, _mp_context, validate_select_sql


def _display_value(value: Any, limit: int = 300) -> str:
    if value is None:
        return "NULL"
    try:
        missing = pd.isna(value)
        if isinstance(missing, (bool, np.bool_)) and missing:
            return "NULL"
    except Exception:
        pass
    rendered = repr(value)
    return rendered if len(rendered) <= limit else rendered[: limit - 3] + "..."


def _equal_scalar(left: Any, right: Any) -> bool:
    try:
        left_missing = pd.isna(left)
        right_missing = pd.isna(right)
        if isinstance(left_missing, (bool, np.bool_)) and isinstance(
            right_missing, (bool, np.bool_)
        ):
            if left_missing or right_missing:
                return bool(left_missing and right_missing)
    except Exception:
        pass
    try:
        result = left == right
        return bool(result) if isinstance(result, (bool, np.bool_)) else False
    except Exception:
        return False


def _compare_frames(
    expected: pd.DataFrame, actual: pd.DataFrame, max_examples: int = 5
) -> tuple[int, list[dict[str, Any]]]:
    mismatch_count = 0
    examples: list[dict[str, Any]] = []
    for column in expected.columns:
        left_values = expected[column].tolist()
        right_values = actual[column].tolist()
        for position, (left, right) in enumerate(zip(left_values, right_values)):
            if _equal_scalar(left, right):
                continue
            mismatch_count += 1
            if len(examples) < max_examples:
                row_id = expected.iloc[position][ROW_ID_COLUMN]
                examples.append(
                    {
                        "row_id": int(row_id),
                        "column": column,
                        "expected": _display_value(left),
                        "actual": _display_value(right),
                    }
                )
    return mismatch_count, examples


def _write_parquet(
    df: pd.DataFrame,
    path: Path,
    codec: str,
    candidate: CandidateSpec | None = None,
) -> int:
    physical = df.drop(columns=[ROW_ID_COLUMN], errors="ignore")
    table = pa.Table.from_pandas(physical, preserve_index=False)
    if candidate is not None:
        metadata = dict(table.schema.metadata or {})
        metadata[b"virtual_agentic_candidate"] = candidate.model_dump_json().encode(
            "utf-8"
        )
        table = table.replace_schema_metadata(metadata)
    pq.write_table(table, path, compression=codec)
    return path.stat().st_size


def _evaluation_worker(
    result_queue: mp.Queue,
    source: pd.DataFrame,
    candidate_payload: dict[str, Any],
    split: str,
    codecs: tuple[str, ...],
    output_dir: str,
    timing_runs: int,
    max_output_bytes: int,
    memory_limit_mb: int,
) -> None:
    started = time.monotonic()
    con = None
    try:
        candidate = CandidateSpec.model_validate(candidate_payload)
        source_columns = list(source.columns)
        source_column_set = set(source_columns)
        missing_targets = sorted(set(candidate.target_columns) - source_column_set)
        missing_references = sorted(
            set(candidate.reference_columns) - source_column_set
        )
        if missing_targets or missing_references:
            raise ValueError(
                f"unknown target/reference columns: {missing_targets + missing_references}"
            )

        con = duckdb.connect(
            database=":memory:",
            config={
                "enable_external_access": "false",
                "threads": "1",
                "memory_limit": f"{memory_limit_mb}MB",
            },
        )
        con.register("source", source)
        source_relation = con.table("source")
        source_types = {
            name: str(data_type)
            for name, data_type in zip(source_relation.columns, source_relation.types)
        }
        compressed_relation = con.sql(candidate.compression_sql)
        compressed_names = compressed_relation.columns
        compressed = compressed_relation.df()

        if len(compressed_names) != len(set(compressed_names)):
            raise ValueError("compression SQL produced duplicate column names")
        if ROW_ID_COLUMN not in compressed.columns:
            raise ValueError(f"compression SQL must preserve {ROW_ID_COLUMN}")
        if len(compressed) != len(source):
            raise ValueError(
                f"compression changed row count from {len(source)} to {len(compressed)}"
            )
        if (
            compressed[ROW_ID_COLUMN].isna().any()
            or not compressed[ROW_ID_COLUMN].is_unique
        ):
            raise ValueError(f"{ROW_ID_COLUMN} must be non-null and unique")

        source_ids = set(source[ROW_ID_COLUMN].astype(int).tolist())
        compressed_ids = set(compressed[ROW_ID_COLUMN].astype(int).tolist())
        if source_ids != compressed_ids:
            raise ValueError("compression SQL changed the set of row identifiers")

        missing_physical_references = sorted(
            set(candidate.reference_columns) - set(compressed.columns)
        )
        if missing_physical_references:
            raise ValueError(
                "compression removed declared reference columns: "
                + ", ".join(missing_physical_references)
            )
        generated = set(compressed.columns) - source_column_set
        declared_residuals = {column.name for column in candidate.residual_columns}
        if generated != declared_residuals:
            raise ValueError(
                "generated columns must exactly match residual_columns; "
                f"generated={sorted(generated)}, declared={sorted(declared_residuals)}"
            )

        output_bytes = int(compressed.memory_usage(index=True, deep=True).sum())
        if output_bytes > max_output_bytes:
            raise ValueError(
                f"compressed result uses approximately {output_bytes} bytes; "
                f"limit is {max_output_bytes}"
            )

        compressed = compressed.sort_values(ROW_ID_COLUMN).reset_index(drop=True)
        con.register("compressed", compressed)
        reconstructed_relation = con.sql(candidate.reconstruction_sql)
        reconstructed_names = reconstructed_relation.columns
        reconstructed_types = {
            name: str(data_type)
            for name, data_type in zip(
                reconstructed_names, reconstructed_relation.types
            )
        }
        reconstructed = reconstructed_relation.df()
        if len(reconstructed_names) != len(set(reconstructed_names)):
            raise ValueError("reconstruction SQL produced duplicate column names")
        if set(reconstructed.columns) != source_column_set:
            missing = sorted(source_column_set - set(reconstructed.columns))
            extra = sorted(set(reconstructed.columns) - source_column_set)
            raise ValueError(
                f"reconstruction schema mismatch; missing={missing}, extra={extra}"
            )
        type_mismatches = {
            name: {
                "expected": source_types[name],
                "actual": reconstructed_types[name],
            }
            for name in source_columns
            if reconstructed_types[name] != source_types[name]
        }
        if type_mismatches:
            raise ValueError(f"reconstruction type mismatch: {type_mismatches}")
        if len(reconstructed) != len(source):
            raise ValueError(
                f"reconstruction changed row count from {len(source)} to {len(reconstructed)}"
            )
        if (
            ROW_ID_COLUMN not in reconstructed
            or not reconstructed[ROW_ID_COLUMN].is_unique
        ):
            raise ValueError(
                f"reconstruction must preserve unique {ROW_ID_COLUMN} values"
            )

        expected = source.sort_values(ROW_ID_COLUMN).reset_index(drop=True)[
            source_columns
        ]
        actual = reconstructed.sort_values(ROW_ID_COLUMN).reset_index(drop=True)[
            source_columns
        ]
        mismatch_count, counterexamples = _compare_frames(expected, actual)
        if mismatch_count:
            result_queue.put(
                {
                    "candidate_id": candidate.id,
                    "split": split,
                    "valid": False,
                    "status": "invalid",
                    "reason": f"reconstruction differs in {mismatch_count} cell(s)",
                    "rows": len(source),
                    "mismatch_count": mismatch_count,
                    "output_columns": list(compressed.columns),
                    "auxiliary_columns": len(generated),
                    "counterexamples": counterexamples,
                    "elapsed_seconds": time.monotonic() - started,
                }
            )
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        codec_sizes: dict[str, dict[str, Any]] = {}
        artifact_paths: dict[str, str] = {}
        for codec in codecs:
            base_path = output_path / f"base-{codec}.parquet"
            compressed_path = output_path / f"compressed-{codec}.parquet"
            base_size = _write_parquet(source, base_path, codec)
            compressed_size = _write_parquet(
                compressed, compressed_path, codec, candidate
            )
            base_path.unlink()
            savings = base_size - compressed_size
            codec_sizes[codec] = {
                "base_bytes": base_size,
                "compressed_bytes": compressed_size,
                "savings_bytes": savings,
                "savings_ratio": (savings / base_size) if base_size else 0.0,
            }
            artifact_paths[codec] = str(compressed_path)

        reconstruction_latency_ms = None
        if timing_runs > 0:
            con.execute(candidate.reconstruction_sql).fetchdf()
            timings: list[float] = []
            for _ in range(timing_runs):
                timing_start = time.perf_counter_ns()
                con.execute(candidate.reconstruction_sql).fetchdf()
                timings.append((time.perf_counter_ns() - timing_start) / 1_000_000)
            reconstruction_latency_ms = float(np.mean(timings))

        result_queue.put(
            {
                "candidate_id": candidate.id,
                "split": split,
                "valid": True,
                "status": "valid",
                "rows": len(source),
                "mismatch_count": 0,
                "output_columns": list(compressed.columns),
                "auxiliary_columns": len(generated),
                "codec_sizes": codec_sizes,
                "reconstruction_latency_ms": reconstruction_latency_ms,
                "counterexamples": [],
                "elapsed_seconds": time.monotonic() - started,
                "artifact_paths": artifact_paths,
            }
        )
    except Exception as exc:
        result_queue.put(
            {
                "candidate_id": candidate_payload.get("id", "unknown"),
                "split": split,
                "valid": False,
                "status": "error",
                "reason": f"{type(exc).__name__}: {exc}",
                "rows": len(source),
                "elapsed_seconds": time.monotonic() - started,
            }
        )
    finally:
        if con is not None:
            con.close()


class CandidateEvaluator:
    def __init__(
        self,
        samples: DatasetSamples,
        *,
        timeout_seconds: float = 30.0,
        full_timeout_seconds: float = 300.0,
        memory_limit_mb: int = 1_024,
        output_size_factor: float = 8.0,
    ) -> None:
        self.samples = samples
        self.timeout_seconds = timeout_seconds
        self.full_timeout_seconds = full_timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.output_size_factor = output_size_factor

    def _data_for_split(self, split: str) -> pd.DataFrame:
        if split == "discovery":
            return self.samples.discovery
        if split == "holdout":
            return self.samples.holdout
        if split == "full":
            return self.samples.full
        raise ValueError(f"unknown evaluation split {split!r}")

    def evaluate(
        self,
        candidate: CandidateSpec,
        *,
        split: str = "discovery",
        codecs: Iterable[str] = ("snappy",),
        require_gain: bool = True,
        artifact_dir: Path | None = None,
        timing_runs: int = 0,
    ) -> CandidateEvaluation:
        started = time.monotonic()
        codecs_tuple = tuple(codecs)
        unsupported = sorted(set(codecs_tuple) - set(SUPPORTED_CODECS))
        if unsupported:
            raise ValueError(f"unsupported codecs: {', '.join(unsupported)}")
        try:
            validate_select_sql(candidate.compression_sql, "source")
            validate_select_sql(candidate.reconstruction_sql, "compressed")
        except SQLValidationError as exc:
            return CandidateEvaluation(
                candidate_id=candidate.id,
                split=split,
                valid=False,
                status="rejected",
                reason=str(exc),
                elapsed_seconds=time.monotonic() - started,
            )

        source = self._data_for_split(split)
        if source.empty:
            return CandidateEvaluation(
                candidate_id=candidate.id,
                split=split,
                valid=False,
                status="skipped",
                reason="dataset split is empty",
                elapsed_seconds=time.monotonic() - started,
            )

        temporary = None
        if artifact_dir is None:
            temporary = tempfile.TemporaryDirectory(prefix="virtual-agentic-eval-")
            output_dir = Path(temporary.name)
        else:
            output_dir = artifact_dir / candidate.id / split
            output_dir.mkdir(parents=True, exist_ok=False)

        max_output_bytes = max(
            1_000_000,
            int(
                source.memory_usage(index=True, deep=True).sum()
                * self.output_size_factor
            ),
        )
        context = _mp_context()
        result_queue = context.Queue(maxsize=1)
        process = context.Process(
            target=_evaluation_worker,
            args=(
                result_queue,
                source,
                candidate.model_dump(mode="json"),
                split,
                codecs_tuple,
                str(output_dir),
                timing_runs,
                max_output_bytes,
                self.memory_limit_mb,
            ),
        )
        process.start()
        timeout = self.full_timeout_seconds if split == "full" else self.timeout_seconds
        process.join(timeout)
        if process.is_alive():
            process.terminate()
            process.join(2)
            evaluation = CandidateEvaluation(
                candidate_id=candidate.id,
                split=split,
                valid=False,
                status="timeout",
                reason=f"candidate exceeded {timeout:.1f}s timeout",
                rows=len(source),
                elapsed_seconds=timeout,
            )
        else:
            try:
                payload = result_queue.get_nowait()
                evaluation = CandidateEvaluation.model_validate(payload)
            except queue.Empty:
                evaluation = CandidateEvaluation(
                    candidate_id=candidate.id,
                    split=split,
                    valid=False,
                    status="error",
                    reason=(
                        f"evaluation worker exited with code {process.exitcode} "
                        "without a result"
                    ),
                    rows=len(source),
                    elapsed_seconds=time.monotonic() - started,
                )

        if temporary is not None:
            temporary.cleanup()
            evaluation.artifact_paths = {}

        if evaluation.valid and require_gain:
            snappy = evaluation.codec_sizes.get("snappy")
            if snappy is None or snappy.savings_bytes <= 0:
                evaluation.valid = False
                evaluation.status = "rejected"
                evaluation.reason = "candidate does not reduce Snappy Parquet size"
                if artifact_dir is not None and output_dir.exists():
                    shutil.rmtree(output_dir)
                    evaluation.artifact_paths = {}
        return evaluation

    def validate(
        self,
        candidate: CandidateSpec,
        *,
        artifact_dir: Path | None = None,
    ) -> list[CandidateEvaluation]:
        evaluations: list[CandidateEvaluation] = []
        for split in ("discovery", "holdout"):
            evaluation = self.evaluate(candidate, split=split)
            evaluations.append(evaluation)
            if not evaluation.valid:
                return evaluations
        evaluations.append(
            self.evaluate(
                candidate,
                split="full",
                codecs=SUPPORTED_CODECS,
                artifact_dir=artifact_dir,
                timing_runs=10,
            )
        )
        return evaluations


def best_evaluation(
    candidates: list[tuple[CandidateSpec, CandidateEvaluation]],
) -> tuple[CandidateSpec, CandidateEvaluation] | None:
    valid = [item for item in candidates if item[1].valid]
    if not valid:
        return None
    return max(
        valid,
        key=lambda item: (
            item[1].snappy_savings_bytes,
            -(item[1].reconstruction_latency_ms or float("inf")),
            -item[1].auxiliary_columns,
        ),
    )
