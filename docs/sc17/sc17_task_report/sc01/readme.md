---
id: SCP-SC17-SC01
estado: en_progreso
propietario: pmo-supercomputing
ultima_actualizacion: 2025-02-18
relacionados: ["SCP-SC17-TASKS", "DOC-DEVOPS-INDEX", "DOC-INDEX-GENERAL"]
---
# Solicitud SC01 · Preparación de entorno MkDocs

Esta solicitud documenta los pasos necesarios para instalar MkDocs en los equipos del equipo SC17. Sigue el procedimiento estándar para garantizar compatibilidad con la base documental y las herramientas de automatización de la oficina de proyectos.

## Requisitos previos
- Python 3.8 o superior instalado y disponible en la variable de entorno `PATH`.
- Conectividad a Internet para descargar dependencias desde PyPI.
- Permisos para instalar paquetes en el entorno de trabajo (virtualenv recomendado).

## Pasos de instalación
1. Instala MkDocs mediante `pip`.
   ```bash
   pip install mkdocs
   ```
2. Verifica la instalación comprobando la versión.
   ```bash
   mkdocs --version
   ```
   El resultado esperado es similar a:
   ```
   mkdocs, version 1.2.0 from /usr/local/lib/python3.8/site-packages/mkdocs (Python 3.8)
   ```

## Notas adicionales
- **Manpages opcionales:** Si se requieren páginas de manual, instala `click-man` y genera la documentación correspondiente.
  ```bash
  pip install click-man
  click-man --target path/to/man/pages mkdocs
  ```
- **Consideraciones en Windows:** Algunos comandos pueden requerir el prefijo `python -m`.
  ```bash
  python -m pip install mkdocs
  python -m mkdocs
  ```
  Para una solución permanente, agrega el directorio `Scripts` de la instalación de Python a la variable `PATH`. Los instaladores recientes incluyen el script `win_add2path.py` en `Tools/Scripts/` para automatizar este paso.

## Checklist de finalización
- [ ] MkDocs instalado y accesible desde la terminal.
- [ ] Versión verificada y documentada.
- [ ] Manpages generadas (si aplica).
- [ ] Actualización de `PATH` confirmada en equipos Windows (si corresponde).
