-- Compression
WITH x AS (
  SELECT
    "__virtual_row_id",
    "id",
    "title",
    "text",
    "url",
    CASE
      WHEN starts_with("url", 'https://zh-classical.wikipedia.org/wiki/%E') THEN TRUE
      ELSE FALSE
    END AS p
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  p AS "url_p",
  CASE WHEN p THEN substr("url", length('https://zh-classical.wikipedia.org/wiki/%E') + 1) ELSE NULL END AS "url_s",
  CASE WHEN p THEN NULL ELSE "url" END AS "url_e"
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "url_p" THEN 'https://zh-classical.wikipedia.org/wiki/%E' || "url_s"
    ELSE "url_e"
  END AS "url",
  "title",
  "text"
FROM compressed;
