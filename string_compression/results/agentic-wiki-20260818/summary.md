# Agentic String Compression Results

| dataset_id | config_name | strategy | candidate_id | status | selected | snappy_savings_ratio | reconstruction_latency_ms | total_tokens | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wikimedia/wikipedia | 20231101.zh-classical | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_2 | valid | False | 0.009030 | 40.724875 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_4 | valid | True | 0.015495 | 29.067992 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_prefix_tail | rejected | False | -0.001338 |  | 12655 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_from_title | rejected | False | -0.003747 |  | 12655 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_and_title_from_path | rejected | False | -0.005615 |  | 12655 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | url_from_title | valid | False | 0.023808 | 26.253329 | 28642 |  |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | url_and_title_from_suffix | valid | False | 0.017691 | 34.996763 | 28642 |  |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | url_and_text_prefix | valid | True | 0.029511 | 27.621729 | 28642 |  |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | url_title_text_from_suffixes | valid | False | 0.017248 | 29.665717 | 28642 |  |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | url-title | invalid | False |  |  | 110923 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | url-text-title | invalid | False |  |  | 110923 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | text-title-prefix | valid | False | 0.005606 | 25.417708 | 110923 |  |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | title-url | valid | True | 0.015493 | 29.405125 | 110923 |  |
| wikimedia/wikipedia | 20231101.ab | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_2 | rejected | False | -0.052264 |  | 0 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_4 | valid | True | 0.046534 | 12.397700 | 0 |  |
| wikimedia/wikipedia | 20231101.ab | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ab | single |  | error | False |  |  | 0 | ValidationError: 5 validation errors for CandidateBatch
candidates.0
  Value error, __virtual_row_id is reserved [type=value_error, input_value={'id': 'url_from_title', ..."text" FROM compressed'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error
candidates.1
  Value error, __virtual_row_id is reserved [type=value_error, input_value={'id': 'title_from_url', ..."text" FROM compressed'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error
candidates.2
  Value error, __virtual_row_id is reserved [type=value_error, input_value={'id': 'url_prefix', 'sum..."text" FROM compressed'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error
candidates.3
  Value error, __virtual_row_id is reserved [type=value_error, input_value={'id': 'text_after_title'..."text" FROM compressed'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error
candidates.4
  Value error, __virtual_row_id is reserved [type=value_error, input_value={'id': 'url_and_text_from..."text" FROM compressed'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.12/v/value_error |
| wikimedia/wikipedia | 20231101.ab | two_stage | url_from_title | valid | True | 0.060822 | 10.834333 | 16551 |  |
| wikimedia/wikipedia | 20231101.ab | tool_loop | url_from_title | invalid | False |  |  | 51541 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.af |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.azb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.bg |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ady |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ar |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.de |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ceb |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.nl |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
