-- Compression
SELECT * EXCLUDE ("url"), CASE WHEN "url" IS NOT DISTINCT FROM ('https://ab.wikipedia.org/wiki/' || url_encode("title")) THEN TRUE ELSE FALSE END AS "uok", CASE WHEN "url" IS NOT DISTINCT FROM ('https://ab.wikipedia.org/wiki/' || url_encode("title")) THEN NULL ELSE "url" END AS "uerr" FROM source;

-- Reconstruction
SELECT * EXCLUDE ("uok", "uerr"), CASE WHEN "uok" THEN 'https://ab.wikipedia.org/wiki/' || url_encode("title") ELSE "uerr" END AS "url" FROM compressed;
