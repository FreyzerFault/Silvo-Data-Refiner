import os
import pandas as pd
from typing import List, Callable
from utils.utils import print_colorized
from utils.file_manager import read_csv, write_csv, ensure_dir_exists
from src.goat_enhancer import get_goat_name
from typing import TypedDict

#region ========================= GROUP BY =========================
class GroupBy:
  """
  Base Group By class.
  
  Use Strategy Pattern to implement different Group Bys as SubClasses.
  """
  def __init__(self, column: str):
      self.column = column

  def group_by(self, df: pd.DataFrame) -> list[pd.DataFrame]:
    """Basic Group By function. Groups by the given column.
    
    If column not exists (day, month, hour...) returns empty [].
    Use another group_by function instead like group_by_day().
    Or create a new.
    """
    
    if self.column not in df.columns:
      print_colorized(f"The column '{self.column}' is not present in {df.columns}.", 'red')
      return []
    
    return [group for _, group in df.groupby([self.column])]


# Las siguientes clases implementan el patron Strategy
# para cada tipo de Group By (por hora, dia, mes, etc.)
# Crea columnas especificas para agruparlo.

class GroupByHour(GroupBy):
  def __init__(self, _):
    super().__init__('hour')

  def group_by(self, df: pd.DataFrame) -> list[pd.DataFrame]:
      df['hour'] = df['sent_time'].dt.floor('h')
      return super().group_by(df)

class GroupByDay(GroupBy):
  def __init__(self, _):
    super().__init__("day")
  
  def group_by(self, df: pd.DataFrame) -> list[pd.DataFrame]:
      df['day'] = df['sent_time'].dt.floor('d')
      return super().group_by(df)

class GroupByMonth(GroupBy):
  def __init__(self, _):
    super().__init__("month")
  
  def group_by(self, df: pd.DataFrame) -> list[pd.DataFrame]:
      df['sent_time'] = df['sent_time'].dt.tz_localize(None)
      df['month'] = df['sent_time'].dt.to_period('M').dt.month
      return super().group_by(df)


group_by_funcs: dict[str, GroupBy] = {
    'hour': GroupByHour('hour'),
    'day': GroupByDay('day'),
    'month': GroupByMonth('month'),
}

#endregion ===============================================================


#region ========================= GROUPER =========================

class GroupData:
  """
  Resulting Dataframes from the Group By.
  Managed by the Grouper class.
  """
  
  def __init__(self, column: str, groups: List[pd.DataFrame], file_names: List[str]):
    self.column = column
    self.groups = groups
    self.file_names = file_names

class Grouper:
  """
  Grouper executes several Group By in a Dataframe by the given columns.
  
  Saves the result GroupData by their column, with extra info like the file_path to save it to.
  """
  
  def __init__(self, df: pd.DataFrame, column_list: List[str]):
    self.dataset = df
    self.group_data_list = {
      column: GroupData(
        column = column,
        groups = group_by_funcs.get(column, GroupBy(column)).group_by(self.dataset),
        file_names=[]
      )
      for column in column_list
    }
    # Build filenames after grouping to use first value of each group to name it
    for group_data in self.group_data_list.values():
      group_data.file_names = self.build_file_names(group_data.column)

  def get_group(self, column: str) -> List[pd.DataFrame]:
    return self.group_data_list.get(column)
  
  
  class SavedGroupResult(TypedDict):
    dfs: List[pd.DataFrame]
    dir_path: str
    files: List[str]
  
  def save_to_files(self, root_path: str) -> SavedGroupResult:
    """
    Save the groups in CSV files under the root_path.
    Each group is saved in a different folder with the column name.
    
    Devuelve un diccionario {columna: {dfs: [df1, df2...], dir_path, files}}
    """
    
    file_results = Grouper.SavedGroupResult()
    for group_data in self.group_data_list.values():
      dir_name = f'group by {group_data.column}'
      dir_path = os.path.join(root_path, dir_name)
      
      # If the folder didn't exist, create it
      os.makedirs(dir_path, exist_ok=True)
      
      # Empty the folder beforehand
      for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))
      
      file_results[group_data.column] = {'dfs': group_data.groups, 'dir_path': dir_path, 'files': group_data.file_names}
      # file_results[group_data.column] =  {'dfs': group_data.groups, 'dir_path': dir_path, 'files': group_data.file_names}

      for (df, file_name) in zip(group_data.groups, group_data.file_names):
        write_csv(df, os.path.join(dir_path, file_name))
    
    return file_results

  
  def build_file_names(self, column) -> list[str]:
    """
    Pre-build the file paths for each group in the column.
    Grouped in folders by the column name.
    """
    file_names = []
    
    for index, group in enumerate(self.group_data_list[column].groups):
      prefix = column
      first_value = str(group.iloc[0][column]).replace(':', '.')
      
      if column == 'device_id':
        prefix = get_goat_name(-1 if index > 10 else index)
      
      file_name = f"{prefix} - {first_value}.csv"
      file_names.append(file_name)
    
    return file_names

#endregion =================================================================


def group_by_to_files(df: pd.DataFrame, column_list: list[str], root_path: str) -> Grouper.SavedGroupResult:
  """
  Do a Group By in the source data by different columns
  
  Save the resulting groups in CSVs under root_path, grouped by subfolders for each column.
  
  If rerun it will empty subfolders first !!
  """
  
  # Create root folder if not exists
  os.makedirs(root_path, exist_ok=True)
  
  # GROUP BY
  grouper = Grouper(df, column_list)
  
  # SAVE
  return grouper.save_to_files(root_path)
