-- Compression
SELECT * EXCLUDE ("url") FROM source;

-- Reconstruction
SELECT *, 'https://azb.wikipedia.org/wiki/' || url_encode("title") AS "url" FROM compressed;
