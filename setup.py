import os, sys 
from setuptools import setup, find_packages

# Leer el contenido de requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

sys.path.append(os.path.join(os.getcwd(), '.'))
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src/utils'))
sys.path.append(os.path.join(os.getcwd(), 'src/data_operations'))
sys.path.append(os.path.join(os.getcwd(), 'config'))
sys.path.append(os.path.join(os.getcwd(), 'data'))

setup(
    name='Datos-Collares', 
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'run-all=src.main:main',
            'refactor=src.main:refactor_only',
            'sort_by=src.main:sort_only',
            'merge=src.main:merge_only',
            'group-by=src.main:group_by_only',
        ],
    },
)

# Instrucciones para construir el proyecto
# Para construir el proyecto, ejecuta el siguiente comando en la terminal:
# python setup.py sdist bdist_wheel

# Para instalar el paquete localmente, ejecuta:
# pip install .