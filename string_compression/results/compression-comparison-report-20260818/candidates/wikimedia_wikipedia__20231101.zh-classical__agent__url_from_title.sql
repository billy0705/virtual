-- Compression
SELECT "__virtual_row_id", "id", "title", "text" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") AS "url", "title", "text" FROM compressed;
