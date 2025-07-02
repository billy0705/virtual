import duckdb
from urllib.parse import quote
import pandas as pd
import time
import json
import os
import pyarrow as pa
import pyarrow.parquet as pq



dataset_id = "nhagar/fineweb_urls"
configs_file = "config.json"
con = duckdb.connect()
# con.create_function('quote', myquote, [str], return_type=str)
total_time_ori = 0
total_time_compress = 0

config_dict = json.load(open(configs_file, "r"))
ori_query = f"""SELECT domain FROM df"""
compress_query = f"""SELECT substr(url, domain_offset + 1, domain_length) AS domain FROM df"""

for config in config_dict[dataset_id]["configs"]:
    print(f"  Config: {config['file']}")
    config_name = config["file"]
    if config_name == "":
        config_name = dataset_id.replace("/", "_").replace("-", "_")

    compress_config = config["compress"][2]
    compress_config["query"] = {}
    
    compress_config["query"]["url_ori"] = ori_query
    compress_config["query"]["url_com"] = compress_query
    compress_config["query_time"] = {}

    df = pd.read_parquet(f"datasets_parquet/{dataset_id}/{config_name}.parquet")
    con.register("df", df)
    start_time = time.time()
    result_ori = con.execute(ori_query).df()
    print(f"Original result: {result_ori.head()}")
    end_time = time.time()
    print(f"Time taken (original): {end_time - start_time} seconds")
    total_time_ori += end_time - start_time
    compress_config["query_time"]["url_ori"] = end_time - start_time

    df = pd.read_parquet(f"datasets_compress/{dataset_id}/{config_name}.parquet")
    con.register("df", df)
    start_time = time.time()
    result = con.execute(compress_query).df()
    print(f"Compressed result: {result.head()}")
    end_time = time.time()
    print(f"Time taken (compress): {end_time - start_time} seconds")
    total_time_compress += end_time - start_time
    compress_config["query_time"]["url_com"] = end_time - start_time

    if result_ori.equals(result):
        print("Results are equal")
    else:
        # compare the two DataFrames
        diff = result_ori.compare(result)
        print("Differences found:")
        print(diff)
        # 
        print("Results are not equal")

    with open(configs_file, "w") as f:
        json.dump(config_dict, f, indent=2)


print(f"Total time taken (original): {total_time_ori} seconds")
print(f"Total time taken (compress): {total_time_compress} seconds")
con.close()
