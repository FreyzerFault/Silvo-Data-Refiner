import os
import pandas as pd
from src.utils import colorize
from src.file_manager import read_csv, write_csv

def group_by(df: pd.DataFrame, column: str) -> list[pd.DataFrame]:
  # Group By si no son columnas especiales (dia, mes, hora...)
  if column not in df.columns:
    print(colorize(f"The column '{column}' is not present in {df.columns}.", 'red'))
    return []
  
  return [group for _, group in df.groupby([column])]

def group_by_id(df: pd.DataFrame) -> list[pd.DataFrame]:
  return group_by(df, 'device_id')

def group_by_hour(df: pd.DataFrame) -> list[pd.DataFrame]:
  df['hour'] = df['sent_time'].dt.floor('h')
  return group_by(df, 'hour')

def group_by_day(df: pd.DataFrame) -> list[pd.DataFrame]:
  df['day'] = df['sent_time'].dt.floor('d')
  return group_by(df, 'day')

def group_by_month(df: pd.DataFrame) -> list[pd.DataFrame]:
  df['month'] = df['sent_time'].dt.to_period('M')
  return group_by(df, 'month')


def group_by_to_files(file_path: str, column: str, dir_path: str) -> list[str]:
  df = read_csv(file_path)
  
  # Si no existe la carpeta se crea
  os.makedirs(dir_path, exist_ok=True)
  
  # Función para dividir los datos
  default_group_by_func = lambda df: group_by(df, column)
  group_by_funcs = {
    'hour': lambda df: group_by_hour(df),
    'day': lambda df: group_by_day(df),
    'month': lambda df: group_by_month(df)
  }
  
  # Dividimos los datos según su función
  grouped_dfs = group_by_funcs.get(column, default_group_by_func)(df)
  
  out_file_paths = []
  
  # Cada grupo de datos se guarda en un archivo con el nombre del valor por el que se agrupa
  for split_df in grouped_dfs:
    first_value = split_df[column].iloc[0]
    file_name = f"grouped by {str(first_value).replace(':', '.')}.csv"
    
    file_path = os.path.join(dir_path, file_name)
    out_file_paths.append(file_path)
    write_csv(split_df, file_path)
  
  return out_file_paths
