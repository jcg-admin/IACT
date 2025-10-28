# Auditoría de Dev Container

## Resumen de extensiones configuradas

El archivo `.devcontainer/devcontainer.json` declara la instalación automática de las siguientes extensiones de VS Code:

- `ms-python.python`
- `ms-python.vscode-pylance`
- `ms-python.debugpy`
- `batisteo.vscode-django`
- `charliermarsh.ruff`
- `ms-python.black-formatter`
- `littlefoxteam.vscode-python-test-adapter`
- `ms-azuretools.vscode-docker`
- `mtxr.sqltools`
- `mtxr.sqltools-driver-pg`
- `mtxr.sqltools-driver-mysql`
- `eamodio.gitlens`
- `usernamehw.errorlens`
- `streetsidesoftware.code-spell-checker`
- `editorconfig.editorconfig`

## Configuraciones relevantes de VS Code

También se declaran las siguientes preferencias destacadas:

- Python:
  - `python.defaultInterpreterPath`: `/usr/local/bin/python`
  - `python.testing.pytestEnabled`: `true`
  - `python.testing.pytestArgs`: `['tests', '-v', '--cov=.', '--cov-report=html', '--cov-report=term-missing']`
  - `python.linting.ruffEnabled`: `true`
  - Formateador predeterminado (`[python].editor.defaultFormatter`): `ms-python.black-formatter`
- Editor:
  - `editor.formatOnSave`: `true`
  - `editor.codeActionsOnSave`: `{"source.organizeImports": "explicit", "source.fixAll": "explicit"}`
  - Reglas de columna: 88 y 120
  - Indentación: 4 espacios, detección automática desactivada
- Archivos:
  - Exclusiones para cachés (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `htmlcov`)
  - Asociación de templates Django a `django-html`/`django-txt`
  - Trim de espacios finales y nueva línea final obligatoria
- Terminal: perfil predeterminado Bash
- Git: `git.autofetch` activo, confirmación de sincronización desactivada, Smart Commit activo
- SQLTools: conexión preconfigurada a PostgreSQL `db_postgres:5432`
- Tema: `Default Dark+`, telemetría desactivada

## Observaciones sobre comandos del contenedor

- `onCreateCommand` intenta ejecutar `pip install -r requirements/dev.txt` y `pip install -r requirements/test.txt`. El repositorio actual solo incluye `requirements.txt` y `requirements-test.txt`, por lo que estos comandos fallarán si no se añaden los archivos esperados.
- `workspaceFolder` está configurado como `/workspace/callcentersite`, mientras que el repositorio clonado en este entorno reside en `/workspace/IACT---project`. Esta discrepancia puede impedir que VS Code abra el árbol de archivos correcto.
- Los comandos de `postStartCommand` asumen la presencia del servicio `db_postgres` y la aplicación Django lista para ejecutar migraciones dentro del contenedor Docker Compose. En este entorno basado en Vagrant no se puede validar su ejecución.

## Verificación dentro del contenedor

Este entorno de automatización no dispone de una instancia de VS Code, por lo que no es posible confirmar de forma directa que las extensiones se instalen o aparezcan activas. Tampoco se encontró un directorio `~/.vscode-server/extensions` que permita comprobar instalaciones previas. Se recomienda verificar manualmente en un Codespace real.

## Extensiones potencialmente ausentes

Dado que no se puede ejecutar VS Code aquí, no se detectaron extensiones faltantes desde el contenedor. Sin embargo, cualquier fallo en `onCreateCommand` podría impedir la instalación de dependencias críticas para la extensión de testing (`littlefoxteam.vscode-python-test-adapter`). Conviene revisar los registros del Codespace para confirmar que todas las extensiones se instalan correctamente.
