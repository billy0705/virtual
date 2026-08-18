from __future__ import annotations

import multiprocessing as mp
import queue
import re
import time
from dataclasses import dataclass
from typing import Any

import duckdb
import numpy as np
import pandas as pd
import sqlglot
from sqlglot import expressions as exp


class SQLValidationError(ValueError):
    pass


DISALLOWED_EXPRESSION_KEYS = {
    "alter",
    "cache",
    "command",
    "copy",
    "create",
    "delete",
    "drop",
    "grant",
    "insert",
    "load_data",
    "merge",
    "pragma",
    "revoke",
    "set",
    "transaction",
    "truncate_table",
    "uncache",
    "update",
    "use",
}

DISALLOWED_FUNCTIONS = {
    "current_date",
    "current_localtime",
    "current_localtimestamp",
    "current_time",
    "current_timestamp",
    "gen_random_uuid",
    "getenv",
    "getvariable",
    "glob",
    "http_get",
    "http_post",
    "nextval",
    "parquet_scan",
    "rand",
    "random",
    "read_blob",
    "read_csv",
    "read_csv_auto",
    "read_json",
    "read_json_auto",
    "read_ndjson",
    "read_parquet",
    "query",
    "query_table",
    "sqlite_scan",
    "uuid",
}

DISALLOWED_SQL_PATTERN = re.compile(
    r"\b(attach|call|copy|detach|export|force\s+install|import|install|load|pragma|set|use)\b",
    re.IGNORECASE,
)


def _function_name(node: exp.Expression) -> str | None:
    if isinstance(node, exp.Anonymous):
        return node.name.lower()
    if isinstance(node, exp.Func):
        try:
            return node.sql_name().lower()
        except Exception:
            return node.key.lower()
    return None


def validate_select_sql(sql: str, allowed_relation: str) -> exp.Expression:
    if not isinstance(sql, str) or not sql.strip():
        raise SQLValidationError("SQL must be a non-empty string")
    if len(sql) > 100_000:
        raise SQLValidationError("SQL exceeds the 100,000 character limit")
    if DISALLOWED_SQL_PATTERN.search(sql):
        raise SQLValidationError("SQL contains a disallowed command")

    try:
        statements = sqlglot.parse(sql, read="duckdb")
    except sqlglot.errors.ParseError as exc:
        raise SQLValidationError(f"DuckDB SQL parse failed: {exc}") from exc
    if len(statements) != 1:
        raise SQLValidationError("exactly one SQL statement is required")

    tree = statements[0]
    if tree.find(exp.Select) is None:
        raise SQLValidationError("only SELECT or WITH ... SELECT queries are allowed")

    for node in tree.walk():
        if node.key.lower() in DISALLOWED_EXPRESSION_KEYS:
            raise SQLValidationError(f"disallowed SQL expression: {node.key}")
        function_name = _function_name(node)
        if function_name and (
            function_name in DISALLOWED_FUNCTIONS
            or function_name.startswith("read_")
            or function_name.endswith("_scan")
        ):
            raise SQLValidationError(
                f"disallowed or nondeterministic function: {function_name}"
            )

    cte_names = {cte.alias_or_name.lower() for cte in tree.find_all(exp.CTE)}
    table_names = {table.name.lower() for table in tree.find_all(exp.Table)}
    allowed_names = {allowed_relation.lower(), *cte_names}
    unexpected = sorted(table_names - allowed_names)
    if unexpected:
        raise SQLValidationError(f"unapproved relation(s): {', '.join(unexpected)}")
    if allowed_relation.lower() not in table_names:
        raise SQLValidationError(
            f"query must read from the {allowed_relation!r} relation"
        )
    return tree


@dataclass(frozen=True)
class SandboxQueryResult:
    ok: bool
    rows: list[dict[str, Any]]
    columns: list[str]
    error: str | None = None
    elapsed_seconds: float = 0.0


def _safe_scalar(value: Any) -> Any:
    try:
        missing = pd.isna(value)
        if isinstance(missing, (bool, np.bool_)) and missing:
            return None
    except Exception:
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _query_worker(
    result_queue: mp.Queue,
    df: pd.DataFrame,
    sql: str,
    relation: str,
    max_rows: int,
    max_columns: int,
    max_output_bytes: int,
    memory_limit_mb: int,
) -> None:
    started = time.monotonic()
    con = None
    try:
        con = duckdb.connect(
            database=":memory:",
            config={
                "enable_external_access": "false",
                "threads": "1",
                "memory_limit": f"{memory_limit_mb}MB",
            },
        )
        con.register(relation, df)
        result = con.execute(sql).fetchdf()
        if len(result) > max_rows:
            raise ValueError(f"query returned {len(result)} rows; limit is {max_rows}")
        if len(result.columns) > max_columns:
            raise ValueError(
                f"query returned {len(result.columns)} columns; limit is {max_columns}"
            )
        estimated_bytes = int(result.memory_usage(index=True, deep=True).sum())
        if estimated_bytes > max_output_bytes:
            raise ValueError(
                f"query output uses approximately {estimated_bytes} bytes; "
                f"limit is {max_output_bytes}"
            )
        rows = [
            {name: _safe_scalar(value) for name, value in row.items()}
            for row in result.to_dict(orient="records")
        ]
        result_queue.put(
            {
                "ok": True,
                "rows": rows,
                "columns": list(result.columns),
                "elapsed_seconds": time.monotonic() - started,
            }
        )
    except Exception as exc:
        result_queue.put(
            {
                "ok": False,
                "rows": [],
                "columns": [],
                "error": f"{type(exc).__name__}: {exc}",
                "elapsed_seconds": time.monotonic() - started,
            }
        )
    finally:
        if con is not None:
            con.close()


def _mp_context() -> mp.context.BaseContext:
    methods = mp.get_all_start_methods()
    return mp.get_context("fork" if "fork" in methods else "spawn")


def run_profile_query(
    df: pd.DataFrame,
    sql: str,
    *,
    relation: str = "source",
    timeout_seconds: float = 10.0,
    max_rows: int = 100,
    max_columns: int = 20,
    max_output_bytes: int = 64_000,
    memory_limit_mb: int = 512,
) -> SandboxQueryResult:
    validate_select_sql(sql, relation)
    context = _mp_context()
    result_queue = context.Queue(maxsize=1)
    process = context.Process(
        target=_query_worker,
        args=(
            result_queue,
            df,
            sql,
            relation,
            max_rows,
            max_columns,
            max_output_bytes,
            memory_limit_mb,
        ),
    )
    process.start()
    process.join(timeout_seconds)
    if process.is_alive():
        process.terminate()
        process.join(2)
        return SandboxQueryResult(
            ok=False,
            rows=[],
            columns=[],
            error=f"query exceeded {timeout_seconds:.1f}s timeout",
            elapsed_seconds=timeout_seconds,
        )
    try:
        payload = result_queue.get_nowait()
    except queue.Empty:
        return SandboxQueryResult(
            ok=False,
            rows=[],
            columns=[],
            error=f"query worker exited with code {process.exitcode} without a result",
        )
    return SandboxQueryResult(**payload)
