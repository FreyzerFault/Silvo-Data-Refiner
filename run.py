import subprocess
import os

def main():
  
  # Ruta al ejecutable en la carpeta Scripts
  script_path = os.path.join('Scripts', 'run-all')
  
  # Ejecutar el script
  subprocess.run(['cmd', '/c', script_path + '.exe'])

if __name__ == '__main__':
  main()