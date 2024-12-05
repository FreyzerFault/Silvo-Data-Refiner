import subprocess
import os

def main():
  # Check si las dependencias están instaladas
  if not os.path.exists('./Lib/site-packages/pandas'):
    print('Installing dependencies...')
    
    # Instala los paquetes necesarios
    subprocess.run(['pip', 'install', '-e', '.'])
  
  
  # Ruta al ejecutable en la carpeta Scripts
  script_path = os.path.join('Scripts', 'run-all')
  
  # Ejecutar el script
  subprocess.run(['cmd', '/c', script_path + '.exe'])

if __name__ == '__main__':
  main()