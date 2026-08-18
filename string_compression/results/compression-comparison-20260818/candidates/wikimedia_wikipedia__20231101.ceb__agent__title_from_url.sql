-- Compression
SELECT "__virtual_row_id", "id", "url", "text" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", url_decode(substr("url", 32)) AS "title", "text" FROM compressed;
