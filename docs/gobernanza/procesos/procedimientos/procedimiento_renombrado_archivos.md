# PROCEDIMIENTO: Renombrado Masivo de Archivos de Documentación

## Objetivo
Estandarizar nomenclatura de archivos de documentación siguiendo convenciones Clean Code.

## Pre-requisitos
1. Tener ADR-021 definido con convenciones claras
2. Tener auditoría de archivos problemáticos (AUDITORIA_NOMBRES_ARCHIVOS.md)
3. Estar en branch específico de trabajo

## Procedimiento Completo

### PASO 1: Auditoría y Planificación
**Input**: Todos los archivos .md del proyecto
**Output**: Lista de archivos a renombrar categorizada por tipo de problema

Acciones:
1. Escanear recursivamente todos los archivos .md
2. Identificar patrones problemáticos:
   - Números secuenciales sin descripción (testing_001.md)
   - MAYÚSCULAS para archivos normales (AGENTES_SDLC.md)
   - Formato inconsistente de ADRs (ADR_2025_XXX vs ADR-XXX)
   - Nombres ambiguos (index.md, TODO vs TAREAS_ACTIVAS)
3. Categorizar por prioridad:
   - ALTA: Números secuenciales (no revelan intención)
   - MEDIA: MAYÚSCULAS (estético pero importante)
   - MEDIA: ADRs inconsistentes (organización)
4. Generar propuestas específicas de renombrado
5. Crear documento AUDITORIA_NOMBRES_ARCHIVOS.md

### PASO 2: Crear/Actualizar ADR de Convenciones
**Input**: Auditoría de problemas
**Output**: ADR-021 con convenciones oficiales

Acciones:
1. Integrar principios de Clean Code de Robert Martin:
   - Principio 1: Nombres que revelen intenciones
   - Principio 3: Distinciones con sentido
   - Principio 4: Nombres pronunciables
   - Principio 5: Nombres buscables
   - Principio 6: Evitar codificaciones
   - Principio 7: Evitar asignaciones mentales
   - Principio 8: Una palabra por concepto
2. Definir reglas claras:
   - Archivos especiales: MAYÚSCULAS (README, CHANGELOG, ADR-XXX, TASK-XXX)
   - Archivos normales: snake_case minúsculas
   - Prefijos semánticos: guia_, procedimiento_, estrategia_, analisis_, reporte_
3. Documentar prohibiciones explícitas
4. Crear ejemplos antes/después

### PASO 3: Fase 1 - Renombrar Archivos Críticos (Números Secuenciales)
**Input**: Archivos con números secuenciales
**Output**: Archivos con nombres descriptivos

Acciones:
1. Identificar archivos (20 archivos típicamente):
   - QA: testing_001.md, testing_002.md, testing_003.md
   - Onboarding: onboarding_001.md ... onboarding_008.md
   - Deployment: deployment_001.md, deployment_002.md
   - Troubleshooting: troubleshooting_001.md

2. Para cada archivo:
   a. Leer contenido para entender propósito
   b. Generar nombre descriptivo basado en contenido:
      - testing_001.md (Backend pytest) → guia_ejecutar_pytest.md
      - onboarding_001.md (Setup entorno) → configurar_entorno_desarrollo.md
   c. Ejecutar: git mv archivo_viejo.md archivo_nuevo.md

3. Actualizar referencias:
   a. Buscar referencias: grep -r "testing_001.md" docs/
   b. Actualizar cada archivo que referencia:
      - QUICKSTART.md
      - gobernanza/guias_README.md
      - Cualquier índice o README que enlace

4. Commit con mensaje descriptivo:
   - Título: "docs(naming): apply Phase 1 naming conventions - rename files with sequential numbers"
   - Cuerpo: Lista de cambios, rationale basado en Clean Code
   
5. Push a branch

### PASO 4: Fase 2 - Estandarizar MAYÚSCULAS → snake_case
**Input**: Archivos normales en MAYÚSCULAS
**Output**: Archivos en snake_case

Acciones:
1. Identificar archivos por dominio (50-60 archivos típicamente):
   - infraestructura/: ESTRATEGIA_GIT_HOOKS.md, WASI_ENVIRONMENT_INTEGRATION.md, etc.
   - gobernanza/procesos/: AGENTES_SDLC.md, DEVOPS_AUTOMATION.md, etc.
   - backend/: ARQUITECTURA-MODULOS-COMPLETA.md, IMPLEMENTACION_PERMISOS_GRANULAR.md, etc.
   - ai/: AGENTES_Y_TECNICAS_APLICADAS.md, CASOS_DE_USO_SDLC.md, etc.

2. Para cada dominio:
   a. Crear lista de archivos: find domain -name "*.md" | grep '[A-Z][A-Z_]'
   b. Convertir cada nombre: ARCHIVO_NOMBRE.md → archivo_nombre.md
   c. Ejecutar batch: git mv ARCHIVO1.md archivo1.md && git mv ARCHIVO2.md archivo2.md
   
3. Casos especiales:
   - TAREAS_ACTIVAS.md → TODO.md (estandarización)
   - INDEX.md → catalogo_apis.md (nombre descriptivo)
   - Mantener: CHANGELOG.md, ROADMAP.md (archivos especiales)

4. Actualizar referencias:
   a. Buscar: grep -r "AGENTES_SDLC.md" docs/
   b. Actualizar archivos encontrados

5. Commit y push

### PASO 5: Fase 3 - Estandarizar ADRs
**Input**: ADRs con formato inconsistente
**Output**: ADRs organizados por dominio con formato estándar

Acciones:
1. Crear estructura de directorios:
   - mkdir -p docs/infraestructura/adr
   - mkdir -p docs/backend/adr
   - mkdir -p docs/frontend/adr
   - mkdir -p docs/ai/adr
   - (gobernanza/adr ya existe)

2. Identificar ADRs a renombrar:
   - Buscar: find docs -name "ADR*.md" | grep -v "ADR-"
   - Formato viejo: ADR_2025_XXX_descripcion.md
   - Formato nuevo: ADR-XXX-descripcion-kebab-case.md

3. Para cada ADR:
   a. Determinar dominio correcto (infraestructura, backend, frontend, ai, gobernanza)
   b. Convertir formato:
      - ADR_2025_001_vagrant_mod_wsgi.md → infraestructura/adr/ADR-001-vagrant-mod-wsgi.md
      - ADR_2025_004_centralized_log_storage.md → backend/adr/ADR-004-centralized-log-storage.md
   c. Ejecutar: git mv docs/old/ADR_2025_XXX.md docs/domain/adr/ADR-XXX.md

4. Eliminar duplicados:
   a. Identificar ADRs que existen en múltiples ubicaciones
   b. Comparar contenido para confirmar duplicación
   c. Eliminar versiones duplicadas (mantener solo en dominio correcto)
   d. git rm docs/gobernanza/adr/ADR_XXX_duplicate.md

5. Commit y push

### PASO 6: Validación Final
**Input**: Todos los cambios aplicados
**Output**: Confirmación de consistencia

Acciones:
1. Verificar que no quedan archivos con formato viejo:
   - find docs -name "*_00[0-9].md"
   - find docs -name "ADR_2025_*.md"
   
2. Validar que todas las referencias están actualizadas:
   - No broken links
   - Ningún grep devuelve referencias a nombres viejos

3. Generar reporte de cambios:
   - Total archivos renombrados
   - Desglose por fase
   - Archivos duplicados eliminados

4. Actualizar documentación:
   - ANALISIS_FALLAS_DOCS.md (marcar como RESUELTO)
   - ADR-021 (marcar implementación como completa)

## Estructura de Datos

### Entrada del Agente
```json
{
  "repository_path": "/path/to/docs",
  "adr_conventions": "docs/gobernanza/adr/ADR-021-convenciones-nomenclatura-documentacion.md",
  "audit_file": "docs/AUDITORIA_NOMBRES_ARCHIVOS.md",
  "branch_name": "claude/fix-naming-conventions-SESSIONID",
  "dry_run": false,
  "phases": ["sequential", "uppercase", "adrs"]
}
```

### Salida del Agente
```json
{
  "summary": {
    "total_files_renamed": 107,
    "duplicates_removed": 7,
    "references_updated": 4,
    "commits_created": 3
  },
  "phases": {
    "phase1_sequential": {
      "files_renamed": 11,
      "qa_files": 3,
      "onboarding_files": 8
    },
    "phase2_uppercase": {
      "files_renamed": 68,
      "infraestructura": 8,
      "gobernanza": 5,
      "backend": 22,
      "ai": 33
    },
    "phase3_adrs": {
      "files_renamed": 21,
      "duplicates_removed": 7,
      "directories_created": 4
    }
  },
  "commits": [
    "ce16d787: Phase 1 - sequential numbers",
    "3c404e94: Phase 2 - UPPERCASE to snake_case", 
    "74b1f31b: Phase 3 - ADR standardization"
  ]
}
```

## Criterios de Éxito
1. ✅ 100% archivos siguen convenciones ADR-021
2. ✅ 0 archivos con números secuenciales sin descripción
3. ✅ 0 archivos normales en MAYÚSCULAS (excepto especiales)
4. ✅ 100% ADRs en formato ADR-XXX-descripcion.md
5. ✅ 100% ADRs en subdirectorios adr/ de su dominio
6. ✅ 0 ADRs duplicados
7. ✅ 0 broken links en documentación
8. ✅ Git history preservado (rename detection)

## Tiempos Estimados
- Auditoría: 10-15 min (automático)
- Fase 1: 15-20 min (11 archivos)
- Fase 2: 25-30 min (68 archivos)
- Fase 3: 20-25 min (28 archivos)
- Validación: 5-10 min
- **Total**: 75-100 min
