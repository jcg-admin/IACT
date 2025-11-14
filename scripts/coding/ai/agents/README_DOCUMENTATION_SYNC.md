# Documentation Sync Agent

Agente especializado que sigue el patrón **Planner → Editor → Verifier → Reporter** para sincronizar el código implementado con la documentación.

## Arquitectura

El agente está compuesto por 4 sub-agentes que trabajan en pipeline:

```
┌────────────────────┐
│  CodeInspector     │  Planner: Inspecciona código y planifica
│  (Planner)         │
└──────────┬─────────┘
           │ inspection_plan
           ↓
┌────────────────────┐
│ DocumentationEditor│  Editor: Genera/actualiza documentación
│  (Editor)          │
└──────────┬─────────┘
           │ created_docs, updated_docs
           ↓
┌────────────────────┐
│ ConsistencyVerifier│  Verifier: Verifica consistencia
│  (Verifier)        │
└──────────┬─────────┘
           │ verification_result
           ↓
┌────────────────────┐
│  SyncReporter      │  Reporter: Genera reporte markdown
│  (Reporter)        │
└────────────────────┘
```

## Agentes

### 1. CodeInspectorAgent (Planner)

**Responsabilidad:** Inspeccionar código fuente y planificar documentación

**Input:**
- `project_root`: Ruta raíz del proyecto
- `domains`: Lista de dominios (["api", "ui", "infrastructure"])

**Output:**
- `discovered_components`: Componentes encontrados por dominio
- `existing_docs`: Documentación ya existente
- `inspection_plan`: Plan de qué crear/actualizar
  - `create`: Lista de docs faltantes
  - `update`: Lista de docs a actualizar
  - `ok`: Lista de docs OK

**Capacidades:**
- Detecta Django apps en `api/`
- Detecta módulos React en `ui/`
- Detecta configs Terraform/Docker en `infrastructure/`
- Compara con documentación existente
- Prioriza qué documentar primero

### 2. DocumentationEditorAgent (Editor)

**Responsabilidad:** Generar/actualizar documentación según el plan

**Input:**
- `inspection_plan`: Plan del CodeInspectorAgent
- `discovered_components`: Componentes descubiertos
- `dry_run`: Si True, no escribe archivos (default: True)

**Output:**
- `created_docs`: Lista de documentación creada
- `updated_docs`: Lista de documentación actualizada
- `files_written`: Rutas de archivos escritos

**Capacidades:**
- Genera documentación usando plantillas
- Documenta Django apps con estructura estándar
- Documenta módulos React
- Documenta infrastructure
- Sigue frontmatter YAML del proyecto
- Modo dry-run seguro

### 3. ConsistencyVerifierAgent (Verifier)

**Responsabilidad:** Verificar consistencia código-documentación

**Input:**
- `discovered_components`: Componentes del código
- `created_docs`: Documentación creada
- `existing_docs`: Documentación existente

**Output:**
- `verification_passed`: Boolean
- `inconsistencies`: Lista de inconsistencias
- `recommendations`: Recomendaciones

**Capacidades:**
- Detecta componentes sin documentación
- Detecta documentación huérfana
- Genera recomendaciones
- Clasifica inconsistencias por severidad

### 4. SyncReporterAgent (Reporter)

**Responsabilidad:** Generar reporte consolidado

**Input:**
- Resultados de todos los agentes anteriores

**Output:**
- `report_markdown`: Reporte en formato markdown
- `report_path`: Ruta donde se guardó (opcional)

**Capacidades:**
- Genera reporte legible en markdown
- Incluye estadísticas
- Lista componentes descubiertos
- Lista plan de documentación
- Reporte de verificación
- Guarda automáticamente en `docs/anexos/analisis_nov_2025/`

## Uso

### Opción A: Script Python (Recomendado)

```bash
# Dry-run (solo simula, no escribe)
python scripts/sync_documentation.py --dry-run

# Con reorganización de docs/ primero
python scripts/sync_documentation.py --dry-run --reorganize

# Ejecutar sincronización real
python scripts/sync_documentation.py

# Solo generar reporte sin modificar nada
python scripts/sync_documentation.py --report-only

# Sincronizar solo un dominio
python scripts/sync_documentation.py --domains api

# Sincronizar dos dominios
python scripts/sync_documentation.py --domains api,ui
```

### Opción B: Uso Programático

```python
from scripts.ai.agents.documentation_sync_agent import create_documentation_sync_pipeline

# Crear pipeline
pipeline = create_documentation_sync_pipeline(
    project_root="/home/user/IACT---project",
    dry_run=True,  # Cambiar a False para escritura real
    domains=["api", "ui", "infrastructure"]
)

# Ejecutar
result = pipeline.execute({
    "domains": ["api", "ui", "infrastructure"]
})

# Verificar resultado
if result["status"] == "success":
    data = result["data"]
    print(f"Componentes: {data['stats']['total_components']}")
    print(f"Docs creadas: {len(data['created_docs'])}")
    print(f"Reporte: {data['report_path']}")
```

### Opción C: Integración con Reorganización

El agente puede ejecutar automáticamente la reorganización de docs/ antes de sincronizar:

```bash
python scripts/sync_documentation.py --reorganize --dry-run
```

Esto ejecuta:
1. `scripts/reorganizar_docs_por_dominio.sh --dry-run`
2. Pipeline de sincronización completo

## Output Generado

### Documentación Creada

La documentación se genera en:
- **Backend:** `docs/implementacion/backend/arquitectura/{app_name}.md`
- **Frontend:** `docs/implementacion/frontend/arquitectura/{module_name}.md`
- **Infrastructure:** `docs/implementacion/infrastructure/arquitectura/{component}.md`

### Formato de Documentación

Cada documento incluye:
- Frontmatter YAML con metadata
- Descripción del componente
- Estructura de archivos
- Modelos/Componentes principales
- Tests
- Dependencias
- Notas

Ejemplo:

```markdown
---
id: APP-NOTIFICATIONS
tipo: django_app
dominio: backend
estado: documentado
fecha: 2025-11-06
auto_generado: true
---

# Django App: notifications

## Descripción

App de Django para notifications.

## Estructura

api/callcentersite/callcentersite/apps/notifications/
├── models.py          # Modelos de datos
├── views.py           # Vistas/ViewSets
...
```

### Reporte de Sincronización

Se genera en: `docs/anexos/analisis_nov_2025/SYNC_REPORT_YYYYMMDD_HHMMSS.md`

Incluye:
- Resumen ejecutivo con métricas
- Componentes descubiertos por dominio
- Plan de documentación (crear/actualizar)
- Documentación generada
- Verificación de consistencia
- Recomendaciones
- Próximos pasos

## Casos de Uso

### UC1: Primera sincronización del proyecto

```bash
# 1. Ejecutar dry-run para ver qué se generaría
python scripts/sync_documentation.py --dry-run

# 2. Revisar el reporte generado
cat docs/anexos/analisis_nov_2025/SYNC_REPORT_*.md

# 3. Si se ve bien, ejecutar sincronización real
python scripts/sync_documentation.py

# 4. Revisar documentación generada
ls -la docs/implementacion/backend/arquitectura/
ls -la docs/implementacion/frontend/arquitectura/

# 5. Completar detalles en cada documento

# 6. Commitear
git add docs/
git commit -m "docs: sincronización inicial código-documentación"
git push
```

### UC2: Sincronización después de nueva feature

Después de implementar una nueva Django app o módulo React:

```bash
# Sincronizar y detectar nuevo componente
python scripts/sync_documentation.py --domains api

# Revisar documentación generada para el nuevo componente
# Completar detalles específicos
# Commitear
```

### UC3: Reorganización + Sincronización en un solo comando

```bash
# Ejecutar ambos procesos
python scripts/sync_documentation.py --reorganize

# Resultado:
# 1. docs/ reorganizado (implementacion/ eliminado)
# 2. Código inspeccionado
# 3. Documentación generada en nueva estructura
# 4. Reporte completo
```

### UC4: Solo generar reporte sin modificar

```bash
# Útil para auditorías o revisiones
python scripts/sync_documentation.py --report-only

# Genera reporte completo sin escribir ningún archivo
```

## Configuración

### Dry-Run por Defecto

Por seguridad, el `DocumentationEditorAgent` tiene `dry_run=True` por defecto. Para escritura real:

```python
pipeline = create_documentation_sync_pipeline(
    project_root="/ruta/proyecto",
    dry_run=False  # Escritura real
)
```

### Dominios a Inspeccionar

Por defecto inspecciona todos los dominios. Para filtrar:

```bash
# Solo backend
python scripts/sync_documentation.py --domains api

# Solo frontend
python scripts/sync_documentation.py --domains ui

# Backend + Frontend (sin infrastructure)
python scripts/sync_documentation.py --domains api,ui
```

### Guardar Reporte

Por defecto el reporte se guarda automáticamente. Para no guardarlo:

```bash
python scripts/sync_documentation.py --no-report
```

## Integración con CI/CD

### GitHub Actions

Ejemplo de workflow para ejecutar sincronización automática:

```yaml
name: Sync Documentation

on:
  push:
    branches: [main, develop]
    paths:
      - 'api/**'
      - 'ui/**'
      - 'infrastructure/**'
  schedule:
    - cron: '0 0 * * 0'  # Semanal

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Sync Documentation
        run: |
          python scripts/sync_documentation.py

      - name: Create PR if changes
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: 'docs: sincronización automática código-documentación'
          title: 'Actualización automática de documentación'
          body: 'Documentación sincronizada con código actual'
```

## Métricas

El agente genera estadísticas detalladas:

```
Componentes totales: 25
Documentación faltante: 8
Documentación creada: 8
Documentación actualizada: 3
Inconsistencias: 2
```

## Limitaciones Actuales

1. **Actualización de docs:** Por ahora solo detecta docs desactualizadas, no las actualiza automáticamente
2. **Extracción de docstrings:** Limitada, depende de estructura estándar
3. **Detección de cambios:** No detecta cambios específicos en código (solo existencia de componentes)
4. **Plantillas:** Plantillas básicas, pueden necesitar personalización

## Roadmap

### v1.1 (Próxima)
- Actualización automática de docs existentes
- Extracción de docstrings Python/JSDoc
- Detección de cambios en código (diff-based)

### v1.2
- Soporte para más frameworks (FastAPI, Vue, etc.)
- Generación de diagramas automática
- Integración con requisitos (trazabilidad)

### v2.0
- Análisis de cambios mediante AST
- Generación de tests desde docs
- Validación de ejemplos de código en docs

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'ai.agents'"

Ejecutar desde la raíz del proyecto:

```bash
cd /home/user/IACT---project
python scripts/sync_documentation.py
```

### Warning: "api_path no existe"

El agente espera la estructura:
```
api/callcentersite/callcentersite/apps/
```

Si tu estructura es diferente, ajustar `_inspect_api()` en el agente.

### No se generan documentos

Verificar que `dry_run=False`:

```bash
python scripts/sync_documentation.py  # Sin --dry-run
```

## Conformidad

### Constitution

El agente sigue los principios de `docs/gobernanza/agentes/constitution.md`:

- Calidad sobre velocidad (no placeholders)
- Trazabilidad completa
- Sin emojis (prohibidos por GUIA_ESTILO.md)
- Testing y validación

### Estándares

- ISO 29148:2018: Trazabilidad código-requisitos
- BABOK v3: Jerarquía de artefactos
- GUIA_ESTILO.md: Formato y convenciones

## Contribuir

Para agregar soporte a nuevos tipos de componentes:

1. Extender `_inspect_*()` en `CodeInspectorAgent`
2. Agregar plantilla en `_generate_*_doc()` en `DocumentationEditorAgent`
3. Agregar tests

## Documentación Relacionada

- **Base Agent:** `scripts/ai/agents/base.py`
- **Constitution:** `docs/gobernanza/agentes/constitution.md`
- **Scripts reorganización:** `scripts/README_REORGANIZACION_DOCS.md`

---

**Versión:** 1.0
**Fecha:** 2025-11-06
**Autor:** equipo-arquitectura
