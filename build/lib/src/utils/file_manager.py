import os
import pandas as pd
from utils.utils import colorize, str_to_time


def get_files_by_extension(dir_path: str, extension = '.csv') -> list[str]:
  return [file for file in os.listdir(dir_path) 
          if file.endswith(extension) and os.path.isfile(os.path.join(dir_path, file))]

def print_files(files: list[str], max_files = 5):
  print(colorize(f"\t- {str.join('\n\t- ', files)}", 'cyan'))
  if len(files) > max_files:
    print(f"\t... ({len(files) - max_files} more)")

def ensure_dir_exists(paths: list[str] | str):
  
  if isinstance(paths, str):
    paths = [paths]
  
  for path in paths:
    # If it's a file, get the directory
    if os.path.isfile(path):
      path = os.path.dirname(path)
    os.makedirs(path, exist_ok=True)


#region======================== CSV ========================

date_format = '%d/%m/%Y %H:%M:%S'

def read_csv(file_path) -> pd.DataFrame:
  try:
    df = pd.read_csv(file_path, sep=None, engine='python', parse_dates=True)
    for column in df.columns:
      if 'time' in column and df.dtypes[column] == 'object':
        df[column] = df[column].apply(str_to_time)
    return df
  except Exception as e:
    print(colorize(f"An error occurred while reading the file: {e}", 'red'))
    return None


def write_csv(df: pd.DataFrame, file_path, separator = ','):
  # Save the cleaned data to a new file
  # Ensure datetime columns are formatted correctly in out_format
  df.to_csv(file_path, sep = separator, index=False, date_format=date_format)

#endregion =================================================