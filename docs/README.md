# Documentación IACT - Estructura v4.0

**Fecha de reorganización**: 2025-11-06
**Basado en**: Propuesta BABOK v3 + PMBOK 7 + ISO/IEC/IEEE 29148:2018

---

## NUEVA ESTRUCTURA (Post-Reorganización)

### Principios de Organización

1. **Requisitos por dominio**: Los requisitos viven en `implementacion/*/requisitos/` co-localizados con el código
2. **Documentación técnica**: `docs/` contiene solo documentación transversal, specs, ADRs y arquitectura
3. **Source of truth único**: Sin duplicación, cada tipo de documento en UN solo lugar

---

## Estructura Actual

```
IACT---project/
│
├── implementacion/                         ← CÓDIGO + REQUISITOS (Source of Truth)
│   ├── backend/
│   │   ├── requisitos/
│   │   │   ├── necesidades/               Necesidades de negocio (N-001, N-002)
│   │   │   ├── negocio/                   Requisitos de negocio (RN-001)
│   │   │   ├── stakeholders/              Requisitos de stakeholders (RS-001)
│   │   │   ├── funcionales/               Requisitos funcionales (RF-001, RF-002)
│   │   │   └── no_funcionales/            Requisitos no funcionales (RNF-001)
│   │   ├── src/
│   │   └── tests/
│   │
│   ├── frontend/
│   │   ├── requisitos/
│   │   │   ├── _necesidades_vinculadas.md ← ENLACE (no duplica)
│   │   │   ├── stakeholders/
│   │   │   ├── funcionales/
│   │   │   └── no_funcionales/
│   │   └── src/
│   │
│   └── infrastructure/
│       ├── requisitos/
│       │   ├── _necesidades_vinculadas.md ← ENLACE (no duplica)
│       │   ├── funcionales/
│       │   └── no_funcionales/
│       └── cpython/                        Sistema CPython precompilado
│
├── docs/                                   ← DOCUMENTACIÓN TRANSVERSAL
│   ├── README.md                           Este archivo
│   ├── adr/                                Architecture Decision Records (consolidado)
│   │   ├── ADR_008-cpython-features-vs-imagen-base.md
│   │   ├── ADR_009-distribucion-artefactos-strategy.md
│   │   ├── ADR_010-organizacion-proyecto-por-dominio.md
│   │   ├── adr_2025_001_vagrant_mod_wsgi.md
│   │   └── adr_2025_002_suite_calidad_codigo.md
│   │
│   ├── specs/                              Especificaciones técnicas
│   │   └── SPEC_INFRA_001-cpython_precompilado.md
│   │
│   ├── arquitectura/                       Arquitectura del sistema
│   │   └── lineamientos_codigo.md
│   │
│   ├── infraestructura/                    Documentación de infraestructura
│   │   └── cpython_precompilado/
│   │
│   ├── requisitos/                         ÍNDICES ISO 29148 (auto-generados en futuro)
│   │
│   ├── anexos/                             Material de referencia
│   │   └── analisis_nov_2025/              Análisis y propuestas archivadas
│   │
│   └── plans/                              Planes de implementación
│
├── docs_legacy/                            ← ESTRUCTURA ANTIGUA (ARCHIVADA 2025-11-06)
│   ├── solicitudes/                        SC00, SC01, SC02 (pendiente clasificar)
│   ├── checklists/
│   ├── gobernanza/
│   ├── qa/
│   ├── devops/
│   └── [otros archivados]
│
└── api/                                    Código de la API (futuro)
    └── [pendiente]
```

---

## Dónde Encontrar Cada Cosa

### Requisitos

| Tipo de Requisito | Ubicación | Owner |
|-------------------|-----------|-------|
| Necesidades de negocio (N-XXX) | `implementacion/backend/requisitos/necesidades/` | BA Lead + PMO |
| Requisitos de negocio (RN-XXX) | `implementacion/{dominio}/requisitos/negocio/` | Cada equipo |
| Requisitos stakeholders (RS-XXX) | `implementacion/{dominio}/requisitos/stakeholders/` | Cada equipo |
| Requisitos funcionales (RF-XXX) | `implementacion/{dominio}/requisitos/funcionales/` | Cada equipo |
| Requisitos no funcionales (RNF-XXX) | `implementacion/{dominio}/requisitos/no_funcionales/` | Cada equipo |

### Documentación Técnica

| Tipo de Documento | Ubicación | Descripción |
|-------------------|-----------|-------------|
| ADRs | `docs/adr/` | Decisiones arquitecturales (consolidado) |
| Specs | `docs/specs/` | Especificaciones técnicas detalladas |
| Arquitectura | `docs/arquitectura/` | Guías y lineamientos de arquitectura |
| Infraestructura | `docs/infraestructura/` | Documentación de infra (CPython, etc.) |
| Planes | `docs/plans/` | Planes de implementación generados |

### Estructura Archivada

| Tipo | Ubicación | Fecha |
|------|-----------|-------|
| Docs antigua | `docs_legacy/` | Archivado 2025-11-06 |
| Análisis | `docs/anexos/analisis_nov_2025/` | Propuestas y análisis |

---

## Cambios Respecto a Estructura Anterior

### COMPLETADO: Mejoras Implementadas

1. **Requisitos co-localizados con código**: Ya no están en `docs/` sino en `implementacion/`
2. **ADRs consolidados**: Un solo directorio `docs/adr/` en lugar de 2
3. **Eliminada duplicación**: Sin directorios devops/, qa/, checklists/ duplicados en múltiples lugares
4. **Estructura archivada**: Antigua estructura preservada en `docs_legacy/` para referencia

### ELIMINADO: Eliminado/Archivado

- `docs/implementacion/` → movido a `implementacion/` (raíz)
- `docs/solicitudes/` → archivado en `docs_legacy/solicitudes/`
- `docs/devops/`, `docs/qa/`, `docs/checklists/` → archivado
- `docs/arquitectura/adr/` → consolidado en `docs/adr/`

---

## Navegación Rápida

### Desarrolladores

```bash
# Ver requisitos funcionales de backend
cd implementacion/backend/requisitos/funcionales/

# Ver decisiones arquitecturales
cd docs/adr/

# Ver especificaciones técnicas
cd docs/specs/
```

### Business Analysts

```bash
# Ver necesidades de negocio
cd implementacion/backend/requisitos/necesidades/

# Ver requisitos de stakeholders
cd implementacion/{backend,frontend,infrastructure}/requisitos/stakeholders/
```

### Arquitectos

```bash
# Ver ADRs
cd docs/adr/

# Ver guías de arquitectura
cd docs/arquitectura/
```

---

## Próximos Pasos (Pendiente)

### FASE 2-3: Migración de Contenido (Futuro)

- [ ] Clasificar `docs_legacy/solicitudes/` → ¿Son Business Needs?
- [ ] Migrar solicitudes a `implementacion/backend/requisitos/necesidades/`
- [ ] Crear plantillas con frontmatter YAML
- [ ] Implementar workflows CI/CD para generación de índices ISO 29148

### FASE 4: Automatización (Futuro)

- [ ] Script `generate-requirements-index.js`
- [ ] Workflow `.github/workflows/requirements_index.yml`
- [ ] Auto-generar BRS, StRS, SyRS, SRS, RTM

---

## Referencias

- **Propuesta original**: `docs/anexos/analisis_nov_2025/PROPUESTA_FINAL_REESTRUCTURACION.md`
- **Análisis de duplicados**: `docs/anexos/analisis_nov_2025/REPORTE_DUPLICADOS.md`
- **Estándares**: BABOK v3, PMBOK 7, ISO/IEC/IEEE 29148:2018

---

## Uso con MkDocs

```bash
pip install -r docs/requirements.txt
mkdocs serve -f docs/mkdocs.yml
```

---

**Última actualización**: 2025-11-06
**Versión**: v4.0 (Post-Reorganización Fase 1)
