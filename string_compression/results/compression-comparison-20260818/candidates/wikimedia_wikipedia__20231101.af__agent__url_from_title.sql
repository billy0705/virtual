-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" IS NOT DISTINCT FROM CASE WHEN "title" IS NULL THEN NULL ELSE 'https://af.wikipedia.org/wiki/' || url_encode("title") END THEN FALSE ELSE TRUE END AS "_u_bad", CASE WHEN "url" IS NOT DISTINCT FROM CASE WHEN "title" IS NULL THEN NULL ELSE 'https://af.wikipedia.org/wiki/' || url_encode("title") END THEN NULL ELSE "url" END AS "_u_raw" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "_u_bad" THEN "_u_raw" ELSE CASE WHEN "title" IS NULL THEN NULL ELSE 'https://af.wikipedia.org/wiki/' || url_encode("title") END END AS "url", "title", "text" FROM compressed;
