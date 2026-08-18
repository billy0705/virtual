-- Compression
WITH x AS (
  SELECT *,
         CASE
           WHEN "text" IS NOT NULL
            AND "title" IS NOT NULL
            AND starts_with("text", "title")
             THEN true
           ELSE false
         END AS m
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "url",
  "title",
  m AS "xb",
  CASE WHEN m THEN substr("text", length("title") + 1) ELSE "text" END AS "xe"
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  "url",
  "title",
  CASE WHEN "xb" THEN "title" || "xe" ELSE "xe" END AS "text"
FROM compressed;
