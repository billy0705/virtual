-- Compression
SELECT "__virtual_row_id", "id", "url", "title", CASE WHEN starts_with("text", "title") THEN TRUE ELSE FALSE END AS "t_p", CASE WHEN starts_with("text", "title") THEN substr("text", length("title") + 1) ELSE "text" END AS "t_x" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", "title", CASE WHEN "t_p" THEN "title" || "t_x" ELSE "t_x" END AS "text" FROM compressed;
