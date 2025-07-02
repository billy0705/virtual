import pandas as pd
import os
import json
from urllib.parse import quote
import pyarrow as pa
import pyarrow.parquet as pq

def write_parquet(df, path, PARQUET_COMPRESSION_TYPE="zstd"):
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path, compression=PARQUET_COMPRESSION_TYPE)


def compare_dataframes(df1, df2):
    # Align columns by name
    df1_sorted = df1.sort_index(axis=1)
    df2_sorted = df2[df1_sorted.columns]  # reorder df2 to match df1

    # Check shape first
    if df1_sorted.shape != df2_sorted.shape:
        print("DataFrames have different shapes:", df1_sorted.shape, df2_sorted.shape)
        return

    # Create a boolean DataFrame of element-wise comparisons
    diff = df1_sorted != df2_sorted

    if not diff.any().any():
        print("DataFrames are equal")
    else:
        print("Differences found at these locations:")
        differing_cells = diff.stack()[diff.stack()]  # True where differences exist
        for (idx, col) in differing_cells.index:
            print(f"- Row {idx}, Column '{col}': df1 = {df1_sorted.at[idx, col]!r}, df2 = {df2_sorted.at[idx, col]!r}")

def get_size(start_path = '.'):
    # check is it a file or directory
    if os.path.isfile(start_path):
        return os.path.getsize(start_path)
    total = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

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
        

dataset_id = "nhagar/fineweb_urls"

os.makedirs(f"datasets_compress/{dataset_id}", exist_ok=True)
configs_file = "config.json"
compression_methods = ["snappy", "gzip", "brotli", "lz4", "zstd"]
config_dict = json.load(open(configs_file, "r"))

total_size = {
    "snappy": 0,
    "gzip": 0,
    "brotli": 0,
    "lz4": 0,
    "zstd": 0
}
total_compress_size = {
    "snappy": 0,
    "gzip": 0,
    "brotli": 0,
    "lz4": 0,
    "zstd": 0
}

for config in config_dict[dataset_id]["configs"]:
    if "compress" not in config:
        config["compress"] = []

    if len(config["compress"]) == 0:
        config["compress"].append({"function": "domain are the infix of the url"})
    compress_config = config["compress"][0]
    print(f"  Config: {config['file']}")
    config_name = config["file"]
    if config_name == "":
        config_name = dataset_id.replace("/", "_").replace("-", "_")
    df = get_df(config["path"])
    for compression_method in compression_methods:
        compress_df = df.copy()
        compress_df = compress_df.drop(columns=['domain'])
        write_parquet(compress_df, f"datasets_compress/{dataset_id}/{config_name}.parquet", PARQUET_COMPRESSION_TYPE=compression_method)
        compress_df = pd.read_parquet(f"datasets_compress/{dataset_id}/{config_name}.parquet")
        size = config[f"size_{compression_method}"]
        compression_size = get_size(f"datasets_compress/{dataset_id}/{config_name}.parquet")
        compression_size = get_size(f"datasets_compress/{dataset_id}/{config_name}.parquet")
        print(f"Size of the dataset: {size / (1024):.2f} kB")
        print(f"Size of the compression: {compression_size / (1024):.2f} kB")
        print(f"Compression ratio: {((size-compression_size) / size) * 100:.2f} %")
        compress_config[f"size_compression_{compression_method}"] = compression_size
        total_size[compression_method] += size
        total_compress_size[compression_method] += compression_size
        # for url_col in url_cols:
        #     compress_df[f"{url_col}"] = compress_df.apply(lambda x: x['url_temp'].replace("_{}", url_suffix_dict[url_col]) if x[f"{url_col}_null"] else None, axis=1)
        #     compress_df = compress_df.drop(columns=[f"{url_col}_null"])
        # compress_df = compress_df.drop(columns=['url_temp'])
        # compare_dataframes(df, compress_df)
        with open(configs_file, "w") as f:
            json.dump(config_dict, f, indent=2)


