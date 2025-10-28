# Evaluación de `.devcontainer/devcontainer.json`

## Resumen del archivo
- Contenedor: `CallCenter Django (Prebuild)` basado en Docker Compose (`docker-compose.yml`) con servicio principal `app` y carpeta de trabajo `/workspace/callcentersite`.
- Requisitos declarados: 2 CPU, 4 GB RAM y 32 GB de almacenamiento.
- Puertos reenviados: 8000 (Django, HTTP), 5432 (PostgreSQL, TCP con `requireLocalPort`), 3306 (MariaDB, TCP con `requireLocalPort`).
- Hooks configurados:
  - `updateContentCommand`: mensaje informativo.
  - `onCreateCommand`: instalaciones mediante `pip install -r requirements/dev.txt` y `requirements/test.txt`, verificación de dependencias e impresión de mensaje final.
  - `postCreateCommand`: configura Git seguro, copia `.env` desde `.env.example` si no existe e imprime mensaje.
  - `postStartCommand`: espera a PostgreSQL, ejecuta migraciones, `collectstatic`, `check` y mensaje final.
  - `postAttachCommand`: muestra mensaje de bienvenida y estado de contenedores con `make ps` o `docker compose ps`.
- Personalizaciones de Codespaces/VS Code: apertura automática de archivos, extensiones para Python/Django/linting/testing/docker, configuraciones de terminal, Git, búsqueda, SQLTools y ajustes de interfaz.
- Features instaladas: `git` y `github-cli` desde `ghcr.io/devcontainers`.
- Variables de entorno remotas (`remoteEnv`): `LOCAL_WORKSPACE_FOLDER` y `CONTAINER_WORKSPACE_FOLDER`.
- Usuario remoto configurado como `django` sin ajustar UID.

## Observaciones detectadas
1. **Rutas de archivos de dependencias inexistentes**: el repositorio solo contiene `requirements.txt` y `requirements-test.txt`, pero los hooks `onCreateCommand.install-dev` y `.install-test` esperan `requirements/dev.txt` y `requirements/test.txt`. Esto provocaría un fallo (`pip install` con archivo inexistente) al crear el contenedor.
2. **Carpeta de trabajo inconsistente**: `workspaceFolder` apunta a `/workspace/callcentersite`, pero el repositorio montado es `/workspace/IACT---project`. Al no existir `callcentersite`, VS Code abriría una ruta inválida y los comandos posteriores (p. ej. `postCreateCommand.copy-env`, `postStartCommand.migrate-postgres`) fallarían por ejecutarse fuera del proyecto real.
3. **Dependencia de herramientas externas no presentes**: `postStartCommand.wait-db` invoca `pg_isready`, que requiere el cliente de PostgreSQL instalado en la imagen base. Si el contenedor base no incluye `postgresql-client`, el hook fallará.
4. **Requisitos de infraestructura incompatibles con lineamientos del proyecto**: el Dev Container se basa en Docker/Compose, pero las directrices del proyecto indican explícitamente usar Vagrant + Apache/mod_wsgi en lugar de Docker. Esto genera una discrepancia con la metodología esperada.

## Pasos pendientes imposibles de reproducir en este entorno
- El entorno de evaluación (sandbox) no permite ejecutar VS Code ni el comando "Dev Containers: Rebuild and Reopen in Container", por lo que no es posible observar la salida real del proceso de creación.
- Debido a la limitación anterior, tampoco se puede comprobar con `printenv` la presencia de las variables de entorno definidas en `remoteEnv`.

## Recomendaciones
- Ajustar las rutas de `requirements` para que coincidan con los archivos existentes (`requirements.txt` y `requirements-test.txt`) o crear la estructura esperada (`requirements/dev.txt`, etc.).
- Corregir `workspaceFolder` y cualquier ruta hardcodeada a `callcentersite` para que apunten al directorio real del repositorio.
- Verificar que la imagen base incluya `postgresql-client` o instalarlo en el Dockerfile para garantizar el funcionamiento de `pg_isready`.
- Evaluar la conveniencia de mantener el flujo basado en Docker frente a las restricciones del proyecto que exigen Vagrant + Apache/mod_wsgi.
- Intentar reconstruir el contenedor en un entorno con VS Code/Dev Containers habilitado para confirmar si existen otros fallos o warnings, y documentar la salida completa.
