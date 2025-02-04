import argparse
import os, json, yaml
from .utils import print_colorized

class Config:
  
  test_mode: bool = False
  
  def parse_args() -> dict[str, any]:
    # -t o --test to run the script in test mode
    argparser = argparse.ArgumentParser(description='Clean and split collar data')
    argparser.add_argument('-t', '--test', action='store_true', help='Run the script in test mode')
    Config.test_mode = argparser.parse_args().test
  
  config_dir = './config'
  
  def config_file(filename) -> dict | str :
    file_path = os.path.join(Config.config_dir, filename)
    with open(file_path, 'r') as f:
      
      data = f.read()
      ext = os.path.splitext(filename)[1]
      
      print_colorized(f"Reading Config file:{file_path}", 'blue')
      
      if ext == '.json':
        return json.loads(data)
      elif ext == '.yaml':
        return yaml.load(data, Loader=yaml.FullLoader)
      
      return data
  

