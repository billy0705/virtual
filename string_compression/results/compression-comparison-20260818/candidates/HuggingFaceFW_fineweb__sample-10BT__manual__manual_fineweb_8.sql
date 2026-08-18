-- Compression
SELECT * EXCLUDE ("url", "text"), CASE WHEN regexp_matches("url", '^https?://[^/]+/$') THEN "url" ELSE regexp_extract("url", '^(https?://[^/]+)', 1) END AS "__v_url_prefix", regexp_extract("url", '^https?://[^/]+/?(.*)$', 1) || "text" AS "__v_url_path_text", length(regexp_extract("url", '^https?://[^/]+/?(.*)$', 1)) AS "__v_url_path_len" FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_url_prefix", "__v_url_path_text", "__v_url_path_len"), CASE WHEN "__v_url_path_len" = 0 THEN "__v_url_prefix" ELSE rtrim("__v_url_prefix", '/') || '/' || substr("__v_url_path_text", 1, "__v_url_path_len") END AS "url", substr("__v_url_path_text", "__v_url_path_len" + 1) AS "text" FROM compressed;
