-- Compression
SELECT * EXCLUDE ("title") FROM source;

-- Reconstruction
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://zh-classical.wikipedia.org/wiki/') THEN substr("url", length('https://zh-classical.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed;
