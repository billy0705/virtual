-- Compression
SELECT * EXCLUDE ("url") FROM source;

-- Reconstruction
SELECT *, 'https://af.wikipedia.org/wiki/' || url_encode("title") AS "url" FROM compressed;
