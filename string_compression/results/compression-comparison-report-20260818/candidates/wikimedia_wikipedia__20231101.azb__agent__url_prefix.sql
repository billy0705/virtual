-- Compression
SELECT "__virtual_row_id", "id", "title", "text", "url" IS NOT NULL AND starts_with("url", 'https://azb.wikipedia.org/wiki/') AS "url_p", CASE WHEN "url" IS NOT NULL AND starts_with("url", 'https://azb.wikipedia.org/wiki/') THEN substr("url", length('https://azb.wikipedia.org/wiki/') + 1) ELSE "url" END AS "url_s" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "url_p" THEN 'https://azb.wikipedia.org/wiki/' || "url_s" ELSE "url_s" END AS "url", "title", "text" FROM compressed;
