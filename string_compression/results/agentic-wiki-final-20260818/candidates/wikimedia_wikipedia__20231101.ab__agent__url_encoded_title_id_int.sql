-- Compression
WITH x AS (SELECT *, try_cast("id" AS INTEGER) AS "v" FROM source) SELECT "__virtual_row_id", "title", "text", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ab.wikipedia.org/wiki/' || url_encode("title") THEN TRUE ELSE FALSE END AS "ue", CASE WHEN "url" IS NOT NULL AND "title" IS NOT NULL AND "url" = 'https://ab.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "ux", CASE WHEN "id" = CAST("v" AS VARCHAR) THEN "v" ELSE NULL END AS "ii", CASE WHEN "id" = CAST("v" AS VARCHAR) THEN NULL ELSE "id" END AS "ix" FROM x;

-- Reconstruction
SELECT "__virtual_row_id", COALESCE("ix", CAST("ii" AS VARCHAR)) AS "id", CASE WHEN "ue" THEN 'https://ab.wikipedia.org/wiki/' || url_encode("title") ELSE "ux" END AS "url", "title", "text" FROM compressed;
