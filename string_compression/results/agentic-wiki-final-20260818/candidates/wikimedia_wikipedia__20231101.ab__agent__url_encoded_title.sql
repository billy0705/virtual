-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ab.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "ue", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ab.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "ux" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "ue" THEN 'https://ab.wikipedia.org/wiki/' || url_encode("title") ELSE "ux" END AS "url", "title", "text" FROM compressed;
