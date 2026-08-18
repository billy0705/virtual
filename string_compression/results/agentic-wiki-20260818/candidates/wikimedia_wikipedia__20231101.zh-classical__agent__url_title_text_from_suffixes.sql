-- Compression
WITH raw AS (
  SELECT *,
    substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) AS "su",
    substr("text", length("title") + 1) AS "sx"
  FROM source
), marked AS (
  SELECT *,
    coalesce(
      "url" LIKE 'https://zh-classical.wikipedia.org/wiki/%'
      AND try(url_decode("su")) IS NOT DISTINCT FROM "title"
      AND starts_with("text", "title"),
      false
    ) AS "ut_ok0"
  FROM raw
)
SELECT
  "__virtual_row_id",
  "id",
  "ut_ok0" AS "ut_ok",
  CASE WHEN "ut_ok0" THEN "su" ELSE "url" END AS "u",
  CASE WHEN "ut_ok0" THEN CAST(NULL AS VARCHAR) ELSE "title" END AS "te",
  CASE WHEN "ut_ok0" THEN "sx" ELSE "text" END AS "x"
FROM marked;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "ut_ok" THEN 'https://zh-classical.wikipedia.org/wiki/' || "u"
    ELSE "u"
  END AS "url",
  CASE WHEN "ut_ok" THEN url_decode("u") ELSE "te" END AS "title",
  CASE
    WHEN "ut_ok" THEN url_decode("u") || "x"
    ELSE "x"
  END AS "text"
FROM compressed;
