-- Compression
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  "language",
  "language_score",
  "token_count",
  CASE
    WHEN "file_path" IS NOT NULL
     AND starts_with("file_path", 's3://commoncrawl/crawl-data/')
     AND ends_with("file_path", '.warc.gz')
     AND length("file_path") >= length('s3://commoncrawl/crawl-data/') + length('.warc.gz')
    THEN TRUE ELSE FALSE
  END AS "file_path_ok",
  CASE
    WHEN "file_path" IS NOT NULL
     AND starts_with("file_path", 's3://commoncrawl/crawl-data/')
     AND ends_with("file_path", '.warc.gz')
     AND length("file_path") >= length('s3://commoncrawl/crawl-data/') + length('.warc.gz')
    THEN substr("file_path", length('s3://commoncrawl/crawl-data/') + 1, length("file_path") - length('s3://commoncrawl/crawl-data/') - length('.warc.gz'))
    ELSE NULL
  END AS "file_path_x",
  CASE
    WHEN "file_path" IS NOT NULL
     AND starts_with("file_path", 's3://commoncrawl/crawl-data/')
     AND ends_with("file_path", '.warc.gz')
     AND length("file_path") >= length('s3://commoncrawl/crawl-data/') + length('.warc.gz')
    THEN NULL ELSE "file_path"
  END AS "file_path_raw"
FROM source;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  CASE WHEN "file_path_ok" THEN 's3://commoncrawl/crawl-data/' || "file_path_x" || '.warc.gz' ELSE "file_path_raw" END AS "file_path",
  "language",
  "language_score",
  "token_count"
FROM compressed;
