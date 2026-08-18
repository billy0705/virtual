-- Compression
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
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  CASE WHEN "m" THEN "p" || "domain" || "s" ELSE "e" END AS "url",
  "domain"
FROM compressed;
