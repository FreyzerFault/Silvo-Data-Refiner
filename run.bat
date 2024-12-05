@echo off

REM Iniciar el entorno virtual
call .\Scripts\activate

REM Comprobar si la carpeta ./Lib/site-packages/pandas existe
if exist .\Lib\site-packages\pandas (
  echo Las dependencias ya se han instalado.
) else (
  echo Instalando dependencias...
  pip install -e .
)

REM Ejecutar el archivo .exe
.\Scripts\run-all.exe