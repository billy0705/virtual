from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
from matplotlib.patches import Patch


STRATEGY_LABELS = {
    "original": "Original",
    "heuristic": "Algorithmic auto-prefix/suffix",
    "manual": "Historical hand-written",
    "single": "Agent single",
    "two_stage": "Agent two-stage",
    "tool_loop": "Agent tool-loop",
}

STRATEGY_COLORS = {
    "original": "#6B7280",
    "heuristic": "#0F766E",
    "manual": "#D97706",
    "single": "#2563EB",
    "two_stage": "#7C3AED",
    "tool_loop": "#DC2626",
}


def _strategy_order(results: dict[str, Any]) -> list[str]:
    configured = [str(item).replace("-", "_") for item in results.get("strategies", [])]
    return ["original", "heuristic", "manual", *configured]


def _selected_candidate(
    group: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    selected_id = group.get("selected_candidate_id")
    if not selected_id:
        return None
    for item in group.get("candidates", []):
        candidate = item.get("candidate")
        if not candidate or candidate.get("id") != selected_id:
            continue
        full = next(
            (
                phase
                for phase in item.get("evaluations", [])
                if phase.get("split") == "full" and phase.get("valid")
            ),
            None,
        )
        if full is not None:
            return candidate, full
    return None


def _comparison_rows(
    results: dict[str, Any], codec: str = "snappy"
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    strategy_order = _strategy_order(results)
    for dataset in results.get("datasets", []):
        if dataset.get("status") == "skipped":
            continue
        original_bytes = dataset.get("original", {}).get("codec_sizes", {}).get(codec)
        if original_bytes is None:
            continue
        dataset_label = dataset.get("config_name") or dataset.get("dataset_id")
        groups = {group.get("strategy"): group for group in dataset.get("groups", [])}
        for strategy in strategy_order:
            candidate = None
            reason = None
            status = "original"
            compressed_bytes = original_bytes
            fallback_to_original = strategy != "original"
            if strategy != "original":
                group = groups.get(strategy)
                selected = _selected_candidate(group or {})
                if selected is not None:
                    candidate, full = selected
                    codec_size = full.get("codec_sizes", {}).get(codec)
                    if codec_size is not None:
                        compressed_bytes = codec_size["compressed_bytes"]
                        fallback_to_original = False
                        status = "valid"
                    else:
                        reason = f"selected candidate has no {codec} measurement"
                else:
                    status = (group or {}).get("status", "skipped")
                    reason = (group or {}).get("reason", "strategy was not run")
            rows.append(
                {
                    "dataset_id": dataset.get("dataset_id"),
                    "config_name": dataset.get("config_name"),
                    "dataset_label": dataset_label,
                    "rows": dataset.get("rows"),
                    "codec": codec,
                    "strategy": strategy,
                    "strategy_label": STRATEGY_LABELS.get(strategy, strategy),
                    "candidate_id": candidate.get("id") if candidate else "identity",
                    "status": status,
                    "fallback_to_original": fallback_to_original,
                    "original_bytes": original_bytes,
                    "compressed_bytes": compressed_bytes,
                    "size_ratio": compressed_bytes / original_bytes
                    if original_bytes
                    else 1.0,
                    "savings_bytes": original_bytes - compressed_bytes,
                    "savings_ratio": (original_bytes - compressed_bytes)
                    / original_bytes
                    if original_bytes
                    else 0.0,
                    "reason": reason,
                    "candidate": candidate,
                }
            )
    return rows


def _legend_handles(strategy_order: list[str]) -> list[Patch]:
    handles = [
        Patch(
            facecolor=STRATEGY_COLORS.get(strategy, "#374151"),
            edgecolor="#111827",
            label=STRATEGY_LABELS.get(strategy, strategy),
        )
        for strategy in strategy_order
    ]
    handles.append(
        Patch(
            facecolor="white",
            edgecolor="#111827",
            hatch="///",
            label="Identity fallback (no valid candidate)",
        )
    )
    return handles


def _candidate_rows(results: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dataset in results.get("datasets", []):
        base = {
            "dataset_id": dataset.get("dataset_id"),
            "config_name": dataset.get("config_name"),
            "rows": dataset.get("rows", 0),
        }
        if dataset.get("status") == "skipped":
            rows.append(
                {
                    **base,
                    "group": "dataset",
                    "strategy": "",
                    "candidate_id": "",
                    "status": "skipped",
                    "valid": False,
                    "selected": False,
                    "reason": dataset.get("reason", ""),
                }
            )
            continue
        original = dataset.get("original", {})
        original_row = {
            **base,
            "group": "original",
            "strategy": "original",
            "candidate_id": "original",
            "status": "valid",
            "valid": True,
            "selected": False,
            "reason": "",
        }
        for codec, size in original.get("codec_sizes", {}).items():
            original_row[f"{codec}_base_bytes"] = size
            original_row[f"{codec}_compressed_bytes"] = size
            original_row[f"{codec}_savings_bytes"] = 0
            original_row[f"{codec}_savings_ratio"] = 0.0
        rows.append(original_row)

        for group in dataset.get("groups", []):
            strategy = group.get("strategy", group.get("name", ""))
            usage = group.get("usage", [])
            usage_totals = {
                "api_calls": group.get("calls", 0),
                "tool_calls": group.get("tool_calls", 0),
                "input_tokens": sum(item.get("input_tokens", 0) for item in usage),
                "output_tokens": sum(item.get("output_tokens", 0) for item in usage),
                "total_tokens": sum(item.get("total_tokens", 0) for item in usage),
            }
            if not group.get("candidates"):
                rows.append(
                    {
                        **base,
                        **usage_totals,
                        "group": group.get("name", ""),
                        "strategy": strategy,
                        "candidate_id": "",
                        "status": group.get("status", "skipped"),
                        "valid": False,
                        "selected": False,
                        "reason": group.get("reason", ""),
                    }
                )
                continue
            for candidate in group["candidates"]:
                phases = candidate.get("evaluations", [])
                final = phases[-1] if phases else {}
                row = {
                    **base,
                    **usage_totals,
                    "group": group.get("name", ""),
                    "strategy": strategy,
                    "candidate_id": candidate.get("candidate", {}).get(
                        "id", candidate.get("id", "")
                    ),
                    "status": final.get("status", candidate.get("status", "skipped")),
                    "valid": final.get("valid", False),
                    "selected": candidate.get("selected", False),
                    "reason": final.get("reason", candidate.get("reason", "")),
                    "reconstruction_latency_ms": final.get("reconstruction_latency_ms"),
                    "auxiliary_columns": final.get("auxiliary_columns", 0),
                }
                for codec, sizes in final.get("codec_sizes", {}).items():
                    for key, value in sizes.items():
                        row[f"{codec}_{key}"] = value
                rows.append(row)
    return rows


class ResultReporter:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir

    def initialize(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=False)
        (self.run_dir / "candidates").mkdir()
        (self.run_dir / "artifacts").mkdir()

    def write(self, results: dict[str, Any]) -> None:
        (self.run_dir / "results.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        rows = _candidate_rows(results)
        self._write_csv(rows)
        self._write_markdown(rows)
        self._write_candidate_sql(results)
        comparison_rows = _comparison_rows(results)
        self._write_comparison_csv(comparison_rows)
        self._write_function_catalog(results, comparison_rows)
        self._write_comparison_plots(results, comparison_rows)

    def _write_csv(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            (self.run_dir / "summary.csv").write_text("", encoding="utf-8")
            return
        fieldnames = sorted({key for row in rows for key in row})
        with (self.run_dir / "summary.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _write_markdown(self, rows: list[dict[str, Any]]) -> None:
        columns = [
            "dataset_id",
            "config_name",
            "strategy",
            "candidate_id",
            "status",
            "selected",
            "snappy_savings_ratio",
            "reconstruction_latency_ms",
            "total_tokens",
            "reason",
        ]
        lines = [
            "# Agentic String Compression Results",
            "",
            "| " + " | ".join(columns) + " |",
            "| " + " | ".join("---" for _ in columns) + " |",
        ]
        for row in rows:
            values = []
            for column in columns:
                value = row.get(column, "")
                if isinstance(value, float):
                    value = f"{value:.6f}"
                values.append(
                    str(value if value is not None else "").replace("|", "\\|")
                )
            lines.append("| " + " | ".join(values) + " |")
        (self.run_dir / "summary.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    def _write_candidate_sql(self, results: dict[str, Any]) -> None:
        root = self.run_dir / "candidates"
        for dataset in results.get("datasets", []):
            dataset_name = f"{dataset.get('dataset_id', 'dataset')}__{dataset.get('config_name', 'default')}".replace(
                "/", "_"
            ).replace(" ", "_")
            for group in dataset.get("groups", []):
                group_name = str(group.get("name", "group")).replace("/", "_")
                for result in group.get("candidates", []):
                    candidate = result.get("candidate")
                    if not candidate:
                        continue
                    candidate_id = candidate["id"].replace("/", "_")
                    path = root / f"{dataset_name}__{group_name}__{candidate_id}.sql"
                    path.write_text(
                        "-- Compression\n"
                        + candidate["compression_sql"].strip()
                        + ";\n\n-- Reconstruction\n"
                        + candidate["reconstruction_sql"].strip()
                        + ";\n",
                        encoding="utf-8",
                    )

    def _write_comparison_csv(self, rows: list[dict[str, Any]]) -> None:
        columns = [
            "dataset_id",
            "config_name",
            "dataset_label",
            "rows",
            "codec",
            "strategy",
            "strategy_label",
            "candidate_id",
            "status",
            "fallback_to_original",
            "original_bytes",
            "compressed_bytes",
            "size_ratio",
            "savings_bytes",
            "savings_ratio",
            "reason",
        ]
        with (self.run_dir / "comparison_plot_data.csv").open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(
                {column: row.get(column) for column in columns} for row in rows
            )

    def _write_function_catalog(
        self, results: dict[str, Any], rows: list[dict[str, Any]]
    ) -> None:
        lines = [
            "# Benchmark Compression Functions",
            "",
            f"Run: `{results.get('run_id', self.run_dir.name)}`  ",
            f"Prompt: `{results.get('prompt_version', 'not applicable')}`  ",
            f"Model: `{results.get('model') or 'offline'}`  ",
            "Codec: `snappy`",
            "",
            "Every non-identity function below passed discovery, disjoint holdout, and "
            "exact full-data reconstruction. The measured candidate size includes the "
            "serialized candidate specification in Parquet metadata. A strategy without "
            "a valid size-positive candidate uses the explicit identity fallback so that "
            "it remains visible in the comparison.",
        ]
        current_dataset = None
        for row in rows:
            dataset_key = (row["dataset_id"], row["config_name"])
            if dataset_key != current_dataset:
                current_dataset = dataset_key
                lines.extend(
                    [
                        "",
                        f"## {row['dataset_id']} / {row['dataset_label']}",
                        "",
                        f"Rows: `{row.get('rows')}`; original Snappy bytes: "
                        f"`{row['original_bytes']}`.",
                    ]
                )
            lines.extend(
                [
                    "",
                    f"### {row['strategy_label']}",
                    "",
                    f"Candidate: `{row['candidate_id']}`  ",
                    f"Status: `{row['status']}`  ",
                    f"Compressed bytes: `{row['compressed_bytes']}`  ",
                    f"Size ratio: `{row['size_ratio']:.6f}`",
                ]
            )
            candidate = row.get("candidate")
            if candidate is None:
                if row.get("reason"):
                    lines.append(f"Reason: {row['reason']}")
                lines.extend(
                    [
                        "",
                        "Compression function: identity.",
                        "",
                        "```sql",
                        "SELECT * FROM source",
                        "```",
                        "",
                        "Reconstruction function: identity.",
                        "",
                        "```sql",
                        "SELECT * FROM compressed",
                        "```",
                    ]
                )
                continue

            residuals = ", ".join(
                item["name"] for item in candidate.get("residual_columns", [])
            )
            lines.extend(
                [
                    f"Summary: {candidate['summary']}",
                    f"Targets: `{', '.join(candidate['target_columns'])}`  ",
                    f"References: `{', '.join(candidate['reference_columns']) or '(none)'}`  ",
                    f"Residuals: `{residuals or '(none)'}`",
                    "",
                    "Compression SQL:",
                    "",
                    "```sql",
                    candidate["compression_sql"].strip(),
                    "```",
                    "",
                    "Reconstruction SQL:",
                    "",
                    "```sql",
                    candidate["reconstruction_sql"].strip(),
                    "```",
                ]
            )
        (self.run_dir / "compression_functions.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )

    def _write_comparison_plots(
        self, results: dict[str, Any], rows: list[dict[str, Any]]
    ) -> None:
        if not rows:
            return
        strategy_order = _strategy_order(results)
        dataset_labels = list(dict.fromkeys(row["dataset_label"] for row in rows))
        lookup = {(row["dataset_label"], row["strategy"]): row for row in rows}
        x = np.arange(len(dataset_labels), dtype=float)
        width = min(0.13, 0.8 / max(len(strategy_order), 1))

        fig_width = max(10.0, len(dataset_labels) * 2.2)
        figure, axis = plt.subplots(figsize=(fig_width, 6.5), constrained_layout=True)
        measured_values = [
            row["compressed_bytes"] for row in rows if row["compressed_bytes"]
        ]
        use_log_scale = (
            bool(measured_values) and max(measured_values) / min(measured_values) >= 20
        )
        for index, strategy in enumerate(strategy_order):
            strategy_rows = [lookup[(label, strategy)] for label in dataset_labels]
            values = [row["compressed_bytes"] / (1024 * 1024) for row in strategy_rows]
            positions = x + (index - (len(strategy_order) - 1) / 2) * width
            bars = axis.bar(
                positions,
                values,
                width=width,
                color=STRATEGY_COLORS.get(strategy, "#374151"),
                edgecolor="#111827",
                linewidth=0.5,
                label=STRATEGY_LABELS.get(strategy, strategy),
            )
            for bar, row in zip(bars, strategy_rows):
                if row["fallback_to_original"]:
                    bar.set_hatch("///")
                    bar.set_alpha(0.55)
        if use_log_scale:
            axis.set_yscale("log")
        axis.set_ylabel(
            "Size after Snappy compression (MiB)"
            + (" - logarithmic scale" if use_log_scale else "")
        )
        axis.set_xlabel("Dataset configuration")
        axis.set_xticks(x, dataset_labels, rotation=20, ha="right")
        axis.set_title("Lossless String Reconstruction: Absolute Stored Size")
        axis.grid(axis="y", color="#D1D5DB", linewidth=0.7, alpha=0.8)
        axis.set_axisbelow(True)
        axis.legend(
            handles=_legend_handles(strategy_order),
            frameon=False,
            loc="upper left",
            bbox_to_anchor=(1.01, 1),
        )
        figure.savefig(
            self.run_dir / "compression_sizes_snappy.png",
            dpi=180,
            bbox_inches="tight",
        )
        figure.savefig(
            self.run_dir / "compression_sizes_snappy.pdf", bbox_inches="tight"
        )
        plt.close(figure)

        figure, axis = plt.subplots(figsize=(fig_width, 6.5), constrained_layout=True)
        for index, strategy in enumerate(strategy_order):
            strategy_rows = [lookup[(label, strategy)] for label in dataset_labels]
            values = [100 * row["size_ratio"] for row in strategy_rows]
            positions = x + (index - (len(strategy_order) - 1) / 2) * width
            bars = axis.bar(
                positions,
                values,
                width=width,
                color=STRATEGY_COLORS.get(strategy, "#374151"),
                edgecolor="#111827",
                linewidth=0.5,
                label=STRATEGY_LABELS.get(strategy, strategy),
            )
            for bar, row in zip(bars, strategy_rows):
                if row["fallback_to_original"]:
                    bar.set_hatch("///")
                    bar.set_alpha(0.55)
        axis.axhline(100, color="#111827", linewidth=1, linestyle="--")
        axis.set_ylabel("Stored size relative to original Snappy file (%)")
        axis.set_xlabel("Dataset configuration")
        axis.set_xticks(x, dataset_labels, rotation=20, ha="right")
        axis.set_ylim(bottom=0)
        axis.set_title("Lossless String Reconstruction: Relative Stored Size")
        axis.grid(axis="y", color="#D1D5DB", linewidth=0.7, alpha=0.8)
        axis.set_axisbelow(True)
        axis.legend(
            handles=_legend_handles(strategy_order),
            frameon=False,
            loc="upper left",
            bbox_to_anchor=(1.01, 1),
        )
        figure.savefig(
            self.run_dir / "compression_ratios_snappy.png",
            dpi=180,
            bbox_inches="tight",
        )
        figure.savefig(
            self.run_dir / "compression_ratios_snappy.pdf", bbox_inches="tight"
        )
        plt.close(figure)
