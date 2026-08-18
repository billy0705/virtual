-- Compression
WITH x AS (SELECT *, CASE WHEN starts_with("url", 'https://ceb.wikipedia.org/wiki/') THEN TRUE ELSE FALSE END AS p, CASE WHEN starts_with("url", 'https://ceb.wikipedia.org/wiki/') THEN substr("url", length('https://ceb.wikipedia.org/wiki/') + 1) ELSE "url" END AS t FROM source) SELECT "__virtual_row_id", "id", "text", p AS "u_p", t AS "u_t", CASE WHEN try(url_decode(t)) = "title" THEN TRUE ELSE FALSE END AS "t_ok", CASE WHEN try(url_decode(t)) = "title" THEN NULL ELSE "title" END AS "t_x" FROM x;

-- Reconstruction
SELECT "__virtual_row_id", "id", CASE WHEN "u_p" THEN 'https://ceb.wikipedia.org/wiki/' || "u_t" ELSE "u_t" END AS "url", CASE WHEN "t_ok" THEN try(url_decode("u_t")) ELSE "t_x" END AS "title", "text" FROM compressed;
