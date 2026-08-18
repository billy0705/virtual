-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN starts_with("url", 'https://ady.wikipedia.org/wiki/') THEN CASE WHEN substr("url", length('https://ady.wikipedia.org/wiki/') + 1) = url_encode("title") THEN NULL ELSE substr("url", length('https://ady.wikipedia.org/wiki/') + 1) END ELSE NULL END AS "url_suf", CASE WHEN starts_with("url", 'https://ady.wikipedia.org/wiki/') THEN NULL ELSE "url" END AS "url_full" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "url_full" IS NOT NULL THEN "url_full" ELSE 'https://ady.wikipedia.org/wiki/' || COALESCE("url_suf", url_encode("title")) END AS "url", "title", "text" FROM compressed;
