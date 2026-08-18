from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from .agents import PROMPT_VERSION, OpenAIAgent
from .baselines import BaselineDefinition, heuristic_candidates, manual_baselines
from .datasets import (
    DatasetConfig,
    load_dataframe,
    load_dataset_configs,
    resolve_dataset,
)
from .evaluator import CandidateEvaluator, best_evaluation
from .models import ROW_ID_COLUMN, SUPPORTED_CODECS, CandidateSpec
from .profiler import profile_dataframe, split_dataset
from .reporting import ResultReporter


class ExperimentRunner:
    def __init__(
        self,
        *,
        config_path: Path,
        run_dir: Path,
        datasets: str = "all",
        strategies: tuple[str, ...] = ("single", "two_stage", "tool_loop"),
        bootstrap_small: bool = False,
        bootstrap_public_samples: bool = False,
        public_sample_rows: int = 5_000,
        max_rows: int = 1_000_000,
        model: str | None = None,
        offline: bool = False,
    ) -> None:
        self.config_path = config_path.resolve()
        self.run_dir = run_dir.resolve()
        self.datasets = datasets
        self.strategies = strategies
        self.bootstrap_small = bootstrap_small
        self.bootstrap_public_samples = bootstrap_public_samples
        self.public_sample_rows = public_sample_rows
        self.max_rows = max_rows
        self.agent = OpenAIAgent(model=model) if not offline else None
        self.reporter = ResultReporter(self.run_dir)

    def run(self) -> dict[str, Any]:
        self.reporter.initialize()
        results: dict[str, Any] = {
            "format_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_dir.name,
            "prompt_version": PROMPT_VERSION,
            "config_path": str(self.config_path),
            "max_rows": self.max_rows,
            "bootstrap_small": self.bootstrap_small,
            "bootstrap_public_samples": self.bootstrap_public_samples,
            "public_sample_rows": self.public_sample_rows,
            "strategies": list(self.strategies),
            "model": self.agent.model if self.agent else None,
            "datasets": [],
        }
        configs = load_dataset_configs(self.config_path, self.datasets)
        for index, config in enumerate(configs, start=1):
            print(
                f"[{index}/{len(configs)}] {config.dataset_id} "
                f"({config.config_name or 'default'})"
            )
            dataset_result = self._run_dataset(config)
            results["datasets"].append(dataset_result)
            self.reporter.write(results)
        return results

    def _run_dataset(self, config: DatasetConfig) -> dict[str, Any]:
        resolution = resolve_dataset(
            self.config_path,
            config,
            bootstrap_small=self.bootstrap_small,
            bootstrap_public_samples=self.bootstrap_public_samples,
            public_sample_rows=self.public_sample_rows,
        )
        result: dict[str, Any] = {
            "dataset_id": config.dataset_id,
            "config_name": config.config_name,
            "resolution_status": resolution.status,
            "status": "available" if resolution.path else "skipped",
            "reason": resolution.reason,
            "groups": [],
        }
        if resolution.path is None:
            return result

        try:
            frame = load_dataframe(resolution.path, max_rows=self.max_rows)
        except Exception as exc:
            result.update(
                status="skipped",
                reason=f"dataset loading failed: {type(exc).__name__}: {exc}",
            )
            return result
        if frame.empty:
            result.update(status="skipped", reason="dataset is empty")
            return result

        samples = split_dataset(frame)
        profile = profile_dataframe(samples.discovery)
        string_columns = [
            column["name"]
            for column in profile["columns"]
            if column["kind"] == "string" and column["name"] != ROW_ID_COLUMN
        ]
        result["rows"] = len(frame)
        result["columns"] = list(frame.columns)
        result["string_columns"] = string_columns
        if len(string_columns) < 2:
            result.update(
                status="skipped",
                reason="at least two string columns are required",
            )
            return result

        dataset_key = f"{config.dataset_id}__{config.output_name}".replace(
            "/", "_"
        ).replace(" ", "_")
        dataset_artifacts = self.run_dir / "artifacts" / dataset_key
        dataset_artifacts.mkdir(parents=True, exist_ok=True)
        result["original"] = self._write_original(samples.full, dataset_artifacts)
        evaluator = CandidateEvaluator(samples)

        manual = manual_baselines(config.dataset_id, config.config_name, frame.columns)
        result["groups"].append(
            self._evaluate_baseline_group(
                "manual", manual, evaluator, dataset_artifacts / "manual"
            )
        )
        heuristic = heuristic_candidates(samples.discovery)
        result["groups"].append(
            self._evaluate_candidates(
                "heuristic",
                heuristic,
                evaluator,
                dataset_artifacts / "heuristic",
                strategy="heuristic",
            )
        )

        if self.agent is None:
            for strategy in self.strategies:
                result["groups"].append(
                    {
                        "name": "agent",
                        "strategy": strategy,
                        "status": "skipped",
                        "reason": "offline mode",
                        "candidates": [],
                    }
                )
        else:
            for strategy in self.strategies:
                strategy_run = self.agent.run(strategy, profile, evaluator)
                group = self._evaluate_candidates(
                    "agent",
                    strategy_run.candidates,
                    evaluator,
                    dataset_artifacts / f"agent_{strategy}",
                    strategy=strategy,
                )
                group.update(
                    {
                        "model": strategy_run.model,
                        "usage": [
                            item.model_dump(mode="json") for item in strategy_run.usage
                        ],
                        "calls": strategy_run.calls,
                        "tool_calls": strategy_run.tool_calls,
                        "agent_elapsed_seconds": strategy_run.elapsed_seconds,
                        "lineage": strategy_run.lineage,
                    }
                )
                if strategy_run.status != "completed":
                    group["status"] = strategy_run.status
                    group["reason"] = strategy_run.reason
                result["groups"].append(group)
        return result

    def _write_original(self, source, output_dir: Path) -> dict[str, Any]:
        physical = source.drop(columns=[ROW_ID_COLUMN])
        table = pa.Table.from_pandas(physical, preserve_index=False)
        codec_sizes: dict[str, int] = {}
        artifacts: dict[str, str] = {}
        original_dir = output_dir / "original"
        original_dir.mkdir(parents=True, exist_ok=True)
        for codec in SUPPORTED_CODECS:
            path = original_dir / f"original-{codec}.parquet"
            pq.write_table(table, path, compression=codec)
            codec_sizes[codec] = path.stat().st_size
            artifacts[codec] = str(path)
        return {"codec_sizes": codec_sizes, "artifact_paths": artifacts}

    def _evaluate_baseline_group(
        self,
        name: str,
        definitions: list[BaselineDefinition],
        evaluator: CandidateEvaluator,
        artifact_dir: Path,
    ) -> dict[str, Any]:
        candidates = [
            definition.candidate for definition in definitions if definition.candidate
        ]
        group = self._evaluate_candidates(
            name,
            candidates,
            evaluator,
            artifact_dir,
            strategy=name,
        )
        for definition in definitions:
            if definition.candidate is None:
                group["candidates"].append(
                    {
                        "id": definition.name,
                        "status": "skipped",
                        "reason": definition.reason,
                        "selected": False,
                        "evaluations": [],
                    }
                )
        return group

    def _evaluate_candidates(
        self,
        name: str,
        candidates: list[CandidateSpec],
        evaluator: CandidateEvaluator,
        artifact_dir: Path,
        *,
        strategy: str,
    ) -> dict[str, Any]:
        group: dict[str, Any] = {
            "name": name,
            "strategy": strategy,
            "status": "completed",
            "candidates": [],
        }
        valid_finals: list[tuple[CandidateSpec, Any]] = []
        seen_candidate_ids: set[str] = set()
        for candidate in candidates:
            if candidate.id in seen_candidate_ids:
                group["candidates"].append(
                    {
                        "candidate": candidate.model_dump(mode="json"),
                        "status": "rejected",
                        "reason": f"duplicate candidate id: {candidate.id}",
                        "selected": False,
                        "evaluations": [],
                    }
                )
                continue
            seen_candidate_ids.add(candidate.id)
            evaluations = evaluator.validate(candidate, artifact_dir=artifact_dir)
            final = evaluations[-1]
            item = {
                "candidate": candidate.model_dump(mode="json"),
                "evaluations": [
                    evaluation.model_dump(mode="json") for evaluation in evaluations
                ],
                "selected": False,
            }
            group["candidates"].append(item)
            if final.valid and final.split == "full":
                valid_finals.append((candidate, final))
        selected = best_evaluation(valid_finals)
        if selected is not None:
            selected_id = selected[0].id
            for item in group["candidates"]:
                if item.get("candidate", {}).get("id") == selected_id:
                    item["selected"] = True
                    break
            group["selected_candidate_id"] = selected_id
        elif candidates:
            group["reason"] = (
                "no candidate passed lossless, size-positive full validation"
            )
        else:
            group["status"] = "skipped"
            group["reason"] = "no candidates were produced"
        return group
