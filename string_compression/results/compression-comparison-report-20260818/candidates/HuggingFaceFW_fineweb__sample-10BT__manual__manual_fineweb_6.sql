-- Compression
SELECT * EXCLUDE ("id"), split_part(replace(replace("id", '<urn:uuid:', ''), '>', ''), '-', 1) AS "__v_fineweb_id_part_1", split_part(replace(replace("id", '<urn:uuid:', ''), '>', ''), '-', 2) AS "__v_fineweb_id_part_2", split_part(replace(replace("id", '<urn:uuid:', ''), '>', ''), '-', 3) AS "__v_fineweb_id_part_3", split_part(replace(replace("id", '<urn:uuid:', ''), '>', ''), '-', 4) AS "__v_fineweb_id_part_4", split_part(replace(replace("id", '<urn:uuid:', ''), '>', ''), '-', 5) AS "__v_fineweb_id_part_5" FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_fineweb_id_part_1", "__v_fineweb_id_part_2", "__v_fineweb_id_part_3", "__v_fineweb_id_part_4", "__v_fineweb_id_part_5"), '<urn:uuid:' || "__v_fineweb_id_part_1" || '-' || "__v_fineweb_id_part_2" || '-' || "__v_fineweb_id_part_3" || '-' || "__v_fineweb_id_part_4" || '-' || "__v_fineweb_id_part_5" || '>' AS "id" FROM compressed;
