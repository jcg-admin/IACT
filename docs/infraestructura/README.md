---
id: DOC-INFRA-INDEX
estado: borrador
propietario: equipo-infraestructura
ultima_actualizacion: 2025-02-20
relacionados: ["DOC-INDEX-GENERAL", "DOC-DEVOPS-INDEX"]
---
# Espacio de documentación - Infraestructura

Este espacio centraliza la documentación operativa y de diseño de la infraestructura que soporta el monolito modular del proyecto. Mantiene alineación con las prácticas de backend y frontend para facilitar la colaboración cruzada:

- `arquitectura`: topologías, diagramas de red y decisiones sobre plataformas de ejecución.
- `checklists`: listas de verificación para provisión, endurecimiento y revisiones operativas.
- `devops`: automatizaciones, pipelines de infraestructura como código y runbooks.
- `diseno_detallado`: definiciones técnicas de servicios compartidos, redes y almacenamiento.
- `planificacion_y_releases`: planes de evolución, ventanas de mantenimiento y bitácoras de cambios.
- `qa`: estrategias de validación, pruebas de resiliencia y métricas de observabilidad.
- `requisitos`: acuerdos de nivel de servicio, controles regulatorios y capacidades esperadas.
- `gobernanza`: políticas de seguridad, cumplimiento y estándares de operación.

Cada carpeta ofrece un README inicial listo para documentar los artefactos correspondientes.

## Recursos destacados recientes
- **CPython precompilado**: consulta el [pipeline y guía de DevContainer](cpython_precompilado/pipeline_devcontainer.md) para entender cómo se construye, publica y consume el intérprete optimizado.【F:docs/infrastructure/cpython_precompilado/pipeline_devcontainer.md†L1-L99】
- **Scripts oficiales**: `build_cpython.sh`, `validate_build.sh` e `install_prebuilt_cpython.sh` viven en `infrastructure/cpython/scripts/` y cuentan con pruebas en `infrastructure/cpython/tests/`.
- **Workspaces Hamilton**: la carpeta [`workspace`](workspace/README.md) concentra tanto el ejemplo `Data → Prompt → LLM → $` (`infrastructure/workspace/hamilton_llm/`) como el lenguaje de servidores (`infrastructure/workspace/dev_tools/language_server/hamilton_lsp/`), cada uno con sus pruebas (`infrastructure/workspace/tests/...`).

## Pipeline activo de infraestructura

Las automatizaciones CI/CD para infraestructura viven en `.github/workflows/infrastructure-ci.yml` y se disparan en cada `push` o `pull_request` a `main` y `develop`. El flujo incluye:

- **validate-shell-scripts**: ejecuta `shellcheck` sobre todos los `scripts/*.sh` y advierte sobre permisos de ejecución.
- **test-validation-scripts**: instala dependencias de `api/requirements.txt` y corre los validadores de seguridad/configuración sobre MySQL de servicio.
- **validate-terraform**: si existe `infrastructure/terraform`, aplica `terraform fmt`, `init`, `validate` y `tfsec`.
- **validate-docker**: lint de `Dockerfile` y validación de `docker-compose` si están presentes en el repo.
- **validate-configurations**: verifica que todo YAML/JSON sea parseable y alerta sobre patrones típicos de secretos hardcodeados.
- **test-health-check**: levanta el servidor Django de pruebas apuntando a MySQL y comprueba el endpoint `/api/health`.

El job `summary` falla el pipeline si alguno de los pasos anteriores no supera las validaciones.【F:.github/workflows/infrastructure-ci.yml†L1-L176】【F:.github/workflows/infrastructure-ci.yml†L177-L247】
