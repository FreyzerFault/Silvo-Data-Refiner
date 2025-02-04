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
