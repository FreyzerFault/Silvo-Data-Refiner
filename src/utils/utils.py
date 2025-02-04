import pandas as pd
from colorama import Back, Fore, Style

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

def print_colorized(text, color = 'blue'):
  print(colorize(text, color))

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
    return time
  except ValueError:
    pass
  
  # Try specifying different formats if the automatic conversion fails
  formats = ['%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%Y/%m/%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S+.%f%z']
  for fmt in formats:
    try:
      time = pd.to_datetime(value, format=fmt)
      return time
    except ValueError:
      continue
  
  # If all formats fail, return the original value
  print(colorize(f"Could not fix the time format for value: {value}", 'yellow'))
  return pd.Timestamp('NaT')