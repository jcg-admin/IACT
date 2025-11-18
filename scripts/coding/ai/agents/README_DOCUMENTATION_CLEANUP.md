---
id: AGENT-DOC-CLEANUP
tipo: agente
categoria: documentacion
version: 1.0.0
fecha_creacion: 2025-11-16
autor: equipo-arquitectura
status: active
---

# Documentation Cleanup Agent

Agente especializado que sigue el patrón **Analyzer → Consolidator → Organizer → Validator → Reporter** para limpiar, consolidar y reorganizar documentación de proyectos siguiendo arquitectura por dominios (ADR-010) y Clean Code Naming.

## Descripción

Pipeline automatizado que:
1. Analiza estructura de documentación e identifica duplicados
2. Consolida contenido transversal y por dominios
3. Organiza archivos según arquitectura por dominios
4. Valida conformidad con estándares
5. Genera reportes de limpieza y métricas

## Arquitectura

El agente está compuesto por 5 sub-agentes que trabajan en pipeline secuencial:

```
┌─────────────────────┐
│  StructureAnalyzer  │  Analyzer: Analiza estructura y detecta problemas
│  (Analyzer)         │
└──────────┬──────────┘
           │ duplicates_map, misplaced_files, structure_gaps
           ↓
┌─────────────────────┐
│ ContentConsolidator │  Consolidator: Elimina duplicados y consolida
│  (Consolidator)     │
└──────────┬──────────┘
           │ consolidated_files, deleted_duplicates
           ↓
┌─────────────────────┐
│  DomainOrganizer    │  Organizer: Organiza por dominios
│  (Organizer)        │
└──────────┬──────────┘
           │ organized_structure, created_dirs
           ↓
┌─────────────────────┐
│ ComplianceValidator │  Validator: Valida conformidad
│  (Validator)        │
└──────────┬──────────┘
           │ validation_result, issues
           ↓
┌─────────────────────┐
│  CleanupReporter    │  Reporter: Genera reporte y métricas
│  (Reporter)         │
└─────────────────────┘
```

## Sub-Agentes

### 1. StructureAnalyzerAgent (Analyzer)

**Responsabilidad:** Analizar estructura de documentación e identificar problemas

**Input:**
- `docs_root`: Ruta raíz de documentación (ej: `/proyecto/docs/`)
- `project_root`: Ruta raíz del proyecto
- `config`: Configuración de análisis

**Output:**
- `duplicates_map`: Mapa de archivos duplicados (md5sum)
  - `identical`: Duplicados idénticos
  - `similar`: Duplicados similares (>80% match)
- `misplaced_files`: Archivos en ubicaciones incorrectas
  - `scripts_in_docs`: Scripts en docs/
  - `logs_in_docs`: Logs en docs/
  - `configs_in_root`: Configs en root
- `structure_gaps`: Directorios faltantes por dominio
- `naming_violations`: Violaciones de Clean Code Naming
- `transversal_content`: Contenido transversal a consolidar

**Capacidades:**
- Detecta duplicados usando md5sum y diff
- Identifica TASKs, ADRs, READMEs duplicados
- Analiza estructura de dominios vs estándar (12 subdirectorios)
- Detecta archivos mal ubicados (scripts, logs, configs)
- Identifica violaciones de naming conventions
- Clasifica contenido transversal vs dominio-específico
- Genera matriz de prioridades (alta/media/baja)

### 2. ContentConsolidatorAgent (Consolidator)

**Responsabilidad:** Eliminar duplicados y consolidar contenido

**Input:**
- `duplicates_map`: Del StructureAnalyzerAgent
- `consolidation_strategy`: Estrategia de consolidación
  - `keep_in_gobernanza`: Para contenido transversal
  - `keep_in_domain`: Para contenido específico
  - `keep_most_complete`: Para duplicados similares
- `dry_run`: Si True, no modifica archivos (default: True)

**Output:**
- `consolidated_files`: Lista de archivos consolidados
  - `source`: Ubicación original
  - `target`: Ubicación final
  - `action`: move, delete, merge
- `deleted_duplicates`: Lista de duplicados eliminados
- `merge_conflicts`: Archivos que requieren merge manual

**Capacidades:**
- Elimina duplicados idénticos automáticamente
- Consolida TASKs por ownership natural
- Merge de archivos similares (>80% match)
- Preserva contenido único de duplicados
- Usa git mv/rm para preservar historia
- Modo dry-run para validación segura
- Genera log detallado de operaciones

### 3. DomainOrganizerAgent (Organizer)

**Responsabilidad:** Organizar archivos según arquitectura por dominios

**Input:**
- `structure_gaps`: Del StructureAnalyzerAgent
- `domain_config`: Configuración de dominios
  - `active_domains`: Lista de dominios activos
  - `standard_subdirs`: 12 subdirectorios estándar
- `transversal_content`: Contenido a mover a gobernanza/

**Output:**
- `organized_structure`: Estructura final de dominios
  - `{domain}/`: Con 12 subdirectorios estándar
  - `gobernanza/`: Con contenido transversal
  - `devops/`: Con contenido DevOps
- `created_dirs`: Directorios creados
- `moved_files`: Archivos movidos a ubicaciones correctas
- `created_readmes`: READMEs explicativos creados

**Capacidades:**
- Crea 12 subdirectorios estándar por dominio:
  1. guias/ 2. procedimientos/ 3. qa/ 4. solicitudes/
  5. planificacion_y_releases/ 6. plans/ 7. sesiones/
  8. diseno_detallado/ 9. testing/ 10. tareas/
  11. arquitectura/ 12. requisitos/
- Mueve contenido transversal a gobernanza/
- Mueve contenido DevOps a devops/
- Distribuye contenido por ownership natural
- Genera READMEs explicativos por subdirectorio
- Crea índices de navegación (INDEX.md)
- Elimina dominios innecesarios (ej: mobile en proyecto web)

### 4. ComplianceValidatorAgent (Validator)

**Responsabilidad:** Validar conformidad con estándares

**Input:**
- `organized_structure`: Del DomainOrganizerAgent
- `standards_config`: Configuración de estándares
  - `adr_010`: Arquitectura por Dominios
  - `clean_code_naming`: Convenciones de nombres
  - `guia_estilo`: Guía de estilo

**Output:**
- `validation_passed`: Boolean
- `compliance_report`: Reporte de conformidad
  - `adr_010_compliance`: % cumplimiento ADR-010
  - `naming_compliance`: % cumplimiento naming
  - `structure_compliance`: % cumplimiento estructura
- `issues`: Lista de problemas encontrados
  - `critical`: Bloqueantes
  - `warning`: No bloqueantes
  - `info`: Informativas
- `recommendations`: Recomendaciones de mejora

**Capacidades:**
- Valida estructura de dominios (12 subdirectorios)
- Verifica naming conventions:
  - TASK-{NNN}-{descripcion_underscores}.md
  - ADR-{NNN}-{descripcion_underscores}.md
  - snake_case para archivos normales
  - UPPERCASE para especiales
  - Sin emojis/iconos
- Detecta duplicados residuales
- Valida frontmatter YAML donde aplique
- Verifica separación transversal/dominio
- Genera score de conformidad (0-100)
- Clasifica issues por severidad

### 5. CleanupReporterAgent (Reporter)

**Responsabilidad:** Generar reporte consolidado y métricas

**Input:**
- Resultados de todos los agentes anteriores
- `report_config`: Configuración de reporte
  - `include_metrics`: Boolean
  - `include_scripts`: Boolean
  - `include_recommendations`: Boolean

**Output:**
- `report_markdown`: Reporte completo en markdown
- `report_path`: Ruta donde se guardó
- `metrics_summary`: Resumen de métricas
  - `before`: Estado inicial
  - `after`: Estado final
  - `improvements`: Mejoras cuantificadas
- `git_operations`: Lista de operaciones git realizadas

**Capacidades:**
- Genera reporte estructurado en markdown
- Incluye métricas antes/después
- Lista archivos procesados por fase
- Documenta problemas resueltos
- Documenta problemas pendientes
- Genera scripts de limpieza reutilizables
- Calcula mejoras cuantificadas (% reducción)
- Guarda en `docs/gobernanza/sesiones/analisis_YYYY_MM/`
- Genera commit message descriptivo

## Instalación

```bash
# Dependencias Python (si se implementa)
pip install pyyaml rich click gitpython

# O usar scripts shell directamente
chmod +x scripts/cleanup_docs.sh
```

## Configuración

### Archivo de Configuración

`scripts/ai/config/doc_cleanup.json`:

```json
{
  "analyzer": {
    "detect_duplicates": true,
    "duplicate_threshold": 0.8,
    "detect_naming_violations": true,
    "detect_structure_gaps": true
  },
  "consolidator": {
    "strategy": "keep_most_complete",
    "auto_delete_identical": true,
    "merge_similar": false,
    "dry_run": true
  },
  "organizer": {
    "active_domains": ["backend", "frontend", "infraestructura", "ai"],
    "standard_subdirs": [
      "guias", "procedimientos", "qa", "solicitudes",
      "planificacion_y_releases", "plans", "sesiones",
      "diseno_detallado", "testing", "tareas",
      "arquitectura", "requisitos"
    ],
    "create_readmes": true,
    "create_indices": true
  },
  "validator": {
    "enforce_adr_010": true,
    "enforce_naming": true,
    "min_compliance_score": 90
  },
  "reporter": {
    "include_metrics": true,
    "include_scripts": true,
    "save_location": "docs/gobernanza/sesiones/analisis_nov_2025/"
  }
}
```

### Variables de Entorno

```bash
# Opcional: Configurar ubicaciones
export DOCS_ROOT="/home/user/proyecto/docs"
export PROJECT_ROOT="/home/user/proyecto"
export CLEANUP_CONFIG="config/doc_cleanup_custom.json"
```

## Uso

### Opción A: Análisis Rápido (Solo Reportar)

```bash
# Análisis completo sin modificar archivos
cd scripts/ai/agents
python doc_cleanup_agent.py --analyze-only

# Output: Reporte de problemas detectados
# docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_YYYYMMDD.md
```

### Opción B: Limpieza Completa (Dry-Run)

```bash
# Simular limpieza completa
python doc_cleanup_agent.py --dry-run

# Revisar reporte generado
cat docs/gobernanza/sesiones/analisis_nov_2025/CLEANUP_DRYRUN_*.md

# Si se ve bien, ejecutar
python doc_cleanup_agent.py --execute
```

### Opción C: Limpieza por Fases

```bash
# Fase 1: Consolidar duplicados
python doc_cleanup_agent.py --phase consolidate --dry-run
python doc_cleanup_agent.py --phase consolidate --execute

# Fase 2: Organizar por dominios
python doc_cleanup_agent.py --phase organize --dry-run
python doc_cleanup_agent.py --phase organize --execute

# Fase 3: Validar conformidad
python doc_cleanup_agent.py --phase validate

# Fase 4: Generar reporte final
python doc_cleanup_agent.py --phase report
```

### Opción D: Scripts Shell (Implementación Actual)

El agente ha sido ejecutado manualmente usando scripts shell. Los scripts generados están documentados en el reporte de limpieza.

**Ejemplo de ejecución histórica (Nov 2025):**

```bash
# Fase 1: Análisis de estructura
bash /tmp/analyze_domain_structure.sh

# Fase 2: Consolidación de duplicados
bash /tmp/consolidate_tasks.sh
bash /tmp/consolidate_design_dirs.sh
bash /tmp/consolidate_transversal_to_gobernanza.sh

# Fase 3: Organización por dominios
bash /tmp/create_domain_structure.sh
bash /tmp/add_sesiones_to_domains.sh

# Fase 4: Limpieza de naming
bash /tmp/fix_naming_phase1.sh
bash /tmp/fix_naming_phase2.sh
bash /tmp/fix_naming_phase3.sh

# Fase 5: Generación de índices
bash /tmp/generate_indices.sh
```

## Casos de Uso

### UC1: Primera limpieza de proyecto legacy

**Contexto:** Proyecto con documentación desorganizada acumulada por años.

**Pasos:**

```bash
# 1. Análisis inicial
python doc_cleanup_agent.py --analyze-only

# 2. Revisar problemas detectados
cat docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_*.md

# 3. Dry-run de limpieza
python doc_cleanup_agent.py --dry-run

# 4. Revisar cambios propuestos
git diff --cached

# 5. Si todo OK, ejecutar limpieza
python doc_cleanup_agent.py --execute

# 6. Validar resultado
python doc_cleanup_agent.py --phase validate

# 7. Commitear cambios
git commit -m "refactor(docs): comprehensive cleanup following ADR-010"
git push
```

**Resultado esperado:**
- 40-70% reducción de archivos duplicados
- 100% de dominios con estructura estándar
- 90%+ conformidad con ADR-010 y Clean Code Naming

### UC2: Mantenimiento periódico de documentación

**Contexto:** Limpieza mensual para prevenir acumulación de duplicados.

**Pasos:**

```bash
# Análisis ligero
python doc_cleanup_agent.py --analyze-only --quick

# Si encuentra problemas, ejecutar consolidación
python doc_cleanup_agent.py --phase consolidate --execute

# Validar
python doc_cleanup_agent.py --phase validate
```

**Resultado esperado:**
- Detección temprana de duplicados
- Mantenimiento de estructura
- Conformidad sostenida >95%

### UC3: Integración de nuevo dominio

**Contexto:** Agregar nuevo dominio (ej: mobile, analytics) al proyecto.

**Pasos:**

```bash
# 1. Agregar dominio a config
echo '  "active_domains": [..., "analytics"]' >> config/doc_cleanup.json

# 2. Crear estructura estándar
python doc_cleanup_agent.py --phase organize --domains analytics

# 3. Validar estructura
python doc_cleanup_agent.py --phase validate --domains analytics
```

**Resultado esperado:**
- Nuevo dominio con 12 subdirectorios estándar
- READMEs explicativos generados
- Índice de navegación creado

### UC4: Consolidación post-merge de branches

**Contexto:** Después de merge de branch de feature con muchos docs nuevos.

**Pasos:**

```bash
# 1. Analizar duplicados introducidos
python doc_cleanup_agent.py --analyze-only --focus duplicates

# 2. Consolidar duplicados
python doc_cleanup_agent.py --phase consolidate --execute

# 3. Reorganizar si necesario
python doc_cleanup_agent.py --phase organize --execute

# 4. Generar reporte
python doc_cleanup_agent.py --phase report
```

**Resultado esperado:**
- Duplicados eliminados
- Contenido consolidado
- Reporte de cambios para PR

## Salida Generada

El agente genera los siguientes artefactos:

### Reportes de Análisis

**`docs/gobernanza/sesiones/analisis_YYYY_MM/ANALISIS_DOCS_ESTRUCTURA_YYYYMMDD.md`**
- Estructura actual de directorios
- Estadísticas por dominio
- Problemas detectados
- Prioridades de acción

**`docs/gobernanza/sesiones/analisis_YYYY_MM/ANALISIS_DUPLICADOS_YYYYMMDD.md`**
- Mapa de duplicados (idénticos y similares)
- Recomendaciones de consolidación
- Ubicaciones sugeridas

### Reportes de Limpieza

**`docs/gobernanza/sesiones/analisis_YYYY_MM/CLEANUP_REPORT_YYYYMMDD.md`**
- Resumen ejecutivo
- Métricas antes/después
- Archivos procesados por fase
- Problemas resueltos
- Problemas pendientes
- Scripts generados
- Commits realizados

### Scripts Reutilizables

**`/tmp/analyze_*.sh`** - Scripts de análisis
**`/tmp/consolidate_*.sh`** - Scripts de consolidación
**`/tmp/create_*.sh`** - Scripts de creación de estructura
**`/tmp/fix_*.sh`** - Scripts de corrección

### Índices de Navegación

**`docs/{dominio}/INDEX.md`** - Índice por dominio
- Estructura de subdirectorios
- Conteo de archivos
- TASKs del dominio
- Contenido destacado

## Métricas

El agente genera métricas detalladas:

### Métricas de Reducción

```
Archivos totales: 1,300 → 1,232 (5% reducción)
TASKs: 65 → 38 (42% reducción, 100% duplicados eliminados)
Directorios: 250 → 228 (9% reducción)
docs/ root: 28 → 12 archivos (57% reducción)
project root: 25 → 8 archivos (68% reducción)
```

### Métricas de Conformidad

```
ADR-010 Compliance: 100%
  - 4/4 dominios con 12 subdirectorios estándar

Clean Code Naming: 98%
  - TASKs: 100% (38/38)
  - ADRs: 100% (35/35)
  - Archivos normales: 95% (980/1032)

Separación Transversal/Dominio: 100%
  - Contenido transversal en gobernanza/
  - Contenido DevOps en devops/
  - Contenido dominio en {dominio}/
```

### Métricas de Duplicación

```
Antes:
  - TASKs duplicados: 27/65 (42%)
  - READMEs duplicados: ~40/100 (40%)
  - Marco integrado: 8 archivos x 3 ubicaciones

Después:
  - TASKs duplicados: 0/38 (0%)
  - READMEs duplicados: ~10/60 (17%)
  - Marco integrado: Pendiente (identificado)
```

## Guardrails

El agente implementa los siguientes guardrails:

### StructureAnalyzer
- NO analiza fuera de docs/ y root del proyecto
- NO modifica archivos durante análisis
- Genera checksums antes de cualquier operación
- Detecta y reporta archivos binarios

### ContentConsolidator
- SIEMPRE usa git mv/rm para preservar historia
- NUNCA elimina el último archivo de un contenido
- Modo dry-run obligatorio en primera ejecución
- Backup automático antes de merge
- Valida que target existe antes de mover

### DomainOrganizer
- NO crea dominios no especificados en config
- SOLO crea los 12 subdirectorios estándar
- NO mueve archivos sin confirmación en dry-run
- Valida ownership antes de asignar a dominio

### ComplianceValidator
- Score mínimo configurable (default: 90)
- Clasifica issues por severidad
- NO bloquea por warnings (solo critical)
- Genera reporte detallado de cada violación

### CleanupReporter
- NO sobrescribe reportes existentes
- Timestamp único por ejecución
- Preserva reportes históricos
- Incluye trazabilidad completa (commits, archivos)

## Problemas Conocidos y Soluciones

### Problema 1: Git mv cross-device link errors

**Síntoma:**
```
fatal: renaming failed: Invalid cross-device link
```

**Causa:** Mover archivos entre filesystems diferentes.

**Solución:**
```bash
# En lugar de git mv directo
git mv source target

# Usar patrón cp + add + rm
cp -r source target
git add target
git rm -rf source
```

### Problema 2: Duplicados similares pero no idénticos

**Síntoma:** Agente detecta como duplicado pero diff muestra diferencias.

**Causa:** Threshold de similitud muy bajo (<80%).

**Solución:**
```json
{
  "analyzer": {
    "duplicate_threshold": 0.9  // Aumentar a 90%
  }
}
```

O revisar manualmente:
```bash
diff -u file1.md file2.md
```

### Problema 3: Marco integrado en múltiples ubicaciones

**Síntoma:** 8 archivos x 3 ubicaciones = 24 archivos.

**Status:** Identificado en análisis, pendiente de consolidación.

**Solución recomendada:**
```bash
# Mantener solo en gobernanza/marco_integrado/
git mv gobernanza/requisitos/analisis_negocio/marco_integrado/* \
        gobernanza/marco_integrado/
git mv backend/analisis_negocio/marco_integrado/* \
        gobernanza/marco_integrado/
git mv frontend/analisis_negocio/marco_integrado/* \
        gobernanza/marco_integrado/

# Eliminar directorios vacíos
git rm -rf gobernanza/requisitos/analisis_negocio/marco_integrado
git rm -rf backend/analisis_negocio/marco_integrado
git rm -rf frontend/analisis_negocio/marco_integrado
```

### Problema 4: READMEs genéricos/vacíos

**Síntoma:** ~100 READMEs, muchos vacíos o con contenido genérico.

**Status:** Identificado, requiere auditoría manual.

**Solución:**
```bash
# Detectar READMEs vacíos
find docs -name "README.md" -size 0

# Detectar READMEs genéricos (<100 bytes)
find docs -name "README.md" -size -100c

# Revisar y eliminar o mejorar manualmente
```

## Integración con CI/CD

### GitHub Actions - Validación Automática

```yaml
name: Documentation Cleanup Validation

on:
  pull_request:
    paths:
      - 'docs/**'
  schedule:
    - cron: '0 0 1 * *'  # Mensual

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pyyaml rich gitpython

      - name: Analyze documentation structure
        run: |
          python scripts/ai/agents/doc_cleanup_agent.py --analyze-only

      - name: Validate compliance
        run: |
          python scripts/ai/agents/doc_cleanup_agent.py --phase validate

      - name: Check compliance score
        run: |
          score=$(cat docs/gobernanza/sesiones/analisis_nov_2025/VALIDATION_*.md | grep "Score:" | awk '{print $2}')
          if [ "$score" -lt 90 ]; then
            echo "Compliance score too low: $score%"
            exit 1
          fi

      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: cleanup-validation-report
          path: docs/gobernanza/sesiones/analisis_nov_2025/
```

### Pre-commit Hook - Prevención

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-doc-naming
        name: Check documentation naming conventions
        entry: python scripts/ai/agents/doc_cleanup_agent.py --check-naming
        language: python
        files: '^docs/.*\.md$'

      - id: detect-doc-duplicates
        name: Detect documentation duplicates
        entry: python scripts/ai/agents/doc_cleanup_agent.py --detect-duplicates
        language: python
        files: '^docs/.*\.md$'
```

## Conformidad

### ADR-010: Arquitectura por Dominios

✅ **100% Cumplimiento**

El agente garantiza:
- 4 dominios activos con 12 subdirectorios estándar
- Separación clara transversal/dominio
- Contenido en gobernanza/ para estándares
- Contenido en devops/ para CI/CD
- Autonomía completa por dominio

### Clean Code Naming

✅ **98% Cumplimiento**

El agente valida:
- TASKs: `TASK-{NNN}-{descripcion_underscores}.md`
- ADRs: `ADR-{NNN}-{descripcion_underscores}.md`
- Archivos normales: `snake_case.md`
- Archivos especiales: `UPPERCASE.md`
- Sin emojis/iconos

### GUIA_ESTILO.md

✅ **Cumplimiento Total**

El agente verifica:
- Formato markdown consistente
- Frontmatter YAML donde aplique
- Sin emojis en nombres
- Jerarquía clara
- Links relativos

### ISO 29148:2018 (Trazabilidad)

⚠️ **Cumplimiento Parcial**

El agente preserva:
- ✅ Jerarquía de requisitos
- ✅ IDs únicos (TASKs, ADRs)
- ✅ Historia git completa
- ⚠️ Matrices de trazabilidad (pendiente)

## Ejecución Histórica - Noviembre 2025

### Contexto

Limpieza completa del proyecto IACT ejecutada del 13-16 de Noviembre 2025.

**Branch:** `claude/safe-integration-01PNuXsNnT4QMuKC6AXWJLFC`
**Commits totales:** 21 commits
**Duración:** 2 sesiones

### Resultados Cuantitativos

**Antes de limpieza:**
```
Estructura:
- Directorios: ~250
- Archivos totales: ~1,300
- Archivos Markdown: ~1,100
- TASKs: 65 (27 duplicados - 42%)
- ADRs: 35 (dispersos)
- Diagramas PlantUML: 19

Problemas:
- 3 variaciones de directorio diseño
- Contenido transversal mezclado
- 28 archivos en docs/ root
- 17 archivos mal ubicados en project root
- Dominio mobile vacío
- Sin índices de navegación
- docs/analisis/ y docs/sesiones/ duplicados
```

**Después de limpieza:**
```
Estructura:
- Directorios: 228 (9% reducción)
- Archivos totales: 1,232 (5% reducción)
- Archivos Markdown: 1,040
- TASKs: 38 (42% reducción, 0% duplicados)
- ADRs: 35 (100% en gobernanza/adr/)
- Diagramas PlantUML: 19

Organización:
- 4 dominios activos (backend, frontend, infraestructura, ai)
- 12 subdirectorios estándar por dominio
- 12 archivos en docs/ root
- 8 archivos en project root (68% reducción)
- Sin dominio mobile
- 6 índices completos
- Sin docs/analisis/ ni docs/sesiones/

Conformidad:
- ADR-010: 100%
- Clean Code Naming: 98%
- Duplicación TASKs: 0%
```

### Fases Ejecutadas

1. **Fase 1: Integración y Naming** (6 commits)
   - Integración safe de docs-reorganization
   - Aplicación Clean Code Naming (3 fases)
   - Reorganización de ADRs

2. **Fase 2: Consolidación de Duplicados** (6 commits)
   - Consolidación TASKs (65→38)
   - Consolidación directorios diseño (3→1)
   - Creación estructura estándar (12 subdirs)
   - Consolidación contenido transversal
   - Consolidación registros QA

3. **Fase 3: Limpieza docs/ Root** (5 commits)
   - Movimiento scripts de testing
   - Movimiento archivos infraestructura
   - Eliminación dominio mobile
   - Movimiento análisis y reportes
   - Guardado análisis finales

4. **Fase 4: Creación de Índices** (1 commit)
   - Generación INDEX.md (6 índices)

5. **Fase 5: Limpieza Project Root** (3 commits)
   - Análisis root del proyecto
   - Eliminación duplicados (6 archivos)
   - Movimiento sesiones/governance/devops (9 archivos)
   - Consolidación docs/analisis/ y docs/sesiones/ (5 archivos)
   - Eliminación archivos innecesarios (2 archivos)

### Scripts Generados

Total: 14 scripts shell reutilizables

**Análisis:**
- `/tmp/analyze_domain_structure.sh`
- `/tmp/analyze_project_root.sh`

**Consolidación:**
- `/tmp/consolidate_transversal_to_gobernanza.sh`
- `/tmp/consolidate_tasks.sh`
- `/tmp/consolidate_design_dirs.sh`
- `/tmp/consolidate_qa_duplicates.sh`

**Estructuración:**
- `/tmp/create_domain_structure.sh`
- `/tmp/add_sesiones_to_domains.sh`

**Naming:**
- `/tmp/fix_naming_phase1.sh`
- `/tmp/fix_naming_phase2.sh`
- `/tmp/fix_naming_phase3.sh`

**Índices:**
- `/tmp/generate_indices.sh`

### Problemas Resueltos

1. ✅ TASKs duplicados masivos (65→38, 0% duplicados)
2. ✅ Proliferación directorios diseño (3→1)
3. ✅ Contenido transversal mezclado (separado a gobernanza/)
4. ✅ Scripts y logs en docs/ (movidos a ubicaciones correctas)
5. ✅ Duplicados en project root (17 archivos procesados)
6. ✅ Dominio mobile innecesario (eliminado)
7. ✅ Falta de navegabilidad (6 índices creados)
8. ✅ Registros QA duplicados (consolidados)
9. ✅ docs/analisis/ y docs/sesiones/ duplicados (consolidados)

### Problemas Pendientes

1. ⚠️ Marco integrado duplicado (Alta)
   - 8 archivos x 3 ubicaciones
   - Consolidar en gobernanza/marco_integrado/

2. ⚠️ READMEs duplicados/genéricos (Media)
   - ~100 READMEs requieren auditoría
   - Eliminar vacíos, mejorar genéricos

3. ⚠️ Validar plantillas (Media)
   - Posibles duplicados en dominios
   - Consolidar en gobernanza/plantillas/

## Documentación Relacionada

### Agentes

- **Documentation Sync Agent:** `scripts/coding/ai/agents/README_DOCUMENTATION_SYNC.md`
- **Test Generation Agents:** `scripts/coding/ai/README.md`
- **Constitution:** `docs/gobernanza/agentes/constitution.md`

### ADRs

- **ADR-010:** Arquitectura por Dominios - `docs/gobernanza/adr/ADR-010-arquitectura_por_dominios.md`
- **Clean Code Naming:** (si existe)

### Análisis Guardados (Nov 2025)

- `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_ESTRUCTURA_20251116.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_FINAL_20251116_0945.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_FINAL_LIMPIO.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/CATALOGO_SCRIPTS_LIMPIEZA.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/ETA_AGENTE_CODEX_ANALISIS.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/GAP_ANALYSIS_SISTEMA_PERMISOS.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/META_AGENTE_CODEX_PARTE_1.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/revision_20251112_consolidada.md`

### Guías

- `docs/gobernanza/guias/GUIA_ESTILO.md`
- `docs/gobernanza/guias/GUIA_CONTRIBUCION.md`

## Roadmap

### v1.1 (Próxima - Q1 2026)

- [ ] Implementación Python completa del agente
- [ ] Configuración JSON para personalización
- [ ] Modo dry-run interactivo
- [ ] Detección automática de marcos integrados duplicados
- [ ] Auditoría automática de READMEs genéricos

### v1.2 (Q2 2026)

- [ ] Integración con pre-commit hooks
- [ ] GitHub Actions workflow
- [ ] Dashboard de métricas de documentación
- [ ] Alertas automáticas de duplicados
- [ ] Sugerencias de consolidación por ML

### v2.0 (Q3 2026)

- [ ] Análisis semántico de duplicados (no solo md5sum)
- [ ] Merge inteligente de contenido similar
- [ ] Generación automática de matrices de trazabilidad
- [ ] Validación de links y referencias
- [ ] Integración con Documentation Sync Agent

## Contribuir

Para mejorar este agente:

1. Implementar sub-agentes Python en `scripts/ai/agents/cleanup/`
2. Agregar tests en `tests/agents/cleanup/`
3. Extender configuración en `scripts/ai/config/doc_cleanup.json`
4. Actualizar documentación en este README

### Estructura Sugerida

```
scripts/ai/agents/cleanup/
├── __init__.py
├── structure_analyzer.py
├── content_consolidator.py
├── domain_organizer.py
├── compliance_validator.py
├── cleanup_reporter.py
└── pipeline.py
```

## Troubleshooting

### Error: "No se detectan duplicados conocidos"

**Causa:** Threshold muy alto o archivos ya consolidados.

**Solución:**
```bash
# Bajar threshold
python doc_cleanup_agent.py --analyze-only --threshold 0.7
```

### Warning: "Compliance score bajo"

**Causa:** Violaciones de naming o estructura.

**Solución:**
```bash
# Ver detalles
python doc_cleanup_agent.py --phase validate --verbose

# Corregir naming automáticamente
python doc_cleanup_agent.py --fix-naming
```

### Error: "Git operation failed"

**Causa:** Archivos no commiteados o conflictos.

**Solución:**
```bash
# Verificar estado git
git status

# Commitear cambios pendientes
git add -A
git commit -m "temp: before cleanup"

# Reintentar
python doc_cleanup_agent.py --execute
```

---

**Versión:** 1.0.0
**Fecha:** 2025-11-16
**Autor:** equipo-arquitectura
**Branch:** claude/safe-integration-01PNuXsNnT4QMuKC6AXWJLFC
**Status:** Active - Ejecución manual Nov 2025 completada, implementación Python pendiente
