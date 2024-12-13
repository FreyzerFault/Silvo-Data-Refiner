import os
import pandas as pd
import argparse

from src.file_manager import get_files, print_files
from src.utils import colorize

from src.refactor import refactor_data_file
from src.merge import merge_csv_files
from src.group_by import group_by_to_files

# TODO: Crear archivos .spp para Unity

# ======================== CONFIG ========================

# -t o --test to run the script in test mode
argparser = argparse.ArgumentParser(description='Clean and split collar data')
argparser.add_argument('-t', '--test', action='store_true', help='Run the script in test mode')

test_mode = argparser.parse_args().test

doRefactor = True
doMerge = True
doSplit = True

# Filtros para separar los datos en distintos archivos
# (por cuestiones de memoria ya que en total son miles de registros)
group_by_columns = [
  'msg_type', 
  'device_id', 
  'hour', 
  'day', 
  'month'
]

# PATHS:
in_data_root = './data/in' if not test_mode else './data/test/in/'
out_data_root = './data/out' if not test_mode else './data/test/out/'
merged_file_path = os.path.join(out_data_root, f'merged/merged_data.csv')

os.makedirs(in_data_root, exist_ok=True)
os.makedirs(out_data_root, exist_ok=True)
os.makedirs(os.path.dirname(merged_file_path), exist_ok=True)

# ======================================================

def main():
  if test_mode:
    print(f'Running in test mode')
    print()
  
  # Process Files
  if doRefactor:
    refactor()

  # Merge Files
  if doMerge:
    merge()

  # Split Files
  if doSplit:
    group_by()


def refactor():
  in_files = get_files(in_data_root)
  print(colorize(f"Refactoring files from {in_data_root}:", 'blue'))
  print_files([os.path.basename(file) for file in in_files])
  print()
  
  out_files = []
  
  for file_path in in_files:
    fixed_path = refactor_data_file(file_path, out_data_root)
    out_files.append(os.path.basename(fixed_path))
  
  print(colorize(f"Refactored data saved in {os.path.basename(out_data_root)}", 'green'))
  print_files(out_files)
  print()


def merge():
  # Input: Files in out except merged
  in_files = get_files(out_data_root)
  
  if merged_file_path in in_files:
    in_files.remove(merged_file_path)
  
  if len(in_files) == 0:
    print(colorize('No files to merge', 'yellow'))
    return
  
  print(colorize(f"Merging files from {out_data_root}:", 'blue'))
  print_files([os.path.basename(file) for file in in_files])
  print()
  
  merge_csv_files(in_files, merged_file_path)
  
  print(colorize(f"Merged data saved in {merged_file_path}", 'green'))
  print_files([os.path.basename(merged_file_path)])
  print()

def group_by():
  print(colorize(f"Splitting file {merged_file_path} by:", 'blue'))
  print(colorize(f"\t{str.join(', ', group_by_columns)}", 'blue'))
  print()
  
  for group_by_column in group_by_columns:
    
    # Carpeta donde se guardaran los archivos
    dir_name = f'group by {group_by_column}'
    dir_path = os.path.join(out_data_root, dir_name)
    
    grouped_file_paths = group_by_to_files(merged_file_path, group_by_column, dir_path)
    grouped_file_names = [os.path.basename(file) for file in grouped_file_paths]
    
    print(colorize(f"Saved in {dir_path}:", 'green'))
    print_files(grouped_file_names)
  print()
  
