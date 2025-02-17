import os, sys
import pandas as pd
from tqdm import tqdm

from utils.file_manager import get_files_by_extension, get_file_paths_by_extension, print_files, read_csv, write_csv
from utils.utils import print_colorized
from utils.config import Config

from data_operations.refactor import refactor, add_end_date, show_unknown_enum_found, delete_null_rows
from data_operations.merge import merge_csv_files, merge
from data_operations.group_by import group_by_to_files, Grouper
from data_operations.sort import sort_by

# ======================== CONFIG ========================

args = Config.parse_args()

settings_file = 'settings.yaml'
settings = Config.config_file(settings_file)

# PATHS:
paths = settings['paths']
in_data_root = paths['raw_data'] if not Config.test_mode else paths['test_raw_data']
out_data_root = paths['processed_data'] if not Config.test_mode else paths['test_processed_data']
merged_file_path = os.path.join(out_data_root, paths['merged_data_subpath'])

os.makedirs(in_data_root, exist_ok=True)
os.makedirs(out_data_root, exist_ok=True)
os.makedirs(os.path.dirname(merged_file_path), exist_ok=True)

print_colorized(f"Using {in_data_root} as input data root", 'blue')

# Pipeline Flags:
pipeline = settings['pipeline']
active_transf = pipeline['active_transformations']

# Filtros para separar los datos en distintos archivos
# (por cuestiones de memoria ya que en total son miles de registros)
group_by_columns = pipeline['group_by']

# Ordenar todos los datos por las columnas especificadas
sort_by_columns = [by['column']for by in pipeline['sort_by']]
sort_by_orders = [by['order']for by in pipeline['sort_by']]

# ======================================================


#region ========================= MAIN =========================

def main():
  if Config.test_mode:
    print()
    print_colorized('==================== Running in test mode ====================', 'blue')
    print()
  
  in_file_paths = get_file_paths_by_extension(in_data_root)
  dfs = []
  
  print_files([os.path.basename(file) for file in in_file_paths])
  print()
  
  # Read and clean/refactor each file
  for i in tqdm(range(len(in_file_paths)), desc='Refactoring and preparing data', unit='file', colour='cyan'):
    
    in_file_path = in_file_paths[i]
    
    df = read_csv(in_file_path)
    if df is None:
      continue
    
    df = refactor(df)
    delete_null_rows(df, 'sent_time', 'lat', 'lon')
    df = sort_by(df, sort_by_columns, sort_by_orders)
    df = add_end_date(df)
    
    # Check UNKNOWN MSG TYPEs => Print unknown values to fix it later
    show_unknown_enum_found()
    
    dfs.append(df)
  
  print()  
  print_colorized(f"Merging {len(dfs)} files into 1...", 'cyan')
  
  # Merge all files
  df = merge(dfs)
  df = sort_by(df, sort_by_columns, sort_by_orders)
  df = add_end_date(df)
  
  print_colorized(f"\nMerged {len(dfs)} files into 1:\t{merged_file_path}\n", 'green')
    
  groups = group_by(df)

  print_colorized(f"{len(groups)} Group By hechos:\n\t{', '.join(f"{key}: {len(group)} datasets" for key, group in groups.items())}", 'green')
  
  
  # TODO Filter Null Positions


#endregion ======================================================


#region ========================= UNIT OPERATIONS =========================

def sort(df: pd.DataFrame) -> dict[str, list[pd.DataFrame]]:
  return sort_by(df, sort_by_columns)


def group_by(df: pd.DataFrame) -> dict[str, list[pd.DataFrame]]:
  grouped_results = group_by_to_files(df, group_by_columns, out_data_root)
  
  for column, result in grouped_results.items():
    print()
    print_colorized(f"Group by {column} (saved to {result['dir_path']}):", 'blue')
    print_files(result['files'])
    print()
  
  return {col: group['dfs'] for col, group in grouped_results.items()}

#region ============= Stand Alone Functions for testing =============

def refactor_only():
  in_files = get_files_by_extension(in_data_root)
  
  print()
  print_colorized(f"Refactoring files from {in_data_root}:", 'blue')
  print_files([os.path.basename(file) for file in in_files])
  print()
  
  for file in in_files:
    df = read_csv(os.path.join(in_data_root, file))
    df = refactor(df)
    write_csv(df, os.path.join(out_data_root, file))
  
  print_colorized(f"Refactored data saved in {out_data_root}", 'green')
  print_files(in_files)
  print()


def merge_only():
  # Input: out files
  in_files = get_files_by_extension(out_data_root)
  in_file_paths = [os.path.join(out_data_root, file) for file in in_files]
    
  if len(in_files) == 0:
    print_colorized('No files to merge', 'yellow')
    return
  
  print_colorized(f"Merging files from {out_data_root}:", 'blue')
  print_files(in_files)
  print()
  
  merge_csv_files(in_file_paths, merged_file_path)
  
  print_colorized(f"Merged data saved in {merged_file_path}", 'green')
  print_files([os.path.basename(merged_file_path)])
  print()


def sort_only():
  # Input: merged file
  file_path = merged_file_path
    
  if not os.path.exists(file_path):
    print_colorized(f'File not found to sort: {file_path}', 'yellow')
    return
  
  print_colorized(f"Sorting file {merged_file_path}", 'blue')
  print()
  
  df = read_csv(file_path)
  df = sort(df)
  write_csv(df, file_path)
  
  print_colorized(f"Sorted data saved in file {merged_file_path}", 'green')
  print()


def group_by_only():
  if not os.path.exists(merged_file_path):
    print_colorized('No merged file to split', 'yellow')
    return
  
  print_colorized(f"Splitting file {merged_file_path} by:", 'blue')
  df = read_csv(merged_file_path)
  
  group_by(df)

#endregion ======================================================

#endregion ======================================================


if __name__ == '__main__':
  main()
