import os

in_dir = "C:/Users/dalcanta/Proyectos/SILVO-PIRO/QGIS/Silvopastoralismo Andalucia/Collares/Collares por id Agosto - Noviembre"

commands = []
file_names = []

for file_name in os.listdir(in_dir):
  if not file_name.endswith('.csv'):
    continue
  
  file_names.append(file_name)
  
  in_path = f"C:/Users/dalcanta/Proyectos/SILVO-PIRO/QGIS/Silvopastoralismo Andalucia/Collares/Collares por id Agosto - Noviembre/{file_name}"
  out_path = f"C:/Users/dalcanta/Proyectos/SILVO-PIRO/QGIS/Silvopastoralismo Andalucia/Collares/Collares por id Agosto - Noviembre/{file_name.replace('.csv', '.shp')}"
  commands.append(f"processing.run(\"native:createpointslayerfromtable\", {'{'}\'INPUT\':\'{in_path}\',\'XFIELD\':\'lon\',\'YFIELD\':\'lat\',\'ZFIELD\':\'\',\'MFIELD\':\'\',\'TARGET_CRS\':QgsCoordinateReferenceSystem(\'EPSG:4326\'),\'OUTPUT\':\'{out_path}\'{'}'})")

print(str.join('\n', file_names))

# Crear un archivo txt con una lista de los comando para crear los shp
open("C:/Users/dalcanta/Proyectos/SILVO-PIRO/QGIS/Silvopastoralismo Andalucia/Collares/Collares por id Agosto - Noviembre/Comandos para crear los SHP.txt", "w").write(str.join('\n\n', commands))

