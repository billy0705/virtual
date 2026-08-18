import time

import pandas as pd
import pytest

import string_compression.agentic.sandbox as sandbox_module
from string_compression.agentic.sandbox import (
    SQLValidationError,
    run_profile_query,
    validate_select_sql,
)


def slow_query_worker(*_args):
    time.sleep(1)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM source",
        "WITH cleaned AS (SELECT lower(name) AS name FROM source) SELECT * FROM cleaned",
        "SELECT regexp_replace(name, '[0-9]', '', 'g') FROM source",
    ],
)
def test_allows_read_only_selects(sql):
    validate_select_sql(sql, "source")


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM read_parquet('/tmp/private.parquet')",
        "SELECT * FROM read_text('/tmp/private.txt')",
        "SELECT * FROM query('SELECT 42')",
        "COPY source TO '/tmp/output.csv'",
        "INSTALL httpfs",
        "LOAD httpfs",
        "DELETE FROM source",
        "SELECT random() FROM source",
        "SELECT * FROM other_table",
        "SELECT * FROM source; SELECT * FROM source",
    ],
)
def test_rejects_unsafe_or_unapproved_sql(sql):
    with pytest.raises(SQLValidationError):
        validate_select_sql(sql, "source")


def test_profile_query_is_bounded():
    frame = pd.DataFrame({"name": ["A", "B", "C"]})
    result = run_profile_query(frame, "SELECT lower(name) AS name FROM source")
    assert result.ok
    assert result.rows == [{"name": "a"}, {"name": "b"}, {"name": "c"}]

    oversized = run_profile_query(frame, "SELECT * FROM source", max_rows=2)
    assert not oversized.ok
    assert "limit is 2" in oversized.error


def test_profile_query_timeout(monkeypatch):
    monkeypatch.setattr(sandbox_module, "_query_worker", slow_query_worker)
    result = run_profile_query(
        pd.DataFrame({"name": ["A"]}),
        "SELECT * FROM source",
        timeout_seconds=0.01,
    )
    assert not result.ok
    assert "timeout" in result.error
