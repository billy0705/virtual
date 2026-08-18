-- Compression
SELECT * EXCLUDE ("url"),
                           CASE WHEN (("url" IS NULL AND "domain" IS NULL) OR ("url" IS NOT NULL AND "domain" IS NOT NULL AND strpos("url", "domain") > 0)) THEN left("url", strpos("url", "domain") - 1) ELSE NULL END AS "__v_0_url_from_1_domain_prefix",
                           CASE WHEN (("url" IS NULL AND "domain" IS NULL) OR ("url" IS NOT NULL AND "domain" IS NOT NULL AND strpos("url", "domain") > 0)) THEN substr("url", strpos("url", "domain") + length("domain")) ELSE NULL END AS "__v_0_url_from_1_domain_suffix",
                           CASE WHEN (("url" IS NULL AND "domain" IS NULL) OR ("url" IS NOT NULL AND "domain" IS NOT NULL AND strpos("url", "domain") > 0)) THEN NULL ELSE "url" END AS "__v_0_url_from_1_domain_error",
                           NOT (("url" IS NULL AND "domain" IS NULL) OR ("url" IS NOT NULL AND "domain" IS NOT NULL AND strpos("url", "domain") > 0)) AS "__v_0_url_from_1_domain_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_0_url_from_1_domain_prefix", "__v_0_url_from_1_domain_suffix", "__v_0_url_from_1_domain_error", "__v_0_url_from_1_domain_error_present"),
                           CASE WHEN "__v_0_url_from_1_domain_error_present"
                                THEN "__v_0_url_from_1_domain_error"
                                ELSE "__v_0_url_from_1_domain_prefix" || "domain" || "__v_0_url_from_1_domain_suffix"
                           END AS "url"
                    FROM compressed;
