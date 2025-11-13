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
- **Workspace Hamilton LLM**: la carpeta [`workspace`](workspace/README.md) concentra el ejemplo `Data → Prompt → LLM → $` situado en `infrastructure/workspace/hamilton_llm/`, con pruebas asociadas en `infrastructure/workspace/tests/hamilton_llm/test_driver.py`.
