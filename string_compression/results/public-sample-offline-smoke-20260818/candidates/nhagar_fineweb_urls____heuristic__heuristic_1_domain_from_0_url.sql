-- Compression
SELECT * EXCLUDE ("domain"),
                           CASE WHEN (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) THEN strpos("url", "domain") ELSE NULL END AS "__v_1_domain_from_0_url_pos",
                           CASE WHEN (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) THEN length("domain") ELSE NULL END AS "__v_1_domain_from_0_url_len",
                           CASE WHEN (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) THEN NULL ELSE "domain" END AS "__v_1_domain_from_0_url_error",
                           NOT (("domain" IS NULL AND "url" IS NULL) OR ("domain" IS NOT NULL AND "url" IS NOT NULL AND strpos("url", "domain") > 0)) AS "__v_1_domain_from_0_url_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_1_domain_from_0_url_pos", "__v_1_domain_from_0_url_len", "__v_1_domain_from_0_url_error", "__v_1_domain_from_0_url_error_present"),
                           CASE WHEN "__v_1_domain_from_0_url_error_present"
                                THEN "__v_1_domain_from_0_url_error"
                                ELSE substr("url", "__v_1_domain_from_0_url_pos", "__v_1_domain_from_0_url_len")
                           END AS "domain"
                    FROM compressed;
