-- Compression
WITH a AS (
  SELECT *,
         CASE
           WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/')
             THEN url_decode(substr("url", length('https://ab.wikipedia.org/wiki/') + 1))
           ELSE NULL
         END AS p
  FROM source
), b AS (
  SELECT *,
         p IS DISTINCT FROM "title" AS tbad,
         CASE
           WHEN "text" IS NOT NULL
            AND "title" IS NOT NULL
            AND starts_with("text", "title")
             THEN true
           ELSE false
         END AS xmatch
  FROM a
)
SELECT
  "__virtual_row_id",
  "id",
  "url",
  tbad AS "tb",
  CASE WHEN tbad THEN "title" ELSE NULL END AS "te",
  xmatch AS "xb",
  CASE WHEN xmatch THEN substr("text", length("title") + 1) ELSE "text" END AS "xe"
FROM b;

-- Reconstruction
WITH r AS (
  SELECT *,
         CASE
           WHEN "tb" THEN "te"
           WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/')
             THEN url_decode(substr("url", length('https://ab.wikipedia.org/wiki/') + 1))
           ELSE NULL
         END AS rt
  FROM compressed
)
SELECT
  "__virtual_row_id",
  "id",
  "url",
  rt AS "title",
  CASE WHEN "xb" THEN rt || "xe" ELSE "xe" END AS "text"
FROM r;
