# Procesamiento de Datos de Collares

Esta herramienta ejecuta una pipeline de procesos de limpieza, unión y clasificación de datos de collares inteligentes.

## Datos

Los datos deben estar en formato CSV.
Deben tener las siguientes columnas:

- device_id
- position_time
- time
- msg_type
- lat
- lon

El programa ya se encarga de limpiarlos y darles un formato consistente.

## Estructura del Proyecto

- `run.py`: Archivo principal que ejecuta toda la pipeline de procesamiento.
- `data/`: Carpeta que contiene los datos de entrada y salida.
  - `data/in/`: Carpeta donde se deben colocar los archivos de datos de collares en formato `.csv`.
  - `data/out/`: Carpeta donde se generarán los archivos `.csv` resultantes después de ejecutar la pipeline.

## Instrucciones de Uso

1. Coloca los archivos de datos de collares en formato `.csv` en la carpeta `data/in/`.
2. Ejecuta el archivo `run.py` para iniciar la pipeline de procesamiento.
3. Los archivos `.csv` resultantes se generarán en la carpeta `data/out/`.

## Requisitos

- Python 3.x
