-- Compression
SELECT * EXCLUDE ("dump") FROM source;

-- Reconstruction
SELECT *, split_part("file_path", '/', 5) AS "dump" FROM compressed;
