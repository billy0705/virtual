-- Compression
SELECT "__virtual_row_id", "id", "title", CASE WHEN "url" IS NOT DISTINCT FROM ('https://azb.wikipedia.org/wiki/' || url_encode("title")) THEN TRUE ELSE FALSE END AS "u_ok", CASE WHEN "url" IS NOT DISTINCT FROM ('https://azb.wikipedia.org/wiki/' || url_encode("title")) THEN NULL ELSE "url" END AS "u_x", CASE WHEN starts_with("text", "title") THEN TRUE ELSE FALSE END AS "t_p", CASE WHEN starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "t_x" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "u_ok" THEN 'https://azb.wikipedia.org/wiki/' || url_encode("title") ELSE "u_x" END AS "url", "title", CASE WHEN "t_p" THEN "title" || "t_x" ELSE "t_x" END AS "text" FROM compressed;
