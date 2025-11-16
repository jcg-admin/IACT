---
id: GUIA-UBICACIONES-ARTEFACTOS
tipo: guia
categoria: gobernanza
version: 1.0.0
fecha_creacion: 2025-11-16
autor: equipo-arquitectura
status: activo
---

# Guía de Ubicaciones Canónicas de Artefactos

Esta guía define **dónde** colocar cada tipo de artefacto generado durante el desarrollo, análisis, documentación y automatización del proyecto IACT.

## Propósito

Eliminar ambigüedad al generar artefactos. Cuando un agente o desarrollador crea un documento, script, reporte o configuración, debe saber **exactamente**:

1. ✅ **Dónde** guardarlo (ubicación canónica)
2. ✅ **Cómo** nombrarlo (convención de naming)
3. ✅ **Qué** metadata incluir (frontmatter YAML)
4. ✅ **Cuándo** moverlo o archivarlo

## Principios

### 1. Separación Transversal vs Dominio-Específico

**Transversal** → `docs/gobernanza/` o `docs/devops/`
**Dominio-específico** → `docs/{dominio}/`

### 2. Temporalidad

**Temporal** → `/tmp/` (se puede eliminar)
**Permanente** → `docs/`, `scripts/`
**Histórico** → `docs/gobernanza/sesiones/`

### 3. Ownership

**Gobernanza/Arquitectura** → `docs/gobernanza/`
**DevOps/CI-CD** → `docs/devops/`
**Backend** → `docs/backend/`
**Frontend** → `docs/frontend/`
**Infraestructura** → `docs/infraestructura/`
**AI/Agentes** → `docs/ai/` o `scripts/coding/ai/`

## Mapa de Artefactos

### 📊 Análisis y Reportes

#### Análisis de Documentación

**Tipo:** Análisis de estructura, duplicados, conformidad de docs/

**Ubicación canónica:**
```
docs/gobernanza/sesiones/analisis_YYYY_MM/ANALISIS_{TEMA}_{YYYYMMDD}.md
```

**Ejemplos:**
- `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_ESTRUCTURA_20251116.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DUPLICADOS_20251116.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_CONFORMIDAD_20251116.md`

**Frontmatter:**
```yaml
---
fecha: 2025-11-16
tipo: analisis
categoria: documentacion
autor: agente-cleanup
relacionado: ["ADR-010"]
---
```

**Cuándo usar:**
- Análisis de estructura de documentación
- Reportes de duplicados
- Auditorías de conformidad
- Análisis de gaps

#### Reporte de Limpieza

**Tipo:** Reporte de proceso de limpieza/consolidación ejecutado

**Ubicación canónica:**
```
docs/gobernanza/sesiones/analisis_YYYY_MM/CLEANUP_REPORT_{YYYYMMDD}.md
```

**Ejemplos:**
- `docs/gobernanza/sesiones/analisis_nov_2025/CLEANUP_REPORT_20251116.md`

**Frontmatter:**
```yaml
---
fecha: 2025-11-16
tipo: reporte
categoria: limpieza
commits: ["67ba2ef3", "318afe66"]
branch: claude/safe-integration-01PNuXsNnT4QMuKC6AXWJLFC
---
```

**Cuándo usar:**
- Después de proceso de limpieza de docs/
- Post-consolidación de duplicados
- Reorganización de estructura

#### Análisis de Negocio / Técnico

**Tipo:** Análisis técnico específico (permisos, arquitectura, etc.)

**Ubicación canónica:**
```
docs/gobernanza/sesiones/analisis_YYYY_MM/{NOMBRE_ANALISIS}.md
```

**Ejemplos:**
- `docs/gobernanza/sesiones/analisis_nov_2025/GAP_ANALYSIS_SISTEMA_PERMISOS.md`
- `docs/gobernanza/sesiones/analisis_nov_2025/ETA_AGENTE_CODEX_ANALISIS.md`

**Frontmatter:**
```yaml
---
fecha: 2025-11-16
tipo: analisis
categoria: tecnico
dominio: backend  # si aplica
autor: equipo-arquitectura
---
```

**Cuándo usar:**
- Análisis de gaps de features
- Análisis de arquitectura
- Análisis de permisos/seguridad

#### Reporte de Sesión de Trabajo

**Tipo:** Registro de sesión de desarrollo/planificación

**Ubicación canónica:**
```
docs/gobernanza/sesiones/SESSION_{TEMA}_{YYYY_MM_DD}.md
```

**Ejemplos:**
- `docs/gobernanza/sesiones/SESSION_PIPELINE_2025_11_13.md`
- `docs/gobernanza/sesiones/SESSION_REFACTORING_2025_11_16.md`

**Frontmatter:**
```yaml
---
fecha: 2025-11-13
tipo: sesion
categoria: desarrollo
participantes: ["dev1", "dev2"]
duracion_horas: 3
---
```

**Cuándo usar:**
- Sesiones de pair programming
- Sesiones de planning
- Sesiones de arquitectura

### 🤖 Agentes y Automatización

#### Documentación de Agente

**Tipo:** README de agente especializado

**Ubicación canónica:**
```
scripts/coding/ai/agents/README_{AGENTE_NAME}.md
```

**Ejemplos:**
- `scripts/coding/ai/agents/README_DOCUMENTATION_SYNC.md`
- `scripts/coding/ai/agents/README_DOCUMENTATION_CLEANUP.md`
- `scripts/coding/ai/agents/README_BUSINESS_ANALYSIS.md`

**Frontmatter:**
```yaml
---
id: AGENT-{NAME}
tipo: agente
categoria: {categoria}
version: 1.0.0
fecha_creacion: 2025-11-16
autor: equipo-arquitectura
status: active
---
```

**Estructura requerida:**
1. Descripción
2. Arquitectura (diagrama ASCII)
3. Sub-Agentes (Input/Output/Capacidades)
4. Uso (ejemplos prácticos)
5. Configuración
6. Casos de Uso
7. Integración CI/CD
8. Guardrails
9. Troubleshooting
10. Conformidad
11. Roadmap

**Cuándo usar:**
- Al crear nuevo agente especializado
- Al documentar pipeline de agentes

#### Script de Automatización (Temporal)

**Tipo:** Script shell para análisis/limpieza temporal

**Ubicación canónica:**
```
/tmp/{accion}_{objeto}.sh
```

**Ejemplos:**
- `/tmp/analyze_domain_structure.sh`
- `/tmp/consolidate_tasks.sh`
- `/tmp/fix_naming_phase1.sh`

**Cuándo usar:**
- Scripts de un solo uso
- Scripts de análisis exploratorio
- Scripts que serán eliminados después de ejecución

**Nota:** Si el script es reutilizable, mover a ubicación permanente.

#### Script de Automatización (Permanente)

**Tipo:** Script reutilizable de automatización

**Ubicación canónica:**
```
scripts/coding/ai/automation/{nombre_script}.sh
```
o
```
scripts/coding/ai/{categoria}/{nombre_script}.py
```

**Ejemplos:**
- `scripts/coding/ai/automation/cleanup_docs.sh`
- `scripts/coding/ai/generators/generate_tests.py`

**Cuándo usar:**
- Scripts reutilizables
- Parte de pipeline de CI/CD
- Herramientas de desarrollo

#### Configuración de Agente

**Tipo:** Archivo JSON de configuración de agente

**Ubicación canónica:**
```
scripts/coding/ai/config/{agente}_config.json
```

**Ejemplos:**
- `scripts/coding/ai/config/test_generation.json`
- `scripts/coding/ai/config/doc_cleanup.json`

**Estructura:**
```json
{
  "version": "1.0",
  "agents": {
    "sub_agent_1": {
      "param1": value
    }
  }
}
```

**Cuándo usar:**
- Configuración parametrizable de agentes
- Perfiles de ejecución (aggressive, conservative, dry-run)

### 📋 TASKs y Solicitudes

#### TASK (Tarea Técnica)

**Tipo:** Tarea de desarrollo, refactoring, feature

**Ubicación canónica (por dominio):**
```
docs/{dominio}/TASK-{NNN}-{descripcion_underscores}.md
```

**Ubicación canónica (transversal):**
```
docs/gobernanza/TASK-{NNN}-{descripcion_underscores}.md
```

**Ejemplos:**
- `docs/backend/TASK-001-modularizacion_backend.md`
- `docs/frontend/TASK-011-ui_component_library.md`
- `docs/gobernanza/TASK-063-codigo_limpio.md`

**Frontmatter:**
```yaml
---
id: TASK-001
tipo: tarea
categoria: desarrollo
dominio: backend
prioridad: alta
estado: en_progreso
fecha_creacion: 2025-11-16
asignado: equipo-backend
relacionado: ["ADR-001", "REQ-005"]
---
```

**Naming:** `TASK-{NNN}-{descripcion_underscores}.md`

**Placement Logic:**
1. Si es específica de un dominio → `docs/{dominio}/`
2. Si es transversal (afecta múltiples dominios) → `docs/gobernanza/`
3. Si es DevOps/CI-CD → `docs/devops/`

#### Solicitud de Cambio

**Tipo:** Solicitud formal de cambio/feature

**Ubicación canónica (transversal):**
```
docs/gobernanza/solicitudes/REQ-{NNN}-{descripcion}.md
```

**Ubicación canónica (dominio):**
```
docs/{dominio}/solicitudes/REQ-{NNN}-{descripcion}.md
```

**Ejemplos:**
- `docs/gobernanza/solicitudes/REQ-001-sistema_autenticacion.md`
- `docs/backend/solicitudes/REQ-015-api_graphql.md`

**Frontmatter:**
```yaml
---
id: REQ-001
tipo: solicitud
categoria: feature
prioridad: alta
solicitante: product-owner
fecha: 2025-11-16
estado: aprobada
---
```

**Placement Logic:**
1. Solicitudes de alto nivel → `docs/gobernanza/solicitudes/`
2. Solicitudes específicas de dominio → `docs/{dominio}/solicitudes/`

### 🏗️ Arquitectura y Diseño

#### ADR (Architecture Decision Record)

**Tipo:** Decisión de arquitectura

**Ubicación canónica:**
```
docs/gobernanza/adr/ADR-{NNN}-{descripcion_underscores}.md
```

**Ejemplos:**
- `docs/gobernanza/adr/ADR-010-arquitectura_por_dominios.md`
- `docs/gobernanza/adr/ADR-015-clean_code_naming.md`

**Frontmatter:**
```yaml
---
id: ADR-010
tipo: adr
categoria: arquitectura
fecha: 2025-11-16
estado: aceptado
supersede: []
superseded_by: []
---
```

**Naming:** `ADR-{NNN}-{descripcion_underscores}.md`

**Nota:** SIEMPRE en `docs/gobernanza/adr/`, nunca en dominios.

#### Diseño Detallado (Dominio-Específico)

**Tipo:** Diseño técnico de módulo/componente

**Ubicación canónica:**
```
docs/{dominio}/diseno_detallado/{componente}.md
```

**Ejemplos:**
- `docs/backend/diseno_detallado/api_authentication.md`
- `docs/frontend/diseno_detallado/dashboard_components.md`

**Frontmatter:**
```yaml
---
id: DIS-BACKEND-AUTH
tipo: diseno
categoria: tecnico
dominio: backend
componente: authentication
fecha: 2025-11-16
---
```

**Placement Logic:**
- SIEMPRE en el dominio correspondiente
- NUNCA en gobernanza/ (gobernanza solo tiene estándares, no diseños específicos)

#### Diagrama (Alto Nivel)

**Tipo:** Diagrama de arquitectura de alto nivel (PlantUML, Mermaid)

**Ubicación canónica:**
```
docs/gobernanza/anexos/diagramas/{nombre_diagrama}.{puml|mmd}
```

**Ejemplos:**
- `docs/gobernanza/anexos/diagramas/arquitectura_general.puml`
- `docs/gobernanza/anexos/diagramas/flujo_autenticacion.mmd`

**Placement Logic:**
- Diagramas de alto nivel (sistema completo) → `gobernanza/anexos/diagramas/`
- Diagramas de dominio específico → `{dominio}/diseno_detallado/diagramas/`

#### Diagrama (Dominio-Específico)

**Tipo:** Diagrama técnico de componente/módulo

**Ubicación canónica:**
```
docs/{dominio}/diseno_detallado/diagramas/{nombre_diagrama}.{puml|mmd}
```

**Ejemplos:**
- `docs/backend/diseno_detallado/diagramas/database_schema.puml`
- `docs/frontend/diseno_detallado/diagramas/component_hierarchy.mmd`

### 📚 Guías y Procedimientos

#### Guía Transversal

**Tipo:** Guía que aplica a todo el proyecto

**Ubicación canónica:**
```
docs/gobernanza/guias/{NOMBRE_GUIA}.md
```

**Ejemplos:**
- `docs/gobernanza/guias/GUIA_ESTILO.md`
- `docs/gobernanza/guias/GUIA_CONTRIBUCION.md`
- `docs/gobernanza/guias/GUIA_UBICACIONES_ARTEFACTOS.md` (este documento)

**Frontmatter:**
```yaml
---
id: GUIA-{NOMBRE}
tipo: guia
categoria: gobernanza
version: 1.0.0
fecha: 2025-11-16
autor: equipo-arquitectura
---
```

**Placement Logic:**
- Si aplica a TODO el proyecto → `gobernanza/guias/`
- Si es específica de dominio → `{dominio}/guias/`

#### Guía Específica de Dominio

**Tipo:** Guía de desarrollo/uso de dominio específico

**Ubicación canónica:**
```
docs/{dominio}/guias/{nombre_guia}.md
```

**Ejemplos:**
- `docs/backend/guias/guia_desarrollo_api.md`
- `docs/frontend/guias/guia_componentes_react.md`

#### Procedimiento

**Tipo:** Procedimiento operativo (runbook, proceso)

**Ubicación canónica (transversal):**
```
docs/gobernanza/procedimientos/{nombre_procedimiento}.md
```

**Ubicación canónica (dominio):**
```
docs/{dominio}/procedimientos/{nombre_procedimiento}.md
```

**Ejemplos:**
- `docs/gobernanza/procedimientos/proceso_release.md`
- `docs/backend/procedimientos/deploy_api.md`

**Placement Logic:**
- Procedimientos organizacionales → `gobernanza/procedimientos/`
- Procedimientos técnicos de dominio → `{dominio}/procedimientos/`

### 🧪 Testing y QA

#### Estrategia de Testing (Transversal)

**Tipo:** Estrategia de QA para todo el proyecto

**Ubicación canónica:**
```
docs/gobernanza/qa/estrategia_qa.md
```

#### Plan de Testing (Dominio)

**Tipo:** Plan de tests específico de dominio

**Ubicación canónica:**
```
docs/{dominio}/testing/plan_testing_{componente}.md
```

**Ejemplos:**
- `docs/backend/testing/plan_testing_api.md`
- `docs/frontend/testing/plan_testing_components.md`

#### Registro de Ejecución de Tests

**Tipo:** Log/reporte de ejecución de tests

**Ubicación canónica:**
```
docs/gobernanza/qa/registros/YYYY_MM_DD_ejecucion_{tipo_test}.md
```

**Ejemplos:**
- `docs/gobernanza/qa/registros/2025_11_16_ejecucion_pytest.md`
- `docs/gobernanza/qa/registros/2025_11_16_ejecucion_e2e.md`

**Placement Logic:**
- Registros de ejecución transversal → `gobernanza/qa/registros/`
- Registros de dominio específico → `{dominio}/qa/registros/`

### 🔧 DevOps y CI/CD

#### Documentación de Pipeline CI/CD

**Tipo:** Documentación de workflow de CI/CD

**Ubicación canónica:**
```
docs/devops/ci_cd/{nombre_pipeline}.md
```

**Ejemplos:**
- `docs/devops/ci_cd/pipeline_tests.md`
- `docs/devops/ci_cd/pipeline_deploy.md`

#### Script de DevOps

**Tipo:** Script de automatización DevOps (deploy, build, etc.)

**Ubicación canónica:**
```
docs/devops/{categoria}/{nombre_script}.sh
```

**Ejemplos:**
- `docs/devops/git/execute_merge_strategy.sh`
- `docs/devops/automatizacion/deploy_staging.sh`

**Placement Logic:**
- Scripts Git → `devops/git/`
- Scripts deploy → `devops/automatizacion/`
- Configs infraestructura → `devops/infraestructura/`

#### Pre-commit Hook Documentation

**Tipo:** Documentación de hooks pre-commit

**Ubicación canónica:**
```
docs/devops/git/pre-commit-hooks.md
```

### 📦 Configuración y Metadatos

#### Configuración de Gobernanza

**Tipo:** Archivo de configuración de gobernanza (.yaml, .json)

**Ubicación canónica:**
```
docs/gobernanza/{nombre_config}.yaml
```

**Ejemplos:**
- `docs/gobernanza/constitucion.yaml`
- `docs/gobernanza/code_owners.yaml`

#### Plantilla

**Tipo:** Plantilla reutilizable de documento

**Ubicación canónica:**
```
docs/gobernanza/plantillas/plantilla_{tipo}.md
```

**Ejemplos:**
- `docs/gobernanza/plantillas/plantilla_task.md`
- `docs/gobernanza/plantillas/plantilla_adr.md`
- `docs/gobernanza/plantillas/plantilla_api_reference.md`

**Placement Logic:**
- SIEMPRE en `gobernanza/plantillas/`
- NUNCA duplicar en dominios

### 📂 Índices y Catálogos

#### Índice de Dominio

**Tipo:** Índice de navegación de dominio

**Ubicación canónica:**
```
docs/{dominio}/INDEX.md
```

**Ejemplos:**
- `docs/backend/INDEX.md`
- `docs/frontend/INDEX.md`

**Contenido requerido:**
1. Estructura de 12 subdirectorios
2. Conteo de archivos
3. TASKs del dominio
4. Contenido destacado

#### Índice Principal

**Tipo:** Índice de navegación principal

**Ubicación canónica:**
```
docs/INDEX.md
```

**Contenido requerido:**
1. Estructura de dominios
2. Links a índices de dominios
3. Links a gobernanza y devops

#### Catálogo de TODOs

**Tipo:** Catálogo de TODOs pendientes

**Ubicación canónica:**
```
docs/catalogo_todos_pendientes.md
```

**Nota:** Ubicación en root docs/ para fácil acceso.

## Algoritmo de Clasificación y Placement

### Algoritmo Programático

Este algoritmo puede implementarse en Python o usarse como guía mental para clasificar artefactos:

```python
def clasificar_y_ubicar_artefacto(
    nombre_archivo: str,
    contenido: str,
    tipo_declarado: str = None,
    contexto: dict = None
) -> dict:
    """
    Clasifica artefacto y determina ubicación canónica.

    Args:
        nombre_archivo: Nombre del archivo
        contenido: Contenido del archivo (para análisis)
        tipo_declarado: Tipo declarado por usuario (opcional)
        contexto: Contexto adicional (dominio, temporal, etc.)

    Returns:
        {
            "tipo": str,  # Tipo de artefacto
            "ubicacion": str,  # Ubicación canónica
            "nombre_sugerido": str,  # Nombre siguiendo convenciones
            "frontmatter": dict,  # Frontmatter sugerido
            "confianza": float  # 0.0-1.0
        }
    """
    contexto = contexto or {}

    # 1. Detectar tipo si no está declarado
    if not tipo_declarado:
        tipo_detectado = detectar_tipo(nombre_archivo, contenido)
    else:
        tipo_detectado = normalizar_tipo(tipo_declarado)

    # 2. Determinar ownership (transversal vs dominio)
    ownership = determinar_ownership(tipo_detectado, contexto, contenido)

    # 3. Determinar temporalidad
    temporalidad = determinar_temporalidad(tipo_detectado, contexto)

    # 4. Construir ubicación
    ubicacion = construir_ubicacion(
        tipo=tipo_detectado,
        ownership=ownership,
        temporalidad=temporalidad,
        contexto=contexto
    )

    # 5. Construir nombre siguiendo convenciones
    nombre_sugerido = construir_nombre(
        tipo=tipo_detectado,
        nombre_original=nombre_archivo,
        contexto=contexto
    )

    # 6. Generar frontmatter
    frontmatter = generar_frontmatter(
        tipo=tipo_detectado,
        contexto=contexto
    )

    # 7. Calcular confianza
    confianza = calcular_confianza(
        tipo_declarado=tipo_declarado,
        tipo_detectado=tipo_detectado,
        matches=analizar_coincidencias(contenido, tipo_detectado)
    )

    return {
        "tipo": tipo_detectado,
        "ubicacion": ubicacion,
        "nombre_sugerido": nombre_sugerido,
        "frontmatter": frontmatter,
        "confianza": confianza
    }


def detectar_tipo(nombre: str, contenido: str) -> str:
    """
    Detecta tipo de artefacto basado en nombre y contenido.
    """
    # Patrones de nombres
    if nombre.startswith("TASK-"):
        return "task"
    elif nombre.startswith("ADR-"):
        return "adr"
    elif nombre.startswith("REQ-"):
        return "solicitud"
    elif nombre.startswith("ANALISIS_"):
        return "analisis"
    elif nombre.startswith("SESSION_"):
        return "sesion"
    elif nombre.startswith("CLEANUP_REPORT_"):
        return "reporte_limpieza"
    elif nombre.startswith("README_") and "Agent" in contenido:
        return "documentacion_agente"
    elif nombre.endswith("_config.json"):
        return "configuracion_agente"
    elif nombre.endswith(".sh") or nombre.endswith(".py"):
        return "script"
    elif "GUIA" in nombre.upper():
        return "guia"
    elif nombre == "INDEX.md":
        return "indice"

    # Análisis de contenido
    if "## Sub-Agentes" in contenido and "## Arquitectura" in contenido:
        return "documentacion_agente"
    elif "## Descripción" in contenido and "## Contexto" in contenido:
        return "analisis"
    elif "## Status" in contenido and "## Decisión" in contenido:
        return "adr"

    # Default
    return "documento_general"


def determinar_ownership(tipo: str, contexto: dict, contenido: str) -> str:
    """
    Determina si es transversal, dominio-específico, o agente.
    """
    TIPOS_SIEMPRE_TRANSVERSALES = ["adr", "guia_transversal", "plantilla"]
    TIPOS_SIEMPRE_AGENTE = ["documentacion_agente", "configuracion_agente", "script"]
    TIPOS_SIEMPRE_DEVOPS = ["pipeline_ci_cd", "script_devops"]

    # Verificar tipos fijos
    if tipo in TIPOS_SIEMPRE_TRANSVERSALES:
        return "transversal"
    elif tipo in TIPOS_SIEMPRE_AGENTE:
        return "agente"
    elif tipo in TIPOS_SIEMPRE_DEVOPS:
        return "devops"

    # Verificar contexto
    if contexto.get("dominio"):
        return f"dominio:{contexto['dominio']}"

    # Análisis de contenido
    dominios_mencionados = detectar_dominios_en_contenido(contenido)

    if len(dominios_mencionados) == 1:
        return f"dominio:{dominios_mencionados[0]}"
    elif len(dominios_mencionados) > 1:
        return "transversal"

    # Default: preguntar
    return "REQUIERE_CLARIFICACION"


def determinar_temporalidad(tipo: str, contexto: dict) -> str:
    """
    Determina si es temporal, permanente, o histórico.
    """
    TIPOS_TEMPORALES = ["script"]  # Scripts por defecto temporales
    TIPOS_HISTORICOS = ["analisis", "reporte_limpieza", "sesion"]

    if contexto.get("temporal") == True:
        return "temporal"
    elif tipo in TIPOS_HISTORICOS:
        return "historico"
    elif tipo in TIPOS_TEMPORALES and not contexto.get("reutilizable"):
        return "temporal"
    else:
        return "permanente"


def construir_ubicacion(tipo: str, ownership: str, temporalidad: str, contexto: dict) -> str:
    """
    Construye ubicación canónica del artefacto.
    """
    from datetime import datetime

    # Mapeo de tipos a ubicaciones
    UBICACIONES = {
        # Análisis y reportes (históricos)
        "analisis": lambda: f"docs/gobernanza/sesiones/analisis_{datetime.now().strftime('%Y_%m')}/",
        "reporte_limpieza": lambda: f"docs/gobernanza/sesiones/analisis_{datetime.now().strftime('%Y_%m')}/",
        "sesion": lambda: "docs/gobernanza/sesiones/",

        # Arquitectura y decisiones
        "adr": lambda: "docs/gobernanza/adr/",

        # Guías y procedimientos
        "guia": lambda: "docs/gobernanza/guias/" if ownership == "transversal"
                        else f"docs/{ownership.split(':')[1]}/guias/",
        "procedimiento": lambda: "docs/gobernanza/procedimientos/" if ownership == "transversal"
                                 else f"docs/{ownership.split(':')[1]}/procedimientos/",

        # TASKs y solicitudes
        "task": lambda: "docs/gobernanza/" if ownership == "transversal"
                        else f"docs/{ownership.split(':')[1]}/",
        "solicitud": lambda: "docs/gobernanza/solicitudes/" if ownership == "transversal"
                             else f"docs/{ownership.split(':')[1]}/solicitudes/",

        # Diseño
        "diseno_detallado": lambda: f"docs/{ownership.split(':')[1]}/diseno_detallado/",
        "diagrama": lambda: "docs/gobernanza/anexos/diagramas/" if ownership == "transversal"
                            else f"docs/{ownership.split(':')[1]}/diseno_detallado/diagramas/",

        # Testing
        "plan_testing": lambda: f"docs/{ownership.split(':')[1]}/testing/",
        "registro_qa": lambda: "docs/gobernanza/qa/registros/",

        # Agentes
        "documentacion_agente": lambda: "scripts/coding/ai/agents/",
        "configuracion_agente": lambda: "scripts/coding/ai/config/",
        "script": lambda: "/tmp/" if temporalidad == "temporal"
                          else "scripts/coding/ai/automation/",

        # DevOps
        "pipeline_ci_cd": lambda: "docs/devops/ci_cd/",
        "script_devops": lambda: "docs/devops/git/" if "git" in contexto.get("categoria", "")
                                 else "docs/devops/automatizacion/",

        # Plantillas
        "plantilla": lambda: "docs/gobernanza/plantillas/",

        # Índices
        "indice": lambda: f"docs/{contexto.get('dominio')}/" if contexto.get('dominio')
                          else "docs/",
    }

    if tipo in UBICACIONES:
        return UBICACIONES[tipo]()

    # Default
    return "docs/"


def construir_nombre(tipo: str, nombre_original: str, contexto: dict) -> str:
    """
    Construye nombre siguiendo convenciones del tipo.
    """
    from datetime import datetime

    FORMATOS = {
        "task": lambda: f"TASK-{contexto.get('id', '001')}-{normalizar_descripcion(contexto.get('descripcion', 'nueva_tarea'))}.md",
        "adr": lambda: f"ADR-{contexto.get('id', '001')}-{normalizar_descripcion(contexto.get('descripcion', 'nueva_decision'))}.md",
        "solicitud": lambda: f"REQ-{contexto.get('id', '001')}-{normalizar_descripcion(contexto.get('descripcion', 'nueva_solicitud'))}.md",
        "analisis": lambda: f"ANALISIS_{contexto.get('tema', 'GENERAL').upper()}_{datetime.now().strftime('%Y%m%d')}.md",
        "reporte_limpieza": lambda: f"CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d')}.md",
        "sesion": lambda: f"SESSION_{contexto.get('tema', 'GENERAL').upper()}_{datetime.now().strftime('%Y_%m_%d')}.md",
        "documentacion_agente": lambda: f"README_{contexto.get('nombre_agente', 'NEW_AGENT').upper()}.md",
        "configuracion_agente": lambda: f"{contexto.get('nombre_agente', 'agent')}_config.json",
        "guia": lambda: f"GUIA_{contexto.get('tema', 'GENERAL').upper()}.md",
        "indice": lambda: "INDEX.md",
        "script": lambda: f"{contexto.get('accion', 'process')}_{contexto.get('objeto', 'data')}.{contexto.get('extension', 'sh')}",
    }

    if tipo in FORMATOS:
        return FORMATOS[tipo]()

    # Default: snake_case
    return normalizar_nombre(nombre_original)


def generar_frontmatter(tipo: str, contexto: dict) -> dict:
    """
    Genera frontmatter YAML apropiado para el tipo.
    """
    from datetime import datetime

    BASE = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "tipo": tipo,
    }

    FRONTMATTER_POR_TIPO = {
        "task": {
            "id": contexto.get("id", "TASK-001"),
            "categoria": contexto.get("categoria", "desarrollo"),
            "dominio": contexto.get("dominio", "transversal"),
            "prioridad": contexto.get("prioridad", "media"),
            "estado": "pendiente",
            "asignado": contexto.get("asignado", ""),
            "relacionado": contexto.get("relacionado", []),
        },
        "adr": {
            "id": contexto.get("id", "ADR-001"),
            "categoria": "arquitectura",
            "estado": "propuesto",
            "supersede": [],
            "superseded_by": [],
        },
        "analisis": {
            "categoria": contexto.get("categoria", "documentacion"),
            "autor": contexto.get("autor", "agente-cleanup"),
            "relacionado": contexto.get("relacionado", []),
        },
        "documentacion_agente": {
            "id": contexto.get("id", "AGENT-NEW"),
            "categoria": contexto.get("categoria", "documentacion"),
            "version": "1.0.0",
            "autor": "equipo-arquitectura",
            "status": "active",
        },
        "guia": {
            "id": f"GUIA-{contexto.get('tema', 'GENERAL').upper()}",
            "categoria": "gobernanza",
            "version": "1.0.0",
            "autor": "equipo-arquitectura",
        },
    }

    specific = FRONTMATTER_POR_TIPO.get(tipo, {})
    return {**BASE, **specific}


def detectar_dominios_en_contenido(contenido: str) -> list:
    """
    Detecta qué dominios se mencionan en el contenido.
    """
    DOMINIOS = ["backend", "frontend", "infraestructura", "ai"]
    mencionados = []

    contenido_lower = contenido.lower()
    for dominio in DOMINIOS:
        if dominio in contenido_lower:
            mencionados.append(dominio)

    return mencionados


def normalizar_descripcion(desc: str) -> str:
    """
    Normaliza descripción a snake_case sin emojis.
    """
    import re
    # Eliminar emojis y caracteres especiales
    desc = re.sub(r'[^\w\s-]', '', desc)
    # Convertir a lowercase y reemplazar espacios/guiones por underscores
    desc = desc.lower().replace(' ', '_').replace('-', '_')
    # Eliminar underscores múltiples
    desc = re.sub(r'_+', '_', desc)
    return desc.strip('_')


def normalizar_nombre(nombre: str) -> str:
    """
    Normaliza nombre de archivo a snake_case.
    """
    import re
    # Mantener extensión
    partes = nombre.rsplit('.', 1)
    base = partes[0]
    ext = partes[1] if len(partes) > 1 else ''

    # Normalizar base
    base = normalizar_descripcion(base)

    return f"{base}.{ext}" if ext else base


def normalizar_tipo(tipo_declarado: str) -> str:
    """
    Normaliza tipo declarado por usuario a tipo canónico.
    """
    ALIASES = {
        "análisis": "analisis",
        "reporte": "analisis",
        "report": "analisis",
        "cleanup": "reporte_limpieza",
        "limpieza": "reporte_limpieza",
        "tarea": "task",
        "decision": "adr",
        "agente": "documentacion_agente",
        "script": "script",
        "guía": "guia",
        "guide": "guia",
        "índice": "indice",
        "index": "indice",
    }

    return ALIASES.get(tipo_declarado.lower(), tipo_declarado.lower())


def calcular_confianza(tipo_declarado: str, tipo_detectado: str, matches: dict) -> float:
    """
    Calcula confianza en la clasificación (0.0-1.0).
    """
    confianza = 0.5  # Base

    # Boost si tipo declarado coincide con detectado
    if tipo_declarado and tipo_declarado == tipo_detectado:
        confianza += 0.3

    # Boost por matches en contenido
    if matches.get("nombre_correcto"):
        confianza += 0.1
    if matches.get("frontmatter_presente"):
        confianza += 0.1
    if matches.get("estructura_correcta"):
        confianza += 0.1

    return min(confianza, 1.0)


def analizar_coincidencias(contenido: str, tipo: str) -> dict:
    """
    Analiza coincidencias entre contenido y tipo esperado.
    """
    return {
        "nombre_correcto": True,  # Simplificado
        "frontmatter_presente": contenido.startswith("---"),
        "estructura_correcta": "##" in contenido,
    }
```

### Decisiones Contextuales

Para casos donde el contexto determina la ubicación:

```python
def decidir_por_contexto(tipo: str, contexto_detectado: dict) -> str:
    """
    Decide ubicación basada en contexto específico.

    Contexto incluye:
    - dominio: backend|frontend|infraestructura|ai
    - afecta_multiples_dominios: bool
    - temporal: bool
    - reutilizable: bool
    - categoria: git|ci_cd|testing|etc
    """
    reglas_contextuales = {
        # (tipo, afecta_múltiples, dominio) → ubicación
        ("task", True, None): "docs/gobernanza/",
        ("task", False, "backend"): "docs/backend/",
        ("task", False, "frontend"): "docs/frontend/",

        ("solicitud", True, None): "docs/gobernanza/solicitudes/",
        ("solicitud", False, "backend"): "docs/backend/solicitudes/",

        ("guia", True, None): "docs/gobernanza/guias/",
        ("guia", False, "backend"): "docs/backend/guias/",

        ("script", None, "git"): "docs/devops/git/",
        ("script", None, "ci_cd"): "docs/devops/automatizacion/",
        ("script", None, "agente"): "scripts/coding/ai/automation/",

        ("diagrama", True, None): "docs/gobernanza/anexos/diagramas/",
        ("diagrama", False, "backend"): "docs/backend/diseno_detallado/diagramas/",

        # Siempre en ubicación fija
        ("adr", None, None): "docs/gobernanza/adr/",
        ("plantilla", None, None): "docs/gobernanza/plantillas/",
        ("documentacion_agente", None, None): "scripts/coding/ai/agents/",
    }

    # Construir key
    key = (
        tipo,
        contexto_detectado.get("afecta_multiples_dominios"),
        contexto_detectado.get("dominio") or contexto_detectado.get("categoria")
    )

    return reglas_contextuales.get(key, "ANALIZAR_MANUAL")
```

### Ejemplo de Uso

```python
# Caso 1: Usuario pide "genera un análisis de documentación"
resultado = clasificar_y_ubicar_artefacto(
    nombre_archivo="analisis_docs.md",
    contenido="## Análisis de Estructura\n\n...",
    tipo_declarado="análisis",
    contexto={
        "tema": "DOCS_ESTRUCTURA",
        "autor": "agente-cleanup"
    }
)

print(resultado)
# {
#     "tipo": "analisis",
#     "ubicacion": "docs/gobernanza/sesiones/analisis_2025_11/",
#     "nombre_sugerido": "ANALISIS_DOCS_ESTRUCTURA_20251116.md",
#     "frontmatter": {
#         "fecha": "2025-11-16",
#         "tipo": "analisis",
#         "categoria": "documentacion",
#         "autor": "agente-cleanup"
#     },
#     "confianza": 0.9
# }


# Caso 2: Usuario pide "crea una TASK para implementar autenticación en backend y frontend"
resultado = clasificar_y_ubicar_artefacto(
    nombre_archivo="task_autenticacion.md",
    contenido="## Implementar Autenticación\n\nAfecta backend (API) y frontend (UI)...",
    tipo_declarado="tarea",
    contexto={
        "id": "050",
        "descripcion": "implementar autenticacion",
        "dominio": None,  # Afecta múltiples dominios
        "afecta_multiples_dominios": True
    }
)

print(resultado)
# {
#     "tipo": "task",
#     "ubicacion": "docs/gobernanza/",
#     "nombre_sugerido": "TASK-050-implementar_autenticacion.md",
#     "frontmatter": {
#         "fecha": "2025-11-16",
#         "tipo": "task",
#         "id": "TASK-050",
#         "dominio": "transversal",
#         "prioridad": "media",
#         "estado": "pendiente"
#     },
#     "confianza": 0.8
# }


# Caso 3: Script temporal de análisis
resultado = clasificar_y_ubicar_artefacto(
    nombre_archivo="analyze_structure.sh",
    contenido="#!/bin/bash\nfind docs -name '*.md'...",
    tipo_declarado="script",
    contexto={
        "accion": "analyze",
        "objeto": "domain_structure",
        "temporal": True,
        "reutilizable": False
    }
)

print(resultado)
# {
#     "tipo": "script",
#     "ubicacion": "/tmp/",
#     "nombre_sugerido": "analyze_domain_structure.sh",
#     "frontmatter": {},
#     "confianza": 0.7
# }
```

## Árbol de Decisión para Placement

### Paso 1: ¿Qué tipo de artefacto es?

```
┌─ Análisis/Reporte ────────────► docs/gobernanza/sesiones/analisis_YYYY_MM/
│
├─ TASK ───────────────────────┬─ Transversal ────► docs/gobernanza/
│                              └─ Dominio ─────────► docs/{dominio}/
│
├─ ADR ────────────────────────► docs/gobernanza/adr/
│
├─ Solicitud (REQ) ────────────┬─ Alto nivel ─────► docs/gobernanza/solicitudes/
│                              └─ Dominio ─────────► docs/{dominio}/solicitudes/
│
├─ Guía ───────────────────────┬─ Transversal ────► docs/gobernanza/guias/
│                              └─ Dominio ─────────► docs/{dominio}/guias/
│
├─ Diseño Detallado ───────────► docs/{dominio}/diseno_detallado/
│
├─ Diagrama ───────────────────┬─ Alto nivel ─────► docs/gobernanza/anexos/diagramas/
│                              └─ Dominio ─────────► docs/{dominio}/diseno_detallado/diagramas/
│
├─ Script ─────────────────────┬─ Temporal ───────► /tmp/
│                              ├─ Agente ─────────► scripts/coding/ai/
│                              └─ DevOps ─────────► docs/devops/
│
├─ Documentación Agente ───────► scripts/coding/ai/agents/README_{AGENTE}.md
│
├─ Configuración Agente ───────► scripts/coding/ai/config/{agente}_config.json
│
├─ QA/Testing ─────────────────┬─ Estrategia ─────► docs/gobernanza/qa/
│                              ├─ Plan ───────────► docs/{dominio}/testing/
│                              └─ Registros ──────► docs/gobernanza/qa/registros/
│
├─ DevOps/CI-CD ───────────────► docs/devops/{subcategoria}/
│
├─ Plantilla ──────────────────► docs/gobernanza/plantillas/
│
└─ Índice ─────────────────────┬─ Dominio ────────► docs/{dominio}/INDEX.md
                               └─ Principal ─────► docs/INDEX.md
```

### Paso 2: ¿Es transversal o dominio-específico?

**Transversal (afecta todo el proyecto):**
- → `docs/gobernanza/`
- → `docs/devops/`

**Dominio-específico (solo afecta backend, frontend, etc.):**
- → `docs/{dominio}/`

**Agentes/Automatización:**
- → `scripts/coding/ai/`

### Paso 3: ¿Es temporal o permanente?

**Temporal (se puede eliminar después):**
- → `/tmp/`

**Permanente (parte del proyecto):**
- → `docs/` o `scripts/`

**Histórico (registro de sesión):**
- → `docs/gobernanza/sesiones/`

## Convenciones de Naming

### Por Tipo de Artefacto

| Tipo | Formato | Ejemplo |
|------|---------|---------|
| TASK | `TASK-{NNN}-{descripcion_underscores}.md` | `TASK-001-modularizacion_backend.md` |
| ADR | `ADR-{NNN}-{descripcion_underscores}.md` | `ADR-010-arquitectura_por_dominios.md` |
| Solicitud | `REQ-{NNN}-{descripcion}.md` | `REQ-001-sistema_autenticacion.md` |
| Análisis | `ANALISIS_{TEMA}_{YYYYMMDD}.md` | `ANALISIS_DOCS_ESTRUCTURA_20251116.md` |
| Reporte | `{TIPO}_REPORT_{YYYYMMDD}.md` | `CLEANUP_REPORT_20251116.md` |
| Sesión | `SESSION_{TEMA}_{YYYY_MM_DD}.md` | `SESSION_PIPELINE_2025_11_13.md` |
| Guía | `GUIA_{TEMA}.md` o `{tema}_guide.md` | `GUIA_ESTILO.md` |
| Script temporal | `{accion}_{objeto}.sh` | `analyze_domain_structure.sh` |
| Script permanente | `{nombre_descriptivo}.{sh\|py}` | `cleanup_docs.sh` |
| Agente | `README_{AGENTE_NAME}.md` | `README_DOCUMENTATION_CLEANUP.md` |
| Config agente | `{agente}_config.json` | `doc_cleanup_config.json` |
| Índice | `INDEX.md` | `INDEX.md` |
| Archivo normal | `{nombre_snake_case}.md` | `arquitectura_general.md` |
| Archivo especial | `{UPPERCASE}.md` | `README.md`, `CHANGELOG.md` |

### Reglas Generales

1. ✅ **IDs numéricos:** Usar 3 dígitos con padding (001, 002, ..., 999)
2. ✅ **Fechas:** Formato YYYYMMDD o YYYY_MM_DD según contexto
3. ✅ **Separadores:**
   - Guión `-` para IDs (`TASK-001`)
   - Underscore `_` para descripción (`descripcion_larga`)
4. ✅ **Sin emojis** en nombres de archivo
5. ✅ **Sin espacios** en nombres de archivo
6. ✅ **Lowercase** para archivos normales, UPPERCASE para especiales

## Frontmatter YAML por Tipo

### TASK
```yaml
---
id: TASK-001
tipo: tarea
categoria: desarrollo|refactoring|feature|bugfix
dominio: backend|frontend|infraestructura|ai|transversal
prioridad: alta|media|baja
estado: pendiente|en_progreso|bloqueado|completado
fecha_creacion: 2025-11-16
asignado: equipo-backend
relacionado: ["ADR-010", "REQ-005"]
---
```

### ADR
```yaml
---
id: ADR-010
tipo: adr
categoria: arquitectura|diseño|proceso
fecha: 2025-11-16
estado: propuesto|aceptado|rechazado|deprecado|superseded
supersede: []
superseded_by: []
---
```

### Análisis
```yaml
---
fecha: 2025-11-16
tipo: analisis
categoria: documentacion|tecnico|arquitectura|negocio
autor: agente-cleanup|equipo-arquitectura
relacionado: ["ADR-010"]
---
```

### Agente
```yaml
---
id: AGENT-{NAME}
tipo: agente
categoria: documentacion|testing|analisis
version: 1.0.0
fecha_creacion: 2025-11-16
autor: equipo-arquitectura
status: active|inactive|deprecated
---
```

### Guía
```yaml
---
id: GUIA-{NOMBRE}
tipo: guia
categoria: gobernanza|desarrollo|proceso
version: 1.0.0
fecha: 2025-11-16
autor: equipo-arquitectura
---
```

### Diseño
```yaml
---
id: DIS-{DOMINIO}-{COMPONENTE}
tipo: diseno
categoria: tecnico|conceptual
dominio: backend|frontend|infraestructura|ai
componente: {nombre_componente}
fecha: 2025-11-16
---
```

## Casos Especiales

### 1. Script Reutilizable Generado Durante Limpieza

**Escenario:** Generé un script útil en `/tmp/` que quiero mantener.

**Acción:**
```bash
# Mover a ubicación permanente
git mv /tmp/consolidate_tasks.sh scripts/coding/ai/automation/
```

**Nueva ubicación:** `scripts/coding/ai/automation/consolidate_tasks.sh`

### 2. Análisis que Combina Múltiples Temas

**Escenario:** Análisis que cubre documentación + arquitectura + duplicados.

**Naming:** Usar tema principal
```
ANALISIS_DOCS_ESTRUCTURA_20251116.md  (tema principal: docs)
```

**Contenido:** Incluir secciones para cada tema.

### 3. TASK que Afecta Múltiples Dominios

**Escenario:** TASK de autenticación que afecta backend (API) + frontend (UI).

**Ubicación:** `docs/gobernanza/` (transversal)
```
docs/gobernanza/TASK-050-implementar_autenticacion.md
```

**Referencia:** Mencionar en `docs/backend/INDEX.md` y `docs/frontend/INDEX.md`

### 4. Diagrama Usado en Múltiples Documentos

**Escenario:** Diagrama de arquitectura general usado en ADR, diseños, README.

**Ubicación:** `docs/gobernanza/anexos/diagramas/` (canónica)
```
docs/gobernanza/anexos/diagramas/arquitectura_general.puml
```

**Uso:** Referenciar con links relativos desde otros docs.

### 5. Configuración que Aplica a Múltiples Agentes

**Escenario:** Config común para varios agentes.

**Ubicación:** `scripts/coding/ai/config/shared_config.json`

**Referencia:** Importar desde configs específicas.

## Checklist de Validación

Antes de crear un artefacto, verificar:

- [ ] ✅ **Tipo identificado** - Sé qué tipo de artefacto es
- [ ] ✅ **Ubicación correcta** - Consulté el mapa de artefactos
- [ ] ✅ **Naming correcto** - Sigo la convención del tipo
- [ ] ✅ **Frontmatter completo** - Incluí metadata requerida
- [ ] ✅ **Ownership claro** - Sé si es transversal o dominio-específico
- [ ] ✅ **No duplica** - Verifiqué que no existe en otra ubicación

## Proceso de Consulta

### Para Agentes/Asistentes

Cuando un usuario pide "realiza un análisis de X":

1. **Identificar tipo:** ¿Qué tipo de análisis?
   - Documentación → `ANALISIS_DOCS_*`
   - Técnico → `ANALISIS_*`
   - Gap → `GAP_ANALYSIS_*`

2. **Determinar ubicación:**
   - Análisis → `docs/gobernanza/sesiones/analisis_YYYY_MM/`

3. **Construir nombre:**
   ```
   ANALISIS_{TEMA}_{YYYYMMDD}.md
   ```
   Ejemplo: `ANALISIS_DOCS_DUPLICADOS_20251116.md`

4. **Generar frontmatter:**
   ```yaml
   ---
   fecha: 2025-11-16
   tipo: analisis
   categoria: documentacion
   autor: agente-cleanup
   ---
   ```

5. **Guardar en ubicación correcta:**
   ```
   docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_DUPLICADOS_20251116.md
   ```

6. **Informar al usuario:**
   "Análisis guardado en: `docs/gobernanza/sesiones/analisis_nov_2025/ANALISIS_DOCS_DUPLICADOS_20251116.md`"

### Para Desarrolladores

Cuando creas un artefacto:

1. Consultar **Mapa de Artefactos** (sección arriba)
2. Identificar **tipo** de artefacto
3. Usar **Árbol de Decisión** si no está claro
4. Aplicar **convención de naming**
5. Incluir **frontmatter** requerido
6. Validar con **checklist**

## Actualización de Esta Guía

Esta guía debe actualizarse cuando:

- Se agrega un nuevo tipo de artefacto
- Se cambia una convención de ubicación
- Se crea un nuevo dominio
- Se identifica ambigüedad en placement

**Responsable:** Equipo de Arquitectura

**Proceso:**
1. Proponer cambio en PR
2. Revisar con equipo
3. Actualizar ADR relacionados si aplica
4. Actualizar esta guía
5. Notificar a equipo

## Referencias

- **ADR-010:** Arquitectura por Dominios
- **GUIA_ESTILO.md:** Convenciones de formato
- **README_DOCUMENTATION_CLEANUP.md:** Agente de limpieza
- **README_DOCUMENTATION_SYNC.md:** Agente de sincronización

---

**Versión:** 1.0.0
**Fecha:** 2025-11-16
**Autor:** equipo-arquitectura
**Revisores:** []
**Próxima revisión:** 2026-02-16
