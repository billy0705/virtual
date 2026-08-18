-- Compression
SELECT "__virtual_row_id", "title", "text", try_cast("id" AS INTEGER) AS "_idn", CASE WHEN "id" IS NOT NULL AND CAST(try_cast("id" AS INTEGER) AS VARCHAR) = "id" THEN NULL ELSE "id" END AS "_ide", CASE WHEN "id" IS NOT NULL AND CAST(try_cast("id" AS INTEGER) AS VARCHAR) = "id" THEN TRUE ELSE FALSE END AS "_idok", CASE WHEN "url" IS NOT NULL AND "url" = 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") THEN FALSE ELSE TRUE END AS "_ue", CASE WHEN "url" IS NOT NULL AND "url" = 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") THEN NULL ELSE "url" END AS "_u" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", CASE WHEN "_idok" THEN CAST("_idn" AS VARCHAR) ELSE "_ide" END AS "id", CASE WHEN "_ue" THEN "_u" ELSE 'https://zh-classical.wikipedia.org/wiki/' || url_encode("title") END AS "url", "title", "text" FROM compressed;
