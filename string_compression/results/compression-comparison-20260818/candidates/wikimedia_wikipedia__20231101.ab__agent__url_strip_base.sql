-- Compression
WITH p AS (
  SELECT *,
    ("url" IS NOT NULL AND starts_with("url", 'https://ab.wikipedia.org/wiki/')) AS ok
  FROM source
)
SELECT
  "__virtual_row_id", "id", "title", "text",
  ok AS "url_ok",
  CASE WHEN ok THEN substring("url", length('https://ab.wikipedia.org/wiki/') + 1) ELSE NULL END AS "url_s",
  CASE WHEN ok THEN NULL ELSE "url" END AS "url_r"
FROM p;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "url_ok" THEN 'https://ab.wikipedia.org/wiki/' || "url_s"
    ELSE "url_r"
  END AS "url",
  "title",
  "text"
FROM compressed;
