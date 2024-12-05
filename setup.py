from setuptools import setup, find_packages

# Leer el contenido de requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='Datos Collares',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'run-all=src.main:main',
            'refactor=src.main:refactor',
            'merge=src.main:merge',
            'group_by=src.main:group_by',
        ],
    },
)