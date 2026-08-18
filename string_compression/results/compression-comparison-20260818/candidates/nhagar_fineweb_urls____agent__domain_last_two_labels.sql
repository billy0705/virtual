-- Compression
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
FROM x;

-- Reconstruction
WITH h AS (
  SELECT *, regexp_extract("url", '^http://([^/?#]*)', 1) AS host
  FROM compressed
)
SELECT
  "__virtual_row_id",
  "url",
  CASE WHEN d_ok THEN regexp_extract(host, '([^.]+[.][^.]+)$', 1) ELSE d_raw END AS "domain"
FROM h;
