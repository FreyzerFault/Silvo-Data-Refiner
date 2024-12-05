import os
import pandas as pd
from src.file_manager import read_csv, write_csv
from src.utils import colorize, str_to_time
from src.sort import sort_by

# ======================== CHECK COLUMNS ========================
required_columns = ['device_id', 'time', 'msg_type', 'position_time', 'lat', 'lon']

def check_required_columns(df):
  for column in required_columns:
    if not column in df.columns:
      print(colorize(f"The required column '{column}' is not present in the file.", 'red'))
      return False
  return True

# ======================================================


# ====================== MSG TYPES ======================

msg_types_identifiers = {
  'seq_msg':    ['seq'],
  'poll_msg':   ['poll'],
  'warn_msg':   ['warn'],
  'zap_msg':    ['zap', 'pulse'],
  'status_msg': ['status'],
}

unknown_msg = 'unknown'
unknown_messages_found = []

def fix_msg_type(value):
  for enum_value, identifiers in msg_types_identifiers.items():
    for identifier in identifiers:
      if identifier in value:
        return enum_value
  
  unknown_messages_found.append(value)
  return unknown_msg

# ======================================================


# ======================== TIME ========================


cached_time_formats = {}

def fix_time_format(value: str | pd.Timestamp) -> pd.Timestamp | None:
  if type(value) == pd.Timestamp:
    return value
  
  # Cached values
  if value in cached_time_formats:
    return cached_time_formats[value]
  
  time = str_to_time(value)
  cached_time_formats[value] = time
  return time

# ======================================================


# ======================== LAT LON ========================

def fix_lat(value):
  return fix_lat_lon_format(value, 2)

def fix_lon(value):
  return fix_lat_lon_format(value, 1)

def fix_lat_lon_format(value, integer_digits):
  if value == '':
    return value
  # Convert value to float and adjust by dividing by 10^(total digits - integer digits)
  try:
    total_digits = len(str(value).replace('.', '').replace('-', ''))
    decimal_digits = total_digits - integer_digits
    value = float(str(value).replace('.', '')) / (10 ** decimal_digits)
  except ValueError:
    pass  # Handle the case where conversion to float fails
  return value

# ======================================================


# ====================== REFACTOR ======================

fixes = {
  'device_id': None,
  'position_time': fix_time_format,
  'time': fix_time_format,
  'msg_type': fix_msg_type,
  'lon': fix_lon,
  'lat': fix_lat,
}

def refactor_data(df: pd.DataFrame):
  if not check_required_columns(df):
    print(colorize(f"DATA INVALID. The required columns are not present in the file. {required_columns}", 'red'))
    return

  # FIXES
  for column, fix_function in fixes.items():
    if column in df.columns and fix_function:
      df[column] = df[column].apply(fix_function)
  
  # UNKNOWN MSG TYPEs
  if unknown_messages_found:
    print(colorize(f"Unknown message types found: {unknown_messages_found}", 'yellow'))
  
  # Rename columns
  df.rename(columns={'time': 'received_time', 'position_time': 'sent_time'}, inplace=True)
  
  # Reorder columns
  df = df[['device_id', 'sent_time', 'received_time', 'msg_type', 'lat', 'lon']]
  
  # Sort by device_id and sent_time
  df = sort_by(df, ['device_id', 'sent_time'])
  
  return df

def refactor_data_file(in_path, out_path):
  df = read_csv(in_path)
  df = refactor_data(df)
  out_path = os.path.join(out_path, os.path.basename(in_path))
  write_csv(df, out_path)
  return out_path

# ======================================================