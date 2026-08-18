-- Compression
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  CASE WHEN "file_path" IS NOT NULL AND starts_with("file_path", 's3://commoncrawl/crawl-data/CC-MAIN-201') AND ends_with("file_path", '.warc.gz') THEN TRUE ELSE FALSE END AS "fp_ok",
  CASE WHEN "file_path" IS NOT NULL AND starts_with("file_path", 's3://commoncrawl/crawl-data/CC-MAIN-201') AND ends_with("file_path", '.warc.gz') THEN substr("file_path", length('s3://commoncrawl/crawl-data/CC-MAIN-201') + 1, length("file_path") - length('s3://commoncrawl/crawl-data/CC-MAIN-201') - length('.warc.gz')) ELSE "file_path" END AS "fp_p",
  "language_score",
  "token_count"
FROM source;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  CASE WHEN "fp_ok" THEN 's3://commoncrawl/crawl-data/CC-MAIN-201' || "fp_p" || '.warc.gz' ELSE "fp_p" END AS "file_path",
  'en' AS "language",
  "language_score",
  "token_count"
FROM compressed;
