-- Compression
WITH x AS (
  SELECT
    *,
    COALESCE(starts_with("url", 'https://ceb.wikipedia.org/wiki/'), FALSE) AS p
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  CASE WHEN p THEN substr("url", length('https://ceb.wikipedia.org/wiki/') + 1) ELSE "url" END AS "_u",
  p AS "_p"
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE WHEN "_p" THEN 'https://ceb.wikipedia.org/wiki/' || "_u" ELSE "_u" END AS "url",
  "title",
  "text"
FROM compressed;
