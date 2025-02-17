import os
import pandas as pd
from tqdm import tqdm
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
    
    return [group for _, group in df.groupby([self.column], observed=False)]


class GroupByCalculated(GroupBy):
  """Group By a Calculated Column.
  
  Use Strategy Pattern to implement different Group Bys as SubClasses.
  Each Group By Calculate his column with the given calculation function.
  When Grouped, the column is removed from the resulting DataFrames.
  """
  def __init__(self, column: str, calculation: Callable[[pd.DataFrame], pd.DataFrame]):
    self.column = column
    self.calculation = calculation
  
  def group_by(self, df: pd.DataFrame) -> list[pd.DataFrame]:
    # Copy the DataFrame to avoid modifying the original to add the calculated column
    df_copy = df.copy()
    df_copy[self.column] = self.calculation(df_copy)
    
    # Group By the calculated column
    groups = super().group_by(df_copy)
    
    # Drop the calculated column from the resulting DataFrames (it's redundant)
    # Uses attributes to store metadata such as the group_by column value
    # So we can drop the whole column to save memory
    for group in groups:
      group.attrs['group_by'] = self.column
      group.attrs['group_by_value'] = group[self.column].iloc[0]
      group.drop(columns=[self.column], inplace=True)
    
    return groups



# FACTORY:
def get_group_by_func(column: str) -> GroupBy:
  return {
    'hour': GroupByHour(),
    'day': GroupByDay(),
    'month': GroupByMonth(),
    'year': GroupByYear(),
  }.get(column, GroupBy(column))

#endregion ===============================================================


#region ========================= GROUP BY SPECIFIC FUNCTIONS =========================
# Las siguientes clases implementan el patron Strategy
# para cada tipo de Group By Calculated (por hora, dia, mes, etc.)
# Crea columnas especificas para agruparlo.

class GroupByHour(GroupByCalculated):
  def __init__(self):
    super().__init__('hour', 
                      lambda df: # Floor the time to the nearest hour
                        df['sent_time'].dt.floor('h').apply(
                          lambda date: # Format the date to a string without mins and secs
                            date.strftime('%Y-%m-%d %H')
                        )
                    )

class GroupByDay(GroupByCalculated):
  def __init__(self):
    super().__init__('day', 
                      lambda df: # Floor the time to the nearest day
                        df['sent_time'].dt.floor('d').apply(
                          lambda date: # Format the date to a string without time
                            date.strftime('%Y-%m-%d')
                        )
                    )

class GroupByMonth(GroupByCalculated):
  def __init__(self):
    super().__init__('month',
                      lambda df: # Floor the time to the nearest month
                        df['sent_time'].dt.to_period('M').astype(str)
                    )

class GroupByYear(GroupByCalculated):
  def __init__(self):
    super().__init__('year',
                      lambda df: # Floor the time to the nearest year
                        df['sent_time'].dt.floor('Y').apply(
                          lambda date: # Format the date to a string
                            date.strftime('%Y')
                        )
                    )

#endregion ===============================================================


#region ========================= GROUPER =========================

class GroupData:
  """
  Resulting Dataframes from the Group By.
  Managed by the Grouper class.
  """
  
  def __init__(self, column: str, dfs: List[pd.DataFrame], file_names: List[str]):
    self.column = column
    self.dfs = dfs
    self.file_names = file_names

class Grouper:
  """
  Grouper executes several Group By in a Dataframe by the given columns.
  
  Saves the result GroupData by their column, with extra info like the file_path to save it to.
  """
  
  def __init__(self, df: pd.DataFrame, column_list: List[str]):
    self.dataset = df
    self.group_data_list = {}
    for i in tqdm(range(len(column_list)), desc=f'Grouping data into {len(column_list)} columns', unit='col', colour='cyan'):
      column = column_list[i]
      self.group_data_list[column] = GroupData(
        column = column,
        dfs = get_group_by_func(column).group_by(self.dataset),
        file_names=[]
      )
    
    # Build filenames after grouping to use first value of each group to name it
    for group_data in self.group_data_list.values():
      group_data.file_names = self.build_file_names(group_data.column)

  def get_group(self, column: str) -> List[pd.DataFrame]:
    return self.group_data_list.get(column)
  
  
  #region ========================= SAVE TO FILES =========================
  
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
    
    for i in tqdm(range(len(self.group_data_list.values())), desc='Saving groups to files', unit='col', colour='cyan'):
      group_data = list(self.group_data_list.values())[i]
      dir_name = f'group by {group_data.column}'
      dir_path = os.path.join(root_path, dir_name)
      
      # If the folder didn't exist, create it
      os.makedirs(dir_path, exist_ok=True)
      
      # Empty the folder beforehand
      for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))
      
      file_results[group_data.column] = {'dfs': group_data.dfs, 'dir_path': dir_path, 'files': group_data.file_names}
      # file_results[group_data.column] =  {'dfs': group_data.groups, 'dir_path': dir_path, 'files': group_data.file_names}

      for (df, file_name) in zip(group_data.dfs, group_data.file_names):
        write_csv(df, os.path.join(dir_path, file_name))
    
    return file_results

  
  def build_file_names(self, column) -> list[str]:
    """
    Pre-build the file paths for each group in the column.
    Grouped in folders by the column name.
    """
    file_names = []
    
    for index, group in enumerate(self.group_data_list[column].dfs):
      group_by_col = group.attrs.get('group_by', '')
      group_by_value = group.attrs.get('group_by_value', '')
      
      if column == 'device_id':
        group_by_col = get_goat_name(-1 if index > 10 else index)
      
      file_name = f"{group_by_col} - {group_by_value}.csv"
      file_names.append(file_name)
    
    return file_names
  
  #endregion ===============================================================

#endregion =================================================================


def group_by(df: pd.DataFrame, column_list: list[str]) -> dict[str, list[pd.DataFrame]]:
  """
  Do a Group By in the source data by different columns
  
  Returns a dictionary with the resulting groups.
  """
  
  # GROUP BY
  grouper = Grouper(df, column_list)
  
  # RETURN
  return {group.column: group.dfs for group in grouper.group_data_list.values()}


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
