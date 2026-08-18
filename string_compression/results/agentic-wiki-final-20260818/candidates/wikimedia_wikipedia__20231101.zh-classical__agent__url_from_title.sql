-- Compression
SELECT
  "__virtual_row_id",
  "id",
  "title",
  "text",
  NOT ("url" IS NOT DISTINCT FROM ('https://zh-classical.wikipedia.org/wiki/' || url_encode("title"))) AS "_u_bad",
  CASE
    WHEN "url" IS NOT DISTINCT FROM ('https://zh-classical.wikipedia.org/wiki/' || url_encode("title")) THEN NULL
    ELSE "url"
  END AS "_u"
FROM "source";

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "_u_bad" THEN "_u"
    ELSE 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title")
  END AS "url",
  "title",
  "text"
FROM "compressed";
