-- Compression
WITH raw AS (
  SELECT *,
    substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) AS "su"
  FROM source
), marked AS (
  SELECT *,
    coalesce(
      "url" LIKE 'https://zh-classical.wikipedia.org/wiki/%'
      AND try(url_decode("su")) IS NOT DISTINCT FROM "title",
      false
    ) AS "u_ok0"
  FROM raw
)
SELECT
  "__virtual_row_id",
  "id",
  "text",
  "u_ok0" AS "u_ok",
  CASE WHEN "u_ok0" THEN "su" ELSE "url" END AS "u",
  CASE WHEN "u_ok0" THEN CAST(NULL AS VARCHAR) ELSE "title" END AS "te"
FROM marked;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "u_ok" THEN 'https://zh-classical.wikipedia.org/wiki/' || "u"
    ELSE "u"
  END AS "url",
  CASE
    WHEN "u_ok" THEN url_decode("u")
    ELSE "te"
  END AS "title",
  "text"
FROM compressed;
