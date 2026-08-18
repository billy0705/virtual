-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/') THEN substr("url", length('https://ab.wikipedia.org/wiki/') + 1) ELSE "url" END AS "url_s", CASE WHEN starts_with("url", 'https://ab.wikipedia.org/wiki/') THEN NULL ELSE TRUE END AS "url_x" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "url_x" THEN "url_s" ELSE 'https://ab.wikipedia.org/wiki/' || "url_s" END AS "url", "title", "text" FROM compressed;
