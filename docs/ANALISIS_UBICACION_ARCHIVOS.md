# 📍 UBICACIÓN CORRECTA DE ARCHIVOS DUPLICADOS

Según la estructura propuesta donde:
- **docs/ raíz**: Documentación GENERAL/TRANSVERSAL del proyecto
- **docs/implementacion/**: Documentación ESPECÍFICA de implementación por área

---

## 📋 Análisis por Archivo

### 1. checklist_desarrollo.md

**Naturaleza**: Checklist de desarrollo transversal

**Ubicación correcta**: `docs/checklists/checklist_desarrollo.md` ✅

**Razón**: 
- Es un checklist que aplica a TODO el desarrollo del proyecto
- Contiene reglas generales (output profesional, linters, tests)
- No es específico de backend, frontend o infrastructure
- La versión general (883 bytes) es más completa que el stub de backend (299 bytes)

**Acción**: 
- ✅ MANTENER: `docs/checklists/checklist_desarrollo.md`
- ❌ ELIMINAR: `docs/implementacion/backend/checklists/checklist_desarrollo.md`

---

### 2. checklist_testing.md

**Naturaleza**: Checklist de testing transversal

**Ubicación correcta**: `docs/checklists/checklist_testing.md` ✅

**Razón**:
- Aplica a tests de cualquier capa (backend, frontend, infrastructure)
- Es documentación general de QA

**Acción**:
- ✅ MANTENER: `docs/checklists/checklist_testing.md`
- ❌ ELIMINAR: `docs/implementacion/backend/checklists/checklist_testing.md` (idéntico)

---

### 3. checklist_trazabilidad_requisitos.md

**Naturaleza**: Checklist de trazabilidad transversal

**Ubicación correcta**: `docs/checklists/checklist_trazabilidad_requisitos.md` ✅

**Razón**:
- La trazabilidad de requisitos es un proceso general del proyecto
- Aplica a requisitos de cualquier área

**Acción**:
- ✅ MANTENER: `docs/checklists/checklist_trazabilidad_requisitos.md`
- ❌ ELIMINAR: `docs/implementacion/backend/checklists/checklist_trazabilidad_requisitos.md` (idéntico)

---

### 4. checklist_cambios_documentales.md

**Naturaleza**: Checklist de gobernanza documental

**Ubicación correcta**: `docs/checklists/checklist_cambios_documentales.md` ✅

**Razón**:
- Es un proceso de gobernanza que aplica a TODA la documentación
- No es específico de infrastructure

**Acción**:
- ✅ MANTENER: `docs/checklists/checklist_cambios_documentales.md`
- ❌ ELIMINAR: `docs/implementacion/infrastructure/checklists/checklist_cambios_documentales.md` (idéntico)

---

### 5. contenedores_devcontainer.md

**Naturaleza**: Documentación de infraestructura de desarrollo general

**Ubicación correcta**: `docs/devops/contenedores_devcontainer.md` ✅

**Razón**:
- Los devcontainers son configuración GENERAL del entorno de desarrollo
- Aplican a todo el proyecto (backend, frontend, infrastructure)
- No es documentación específica de implementación de infrastructure
- La versión general (8.5KB) es mucho más completa que el stub (1.9KB)

**Acción**:
- ✅ MANTENER: `docs/devops/contenedores_devcontainer.md`
- ❌ ELIMINAR: `docs/implementacion/infrastructure/devops/contenedores_devcontainer.md` (stub)

---

### 6. github_copilot_codespaces.md

**Naturaleza**: Runbook operativo de infraestructura de desarrollo

**Ubicación correcta**: `docs/devops/runbooks/github_copilot_codespaces.md` ⚠️

**Razón**:
- Es un runbook operativo que aplica al entorno general de desarrollo
- No es específico de la implementación de infrastructure como área

**PERO**: Las dos versiones tienen contenido diferente (9.5KB vs 13.6KB)

**Acción**:
- 🔍 REVISAR MANUALMENTE: Comparar ambas versiones para determinar cuál es más actual
- Luego mantener solo una en `docs/devops/runbooks/`
- Eliminar la versión en `docs/implementacion/infrastructure/`

---

### 7. lineamientos_codigo.md

**Naturaleza**: Lineamientos arquitectónicos generales

**Ubicación correcta**: `docs/arquitectura/lineamientos_codigo.md` ✅

**Razón**:
- Los lineamientos de código son TRANSVERSALES a todo el proyecto
- Aunque el backend tenga especificidades, la base debe ser general
- La versión general (11KB) es 18x más completa que el stub de backend (618 bytes)

**Acción**:
- ✅ MANTENER: `docs/arquitectura/lineamientos_codigo.md`
- ⚠️ OPCIONES para `docs/implementacion/backend/arquitectura/lineamientos_codigo.md`:
  - **Opción A**: Eliminar el stub
  - **Opción B**: Expandir con lineamientos ESPECÍFICOS de Django/Python (herencia del general)

**Recomendación**: Opción B - Expandir con:
```markdown
# Lineamientos de Código - Backend

Este documento extiende los [lineamientos generales](../../../arquitectura/lineamientos_codigo.md) con especificaciones para el backend Django.

## Herencia
Ver lineamientos base en: `docs/arquitectura/lineamientos_codigo.md`

## Específicos de Backend Django
- Convenciones de models.py
- Estructura de services.py
- Patrones de views y serializers
- etc.
```

---

### 8. lineamientos_gobernanza.md

**Naturaleza**: Lineamientos de gobernanza

**Ubicación correcta**: `docs/gobernanza/lineamientos_gobernanza.md` ⚠️

**Razón**:
- La gobernanza puede tener aspectos generales Y específicos por área
- Ambas versiones son pequeñas (358 vs 417 bytes) y diferentes

**Acción**:
- 🔍 REVISAR MANUALMENTE: Comparar contenido
- Si el contenido de infrastructure es un SUBSET del general → Eliminar versión de infrastructure
- Si el contenido de infrastructure tiene ESPECIFICIDADES → Mantener ambas con herencia clara

---

### 9. reprocesar_etl_fallido.md

**Naturaleza**: Runbook operativo

**Ubicación correcta**: `docs/devops/runbooks/reprocesar_etl_fallido.md` ✅

**Razón**:
- Los runbooks operativos deben estar CENTRALIZADOS en devops
- Aunque sea específico del ETL backend, el equipo de DevOps necesita acceso directo
- La versión general (9.6KB) es 8x más completa que el stub (1.2KB)

**Acción**:
- ✅ MANTENER: `docs/devops/runbooks/reprocesar_etl_fallido.md`
- ❌ ELIMINAR: `docs/implementacion/backend/devops/runbooks/reprocesar_etl_fallido.md` (stub)

**Nota**: Si el backend necesita documentación de diseño del ETL, eso va en `docs/implementacion/backend/diseno/` (no runbooks)

---

### 10. verificar_servicios.md

**Naturaleza**: Runbook operativo de verificación

**Ubicación correcta**: `docs/devops/runbooks/verificar_servicios.md` ✅

**Razón**:
- Runbook operativo transversal (verifica TODOS los servicios)
- Debe estar centralizado para el equipo de DevOps/SRE
- Versión general (7.5KB) es 7x más completa

**Acción**:
- ✅ MANTENER: `docs/devops/runbooks/verificar_servicios.md`
- ❌ ELIMINAR: `docs/implementacion/infrastructure/devops/runbooks/verificar_servicios.md` (stub)

---

### 11. post_create.md

**Naturaleza**: Runbook de inicialización de entorno

**Ubicación correcta**: `docs/devops/runbooks/post_create.md` ✅

**Razón**:
- Script de post-create aplica al entorno general de desarrollo
- No es específico de la implementación de infrastructure
- Versión general (8KB) es 8x más completa

**Acción**:
- ✅ MANTENER: `docs/devops/runbooks/post_create.md`
- ❌ ELIMINAR: `docs/implementacion/infrastructure/devops/runbooks/post_create.md` (stub)

---

### 12. adr_2025_001_vagrant_mod_wsgi.md

**Naturaleza**: ADR (Architecture Decision Record)

**Ubicación correcta**: `docs/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md` ✅

**Razón**:
- Los ADRs deben estar CENTRALIZADOS en un solo lugar
- Son decisiones arquitectónicas del PROYECTO, no de un área específica
- Aunque el ADR sea sobre Vagrant (infra), la decisión afecta a todo el proyecto
- Versión general (7.5KB) es 6x más completa

**Acción**:
- ✅ MANTENER: `docs/arquitectura/adr/`
- ❌ ELIMINAR: `docs/implementacion/infrastructure/arquitectura/adr/` (stub)

**Principio**: Un proyecto debe tener UNA ÚNICA fuente de ADRs

---

### 13. plantilla_adr.md

**Naturaleza**: Plantilla de ADR

**Ubicación correcta**: `docs/arquitectura/adr/plantilla_adr.md` ✅

**Alternativa aceptable**: `docs/plantillas/plantilla_adr.md`

**Razón**:
- Las plantillas deben estar en un lugar centralizado
- Todos los equipos (backend, frontend, infrastructure) deben usar la MISMA plantilla
- Versión general (4.6KB) es 6.5x más completa

**Acción**:
- ✅ MANTENER: `docs/arquitectura/adr/plantilla_adr.md`
- ❌ ELIMINAR: `docs/implementacion/infrastructure/arquitectura/adr/plantilla_adr.md` (simplificada)

---

## 📊 RESUMEN DE UBICACIONES

### Checklists → `docs/checklists/`
- ✅ checklist_desarrollo.md
- ✅ checklist_testing.md
- ✅ checklist_trazabilidad_requisitos.md
- ✅ checklist_cambios_documentales.md

### DevOps → `docs/devops/`
- ✅ contenedores_devcontainer.md
- ✅ runbooks/github_copilot_codespaces.md (revisar cuál versión)
- ✅ runbooks/reprocesar_etl_fallido.md
- ✅ runbooks/verificar_servicios.md
- ✅ runbooks/post_create.md

### Arquitectura → `docs/arquitectura/`
- ✅ lineamientos_codigo.md
- ✅ adr/adr_2025_001_vagrant_mod_wsgi.md
- ✅ adr/plantilla_adr.md

### Gobernanza → `docs/gobernanza/`
- ⚠️ lineamientos_gobernanza.md (revisar si mantener ambos)

---

## 🎯 PRINCIPIO DE DECISIÓN

**Regla de oro**: Preguntarse:

1. **¿Es transversal/general?** → `docs/` raíz
   - Aplica a todo el proyecto
   - Usado por múltiples equipos
   - Ej: runbooks, ADRs, checklists, lineamientos

2. **¿Es específico de implementación?** → `docs/implementacion/{area}/`
   - Requisitos específicos de un área
   - Diseño detallado de componentes
   - Documentación técnica de código
   - Ej: requisitos RF-001 del backend, diseño de componentes React

3. **¿Hay duda?** → Documentación operativa y de gobernanza suele ser GENERAL

---

## 🛠️ ACCIONES RECOMENDADAS

### Eliminar inmediatamente (10 archivos):
```bash
# Duplicados idénticos
rm docs/implementacion/backend/checklists/checklist_testing.md
rm docs/implementacion/backend/checklists/checklist_trazabilidad_requisitos.md
rm docs/implementacion/infrastructure/checklists/checklist_cambios_documentales.md

# Stubs de backend
rm docs/implementacion/backend/checklists/checklist_desarrollo.md
rm docs/implementacion/backend/devops/runbooks/reprocesar_etl_fallido.md

# Stubs de infrastructure
rm docs/implementacion/infrastructure/devops/contenedores_devcontainer.md
rm docs/implementacion/infrastructure/devops/runbooks/verificar_servicios.md
rm docs/implementacion/infrastructure/devops/runbooks/post_create.md
rm docs/implementacion/infrastructure/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md
rm docs/implementacion/infrastructure/arquitectura/adr/plantilla_adr.md
```

### Revisar manualmente (2 archivos):
1. Comparar `github_copilot_codespaces.md` (ambas versiones extensas)
2. Comparar `lineamientos_gobernanza.md` (contenido diferente)

### Considerar expandir (1 archivo):
- `docs/implementacion/backend/arquitectura/lineamientos_codigo.md` 
  → Expandir con lineamientos específicos de Django, o eliminar

