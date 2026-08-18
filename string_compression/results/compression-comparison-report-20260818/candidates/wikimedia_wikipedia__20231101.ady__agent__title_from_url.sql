-- Compression
SELECT "__virtual_row_id", "id", "url", "text", CASE WHEN "title" IS NOT NULL AND "url" IS NOT NULL AND starts_with("url", 'https://ady.wikipedia.org/wiki/') THEN CASE WHEN "title" = url_decode(substr("url", length('https://ady.wikipedia.org/wiki/') + 1)) THEN TRUE ELSE FALSE END ELSE FALSE END AS "title_ok", CASE WHEN "title" IS NOT NULL AND "url" IS NOT NULL AND starts_with("url", 'https://ady.wikipedia.org/wiki/') AND "title" = url_decode(substr("url", length('https://ady.wikipedia.org/wiki/') + 1)) THEN NULL ELSE "title" END AS "title_e" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", CASE WHEN "title_ok" THEN url_decode(substr("url", length('https://ady.wikipedia.org/wiki/') + 1)) ELSE "title_e" END AS "title", "text" FROM compressed;
