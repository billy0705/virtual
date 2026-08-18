-- Compression
SELECT
  "__virtual_row_id",
  "domain",
  CASE WHEN COALESCE(starts_with("url", 'http://'), FALSE) THEN substr("url", 8) ELSE '' END AS "t",
  CASE WHEN COALESCE(starts_with("url", 'http://'), FALSE) THEN '' ELSE "url" END AS "e",
  COALESCE(starts_with("url", 'http://'), FALSE) AS "m"
FROM source;

-- Reconstruction
SELECT
  "__virtual_row_id",
  CASE WHEN "m" THEN 'http://' || "t" ELSE "e" END AS "url",
  "domain"
FROM compressed;
