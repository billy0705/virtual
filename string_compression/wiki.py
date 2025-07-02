
import pandas as pd
import os
import json
from urllib.parse import quote, unquote
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
    parser = argparse.ArgumentParser(description='Compress Wikipedia dataset.')
    parser.add_argument('compression_method', type=int, choices=[1, 2, 3, 4], help='Compression method to use (1, 2, 3, or 4)')
    args = parser.parse_args()

    os.makedirs("datasets_compress/wikimedia/wikipedia", exist_ok=True)

    dataset_id = "wikimedia/wikipedia"
    configs_file = "config.json"
    compression_methods = ["snappy", "gzip", "brotli", "lz4", "zstd"]
    config_dict = json.load(open(configs_file, "r"))
    prefixs = {
        '20231101.zh-classical': "https://zh-classical.wikipedia.org/wiki/", 
        '20231101.ab': "https://ab.wikipedia.org/wiki/", 
        '20231101.af': "https://af.wikipedia.org/wiki/", 
        '20231101.azb': "https://azb.wikipedia.org/wiki/", 
        '20231101.bg': "https://bg.wikipedia.org/wiki/",
        '20231101.ady': "https://ady.wikipedia.org/wiki/",
        '20231101.ar': "https://ar.wikipedia.org/wiki/",
        '20231101.de': "https://de.wikipedia.org/wiki/",
        '20231101.ceb': "https://ceb.wikipedia.org/wiki/",
        '20231101.nl': "https://nl.wikipedia.org/wiki/"
    }

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
        df = get_df(f"datasets/{dataset_id}/{config_name}/")

        for compression_method in compression_methods:
            compress_df = df.copy()

            if args.compression_method == 1:
                compress_config["function"] = "url=offset+transfer(title)"
                compress_df = df.drop(columns=["url"])
            elif args.compression_method == 2:
                compress_config["function"] = "title=combine[:len], text=combine[len:]"
                compress_df["combine_title_text"] = compress_df["title"] + compress_df["text"]
                compress_df["title_len"] = compress_df["title"].str.len()
                compress_df = compress_df.drop(columns=["title", "text"])
            elif args.compression_method == 3:
                compress_config["function"] = "url=offset+transfer(title), title=combine[:len], text=combine[len:]"
                compress_df = df.drop(columns=["url"])
                compress_df["combine_title_text"] = compress_df["title"] + compress_df["text"]
                compress_df["title_len"] = compress_df["title"].str.len()
                compress_df = compress_df.drop(columns=["title", "text"])
            elif args.compression_method == 4:
                compress_config["function"] = "title=transfer(url-prefix)"
                compress_df = df.drop(columns=["title"])

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
            #     compress_df["url"] = compress_df["title"].apply(lambda x: prefixs[config_name] + quote(x))
            # elif args.compression_method == 2:
            #     compress_df["title"] = compress_df.apply(lambda r: r["combine_title_text"][: r["title_len"]], axis=1, result_type="reduce")
            #     compress_df["text"] = compress_df.apply(lambda r: r["combine_title_text"][r["title_len"] :], axis=1, result_type="reduce")
            #     compress_df = compress_df.drop(columns=["combine_title_text", "title_len"])
            # elif args.compression_method == 3:
            #     compress_df["title"] = compress_df.apply(lambda r: r["combine_title_text"][: r["title_len"]], axis=1, result_type="reduce")
            #     compress_df["text"] = compress_df.apply(lambda r: r["combine_title_text"][r["title_len"] :], axis=1, result_type="reduce")
            #     compress_df["url"] = compress_df["title"].apply(lambda x: prefixs[config_name] + quote(x))
            #     compress_df = compress_df.drop(columns=["combine_title_text", "title_len"])
            # elif args.compression_method == 4:
            #     prefix = prefixs[config_name]
            #     compress_df["title"] = compress_df["url"].apply(lambda x: unquote(x.replace(prefix, "")))

            # compare_dataframes(df, compress_df)
            with open(configs_file, "w") as f:
                json.dump(config_dict, f, indent=2)

if __name__ == '__main__':
    main()
