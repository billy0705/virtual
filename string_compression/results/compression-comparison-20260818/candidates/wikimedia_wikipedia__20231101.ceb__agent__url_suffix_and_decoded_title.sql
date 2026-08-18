-- Compression
WITH x AS (
  SELECT
    *,
    COALESCE(starts_with("url", 'https://ceb.wikipedia.org/wiki/'), FALSE) AS p
  FROM source
), y AS (
  SELECT
    *,
    CASE WHEN p THEN substr("url", length('https://ceb.wikipedia.org/wiki/') + 1) ELSE "url" END AS u
  FROM x
), z AS (
  SELECT
    *,
    CASE
      WHEN p AND regexp_matches(u, '^([^%]|%[0-9A-Fa-f]{2})*$')
        THEN ("title" IS NOT DISTINCT FROM url_decode(u))
      ELSE FALSE
    END AS d
  FROM y
)
SELECT
  "__virtual_row_id",
  "id",
  "text",
  u AS "_u",
  p AS "_p",
  CASE WHEN d THEN NULL ELSE "title" END AS "_t",
  d AS "_d"
FROM z;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE WHEN "_p" THEN 'https://ceb.wikipedia.org/wiki/' || "_u" ELSE "_u" END AS "url",
  CASE WHEN "_d" THEN url_decode("_u") ELSE "_t" END AS "title",
  "text"
FROM compressed;
