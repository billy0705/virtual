import duckdb
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms
import matplotlib
import os
# import pandas as pd
import numpy as np

matplotlib.rcParams.update({
  "pgf.texsystem": "pdflatex",
  'font.family': 'serif',
  'text.usetex': True,
  'pgf.rcfonts': False,
})

class TargetColumnSQL:
    """
    A class to handle SQL queries for summarizing a target column in a dataset.
    It provides methods to generate SQL queries for summarization and length operations.
    """

    def __init__(self, target_column: str, virtual_sql: str, virtual_length_trick: str = None):
        """
        Initializes the TargetColumnSQL with the target column name.

        Args:
            target_column: The column to summarize in the queries.
        """
        self.target_column = target_column
        self.target_column_sql = f"{self.target_column}"
        self.target_column_sql_length = f"LENGTH({self.target_column})"
        self.virtual_sql = f"{virtual_sql} AS {self.target_column}"
        self.virtual_sql_length = f"LENGTH({virtual_sql}) AS 'LENGTH({self.target_column})'"
        if virtual_length_trick:
            self.virtual_length_trick = f"{virtual_length_trick} AS 'LENGTH({self.target_column})'"
        else:
            self.virtual_length_trick = None



class SummarizePlotter:
    """
    A class to handle plotting of results for string compression summarization.
    It provides methods to plot file sizes and query times for original and compressed datasets.
    """

    def __init__(self, original_path: str, compressed_path: str, dataset_name: str, print_flag:bool = False):
        """
        Initializes the SummarizePlotter with paths to original and compressed datasets.

        Args:
            original_path: Path to the original dataset file.
            compressed_path: Path to the compressed dataset file.
            dataset_name: Name of the dataset for labeling plots.
        """
        self.original_path = original_path
        self.compressed_path = compressed_path
        self.original_size = os.path.getsize(original_path)
        self.compressed_size = os.path.getsize(compressed_path)
        self.con = duckdb.connect()
        self.dataset_name = dataset_name
        self.print_flag = print_flag
        self.list_of_targets_columns = []
        self.dict_of_target_columns = {}

        # Initialize the DuckDB views for the datasets
        self.register_views()
        columns = self.con.execute("PRAGMA table_info('original')").fetchdf()
        self.columns_name = columns['name'].tolist()

    def register_views(self):
        """
        Registers the original and compressed datasets as views in DuckDB.
        This allows for SQL queries to be run against these datasets.
        """
        self.con.execute(f"CREATE OR REPLACE VIEW original AS SELECT * FROM parquet_scan('{self.original_path}')")
        self.con.execute(f"CREATE OR REPLACE VIEW virtual AS SELECT * FROM parquet_scan('{self.compressed_path}')")

    def time_query(self, sql: str) -> float:
        """
        Executes a DuckDB SQL query and measures the execution time.

        Args:
            sql: The SQL query string.
            print_result: If True, prints the DataFrame result of the query.

        Returns:
            The time taken to execute the query in seconds.
        """
        if self.print_flag:
            print(f"Executing SQL: {sql}")
        start = time.time()
        result = self.con.execute(sql).fetchdf()
        if self.print_flag:
            print(result)
        return time.time() - start
    
    def add_target_column(self, target_column: str, virtual_sql: str, virtual_sql_length: str = None):
        """
        Adds a target column to the list of target columns for summarization.

        Args:
            target_column: The column to summarize in the queries.
        """
        # Check if the target column is already in the list
        if target_column in self.list_of_targets_columns:
            print(f"Target column {target_column} already exists.")
            return
        
        # Create a TargetColumnSQL instance and add it to the list
        target_sql = TargetColumnSQL(target_column, virtual_sql, virtual_sql_length)
        self.list_of_targets_columns.append(target_column)
        self.dict_of_target_columns[target_column] = target_sql

        print(f"Added target column: {target_column}")
    
    def query_rewrite(self, query: str, target_column: list[str], length_sql=False, length_trick=False) -> str:
        """
        Rewrites the SQL query to summarize the target column.

        Args:
            target_column: The column to summarize in the queries.

        Returns:
            The rewritten SQL query string.
        """
        for col in target_column:
            target_sql = self.dict_of_target_columns[col]
            if length_sql:
                if length_trick:
                    query = query.replace(f' LENGTH({col})', f' {target_sql.virtual_length_trick}')
                else:
                    query = query.replace(f' LENGTH({col})', f' {target_sql.virtual_sql_length}')
            else:
                query = query.replace(f' {col}', f' {target_sql.virtual_sql}')
        return query

    def plot_target_column(self, target_column: str):
        """
        Generates and displays a plot comparing file sizes and query times for the specified target column.

        Args:
            target_column: The column to summarize in the queries.
        """
        
        # Check if the target column is already in the list
        if target_column not in self.list_of_targets_columns:
            print(f"No target column {target_column} found. Please add it first.")
            return
        
        target_sql = self.dict_of_target_columns[target_column]

        
        # print(columns['name'].tolist())

        # Define SQL queries for summarization operations
        summarize_col_sql = f"SUMMARIZE SELECT {target_column} FROM original"
        summarize_col_sql_virtual = self.query_rewrite(
            f"SUMMARIZE SELECT {target_column} FROM virtual",
            [target_column]
        )

        # Define SQL queries for summarization length operations
        summarize_len_sql = f"SUMMARIZE SELECT LENGTH({target_column}) FROM original"
        summarize_len_sql_virtual = self.query_rewrite(
            f"SUMMARIZE SELECT LENGTH({target_column}) FROM virtual",
            [target_column],
            length_sql=True
        )
        if target_sql.virtual_length_trick is not None:
            summarize_len_sql_virtual_trick = self.query_rewrite(
                f"SUMMARIZE SELECT LENGTH({target_column}) FROM virtual",
                [target_column],
                length_sql=True,
                length_trick=True
            )

        sql_all = f"SUMMARIZE SELECT {', '.join(self.columns_name)} FROM original"
        sql_all_virtual = self.query_rewrite(
            f"SUMMARIZE SELECT {', '.join(self.columns_name)} FROM virtual",
            self.list_of_targets_columns
        )
        length_expressions = [f'LENGTH({col})' for col in self.columns_name]
        sql_all_length = f"SUMMARIZE SELECT {', '.join(length_expressions)} FROM original"
        sql_all_length_virtual = self.query_rewrite(
            f"SUMMARIZE SELECT {', '.join(length_expressions)} FROM virtual",
            self.list_of_targets_columns,
            length_sql=True
        )
        if target_sql.virtual_length_trick is not None:
            sql_all_length_trick = self.query_rewrite(
                f"SUMMARIZE SELECT {', '.join(length_expressions)} FROM virtual",
                self.list_of_targets_columns,
                length_sql=True,
                length_trick=True
            )

        # Measure query times
        t1 = self.time_query(summarize_col_sql)
        t2 = self.time_query(summarize_col_sql_virtual)
        t3 = self.time_query(summarize_len_sql)
        t4 = self.time_query(summarize_len_sql_virtual)
        if target_sql.virtual_length_trick is not None:
            t5 = self.time_query(summarize_len_sql_virtual_trick)

        print(sql_all_virtual)

        t6 = self.time_query(sql_all)
        t7 = self.time_query(sql_all_virtual)
        t8 = self.time_query(sql_all_length)
        t9 = self.time_query(sql_all_length_virtual)
        if target_sql.virtual_length_trick is not None:
            t10 = self.time_query(sql_all_length_trick)
        
        # Print query times if print_flag is set
        if self.print_flag:
            print(f"Original query time: {t1:.4f} seconds")
            print(f"Compressed query time: {t2:.4f} seconds")
            print(f"Original query time: {t3:.4f} seconds")
            print(f"Compressed query time: {t4:.4f} seconds")
            if target_sql.virtual_length_trick is not None:
                print(f"Trick query time: {t5:.4f} seconds")
        
        # Prepare query times for plotting
        query_col_times = [t1, t2, t3, t4]
        if target_sql.virtual_length_trick is not None:
            query_col_times.append(t5)

        query_all_times = [t6, t7, t8, t9]
        if target_sql.virtual_length_trick is not None:
            query_all_times.append(t10)
            
        # Plot the results
        self.plot_results(
            query_col_times,
            query_all_times,
            target_column=target_column
        )
    
    def plot_results(self, query_col_times: list, query_all_times: list, target_column: str = "Target Column"):
        """
        Generates and displays a plot comparing file sizes and query times.

        Args:
            original_size: Size of the original file in bytes.
            compressed_size: Size of the compressed file in bytes.
            query_times: A dictionary containing query labels and their corresponding times.
            dataset_name: Name of the dataset for plot titles.
        """

        original_ratio = (self.original_size / self.original_size) * 100
        compressed_ratio = (self.compressed_size / self.original_size) * 100
        times = query_col_times
        all_times = query_all_times

        # Prepare data
        original_list = [original_ratio, (times[0] / times[0]) * 100, (times[2] / times[2]) * 100,
                         (all_times[0] / all_times[0]) * 100, (all_times[2] / all_times[2]) * 100]
        compressed_list = [compressed_ratio, (times[1] / times[0]) * 100, (times[3] / times[2]) * 100,
                           (all_times[1] / all_times[0]) * 100, (all_times[3] / all_times[2]) * 100]
        if len(times) == 5:
            trick_list = [0, 0, (times[4] / times[2]) * 100, 0, (all_times[4] / all_times[2]) * 100]

        y_max = max(120, max(compressed_list[1:]) * 1.1)

        x_labels = [
            r'$\texttt{File Size}$',
            rf'$\texttt{{SUMMARIZE\ {target_column}}}$',
            rf'$\texttt{{SUMMARIZE\ LENGTH({target_column})}}$',
            rf'$\texttt{{SUMMARIZE\ *}}$',
            rf'$\texttt{{SUMMARIZE\ LENGTH(*)}}$'
        ]
        bar_width = 0.25

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 5))

        # Plot 1: File size
        ax1.bar(0 - bar_width/2, original_ratio, bar_width, color='blue', label=r'$\texttt{parquet}$')
        ax1.bar(0 + bar_width/2, compressed_ratio, bar_width, color='orange', label=r'$\texttt{virtual}$')
        ax1.set_xticks([0])
        ax1.set_xticklabels([x_labels[0]])
        ax1.set_ylabel(r'File Size [\%]')
        ax1.grid(True)
        ax1.legend(loc='upper left')

        # Plot 2: Query latency
        x_query = np.arange(1, 3)  # index 1 and 2
        if len(times) == 5:
            x_1 = [x_query[0] - bar_width/2, x_query[-1] - bar_width]
            x_2 = [x_query[0] + bar_width/2, x_query[-1]]
            x_3 = [0, 0, x_query[-1] + bar_width]
        else:
            x_1 = x_query - bar_width/2
            x_2 = x_query + bar_width/2

        ax2.bar(x_1, original_list[1:3], bar_width, color='blue', label=r'$\texttt{parquet}$')
        ax2.bar(x_2, compressed_list[1:3], bar_width, color='orange', label=r'$\texttt{virtual}$')
        if len(times) == 5:
            ax2.bar(x_3[2], trick_list[2], bar_width, color='yellow', label=r'fast $\texttt{virtual}$')

        ax2.set_xticks(x_query)
        ax2.set_xticklabels(x_labels[1:3])
        ax2.set_ylabel(r'Query Latency [\%]')
        ax2.set_ylim(0, y_max)
        ax2.grid(True)
        ax2.legend(loc='upper left')

        print(trick_list)

        # Plot 3: Query latency for all columns
        x_all = np.arange(1, 3)  # index 0 and 1
        ax3.bar(x_1, original_list[3:], bar_width, color='blue', label=r'$\texttt{parquet}$')
        ax3.bar(x_2, compressed_list[3:], bar_width, color='orange', label=r'$\texttt{virtual}$')
        if len(all_times) == 5:
            print(trick_list)
            ax3.bar(x_3[2], trick_list[4], bar_width, color='yellow', label=r'fast $\texttt{virtual}$')
        ax3.set_xticks(x_all)
        ax3.set_xticklabels(x_labels[3:])
        ax3.set_ylabel(r'Query Latency [\%]')
        ax3.set_ylim(0, y_max)
        ax3.grid(True)
        ax3.legend(loc='upper left')

        fig.suptitle(rf'{self.dataset_name.lower()} - column $\texttt{{{target_column}}}$')

        plt.tight_layout()
        plt.show()

