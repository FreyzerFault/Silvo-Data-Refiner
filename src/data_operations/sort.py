import pandas as pd
from utils.utils import print_colorized

def sort_by(df: pd.DataFrame, columns: list[str] | str = ['device_id', 'sent_time'], order: list[str] | str = ['asc', 'asc']) -> pd.DataFrame:  
  columns = columns if isinstance(columns, list) else [columns]
  order = order if isinstance(order, list) else [order]
  
  # Search for columns out of the DataFrame to filter  
  for i, pair in enumerate(zip(columns, order)):
    if not pair[0] in df.columns:
      col_not_found = columns.pop(i)
      order.pop(i) 
      print_colorized(f"\nColumn not found in DataFrame while Sorting: {col_not_found}\n", 'yellow')
  
  return df.sort_values(by=columns, ascending=list(map(lambda o: o == 'asc', order)))

def sort_by_id(df: pd.DataFrame):  
  return sort_by(df, ['device_id'], ['asc'])

def sort_by_id_and_time(df):
  return sort_by(df, ['device_id', 'sent_time'], ['asc', 'asc'])

def sort_by_time(df):
  return sort_by(df, ['sent_time'], ['asc'])
