-- Compression
SELECT * EXCLUDE ("url", "title", "text"), "title" || "text" AS "__v_wiki_title_text", length("title") AS "__v_wiki_title_len" FROM source;

-- Reconstruction
SELECT * EXCLUDE ("__v_wiki_title_text", "__v_wiki_title_len"), substr("__v_wiki_title_text", 1, "__v_wiki_title_len") AS "title", substr("__v_wiki_title_text", "__v_wiki_title_len" + 1) AS "text", 'https://ceb.wikipedia.org/wiki/' || url_encode(substr("__v_wiki_title_text", 1, "__v_wiki_title_len")) AS "url" FROM compressed;
