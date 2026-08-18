-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN starts_with("url", 'https://ady.wikipedia.org/wiki/') THEN substr("url", length('https://ady.wikipedia.org/wiki/') + 1) ELSE NULL END AS "url_tail", CASE WHEN starts_with("url", 'https://ady.wikipedia.org/wiki/') THEN NULL ELSE "url" END AS "url_full" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", COALESCE("url_full", 'https://ady.wikipedia.org/wiki/' || "url_tail") AS "url", "title", "text" FROM compressed;
