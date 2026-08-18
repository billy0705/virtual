# Benchmark Compression Functions

Run: `public-sample-offline-smoke-20260818`  
Prompt: `agentic-string-compression-v1`  
Model: `offline`  
Codec: `snappy`

Every non-identity function below passed discovery, disjoint holdout, and exact full-data reconstruction. The measured candidate size includes the serialized candidate specification in Parquet metadata. A strategy without a valid size-positive candidate uses the explicit identity fallback so that it remains visible in the comparison.

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
Status: `skipped`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`
Reason: offline mode

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Agent two-stage

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`
Reason: offline mode

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `10003818`  
Size ratio: `1.000000`
Reason: offline mode

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

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `302568`  
Size ratio: `1.000000`
Reason: offline mode

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Agent two-stage

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `302568`  
Size ratio: `1.000000`
Reason: offline mode

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```

### Agent tool-loop

Candidate: `identity`  
Status: `skipped`  
Compressed bytes: `302568`  
Size ratio: `1.000000`
Reason: offline mode

Compression function: identity.

```sql
SELECT * FROM source
```

Reconstruction function: identity.

```sql
SELECT * FROM compressed
```
