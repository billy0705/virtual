-- Compression
SELECT "__virtual_row_id", "id", "title", "url" IS NOT DISTINCT FROM 'https://bg.wikipedia.org/wiki/' || url_encode("title") AS "url_ok", CASE WHEN "url" IS NOT DISTINCT FROM 'https://bg.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_e", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN TRUE ELSE FALSE END AS "text_p", CASE WHEN "text" IS NOT NULL AND "title" IS NOT NULL AND starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "text_r" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "url_ok" THEN 'https://bg.wikipedia.org/wiki/' || url_encode("title") ELSE "url_e" END AS "url", "title", CASE WHEN "text_p" THEN "title" || "text_r" ELSE "text_r" END AS "text" FROM compressed;
