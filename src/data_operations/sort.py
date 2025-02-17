import pandas as pd
from utils.utils import print_colorized

def sort_by(df: pd.DataFrame, columns: list[str] | str = ['device_id', 'sent_time'], order: list[str] | str = ['asc', 'asc']) -> pd.DataFrame:
  columns = columns if isinstance(columns, list) else [columns]
  order = order if isinstance(order, list) else [order]

  # Verify columns exist
  df_columns_set = set(df.columns)
  valid_columns = []
  valid_order = []

  for col, ord in zip(columns, order):
      if col in df_columns_set:
          valid_columns.append(col)
          valid_order.append(ord)
      else:
          print_colorized(f"\nColumn not found in DataFrame while Sorting: {col}\n", 'yellow')

  # Convert categorical columns to ordered if necessary
  for col in valid_columns:
      if pd.api.types.is_categorical_dtype(df[col]):
          df[col] = df[col].cat.as_ordered()

  # Sorting
  ascending = [ord == 'asc' for ord in valid_order]
  return df.sort_values(by=valid_columns, ascending=ascending)

def sort_by_id(df: pd.DataFrame):
    return sort_by(df, ['device_id'], ['asc'])

def sort_by_id_and_time(df):
    return sort_by(df, ['device_id', 'sent_time'], ['asc', 'asc'])

def sort_by_time(df):
    return sort_by(df, ['sent_time'], ['asc'])
