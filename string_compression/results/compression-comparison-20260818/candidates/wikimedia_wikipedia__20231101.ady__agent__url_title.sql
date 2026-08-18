-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_err" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", COALESCE("url_err", 'https://ady.wikipedia.org/wiki/' || url_encode("title")) AS "url", "title", "text" FROM compressed;
