-- Compression
SELECT * EXCLUDE ("language"),
                           CASE WHEN (("language" IS NULL AND "file_path" IS NULL) OR ("language" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "language") > 0)) THEN strpos("file_path", "language") ELSE NULL END AS "__v_6_language_from_5_file_path_pos",
                           CASE WHEN (("language" IS NULL AND "file_path" IS NULL) OR ("language" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "language") > 0)) THEN length("language") ELSE NULL END AS "__v_6_language_from_5_file_path_len",
                           CASE WHEN (("language" IS NULL AND "file_path" IS NULL) OR ("language" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "language") > 0)) THEN NULL ELSE "language" END AS "__v_6_language_from_5_file_path_error",
                           NOT (("language" IS NULL AND "file_path" IS NULL) OR ("language" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "language") > 0)) AS "__v_6_language_from_5_file_path_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_6_language_from_5_file_path_pos", "__v_6_language_from_5_file_path_len", "__v_6_language_from_5_file_path_error", "__v_6_language_from_5_file_path_error_present"),
                           CASE WHEN "__v_6_language_from_5_file_path_error_present"
                                THEN "__v_6_language_from_5_file_path_error"
                                ELSE substr("file_path", "__v_6_language_from_5_file_path_pos", "__v_6_language_from_5_file_path_len")
                           END AS "language"
                    FROM compressed;
