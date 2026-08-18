-- Compression
SELECT
  "__virtual_row_id",
  "text",
  "url",
  "date",
  "file_path",
  "language_score",
  "token_count",
  CASE WHEN "id" IS NOT NULL AND length("id") = 47 AND starts_with("id", '<urn:uuid:') AND ends_with("id", '>') THEN TRUE ELSE FALSE END AS "id_ok",
  CASE WHEN "id" IS NOT NULL AND length("id") = 47 AND starts_with("id", '<urn:uuid:') AND ends_with("id", '>') THEN substr("id", 11, 36) ELSE NULL END AS "id_x",
  CASE WHEN "id" IS NOT NULL AND length("id") = 47 AND starts_with("id", '<urn:uuid:') AND ends_with("id", '>') THEN NULL ELSE "id" END AS "id_raw",
  CASE WHEN "dump" IS NOT NULL AND length("dump") = 15 AND starts_with("dump", 'CC-MAIN-') THEN TRUE ELSE FALSE END AS "dump_ok",
  CASE WHEN "dump" IS NOT NULL AND length("dump") = 15 AND starts_with("dump", 'CC-MAIN-') THEN substr("dump", 9, 7) ELSE NULL END AS "dump_x",
  CASE WHEN "dump" IS NOT NULL AND length("dump") = 15 AND starts_with("dump", 'CC-MAIN-') THEN NULL ELSE "dump" END AS "dump_raw",
  CASE WHEN "language" = 'en' THEN TRUE ELSE FALSE END AS "language_ok",
  CASE WHEN "language" = 'en' THEN NULL ELSE "language" END AS "language_raw"
FROM source;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "text",
  CASE WHEN "id_ok" THEN '<urn:uuid:' || "id_x" || '>' ELSE "id_raw" END AS "id",
  CASE WHEN "dump_ok" THEN 'CC-MAIN-' || "dump_x" ELSE "dump_raw" END AS "dump",
  "url",
  "date",
  "file_path",
  CASE WHEN "language_ok" THEN 'en' ELSE "language_raw" END AS "language",
  "language_score",
  "token_count"
FROM compressed;
