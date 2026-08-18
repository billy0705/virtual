-- Compression
SELECT "__virtual_row_id", "id", "text", substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) AS "p" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", 'https://zh-classical.wikipedia.org/wiki/' || "p" AS "url", url_decode("p") AS "title", "text" FROM compressed;
