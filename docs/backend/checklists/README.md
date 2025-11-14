---
id: DOC-CHECKLISTS-BACKEND
estado: borrador
propietario: equipo-qa
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-QA-001", "DOC-ARQ-BACKEND"]
date: 2025-11-13
---
# Checklists del backend

Listas de verificación para validar entregables clave del backend dentro del SDLC. Cada checklist debe asociarse a un espacio principal y actualizarse conforme evolucione el proceso.

## Página padre
- [`../README.md`](../README.md)

## Páginas hijas
- [`checklist_desarrollo.md`](checklist_desarrollo.md)
- [`checklist_testing.md`](checklist_testing.md)
- [`checklist_trazabilidad_requisitos.md`](checklist_trazabilidad_requisitos.md)

## Información clave
### Recursos disponibles
- `checklist_desarrollo.md`
- `checklist_testing.md`
- `checklist_trazabilidad_requisitos.md`

### Recomendaciones
- Mantener responsables y fechas de revisión en el front matter de cada checklist.
- Referenciar estos artefactos desde [`../gobernanza/README.md`](../gobernanza/README.md) al preparar ceremonias del backend.
- Registrar el control documental transversal en [`../../infrastructure/checklists/checklist_cambios_documentales.md`](../../infrastructure/checklists/checklist_cambios_documentales.md).

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada del espacio de checklists | Sí | Este archivo mantiene la jerarquía y metadatos requeridos. |
| Checklist de desarrollo | Sí | Disponible en [`checklist_desarrollo.md`](checklist_desarrollo.md). |
| Checklist de pruebas | Sí | Registrado en [`checklist_testing.md`](checklist_testing.md). |
| Checklist de trazabilidad de requisitos | Sí | Disponible en [`checklist_trazabilidad_requisitos.md`](checklist_trazabilidad_requisitos.md). |
| Registro de owners y fechas de vigencia | No | Falta consolidar inventario con responsables y última revisión. |

## Acciones prioritarias
- [ ] Crear inventario maestro con owners y fechas de revisión de cada checklist.
- [ ] Definir cadencia de auditoría para medir cumplimiento y actualizar métricas en QA.
- [ ] Conectar cada checklist con los rituales documentados en Gobernanza.
