# Correlation-Aware String Compression

This directory contains the original hand-written string compression experiments and
an experiment framework in `agentic/` that asks an OpenAI model to propose lossless
DuckDB SQL transformations between string columns.

The framework is intentionally separate from the public `virtual` package. Every
agentic, heuristic, and hand-written candidate is passed through the same local
evaluator. A candidate is only accepted when it reconstructs every value and NULL,
preserves row cardinality, and reduces Snappy-compressed Parquet size.

## Setup

Install the project and experiment dependencies from the repository root:

```bash
python -m pip install -e . -r string_compression/requirements.txt
```

Create a repository-root `.env` containing:

```dotenv
OPENAI_API_KEY=...
# Optional; defaults to gpt-5.6-terra.
VIRTUAL_OPENAI_MODEL=gpt-5.6-terra
```

API keys and sampled prompt rows are never written to result artifacts. OpenAI calls
use the Responses API with `store=False`.

## Run

Run all configured datasets, automatically downloading only the two allowlisted small
Wikipedia configurations when they are missing:

```bash
python string_compression/run_agentic_experiments.py \
  --datasets all \
  --strategies single,two-stage,tool-loop \
  --bootstrap-small \
  --bootstrap-public-samples \
  --public-sample-rows 5000 \
  --max-rows 1000000
```

`--bootstrap-public-samples` is explicit opt-in. It streams a bounded local sample for
supported public datasets instead of downloading their complete multi-gigabyte sources.
Without that flag, automatic downloads remain limited to Wikipedia `20231101.ab` and
`20231101.zh-classical`; other missing or gated data is reported as skipped.

Run only deterministic baselines without an API key:

```bash
python string_compression/run_agentic_experiments.py \
  --datasets wikimedia/wikipedia \
  --bootstrap-small \
  --offline
```

Use `--run-id NAME` for a stable output name, `--model MODEL` to override the model,
or `--output-root PATH` to relocate artifacts. Existing run directories are never
overwritten.

## Agent Strategies

- `single`: one structured response proposes up to five candidates.
- `two-stage`: one proposal call, deterministic evaluation, and one repair call.
- `tool-loop`: up to eight model turns and twelve calls to local profiling,
  candidate-evaluation, and submission tools.

The model receives column types and statistics plus 32 deterministic, truncated sample
rows. Full datasets stay local. Candidate SQL runs in a subprocess using an in-memory
DuckDB connection with external access disabled, a relation allowlist, memory and
output limits, and a wall timeout.

## Candidate Contract

`compression_sql` reads only `source`, preserves `__virtual_row_id`, and declares every
generated helper or error column. `reconstruction_sql` reads only `compressed` and must
return the complete original schema plus the row ID. Both queries must be a single
DuckDB `SELECT` or `WITH ... SELECT` statement.

Unsafe commands, filesystem and network readers, extensions, DDL/DML, random values,
clocks, and unapproved relations are rejected before execution. The row ID is used for
validation but omitted from measured Parquet files.

## Results

Each run creates `string_compression/results/<run-id>/` with:

- `results.json`: complete candidates, phase evaluations, API usage, and skip reasons.
- `summary.csv`: one row per original, baseline, or agent candidate.
- `summary.md`: compact comparison table.
- `comparison_plot_data.csv`: exact Snappy bytes plotted for each dataset/strategy.
- `compression_sizes_snappy.{png,pdf}`: absolute grouped size comparison.
- `compression_ratios_snappy.{png,pdf}`: normalized grouped size comparison.
- `compression_functions.md`: selected SQL functions and explicit identity fallbacks.
- `candidates/*.sql`: accepted and rejected candidate SQL for inspection.
- `artifacts/`: original and lossless, size-positive compressed Parquet files.

Final candidates are checked on discovery, disjoint holdout, and full-data splits.
Full-data results include Snappy, gzip, Brotli, LZ4, and Zstd sizes and reconstruction
latency after one warm-up plus ten measured executions. Missing, gated, and non-
allowlisted large datasets appear explicitly as skipped. Accepted Parquet files embed
the complete candidate specification in metadata, and those metadata bytes are included
in every reported compressed size.

The plots compare one result per strategy. If a strategy has no fully validated,
size-positive candidate, its bar is set to the original size and drawn with hatching;
failed strategies are not omitted. The generic algorithmic heuristic and historical
dataset-specific methods are shown separately. `comparison_plot_data.csv` is the
auditable source for both plots.

## Tests

```bash
python -m pytest -q tests/test_agentic_*.py
```

The default tests mock OpenAI. Live calls and Wikipedia downloads are intentionally
opt-in:

```bash
RUN_AGENTIC_LIVE_TESTS=1 python -m pytest -q tests/test_agentic_live.py
```
