-- Compression
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  COALESCE(left("url", length('https://zh-classical.wikipedia.org/wiki/%E')) = 'https://zh-classical.wikipedia.org/wiki/%E', FALSE) AS "u_p",
  CASE
    WHEN COALESCE(left("url", length('https://zh-classical.wikipedia.org/wiki/%E')) = 'https://zh-classical.wikipedia.org/wiki/%E', FALSE)
      THEN substr("url", length('https://zh-classical.wikipedia.org/wiki/%E') + 1)
    ELSE "url"
  END AS "u_r"
FROM source;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "u_p" THEN 'https://zh-classical.wikipedia.org/wiki/%E' || "u_r"
    ELSE "u_r"
  END AS "url",
  "title",
  "text"
FROM compressed;
