# Agentic String Compression Results

| dataset_id | config_name | strategy | candidate_id | status | selected | snappy_savings_ratio | reconstruction_latency_ms | total_tokens | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wikimedia/wikipedia | 20231101.zh-classical | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_2 | valid | False | 0.009030 | 38.803225 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_4 | valid | True | 0.015495 | 36.804462 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.zh-classical | single |  | skipped | False |  |  | 0 | offline mode |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage |  | skipped | False |  |  | 0 | offline mode |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop |  | skipped | False |  |  | 0 | offline mode |
| wikimedia/wikipedia | 20231101.ab | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_2 | rejected | False | -0.052264 |  | 0 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_4 | valid | True | 0.046534 | 11.115304 | 0 |  |
| wikimedia/wikipedia | 20231101.ab | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ab | single |  | skipped | False |  |  | 0 | offline mode |
| wikimedia/wikipedia | 20231101.ab | two_stage |  | skipped | False |  |  | 0 | offline mode |
| wikimedia/wikipedia | 20231101.ab | tool_loop |  | skipped | False |  |  | 0 | offline mode |
| wikimedia/wikipedia | 20231101.af |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.azb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.bg |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ady |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ar |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.de |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ceb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.nl |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
