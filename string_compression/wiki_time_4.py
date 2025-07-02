import duckdb
from urllib.parse import unquote
import pandas as pd
import time
import json
import os
import pyarrow as pa
import pyarrow.parquet as pq

prefixs = {
    '20231101.zh-classical': "https://zh-classical.wikipedia.org/wiki/", 
    '20231101.ab': "https://ab.wikipedia.org/wiki/", 
    '20231101.af': "https://af.wikipedia.org/wiki/", 
    '20231101.azb': "https://azb.wikipedia.org/wiki/", 
    '20231101.bg': "https://bg.wikipedia.org/wiki/",
    '20231101.ady': "https://ady.wikipedia.org/wiki/",
    '20231101.bg': "https://bg.wikipedia.org/wiki/",
    '20231101.ar': "https://ar.wikipedia.org/wiki/",
    '20231101.de': "https://de.wikipedia.org/wiki/",
    '20231101.ceb': "https://ceb.wikipedia.org/wiki/",
    '20231101.nl': "https://nl.wikipedia.org/wiki/"
}

def strip_and_unquote(url, prefix):
    return unquote(url.replace(prefix, ""))

# Define UDF

dataset_id = "wikimedia/wikipedia"
configs_file = "config.json"
con = duckdb.connect()
con.create_function('strip_and_unquote', strip_and_unquote, [str, str], return_type=str)
total_time_ori = 0
total_time_compress = 0

config_dict = json.load(open(configs_file, "r"))
ori_query_title = f"""SELECT title FROM df"""

for config in config_dict[dataset_id]["configs"]:
    print(f"  Config: {config['file']}")
    config_name = config["file"]
    if config_name == "":
        config_name = dataset_id.replace("/", "_").replace("-", "_")

    compress_config = config["compress"][3]
    compress_config["query"] = {}
    compress_query_title = f"""SELECT strip_and_unquote(url, '{prefixs[config_name]}') AS title FROM df"""
    compress_config["query"]["title_ori"] = ori_query_title
    compress_config["query"]["title_com"] = compress_query_title
    compress_config["query_time"] = {}

    df = pd.read_parquet(f"datasets_parquet/{dataset_id}/{config_name}.parquet")
    con.register("df", df)
    start_time = time.time()
    result_ori = con.execute(ori_query_title).df()
    end_time = time.time()
    print(f"Time taken (original): {end_time - start_time} seconds")
    total_time_ori += end_time - start_time
    compress_config["query_time"]["title_ori"] = end_time - start_time

    df = pd.read_parquet(f"datasets_compress/{dataset_id}/{config_name}.parquet")
    con.register("df", df)
    start_time = time.time()
    result = con.execute(compress_query_title).df()
    end_time = time.time()
    print(f"Time taken (compress): {end_time - start_time} seconds")
    total_time_compress += end_time - start_time
    compress_config["query_time"]["title_com"] = end_time - start_time

    if result_ori.equals(result):
        print("Results are equal")
    else:
        print("Results are not equal")

    with open(configs_file, "w") as f:
        json.dump(config_dict, f, indent=2)


print(f"Total time taken (original): {total_time_ori} seconds")
print(f"Total time taken (compress): {total_time_compress} seconds")
con.close()
