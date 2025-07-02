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
        

dataset_id = "Metanova/SAVI-2020"

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

    if len(config["compress"]) == 4:
        config["compress"].append({"function": "function 1 + 4"})
    compress_config = config["compress"][4]
    print(f"  Config: {config['file']}")
    config_name = config["file"]
    df = get_df(config["path"])
    for compression_method in compression_methods:
        compress_df = df.copy()
        compress_df = compress_df.drop(columns=['product_hashisy'], axis=1)
        compress_df['r1_url'] = compress_df.apply(lambda x: x['r1_url'].replace(x['r1_ident'][1:-1], ""), axis=1)
        compress_df['r2_url'] = compress_df.apply(lambda x: x['r2_url'].replace(x['r2_ident'][1:-1], ""), axis=1)
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
        compress_df['product_hashisy'] = compress_df['product_name'].apply(lambda x: x.split('_')[0] + '"')
        compress_df['r1_url'] = compress_df['r1_url'].str[:-1] + compress_df['r1_ident'].str[1:-1] + compress_df['r1_url'].str[-1]
        compress_df['r2_url'] = compress_df['r2_url'].str[:-1] + compress_df['r2_ident'].str[1:-1] + compress_df['r2_url'].str[-1]
        # compare_dataframes(df, compress_df)
        with open(configs_file, "w") as f:
            json.dump(config_dict, f, indent=2)


