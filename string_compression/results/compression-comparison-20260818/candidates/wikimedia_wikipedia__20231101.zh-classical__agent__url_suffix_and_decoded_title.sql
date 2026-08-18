-- Compression
WITH x AS (
  SELECT
    "__virtual_row_id",
    "id",
    "text",
    "title",
    "url",
    CASE
      WHEN starts_with("url", 'https://zh-classical.wikipedia.org/wiki/%E') THEN TRUE
      ELSE FALSE
    END AS p
  FROM source
), y AS (
  SELECT
    "__virtual_row_id",
    "id",
    "text",
    "title",
    p,
    CASE WHEN p THEN substr("url", length('https://zh-classical.wikipedia.org/wiki/%E') + 1) ELSE NULL END AS s,
    CASE WHEN p THEN NULL ELSE "url" END AS e
  FROM x
), z AS (
  SELECT
    *,
    CASE
      WHEN p AND "title" IS NOT DISTINCT FROM url_decode(s) THEN TRUE
      ELSE FALSE
    END AS t_ok
  FROM y
)
SELECT
  "__virtual_row_id",
  "id",
  "text",
  p AS "url_p",
  s AS "url_s",
  e AS "url_e",
  t_ok AS "title_ok",
  CASE WHEN t_ok THEN NULL ELSE "title" END AS "title_e"
FROM z;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "url_p" THEN 'https://zh-classical.wikipedia.org/wiki/%E' || "url_s"
    ELSE "url_e"
  END AS "url",
  CASE
    WHEN "title_ok" THEN url_decode("url_s")
    ELSE "title_e"
  END AS "title",
  "text"
FROM compressed;
