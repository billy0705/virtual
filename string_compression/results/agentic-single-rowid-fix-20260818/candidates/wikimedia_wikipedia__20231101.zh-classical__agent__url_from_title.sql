-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT NULL AND "url" = 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") THEN FALSE ELSE TRUE END AS "_ue", CASE WHEN "url" IS NOT NULL AND "url" = 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "_u" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "_ue" THEN "_u" ELSE 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") END AS "url", "title", "text" FROM compressed;
