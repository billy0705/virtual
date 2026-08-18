from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import duckdb
import numpy as np
import pandas as pd

from .models import ROW_ID_COLUMN


PROMPT_ROW_COUNT = 32
PROMPT_VALUE_LIMIT = 256
DISCOVERY_ROWS = 1_000
HOLDOUT_ROWS = 10_000


@dataclass(frozen=True)
class DatasetSamples:
    full: pd.DataFrame
    discovery: pd.DataFrame
    holdout: pd.DataFrame


def with_row_id(df: pd.DataFrame) -> pd.DataFrame:
    if ROW_ID_COLUMN in df.columns:
        raise ValueError(f"input contains reserved column {ROW_ID_COLUMN}")
    result = df.reset_index(drop=True).copy()
    result.insert(0, ROW_ID_COLUMN, np.arange(len(result), dtype=np.int64))
    return result


def split_dataset(
    df: pd.DataFrame,
    *,
    discovery_rows: int = DISCOVERY_ROWS,
    holdout_rows: int = HOLDOUT_ROWS,
    random_state: int = 42,
) -> DatasetSamples:
    full = with_row_id(df)
    if full.empty:
        return DatasetSamples(full=full, discovery=full.copy(), holdout=full.copy())

    permutation = np.random.default_rng(random_state).permutation(len(full))
    discovery_count = min(discovery_rows, len(full))
    discovery_positions = permutation[:discovery_count]
    remaining = permutation[discovery_count:]
    holdout_positions = remaining[: min(holdout_rows, len(remaining))]

    discovery = (
        full.iloc[discovery_positions].sort_values(ROW_ID_COLUMN).reset_index(drop=True)
    )
    if len(holdout_positions):
        holdout = (
            full.iloc[holdout_positions]
            .sort_values(ROW_ID_COLUMN)
            .reset_index(drop=True)
        )
    else:
        holdout = discovery.copy()
    return DatasetSamples(full=full, discovery=discovery, holdout=holdout)


def _duckdb_types(df: pd.DataFrame) -> dict[str, str]:
    con = duckdb.connect(database=":memory:")
    try:
        con.register("profile_source", df)
        described = con.execute("DESCRIBE SELECT * FROM profile_source").fetchdf()
        return dict(zip(described["column_name"], described["column_type"]))
    finally:
        con.close()


def _common_prefix(values: list[str]) -> str:
    if not values:
        return ""
    prefix = values[0]
    for value in values[1:]:
        while prefix and not value.startswith(prefix):
            prefix = prefix[:-1]
        if not prefix:
            break
    return prefix[:64]


def _common_suffix(values: list[str]) -> str:
    reversed_values = [value[::-1] for value in values]
    return _common_prefix(reversed_values)[::-1]


def _prompt_value(value: Any, limit: int = PROMPT_VALUE_LIMIT) -> Any:
    try:
        missing = pd.isna(value)
        if isinstance(missing, (bool, np.bool_)) and missing:
            return None
    except Exception:
        pass
    if isinstance(value, (np.integer, np.floating, np.bool_)):
        return value.item()
    if isinstance(value, (pd.Timestamp, pd.Timedelta)):
        return str(value)
    if isinstance(value, (bytes, bytearray)):
        return repr(bytes(value)[:limit])
    if isinstance(value, str):
        return value[:limit]
    return value if isinstance(value, (int, float, bool)) else str(value)[:limit]


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    types = _duckdb_types(df)
    columns: list[dict[str, Any]] = []
    for name in df.columns:
        series = df[name]
        non_null = series.dropna()
        info: dict[str, Any] = {
            "name": name,
            "duckdb_type": types.get(name, str(series.dtype)),
            "rows": int(len(series)),
            "null_fraction": float(series.isna().mean()) if len(series) else 0.0,
            "distinct_count": int(non_null.nunique(dropna=True)),
        }
        is_string = pd.api.types.is_string_dtype(
            series.dtype
        ) or pd.api.types.is_object_dtype(series.dtype)
        if is_string:
            strings = non_null.astype(str)
            lengths = strings.str.len()
            representative = strings.drop_duplicates().head(128).tolist()
            info.update(
                {
                    "kind": "string",
                    "min_length": int(lengths.min()) if len(lengths) else 0,
                    "mean_length": float(lengths.mean()) if len(lengths) else 0.0,
                    "max_length": int(lengths.max()) if len(lengths) else 0,
                    "common_prefix": _common_prefix(representative),
                    "common_suffix": _common_suffix(representative),
                }
            )
        else:
            info["kind"] = "other"
        columns.append(info)

    sample = df.head(min(PROMPT_ROW_COUNT, len(df)))
    rows = [
        {name: _prompt_value(value) for name, value in row.items()}
        for row in sample.to_dict(orient="records")
    ]
    return {"row_count": len(df), "columns": columns, "sample_rows": rows}


def profile_json(df: pd.DataFrame) -> str:
    return json.dumps(profile_dataframe(df), ensure_ascii=False, indent=2)
