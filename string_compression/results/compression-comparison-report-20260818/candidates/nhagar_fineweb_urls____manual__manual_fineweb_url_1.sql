-- Compression
SELECT * EXCLUDE ("domain") FROM source;

-- Reconstruction
SELECT *, regexp_extract("url", 'https?://(?:[^./]+\.)*([^./]+\.[^./]+)', 1) AS "domain" FROM compressed;
