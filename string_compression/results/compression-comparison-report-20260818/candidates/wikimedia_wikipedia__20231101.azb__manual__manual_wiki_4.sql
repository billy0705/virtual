-- Compression
SELECT * EXCLUDE ("title") FROM source;

-- Reconstruction
SELECT *, url_decode(CASE WHEN starts_with("url", 'https://azb.wikipedia.org/wiki/') THEN substr("url", length('https://azb.wikipedia.org/wiki/') + 1) ELSE "url" END) AS "title" FROM compressed;
