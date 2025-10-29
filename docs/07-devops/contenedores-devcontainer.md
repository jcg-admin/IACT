---
id: DOC-OPS-001
estado: borrador
propietario: equipo-devops
ultima_actualizacion: 2025-02-14
relacionados: ["ADR-2025-001"]
---
# Guía rápida de evaluación de Dev Container

## Hallazgos principales
- `workspaceFolder` configurado como `/workspace/callcentersite` no coincide con el repositorio (`/workspace/IACT---project`).
- Hooks `onCreateCommand` esperan `requirements/dev.txt` y `requirements/test.txt` inexistentes en la raíz; solo hay `requirements.txt` y `requirements-test.txt`.
- La imagen base carece de `postgresql-client`, provocando fallos en `pg_isready` durante `postStartCommand`.
- El flujo depende de Docker Compose, contrario a la política que exige Vagrant + Apache + APScheduler.

## Recomendaciones
1. Ajustar rutas al árbol real (`api/requirements/`) o crear los archivos faltantes.
2. Homologar `workspaceFolder` con la raíz del repositorio y validar comandos con `python manage.py` desde `api/`.
3. Documentar por qué el proyecto prioriza Vagrant y cómo reproducir la infraestructura sin Docker.

## Verificación sugerida
- Confirmar instalación de extensiones críticas (`ms-python.python`, `batisteo.vscode-django`, `charliermarsh.ruff`).
- Ejecutar `pip install -r api/requirements/dev.txt` y `pip install -r api/requirements/test.txt` tras ajustar rutas.
- Reconstruir el contenedor y revisar logs de `postCreateCommand` antes de adoptar cambios.

## Parámetros de Dev Container
- **Feature Node.js**: configurado en `.devcontainer/devcontainer.json` con `version: "22"` y `npm: "10"` para garantizar compatibilidad con GitHub Copilot CLI.
- **DEVCONTAINER_INSTALL_COPILOT_CLI**: controla la instalación automática de `@github/copilot`; por defecto es `1` (habilitado). Establecerlo en `0` omite el paso.
- **DEVCONTAINER_RUN_TESTS**: define si se ejecutan pruebas de humo con `pytest` al finalizar el `postCreate`; el valor por defecto es `1` (se ejecutan). Cambiarlo a `0` salta las pruebas iniciales.
