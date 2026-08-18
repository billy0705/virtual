-- Compression
WITH x AS (
  SELECT *,
         'https://ab.wikipedia.org/wiki/' || url_encode("title") AS p
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  p IS DISTINCT FROM "url" AS "ub",
  CASE WHEN p IS DISTINCT FROM "url" THEN "url" ELSE NULL END AS "ue"
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE WHEN "ub" THEN "ue" ELSE 'https://ab.wikipedia.org/wiki/' || url_encode("title") END AS "url",
  "title",
  "text"
FROM compressed;
