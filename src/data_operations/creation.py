import pandas as pd
from data_operations.group_by import GroupBy
from data_operations.merge import merge

#region ====================== END DATE ======================

# Añade la fecha de fin como la fecha del proximo mensaje del mismo collar
# Esto después permite animarlo en QGIS para ver la trayectoria de los collares mas claramente
def add_end_date(df: pd.DataFrame):
  
  # Add end_date col with the time of the next message
  df['end_date'] = df.groupby('device_id')['sent_time'].shift(-1)
  
  # Reorder end_date after sent_time
  columns = df.columns.tolist()
  sent_index = columns.index('sent_time')
  columns.insert(sent_index + 1, columns.pop(columns.index('end_date')))
  df = df[columns]
  
  # Fill empty end_date with his sent_time + 15 mins
  df['end_date'] = df['end_date'].fillna(df['sent_time'] + pd.Timedelta(minutes=15))
  
  return df

#endregion