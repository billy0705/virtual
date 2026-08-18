-- Compression
SELECT * EXCLUDE ("language"),
                           CASE WHEN (("language" IS NULL AND "text" IS NULL) OR ("language" IS NOT NULL AND "text" IS NOT NULL AND strpos("text", "language") > 0)) THEN strpos("text", "language") ELSE NULL END AS "__v_6_language_from_0_text_pos",
                           CASE WHEN (("language" IS NULL AND "text" IS NULL) OR ("language" IS NOT NULL AND "text" IS NOT NULL AND strpos("text", "language") > 0)) THEN length("language") ELSE NULL END AS "__v_6_language_from_0_text_len",
                           CASE WHEN (("language" IS NULL AND "text" IS NULL) OR ("language" IS NOT NULL AND "text" IS NOT NULL AND strpos("text", "language") > 0)) THEN NULL ELSE "language" END AS "__v_6_language_from_0_text_error",
                           NOT (("language" IS NULL AND "text" IS NULL) OR ("language" IS NOT NULL AND "text" IS NOT NULL AND strpos("text", "language") > 0)) AS "__v_6_language_from_0_text_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_6_language_from_0_text_pos", "__v_6_language_from_0_text_len", "__v_6_language_from_0_text_error", "__v_6_language_from_0_text_error_present"),
                           CASE WHEN "__v_6_language_from_0_text_error_present"
                                THEN "__v_6_language_from_0_text_error"
                                ELSE substr("text", "__v_6_language_from_0_text_pos", "__v_6_language_from_0_text_len")
                           END AS "language"
                    FROM compressed;
