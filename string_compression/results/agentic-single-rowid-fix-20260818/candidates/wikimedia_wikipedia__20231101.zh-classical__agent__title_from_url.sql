-- Compression
SELECT "__virtual_row_id", "id", "url", "text", CASE WHEN "url" IS NOT NULL AND starts_with("url", 'https://zh-classical.wikipedia.org/wiki/') AND url_decode(substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1)) = "title" THEN FALSE ELSE TRUE END AS "_te", CASE WHEN "url" IS NOT NULL AND starts_with("url", 'https://zh-classical.wikipedia.org/wiki/') AND url_decode(substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1)) = "title" THEN NULL ELSE "title" END AS "_t" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", CASE WHEN "_te" THEN "_t" ELSE url_decode(substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1)) END AS "title", "text" FROM compressed;
