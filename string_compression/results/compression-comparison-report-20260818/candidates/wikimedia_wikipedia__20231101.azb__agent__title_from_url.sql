-- Compression
SELECT "__virtual_row_id", "id", "url", "text", "title" IS NOT NULL AND "url" IS NOT NULL AND starts_with("url", 'https://azb.wikipedia.org/wiki/') AND "title" = url_decode(substr("url", length('https://azb.wikipedia.org/wiki/') + 1)) AS "title_ok", CASE WHEN "title" IS NOT NULL AND "url" IS NOT NULL AND starts_with("url", 'https://azb.wikipedia.org/wiki/') AND "title" = url_decode(substr("url", length('https://azb.wikipedia.org/wiki/') + 1)) THEN NULL ELSE "title" END AS "title_x" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", CASE WHEN "title_ok" THEN url_decode(substr("url", length('https://azb.wikipedia.org/wiki/') + 1)) ELSE "title_x" END AS "title", "text" FROM compressed;
