# Agentic String Compression Results

| dataset_id | config_name | strategy | candidate_id | status | selected | snappy_savings_ratio | reconstruction_latency_ms | total_tokens | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wikimedia/wikipedia | 20231101.zh-classical | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_2 | valid | False | 0.009030 | 37.952908 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_4 | valid | True | 0.015495 | 29.435754 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_from_title | valid | True | 0.023818 | 26.053167 | 11843 |  |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_common_prefix | rejected | False | -0.000932 |  | 11843 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | url_from_title | valid | True | 0.023823 | 25.527696 | 23373 |  |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | title_from_url | valid | False | 0.015286 | 29.349854 | 23373 |  |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop |  | error | False |  |  | 95904 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.ab | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_2 | rejected | False | -0.052264 |  | 0 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_4 | valid | True | 0.046534 | 11.759996 | 0 |  |
| wikimedia/wikipedia | 20231101.ab | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ab | single | url_from_title | valid | True | 0.060150 | 11.488308 | 10973 |  |
| wikimedia/wikipedia | 20231101.ab | single | title_from_url | valid | False | 0.044304 | 12.219008 | 10973 |  |
| wikimedia/wikipedia | 20231101.ab | single | text_without_title_prefix | rejected | False | -0.025877 |  | 10973 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | single | title_and_text_from_url_prefix | valid | False | 0.049575 | 12.534238 | 10973 |  |
| wikimedia/wikipedia | 20231101.ab | two_stage | url_encoded_title | valid | False | 0.059896 | 10.806237 | 20685 |  |
| wikimedia/wikipedia | 20231101.ab | two_stage | url_encoded_title_id_int | valid | True | 0.060469 | 11.186867 | 20685 |  |
| wikimedia/wikipedia | 20231101.ab | tool_loop |  | error | False |  |  | 87840 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.af |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.azb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.bg |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ady |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ar |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.de |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ceb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.nl |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
