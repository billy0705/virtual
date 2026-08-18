-- Compression
SELECT "__virtual_row_id", "id", "title", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "url_ok", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ady.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_e", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN TRUE ELSE FALSE END AS "text_ok", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "text_r" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "url_ok" THEN 'https://ady.wikipedia.org/wiki/' || url_encode("title") ELSE "url_e" END AS "url", "title", CASE WHEN "text_ok" THEN "title" || "text_r" ELSE "text_r" END AS "text" FROM compressed;
