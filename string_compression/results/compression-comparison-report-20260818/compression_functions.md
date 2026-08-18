# Benchmark Compression Functions

Run: `compression-comparison-20260818`  
Prompt: `agentic-string-compression-v1`  
Model: `gpt-5.6-terra`  
Codec: `snappy`

Every non-identity function below passed discovery, disjoint holdout, and exact full-data reconstruction. The measured candidate size includes the serialized candidate specification in Parquet metadata. A strategy without a valid size-positive candidate uses the explicit identity fallback so that it remains visible in the comparison.

## wikimedia/wikipedia / 20231101.zh-classical

Rows: `12708`; original Snappy bytes: `9957397`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `9957397`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `9957397`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `9803107`  
Size ratio: `0.984505`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://zh-classical.wikipedia.org/wiki/') THEN substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `identity`  
Status: `completed`  
Compressed bytes: `9957397`  
Size ratio: `1.000000`
Reason: no candidate passed lossless, size-positive full validation

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Agent two-stage

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `9720362`  
Size ratio: `0.976195`
Summary: Reconstruct a URL from the title using DuckDB URL encoding when it exactly matches, while retaining only mismatching URLs as exceptions.
Targets: `url`  
References: `id, title, text`  
Residuals: `u_ok, u_e`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NULL THEN NULL WHEN "url" = 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "u_ok", CASE WHEN "url" IS NULL THEN NULL WHEN "url" = 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "u_e" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "u_ok" IS NULL THEN NULL WHEN "u_ok" THEN 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") ELSE "u_e" END AS "url", "title", "text" FROM compressed
```

### Agent tool-loop

Candidate: `url_title_from_suffix`  
Status: `valid`  
Compressed bytes: `9778481`  
Size ratio: `0.982032`
Summary: Store only the URL suffix after the invariant wiki prefix; derive both URL and title by prefixing and URL-decoding it.
Targets: `url, title`  
References: `(none)`  
Residuals: `p`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "text", substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) AS "p" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", 'https://zh-classical.wikipedia.org/wiki/' || "p" AS "url", url_decode("p") AS "title", "text" FROM compressed
```

## wikimedia/wikipedia / 20231101.ab

Rows: `6152`; original Snappy bytes: `1243983`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `1243983`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `1243983`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `1186095`  
Size ratio: `0.953466`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/') THEN substr("url", length('https://ab.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `1169333`  
Size ratio: `0.939991`
Summary: Remove the URL when it is the Abkhaz Wikipedia base URL plus URL-encoded title; retain explicit exceptions.
Targets: `url`  
References: `title`  
Residuals: `url_bad, url_r`

Compression SQL:

```sql
WITH p AS (
  SELECT *,
    'https://ab.wikipedia.org/wiki/' || url_encode("title") AS u0
  FROM source
)
SELECT
  "__virtual_row_id", "id", "title", "text",
  "url" IS DISTINCT FROM u0 AS "url_bad",
  CASE WHEN "url" IS DISTINCT FROM u0 THEN "url" ELSE NULL END AS "url_r"
FROM p
```

Reconstruction SQL:

```sql
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "url_bad" THEN "url_r"
    ELSE 'https://ab.wikipedia.org/wiki/' || url_encode("title")
  END AS "url",
  "title",
  "text"
FROM compressed
```

### Agent two-stage

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `1169198`  
Size ratio: `0.939883`
Summary: Reconstruct a Wikipedia URL from the URL-encoded title when exact; retain the original URL only for exceptions.
Targets: `url`  
References: `title`  
Residuals: `uok, uerr`

Compression SQL:

```sql
SELECT * EXCLUDE ("url"), CASE WHEN "url" IS NOT DISTINCT FROM ('https://ab.wikipedia.org/wiki/' || url_encode("title")) THEN TRUE ELSE FALSE END AS "uok", CASE WHEN "url" IS NOT DISTINCT FROM ('https://ab.wikipedia.org/wiki/' || url_encode("title")) THEN NULL ELSE "url" END AS "uerr" FROM source
```

Reconstruction SQL:

```sql
SELECT * EXCLUDE ("uok", "uerr"), CASE WHEN "uok" THEN 'https://ab.wikipedia.org/wiki/' || url_encode("title") ELSE "uerr" END AS "url" FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `1243983`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

## wikimedia/wikipedia / 20231101.af

Rows: `20000`; original Snappy bytes: `38842945`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `38842945`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `38842945`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `38576496`  
Size ratio: `0.993140`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://af.wikipedia.org/wiki/') THEN substr("url", length('https://af.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `38539578`  
Size ratio: `0.992190`
Summary: Reconstruct the Wikipedia URL from the retained title using the observed site prefix and DuckDB URL encoding; retain the original URL only for explicit nonmatching rows.
Targets: `url`  
References: `title`  
Residuals: `url_ok, url_err`

Compression SQL:

```sql
WITH x AS (
  SELECT
    *,
    'https://af.wikipedia.org/wiki/' || url_encode("title") AS u0
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  ("url" IS NOT NULL AND "url" = u0) AS "url_ok",
  CASE WHEN "url" IS NOT NULL AND "url" = u0 THEN NULL ELSE "url" END AS "url_err"
FROM x
```

Reconstruction SQL:

```sql
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "url_ok" THEN 'https://af.wikipedia.org/wiki/' || url_encode("title")
    ELSE "url_err"
  END AS "url",
  "title",
  "text"
FROM compressed
```

### Agent two-stage

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `38539640`  
Size ratio: `0.992192`
Summary: Remove "url" when it equals the Afrikaans Wikipedia prefix plus URL-encoding of "title"; retain an exact per-row fallback otherwise.
Targets: `url`  
References: `title`  
Residuals: `_u_bad, _u_raw`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT DISTINCT FROM CASE WHEN "title" IS NULL THEN NULL ELSE 'https://af.wikipedia.org/wiki/' || url_encode("title") END THEN FALSE ELSE TRUE END AS "_u_bad", CASE WHEN "url" IS NOT DISTINCT FROM CASE WHEN "title" IS NULL THEN NULL ELSE 'https://af.wikipedia.org/wiki/' || url_encode("title") END THEN NULL ELSE "url" END AS "_u_raw" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "_u_bad" THEN "_u_raw" ELSE CASE WHEN "title" IS NULL THEN NULL ELSE 'https://af.wikipedia.org/wiki/' || url_encode("title") END END AS "url", "title", "text" FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `38842945`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

## wikimedia/wikipedia / 20231101.azb

Rows: `20000`; original Snappy bytes: `9384190`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `9384190`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `9384190`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `9098099`  
Size ratio: `0.969514`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://azb.wikipedia.org/wiki/') THEN substr("url", length('https://azb.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `8955171`  
Size ratio: `0.954283`
Summary: Reconstruct Wikipedia URLs from the URL-encoded title; retain the original URL only for rows whose exact encoding differs.
Targets: `url`  
References: `title`  
Residuals: `url_ok, url_x`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", "text", "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://azb.wikipedia.org/wiki/' || url_encode("title") AS "url_ok", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://azb.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_x" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "url_ok" THEN 'https://azb.wikipedia.org/wiki/' || url_encode("title") ELSE "url_x" END AS "url", "title", "text" FROM compressed
```

### Agent two-stage

Candidate: `url_and_text_from_title`  
Status: `valid`  
Compressed bytes: `8825573`  
Size ratio: `0.940473`
Summary: Jointly removes the URL and text, deriving canonical URLs from title and stripping exact title prefixes from article text, with independent exact fallbacks.
Targets: `url, text`  
References: `title`  
Residuals: `u_ok, u_x, t_p, t_x`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", CASE WHEN "url" IS NOT DISTINCT FROM ('https://azb.wikipedia.org/wiki/' || url_encode("title")) THEN TRUE ELSE FALSE END AS "u_ok", CASE WHEN "url" IS NOT DISTINCT FROM ('https://azb.wikipedia.org/wiki/' || url_encode("title")) THEN NULL ELSE "url" END AS "u_x", CASE WHEN starts_with("text", "title") THEN TRUE ELSE FALSE END AS "t_p", CASE WHEN starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "t_x" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "u_ok" THEN 'https://azb.wikipedia.org/wiki/' || url_encode("title") ELSE "u_x" END AS "url", "title", CASE WHEN "t_p" THEN "title" || "t_x" ELSE "t_x" END AS "text" FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `9384190`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

## wikimedia/wikipedia / 20231101.bg

Rows: `20000`; original Snappy bytes: `68833228`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `68833228`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `68833228`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `68539364`  
Size ratio: `0.995731`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://bg.wikipedia.org/wiki/') THEN substr("url", length('https://bg.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `url_and_text_title_prefix`  
Status: `valid`  
Compressed bytes: `68348063`  
Size ratio: `0.992952`
Summary: Derives canonical URLs and stores text as a suffix when it begins with its title; each transformation has a lossless fallback.
Targets: `url, text`  
References: `__virtual_row_id, id, title`  
Residuals: `url_ok, url_e, text_p, text_r`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", "url" IS NOT DISTINCT FROM 'https://bg.wikipedia.org/wiki/' || url_encode("title") AS "url_ok", CASE WHEN "url" IS NOT DISTINCT FROM 'https://bg.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_e", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN TRUE ELSE FALSE END AS "text_p", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "text_r" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "url_ok" THEN 'https://bg.wikipedia.org/wiki/' || url_encode("title") ELSE "url_e" END AS "url", "title", CASE WHEN "text_p" THEN "title" || "text_r" ELSE "text_r" END AS "text" FROM compressed
```

### Agent two-stage

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `68399674`  
Size ratio: `0.993701`
Summary: Reconstruct canonical Bulgarian Wikipedia URLs from the retained title; preserve a full URL fallback for every noncanonical or NULL relationship.
Targets: `url`  
References: `id, title, text`  
Residuals: `uk, ue`

Compression SQL:

```sql
SELECT
  s."__virtual_row_id",
  s."id",
  s."title",
  s."text",
  CASE
    WHEN s."url" IS NOT DISTINCT FROM ('https://bg.wikipedia.org/wiki/' || url_encode(s."title")) THEN TRUE
    ELSE FALSE
  END AS "uk",
  CASE
    WHEN s."url" IS NOT DISTINCT FROM ('https://bg.wikipedia.org/wiki/' || url_encode(s."title")) THEN NULL
    ELSE s."url"
  END AS "ue"
FROM source AS s
```

Reconstruction SQL:

```sql
SELECT
  c."__virtual_row_id",
  c."id",
  CASE
    WHEN c."uk" THEN 'https://bg.wikipedia.org/wiki/' || url_encode(c."title")
    ELSE c."ue"
  END AS "url",
  c."title",
  c."text"
FROM compressed AS c
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `68833228`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

## wikimedia/wikipedia / 20231101.ady

Rows: `706`; original Snappy bytes: `345621`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `345621`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `345621`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `335769`  
Size ratio: `0.971495`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://ady.wikipedia.org/wiki/') THEN substr("url", length('https://ady.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `url_and_leading_title_text`  
Status: `valid`  
Compressed bytes: `332681`  
Size ratio: `0.962560`
Summary: Combine URL-from-title reconstruction with removal of a title prefix from text when present; both transformations have exact fallbacks.
Targets: `url, text`  
References: `title`  
Residuals: `url_ok, url_e, text_ok, text_r`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "url_ok", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_e", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN TRUE ELSE FALSE END AS "text_ok", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "text_r" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "url_ok" THEN 'https://ady.wikipedia.org/wiki/' || url_encode("title") ELSE "url_e" END AS "url", "title", CASE WHEN "text_ok" THEN "title" || "text_r" ELSE "text_r" END AS "text" FROM compressed
```

### Agent two-stage

Candidate: `url_title`  
Status: `valid`  
Compressed bytes: `333180`  
Size ratio: `0.964004`
Summary: Reconstruct each URL from the fixed wiki prefix and URL-encoded title; retain an exact URL residual only for rows where that formula differs.
Targets: `url`  
References: `title`  
Residuals: `url_err`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_err" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", COALESCE("url_err", 'https://ady.wikipedia.org/wiki/' || url_encode("title")) AS "url", "title", "text" FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `345621`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

## wikimedia/wikipedia / 20231101.ceb

Rows: `20000`; original Snappy bytes: `1776099`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `1776099`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `1776099`  
Size ratio: `1.000000`
Reason: no candidates were produced

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_wiki_4`  
Status: `valid`  
Compressed bytes: `1537632`  
Size ratio: `0.865736`
Summary: Drop title and decode it from the URL.
Targets: `title`  
References: `url`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * EXCLUDE ("title") FROM source
```

Reconstruction SQL:

```sql
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://ceb.wikipedia.org/wiki/') THEN substr("url", length('https://ceb.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed
```

### Agent single

Candidate: `url_from_title`  
Status: `valid`  
Compressed bytes: `1506500`  
Size ratio: `0.848207`
Summary: Rebuild canonical Wikipedia URLs by URL-encoding title; retain the complete URL only when that exact reconstruction does not match.
Targets: `url`  
References: `__virtual_row_id, id, title, text`  
Residuals: `_u, _m`

Compression SQL:

```sql
WITH x AS (
  SELECT
    *,
    ("url" IS NOT DISTINCT FROM 'https://ceb.wikipedia.org/wiki/' || url_encode("title")) AS m
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  CASE WHEN m THEN NULL ELSE "url" END AS "_u",
  m AS "_m"
FROM x
```

Reconstruction SQL:

```sql
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "_m" THEN 'https://ceb.wikipedia.org/wiki/' || url_encode("title")
    ELSE "_u"
  END AS "url",
  "title",
  "text"
FROM compressed
```

### Agent two-stage

Candidate: `url_title_encode`  
Status: `valid`  
Compressed bytes: `1506425`  
Size ratio: `0.848165`
Summary: Remove "url" when it is exactly the Wikipedia prefix plus DuckDB URL encoding of the retained title; retain the original URL only for exceptions.
Targets: `url`  
References: `title`  
Residuals: `u_ok, u_x`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" = 'https://ceb.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "u_ok", CASE WHEN "url" = 'https://ceb.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "u_x" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", CASE WHEN "u_ok" THEN 'https://ceb.wikipedia.org/wiki/' || url_encode("title") ELSE "u_x" END AS "url", "title", "text" FROM compressed
```

### Agent tool-loop

Candidate: `url_title_path`  
Status: `valid`  
Compressed bytes: `1511405`  
Size ratio: `0.850969`
Summary: Store only the URL-encoded Wikipedia path, deriving both title and full URL.
Targets: `url, title`  
References: `(none)`  
Residuals: `p`

Compression SQL:

```sql
SELECT "__virtual_row_id", "id", "text", substr("url", 32) AS "p" FROM source
```

Reconstruction SQL:

```sql
SELECT "__virtual_row_id", "id", 'https://ceb.wikipedia.org/wiki/' || "p" AS "url", url_decode("p") AS "title", "text" FROM compressed
```

## HuggingFaceFW/fineweb / sample-10BT

Rows: `5000`; original Snappy bytes: `10003818`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `identity`  
Status: `completed`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`
Reason: no candidate passed lossless, size-positive full validation

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Historical hand-written

Candidate: `manual_fineweb_5`  
Status: `valid`  
Compressed bytes: `9995066`  
Size ratio: `0.999125`
Summary: Remove historical constant prefixes from FineWeb string columns.
Targets: `id, dump, url, file_path`  
References: `(none)`  
Residuals: `(none)`

Compression SQL:

```sql
SELECT * REPLACE (CASE WHEN starts_with("id", '<urn:uuid:') THEN substr("id", length('<urn:uuid:') + 1) ELSE "id" END AS "id", CASE WHEN starts_with("dump", 'CC-MAIN-') THEN substr("dump", length('CC-MAIN-') + 1) ELSE "dump" END AS "dump", CASE WHEN starts_with("url", 'http') THEN substr("url", length('http') + 1) ELSE "url" END AS "url", CASE WHEN starts_with("file_path", 's3://commoncrawl/crawl-data/CC-MAIN-') THEN substr("file_path", length('s3://commoncrawl/crawl-data/CC-MAIN-') + 1) ELSE "file_path" END AS "file_path") FROM source
```

Reconstruction SQL:

```sql
SELECT * REPLACE (CASE WHEN "id" IS NULL THEN NULL ELSE '<urn:uuid:' || "id" END AS "id", CASE WHEN "dump" IS NULL THEN NULL ELSE 'CC-MAIN-' || "dump" END AS "dump", CASE WHEN "url" IS NULL THEN NULL ELSE 'http' || "url" END AS "url", CASE WHEN "file_path" IS NULL THEN NULL ELSE 's3://commoncrawl/crawl-data/CC-MAIN-' || "file_path" END AS "file_path") FROM compressed
```

### Agent single

Candidate: `identity`  
Status: `completed`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`
Reason: no candidate passed lossless, size-positive full validation

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Agent two-stage

Candidate: `filepath_affix_language_en`  
Status: `valid`  
Compressed bytes: `10001564`  
Size ratio: `0.999775`
Summary: Combine the validated file-path affix removal with literal reconstruction of the sampled constant language value.
Targets: `file_path, language`  
References: `text, id, dump, url, date, language_score, token_count`  
Residuals: `fp_ok, fp_p`

Compression SQL:

```sql
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  CASE WHEN "file_path" IS NOT NULL AND starts_with("file_path", 's3://commoncrawl/crawl-data/CC-MAIN-201') AND ends_with("file_path", '.warc.gz') THEN TRUE ELSE FALSE END AS "fp_ok",
  CASE WHEN "file_path" IS NOT NULL AND starts_with("file_path", 's3://commoncrawl/crawl-data/CC-MAIN-201') AND ends_with("file_path", '.warc.gz') THEN substr("file_path", length('s3://commoncrawl/crawl-data/CC-MAIN-201') + 1, length("file_path") - length('s3://commoncrawl/crawl-data/CC-MAIN-201') - length('.warc.gz')) ELSE "file_path" END AS "fp_p",
  "language_score",
  "token_count"
FROM source
```

Reconstruction SQL:

```sql
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  CASE WHEN "fp_ok" THEN 's3://commoncrawl/crawl-data/CC-MAIN-201' || "fp_p" || '.warc.gz' ELSE "fp_p" END AS "file_path",
  'en' AS "language",
  "language_score",
  "token_count"
FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

## nhagar/fineweb_urls / nhagar/fineweb_urls

Rows: `5000`; original Snappy bytes: `302568`.

### Original

Candidate: `identity`  
Status: `original`  
Compressed bytes: `302568`  
Size ratio: `1.000000`

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Algorithmic auto-prefix/suffix

Candidate: `heuristic_1_domain_from_0_url`  
Status: `valid`  
Compressed bytes: `264940`  
Size ratio: `0.875638`
Summary: Reconstruct domain as a substring of url; sample match rate 1.000.
Targets: `domain`  
References: `url`  
Residuals: `__v_1_domain_from_0_url_pos, __v_1_domain_from_0_url_len, __v_1_domain_from_0_url_error, __v_1_domain_from_0_url_error_present`

Compression SQL:

```sql
SELECT * EXCLUDE ("domain"),
                           CASE WHEN (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) THEN strpos("url", "domain") ELSE NULL END AS "__v_1_domain_from_0_url_pos",
                           CASE WHEN (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) THEN length("domain") ELSE NULL END AS "__v_1_domain_from_0_url_len",
                           CASE WHEN (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) THEN NULL ELSE "domain" END AS "__v_1_domain_from_0_url_error",
                           NOT (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) AS "__v_1_domain_from_0_url_error_present"
                    FROM source
```

Reconstruction SQL:

```sql
SELECT * EXCLUDE ("__v_1_domain_from_0_url_pos", "__v_1_domain_from_0_url_len", "__v_1_domain_from_0_url_error", "__v_1_domain_from_0_url_error_present"),
                           CASE WHEN "__v_1_domain_from_0_url_error_present"
                                THEN "__v_1_domain_from_0_url_error"
                                ELSE substr("url", "__v_1_domain_from_0_url_pos", "__v_1_domain_from_0_url_len")
                           END AS "domain"
                    FROM compressed
```

### Historical hand-written

Candidate: `manual_fineweb_url_3`  
Status: `valid`  
Compressed bytes: `260065`  
Size ratio: `0.859526`
Summary: Drop domain while retaining its URL offset and length.
Targets: `domain`  
References: `url`  
Residuals: `__v_domain_offset, __v_domain_length`

Compression SQL:

```sql
SELECT * EXCLUDE ("domain"), strpos("url", "domain") AS "__v_domain_offset", length("domain") AS "__v_domain_length" FROM source
```

Reconstruction SQL:

```sql
SELECT * EXCLUDE ("__v_domain_offset", "__v_domain_length"), substr("url", "__v_domain_offset", "__v_domain_length") AS "domain" FROM compressed
```

### Agent single

Candidate: `domain_first_occurrence`  
Status: `valid`  
Compressed bytes: `264765`  
Size ratio: `0.875059`
Summary: Factor the first occurrence of the domain string from the URL regardless of URL syntax. Nonmatching rows retain the full URL in an explicit fallback residual.
Targets: `url`  
References: `domain`  
Residuals: `p, s, e, m`

Compression SQL:

```sql
WITH x AS (
  SELECT
    "__virtual_row_id",
    "url",
    "domain",
    CASE
      WHEN "url" IS NOT NULL AND "domain" IS NOT NULL AND "domain" <> ''
      THEN strpos("url", "domain")
      ELSE 0
    END AS k
  FROM source
)
SELECT
  "__virtual_row_id",
  "domain",
  CASE WHEN k > 0 THEN left("url", k - 1) ELSE '' END AS "p",
  CASE WHEN k > 0 THEN substr("url", k + length("domain")) ELSE '' END AS "s",
  CASE WHEN k > 0 THEN '' ELSE "url" END AS "e",
  k > 0 AS "m"
FROM x
```

Reconstruction SQL:

```sql
SELECT
  "__virtual_row_id",
  CASE WHEN "m" THEN "p" || "domain" || "s" ELSE "e" END AS "url",
  "domain"
FROM compressed
```

### Agent two-stage

Candidate: `domain_last_two_labels`  
Status: `valid`  
Compressed bytes: `272431`  
Size ratio: `0.900396`
Summary: Retain the URL and reconstruct domains equal to the final two hostname labels; store exact domain fallbacks for multi-label public suffixes or other exceptions.
Targets: `domain`  
References: `url`  
Residuals: `d_ok, d_raw`

Compression SQL:

```sql
WITH h AS (
  SELECT *, regexp_extract("url", '^http://([^/?#]*)', 1) AS host
  FROM source
), x AS (
  SELECT *, regexp_extract(host, '([^.]+[.][^.]+)$', 1) AS last2
  FROM h
)
SELECT
  "__virtual_row_id",
  "url",
  CASE WHEN "domain" IS NOT NULL AND "domain" = last2 THEN TRUE ELSE FALSE END AS d_ok,
  CASE WHEN "domain" IS NOT NULL AND "domain" = last2 THEN NULL ELSE "domain" END AS d_raw
FROM x
```

Reconstruction SQL:

```sql
WITH h AS (
  SELECT *, regexp_extract("url", '^http://([^/?#]*)', 1) AS host
  FROM compressed
)
SELECT
  "__virtual_row_id",
  "url",
  CASE WHEN d_ok THEN regexp_extract(host, '([^.]+[.][^.]+)$', 1) ELSE d_raw END AS "domain"
FROM h
```

### Agent tool-loop

Candidate: `identity`  
Status: `error`  
Compressed bytes: `302568`  
Size ratio: `1.000000`
Reason: ValueError: tool loop ended without submit_candidates

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```
