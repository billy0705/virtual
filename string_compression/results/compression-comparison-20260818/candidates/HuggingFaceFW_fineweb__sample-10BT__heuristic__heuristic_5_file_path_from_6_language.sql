-- Compression
SELECT * EXCLUDE ("file_path"),
                           CASE WHEN (("file_path" IS NULL AND "language" IS NULL) OR ("file_path" IS NOT NULL AND "language" IS NOT NULL AND strpos("file_path", "language") > 0)) THEN left("file_path", strpos("file_path", "language") - 1) ELSE NULL END AS "__v_5_file_path_from_6_language_prefix",
                           CASE WHEN (("file_path" IS NULL AND "language" IS NULL) OR ("file_path" IS NOT NULL AND "language" IS NOT NULL AND strpos("file_path", "language") > 0)) THEN substr("file_path", strpos("file_path", "language") + length("language")) ELSE NULL END AS "__v_5_file_path_from_6_language_suffix",
                           CASE WHEN (("file_path" IS NULL AND "language" IS NULL) OR ("file_path" IS NOT NULL AND "language" IS NOT NULL AND strpos("file_path", "language") > 0)) THEN NULL ELSE "file_path" END AS "__v_5_file_path_from_6_language_error",
                           NOT (("file_path" IS NULL AND "language" IS NULL) OR ("file_path" IS NOT NULL AND "language" IS NOT NULL AND strpos("file_path", "language") > 0)) AS "__v_5_file_path_from_6_language_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_5_file_path_from_6_language_prefix", "__v_5_file_path_from_6_language_suffix", "__v_5_file_path_from_6_language_error", "__v_5_file_path_from_6_language_error_present"),
                           CASE WHEN "__v_5_file_path_from_6_language_error_present"
                                THEN "__v_5_file_path_from_6_language_error"
                                ELSE "__v_5_file_path_from_6_language_prefix" || "language" || "__v_5_file_path_from_6_language_suffix"
                           END AS "file_path"
                    FROM compressed;
