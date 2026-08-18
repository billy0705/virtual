-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" = 'https://ceb.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "u_ok", CASE WHEN "url" = 'https://ceb.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "u_x" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "u_ok" THEN 'https://ceb.wikipedia.org/wiki/' || url_encode("title") ELSE "u_x" END AS "url", "title", "text" FROM compressed;
