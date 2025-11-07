---
id: DOC-INDEX-GENERAL
estado: activo
propietario: equipo-documentacion
ultima_actualizacion: 2025-11-06
version: 4.0
estandares: ["ISO/IEC/IEEE 29148:2018", "BABOK v3", "PMBOK 7th Ed"]
---
# Indice de Documentacion - IACT Project

Sistema de documentacion del proyecto IACT (IVR Analytics & Customer Tracking) organizado segun ISO/IEC/IEEE 29148:2018.

## Pagina padre
- [README Principal](../README.md)

## Estructura de Documentacion v4.0

### Requisitos (ISO 29148)
- [Requisitos - Indices Auto-generados](requisitos/README.md)
  - BRS (Business Requirements Specification)
  - StRS (Stakeholder Requirements Specification)
  - SRS (Software Requirements Specification)
  - RTM (Requirements Traceability Matrix)

### Implementacion por Dominio
- [Implementacion](implementacion/README.md)
  - [Backend](backend/README.md) - Requisitos, arquitectura, diseno
  - [Frontend](frontend/README.md) - Requisitos, arquitectura, diseno
  - [Infrastructure](infrastructure/README.md) - Requisitos, arquitectura, diseno

### Decisiones de Arquitectura
- [ADRs (Architecture Decision Records)](adr/) - 14 ADRs documentados

### Infraestructura
- [Infraestructura](infraestructura/README.md)
  - [CPython Precompilado](infrastructure/cpython_precompilado/README.md)

### Gobernanza y Plantillas
- [Plantillas](plantillas/) - Templates para requisitos
- [Arquitectura](arquitectura/) - Guias y lineamientos

### Anexos y Referencias
- [Anexos](anexos/) - Glosarios, FAQs, analisis
- [Especificaciones](specs/) - Especificaciones tecnicas
- [Planes](plans/) - Planes de implementacion

## Convenciones

### Organizacion por Dominio
El proyecto sigue ADR_010 (Organizacion por Dominio):
- Codigo por dominio: `/api/`, `/ui/`, `/infrastructure/`
- Documentacion de implementacion: `docs/implementacion/{dominio}/`
- Requisitos co-localizados con codigo

### Nomenclatura
- Archivos README: Siempre `README.md` (mayusculas)
- Documentos markdown: `nombre_descriptivo.md` o `nombre-descriptivo.md`
- Sin emojis en ningun archivo (restriccion IACT)

### Requisitos (ISO 29148)
- **Source of truth**: `docs/implementacion/{dominio}/requisitos/`
- **Indices auto-generados**: `docs/requisitos/` (NO editar manualmente)
- **Conformidad**: Full ISO/IEC/IEEE 29148:2018
- **Generacion**: Script Python `scripts/requisitos/generate_requirements_index.py`

## Uso con MkDocs

La configuracion `mkdocs.yml` apunta a este directorio como `docs_dir`. Para ver la documentacion:

```bash
./ver_documentacion.sh
```

## Estado de Conformidad ISO 29148

| Clausula ISO 29148 | Estado | Evidencia |
|-------------------|--------|-----------|
| 4.2 Full Conformance | COMPLETO | Indices BRS, StRS, SRS generados |
| 5.2.8 Traceability | COMPLETO | RTM con trazabilidad bidireccional |
| 6.2 Business Analysis | COMPLETO | 3 Necesidades documentadas |
| 6.3 Stakeholder Needs | COMPLETO | 4 Requisitos stakeholder |
| 9.3-9.6 Information Items | COMPLETO | BRS, StRS, SRS generados |

Total requisitos rastreados: 36
- Necesidades (N-XXX): 3
- Requisitos Negocio (RN-XXX): 3
- Stakeholder (RS-XXX): 4
- Funcionales (RF-XXX): 18
- No Funcionales (RNF-XXX): 8

## Acciones Prioritarias

- [ ] Verificar indices ISO 29148 actualizados mensualmente
- [ ] Revisar ADRs cuando se tomen decisiones arquitectonicas
- [ ] Mantener requisitos sincronizados con codigo
- [ ] Actualizar MkDocs navigation cuando se agreguen secciones

## Referencias

- **BABOK v3**: Business Analysis Body of Knowledge
- **PMBOK 7th Ed**: Project Management Body of Knowledge
- **ISO/IEC/IEEE 29148:2018**: Requirements engineering
- **ADR_010**: Organizacion del Proyecto por Dominio
