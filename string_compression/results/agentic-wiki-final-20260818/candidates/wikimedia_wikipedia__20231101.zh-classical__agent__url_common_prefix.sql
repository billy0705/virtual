-- Compression
SELECT "__virtual_row_id", "id", "title", "text", COALESCE(starts_with("url", 'https://zh-classical.wikipedia.org/wiki/'), FALSE) AS "u_ok", CASE WHEN COALESCE(starts_with("url", 'https://zh-classical.wikipedia.org/wiki/'), FALSE) THEN substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) ELSE "url" END AS "u_err" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "u_ok" THEN 'https://zh-classical.wikipedia.org/wiki/' || "u_err" ELSE "u_err" END AS "url", "title", "text" FROM compressed;
