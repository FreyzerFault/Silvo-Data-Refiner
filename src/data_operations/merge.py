import pandas as pd
from utils.file_manager import read_csv, write_csv

def merge(dfs: list[pd.DataFrame]) -> pd.DataFrame:
  return pd.concat(dfs)

# Merge CSV files, Sort and Save as 1 file
def merge_csv_files(in_file_paths, merged_file_path) -> pd.DataFrame:
  merged_df = merge([read_csv(file) for file in in_file_paths])
  write_csv(merged_df, merged_file_path)
  return merged_df