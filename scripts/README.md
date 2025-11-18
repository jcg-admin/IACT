# Inventario real de scripts (2025-11-12)

Este README refleja la estructura **existente** de `scripts/` después de la revisión documental. Cualquier referencia anterior a `scripts/requisitos/` u otras carpetas inexistentes debe considerarse obsoleta.

## Estructura actual
```
scripts/
├── benchmarks/                ← Scripts de mediciones puntuales
├── ci/                        ← Gates y validaciones de CI
├── cli/                       ← Utilidades de línea de comandos
├── coding/                    ← Experimentos y soporte para AI copilots
├── examples/                  ← Ejemplos de automatizaciones
├── guides/                    ← Guías de operación de scripts
├── infrastructure/            ← Herramientas de infraestructura (cassandra, wasi, etc.)
├── lib/                       ← Librerías auxiliares reutilizables
├── templates/                 ← Plantillas para nuevos scripts
├── validation/                ← Validaciones automatizadas (nomenclatura en inglés)
├── validacion/                ← Validaciones heredadas (nomenclatura en español)
├── workflows/                 ← Automatizaciones compuestas
└── run_all_tests.sh           ← Orquestador de validaciones (ver sección dedicada)
```

## Directorios destacados
- **ci/**: contiene gates como `gate-no-emojis.sh`, `gate-docs-structure.sh`, `run-all-checks.sh` y scripts Python para evaluar calidad (`evaluate_quality_score.py`).
- **validation/**: alberga verificaciones automáticas (calidad, seguridad, cumplimiento). Reemplaza gradualmente a `validacion/`.
- **validacion/**: versión anterior en español; los scripts siguen operativos y se están migrando progresivamente.
- **infrastructure/**: scripts relacionados con entornos (dev, benchmarking, logging, disaster recovery, wasi, cassandra).
- **templates/**: plantillas para crear nuevos scripts (`bash`, bibliotecas compartidas, etc.).

## Scripts importantes
- `run_all_tests.sh`: ejecuta validaciones encadenadas (backend, UI, seguridad y restricciones). Revisa el propio script para conocer flags como `--skip-frontend` o `--skip-security`.
- `ci/run-all-checks.sh`: combina gates individuales en una sola ejecución.
- `ci/run_architecture_analysis.py`: analiza el estado arquitectónico utilizando los reportes disponibles.
- `validation/docs/`: contiene verificaciones específicas para estructura documental.

## Buenas prácticas
1. Documenta cualquier script nuevo dentro de `docs/scripts/`.
2. Usa las plantillas de `templates/` para mantener consistencia.
3. Cuando migres un script de `validacion/` a `validation/`, deja un enlace o aviso temporal para no perder trazabilidad.
4. Ejecuta `shellcheck` y `bash -n` antes de abrir un PR con cambios en scripts.
