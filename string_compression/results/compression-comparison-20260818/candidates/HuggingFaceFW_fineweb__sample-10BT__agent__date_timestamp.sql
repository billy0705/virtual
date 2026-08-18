-- Compression
WITH p AS (
  SELECT
    *,
    try_strptime("date", '%Y-%m-%dT%H:%M:%SZ') AS d
  FROM source
)
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "file_path",
  "language",
  "language_score",
  "token_count",
  CASE WHEN d IS NOT NULL AND "date" = strftime(d, '%Y-%m-%dT%H:%M:%SZ') THEN TRUE ELSE FALSE END AS "date_ok",
  CASE WHEN d IS NOT NULL AND "date" = strftime(d, '%Y-%m-%dT%H:%M:%SZ') THEN d ELSE NULL END AS "date_ts",
  CASE WHEN d IS NOT NULL AND "date" = strftime(d, '%Y-%m-%dT%H:%M:%SZ') THEN NULL ELSE "date" END AS "date_raw"
FROM p;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  CASE WHEN "date_ok" THEN strftime("date_ts", '%Y-%m-%dT%H:%M:%SZ') ELSE "date_raw" END AS "date",
  "file_path",
  "language",
  "language_score",
  "token_count"
FROM compressed;
