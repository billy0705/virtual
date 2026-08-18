-- Compression
SELECT * EXCLUDE ("file_path"),
                           CASE WHEN (("file_path" IS NULL AND "dump" IS NULL) OR ("file_path" IS NOT NULL AND "dump" IS NOT NULL AND strpos("file_path", "dump") > 0)) THEN left("file_path", strpos("file_path", "dump") - 1) ELSE NULL END AS "__v_5_file_path_from_2_dump_prefix",
                           CASE WHEN (("file_path" IS NULL AND "dump" IS NULL) OR ("file_path" IS NOT NULL AND "dump" IS NOT NULL AND strpos("file_path", "dump") > 0)) THEN substr("file_path", strpos("file_path", "dump") + length("dump")) ELSE NULL END AS "__v_5_file_path_from_2_dump_suffix",
                           CASE WHEN (("file_path" IS NULL AND "dump" IS NULL) OR ("file_path" IS NOT NULL AND "dump" IS NOT NULL AND strpos("file_path", "dump") > 0)) THEN NULL ELSE "file_path" END AS "__v_5_file_path_from_2_dump_error",
                           NOT (("file_path" IS NULL AND "dump" IS NULL) OR ("file_path" IS NOT NULL AND "dump" IS NOT NULL AND strpos("file_path", "dump") > 0)) AS "__v_5_file_path_from_2_dump_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_5_file_path_from_2_dump_prefix", "__v_5_file_path_from_2_dump_suffix", "__v_5_file_path_from_2_dump_error", "__v_5_file_path_from_2_dump_error_present"),
                           CASE WHEN "__v_5_file_path_from_2_dump_error_present"
                                THEN "__v_5_file_path_from_2_dump_error"
                                ELSE "__v_5_file_path_from_2_dump_prefix" || "dump" || "__v_5_file_path_from_2_dump_suffix"
                           END AS "file_path"
                    FROM compressed;
