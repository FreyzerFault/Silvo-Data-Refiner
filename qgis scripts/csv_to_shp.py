# Ejecutar en la consola de QGIS

# Convierte datos de PUNTOS en CSV a SHP para usar en QGIS
# Cambia la root a la carpeta donde están los CSVs
# Se creará una carpeta '/SHP' con los SHPs resultantes

import os

import sys
from PyQt5.QtGui import *
from qgis.core import *
from qgis import processing

# =========== Cambia estos valores para adaptarlos a tu caso ===========

root = "C:/Users/dalcanta/Proyectos/SILVO-PIRO/QGIS/Silvopastoralismo Andalucia/Collares/Collares por mes"

debug = True
overwrite_layer = False

params = {
  'qgis_algorithm': 'native:createpointslayerfromtable',
  
  'in_dir': root,
  'out_dir': os.path.join(root, "SHP"),
  
  'projection': QgsCoordinateReferenceSystem('EPSG:4326'),
  'coordinate_fields': ('lon', 'lat'),
  
  # Si no se especifica, se usan todos los CSVs en la carpeta de entrada
  'in_files': ['Collares Agosto']
}

# =======================================================================

in_files = [(file + '.csv') for file in params['in_files']] if params['in_files'] else os.listdir(params['in_dir'])


if debug:
  print(f"\nParsing files:")
  print('\n'.join([f"{file} -> .shp" for file in in_files]))


# Crea la carpeta de salida si no existe
if not os.path.exists(params['out_dir']):
  os.makedirs(params['out_dir'])

# Se repite el proceso por cada CSV en la carpeta de entrada
executed_commands = []
parsed_CSVs = []  
for file_name in in_files:
  if not file_name.endswith('.csv'):
    continue
  
  in_path = os.path.join(params['in_dir'], file_name)
  out_path = os.path.join(params['out_dir'], file_name.replace('.csv', '.shp'))
  
  command_name = params['qgis_algorithm']
  command_args = {
    'INPUT':in_path,
    'XFIELD':params['coordinate_fields'][0],
    'YFIELD':params['coordinate_fields'][1],
    'ZFIELD':'',
    'MFIELD':'',
    'TARGET_CRS': params['projection'],
    'OUTPUT':out_path
  }
  
  # Busca la layer que tenga de fuente el archivo SHP a ver si existe ya
  existing_layer = None
  layer_exists = False
  for layer in QgsProject.instance().mapLayers().values():
    if layer.source().endswith(file_name.replace('.csv', '.shp')):
      existing_layer = layer
      layer_exists = True
      break
  
  # Si permites sobrescribirla, elimina la capa para sustituirla
  # Si no, cancelará la conversión de este archivo y seguirá si hay más
  if layer_exists:
    if overwrite_layer:
      QgsProject.instance().removeMapLayer(layer)
    else:
      print(f'''
Error: Layer {file_name.replace('.csv', '')} already exists. You could:
- Set 'overwrite_layer' to True to overwrite it
- Change the out_file name
- Delete the existing layer manually
''')
      continue
  
  try:
    processing.run(command_name, command_args)
    
    # Sustituimos la capa eliminada por la nueva con el nuevo SHP
    if overwrite_layer and layer_exists:
      out_layer = QgsVectorLayer(out_path, file_name.replace('.csv', ''), 'ogr')
      if out_layer.isValid():
        QgsProject.instance().addMapLayer(out_layer)
      else:
        print(f"Error: Layer {file_name.replace('.csv', '')} is not valid")
    
  except Exception as e:
    print(f"Error {e} in command:\n{command_name} {command_args}")
    continue
  
  parsed_CSVs.append(file_name)
  executed_commands.append((command_name, command_args))

# DEBUG
if debug:
  if not executed_commands:
    print("Error parsing. No command executed")
  else:
    print("========================================================")
    print("EXECUTED COMMANDS:")
    for i in range(len(executed_commands)):
      print(f"CSV: {parsed_CSVs[i]} \n -> SHP: {parsed_CSVs[i].replace('.csv', '.shp')}")
      print(f"Command executed: {executed_commands[i][0]} {executed_commands[i][1]}")
      print("========================================================")
