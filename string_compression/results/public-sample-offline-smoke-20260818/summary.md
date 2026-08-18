# Agentic String Compression Results

| dataset_id | config_name | strategy | candidate_id | status | selected | snappy_savings_ratio | reconstruction_latency_ms | total_tokens | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HuggingFaceFW/fineweb | sample-10BT | original | original | valid | False | 0.000000 |  |  |  |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_1 | rejected | False | -0.000097 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_2 | invalid | False |  |  | 0 | reconstruction differs in 1000 cell(s) |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_3 | rejected | False | -0.018670 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_5 | valid | True | 0.000875 | 7.336925 | 0 |  |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_6 | rejected | False | -0.005622 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_7 | rejected | False | -0.003613 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_8 | rejected | False | -0.004278 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_4 | skipped | False |  |  | 0 | numeric regression baseline is outside string reconstruction scope |
| HuggingFaceFW/fineweb | sample-10BT | heuristic | heuristic_2_dump_from_5_file_path | rejected | False | -0.003757 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | heuristic | heuristic_5_file_path_from_2_dump | rejected | False | -0.001681 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | heuristic | heuristic_5_file_path_from_6_language | rejected | False | -0.001982 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | heuristic | heuristic_6_language_from_5_file_path | rejected | False | -0.004053 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | heuristic | heuristic_0_text_from_6_language | rejected | False | -0.016066 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | heuristic | heuristic_6_language_from_0_text | rejected | False | -0.005229 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | single |  | skipped | False |  |  | 0 | offline mode |
| HuggingFaceFW/fineweb | sample-10BT | two_stage |  | skipped | False |  |  | 0 | offline mode |
| HuggingFaceFW/fineweb | sample-10BT | tool_loop |  | skipped | False |  |  | 0 | offline mode |
| nhagar/fineweb_urls |  | original | original | valid | False | 0.000000 |  |  |  |
| nhagar/fineweb_urls |  | manual | manual_fineweb_url_1 | invalid | False |  |  | 0 | reconstruction differs in 78 cell(s) |
| nhagar/fineweb_urls |  | manual | manual_fineweb_url_3 | valid | True | 0.140474 | 0.960933 | 0 |  |
| nhagar/fineweb_urls |  | manual | manual_fineweb_url_2 | skipped | False |  |  | 0 | historical method has no lossless reconstruction SQL |
| nhagar/fineweb_urls |  | heuristic | heuristic_0_url_from_1_domain | valid | False | 0.115419 | 1.425054 | 0 |  |
| nhagar/fineweb_urls |  | heuristic | heuristic_1_domain_from_0_url | valid | True | 0.124362 | 1.121317 | 0 |  |
| nhagar/fineweb_urls |  | single |  | skipped | False |  |  | 0 | offline mode |
| nhagar/fineweb_urls |  | two_stage |  | skipped | False |  |  | 0 | offline mode |
| nhagar/fineweb_urls |  | tool_loop |  | skipped | False |  |  | 0 | offline mode |
