import pandas as pd
from src.sort import sort_by_id_and_time, sort_by_time
from src.file_manager import read_csv, write_csv

# Merge CSV files, Sort and Save as 1 file
def merge_csv_files(in_file_paths, merged_file_path):
  merged_df = pd.concat([read_csv(file) for file in in_file_paths])
  merged_df = sort_by_id_and_time(merged_df)
  write_csv(merged_df, merged_file_path)