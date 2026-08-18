#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from string_compression.agentic.experiment import ExperimentRunner  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark agentic and algorithmic string reconstruction strategies."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("config.json"),
        help="Dataset configuration JSON.",
    )
    parser.add_argument(
        "--datasets",
        default="all",
        help="Comma-separated dataset IDs or 'all'.",
    )
    parser.add_argument(
        "--strategies",
        default="single,two-stage,tool-loop",
        help="Comma-separated agent strategies.",
    )
    parser.add_argument(
        "--bootstrap-small",
        action="store_true",
        help="Download the two allowlisted small Wikipedia configurations if absent.",
    )
    parser.add_argument(
        "--bootstrap-public-samples",
        action="store_true",
        help="Stream bounded samples from supported public datasets when local data is absent.",
    )
    parser.add_argument(
        "--public-sample-rows",
        type=int,
        default=5_000,
        help="Rows to retain for each explicitly bootstrapped public sample.",
    )
    parser.add_argument("--max-rows", type=int, default=1_000_000)
    parser.add_argument("--model", default=None, help="Override VIRTUAL_OPENAI_MODEL.")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Run heuristic and manual baselines without OpenAI calls.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).with_name("results"),
    )
    parser.add_argument("--run-id", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_rows <= 0:
        raise SystemExit("--max-rows must be positive")
    if args.public_sample_rows <= 0:
        raise SystemExit("--public-sample-rows must be positive")
    strategies = tuple(
        strategy.strip().replace("-", "_")
        for strategy in args.strategies.split(",")
        if strategy.strip()
    )
    unknown = sorted(set(strategies) - {"single", "two_stage", "tool_loop"})
    if unknown:
        raise SystemExit(f"unknown strategies: {', '.join(unknown)}")
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.output_root / run_id
    runner = ExperimentRunner(
        config_path=args.config,
        run_dir=run_dir,
        datasets=args.datasets,
        strategies=strategies,
        bootstrap_small=args.bootstrap_small,
        bootstrap_public_samples=args.bootstrap_public_samples,
        public_sample_rows=args.public_sample_rows,
        max_rows=args.max_rows,
        model=args.model,
        offline=args.offline,
    )
    results = runner.run()
    available = sum(
        dataset.get("status") != "skipped" for dataset in results["datasets"]
    )
    print(f"Completed {available}/{len(results['datasets'])} dataset configurations.")
    print(f"Results: {run_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
