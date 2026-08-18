from urllib.parse import quote

import pandas as pd

from string_compression.agentic.evaluator import CandidateEvaluator
from string_compression.agentic.models import CandidateSpec, ResidualColumn
from string_compression.agentic.profiler import profile_dataframe, split_dataset


def candidate(**overrides):
    data = {
        "id": "candidate",
        "summary": "Test candidate.",
        "target_columns": ["target"],
        "reference_columns": ["source_text"],
        "residual_columns": [],
        "compression_sql": 'SELECT * EXCLUDE ("target") FROM source',
        "reconstruction_sql": 'SELECT *, "source_text" AS "target" FROM compressed',
    }
    data.update(overrides)
    return CandidateSpec(**data)


def test_exact_multi_operation_reconstruction():
    frame = pd.DataFrame(
        {
            "source_text": ["Alpha", "", None, "Straße"],
            "lower_text": ["alpha", "", None, "straße"],
            "wrapped": ["<Alpha>", "<>", None, "<Straße>"],
        }
    )
    spec = CandidateSpec(
        id="lower_concat",
        summary="Derive lowercase and wrapped strings.",
        target_columns=["lower_text", "wrapped"],
        reference_columns=["source_text"],
        residual_columns=[],
        compression_sql='SELECT * EXCLUDE ("lower_text", "wrapped") FROM source',
        reconstruction_sql="""
            SELECT *, lower("source_text") AS "lower_text",
                   CASE WHEN "source_text" IS NULL THEN NULL
                        ELSE '<' || "source_text" || '>' END AS "wrapped"
            FROM compressed
        """,
    )
    evaluation = CandidateEvaluator(split_dataset(frame)).evaluate(
        spec, require_gain=False
    )
    assert evaluation.valid, evaluation.reason


def test_trim_split_and_url_encoding_reconstruction():
    source_values = [" Alpha |One ", "", None, "Straße|東京"]
    frame = pd.DataFrame(
        {
            "source_text": source_values,
            "trimmed": ["Alpha |One", "", None, "Straße|東京"],
            "first_part": [" Alpha ", "", None, "Straße"],
            "second_part": ["One ", "", None, "東京"],
            "encoded": [
                quote(value, safe="") if value is not None else None
                for value in source_values
            ],
        }
    )
    spec = CandidateSpec(
        id="trim_split_url",
        summary="Derive trimmed, split, and URL-encoded strings.",
        target_columns=["trimmed", "first_part", "second_part", "encoded"],
        reference_columns=["source_text"],
        residual_columns=[],
        compression_sql=(
            'SELECT * EXCLUDE ("trimmed", "first_part", "second_part", "encoded") '
            "FROM source"
        ),
        reconstruction_sql="""
            SELECT *, trim("source_text") AS "trimmed",
                   split_part("source_text", '|', 1) AS "first_part",
                   split_part("source_text", '|', 2) AS "second_part",
                   url_encode("source_text") AS "encoded"
            FROM compressed
        """,
    )
    evaluation = CandidateEvaluator(split_dataset(frame)).evaluate(
        spec, require_gain=False
    )
    assert evaluation.valid, evaluation.reason


def test_agent_designed_error_columns_are_lossless():
    frame = pd.DataFrame(
        {
            "source_text": ["ALPHA", "BETA", None, ""],
            "target": ["alpha", "special", None, ""],
        }
    )
    predicate = '"target" IS NOT DISTINCT FROM lower("source_text")'
    spec = candidate(
        id="lower_with_errors",
        residual_columns=[
            ResidualColumn(name="__v_error", purpose="Exceptional target value"),
            ResidualColumn(name="__v_error_present", purpose="Fallback indicator"),
        ],
        compression_sql=f"""
            SELECT * EXCLUDE ("target"),
                   CASE WHEN {predicate} THEN NULL ELSE "target" END AS "__v_error",
                   NOT {predicate} AS "__v_error_present"
            FROM source
        """,
        reconstruction_sql="""
            SELECT * EXCLUDE ("__v_error", "__v_error_present"),
                   CASE WHEN "__v_error_present" THEN "__v_error"
                        ELSE lower("source_text") END AS "target"
            FROM compressed
        """,
    )
    evaluation = CandidateEvaluator(split_dataset(frame)).evaluate(
        spec, require_gain=False
    )
    assert evaluation.valid, evaluation.reason


def test_lossy_and_cardinality_changing_candidates_are_rejected():
    frame = pd.DataFrame(
        {"source_text": ["A", "B", "C"], "target": ["A", "wrong", "C"]}
    )
    evaluator = CandidateEvaluator(split_dataset(frame))

    lossy = evaluator.evaluate(candidate(), require_gain=False)
    assert not lossy.valid
    assert lossy.status == "invalid"
    assert lossy.mismatch_count == 1
    assert lossy.counterexamples[0].column == "target"

    cardinality = evaluator.evaluate(
        candidate(
            id="cardinality",
            compression_sql='SELECT * EXCLUDE ("target") FROM source LIMIT 1',
        ),
        require_gain=False,
    )
    assert not cardinality.valid
    assert "row count" in cardinality.reason

    duplicate_ids = evaluator.evaluate(
        candidate(
            id="duplicate_ids",
            compression_sql="""
                SELECT * EXCLUDE ("target") FROM source
                WHERE "__virtual_row_id" <> 2
                UNION ALL
                SELECT * EXCLUDE ("target") FROM source
                WHERE "__virtual_row_id" = 1
            """,
        ),
        require_gain=False,
    )
    assert not duplicate_ids.valid
    assert "non-null and unique" in duplicate_ids.reason


def test_schema_type_and_output_size_changes_are_rejected():
    frame = pd.DataFrame(
        {"number": [1, 2, 3], "source_text": ["A", "B", "C"], "target": ["A", "B", "C"]}
    )
    evaluator = CandidateEvaluator(split_dataset(frame))

    missing_column = evaluator.evaluate(
        candidate(reconstruction_sql="SELECT * FROM compressed"), require_gain=False
    )
    assert not missing_column.valid
    assert "schema mismatch" in missing_column.reason

    changed_type = evaluator.evaluate(
        candidate(
            id="changed_type",
            reconstruction_sql="""
                SELECT * EXCLUDE ("number"),
                       CAST("number" AS DOUBLE) AS "number",
                       "source_text" AS "target"
                FROM compressed
            """,
        ),
        require_gain=False,
    )
    assert not changed_type.valid
    assert "type mismatch" in changed_type.reason

    large_output = evaluator.evaluate(
        candidate(
            id="large_output",
            residual_columns=[
                ResidualColumn(name="huge", purpose="Deliberately oversized output")
            ],
            compression_sql="""
                SELECT * EXCLUDE ("target"),
                       repeat("source_text", 400000) AS "huge"
                FROM source
            """,
            reconstruction_sql="""
                SELECT * EXCLUDE ("huge"), "source_text" AS "target"
                FROM compressed
            """,
        ),
        require_gain=False,
    )
    assert not large_output.valid
    assert "limit is" in large_output.reason


def test_non_positive_candidate_is_rejected():
    frame = pd.DataFrame({"source_text": ["A"], "target": ["A"]})
    evaluation = CandidateEvaluator(split_dataset(frame)).evaluate(candidate())
    assert not evaluation.valid
    assert evaluation.status == "rejected"
    assert "does not reduce" in evaluation.reason


def test_profile_truncates_values_and_reports_duckdb_types():
    frame = split_dataset(
        pd.DataFrame({"left": ["x" * 300], "right": ["x" * 300]})
    ).discovery
    profile = profile_dataframe(frame)
    left = next(column for column in profile["columns"] if column["name"] == "left")
    assert left["duckdb_type"] == "VARCHAR"
    assert len(profile["sample_rows"][0]["left"]) == 256
