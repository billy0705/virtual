-- Compression
WITH p AS (
  SELECT *, try_cast("id" AS BIGINT) AS n
  FROM source
)
SELECT
  "__virtual_row_id", "url", "title", "text",
  n AS "id_n",
  "id" IS DISTINCT FROM cast(n AS VARCHAR) AS "id_bad",
  CASE WHEN "id" IS DISTINCT FROM cast(n AS VARCHAR) THEN "id" ELSE NULL END AS "id_r"
FROM p;

-- Reconstruction
SELECT
  "__virtual_row_id",
  CASE WHEN "id_bad" THEN "id_r" ELSE cast("id_n" AS VARCHAR) END AS "id",
  "url",
  "title",
  "text"
FROM compressed;
