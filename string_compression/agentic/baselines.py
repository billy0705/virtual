from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from .models import CandidateSpec, ResidualColumn, ROW_ID_COLUMN


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "candidate"


def _is_missing(value: object) -> bool:
    try:
        result = pd.isna(value)
        return bool(result) if isinstance(result, bool) else False
    except Exception:
        return False


def _containment_rate(
    target: pd.Series, reference: pd.Series, target_in_reference: bool
) -> float:
    matches = 0
    for target_value, reference_value in zip(target.tolist(), reference.tolist()):
        target_missing = _is_missing(target_value)
        reference_missing = _is_missing(reference_value)
        if target_missing or reference_missing:
            matches += int(target_missing and reference_missing)
            continue
        left = str(target_value)
        right = str(reference_value)
        matches += int(left in right if target_in_reference else right in left)
    return matches / len(target) if len(target) else 0.0


def _equality_rate(target: pd.Series, reference: pd.Series) -> float:
    matches = 0
    for target_value, reference_value in zip(target.tolist(), reference.tolist()):
        target_missing = _is_missing(target_value)
        reference_missing = _is_missing(reference_value)
        if target_missing or reference_missing:
            matches += int(target_missing and reference_missing)
        else:
            matches += int(target_value == reference_value)
    return matches / len(target) if len(target) else 0.0


def heuristic_candidates(
    sample: pd.DataFrame,
    *,
    threshold: float = 0.9,
    max_candidates: int = 20,
) -> list[CandidateSpec]:
    string_columns = [
        name
        for name in sample.columns
        if name != ROW_ID_COLUMN
        and (
            pd.api.types.is_string_dtype(sample[name].dtype)
            or pd.api.types.is_object_dtype(sample[name].dtype)
        )
    ]
    ranked: list[tuple[float, CandidateSpec]] = []
    for target_index, target in enumerate(string_columns):
        for reference_index, reference in enumerate(string_columns):
            if target == reference:
                continue
            target_q = quote_identifier(target)
            reference_q = quote_identifier(reference)

            equality_rate = _equality_rate(sample[target], sample[reference])
            if equality_rate >= threshold:
                stem = _safe_id(
                    f"{target_index}_{target}_equals_{reference_index}_{reference}"
                )
                if equality_rate == 1.0:
                    compression_sql = f"SELECT * EXCLUDE ({target_q}) FROM source"
                    reconstruction_sql = (
                        f"SELECT *, {reference_q} AS {target_q} FROM compressed"
                    )
                    residuals: list[ResidualColumn] = []
                else:
                    fallback = f"__v_{stem}_error"
                    present = f"__v_{stem}_error_present"
                    condition = f"{target_q} IS NOT DISTINCT FROM {reference_q}"
                    compression_sql = f"""
                        SELECT * EXCLUDE ({target_q}),
                               CASE WHEN {condition} THEN NULL ELSE {target_q} END AS {quote_identifier(fallback)},
                               NOT {condition} AS {quote_identifier(present)}
                        FROM source
                    """
                    reconstruction_sql = f"""
                        SELECT * EXCLUDE ({quote_identifier(fallback)}, {quote_identifier(present)}),
                               CASE WHEN {quote_identifier(present)}
                                    THEN {quote_identifier(fallback)}
                                    ELSE {reference_q}
                               END AS {target_q}
                        FROM compressed
                    """
                    residuals = [
                        ResidualColumn(
                            name=fallback, purpose="Full target for non-equal rows"
                        ),
                        ResidualColumn(
                            name=present, purpose="Whether the fallback is active"
                        ),
                    ]
                ranked.append(
                    (
                        equality_rate + 1.0,
                        CandidateSpec(
                            id=f"heuristic_{stem}",
                            summary=(
                                f"Reconstruct {target} from equal column {reference}; "
                                f"sample match rate {equality_rate:.3f}."
                            ),
                            target_columns=[target],
                            reference_columns=[reference],
                            residual_columns=residuals,
                            compression_sql=compression_sql.strip(),
                            reconstruction_sql=reconstruction_sql.strip(),
                        ),
                    )
                )
                continue

            slice_rate = _containment_rate(
                sample[target], sample[reference], target_in_reference=True
            )
            around_rate = _containment_rate(
                sample[target], sample[reference], target_in_reference=False
            )
            if max(slice_rate, around_rate) < threshold:
                continue

            stem = _safe_id(
                f"{target_index}_{target}_from_{reference_index}_{reference}"
            )
            if slice_rate >= around_rate:
                pos = f"__v_{stem}_pos"
                length = f"__v_{stem}_len"
                fallback = f"__v_{stem}_error"
                present = f"__v_{stem}_error_present"
                condition = (
                    f"(({target_q} IS NULL AND {reference_q} IS NULL) OR "
                    f"({target_q} IS NOT NULL AND {reference_q} IS NOT NULL "
                    f"AND strpos({reference_q}, {target_q}) > 0))"
                )
                compression_sql = f"""
                    SELECT * EXCLUDE ({target_q}),
                           CASE WHEN {condition} THEN strpos({reference_q}, {target_q}) ELSE NULL END AS {quote_identifier(pos)},
                           CASE WHEN {condition} THEN length({target_q}) ELSE NULL END AS {quote_identifier(length)},
                           CASE WHEN {condition} THEN NULL ELSE {target_q} END AS {quote_identifier(fallback)},
                           NOT {condition} AS {quote_identifier(present)}
                    FROM source
                """
                reconstruction_sql = f"""
                    SELECT * EXCLUDE ({quote_identifier(pos)}, {quote_identifier(length)}, {quote_identifier(fallback)}, {quote_identifier(present)}),
                           CASE WHEN {quote_identifier(present)}
                                THEN {quote_identifier(fallback)}
                                ELSE substr({reference_q}, {quote_identifier(pos)}, {quote_identifier(length)})
                           END AS {target_q}
                    FROM compressed
                """
                residuals = [
                    ResidualColumn(name=pos, purpose="One-based substring position"),
                    ResidualColumn(name=length, purpose="Substring length"),
                    ResidualColumn(
                        name=fallback, purpose="Full target for non-matching rows"
                    ),
                    ResidualColumn(
                        name=present, purpose="Whether the fallback is active"
                    ),
                ]
                summary = (
                    f"Reconstruct {target} as a substring of {reference}; "
                    f"sample match rate {slice_rate:.3f}."
                )
                score = slice_rate
            else:
                prefix = f"__v_{stem}_prefix"
                suffix = f"__v_{stem}_suffix"
                fallback = f"__v_{stem}_error"
                present = f"__v_{stem}_error_present"
                condition = (
                    f"(({target_q} IS NULL AND {reference_q} IS NULL) OR "
                    f"({target_q} IS NOT NULL AND {reference_q} IS NOT NULL "
                    f"AND strpos({target_q}, {reference_q}) > 0))"
                )
                position = f"strpos({target_q}, {reference_q})"
                compression_sql = f"""
                    SELECT * EXCLUDE ({target_q}),
                           CASE WHEN {condition} THEN left({target_q}, {position} - 1) ELSE NULL END AS {quote_identifier(prefix)},
                           CASE WHEN {condition} THEN substr({target_q}, {position} + length({reference_q})) ELSE NULL END AS {quote_identifier(suffix)},
                           CASE WHEN {condition} THEN NULL ELSE {target_q} END AS {quote_identifier(fallback)},
                           NOT {condition} AS {quote_identifier(present)}
                    FROM source
                """
                reconstruction_sql = f"""
                    SELECT * EXCLUDE ({quote_identifier(prefix)}, {quote_identifier(suffix)}, {quote_identifier(fallback)}, {quote_identifier(present)}),
                           CASE WHEN {quote_identifier(present)}
                                THEN {quote_identifier(fallback)}
                                ELSE {quote_identifier(prefix)} || {reference_q} || {quote_identifier(suffix)}
                           END AS {target_q}
                    FROM compressed
                """
                residuals = [
                    ResidualColumn(
                        name=prefix, purpose="Target text before the reference"
                    ),
                    ResidualColumn(
                        name=suffix, purpose="Target text after the reference"
                    ),
                    ResidualColumn(
                        name=fallback, purpose="Full target for non-matching rows"
                    ),
                    ResidualColumn(
                        name=present, purpose="Whether the fallback is active"
                    ),
                ]
                summary = (
                    f"Reconstruct {target} by surrounding {reference} with residual text; "
                    f"sample match rate {around_rate:.3f}."
                )
                score = around_rate

            ranked.append(
                (
                    score,
                    CandidateSpec(
                        id=f"heuristic_{stem}",
                        summary=summary,
                        target_columns=[target],
                        reference_columns=[reference],
                        residual_columns=residuals,
                        compression_sql=compression_sql.strip(),
                        reconstruction_sql=reconstruction_sql.strip(),
                    ),
                )
            )
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [candidate for _, candidate in ranked[:max_candidates]]


@dataclass(frozen=True)
class BaselineDefinition:
    name: str
    candidate: CandidateSpec | None
    reason: str | None = None


def _candidate(
    method_id: str,
    summary: str,
    targets: list[str],
    references: list[str],
    residuals: Iterable[tuple[str, str]],
    compression_sql: str,
    reconstruction_sql: str,
) -> BaselineDefinition:
    return BaselineDefinition(
        name=method_id,
        candidate=CandidateSpec(
            id=method_id,
            summary=summary,
            target_columns=targets,
            reference_columns=references,
            residual_columns=[
                ResidualColumn(name=name, purpose=purpose)
                for name, purpose in residuals
            ],
            compression_sql=compression_sql.strip(),
            reconstruction_sql=reconstruction_sql.strip(),
        ),
    )


def _wiki_baselines(config_name: str) -> list[BaselineDefinition]:
    language = config_name.rsplit(".", 1)[-1]
    prefix = quote_literal(f"https://{language}.wikipedia.org/wiki/")
    combine = "__v_wiki_title_text"
    title_len = "__v_wiki_title_len"
    method_1 = _candidate(
        "manual_wiki_1",
        "Drop URL and reconstruct it from the language prefix and encoded title.",
        ["url"],
        ["title"],
        [],
        'SELECT * EXCLUDE ("url") FROM source',
        f'SELECT *, {prefix} || url_encode("title") AS "url" FROM compressed',
    )
    method_2 = _candidate(
        "manual_wiki_2",
        "Concatenate title and text and retain the title length.",
        ["title", "text"],
        [],
        [(combine, "Concatenated title and text"), (title_len, "Title length")],
        f"""SELECT * EXCLUDE ("title", "text"), "title" || "text" AS {quote_identifier(combine)}, length("title") AS {quote_identifier(title_len)} FROM source""",
        f"""SELECT * EXCLUDE ({quote_identifier(combine)}, {quote_identifier(title_len)}), substr({quote_identifier(combine)}, 1, {quote_identifier(title_len)}) AS "title", substr({quote_identifier(combine)}, {quote_identifier(title_len)} + 1) AS "text" FROM compressed""",
    )
    method_3 = _candidate(
        "manual_wiki_3",
        "Combine title/text and reconstruct URL from the reconstructed title.",
        ["url", "title", "text"],
        [],
        [(combine, "Concatenated title and text"), (title_len, "Title length")],
        f"""SELECT * EXCLUDE ("url", "title", "text"), "title" || "text" AS {quote_identifier(combine)}, length("title") AS {quote_identifier(title_len)} FROM source""",
        f"""SELECT * EXCLUDE ({quote_identifier(combine)}, {quote_identifier(title_len)}), substr({quote_identifier(combine)}, 1, {quote_identifier(title_len)}) AS "title", substr({quote_identifier(combine)}, {quote_identifier(title_len)} + 1) AS "text", {prefix} || url_encode(substr({quote_identifier(combine)}, 1, {quote_identifier(title_len)})) AS "url" FROM compressed""",
    )
    method_4 = _candidate(
        "manual_wiki_4",
        "Drop title and decode it from the URL.",
        ["title"],
        ["url"],
        [],
        'SELECT * EXCLUDE ("title") FROM source',
        f"""SELECT *, url_decode(CASE WHEN starts_with("url", {prefix}) THEN substr("url", length({prefix}) + 1) ELSE "url" END) AS "title" FROM compressed""",
    )
    return [method_1, method_2, method_3, method_4]


def _fineweb_url_baselines() -> list[BaselineDefinition]:
    method_1 = _candidate(
        "manual_fineweb_url_1",
        "Drop domain and recover it with the historical URL regular expression.",
        ["domain"],
        ["url"],
        [],
        'SELECT * EXCLUDE ("domain") FROM source',
        r"""SELECT *, regexp_extract("url", 'https?://(?:[^./]+\.)*([^./]+\.[^./]+)', 1) AS "domain" FROM compressed""",
    )
    method_3 = _candidate(
        "manual_fineweb_url_3",
        "Drop domain while retaining its URL offset and length.",
        ["domain"],
        ["url"],
        [
            ("__v_domain_offset", "One-based domain offset in URL"),
            ("__v_domain_length", "Domain length"),
        ],
        """SELECT * EXCLUDE ("domain"), strpos("url", "domain") AS "__v_domain_offset", length("domain") AS "__v_domain_length" FROM source""",
        """SELECT * EXCLUDE ("__v_domain_offset", "__v_domain_length"), substr("url", "__v_domain_offset", "__v_domain_length") AS "domain" FROM compressed""",
    )
    return [
        method_1,
        BaselineDefinition(
            name="manual_fineweb_url_2",
            candidate=None,
            reason="historical method has no lossless reconstruction SQL",
        ),
        method_3,
    ]


def _metanova_baselines() -> list[BaselineDefinition]:
    method_1 = _candidate(
        "manual_metanova_1",
        "Drop product_hashisy and derive it from product_name.",
        ["product_hashisy"],
        ["product_name"],
        [],
        'SELECT * EXCLUDE ("product_hashisy") FROM source',
        """SELECT *, split_part("product_name", '_', 1) || '"' AS "product_hashisy" FROM compressed""",
    )
    method_2 = _candidate(
        "manual_metanova_2",
        "Remove the product hash from product_name.",
        ["product_name"],
        ["product_hashisy"],
        [],
        """SELECT * REPLACE (replace("product_name", substr("product_hashisy", 2, length("product_hashisy") - 2), '') AS "product_name") FROM source""",
        """SELECT * REPLACE (left("product_name", 1) || substr("product_hashisy", 2, length("product_hashisy") - 2) || substr("product_name", 2) AS "product_name") FROM compressed""",
    )
    method_3 = _candidate(
        "manual_metanova_3",
        "Drop r1_ident and r2_ident and derive them from URL suffixes.",
        ["r1_ident", "r2_ident"],
        ["r1_url", "r2_url"],
        [],
        'SELECT * EXCLUDE ("r1_ident", "r2_ident") FROM source',
        """SELECT *, '"' || list_extract(string_split("r1_url", '/'), -1) AS "r1_ident", '"' || list_extract(string_split("r2_url", '/'), -1) AS "r2_ident" FROM compressed""",
    )
    method_4 = _candidate(
        "manual_metanova_4",
        "Remove identifier text from r1_url and r2_url.",
        ["r1_url", "r2_url"],
        ["r1_ident", "r2_ident"],
        [],
        """SELECT * REPLACE (replace("r1_url", substr("r1_ident", 2, length("r1_ident") - 2), '') AS "r1_url", replace("r2_url", substr("r2_ident", 2, length("r2_ident") - 2), '') AS "r2_url") FROM source""",
        """SELECT * REPLACE (left("r1_url", length("r1_url") - 1) || substr("r1_ident", 2, length("r1_ident") - 2) || right("r1_url", 1) AS "r1_url", left("r2_url", length("r2_url") - 1) || substr("r2_ident", 2, length("r2_ident") - 2) || right("r2_url", 1) AS "r2_url") FROM compressed""",
    )
    method_5 = _candidate(
        "manual_metanova_5",
        "Combine Metanova methods 1 and 4.",
        ["product_hashisy", "r1_url", "r2_url"],
        ["product_name", "r1_ident", "r2_ident"],
        [],
        """SELECT * EXCLUDE ("product_hashisy") REPLACE (replace("r1_url", substr("r1_ident", 2, length("r1_ident") - 2), '') AS "r1_url", replace("r2_url", substr("r2_ident", 2, length("r2_ident") - 2), '') AS "r2_url") FROM source""",
        """SELECT * REPLACE (left("r1_url", length("r1_url") - 1) || substr("r1_ident", 2, length("r1_ident") - 2) || right("r1_url", 1) AS "r1_url", left("r2_url", length("r2_url") - 1) || substr("r2_ident", 2, length("r2_ident") - 2) || right("r2_url", 1) AS "r2_url"), split_part("product_name", '_', 1) || '"' AS "product_hashisy" FROM compressed""",
    )
    return [method_1, method_2, method_3, method_4, method_5]


def _flickr_baselines(columns: set[str]) -> list[BaselineDefinition]:
    suffixes = {
        "url_sq": "_s",
        "url_q": "_q",
        "url_t": "_t",
        "url_s": "_m",
        "url_n": "_n",
        "url_w": "_w",
        "url_m": "",
        "url_z": "_z",
        "url_c": "_c",
        "url_l": "_b",
    }
    url_columns = [name for name in suffixes if name in columns]
    if "url_sq" not in columns or not url_columns:
        return [
            BaselineDefinition(
                name="manual_flickr_1",
                candidate=None,
                reason="required Flickr URL columns are absent",
            )
        ]
    template = "__v_flickr_url_template"
    flags = [f"__v_{name}_present" for name in url_columns]
    drop = ", ".join(quote_identifier(name) for name in url_columns)
    generated = [
        f"replace(\"url_sq\", '_s', '_{{}}') AS {quote_identifier(template)}"
    ] + [
        f"{quote_identifier(name)} IS NOT NULL AS {quote_identifier(flag)}"
        for name, flag in zip(url_columns, flags)
    ]
    reconstruction = [
        f"CASE WHEN {quote_identifier(flag)} THEN replace({quote_identifier(template)}, '_{{}}', {quote_literal(suffixes[name])}) ELSE NULL END AS {quote_identifier(name)}"
        for name, flag in zip(url_columns, flags)
    ]
    return [
        _candidate(
            "manual_flickr_1",
            "Store one Flickr URL template plus per-size presence flags.",
            url_columns,
            [],
            [(template, "Shared Flickr URL template")]
            + [
                (flag, f"Presence flag for {name}")
                for name, flag in zip(url_columns, flags)
            ],
            f"SELECT * EXCLUDE ({drop}), {', '.join(generated)} FROM source",
            f"SELECT * EXCLUDE ({quote_identifier(template)}, {', '.join(quote_identifier(flag) for flag in flags)}), {', '.join(reconstruction)} FROM compressed",
        )
    ]


def _fineweb_baselines(columns: set[str]) -> list[BaselineDefinition]:
    definitions: list[BaselineDefinition] = []
    if {"dump", "file_path"} <= columns:
        definitions.append(
            _candidate(
                "manual_fineweb_1",
                "Drop dump and derive it from file_path.",
                ["dump"],
                ["file_path"],
                [],
                'SELECT * EXCLUDE ("dump") FROM source',
                """SELECT *, split_part("file_path", '/', 5) AS "dump" FROM compressed""",
            )
        )
        definitions.append(
            _candidate(
                "manual_fineweb_2",
                "Remove dump text from file_path.",
                ["file_path"],
                ["dump"],
                [],
                """SELECT * REPLACE (replace("file_path", "dump", '') AS "file_path") FROM source""",
                """SELECT * REPLACE (replace("file_path", 'crawl-data/', 'crawl-data/' || "dump" || '/') AS "file_path") FROM compressed""",
            )
        )
    combine_columns = [
        name
        for name in ["id", "dump", "url", "date", "file_path", "language", "text"]
        if name in columns
    ]
    if len(combine_columns) >= 2:
        combine_name = "__v_fineweb_combined"
        length_names = [
            f"__v_fineweb_{_safe_id(name)}_len" for name in combine_columns[:-1]
        ]
        combine_expr = " || ".join(quote_identifier(name) for name in combine_columns)
        compression_parts = [f"{combine_expr} AS {quote_identifier(combine_name)}"]
        compression_parts.extend(
            f"length({quote_identifier(name)}) AS {quote_identifier(length_name)}"
            for name, length_name in zip(combine_columns[:-1], length_names)
        )
        reconstructed = []
        offset = "1"
        for name, length_name in zip(combine_columns[:-1], length_names):
            reconstructed.append(
                f"substr({quote_identifier(combine_name)}, {offset}, {quote_identifier(length_name)}) AS {quote_identifier(name)}"
            )
            offset = f"({offset} + {quote_identifier(length_name)})"
        reconstructed.append(
            f"substr({quote_identifier(combine_name)}, {offset}) AS {quote_identifier(combine_columns[-1])}"
        )
        definitions.append(
            _candidate(
                "manual_fineweb_3",
                "Combine the historical FineWeb string columns and retain split lengths.",
                combine_columns,
                [],
                [(combine_name, "Concatenated string columns")]
                + [
                    (length_name, f"Length of {name}")
                    for name, length_name in zip(combine_columns[:-1], length_names)
                ],
                f"SELECT * EXCLUDE ({', '.join(quote_identifier(name) for name in combine_columns)}), {', '.join(compression_parts)} FROM source",
                f"SELECT * EXCLUDE ({quote_identifier(combine_name)}, {', '.join(quote_identifier(name) for name in length_names)}), {', '.join(reconstructed)} FROM compressed",
            )
        )
    definitions.append(
        BaselineDefinition(
            name="manual_fineweb_4",
            candidate=None,
            reason="numeric regression baseline is outside string reconstruction scope",
        )
    )
    prefixes = {
        "id": "<urn:uuid:",
        "dump": "CC-MAIN-",
        "url": "http",
        "file_path": "s3://commoncrawl/crawl-data/CC-MAIN-",
    }
    prefix_columns = [name for name in prefixes if name in columns]
    if prefix_columns:
        compression_replacements = []
        reconstruction_replacements = []
        for name in prefix_columns:
            quoted = quote_identifier(name)
            literal = quote_literal(prefixes[name])
            compression_replacements.append(
                f"CASE WHEN starts_with({quoted}, {literal}) THEN substr({quoted}, length({literal}) + 1) ELSE {quoted} END AS {quoted}"
            )
            reconstruction_replacements.append(
                f"CASE WHEN {quoted} IS NULL THEN NULL ELSE {literal} || {quoted} END AS {quoted}"
            )
        definitions.append(
            _candidate(
                "manual_fineweb_5",
                "Remove historical constant prefixes from FineWeb string columns.",
                prefix_columns,
                [],
                [],
                f"SELECT * REPLACE ({', '.join(compression_replacements)}) FROM source",
                f"SELECT * REPLACE ({', '.join(reconstruction_replacements)}) FROM compressed",
            )
        )
    if "id" in columns:
        parts = [f"__v_fineweb_id_part_{index}" for index in range(1, 6)]
        cleaned = "replace(replace(\"id\", '<urn:uuid:', ''), '>', '')"
        definitions.append(
            _candidate(
                "manual_fineweb_6",
                "Split the UUID-like id into five components.",
                ["id"],
                [],
                [
                    (part, f"ID component {index}")
                    for index, part in enumerate(parts, 1)
                ],
                'SELECT * EXCLUDE ("id"), '
                + ", ".join(
                    f"split_part({cleaned}, '-', {index}) AS {quote_identifier(part)}"
                    for index, part in enumerate(parts, 1)
                )
                + " FROM source",
                f"""SELECT * EXCLUDE ({", ".join(quote_identifier(part) for part in parts)}), '<urn:uuid:' || {" || '-' || ".join(quote_identifier(part) for part in parts)} || '>' AS "id" FROM compressed""",
            )
        )
    if {"url", "text"} <= columns:
        definitions.append(
            _candidate(
                "manual_fineweb_7",
                "Concatenate URL and text and retain URL length.",
                ["url", "text"],
                [],
                [
                    ("__v_url_text", "Concatenated URL and text"),
                    ("__v_url_len", "URL length"),
                ],
                """SELECT * EXCLUDE ("url", "text"), "url" || "text" AS "__v_url_text", length("url") AS "__v_url_len" FROM source""",
                """SELECT * EXCLUDE ("__v_url_text", "__v_url_len"), substr("__v_url_text", 1, "__v_url_len") AS "url", substr("__v_url_text", "__v_url_len" + 1) AS "text" FROM compressed""",
            )
        )
        path_expr = "regexp_extract(\"url\", '^https?://[^/]+/?(.*)$', 1)"
        prefix_expr = (
            'CASE WHEN regexp_matches("url", \'^https?://[^/]+/$\') THEN "url" '
            "ELSE regexp_extract(\"url\", '^(https?://[^/]+)', 1) END"
        )
        definitions.append(
            _candidate(
                "manual_fineweb_8",
                "Store the URL origin and concatenate URL path with text.",
                ["url", "text"],
                [],
                [
                    ("__v_url_prefix", "URL scheme and authority"),
                    ("__v_url_path_text", "Concatenated URL path and text"),
                    ("__v_url_path_len", "URL path length"),
                ],
                f"""SELECT * EXCLUDE ("url", "text"), {prefix_expr} AS "__v_url_prefix", {path_expr} || "text" AS "__v_url_path_text", length({path_expr}) AS "__v_url_path_len" FROM source""",
                """SELECT * EXCLUDE ("__v_url_prefix", "__v_url_path_text", "__v_url_path_len"), CASE WHEN "__v_url_path_len" = 0 THEN "__v_url_prefix" ELSE rtrim("__v_url_prefix", '/') || '/' || substr("__v_url_path_text", 1, "__v_url_path_len") END AS "url", substr("__v_url_path_text", "__v_url_path_len" + 1) AS "text" FROM compressed""",
            )
        )
    return definitions


def manual_baselines(
    dataset_id: str, config_name: str, columns: Iterable[str]
) -> list[BaselineDefinition]:
    column_set = set(columns)
    if dataset_id == "wikimedia/wikipedia":
        return _wiki_baselines(config_name)
    if dataset_id == "nhagar/fineweb_urls":
        return _fineweb_url_baselines()
    if dataset_id == "Metanova/SAVI-2020":
        return _metanova_baselines()
    if dataset_id == "bigdata-pw/Flickr":
        return _flickr_baselines(column_set)
    if dataset_id == "HuggingFaceFW/fineweb":
        return _fineweb_baselines(column_set)
    return []
