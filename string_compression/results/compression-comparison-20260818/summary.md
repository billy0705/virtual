# Agentic String Compression Results

| dataset_id | config_name | strategy | candidate_id | status | selected | snappy_savings_ratio | reconstruction_latency_ms | total_tokens | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| wikimedia/wikipedia | 20231101.zh-classical | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_2 | valid | False | 0.009030 | 19.984379 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | manual | manual_wiki_4 | valid | True | 0.015495 | 14.868642 | 0 |  |
| wikimedia/wikipedia | 20231101.zh-classical | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_from_title | error | False |  |  | 13398 | BinderException: Binder Error: Ambiguous reference to column name "id" (use: "x.id" or "source.id") |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_common_prefix | rejected | False | -0.002582 |  | 13398 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.zh-classical | single | url_suffix_and_decoded_title | error | False |  |  | 13398 | InvalidInputException: Invalid Input Error: Failed to decode string "5%B2%B3%E9%A3%9B" using URL decoding - decoded value is invalid UTF8 |
| wikimedia/wikipedia | 20231101.zh-classical | two_stage | url_from_title | valid | True | 0.023805 | 13.970179 | 23092 |  |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | url_from_title | invalid | False |  |  | 69591 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | title_from_url | valid | False | 0.015493 | 14.958187 | 69591 |  |
| wikimedia/wikipedia | 20231101.zh-classical | tool_loop | url_title_from_suffix | valid | True | 0.017968 | 14.745804 | 69591 |  |
| wikimedia/wikipedia | 20231101.ab | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_2 | rejected | False | -0.052264 |  | 0 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.ab | manual | manual_wiki_4 | valid | True | 0.046534 | 6.336421 | 0 |  |
| wikimedia/wikipedia | 20231101.ab | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ab | single | url_from_title | valid | True | 0.060009 | 5.612737 | 10620 |  |
| wikimedia/wikipedia | 20231101.ab | single | id_as_integer | rejected | False | -0.013377 |  | 10620 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | single | url_strip_base | rejected | False | -0.011477 |  | 10620 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ab | single | id_and_url_from_title | valid | False | 0.059963 | 5.729554 | 10620 |  |
| wikimedia/wikipedia | 20231101.ab | two_stage | url_from_title | valid | True | 0.060117 | 5.625850 | 20674 |  |
| wikimedia/wikipedia | 20231101.ab | two_stage | url_title_pair | valid | False | 0.045217 | 6.137071 | 20674 |  |
| wikimedia/wikipedia | 20231101.ab | tool_loop |  | error | False |  |  | 74243 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.af | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.af | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.af | manual | manual_wiki_2 | valid | False | 0.004318 | 70.082300 | 0 |  |
| wikimedia/wikipedia | 20231101.af | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 1 cell(s) |
| wikimedia/wikipedia | 20231101.af | manual | manual_wiki_4 | valid | True | 0.006860 | 33.218808 | 0 |  |
| wikimedia/wikipedia | 20231101.af | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.af | single | url_from_title | valid | True | 0.007810 | 39.920683 | 7667 |  |
| wikimedia/wikipedia | 20231101.af | single | title_from_url | valid | False | 0.006779 | 32.997996 | 7667 |  |
| wikimedia/wikipedia | 20231101.af | two_stage | url_from_title | valid | True | 0.007808 | 39.634992 | 14583 |  |
| wikimedia/wikipedia | 20231101.af | two_stage | title_from_url | valid | False | 0.006778 | 39.921696 | 14583 |  |
| wikimedia/wikipedia | 20231101.af | tool_loop |  | error | False |  |  | 57589 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.azb | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.azb | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.azb | manual | manual_wiki_2 | valid | False | 0.014238 | 52.367034 | 0 |  |
| wikimedia/wikipedia | 20231101.azb | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 6 cell(s) |
| wikimedia/wikipedia | 20231101.azb | manual | manual_wiki_4 | valid | True | 0.030486 | 38.170254 | 0 |  |
| wikimedia/wikipedia | 20231101.azb | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.azb | single | url_prefix | rejected | False | -0.003675 |  | 10363 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.azb | single | url_from_title | valid | True | 0.045717 | 33.764217 | 10363 |  |
| wikimedia/wikipedia | 20231101.azb | single | title_from_url | valid | False | 0.030169 | 38.473275 | 10363 |  |
| wikimedia/wikipedia | 20231101.azb | two_stage | url_from_title | valid | False | 0.045727 | 30.825108 | 22754 |  |
| wikimedia/wikipedia | 20231101.azb | two_stage | text_title_prefix | valid | False | 0.013687 | 30.409892 | 22754 |  |
| wikimedia/wikipedia | 20231101.azb | two_stage | url_and_text_from_title | valid | True | 0.059527 | 32.340729 | 22754 |  |
| wikimedia/wikipedia | 20231101.azb | tool_loop |  | error | False |  |  | 116694 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.bg | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.bg | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 4 cell(s) |
| wikimedia/wikipedia | 20231101.bg | manual | manual_wiki_2 | valid | False | 0.001792 | 332.901466 | 0 |  |
| wikimedia/wikipedia | 20231101.bg | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 4 cell(s) |
| wikimedia/wikipedia | 20231101.bg | manual | manual_wiki_4 | valid | True | 0.004269 | 182.903600 | 0 |  |
| wikimedia/wikipedia | 20231101.bg | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.bg | single | url_from_title | valid | False | 0.006304 | 181.269992 | 9819 |  |
| wikimedia/wikipedia | 20231101.bg | single | url_and_id_from_title_row | valid | False | 0.006280 | 182.090950 | 9819 |  |
| wikimedia/wikipedia | 20231101.bg | single | url_and_text_title_prefix | valid | True | 0.007048 | 184.764092 | 9819 |  |
| wikimedia/wikipedia | 20231101.bg | single | title_from_url | valid | False | 0.004236 | 175.216329 | 9819 |  |
| wikimedia/wikipedia | 20231101.bg | two_stage | url_from_title | valid | True | 0.006299 | 183.442971 | 20093 |  |
| wikimedia/wikipedia | 20231101.bg | two_stage | title_from_url_decode | valid | False | 0.004221 | 192.040967 | 20093 |  |
| wikimedia/wikipedia | 20231101.bg | tool_loop |  | error | False |  |  | 72574 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.ady | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ady | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 4 cell(s) |
| wikimedia/wikipedia | 20231101.ady | manual | manual_wiki_2 | valid | False | 0.005654 | 1.989767 | 0 |  |
| wikimedia/wikipedia | 20231101.ady | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 4 cell(s) |
| wikimedia/wikipedia | 20231101.ady | manual | manual_wiki_4 | valid | True | 0.028505 | 1.530579 | 0 |  |
| wikimedia/wikipedia | 20231101.ady | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ady | single | url_from_title | valid | False | 0.032631 | 1.435696 | 11657 |  |
| wikimedia/wikipedia | 20231101.ady | single | title_from_url | valid | False | 0.019981 | 1.539313 | 11657 |  |
| wikimedia/wikipedia | 20231101.ady | single | url_and_leading_title_text | valid | True | 0.037440 | 1.493475 | 11657 |  |
| wikimedia/wikipedia | 20231101.ady | two_stage | url_title | valid | True | 0.035996 | 1.407621 | 21004 |  |
| wikimedia/wikipedia | 20231101.ady | two_stage | url_title_suffix | valid | False | 0.032064 | 1.465887 | 21004 |  |
| wikimedia/wikipedia | 20231101.ady | two_stage | url_host | rejected | False | -0.006064 |  | 21004 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ady | tool_loop |  | error | False |  |  | 90171 | ValueError: tool loop ended without submit_candidates |
| wikimedia/wikipedia | 20231101.ar |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.de |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| wikimedia/wikipedia | 20231101.ceb | original | original | valid | False | 0.000000 |  |  |  |
| wikimedia/wikipedia | 20231101.ceb | manual | manual_wiki_1 | invalid | False |  |  | 0 | reconstruction differs in 3 cell(s) |
| wikimedia/wikipedia | 20231101.ceb | manual | manual_wiki_2 | valid | False | 0.060690 | 10.725475 | 0 |  |
| wikimedia/wikipedia | 20231101.ceb | manual | manual_wiki_3 | invalid | False |  |  | 0 | reconstruction differs in 3 cell(s) |
| wikimedia/wikipedia | 20231101.ceb | manual | manual_wiki_4 | valid | True | 0.134264 | 8.377625 | 0 |  |
| wikimedia/wikipedia | 20231101.ceb | heuristic |  | skipped | False |  |  | 0 | no candidates were produced |
| wikimedia/wikipedia | 20231101.ceb | single | url_prefix | rejected | False | -0.015182 |  | 8963 | candidate does not reduce Snappy Parquet size |
| wikimedia/wikipedia | 20231101.ceb | single | url_from_title | valid | True | 0.151793 | 7.781671 | 8963 |  |
| wikimedia/wikipedia | 20231101.ceb | single | url_suffix_and_decoded_title | valid | False | 0.146739 | 7.820133 | 8963 |  |
| wikimedia/wikipedia | 20231101.ceb | two_stage | url_title_encode | valid | True | 0.151835 | 7.750600 | 15075 |  |
| wikimedia/wikipedia | 20231101.ceb | two_stage | url_tail_title_decode | valid | False | 0.146987 | 7.658671 | 15075 |  |
| wikimedia/wikipedia | 20231101.ceb | tool_loop | url_from_title | invalid | False |  |  | 34535 | reconstruction differs in 3 cell(s) |
| wikimedia/wikipedia | 20231101.ceb | tool_loop | title_from_url | valid | False | 0.134294 | 7.668096 | 34535 |  |
| wikimedia/wikipedia | 20231101.ceb | tool_loop | url_title_path | valid | True | 0.149031 | 7.490642 | 34535 |  |
| wikimedia/wikipedia | 20231101.nl |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| HuggingFaceFW/fineweb | sample-10BT | original | original | valid | False | 0.000000 |  |  |  |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_1 | rejected | False | -0.000097 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_2 | invalid | False |  |  | 0 | reconstruction differs in 1000 cell(s) |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_3 | rejected | False | -0.018670 |  | 0 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | manual | manual_fineweb_5 | valid | True | 0.000875 | 8.411533 | 0 |  |
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
| HuggingFaceFW/fineweb | sample-10BT | single | file_path_affix | rejected | False | -0.000964 |  | 13698 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | single | id_dump_language | rejected | False | -0.004029 |  | 13698 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | single | date_timestamp | rejected | False | -0.001389 |  | 13698 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | two_stage | filepath_affix | valid | False | 0.000173 | 8.637517 | 28250 |  |
| HuggingFaceFW/fineweb | sample-10BT | two_stage | language_en | rejected | False | -0.000569 |  | 28250 | candidate does not reduce Snappy Parquet size |
| HuggingFaceFW/fineweb | sample-10BT | two_stage | filepath_affix_language_en | valid | True | 0.000225 | 7.184325 | 28250 |  |
| HuggingFaceFW/fineweb | sample-10BT | tool_loop |  | error | False |  |  | 104736 | ValueError: tool loop ended without submit_candidates |
| Metanova/SAVI-2020 | default |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| bigdata-pw/Flickr |  |  |  | skipped | False |  |  |  | dataset is not local and the configured repository may require authentication |
| vCache/SemBenchmarkLmArena | default |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| vCache/SemBenchmarkClassification | default |  |  | skipped | False |  |  |  | dataset is not local and is outside the capped bootstrap allowlist |
| nhagar/fineweb_urls |  | original | original | valid | False | 0.000000 |  |  |  |
| nhagar/fineweb_urls |  | manual | manual_fineweb_url_1 | invalid | False |  |  | 0 | reconstruction differs in 78 cell(s) |
| nhagar/fineweb_urls |  | manual | manual_fineweb_url_3 | valid | True | 0.140474 | 1.002242 | 0 |  |
| nhagar/fineweb_urls |  | manual | manual_fineweb_url_2 | skipped | False |  |  | 0 | historical method has no lossless reconstruction SQL |
| nhagar/fineweb_urls |  | heuristic | heuristic_0_url_from_1_domain | valid | False | 0.115419 | 1.578037 | 0 |  |
| nhagar/fineweb_urls |  | heuristic | heuristic_1_domain_from_0_url | valid | True | 0.124362 | 1.186296 | 0 |  |
| nhagar/fineweb_urls |  | single | http_domain_suffix | invalid | False |  |  | 6330 | reconstruction differs in 424 cell(s) |
| nhagar/fineweb_urls |  | single | http_prefix | rejected | False | -0.043848 |  | 6330 | candidate does not reduce Snappy Parquet size |
| nhagar/fineweb_urls |  | single | domain_first_occurrence | valid | True | 0.124941 | 1.448692 | 6330 |  |
| nhagar/fineweb_urls |  | two_stage | url_host_domain_tail | valid | False | 0.090694 | 1.383025 | 9550 |  |
| nhagar/fineweb_urls |  | two_stage | domain_last_two_labels | valid | True | 0.099604 | 2.090646 | 9550 |  |
| nhagar/fineweb_urls |  | tool_loop |  | error | False |  |  | 37241 | ValueError: tool loop ended without submit_candidates |
