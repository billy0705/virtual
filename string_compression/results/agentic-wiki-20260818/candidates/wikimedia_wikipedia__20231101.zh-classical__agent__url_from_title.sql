-- Compression
WITH f AS (
  SELECT *,
    'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") AS "gen_url"
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  ("url" IS NOT DISTINCT FROM "gen_url") AS "url_ok",
  CASE WHEN "url" IS NOT DISTINCT FROM "gen_url" THEN CAST(NULL AS VARCHAR) ELSE "url" END AS "url_err"
FROM f;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "url_ok" THEN 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title")
    ELSE "url_err"
  END AS "url",
  "title",
  "text"
FROM compressed;
