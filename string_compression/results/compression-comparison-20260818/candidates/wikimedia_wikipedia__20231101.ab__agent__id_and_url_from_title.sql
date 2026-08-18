-- Compression
WITH p AS (
  SELECT *,
    try_cast("id" AS BIGINT) AS n,
    'https://ab.wikipedia.org/wiki/' || url_encode("title") AS u0
  FROM source
)
SELECT
  "__virtual_row_id", "title", "text",
  n AS "id_n",
  "id" IS DISTINCT FROM cast(n AS VARCHAR) AS "id_bad",
  CASE WHEN "id" IS DISTINCT FROM cast(n AS VARCHAR) THEN "id" ELSE NULL END AS "id_r",
  "url" IS DISTINCT FROM u0 AS "url_bad",
  CASE WHEN "url" IS DISTINCT FROM u0 THEN "url" ELSE NULL END AS "url_r"
FROM p;

-- Reconstruction
SELECT
  "__virtual_row_id",
  CASE WHEN "id_bad" THEN "id_r" ELSE cast("id_n" AS VARCHAR) END AS "id",
  CASE
    WHEN "url_bad" THEN "url_r"
    ELSE 'https://ab.wikipedia.org/wiki/' || url_encode("title")
  END AS "url",
  "title",
  "text"
FROM compressed;
