-- Compression
SELECT * EXCLUDE ("text"),
                           CASE WHEN (("text" IS NULL AND "language" IS NULL) OR ("text" IS NOT NULL AND "language" IS NOT NULL AND strpos("text", "language") > 0)) THEN left("text", strpos("text", "language") - 1) ELSE NULL END AS "__v_0_text_from_6_language_prefix",
                           CASE WHEN (("text" IS NULL AND "language" IS NULL) OR ("text" IS NOT NULL AND "language" IS NOT NULL AND strpos("text", "language") > 0)) THEN substr("text", strpos("text", "language") + length("language")) ELSE NULL END AS "__v_0_text_from_6_language_suffix",
                           CASE WHEN (("text" IS NULL AND "language" IS NULL) OR ("text" IS NOT NULL AND "language" IS NOT NULL AND strpos("text", "language") > 0)) THEN NULL ELSE "text" END AS "__v_0_text_from_6_language_error",
                           NOT (("text" IS NULL AND "language" IS NULL) OR ("text" IS NOT NULL AND "language" IS NOT NULL AND strpos("text", "language") > 0)) AS "__v_0_text_from_6_language_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_0_text_from_6_language_prefix", "__v_0_text_from_6_language_suffix", "__v_0_text_from_6_language_error", "__v_0_text_from_6_language_error_present"),
                           CASE WHEN "__v_0_text_from_6_language_error_present"
                                THEN "__v_0_text_from_6_language_error"
                                ELSE "__v_0_text_from_6_language_prefix" || "language" || "__v_0_text_from_6_language_suffix"
                           END AS "text"
                    FROM compressed;
