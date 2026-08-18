-- Compression
SELECT * EXCLUDE ("domain"), strpos("url", "domain") AS "__v_domain_offset", length("domain") AS "__v_domain_length" FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_domain_offset", "__v_domain_length"), substr("url", "__v_domain_offset", "__v_domain_length") AS "domain" FROM compressed;
