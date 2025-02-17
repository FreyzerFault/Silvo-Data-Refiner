import pandas as pd
from colorama import Back, Fore, Style

#region ========================= LOGGING =========================
def colorize(text, color):
  color_dict = {
    'red': Fore.RED,
    'green': Fore.GREEN,
    'yellow': Fore.YELLOW,
    'blue': Fore.BLUE,
    'magenta': Fore.MAGENTA,
    'cyan': Fore.CYAN,
    'white': Fore.WHITE,
    'black': Fore.BLACK,
    'gray': Fore.LIGHTBLACK_EX,
    'grey': Fore.LIGHTBLACK_EX,
    'reset': Style.RESET_ALL
  }
  color_code = color_dict.get(color.lower(), Fore.RESET)
  return f"{color_code}{text}{Style.RESET_ALL}"

def print_colorized(text, color = 'blue', end = '\n'):
  print(colorize(text, color), end=end)

#endregion ======================================================


#region ========================= DATE =========================

def time_to_str(time: pd.Timestamp, date_format = '%d/%m/%Y %H:%M:%S') -> str:
  if pd.isnull(time):
    return time
  return time.strftime(date_format)

def str_to_time(value: str, date_format = '%d/%m/%Y %H:%M:%S') -> pd.Timestamp:
    # Invalid values
  if str(value) == '' or 'nan' in str.lower(str(value)) or 'NaT' in str(value):
    return pd.Timestamp('NaT')
  
  # Try to convert the value to a datetime object
  try:
    split_date = value.split('-')
    if len(split_date) == 1:
      split_date = value.split('/')
    
    dayfirst = True if len(split_date) == 1 or len(str(split_date[0])) == 2 else False
    time = pd.to_datetime(value, dayfirst=dayfirst)
    time = unlocalize_utc_dt(time)
    return time
  except ValueError as e:
    pass
  
  # Try specifying different formats if the automatic conversion fails
  formats = ['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S+.%f%z']
  for fmt in formats:
    try:
      time = pd.to_datetime(value, format=fmt)
      time = unlocalize_utc_dt(time)
      return time
    except ValueError as e:
      print(colorize(f"Could not fix the time format for value: {value}\n Error: {e}", 'yellow'))
  
  # If all formats fail, return the original value
  return pd.Timestamp('NaT')

def unlocalize_utc_dt(time: pd.Timestamp) -> pd.Timestamp:
  if time.tzinfo is not None:
    return time.tz_localize(None)
  return time

#endregion ======================================================