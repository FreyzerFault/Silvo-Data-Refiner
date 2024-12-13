import os
import pandas as pd
from src.file_manager import read_csv, write_csv
from src.utils import colorize, str_to_time
from src.sort import sort_by


#region ==================== CHECK COLUMNS ========================
required_columns = ['device_id', 'time', 'msg_type', 'position_time', 'lat', 'lon']

def check_required_columns(df):
  for column in required_columns:
    if not column in df.columns:
      print(colorize(f"The required column '{column}' is not present in the file.", 'red'))
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

#endregion


#region ===================== ENUM ======================

unknown_msg = 'unknown'
empty_msg = ''
unknown_enum_found = {
  "msg_type": set(),
  "collar_status": set(),
  "fence_status": set(),
  "mode": set()
}

msg_types_identifiers = {
  'seq_msg':    ['seq'],
  'poll_msg':   ['poll'],
  'warn_msg':   ['warn'],
  'zap_msg':    ['zap', 'pulse'],
  'status_msg': ['status'],
}

mode_identifiers = {
  'fence':    ['Fence'],
  'trace':    ['Trace'],
  'teach':    ['Teach'],
}

collar_status_identifiers = {
  'normal':    ['Normal'],
  'sleep':   ['Sleep'],
  'power_off':    ['PowerOff', 'Off'],
  'off_animal': ['OffAnimal'],
}

fence_status_identifiers = {
  'normal':    ['FenceStatus_Normal', 'Normal'],
}

fix_msg_type = lambda value: fix_enum('msg_type', value, msg_types_identifiers)
fix_mode = lambda value: fix_enum('mode', value, mode_identifiers)
fix_collar_status = lambda value: fix_enum('collar_status', value, collar_status_identifiers)
fix_fence_status = lambda value: fix_enum('fence_status', value, fence_status_identifiers)

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

def refactor_data(df: pd.DataFrame):
  if not check_required_columns(df):
    print(colorize(f"DATA INVALID. The required columns are not present in the file. {required_columns}", 'red'))
    return

  # FIXES
  for column, fix_function in fixes.items():
    if column in df.columns and fix_function:
      df[column] = df[column].apply(fix_function)
  
  # UNKNOWN MSG TYPEs
  for column, unknown_msgs in unknown_enum_found.items():
    if len(unknown_msgs) > 0:
      print(colorize(f"Unknown {column} found: {unknown_msgs}", 'yellow'))
  
  # Rename columns
  df.rename(columns={'time': 'received_time', 'position_time': 'sent_time'}, inplace=True)
  
  # Reorder columns
  required_columns = ['device_id', 'sent_time', 'received_time', 'msg_type', 'lat', 'lon']
  optional_columns = ['mode', 'collar_status', 'fence_status']
  optional_columns = [column for column in optional_columns if column in df.columns]
  df = df[required_columns + optional_columns]
  
  # Sort by device_id and sent_time
  df = sort_by(df, ['device_id', 'sent_time'])
  
  return df

def refactor_data_file(in_path, out_path):
  df = read_csv(in_path)
  df = refactor_data(df)
  out_path = os.path.join(out_path, os.path.basename(in_path))
  write_csv(df, out_path)
  return out_path

#endregion