-- Compression
WITH x AS (
  SELECT
    "__virtual_row_id",
    "url",
    "domain",
    regexp_extract("url", '^[A-Za-z][A-Za-z0-9+.-]*://([^/?#:]+)', 1) AS h
  FROM source
), y AS (
  SELECT *,
    "url" IS NOT NULL
    AND "domain" IS NOT NULL
    AND "domain" <> ''
    AND regexp_extract("url", '^[A-Za-z][A-Za-z0-9+.-]*://', 0) = 'http://'
    AND h <> ''
    AND (h = "domain" OR ends_with(h, '.' || "domain")) AS ok
  FROM x
)
SELECT
  "__virtual_row_id",
  "domain",
  CASE WHEN ok THEN left("url", length(h) - length("domain")) ELSE '' END AS "a",
  CASE WHEN ok THEN substr("url", 8 + length(h)) ELSE '' END AS "b",
  CASE WHEN ok THEN '' ELSE "url" END AS "e",
  ok AS "m"
FROM y;

-- Reconstruction
SELECT
  "__virtual_row_id",
  CASE WHEN "m" THEN 'http://' || "a" || "domain" || "b" ELSE "e" END AS "url",
  "domain"
FROM compressed;
