-- Compression
SELECT "__virtual_row_id", "id", "url", "text", "title" IS NOT DISTINCT FROM url_decode(substr("url", 31)) AS "title_ok", CASE WHEN "title" IS NOT DISTINCT FROM url_decode(substr("url", 31)) THEN NULL ELSE "title" END AS "title_e" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", CASE WHEN "title_ok" THEN url_decode(substr("url", 31)) ELSE "title_e" END AS "title", "text" FROM compressed;
