import argparse
import os, json, yaml

class Config:
  
  test_mode: bool = False
  
  def parse_args() -> dict[str, any]:
    # -t o --test to run the script in test mode
    argparser = argparse.ArgumentParser(description='Clean and split collar data')
    argparser.add_argument('-t', '--test', action='store_true', help='Run the script in test mode')
    Config.test_mode = argparser.parse_args().test
  
  config_dir = './config'
  
  def config_file(filename) -> dict | str :
    with open(os.path.join(Config.config_dir, filename), 'r') as f:
      
      data = f.read()
      ext = os.path.splitext(filename)[1]
      
      if ext == '.json':
        return json.loads(data)
      elif ext == '.yaml':
        return yaml.load(data, Loader=yaml.FullLoader)
      
      return data
  

