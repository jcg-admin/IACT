---
id: DOC-REQ-BACKEND
estado: borrador
propietario: equipo-backend
ultima_actualizacion: 2025-02-18
relacionados: ["DOC-REQ-INDEX", "DOC-ARQ-BACKEND", "ADR-2025-001"]
---
# Requisitos del backend

Extiende la visión corporativa descrita en [`../../requisitos/readme.md`](../../requisitos/readme.md) con acuerdos específicos para servicios, integraciones y contratos públicos del backend.

## Página padre
- [`../readme.md`](../readme.md)

## Relación con otros espacios
- Arquitectura técnica: [`../arquitectura/readme.md`](../arquitectura/readme.md)
- Diseño detallado: [`../diseno_detallado/readme.md`](../diseno_detallado/readme.md)
- Gobernanza operativa: [`../../infrastructure/gobernanza/readme.md`](../../infrastructure/gobernanza/readme.md)

## Alcance
- **Servicios expuestos.** Requisitos sobre endpoints REST, eventos y tareas batch.
- **Integraciones internas.** Dependencias con módulos compartidos y orquestadores.
- **Restricciones no funcionales.** SLAs, observabilidad y políticas de seguridad aplicables al backend.

## Artefactos reutilizados
- Plantilla corporativa: [`../../requisitos/rq_plantilla.md`](../../requisitos/rq_plantilla.md)
- Matriz de trazabilidad global: [`../../requisitos/trazabilidad.md`](../../requisitos/trazabilidad.md)
- Registro de releases: [`../../infrastructure/planificacion_y_releases/readme.md`](../../infrastructure/planificacion_y_releases/readme.md)

## Próximos pasos
- [ ] Definir catálogo de requisitos pendientes del backend priorizado por valor de negocio.
- [ ] Mapear requisitos no funcionales críticos (latencia, observabilidad, resiliencia).
- [ ] Alinear dependencias con QA para asegurar cobertura de pruebas automatizadas.
