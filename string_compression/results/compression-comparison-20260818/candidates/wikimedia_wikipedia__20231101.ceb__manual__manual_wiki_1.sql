-- Compression
SELECT * EXCLUDE ("url") FROM source;

-- Reconstruction
SELECT *, 'https://ceb.wikipedia.org/wiki/' || url_encode("title") AS "url" FROM compressed;
