# Silvo Data Refiner

Procesamiento de Datos de Collares Inteligentes en Silvopastoralismo

<img src="./Silvo%20Data%20Refiner%20Icon.png" alt="Silvo Data Refiner Icon" width="50%" style="margin-left:auto;margin-right:auto;display:block">

## Descripción

Silvo Data Refiner es una herramienta de procesamiento de datos de collares inteligentes.

Se encarga de limpiar, ordenar y juntar los datos para su uso consistente en otros procesos posteriores.

También permite agrupar todos los datos por atributos. Por ejemplo, por ID o por mes.

## Uso

Inserta los datos CSV en la carpeta **/data/in/**.

Los resultados se almacenan en **/data/out**.

Puedes ejecutar todo el proceso con el archivo **run.bat**

Si quieres configurar otras rutas, además de otros parámetros, puedes modificar **/config/settings.yaml**.

## Datos de Entrada

Por ahora la estructura de los Datos de Entrada requiere de las siguientes columnas (formato de collares NoFence):

| device_id | position_time | time | msg_type | lat | lon | ... |
|-|-|-|-|-|-|-|
|229175|2024-09-02 21:58:20+00:00|2024-09-30 21:32:57+00:00|poll_msg|38.3843833|-2.6894614| ... |

## Pipeline

Para cada dataset de entrada:

### Refactorizado

Ordena y renombra las columnas de forma consistente.

Renombrados:

- position_time -> sent_time
- time -> received_time

### Reformateo de fechas

Para seguir un formato consistente entre todos los dataset.

### Ordenado

Por ID y sent_time (configurable en *settings.yaml*)

### Columnas Extra

Se añade una columna **end_date** (fecha y hora del siguiente elemento en orden para usarla en QGIS)

### Unión de datasets

Se **unen** en uno y se vuelve a ordenar por ID y sent_time (configurable en *settings.yaml*).

El resultado se guarda en *out/merged/merged.csv*

### Agrupación

Se agrupa por los atributos más relevantes (configurable en *settings.yaml*):

- ID
- Mes
- Día
- Tipo de mensaje
- ...

Se agrupan para obtener archivos más pequeños para usar en posteriores procesos de forma más eficiente y legible. En QGIS ayuda a su uso ágil.

Los resultados se guardan en *out/group by [columna]/[valor].csv*

## Instalación del Entorno de Desarrollo

Debes tener python 3 instalado.

Crea un entorno virtual de python y ejecútalo:

```shell
python -m venv .venv
```

```shell
activate
```

Instala las dependencias:

```shell
python setup.py sdist bdist_wheel
```

```shell
pip install .
```

Tiene varios scripts:

- **run-all**: Ejecuta toda la pipeline
- **refactor**: Ejecuta solo el refactor de los archivos individuales
- **merge**: Junta todos los datasets en uno
- **sort_by**: Ejecuta la ordenación del dataset resultado del merge
- **group-by**: Agrupa el dataset del merge en distintos subgrupos por cada una de las columnas dadas en **/config/settings.yaml**

```shell
run-all
```

## Testing

Si los datos son demasiado pesados y el algoritmo tarda mucho en completarse puedes usar el modo testing:

Usa **'-t'** para configurar como entrada los datasets dentro de **data/test/in** y sus resultados en **data/test/out**:

```shell
run-all -t
```

## Conversor CSV a SHP

Cuando tengas los datos procesados puedes convertirlos a SHP para usarlos en QGIS, por ejemplo, ejecutando este script.

Ubicación: ./qgis_scripts/csv_to_shp.py

### Funcionamiento

Inserta el script en la consola de QGIS (no funciona por sí solo sin QGIS).

- Abre la Consola en QGIS
- Pulsa en "Mostrar editor" y abre el script.
- Pulsa en ejecutar

### Configuración

Al principio del script está toda la configuración.

- **root**: con la ruta de la carpeta con todos los CSV que quieras convertir.
- **debug**: Muestra por consola más información.
- **overwrite_layer**: Si quieres sobrescribir SHPs ya generados anteriormente, y hay layers usándolos, sobrescribe las layers.
(Si sobrescribes las layers perderán todo el estilo, queda pendiente solucionarlo pero no he sido capaz).
- **params**: Parámetros del algoritmo usado. Si los datos del CSV tienen coordenadas distintas de **"lon"** y **"lat"**, con otra **proyección**. Para los datos de collares de este proyecto no será necesario.
Si quieres filtrar qué archivos serán procesados de dentro de la carpeta root (**in_files**), puedes añadir los archivos que quieras usar. Déjalo vacío para que procese TODOS los CSVs.

### Recomendación al Sobrescribir

Abre otro **proyecto vacío** temporalmente, ejecútalo con **overwrite_layer = False**.

>(Si lo ejecutas con *overwrite_layer = False* en el mismo proyecto dará un error al escribir los SHP porque no pueden modificarse mientras estén usándose por QGIS.)

Vuelve a abrir el proyecto. La fuente de datos de las layers deberían haberse modificado automáticamente sin perder todo el estilo.
