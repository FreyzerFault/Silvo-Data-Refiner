import pandas as pd

#region ====================== END DATE ======================

# Añade la fecha de fin como la fecha del proximo mensaje del mismo collar
# Esto después permite animarlo en QGIS para ver la trayectoria de los collares mas claramente
def add_end_date(df: pd.DataFrame):
  sent_time = df['sent_time']
  df['end_date'] = sent_time.shift(-1)
  return df

#endregion