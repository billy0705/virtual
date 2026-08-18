import json

import pandas as pd

import string_compression.agentic.datasets as datasets_module
from string_compression.agentic.datasets import DatasetConfig, resolve_dataset
from string_compression.agentic.experiment import ExperimentRunner
from string_compression.agentic.datasets import load_dataframe


def test_offline_experiment_writes_comparison_artifacts(tmp_path):
    values = ["common-prefix-" + "x" * 300 + str(index) for index in range(300)]
    dataset_path = tmp_path / "sample.parquet"
    pd.DataFrame({"source_text": values, "target": values}).to_parquet(dataset_path)
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "example/strings": {
                    "configs": [
                        {
                            "file": "default",
                            "status": "processed",
                            "path": str(dataset_path),
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    run_dir = tmp_path / "run"
    results = ExperimentRunner(
        config_path=config_path,
        run_dir=run_dir,
        offline=True,
        max_rows=300,
    ).run()

    dataset = results["datasets"][0]
    heuristic = next(
        group for group in dataset["groups"] if group["name"] == "heuristic"
    )
    assert heuristic["selected_candidate_id"]
    assert (run_dir / "results.json").exists()
    assert (run_dir / "summary.csv").exists()
    assert (run_dir / "summary.md").exists()
    assert list((run_dir / "candidates").glob("*.sql"))
    assert (run_dir / "compression_sizes_snappy.png").stat().st_size > 0
    assert (run_dir / "compression_ratios_snappy.png").stat().st_size > 0
    assert (run_dir / "compression_functions.md").exists()
    comparison = pd.read_csv(run_dir / "comparison_plot_data.csv")
    assert set(comparison["strategy"]) == {
        "original",
        "heuristic",
        "manual",
        "single",
        "two_stage",
        "tool_loop",
    }
    assert comparison["original_bytes"].nunique() == 1
    heuristic_row = comparison.loc[comparison["strategy"] == "heuristic"].iloc[0]
    assert heuristic_row["compressed_bytes"] < heuristic_row["original_bytes"]
    assert not heuristic_row["fallback_to_original"]
    offline_agents = comparison.loc[
        comparison["strategy"].isin(["single", "two_stage", "tool_loop"])
    ]
    assert offline_agents["fallback_to_original"].all()
    function_catalog = (run_dir / "compression_functions.md").read_text(
        encoding="utf-8"
    )
    assert "Algorithmic auto-prefix/suffix" in function_catalog
    assert "Compression SQL:" in function_catalog
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    assert payload["run_id"] == "run"
    assert payload["prompt_version"] == "agentic-string-compression-v1"


def test_parquet_loading_honors_the_row_cap_without_pandas_read_parquet(
    tmp_path, monkeypatch
):
    dataset_path = tmp_path / "capped.parquet"
    pd.DataFrame({"value": range(100)}).to_parquet(dataset_path)

    def unexpected_full_read(*_args, **_kwargs):
        raise AssertionError("pandas.read_parquet would load the full file")

    monkeypatch.setattr(pd, "read_parquet", unexpected_full_read)
    loaded = load_dataframe(dataset_path, max_rows=7)
    assert loaded["value"].tolist() == list(range(7))


def test_resolver_uses_prefetched_cache_and_explicit_public_samples(
    tmp_path, monkeypatch
):
    config_path = tmp_path / "string_compression" / "config.json"
    config_path.parent.mkdir()
    config_path.write_text("{}", encoding="utf-8")

    cached_config = DatasetConfig("example/cached", "default", {})
    cached_path = (
        config_path.parent
        / ".cache"
        / "agentic_datasets"
        / "example"
        / "cached"
        / "default"
    )
    cached_path.mkdir(parents=True)
    pd.DataFrame({"value": [1]}).to_parquet(cached_path / "sample.parquet")
    cached = resolve_dataset(config_path, cached_config)
    assert cached.path == cached_path

    empty_config = DatasetConfig("example/empty", "default", {})
    empty_path = (
        config_path.parent
        / ".cache"
        / "agentic_datasets"
        / "example"
        / "empty"
        / "default"
    )
    empty_path.mkdir(parents=True)
    empty = resolve_dataset(config_path, empty_config)
    assert empty.path is None

    sampled_path = tmp_path / "sample.parquet"
    pd.DataFrame({"value": [1]}).to_parquet(sampled_path)
    monkeypatch.setattr(
        datasets_module, "_bootstrap_public_sample", lambda *_args: sampled_path
    )
    public = resolve_dataset(
        config_path,
        DatasetConfig("nhagar/fineweb_urls", "", {}),
        bootstrap_public_samples=True,
        public_sample_rows=1,
    )
    assert public.status == "sampled"
    assert public.path == sampled_path
