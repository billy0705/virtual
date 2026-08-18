-- Compression
SELECT
  "__virtual_row_id",
  "id",
  "url",
  "text",
  NOT ("title" IS NOT DISTINCT FROM url_decode(substr("url", 41))) AS "_t_bad",
  CASE
    WHEN "title" IS NOT DISTINCT FROM url_decode(substr("url", 41)) THEN NULL
    ELSE "title"
  END AS "_t"
FROM "source";

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  "url",
  CASE
    WHEN "_t_bad" THEN "_t"
    ELSE url_decode(substr("url", 41))
  END AS "title",
  "text"
FROM "compressed";
