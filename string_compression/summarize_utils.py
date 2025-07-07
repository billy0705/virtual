import duckdb
import time
import matplotlib.pyplot as plt
import os
import pandas as pd

def time_query(con: duckdb.DuckDBPyConnection, sql: str, print_result: bool = True) -> float:
    """
    Executes a DuckDB SQL query and measures the execution time.

    Args:
        con: The DuckDB connection object.
        sql: The SQL query string.
        print_result: If True, prints the DataFrame result of the query.

    Returns:
        The time taken to execute the query in seconds.
    """
    start = time.time()
    result = con.execute(sql).fetchdf()
    if print_result:
        print(result)
    return time.time() - start

def setup_duckdb_views(con: duckdb.DuckDBPyConnection, original_path: str, compressed_path: str):
    """
    Registers original and compressed Parquet files as DuckDB views.

    Args:
        con: The DuckDB connection object.
        original_path: Path to the original Parquet file.
        compressed_path: Path to the compressed Parquet file.
    """
    con.execute(f"CREATE OR REPLACE VIEW original AS SELECT * FROM parquet_scan('{original_path}')")
    con.execute(f"CREATE OR REPLACE VIEW virtual AS SELECT * FROM parquet_scan('{compressed_path}')")

def plot_results(original_size: int, compressed_size: int, query_times: dict, dataset_name: str):
    """
    Generates and displays a plot comparing file sizes and query times.

    Args:
        original_size: Size of the original file in bytes.
        compressed_size: Size of the compressed file in bytes.
        query_times: A dictionary containing query labels and their corresponding times.
        dataset_name: Name of the dataset for plot titles.
    """
    plt.figure(figsize=(12, 5))

    # Left: File sizes
    plt.subplot(1, 2, 1)
    plt.bar(['Original', 'Compressed'], [original_size, compressed_size])
    plt.ylabel('File Size (bytes)')
    plt.title(f'Parquet Compression Size - {dataset_name}')
    plt.grid(True)

    # Right: Query times
    labels = list(query_times.keys())
    times = list(query_times.values())
    plt.subplot(1, 2, 2)
    plt.bar(labels, times)
    plt.ylabel('Time (seconds)')
    plt.title(f'Query Time Comparison - {dataset_name}')
    plt.xticks(rotation=20, ha='right')
    plt.grid(True)

    plt.tight_layout()
    plt.show()
