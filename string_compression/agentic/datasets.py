from __future__ import annotations

import json
import multiprocessing as mp
import queue
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import pyarrow.parquet as pq


SMALL_WIKIPEDIA_CONFIGS = {
    "20231101.ab",
    "20231101.zh-classical",
}

PUBLIC_SAMPLE_DATASETS = {
    "HuggingFaceFW/fineweb",
    "vCache/SemBenchmarkLmArena",
    "vCache/SemBenchmarkClassification",
    "nhagar/fineweb_urls",
}


@dataclass(frozen=True)
class DatasetConfig:
    dataset_id: str
    config_name: str
    details: dict[str, Any]

    @property
    def output_name(self) -> str:
        if self.config_name:
            return self.config_name
        return self.dataset_id.replace("/", "_").replace("-", "_")


@dataclass(frozen=True)
class DatasetResolution:
    config: DatasetConfig
    path: Path | None
    status: str
    reason: str | None = None


def load_dataset_configs(
    config_path: Path, selected: str | Iterable[str] = "all"
) -> list[DatasetConfig]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    if isinstance(selected, str):
        selected_ids = None if selected == "all" else set(selected.split(","))
    else:
        selected_ids = set(selected)
    configs: list[DatasetConfig] = []
    for dataset_id, dataset_details in data.items():
        if selected_ids is not None and dataset_id not in selected_ids:
            continue
        for details in dataset_details.get("configs", []):
            configs.append(
                DatasetConfig(
                    dataset_id=dataset_id,
                    config_name=str(details.get("file") or ""),
                    details=dict(details),
                )
            )
    return configs


def _candidate_paths(config_path: Path, config: DatasetConfig) -> list[Path]:
    base = config_path.parent
    candidates: list[Path] = []
    configured_path = config.details.get("path")
    if configured_path:
        candidates.append((base / configured_path).resolve())
        candidates.append((config_path.parents[1] / configured_path).resolve())
    parquet_name = config.output_name + ".parquet"
    candidates.append(
        (base / "datasets_parquet" / config.dataset_id / parquet_name).resolve()
    )
    candidates.append(
        (
            config_path.parents[1]
            / "datasets_parquet"
            / config.dataset_id
            / parquet_name
        ).resolve()
    )
    candidates.append(
        (
            base
            / ".cache"
            / "agentic_datasets"
            / config.dataset_id
            / config.output_name
        ).resolve()
    )
    return candidates


def _contains_supported_data(path: Path) -> bool:
    if path.is_file():
        return path.suffix.lower() in {".parquet", ".parq", ".csv"}
    if not path.is_dir():
        return False
    return any(
        file.is_file() and file.suffix.lower() in {".parquet", ".parq", ".csv"}
        for file in path.rglob("*")
    )


def _bootstrap_wikipedia(config_path: Path, config: DatasetConfig) -> Path:
    from huggingface_hub import snapshot_download

    cache_root = config_path.parent / ".cache" / "agentic_datasets"
    local_dataset = cache_root / config.dataset_id
    snapshot_download(
        repo_id=config.dataset_id,
        repo_type="dataset",
        local_dir=local_dataset,
        cache_dir=cache_root / "huggingface",
        allow_patterns=[f"{config.config_name}/*"],
    )
    resolved = local_dataset / config.config_name
    if not resolved.exists():
        raise FileNotFoundError(
            f"download completed but {resolved} was not materialized"
        )
    return resolved


def _public_sample_worker(
    result_queue: mp.Queue,
    dataset_id: str,
    config_name: str | None,
    sample_rows: int,
    cache_dir: str,
    output_path: str,
) -> None:
    from datasets import load_dataset

    try:
        dataset = load_dataset(
            dataset_id,
            config_name,
            split="train",
            streaming=True,
            cache_dir=cache_dir,
        )
        iterator = iter(dataset)
        try:
            rows = list(islice(iterator, sample_rows))
        finally:
            close = getattr(iterator, "close", None)
            if callable(close):
                close()
        if not rows:
            raise ValueError("streaming dataset returned no rows")
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        incomplete = destination.with_suffix(destination.suffix + ".incomplete")
        pd.DataFrame.from_records(rows).to_parquet(incomplete, index=False)
        incomplete.replace(destination)
        result_queue.put({"ok": True, "path": str(destination)})
    except Exception as exc:
        result_queue.put({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


def _bootstrap_public_sample(
    config_path: Path,
    config: DatasetConfig,
    sample_rows: int,
    timeout_seconds: float = 300.0,
) -> Path:
    cache_root = config_path.parent / ".cache" / "agentic_datasets"
    output_path = (
        cache_root
        / config.dataset_id
        / config.output_name
        / f"sample-{sample_rows}.parquet"
    )
    if output_path.exists():
        return output_path

    config_name = (
        config.config_name if config.config_name not in {"", "default"} else None
    )
    methods = mp.get_all_start_methods()
    context = mp.get_context("spawn" if "spawn" in methods else methods[0])
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_public_sample_worker,
        args=(
            result_queue,
            config.dataset_id,
            config_name,
            sample_rows,
            str(cache_root / "huggingface"),
            str(output_path),
        ),
    )
    process.start()
    try:
        payload = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as exc:
        process.terminate()
        process.join(2)
        raise TimeoutError(
            f"streaming sample exceeded {timeout_seconds:.1f}s timeout"
        ) from exc

    process.join(1)
    if process.is_alive():
        process.terminate()
        process.join(2)
    if not payload["ok"]:
        raise RuntimeError(payload["error"])
    return Path(payload["path"])


def resolve_dataset(
    config_path: Path,
    config: DatasetConfig,
    *,
    bootstrap_small: bool = False,
    bootstrap_public_samples: bool = False,
    public_sample_rows: int = 5_000,
) -> DatasetResolution:
    for path in _candidate_paths(config_path, config):
        if _contains_supported_data(path):
            return DatasetResolution(config=config, path=path, status="available")

    if (
        bootstrap_small
        and config.dataset_id == "wikimedia/wikipedia"
        and config.config_name in SMALL_WIKIPEDIA_CONFIGS
    ):
        try:
            path = _bootstrap_wikipedia(config_path, config)
            return DatasetResolution(config=config, path=path, status="bootstrapped")
        except Exception as exc:
            return DatasetResolution(
                config=config,
                path=None,
                status="skipped",
                reason=f"small-dataset bootstrap failed: {type(exc).__name__}: {exc}",
            )

    if bootstrap_public_samples and config.dataset_id in PUBLIC_SAMPLE_DATASETS:
        try:
            path = _bootstrap_public_sample(config_path, config, public_sample_rows)
            return DatasetResolution(config=config, path=path, status="sampled")
        except Exception as exc:
            return DatasetResolution(
                config=config,
                path=None,
                status="skipped",
                reason=f"public streaming sample failed: {type(exc).__name__}: {exc}",
            )

    if config.dataset_id == "bigdata-pw/Flickr":
        reason = "dataset is not local and the configured repository may require authentication"
    else:
        reason = "dataset is not local and is outside the capped bootstrap allowlist"
    return DatasetResolution(config=config, path=None, status="skipped", reason=reason)


def _read_frame(path: Path, remaining: int) -> pd.DataFrame:
    if path.suffix.lower() in {".parquet", ".parq"}:
        parquet = pq.ParquetFile(path)
        frames: list[pd.DataFrame] = []
        rows = 0
        for batch in parquet.iter_batches(batch_size=min(65_536, remaining)):
            needed = remaining - rows
            if needed <= 0:
                break
            if batch.num_rows > needed:
                batch = batch.slice(0, needed)
            frames.append(batch.to_pandas())
            rows += batch.num_rows
        if not frames:
            return parquet.schema_arrow.empty_table().to_pandas()
        frame = pd.concat(frames, ignore_index=True)
    elif path.suffix.lower() == ".csv":
        frame = pd.read_csv(path, nrows=remaining)
    else:
        raise ValueError(f"unsupported dataset file {path}")
    return frame.head(remaining)


def load_dataframe(path: Path, max_rows: int = 1_000_000) -> pd.DataFrame:
    if path.is_file():
        return _read_frame(path, max_rows).reset_index(drop=True)

    files = sorted(
        file
        for file in path.rglob("*")
        if file.is_file() and file.suffix.lower() in {".parquet", ".parq", ".csv"}
    )
    frames: list[pd.DataFrame] = []
    rows = 0
    for file in files:
        remaining = max_rows - rows
        if remaining <= 0:
            break
        frame = _read_frame(file, remaining)
        frames.append(frame)
        rows += len(frame)
    if not frames:
        raise FileNotFoundError(f"no Parquet or CSV files found under {path}")
    return pd.concat(frames, ignore_index=True).head(max_rows)
