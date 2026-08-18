-- Compression
WITH x AS (
  SELECT
    *,
    "url" IS NOT NULL
      AND "title" IS NOT NULL
      AND "url" = 'https://zh-classical.wikipedia.org/wiki/%E' || url_encode("title") AS ok
  FROM source
)
SELECT
  "__virtual_row_id",
  "id",
  "text",
  ok AS "ut_ok",
  CASE WHEN ok THEN NULL ELSE "url" END AS "ut_u",
  CASE WHEN ok THEN NULL ELSE "title" END AS "ut_t"
FROM x;

-- Reconstruction
SELECT
  "__virtual_row_id",
  "id",
  CASE
    WHEN "ut_ok" THEN 'https://zh-classical.wikipedia.org/wiki/%E' || url_encode(url_decode(substr('https://zh-classical.wikipedia.org/wiki/%E' || '', length('https://zh-classical.wikipedia.org/wiki/%E') + 1)))
    ELSE "ut_u"
  END AS "url",
  CASE
    WHEN "ut_ok" THEN url_decode(substr(CASE WHEN "ut_ok" THEN 'https://zh-classical.wikipedia.org/wiki/%E' || url_encode(url_decode(substr("ut_u", length('https://zh-classical.wikipedia.org/wiki/%E') + 1))) ELSE "ut_u" END, length('https://zh-classical.wikipedia.org/wiki/%E') + 1))
    ELSE "ut_t"
  END AS "title",
  "text"
FROM compressed;
