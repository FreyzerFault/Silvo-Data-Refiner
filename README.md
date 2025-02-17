# Silvo Data Refiner

## Descripción

Silvo Data Refiner es una herramienta de procesamiento de datos de collares inteligentes.

Se encarga de limpiar, ordenar y juntar los datos para su uso consistente en otros procesos posteriores.

También permite agrupar todos los datos por atributos. Por ejemplo, por ID o por mes.

Toda la configuración referente al procesamiento de estos está en **/config/settings.yaml**.

## Datos

Inserta los datos CSV en la carpeta **/data/in/**.

Los resultados se almacenan en **/data/out**.

Si quieres configurar otras rutas puedes modificar **/config/settings.yaml**.

Por ahora la estructura de los Datos requiere de las siguientes columnas (formato de collares NoFence):

| device_id | position_time | time | msg_type | lat | lon | ... |
|-|-|-|-|-|-|-|
|2024-09-02 21:58:20+00:00|229175|poll_msg|2024-09-30 21:32:57+00:00|38.3843833|-2.6894614| ... |

---

Para su uso posterior he decidido renombrar:

- position_time -> sent_time
- time -> received_time

## Pipeline

Para cada dataset de entrada:

- **Refactoriza** los datos ordenando las columnas y asignándoles nombres de columnas consistentes.
- **Reformatea** las fechas a un formato consistente entre todos los dataset
- **Ordena** los dataset por ID y sent_time (configurable)
- Añade una columna **end_date** (fecha y hora del siguiente elemento en orden para usarla en QGIS)

Todos los dataset se **juntan** en uno y se vuelve a ordenar por ID y sent_time (configurable).

Luego se agrupa por los atributos más relevantes:

- ID
- Mes
- Día
- Tipo de mensaje
- ...

Se agrupan para obtener archivos más pequeños para usar en posteriores procesos de forma más eficiente y legible. En QGIS por ejemplo.

## Uso

Puedes ejecutar todo el proceso con el archivo **run.bat**

## Instalación

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

Usa **'-t'** para configurar como entrada los datasets dentro de **data/test/in** y sus resultados en **data/test/out**:

```shell
run-all -t
```

---

## Conversor CSV a SHP

Ubicación script: ./qgis_scripts/csv_to_shp.py

Convierte todos los archivos CSV de una carpeta a SHP.

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

