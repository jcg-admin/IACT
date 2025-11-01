---
id: DOC-DEVOPS-INDEX
estado: borrador
propietario: equipo-devops
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-ARQ-INDEX", "DOC-QA-001"]
---
# DevOps

Centraliza runbooks, bitácoras y lineamientos operativos para mantener los entornos del monolito modular. Conecta las decisiones técnicas con procedimientos repetibles.

## Página padre
- [`../index.md`](../index.md)

## Páginas hijas
- [`contenedores_devcontainer.md`](contenedores_devcontainer.md)
- [`runbooks/`](runbooks/)

## Información clave
### Artefactos disponibles
- Runbooks (`runbooks/`).
- Guías de contenedores (`contenedores_devcontainer.md`).
- Bitácora de ejecución (pendiente, crear `bitacora.md`).

### Integraciones operativas
- Sincroniza despliegues con [`../planificacion_y_releases/readme.md`](../planificacion_y_releases/readme.md).
- Comparte evidencias de pruebas técnicas con [`../qa/estrategia_qa.md`](../qa/estrategia_qa.md).
- Consume lineamientos de [`../arquitectura/readme.md`](../arquitectura/readme.md) para asegurar consistencia técnica.

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio DevOps | Sí | Este archivo replica la jerarquía y metadatos oficiales. |
| Catálogo de runbooks operativos | Parcial | Directorio [`runbooks/`](runbooks/) con guías iniciales; falta índice maestro. |
| Guía de entornos de desarrollo | Sí | Documentada en [`contenedores_devcontainer.md`](contenedores_devcontainer.md). |
| Bitácora operativa consolidada | No | Debe crearse `bitacora.md` para registrar ejecuciones y SLAs. |

## Acciones prioritarias
- [ ] Documentar procedimientos de recuperación y monitoreo.
- [ ] Crear un índice de runbooks con propietarios y SLAs.
- [ ] Sincronizar evidencias de despliegue con QA y Planificación (`../planificacion_y_releases/readme.md`, `../qa/estrategia_qa.md`).
