
"""
This script automates the process of downloading datasets from the Hugging Face Hub,
processing them to calculate their size under various compression algorithms, and
updating a central JSON configuration file with the results.

The script performs the following main steps:
1.  Reads a `config.json` file that defines which datasets to process and their
    current status.
2.  For each dataset marked as "not yet started":
    - Downloads the specified dataset files from Hugging Face Hub.
    - Updates its status to "downloaded".
3.  For each dataset marked as "downloaded":
    - Calculates the total original size of the dataset files.
    - Reads the dataset into a Pandas DataFrame (up to a 1M row limit).
    - Calculates the size of the DataFrame when saved as a Parquet file using
      different compression methods (snappy, gzip, brotli, lz4, zstd).
    - Records the row count and all calculated sizes in the config.
    - Updates its status to "processed".
4.  Cleans up temporary cache files and directories.
5.  Saves the updated configuration back to `config.json`.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import snapshot_download, list_repo_files

# --- Constants ---
CONFIG_FILE = "config.json"
TEMP_PARQUET_FILE = "tmp.parquet"
COMPRESSION_METHODS = ["snappy", "gzip", "brotli", "lz4", "zstd"]
STATUS_PENDING = "not yet started"
STATUS_DOWNLOADED = "downloaded"
STATUS_PROCESSED = "processed"


def write_parquet(df: pd.DataFrame, path: str, compression: str = "snappy"):
    """
    Writes a Pandas DataFrame to a Parquet file with specified compression.

    Args:
        df: The DataFrame to write.
        path: The output file path.
        compression: The compression codec to use (e.g., "snappy", "gzip").
    """
    table = pa.Table.from_pandas(df)
    pq.write_table(table, path, compression=compression)


def get_df_from_parquet_directory(path: str, max_rows: int = 1_000_000) -> pd.DataFrame:
    """
    Reads multiple Parquet files from a directory into a single DataFrame.

    Stops reading once max_rows is reached.

    Args:
        path: The directory containing the Parquet files.
        max_rows: The maximum number of rows to load.

    Returns:
        A concatenated Pandas DataFrame.
    """
    parts = []
    total_rows = 0

    if not os.path.isdir(path):
        print(f"Error: Path is not a directory: {path}")
        return pd.DataFrame()

    for fname in sorted(os.listdir(path)):
        if not fname.endswith(('.parquet', '.parq')):
            continue

        file_path = os.path.join(path, fname)
        try:
            df_part = pd.read_parquet(file_path)
            n = len(df_part)

            if total_rows + n >= max_rows:
                # Only take what we still need to reach the cap
                rows_to_take = max_rows - total_rows
                df_part = df_part.iloc[:rows_to_take]
                parts.append(df_part)
                break

            parts.append(df_part)
            total_rows += n
        except Exception as e:
            print(f"Warning: Could not read {file_path}. Error: {e}")
            continue

    if not parts:
        return pd.DataFrame()

    return pd.concat(parts, ignore_index=True)


def download_dataset(dataset_id: str, config_file: str):
    """
    Downloads a dataset from the Hugging Face Hub based on predefined configurations.

    Args:
        dataset_id: The Hugging Face repository ID of the dataset.
        config_file: The specific configuration file/pattern for the dataset.
    """
    # This dictionary maps dataset IDs to their specific download parameters.
    # This approach is more scalable and readable than a long if-elif chain.
    DATASET_DOWNLOAD_CONFIG: Dict[str, Dict[str, Any]] = {
        "HuggingFaceFW/fineweb": {
            "pattern_template": "{split_0}/{split_1}/*",
            "revision": None
        },
        "wikimedia/wikipedia": {
            "pattern_template": "{config}/*",
            "revision": None
        },
        "Metanova/SAVI-2020": {
            "pattern_template": "{config}/*",
            "revision": "refs/convert/parquet"
        },
        "bigdata-pw/Flickr": {
            "get_pattern": lambda: list_repo_files("bigdata-pw/Flickr", repo_type="dataset")[2:22],
            "revision": None
        },
        "vCache/SemBenchmarkLmArena": {
            "pattern_template": "{config}/*",
            "revision": "refs/convert/parquet"
        },
        "vCache/SemBenchmarkClassification": {
            "pattern_template": "{config}/*",
            "revision": "refs/convert/parquet"
        },
        "nhagar/fineweb_urls": {
            "get_pattern": lambda: list_repo_files("nhagar/fineweb_urls", repo_type="dataset")[2:12],
            "revision": None
        }
    }

    if dataset_id not in DATASET_DOWNLOAD_CONFIG:
        print(f"Error: Unknown dataset_id '{dataset_id}'. No download configuration found.")
        return

    config = DATASET_DOWNLOAD_CONFIG[dataset_id]
    pattern = None

    if "pattern_template" in config:
        template = config["pattern_template"]
        if "{config}" in template:
            pattern = [template.format(config=config_file)]
        elif "{split_0}" in template:
            parts = config_file.split('-')
            pattern = [template.format(split_0=parts[0], split_1=parts[1])]
    elif "get_pattern" in config:
        pattern = config["get_pattern"]()

    if pattern is None:
        print(f"Error: Could not determine download pattern for {dataset_id} with config {config_file}")
        return

    print(f"  Downloading {dataset_id} with pattern: {pattern}")

    # Common snapshot_download arguments
    download_args = {
        "repo_id": dataset_id,
        "repo_type": "dataset",
        "local_dir": f"./datasets/{dataset_id}",
        "cache_dir": "./datasets/.cache",
        "allow_patterns": pattern
    }

    # Add revision only if it exists
    if config.get("revision"):
        download_args["revision"] = config["revision"]

    snapshot_download(**download_args)


def get_total_size(path: str) -> int:
    """
    Calculates the total size of a file or a directory and its contents.

    Args:
        path: The path to the file or directory.

    Returns:
        The total size in bytes.
    """
    if os.path.isfile(path):
        return os.path.getsize(path)

    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Ensure the path is a file and not a broken symlink
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size


def main():
    """
    Main execution function.

    - Reads dataset configurations from `config.json`.
    - Downloads datasets if they are marked as "not yet started".
    - Processes downloaded datasets to calculate original and compressed sizes.
    - Updates the configuration file with the results and status changes.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{CONFIG_FILE}'.")
        return

    # --- Process each dataset defined in the config ---
    for dataset_id, details in config_data.items():
        print(f"Processing Dataset: {dataset_id}")
        for dataset_config in details.get("configs", []):
            config_file = dataset_config.get("file")
            status = dataset_config.get("status")
            print(f"  Config: {config_file}, Status: {status}")

            # Step 1: Download dataset if not already downloaded
            if status == STATUS_PENDING:
                download_dataset(dataset_id, config_file)
                dataset_config["status"] = STATUS_DOWNLOADED
                dataset_config["download_datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                dataset_config["path"] = f"./datasets/{dataset_id}/{config_file}"
                print(f"    -> Status changed to: {STATUS_DOWNLOADED}")

            # Step 2: Calculate sizes if downloaded but not processed
            if dataset_config.get("status") == STATUS_DOWNLOADED:
                dataset_path = dataset_config.get("path")
                if not dataset_path or not os.path.exists(dataset_path):
                    print(f"    Warning: Path '{dataset_path}' not found. Skipping size calculation.")
                    continue

                print("    Calculating file sizes...")
                # Calculate original size
                original_size = get_total_size(dataset_path)
                dataset_config["size_original"] = original_size
                print(f"      Original size: {original_size} bytes")

                # Read dataframe to get row count and calculate compressed sizes
                df = get_df_from_parquet_directory(dataset_path)
                if df.empty:
                    print(f"    Warning: No data loaded from {dataset_path}. Skipping compression tests.")
                    dataset_config["status"] = "processing_failed"
                    continue

                dataset_config["rows"] = len(df)

                # Calculate size for each compression method
                for method in COMPRESSION_METHODS:
                    size_key = f"size_{method}"
                    write_parquet(df, TEMP_PARQUET_FILE, compression=method)
                    compressed_size = get_total_size(TEMP_PARQUET_FILE)
                    dataset_config[size_key] = compressed_size
                    print(f"      Size with '{method}' compression: {compressed_size} bytes")

                dataset_config["status"] = STATUS_PROCESSED
                print(f"    -> Status changed to: {STATUS_PROCESSED}")

            # Clean up cache for the specific dataset repo to save space
            repo_cache_path = f"./datasets/{dataset_id}/.cache"
            if os.path.isdir(repo_cache_path):
                print(f"  Cleaning up cache for {dataset_id}...")
                shutil.rmtree(repo_cache_path)

    # --- Final Cleanup ---
    # Remove the global cache directory
    global_cache_path = "./datasets/.cache"
    if os.path.isdir(global_cache_path):
        print("Cleaning up global dataset cache...")
        shutil.rmtree(global_cache_path)

    # Remove the temporary parquet file
    if os.path.exists(TEMP_PARQUET_FILE):
        print("Removing temporary parquet file...")
        os.remove(TEMP_PARQUET_FILE)

    # --- Save Updated Configuration ---
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=2)
    print(f"\nProcessing complete. Configuration saved to '{CONFIG_FILE}'.")


if __name__ == "__main__":
    main()
