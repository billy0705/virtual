import json
import os
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

def write_parquet(df, path, PARQUET_COMPRESSION_TYPE="snappy"):
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path, compression=PARQUET_COMPRESSION_TYPE)

def get_df(path, max_rows=1_000_000):
    parts = []
    total_rows = 0

    for fname in sorted(os.listdir(path)):
        df_part = pd.read_parquet(os.path.join(path, fname))
        n = len(df_part)

        if total_rows + n >= max_rows:
            # Only take what we still need to reach the cap
            df_part = df_part.iloc[: max_rows - total_rows]
            parts.append(df_part)
            break

        parts.append(df_part)
        total_rows += n

        if total_rows >= max_rows:
            break

    return pd.concat(parts, ignore_index=True)

config_name = "config.json"
config_dict = json.load(open(config_name, "r"))
for dataset_id in config_dict:
    print(f"Name: {dataset_id}")
    if dataset_id != "nhagar/fineweb_urls":
        continue
    os.makedirs(f"datasets_parquet/{dataset_id}", exist_ok=True)
    for config in config_dict[dataset_id]["configs"]:
        config_name = config["file"]
        if config_name == "":
            config_name = dataset_id.replace("/", "_").replace("-", "_")
        print(f"  Config: {config_name}")
        df = get_df(config["path"])
        print(f"  Writing {config_name} to parquet...")
        write_parquet(df, f"datasets_parquet/{dataset_id}/{config_name}.parquet")
        print(f"  Config: {config_name} done")
