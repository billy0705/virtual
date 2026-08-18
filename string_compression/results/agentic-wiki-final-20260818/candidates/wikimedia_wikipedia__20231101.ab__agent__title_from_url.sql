-- Compression
WITH x AS (
  SELECT *,
         CASE
           WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/')
             THEN url_decode(substr("url", length('https://ab.wikipedia.org/wiki/') + 1))
           ELSE NULL
         END AS p
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "url",
  "text",
  p IS DISTINCT FROM "title" AS "tb",
  CASE WHEN p IS DISTINCT FROM "title" THEN "title" ELSE NULL END AS "te"
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  "url",
  CASE
    WHEN "tb" THEN "te"
    WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/')
      THEN url_decode(substr("url", length('https://ab.wikipedia.org/wiki/') + 1))
    ELSE NULL
  END AS "title",
  "text"
FROM compressed;
