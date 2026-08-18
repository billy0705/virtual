-- Compression
SELECT * EXCLUDE ("url") FROM source;

-- Reconstruction
SELECT *, 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") AS "url" FROM compressed;
