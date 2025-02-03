import pandas as pd

def sort_by(df: pd.DataFrame, columns: list[(str, str)] | str = [('device_id', 'asc'), ('sent_time', 'asc')]) -> pd.DataFrame:  
  df = df.sort_values(by=columns if isinstance(columns, list) else [columns])
  return df

def sort_by_id(df: pd.DataFrame):  
  return sort_by(df, ['device_id'])

def sort_by_id_and_time(df):
  return sort_by(df, ['device_id', 'sent_time'])

def sort_by_time(df):
  return sort_by(df, ['sent_time'])