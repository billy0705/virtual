-- Compression
SELECT "__virtual_row_id", "id", "title", CASE WHEN starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "tp", starts_with("text", "title") AS "tm" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") AS "url", "title", CASE WHEN "tm" THEN "title" || "tp" ELSE "tp" END AS "text" FROM compressed;
