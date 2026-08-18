-- Compression
SELECT "__virtual_row_id", "id", "url", "text", CASE WHEN "title" IS NOT DISTINCT FROM CASE WHEN starts_with("url", 'https://af.wikipedia.org/wiki/') THEN try(url_decode(substring("url", length('https://af.wikipedia.org/wiki/') + 1))) ELSE NULL END THEN FALSE ELSE TRUE END AS "_t_bad", CASE WHEN "title" IS NOT DISTINCT FROM CASE WHEN starts_with("url", 'https://af.wikipedia.org/wiki/') THEN try(url_decode(substring("url", length('https://af.wikipedia.org/wiki/') + 1))) ELSE NULL END THEN NULL ELSE "title" END AS "_t_raw" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", "url", CASE WHEN "_t_bad" THEN "_t_raw" ELSE CASE WHEN starts_with("url", 'https://af.wikipedia.org/wiki/') THEN try(url_decode(substring("url", length('https://af.wikipedia.org/wiki/') + 1))) ELSE NULL END END AS "title", "text" FROM compressed;
