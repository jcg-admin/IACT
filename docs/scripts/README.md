# Documentación de scripts (estado real)

Este resumen reemplaza la descripción aspiracional previa y refleja únicamente los scripts presentes en el repositorio.

## Directorios principales
- **`scripts/ci/`**: gates de calidad (`gate-no-emojis.sh`, `gate-docs-structure.sh`, `run-all-checks.sh`, `run_architecture_analysis.py`).
- **`scripts/validation/`**: validaciones automáticas (calidad, seguridad, documentación). Incluye subdirectorios `quality/`, `compliance/`, `security/` y `docs/`.
- **`scripts/validacion/`**: generación anterior en español. Los scripts siguen operativos y están en proceso de migración a `validation/`.
- **`scripts/infrastructure/`**: soporte para entornos (cassandra, logging, disaster recovery, wasi, etc.).
- **`scripts/templates/`**: plantillas para crear nuevos scripts (`bash`, bibliotecas compartidas, etc.).
- **`scripts/run_all_tests.sh`**: orquestador para ejecutar validaciones encadenadas.

## Qué quedó fuera
- No existen scripts como `scripts/sdlc_agent.py`, `scripts/dora_metrics.py` ni `scripts/requisitos/*`.
- Cualquier referencia a `scripts/ai/agents/` corresponde a un diseño futuro y se mantiene archivada en `docs/anexos/`.

## Cómo colaborar
1. Añade documentación en este directorio cada vez que se cree o modifique un script relevante.
2. Marca con “automatización pendiente” cualquier sección que describa procesos manuales.
3. Asegura que los ejemplos de uso correspondan a archivos reales y con permisos de ejecución (`chmod +x`).
