---
title: ADR-047 - Relacion entre Gobernanza y Dominios
date: 2025-11-16
status: Accepted
decision_makers: Architecture Team
tags: [architecture, organization, governance, domains]
related_adrs: [ADR-010, ADR-046]
---

# ADR-047: Relacion entre Gobernanza y Dominios

## Context

### Problem Statement

ADR-010 define organizacion por dominios (`docs/backend/`, `docs/frontend/`, `docs/infraestructura/`, `docs/ai/`), pero no clarifica la relacion con `docs/gobernanza/`. Esto genera ambiguedad:

1. **ADRs**: ¿Van en `docs/gobernanza/adr/` o `docs/ai/arquitectura/`?
2. **Plantillas**: ¿Son transversales o cada dominio tiene las suyas?
3. **Procedimientos**: ¿En `docs/gobernanza/procedimientos/` o `docs/backend/procedimientos/`?
4. **Ownership**: ¿Quien es responsable de artefactos transversales vs especificos?

**Problemas observados:**

- Duplicacion: Mismas plantillas en gobernanza/ y dominios
- Confusion: ADRs de IA a veces en gobernanza/, a veces en ai/
- CODEOWNERS ambiguo para contenido transversal

### Current State

```
docs/
├── gobernanza/              # ¿Que va aqui?
│   ├── adr/                 # ADRs... ¿de que?
│   ├── plantillas/          # Plantillas... ¿para quien?
│   └── procedimientos/      # Procedimientos... ¿de que dominio?
│
├── backend/                 # Dominio Backend
│   ├── arquitectura/        # ¿ADRs especificos backend?
│   ├── procedimientos/      # ¿Procedimientos backend?
│   └── ...
│
├── ai/                      # Dominio AI
│   ├── arquitectura/        # ¿ADRs especificos AI?
│   └── ...
```

### Requirements

1. **Clara separacion**: Definir que es transversal vs especifico
2. **Sin duplicacion**: Contenido vive en UN solo lugar
3. **Ownership explicito**: CODEOWNERS refleja responsabilidades reales
4. **Extensible**: Permite que dominios extiendan gobernanza

## Decision

Establecemos **jerarquia de ownership** donde `docs/gobernanza/` contiene contenido **transversal** que afecta a multiples dominios, y cada dominio extiende/especializa segun necesidad.

### Principio 1: Transversalidad

**Transversal** = Afecta a 2+ dominios o define estandares del proyecto completo

```yaml
Transversal (docs/gobernanza/):
  - ADRs arquitectonicos del proyecto completo
  - Plantillas genericas usadas por todos los dominios
  - Procedimientos que cruzan dominios
  - Guias de estilo/convenciones del proyecto
  - Constitution del proyecto

Especifico (docs/{dominio}/):
  - ADRs que solo afectan ese dominio
  - Procedimientos internos del dominio
  - Guias tecnicas especificas
```

### Principio 2: Jerarquia de Decision

```
docs/gobernanza/adr/              # Decisiones arquitectonicas nivel proyecto
    ├── ADR-010: Estructura por dominios (afecta todos)
    ├── ADR-046: Clasificacion artefactos (afecta todos)
    └── ADR-047: Relacion gobernanza (afecta todos)

docs/ai/arquitectura/             # Decisiones arquitectonicas nivel AI
    ├── ADR-AI-001: LLM selection (solo AI)
    ├── ADR-AI-002: Agent pattern (solo AI)
    └── Referencia a ADR-010, ADR-046 (hereda transversales)

docs/backend/arquitectura/        # Decisiones arquitectonicas nivel Backend
    ├── ADR-BE-001: Django REST (solo backend)
    └── Referencia a ADR-010 (hereda transversales)
```

### Principio 3: Mapeo de Contenido

| Tipo Artefacto    | Criterio                      | Ubicacion                         | Ejemplo                         |
| ----------------- | ----------------------------- | --------------------------------- | ------------------------------- |
| **ADR**           | Afecta 2+ dominios            | `docs/gobernanza/adr/`            | ADR-010 (estructura proyecto)   |
| **ADR**           | Solo 1 dominio                | `docs/{dominio}/arquitectura/`    | ADR-AI-001 (LLM selection)      |
| **Plantilla**     | Generica (template_requisito) | `docs/gobernanza/plantillas/`     | template_requisito_funcional.md |
| **Plantilla**     | Especifica (Django model)     | `docs/backend/plantillas/`        | template_django_model.py        |
| **Procedimiento** | Cruza dominios (deploy)       | `docs/gobernanza/procedimientos/` | PROC-001-deploy-produccion.md   |
| **Procedimiento** | Interno dominio (test)        | `docs/{dominio}/procedimientos/`  | PROC-BE-001-test-api.md         |
| **Guia**          | Estilo proyecto               | `docs/gobernanza/guias/`          | GUIA_ESTILO.md                  |
| **Guia**          | Tecnica dominio               | `docs/{dominio}/guias/`           | GUIA_DJANGO_VIEWS.md            |

### Principio 4: Ownership en CODEOWNERS

```bash
# .github/CODEOWNERS

# Gobernanza (transversal) - Equipo multidisciplinario
docs/gobernanza/adr/              @equipo-arquitectura @arquitecto-senior
docs/gobernanza/plantillas/       @equipo-ba @tech-lead
docs/gobernanza/procedimientos/   @tech-lead @scrum-master
docs/gobernanza/guias/            @tech-lead
docs/gobernanza/constitution.md   @arquitecto-senior

# Dominios especificos - Equipos especializados
docs/ai/arquitectura/             @arquitecto-ai @tech-lead
docs/ai/requisitos/               @equipo-ba @arquitecto-ai
docs/ai/procedimientos/           @arquitecto-ai

docs/backend/arquitectura/        @equipo-backend @arquitecto-senior
docs/backend/requisitos/          @equipo-ba @equipo-backend
docs/backend/procedimientos/      @equipo-backend

docs/frontend/arquitectura/       @equipo-frontend @arquitecto-frontend
docs/infraestructura/arquitectura/ @equipo-devops @arquitecto-senior
```

### Principio 5: Estructura de 12 Subdirectorios

Cada dominio tiene estructura completa (ADR-010), pero **hereda** de gobernanza:

```
docs/ai/                          # Dominio AI
├── arquitectura/                 # ADRs especificos AI
│   ├── ADR-AI-001-llm-selection.md
│   └── README.md (referencia a docs/gobernanza/adr/)
│
├── guias/                        # Guias especificas AI
│   ├── GUIA_AGENT_PATTERN.md
│   └── README.md (referencia a docs/gobernanza/guias/)
│
├── procedimientos/               # Procedimientos AI
│   ├── PROC-AI-001-test-agents.md
│   └── README.md (referencia a docs/gobernanza/procedimientos/)
│
└── requisitos/                   # Requisitos AI
    ├── necesidades/
    ├── reglas_negocio/
    └── funcionales/

# Herencia explicita via README:
docs/ai/arquitectura/README.md:
  "Ver tambien: docs/gobernanza/adr/ para decisiones transversales"
```

## Consequences

### Positive

1. **Clara separacion**: Desarrolladores saben donde buscar contenido
2. **Sin duplicacion**: Plantillas genericas en UN solo lugar
3. **Ownership claro**: CODEOWNERS mapea responsabilidades
4. **Extensibilidad**: Dominios pueden extender sin duplicar
5. **Trazabilidad**: ADRs especificos referencian transversales

### Negative

1. **Dos niveles de busqueda**: Desarrollador debe revisar gobernanza/ + dominio/
   - Mitigacion: READMEs en dominios referencian gobernanza

2. **Criterio de transversalidad subjetivo**: "¿Esto afecta 2+ dominios?"
   - Mitigacion: Regla clara en ADR-047 (este documento)

## Implementation

### Decision Tree: ¿Donde va este artefacto?

```python
def determinar_ubicacion(tipo: str, contenido: str) -> str:
    # 1. Analizar dominios mencionados
    dominios = detectar_dominios_en_contenido(contenido)

    # 2. Decision basada en cantidad de dominios
    if len(dominios) >= 2:
        # Transversal: afecta multiples dominios
        return f"docs/gobernanza/{tipo}/"

    elif len(dominios) == 1:
        # Especifico: solo un dominio
        dominio = dominios[0]
        return f"docs/{dominio}/{tipo}/"

    else:
        # Sin mencion explicita, usar tipo
        if tipo in ["adr", "plantilla", "guia_estilo"]:
            # Tipos naturalmente transversales
            return f"docs/gobernanza/{tipo}/"
        else:
            # Requiere clarificacion
            return "REQUIERE_CLARIFICACION"
```

### Migration Guide

Para artefactos existentes mal ubicados:

```bash
# ADR especifico de AI en gobernanza → mover a ai/arquitectura/
git mv docs/gobernanza/adr/ADR-AI-specific.md docs/ai/arquitectura/

# Plantilla generica en dominio → mover a gobernanza
git mv docs/backend/plantillas/template_generic.md docs/gobernanza/plantillas/

# Procedimiento que cruza dominios → mover a gobernanza
git mv docs/backend/procedimientos/PROC-deploy-all.md docs/gobernanza/procedimientos/
```

### Validation

```python
# Validar coherencia
def validar_coherencia():
    # 1. ADRs en gobernanza deben mencionar 2+ dominios
    for adr in glob("docs/gobernanza/adr/*.md"):
        dominios = detectar_dominios_en_contenido(read(adr))
        assert len(dominios) >= 2, f"{adr} solo afecta {dominios}"

    # 2. ADRs en dominio deben mencionar solo ese dominio
    for adr in glob("docs/ai/arquitectura/*.md"):
        dominios = detectar_dominios_en_contenido(read(adr))
        assert dominios == ["ai"], f"{adr} es transversal, mover a gobernanza"
```

## Examples

### Example 1: ADR Transversal

**ADR-046: Clasificacion Automatica de Artefactos**

- Afecta: Todos los agentes SDLC (backend, frontend, ai, infraestructura)
- Ubicacion: `docs/gobernanza/adr/ADR-046-clasificacion-automatica-artefactos.md`
- Owner: `@equipo-arquitectura @arquitecto-senior`

### Example 2: ADR Especifico de Dominio

**ADR-AI-001: LLM Selection for Agents**

- Afecta: Solo dominio AI
- Ubicacion: `docs/ai/arquitectura/ADR-AI-001-llm-selection.md`
- Owner: `@arquitecto-ai @tech-lead`
- Referencia: ADR-046 (hereda decision de clasificacion)

### Example 3: Plantilla Generica

**template_requisito_funcional.md**

- Usada por: Todos los dominios
- Ubicacion: `docs/gobernanza/plantillas/template_requisito_funcional.md`
- Owner: `@equipo-ba @tech-lead`

### Example 4: Plantilla Especifica

**template_agent.py**

- Usada por: Solo dominio AI
- Ubicacion: `docs/ai/plantillas/template_agent.py`
- Owner: `@arquitecto-ai`

### Example 5: Procedimiento Transversal

**PROC-001: Deploy a Produccion**

- Involucra: Backend (API), Frontend (UI), Infraestructura (servers)
- Ubicacion: `docs/gobernanza/procedimientos/PROC-001-deploy-produccion.md`
- Owner: `@tech-lead @scrum-master`

### Example 6: Procedimiento Especifico

**PROC-AI-001: Testing Agents**

- Involucra: Solo agentes AI
- Ubicacion: `docs/ai/procedimientos/PROC-AI-001-test-agents.md`
- Owner: `@arquitecto-ai`

## Related Decisions

- **ADR-010**: Define estructura por dominios (base)
- **ADR-046**: Usa este ADR para determinar ownership automaticamente
- **.github/CODEOWNERS**: Implementa ownership definido aqui

## Validation Criteria

- ✓ Cada ADR en gobernanza/ menciona 2+ dominios
- ✓ Cada ADR en dominio/ menciona solo ese dominio
- ✓ Plantillas genericas en gobernanza/, especificas en dominios
- ✓ CODEOWNERS refleja ownership segun transversalidad
- ✓ READMEs en dominios referencian gobernanza/

## References

- ADR-010: Organizacion proyecto por dominio
- `.github/CODEOWNERS`: Ownership mapping
- Clean Code: Principio de Single Responsibility (aplicado a ubicacion)
