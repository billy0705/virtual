-- Compression
WITH f AS (
  SELECT *,
    'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") AS "gen_url",
    coalesce(starts_with("text", "title"), false) AS "txt_ok0"
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  ("url" IS NOT DISTINCT FROM "gen_url") AS "url_ok",
  CASE WHEN "url" IS NOT DISTINCT FROM "gen_url" THEN CAST(NULL AS VARCHAR) ELSE "url" END AS "url_err",
  "txt_ok0" AS "txt_ok",
  CASE WHEN "txt_ok0" THEN substr("text", length("title") + 1) ELSE "text" END AS "txt_frag"
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
  CASE WHEN "txt_ok" THEN "title" || "txt_frag" ELSE "txt_frag" END AS "text"
FROM compressed;
