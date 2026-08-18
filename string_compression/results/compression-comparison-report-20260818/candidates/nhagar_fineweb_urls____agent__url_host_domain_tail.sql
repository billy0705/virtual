-- Compression
WITH h AS (
  SELECT *, regexp_extract("url", '^http://([^/?#]*)', 1) AS host
  FROM source
), x AS (
  SELECT *, CASE
    WHEN "url" IS NOT NULL
     AND "domain" IS NOT NULL
     AND starts_with("url", 'http://')
     AND (host = "domain" OR ends_with(host, '.' || "domain"))
    THEN TRUE ELSE FALSE
  END AS ok
  FROM h
)
SELECT
  "__virtual_row_id",
  "domain",
  ok AS u_ok,
  CASE WHEN ok THEN left(host, length(host) - length("domain")) END AS u_sub,
  CASE WHEN ok THEN substr("url", 8 + length(host)) END AS u_tail,
  CASE WHEN NOT ok THEN "url" END AS u_raw
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  CASE WHEN u_ok THEN 'http://' || u_sub || "domain" || u_tail ELSE u_raw END AS "url",
  "domain"
FROM compressed;
