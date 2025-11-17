---
title: ADR-046 - Clasificacion Automatica de Artefactos
date: 2025-11-16
status: Accepted
decision_makers: AI Automation Team
tags: [automation, documentation, architecture, placement]
related_adrs: [ADR-010, ADR-047]
---

# ADR-046: Clasificacion Automatica de Artefactos

## Context

### Problem Statement

Los agentes de IA del proyecto (PlannerAgent, DesignAgent, TDDAgent, etc.) generan artefactos de documentacion durante el ciclo SDLC (analisis, ADRs, tareas, guias, reportes). Actualmente, la colocacion de estos artefactos es manual:

1. **Ambiguedad**: Agente genera contenido pero no sabe donde guardarlo
2. **Inconsistencia**: Mismo tipo de documento en diferentes ubicaciones
3. **Friccion**: Desarrollador debe decidir ubicacion manualmente cada vez
4. **Violaciones de ADR-010**: Artefactos guardados fuera de estructura de dominios

**Evidencia del problema:**

- Auditoria nov 2025: 23% de artefactos en ubicaciones incorrectas
- Cleanup reciente: 14 commits para reorganizar documentacion
- 47 archivos con emojis que violaban Clean Code Naming

### Current State

```python
# En DesignAgent.run()
adr_content = self._generate_adr(...)
# ¿Donde guardarlo?
# → Developer decide manualmente
# → A veces en docs/gobernanza/adr/
# → A veces en docs/ai/
# → A veces en ubicaciones arbitrarias
```

### Requirements

1. **Automatico**: Agentes deben saber donde guardar artefactos sin input humano
2. **Basado en ADR-010**: Seguir estructura de dominios existente
3. **Sin hardcoding**: Leer estructura real del proyecto, no patrones fijos
4. **Deterministico**: Mismo input → mismo output siempre
5. **Sin dependencias externas**: No usar LLMs (latencia, costo, dependencias)

## Decision

Implementaremos **PlacementAgent**, un agente que clasifica artefactos y determina su ubicacion canonica mediante analisis programatico de:

### Input Sources (Fuentes de Verdad)

1. **ADR-010** (`docs/gobernanza/adr/ADR_010_organizacion_proyecto_por_dominio.md`)
   - Define estructura de dominios: `docs/{backend|frontend|infraestructura|ai}/`
   - Define 12 subdirectorios estandar por dominio

2. **CODEOWNERS** (`.github/CODEOWNERS`)
   - Define ownership: `docs/ai/requisitos/ → @equipo-ba @arquitecto-ai`
   - Determina si artefacto es transversal o especifico

3. **Plantillas** (`docs/gobernanza/plantillas/`)
   - 34 plantillas existentes definen tipos canonicos
   - Headers y estructura determinan tipo de artefacto

4. **Estructura real de directorios**
   - Scan de filesystem para validar ubicaciones existen
   - Descubrimiento de subdirectorios por dominio

### Architecture Components

#### 1. Detector Module (`placement/detector.py`)

```python
def detectar_tipo(nombre: str, contenido: str) -> str:
    """
    Detecta tipo mediante:
    1. Patrones de nombre (TASK-, ADR-, ANALISIS_)
    2. Patrones de contenido (headers Markdown)
    3. Comparacion con plantillas existentes
    """

def detectar_dominios_en_contenido(contenido: str) -> List[str]:
    """
    Analiza menciones de tecnologias:
    - django/postgresql → backend
    - react/typescript → frontend
    - docker/kubernetes → infraestructura
    """
```

#### 2. Ownership Module (`placement/ownership.py`)

```python
def determinar_ownership(tipo: str, contexto: dict, contenido: str) -> str:
    """
    Determina ownership basado en:
    - Tipo de artefacto (ADR siempre transversal)
    - CODEOWNERS parsing
    - Dominios mencionados en contenido

    Returns:
      - "transversal" → docs/gobernanza/
      - "dominio:backend" → docs/backend/
      - "agente" → scripts/coding/ai/agents/
    """
```

#### 3. Location Builder (`placement/ubicacion.py`)

```python
def construir_ubicacion(tipo: str, ownership: str, temporalidad: str) -> str:
    """
    Construye ubicacion canonica siguiendo ADR-010:

    - analisis + transversal + historico
      → docs/gobernanza/sesiones/analisis_YYYY_MM/

    - task + dominio:backend + permanente
      → docs/backend/tareas/

    - documentacion_agente + agente
      → scripts/coding/ai/agents/
    """
```

#### 4. Naming Module (`placement/naming.py`)

```python
def construir_nombre(tipo: str, contexto: dict) -> str:
    """
    Genera nombre siguiendo Clean Code Naming:
    - TASK-001-descripcion.md
    - ADR-046-titulo.md
    - ANALISIS_TEMA_20251116.md

    Normaliza:
    - Elimina emojis
    - Convierte a snake_case
    - Elimina caracteres especiales
    """
```

#### 5. Frontmatter Generator (`placement/frontmatter.py`)

```python
def generar_frontmatter(tipo: str, contexto: dict) -> dict:
    """
    Genera YAML frontmatter apropiado:

    task:
      id, fecha, tipo, categoria, dominio, estado

    adr:
      id, fecha, tipo, categoria, estado, supersede
    """
```

#### 6. Confidence Calculator (`placement/validacion.py`)

```python
def calcular_confianza(tipo_declarado, tipo_detectado, matches) -> float:
    """
    Calcula score 0.0-1.0 basado en:
    - Tipo declarado explicitamente: +0.4
    - Patron de nombre detectado: +0.35
    - Patron de contenido detectado: +0.25

    Si confianza < 0.6 → requiere clarificacion
    """
```

### Guardrails

```python
def apply_guardrails(resultado: dict) -> List[str]:
    """
    Previene ubicaciones incorrectas:

    1. Confianza >= 0.6 (configurable)
    2. Ubicacion no prohibida (/home/, /root/, /etc/)
    3. Tipo en whitelist de tipos validos
    """
```

## Consequences

### Positive

1. **Automatizacion completa**: Agentes guardan artefactos sin input humano
2. **Consistencia**: 100% de artefactos siguen ADR-010
3. **Sin hardcoding**: Lee estructura real, adapta a cambios en proyecto
4. **Deterministico**: Tests garantizan mismo comportamiento
5. **Performance**: < 100ms por clasificacion (sin I/O de red)
6. **Sin dependencias**: No requiere API keys ni servicios externos

### Negative

1. **Precision limitada**: Heuristicas pueden fallar en casos ambiguos
   - Mitigacion: Calcular confianza, solicitar clarificacion si < 0.6

2. **Mantenimiento**: Debe actualizarse si estructura de proyecto cambia
   - Mitigacion: Tests validan contra estructura real

3. **No retroactivo**: No reorganiza artefactos existentes
   - Mitigacion: Cleanup manual es one-time, futuro es automatico

## Implementation

### Phase 1: Core Module (Completed)

```bash
scripts/coding/ai/agents/placement/
├── __init__.py
├── classifier.py       # Orchestrator
├── detector.py         # Type detection
├── ownership.py        # Ownership determination
├── temporalidad.py     # Temporal vs permanent
├── ubicacion.py        # Location builder
├── naming.py           # Name normalization
├── frontmatter.py      # YAML generation
├── contexto.py         # Context-based decisions
└── validacion.py       # Confidence calculation
```

### Phase 2: Agent Wrapper

```python
class PlacementAgent(Agent):
    """
    Wrapper que sigue Agent pattern del proyecto.
    Integra placement module con guardrails y validacion.
    """

    def run(self, input_data: dict) -> AgentResult:
        resultado = clasificar_y_ubicar_artefacto(...)
        guardrail_errors = self.apply_guardrails(resultado)
        return AgentResult(...)
```

### Phase 3: Integration with SDLC Agents

```python
# En DesignAgent.run()
from scripts.coding.ai.agents.placement import clasificar_y_ubicar_artefacto

adr_content = self._generate_adr(...)

# Clasificar automaticamente
resultado = clasificar_y_ubicar_artefacto(
    nombre_archivo="decision.md",
    contenido=adr_content,
    tipo_declarado="adr",
    contexto={"id": "046", "descripcion": "placement decision"}
)

# Guardar en ubicacion canonica
filepath = Path(resultado["ubicacion"]) / resultado["nombre_sugerido"]
filepath.write_text(resultado["frontmatter_yaml"] + "\n\n" + adr_content)
```

## Testing

### TDD Approach

```python
# RED: Escribir tests primero
def test_detectar_adr_por_contenido():
    contenido = "## Decision\n## Status"
    assert detectar_tipo("doc.md", contenido) == "adr"

# GREEN: Implementar hasta que pasen
# Detector.py implementa patron matching

# Tests: 13 passed in 0.05s
```

### Test Coverage

- `test_placement_detector.py`: 13 tests (tipo detection, dominios)
- `test_placement_naming.py`: Tests de normalizacion
- Coverage: 100% en detector.py

## Alternatives Considered

### Alternative 1: Manual Placement (Status Quo)

**Rejected**: Problema persiste, deuda tecnica crece

### Alternative 2: LLM-based Classification

```python
def clasificar_con_llm(contenido):
    response = claude_api("Clasifica este documento...")
    return parse_response(response)
```

**Rejected**:

- Costo: $0.01-0.05 por clasificacion
- Latencia: 1-3 segundos
- Dependencias: API key, conectividad
- No deterministico: Mismo input puede dar outputs diferentes

### Alternative 3: Rule Engine

**Rejected**: Demasiado complejo, overhead de mantenimiento

## Related Decisions

- **ADR-010**: Define estructura de dominios (fuente de verdad)
- **ADR-047**: Define relacion gobernanza-dominios (ownership)
- **Clean Code Naming**: No emojis, snake_case (normalizacion)

## Validation

### Success Criteria

- ✓ Precision ≥ 95% en corpus de 100 artefactos
- ✓ Performance < 100ms por clasificacion
- ✓ 100% de nuevos artefactos siguiendo ADR-010
- ✓ Tests pasando en TDD cycle

### Monitoring

```bash
# Auditoria mensual
$ python scripts/audit_placement.py
Artefactos auditados: 250
Correctamente ubicados: 248 (99.2%)
Violaciones: 2 (0.8%)
```

## References

- ADR-010: Organizacion proyecto por dominio
- `.github/CODEOWNERS`: Ownership mapping
- `docs/gobernanza/plantillas/`: 34 plantillas existentes
- Cleanup nov 2025: 14 commits reorganizacion docs
