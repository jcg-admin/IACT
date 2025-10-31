# Errores detectados en bootstrap.sh

1. **Ejecución abortada antes de la lógica principal**: el script realiza una fase de diagnóstico inicial y luego ejecuta `exit 0`, lo que impide que se definan y ejecuten las funciones de instalación declaradas en la segunda mitad del archivo. Ningún paso del bootstrap llega a ejecutarse por este corte prematuro. (Ver líneas 200-214 del `bootstrap.sh`).

2. **Comandos de diagnóstico frágiles**: durante la fase previa al `exit` se listan y consultan permisos de `/vagrant` y `$PROJECT_ROOT/scripts` sin comprobar su existencia. En entornos donde `/vagrant` no existe (por ejemplo, ejecución fuera de Vagrant) `ls` y `stat` fallan, provocando ruido o errores si se habilita `set -e`. (Líneas 24-33).

3. **Captura incorrecta de fallos en scripts hijo**: `execute_installation_script` encadena la ejecución con `tee` sin `set -o pipefail`, de modo que un script hijo que falle devuelve exit code 0 al evaluarse la tubería, y el error no se detecta. (Líneas 243-250).

4. **Definición de pasos con espacios en blanco**: las funciones `define_*_steps` generan cadenas multilínea con sangrías; al mapearse, cada entrada conserva espacios iniciales, lo que produce tipos como `'        func'` y hace que `run_bootstrap_steps` las trate como pasos de tipo desconocido. (Líneas 300-354 y 370-393).

5. **Mensajes incongruentes**: `report_bootstrap_results` afirma que "Todos los servicios están en ejecución" aunque ningún chequeo real de servicios se ha ejecutado debido al `exit 0` anterior, lo que induce a error al operador. (Líneas 408-424).

