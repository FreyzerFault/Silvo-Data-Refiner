import os, json
import pandas as pd
from utils.config import Config
from utils.file_manager import read_csv, write_csv
from utils.utils import print_colorized, str_to_time
from data_operations.sort import sort_by
from data_operations.creation import add_end_date


#region ==================== CHECK COLUMNS ========================
required_columns = ['device_id', 'time', 'msg_type', 'position_time', 'lat', 'lon']

def has_required_columns(df):
  for column in required_columns:
    if not column in df.columns:
      print_colorized(f"The required column '{column}' is not present in the file.", 'red')
      return False
  return True

#endregion


#region ======================== TIME ========================


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

#endregion


#region ====================== LAT LON ========================

def fix_lat(lat):  return fix_lat_lon_format(lat, 2)
def fix_lon(lon):  return fix_lat_lon_format(lon, 1)

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

#endregion


#region ===================== ENUM ======================

# Use /config/enum_identifiers.json to substitute similar values with the one correct enum value
# This makes enum values consistent and easier to work with in the data

identifiers: dict = Config.config_file('enum_identifiers.json')

def fix_msg_type(value: str):       return fix_enum('msg_type', value, identifiers['msg_type'])
def fix_mode(value: str):           return fix_enum('mode', value, identifiers['mode'])
def fix_collar_status(value: str):  return fix_enum('collar_status', value, identifiers['collar_status'])
def fix_fence_status(value: str):   return fix_enum('fence_status', value, identifiers['fence_status'])

# UNKNOWN VALUES:
# All unknown values found will be stored in unknown_enum_found
# For future analysis and correction in /config/enum_identifiers.json
unknown_msg = 'unknown'
empty_msg = ''
unknown_enum_found = {
  "msg_type": set(),
  "collar_status": set(),
  "fence_status": set(),
  "mode": set()
}

def show_unknown_enum_found():
  for column, unknown_msgs in unknown_enum_found.items():
    if len(unknown_msgs) > 0:
      print_colorized(f"Unknown {column} found: {unknown_msgs}", 'yellow')


def fix_enum(column_name: str, value: str, enum_values: dict):
  if value == '' or value == None or value == 'nan':
    return ''
  
  if type(value) != str:
    unknown_enum_found[column_name].add(f"{value} ({type(value)})")
    return unknown_msg
  
  for enum_value, identifiers in enum_values.items():
    for identifier in identifiers:
      if identifier.lower() in value.lower():
        return enum_value
  
  unknown_enum_found[column_name].add(value)
  return unknown_msg

#endregion


#region ====================== REFACTOR ======================

# FIXES => Apply fix function to each column
fixes = {
  'device_id': None,
  'position_time': fix_time_format,
  'time': fix_time_format,
  'msg_type': fix_msg_type,
  'lon': fix_lon,
  'lat': fix_lat,
  'mode': fix_mode,
  'collar_status': fix_collar_status,
  'fence_status': fix_fence_status,
}

def refactor(df: pd.DataFrame) -> pd.DataFrame:
  if not has_required_columns(df):
    print_colorized(f"DATA INVALID. The required columns are not present in the file. {required_columns}", 'red')
    return

  # FIXES => Apply fix function to each column
  for column, fix_function in fixes.items():
    if column in df.columns and fix_function:
      df[column] = df[column].apply(fix_function)
  
  # Check UNKNOWN MSG TYPEs => Print unknown values to fix it later
  show_unknown_enum_found()
  
  # Rename columns
  df.rename(
      columns={
          'time': 'received_time', 
          'position_time': 'sent_time'
      }, 
      inplace=True
    )
  
  # Reorder columns
  required_columns = ['device_id', 'sent_time', 'received_time', 'msg_type', 'lat', 'lon']
  
  # Optional columns are added if previously present in the dataset
  optional_columns = ['mode', 'collar_status', 'fence_status']
  optional_columns = [column for column in optional_columns if column in df.columns]
  
  df = df[required_columns + optional_columns]
  
  # Sort by device_id and sent_time
  df = sort_by(df, ['device_id', 'sent_time'])
  
  return df


def refactor_data_file(in_path, out_path, do_add_end_date=False):
  df = read_csv(in_path)
  df = refactor(df)
  
  out_path = os.path.join(out_path, os.path.basename(in_path))
  write_csv(df, out_path)
  return out_path

#endregion

