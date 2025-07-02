
import pandas as pd
import os
import json
from urllib.parse import quote
import pyarrow as pa
import pyarrow.parquet as pq
import argparse

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

def main():
    parser = argparse.ArgumentParser(description='Compress Fineweb URL dataset.')
    parser.add_argument('compression_method', type=int, choices=[1, 2, 3], help='Compression method to use (1, 2, or 3)')
    args = parser.parse_args()

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

        if len(config["compress"]) < args.compression_method:
            config["compress"].append({})

        compress_config = config["compress"][args.compression_method - 1]
        
        print(f"  Config: {config['file']}")
        config_name = config["file"]
        if config_name == "":
            config_name = dataset_id.replace("/", "_").replace("-", "_")
        df = get_df(config["path"])

        for compression_method in compression_methods:
            compress_df = df.copy()

            if args.compression_method == 1:
                compress_config["function"] = "domain are the infix of the url"
                compress_df = compress_df.drop(columns=['domain'])
            elif args.compression_method == 2:
                compress_config["function"] = "remove the domain in url"
                compress_df['url'] = compress_df.apply(lambda x: x['url'].replace(x['domain'], ""), axis=1)
            elif args.compression_method == 3:
                compress_config["function"] = "domain are the infix of the url, and store the domain offset and length"
                df['domain_offset'] = df.apply(lambda row: row['url'].find(row['domain']), axis=1)
                df['domain_length'] = df['domain'].apply(len)
                compress_df = compress_df.drop(columns=['domain'])

            write_parquet(compress_df, f"datasets_compress/{dataset_id}/{config_name}.parquet", PARQUET_COMPRESSION_TYPE=compression_method)
            size = config[f"size_{compression_method}"]
            compression_size = get_size(f"datasets_compress/{dataset_id}/{config_name}.parquet")
            print(f"Size of the dataset: {size / (1024):.2f} kB")
            print(f"Size of the compression: {compression_size / (1024):.2f} kB")
            print(f"Compression ratio: {((size-compression_size) / size) * 100:.2f} %")
            compress_config[f"size_compression_{compression_method}"] = compression_size
            total_size[compression_method] += size
            total_compress_size[compression_method] += compression_size
            # Decompression and verification
            # if args.compression_method == 1:
            #     # This method does not have a decompression step
            #     pass
            # elif args.compression_method == 2:
            #     # This method does not have a decompression step
            #     pass
            # elif args.compression_method == 3:
            #     # This method does not have a decompression step
            #     pass
            # compare_dataframes(df, compress_df)
            with open(configs_file, "w") as f:
                json.dump(config_dict, f, indent=2)

if __name__ == '__main__':
    main()
