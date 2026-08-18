-- Compression
SELECT * EXCLUDE ("url", "text"), "url" || "text" AS "__v_url_text", length("url") AS "__v_url_len" FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_url_text", "__v_url_len"), substr("__v_url_text", 1, "__v_url_len") AS "url", substr("__v_url_text", "__v_url_len" + 1) AS "text" FROM compressed;
