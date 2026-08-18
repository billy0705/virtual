-- Compression
SELECT
  "__virtual_row_id",
  "text",
  "id",
  "dump",
  "url",
  "date",
  "file_path",
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
  "file_path",
  'en' AS "language",
  "language_score",
  "token_count"
FROM compressed;
