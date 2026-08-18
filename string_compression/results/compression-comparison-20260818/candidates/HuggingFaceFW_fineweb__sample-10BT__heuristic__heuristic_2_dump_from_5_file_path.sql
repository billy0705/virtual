-- Compression
SELECT * EXCLUDE ("dump"),
                           CASE WHEN (("dump" IS NULL AND "file_path" IS NULL) OR ("dump" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "dump") > 0)) THEN strpos("file_path", "dump") ELSE NULL END AS "__v_2_dump_from_5_file_path_pos",
                           CASE WHEN (("dump" IS NULL AND "file_path" IS NULL) OR ("dump" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "dump") > 0)) THEN length("dump") ELSE NULL END AS "__v_2_dump_from_5_file_path_len",
                           CASE WHEN (("dump" IS NULL AND "file_path" IS NULL) OR ("dump" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "dump") > 0)) THEN NULL ELSE "dump" END AS "__v_2_dump_from_5_file_path_error",
                           NOT (("dump" IS NULL AND "file_path" IS NULL) OR ("dump" IS NOT NULL AND "file_path" IS NOT NULL AND strpos("file_path", "dump") > 0)) AS "__v_2_dump_from_5_file_path_error_present"
                    FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_2_dump_from_5_file_path_pos", "__v_2_dump_from_5_file_path_len", "__v_2_dump_from_5_file_path_error", "__v_2_dump_from_5_file_path_error_present"),
                           CASE WHEN "__v_2_dump_from_5_file_path_error_present"
                                THEN "__v_2_dump_from_5_file_path_error"
                                ELSE substr("file_path", "__v_2_dump_from_5_file_path_pos", "__v_2_dump_from_5_file_path_len")
                           END AS "dump"
                    FROM compressed;
