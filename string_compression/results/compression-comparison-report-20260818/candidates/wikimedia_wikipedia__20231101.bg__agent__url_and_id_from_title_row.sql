-- Compression
SELECT "__virtual_row_id", "title", "text", "id" IS NOT DISTINCT FROM CAST("__virtual_row_id" + 2254 AS VARCHAR) AS "id_ok", CASE WHEN "id" IS NOT DISTINCT FROM CAST("__virtual_row_id" + 2254 AS VARCHAR) THEN NULL ELSE "id" END AS "id_e", "url" IS NOT DISTINCT FROM 'https://bg.wikipedia.org/wiki/' || url_encode("title") AS "url_ok", CASE WHEN "url" IS NOT DISTINCT FROM 'https://bg.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "url_e" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", CASE WHEN "id_ok" THEN CAST("__virtual_row_id" + 2254 AS VARCHAR) ELSE "id_e" END AS "id", CASE WHEN "url_ok" THEN 'https://bg.wikipedia.org/wiki/' || url_encode("title") ELSE "url_e" END AS "url", "title", "text" FROM compressed;
