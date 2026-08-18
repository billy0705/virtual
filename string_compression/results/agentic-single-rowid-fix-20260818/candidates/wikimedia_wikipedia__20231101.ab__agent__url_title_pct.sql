-- Compression
SELECT "__virtual_row_id", "id", "title", "text", CASE WHEN "url" = 'https://ab.wikipedia.org/wiki/' || replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(url_encode("title"), '%', '%25'), '!', '%21'), '''', '%27'), '(', '%28'), ')', '%29'), '*', '%2A'), '-', '%2D'), '.', '%2E'), '_', '%5F'), '~', '%7E'), '%2F', '/'), '%3A', ':'), '%40', '@') THEN NULL ELSE "url" END AS "url_e" FROM source;

-- Reconstruction
SELECT "__virtual_row_id", "id", COALESCE("url_e", 'https://ab.wikipedia.org/wiki/' || replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(url_encode("title"), '%', '%25'), '!', '%21'), '''', '%27'), '(', '%28'), ')', '%29'), '*', '%2A'), '-', '%2D'), '.', '%2E'), '_', '%5F'), '~', '%7E'), '%2F', '/'), '%3A', ':'), '%40', '@')) AS "url", "title", "text" FROM compressed;
