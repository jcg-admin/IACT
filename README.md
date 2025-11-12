# Call Center Analytics

Repositorio monolítico para la plataforma de analítica de centros de contacto (IACT). El proyecto se encuentra en fase de consolidación documental: la mayor parte del trabajo actual vive en `docs/` y en los scripts de automatización que acompañan la migración.

## Estado actual del repositorio
- **Documentación activa**: se centraliza en [`docs/index.md`](docs/index.md).
- **Scripts utilitarios**: viven en [`scripts/`](scripts/README.md) y cubren validaciones, gates de CI y herramientas de soporte.
- **Infraestructura CPython**: disponible en [`infrastructure/cpython/`](infrastructure/cpython/README.md) para construir e instalar intérpretes precompilados.
- **Registros temporales**: se almacenan en [`logs_data/`](logs_data/README.md).
- **Histórico**: contenido legado preservado en [`respaldo/docs_legacy/`](respaldo/docs_legacy/README.md).
- **No existe un Makefile en la raíz**; cualquier instrucción previa que invoque `make` debe reinterpretarse usando los scripts disponibles.

## Primeros pasos
1. Clona el repositorio y activa un entorno virtual si trabajarás con herramientas Python opcionales.
2. Instala dependencias de soporte para documentación si es necesario: `pip install -r docs/requirements.txt` (archivo opcional, revisar README correspondiente).
3. Revisa el [plan de remediación activo](docs/plans/REV_20251112_remediation_plan.md) para entender el estado del trabajo.
4. Navega el índice consolidado para ubicar la documentación relevante.

## Verificación manual de servicios
- La guía vigente se encuentra en [`docs/operaciones/verificar_servicios.md`](docs/operaciones/verificar_servicios.md).
- Actualmente **no existe** `./scripts/verificar_servicios.sh`. Sigue los pasos manuales descritos en el runbook para validar PostgreSQL y MariaDB.

## Infraestructura CPython
Los scripts disponibles dentro de `infrastructure/cpython/scripts/` son:

| Script | Descripción | Ejemplo |
| --- | --- | --- |
| `build_cpython.sh` | Compila CPython dentro de la VM o desde el host. | `./infrastructure/cpython/scripts/build_cpython.sh 3.12.6` |
| `validate_build.sh` | Verifica la integridad del artefacto generado (`.tgz` + `.sha256`). | `./infrastructure/cpython/scripts/validate_build.sh cpython-3.12.6-ubuntu20.04-build1.tgz` |
| `install_prebuilt_cpython.sh` | Instala un artefacto precompilado existente en un destino (`INSTALLPREFIX`). | `VERSION=3.12.6 INSTALLPREFIX=/opt/python ./infrastructure/cpython/scripts/install_prebuilt_cpython.sh` |

Consulta [`docs/infrastructure/README.md`](docs/infrastructure/README.md) y [`docs/infrastructure/CHANGELOG-cpython.md`](docs/infrastructure/CHANGELOG-cpython.md) para conocer más detalles sobre estos flujos.

## Calidad y contribución
1. Ejecuta las validaciones disponibles antes de abrir un PR:
   ```bash
   # Tests unitarios disponibles
   pytest -c docs/pytest.ini docs/testing

   # Ejecuta validaciones de shell y gates en cascada
   ./scripts/run_all_tests.sh --skip-frontend --skip-security
   ```
2. Mantén la cobertura mínima del 80% para los módulos Python modificados.
3. Sigue TDD (Red → Green → Refactor) y registra commits en formato Conventional Commits.
4. Evita `git push --no-verify`. Si un hook falla, corrige la causa o ajusta la regla correspondiente; documenta cualquier excepción justificada en tu PR.

## Estructura de carpetas relevante
| Carpeta | Propósito |
| --- | --- |
| `docs/` | Documentación vigente, análisis y guías (ver índice consolidado). |
| `scripts/` | Scripts de validación, CI y utilidades operativas. |
| `infrastructure/` | Artefactos y herramientas de soporte (ej. builder de CPython). |
| `logs_data/` | JSON temporales y reportes generados manualmente. |
| `respaldo/` | Documentación histórica etiquetada como legado. |

## Recursos adicionales
- [Índice general de documentación](docs/index.md)
- [Guía de planes y seguimiento](docs/plans/)
- [Estrategia de git hooks](docs/ESTRATEGIA_GIT_HOOKS.md)
- [Análisis de reorganización de scripts](docs/ANALISIS_REORGANIZACION_SCRIPTS.md)
- [Guía de estilo](docs/gobernanza/GUIA_ESTILO.md)

Para dudas específicas consulta el directorio correspondiente en `docs/` o registra la pregunta en el backlog del proyecto.
