-- Compression
SELECT
  s."__virtual_row_id",
  s."id",
  s."title",
  s."text",
  CASE
    WHEN s."url" IS NOT DISTINCT FROM ('https://bg.wikipedia.org/wiki/' || url_encode(s."title")) THEN TRUE
    ELSE FALSE
  END AS "uk",
  CASE
    WHEN s."url" IS NOT DISTINCT FROM ('https://bg.wikipedia.org/wiki/' || url_encode(s."title")) THEN NULL
    ELSE s."url"
  END AS "ue"
FROM source AS s;

-- Reconstruction
SELECT
  c."__virtual_row_id",
  c."id",
  CASE
    WHEN c."uk" THEN 'https://bg.wikipedia.org/wiki/' || url_encode(c."title")
    ELSE c."ue"
  END AS "url",
  c."title",
  c."text"
FROM compressed AS c;
