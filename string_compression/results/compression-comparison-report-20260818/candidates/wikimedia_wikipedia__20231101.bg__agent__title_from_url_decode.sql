-- Compression
SELECT
  s."__virtual_row_id",
  s."id",
  s."url",
  s."text",
  CASE
    WHEN s."url" IS NOT NULL
     AND starts_with(s."url", 'https://bg.wikipedia.org/wiki/')
     AND try(url_decode(substring(s."url", length('https://bg.wikipedia.org/wiki/') + 1))) IS NOT DISTINCT FROM s."title"
    THEN TRUE
    ELSE FALSE
  END AS "tk",
  CASE
    WHEN s."url" IS NOT NULL
     AND starts_with(s."url", 'https://bg.wikipedia.org/wiki/')
     AND try(url_decode(substring(s."url", length('https://bg.wikipedia.org/wiki/') + 1))) IS NOT DISTINCT FROM s."title"
    THEN NULL
    ELSE s."title"
  END AS "te"
FROM source AS s;

-- Reconstruction
SELECT
  c."__virtual_row_id",
  c."id",
  c."url",
  CASE
    WHEN c."tk" THEN try(url_decode(substring(c."url", length('https://bg.wikipedia.org/wiki/') + 1)))
    ELSE c."te"
  END AS "title",
  c."text"
FROM compressed AS c;
