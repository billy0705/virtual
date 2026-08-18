-- Compression
SELECT "__virtual_row_id", "id", "text", substr("url", 32) AS "p" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", 'https://ceb.wikipedia.org/wiki/' || "p" AS "url", url_decode("p") AS "title", "text" FROM compressed;
