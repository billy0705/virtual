-- Compression
SELECT * REPLACE (replace("file_path", "dump", '') AS "file_path") FROM source;

-- Reconstruction
SELECT * REPLACE (replace("file_path", 'crawl-data/', 'crawl-data/' || "dump" || '/') AS "file_path") FROM compressed;
