# Agentic String Compression Results

| dataset_id | config_name | strategy | candidate_id | status | selected | snappy_savings_ratio | reconstruction_latency_ms | total_tokens | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wikimedia/wikipedia | 20231101.zh-classical | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_2 | valid | False | 0.009030 | 37.614666 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_4 | valid | True | 0.015495 | 29.711133 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_from_title | valid | False | 0.023829 | 26.826667 | 12584 |  |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_and_numeric_id | valid | True | 0.023980 | 26.149554 | 12584 |  |
| wikimedia/wikipedia | 20231101.zh-classical | single | title_from_url | valid | False | 0.015213 | 31.180154 | 12584 |  |
| wikimedia/wikipedia | 20231101.ab | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_2 | rejected | False | -0.052264 |  | 0 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_4 | valid | True | 0.046534 | 11.830121 | 0 |  |
| wikimedia/wikipedia | 20231101.ab | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ab | single | url_title_pct | rejected | False | -0.003901 |  | 7672 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | single | url_prefix | rejected | False | -0.007599 |  | 7672 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.af |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.azb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.bg |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ady |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ar |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.de |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ceb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.nl |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
