-- Compression
SELECT * REPLACE (CASE WHEN starts_with("id", '<urn:uuid:') THEN substr("id", length('<urn:uuid:') + 1) ELSE "id" END AS "id", CASE WHEN starts_with("dump", 'CC-MAIN-') THEN substr("dump", length('CC-MAIN-') + 1) ELSE "dump" END AS "dump", CASE WHEN starts_with("url", 'http') THEN substr("url", length('http') + 1) ELSE "url" END AS "url", CASE WHEN starts_with("file_path", 's3://commoncrawl/crawl-data/CC-MAIN-') THEN substr("file_path", length('s3://commoncrawl/crawl-data/CC-MAIN-') + 1) ELSE "file_path" END AS "file_path") FROM source;

-- Reconstruction
SELECT * REPLACE (CASE WHEN "id" IS NULL THEN NULL ELSE '<urn:uuid:' || "id" END AS "id", CASE WHEN "dump" IS NULL THEN NULL ELSE 'CC-MAIN-' || "dump" END AS "dump", CASE WHEN "url" IS NULL THEN NULL ELSE 'http' || "url" END AS "url", CASE WHEN "file_path" IS NULL THEN NULL ELSE 's3://commoncrawl/crawl-data/CC-MAIN-' || "file_path" END AS "file_path") FROM compressed;
