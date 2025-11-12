# docs_legacy/ - Estructura Documental Archivada

**Fecha de archivo**: 2025-11-06
**Razón**: Reorganización según BABOK v3 + PMBOK 7 + ISO/IEC/IEEE 29148:2018

---

## ⚠️ AVISO IMPORTANTE

Este directorio contiene la **estructura documental ANTIGUA** del proyecto IACT que fue archivada el 2025-11-06.

**NO EDITAR** archivos en este directorio. Es solo para referencia histórica.

---

## ¿Por qué fue archivada?

### Problemas de la Estructura Antigua

1. **40% de duplicación**: Directorios devops/, qa/, checklists/ repetidos en múltiples lugares
2. **Requisitos centralizados**: Todos en `docs/` en lugar de co-localizados con código
3. **Búsqueda lenta**: 10-15 minutos para encontrar un requisito
4. **Sin trazabilidad**: Requisitos sin relación clara con necesidades de negocio
5. **ADRs duplicados**: Dos ubicaciones diferentes (`docs/adr/` y `docs/arquitectura/adr/`)

### Nueva estructura planificada vs realidad

La reorganización planeada (estructura “v4.0”) no se completó. La documentación activa se mantiene en `docs/` y los requisitos continúan distribuidos en varios análisis dentro de `docs/backend_analisis/` y `docs/analisis/`.

Consulta [`../docs/README.md`](../docs/README.md) para conocer la estructura vigente.

---

## Contenido Archivado

### Directorios Principales

| Directorio | Descripción | Nueva Ubicación |
|------------|-------------|-----------------|
| `solicitudes/` | SC00, SC01, SC02, SC03 | Pendiente clasificar como Business Needs |
| `checklists/` | Checklists de desarrollo, testing, etc. | Pendiente migrar a `implementacion/*/qa/` |
| `devops/` | Runbooks, guías DevOps | Pendiente migrar a `implementacion/infrastructure/` |
| `qa/` | Estrategia QA, registros | Pendiente migrar a `implementacion/*/qa/` |
| `gobernanza/` | Políticas, procesos, guías | Pendiente migrar selectivamente |
| `plantillas/` | Templates de documentos | Pendiente revisar y migrar útiles |
| `desarrollo/` | Metodologías, workflows | Pendiente migrar a docs/ o implementacion/ |
| `legacy_analysis/` | Análisis de estructuras antiguas | Archivado permanentemente |
| `vision_y_alcance/` | Visión del proyecto | Pendiente migrar a docs/ |
| `planificacion_y_releases/` | Planificación | Pendiente migrar a docs/ |
| `procedimientos/` | Procedimientos operativos | Pendiente migrar según dominio |
| `diseno_detallado/` | Diseños técnicos | Pendiente migrar a `implementacion/*/diseno/` |

---

## Cómo Buscar Contenido Antiguo

### Buscar por palabra clave

```bash
# Buscar en toda la estructura archivada
grep -r "palabra_clave" docs_legacy/

# Buscar solo en solicitudes
grep -r "palabra_clave" docs_legacy/solicitudes/

# Buscar archivos por nombre
find docs_legacy/ -name "*palabra*.md"
```

### Solicitudes Específicas

```bash
# SC00
cd docs_legacy/solicitudes/sc00/

# SC01
cd docs_legacy/solicitudes/sc01/

# SC02
cd docs_legacy/solicitudes/sc02/
```

---

## Migración Futura (Pendiente)

### FASE 2-3: Clasificar y Migrar Contenido

**Prioridad Alta**:
- [ ] Clasificar solicitudes (SC00, SC01, SC02) como Business Needs
- [ ] Migrar Business Needs a `implementacion/backend/requisitos/necesidades/`
- [ ] Migrar plantillas útiles a estructura nueva

**Prioridad Media**:
- [ ] Migrar checklists por dominio
- [ ] Migrar runbooks a implementacion/infrastructure/
- [ ] Migrar estrategia QA

**Prioridad Baja**:
- [ ] Revisar gobernanza y migrar selectivamente
- [ ] Archivar permanentemente análisis antiguos (legacy_analysis/)

---

## Enlaces Útiles

- **Nueva estructura**: [`../docs/README.md`](../docs/README.md)
- **Propuesta original**: [`../docs/anexos/analisis_nov_2025/PROPUESTA_FINAL_REESTRUCTURACION.md`](../docs/anexos/analisis_nov_2025/PROPUESTA_FINAL_REESTRUCTURACION.md)
- **ADRs consolidados**: [`../docs/adr/`](../docs/adr/)
- **Specs actuales**: [`../docs/specs/`](../docs/specs/)

---

## Preguntas Frecuentes

### ¿Puedo editar archivos aquí?

**NO**. Este directorio es solo para referencia. Editar aquí NO afectará el proyecto.

### ¿Dónde creo nuevos documentos?

Ver guía en: [`../docs/README.md`](../docs/README.md)

- Requisitos → `implementacion/*/requisitos/`
- ADRs → `docs/adr/`
- Specs → `docs/specs/`

### ¿Cuánto tiempo se mantendrá este archivo?

**3 meses** (hasta 2026-02-06) como read-only para referencia, luego se evaluará eliminación permanente.

### ¿Cómo recupero un documento archivado?

1. Identificar el archivo en `docs_legacy/`
2. Copiar a nueva ubicación apropiada
3. Actualizar formato si es necesario
4. Commit en nueva ubicación

---

## Contacto

Para preguntas sobre:
- **Migración de contenido**: BA Lead
- **Estructura nueva**: Tech Lead + Arquitecto
- **Acceso a archivos archivados**: PMO

---

**Fecha de archivo**: 2025-11-06
**Última revisión**: 2025-11-06
**Estado**: Archivado permanentemente (read-only)
