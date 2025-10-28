# Informe de validación de `.devcontainer`

## 1. Validar build inicial de `.devcontainer`
- `workspaceFolder` apunta a `/workspace/callcentersite`, pero el repositorio actual utiliza `/workspace/api`, lo que impediría abrir el workspace correcto al iniciar el contenedor.
- `onCreateCommand` intenta instalar `requirements/dev.txt` y `requirements/test.txt` en la raíz del repo, pero los archivos reales viven en `api/requirements/`. Esto provocaría fallos en la construcción inicial.
- El `Dockerfile` copia `callcentersite/requirements/base.txt`, ruta que no existe; los requirements se ubican en `api/requirements/base.txt`.

## 2. Comprobar comandos `postCreateCommand` y `postStartCommand`
- `postCreateCommand.copy-env` intenta copiar `.env` en la raíz, pero el proyecto espera la configuración dentro de `api/`. El comando fallaría porque `.env.example` tampoco existe en la raíz.
- Los comandos `postStartCommand` (migraciones, `collectstatic`, `check`) se ejecutan como `python manage.py ...`, pero el archivo `manage.py` está dentro de `api/`; al ejecutarse desde `/workspace/callcentersite` fallarían con `python: can't open file 'manage.py'`.
- `postStartCommand.wait-db` y la configuración de `docker-compose` asumen servicios PostgreSQL/MariaDB, pero la política del proyecto especifica Vagrant y Apache + mod_wsgi; la dependencia en Docker contradice las restricciones.

## 3. Ejecutar pruebas dentro del Dev Container
- `pip install -r requirements.txt` instala dependencias correctamente, pero `pip install -r requirements-test.txt` falla por restricciones de red externas (`ProxyError: Tunnel connection failed: 403`).
- `pytest` se ejecuta pero no descubre tests (`collected 0 items`).

## 4. Verificar extensiones/editor settings
- La sección `customizations.codespaces` y `customizations.vscode` apunta a abrir `callcentersite/settings.py`, archivo inexistente en la ruta esperada. Extensiones y configuraciones no se pueden validar fuera de Codespaces, pero las rutas definidas son inconsistentes con la estructura del proyecto.

## 5. Probar servicios auxiliares dentro del contenedor
- `docker-compose.yml` intenta levantar PostgreSQL y MariaDB dentro del Dev Container, pero el proyecto opera con Vagrant + Apache según las políticas. La capa Docker no está alineada con la infraestructura requerida y no puede probarse en este entorno sin contravenir las restricciones.

## Ubicación sugerida para pruebas automatizadas
Para seguir TDD y mantener la estructura modular, se recomienda:
- Añadir un paquete `tests` por aplicación Django bajo `api/<app>/tests/` con archivos `test_*.py`.
- Para pruebas de integración comunes, crear `api/tests/` en la raíz del proyecto Django y configurar `pytest.ini`/`conftest.py` para descubrimiento automático.

Esta estructura respeta las convenciones de Django + Pytest y facilita alcanzar la cobertura mínima del 80 %. 
