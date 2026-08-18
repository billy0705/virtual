-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "url_ok", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_e" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "url_ok" THEN 'https://ady.wikipedia.org/wiki/' || url_encode("title") ELSE "url_e" END AS "url", "title", "text" FROM compressed;
