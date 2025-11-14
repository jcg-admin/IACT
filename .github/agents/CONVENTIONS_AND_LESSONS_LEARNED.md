# Convenciones y Lecciones Aprendidas - Agentes IACT

Este documento registra convenciones del proyecto y lecciones aprendidas para evitar errores repetidos.

---

## Convenciones de Ubicación de Documentación

### Regla General: Documentación sigue al Código

**Principio**: La ubicación de la documentación debe reflejar el tipo de código que documenta.

### Estructura de Documentación

La documentación sigue un patrón de **Gobernanza Multinivel**:

#### Nivel Padre (Transversal)

Documentación de alto nivel que aplica a todos los dominios:

```
docs/
├── gobernanza/              # Gobernanza padre con matriz de relación a dominios
├── adr/                     # ADRs arquitectónicos de alto nivel
├── analisis/                # Análisis general del proyecto
├── vision_y_alcance/        # Visión y alcance del proyecto
├── planificacion_y_releases/# Planificación general
├── guias/                   # Guías transversales
├── anexos/                  # Material complementario
└── INDEX.md                 # Punto de entrada principal
```

#### Dominios (Autónomos)

Cada dominio tiene su propia estructura completa:

```
docs/
├── ai/                      # Dominio AI/ML
│   ├── gobernanza/         # Gobernanza específica de AI
│   ├── adr/                # ADRs de AI
│   ├── procedimientos/     # Procedimientos de AI
│   ├── testing/            # Tests de AI
│   └── README.md           # Índice del dominio
│
├── backend/                 # Dominio Backend
│   ├── gobernanza/
│   ├── adr/
│   ├── procedimientos/
│   ├── testing/
│   ├── planning/           # SDLC Planning
│   ├── feasibility/        # SDLC Feasibility
│   ├── design/             # SDLC Design
│   ├── deployment/         # SDLC Deployment
│   └── README.md
│
├── frontend/                # Dominio Frontend
│   ├── gobernanza/
│   ├── adr/
│   ├── procedimientos/
│   ├── testing/
│   └── README.md
│
├── infraestructura/         # Dominio Infraestructura
│   ├── gobernanza/
│   ├── adr/
│   ├── procedimientos/
│   └── README.md
│
├── devops/                  # Dominio DevOps
│   ├── gobernanza/
│   ├── adr/
│   ├── procedimientos/
│   └── README.md
│
├── operaciones/             # Dominio Operaciones
│   ├── gobernanza/
│   ├── adr/
│   ├── procedimientos/
│   └── README.md
│
├── dora/                    # Dominio Métricas DORA
│   ├── gobernanza/
│   ├── adr/
│   └── README.md
│
└── qa/                      # Dominio Quality Assurance
    ├── gobernanza/
    ├── adr/
    ├── procedimientos/
    └── README.md
```

#### Definiciones de Agentes

```
.github/agents/              # Definiciones de agentes (fuera de docs/)
├── README.md                # Catálogo de agentes
├── sdlc/
├── automation/
└── CONVENTIONS_AND_LESSONS_LEARNED.md
```

### Casos Específicos

#### Gobernanza de Alto Nivel vs Gobernanza de Dominio
```
CORRECTO (Padre): docs/gobernanza/matriz_relacion_dominios.md
CORRECTO (Dominio): docs/backend/gobernanza/coding_standards.md

Razón: docs/gobernanza/ es nivel padre con matriz de relación.
       Cada dominio tiene su propia gobernanza específica.
```

#### ADRs de Arquitectura vs ADRs de Dominio
```
CORRECTO (Alto nivel): docs/adr/ADR-001-multi-tenant-architecture.md
CORRECTO (Dominio AI): docs/ai/adr/ADR-AI-001-llm-provider-selection.md

Razón: docs/adr/ para decisiones arquitectónicas transversales.
       docs/{dominio}/adr/ para decisiones específicas del dominio.
```

#### Tests de Código Backend
```
CORRECTO: docs/backend/testing/
INCORRECTO: docs/agent/testing/

Razón: Los tests son de código Python backend (técnicas de prompting)
```

#### Tests de Código Frontend
```
CORRECTO: docs/frontend/testing/
INCORRECTO: docs/ui/testing/

Razón: Consistencia con estructura docs/backend/
```

#### Documentación de Agentes (Definiciones)
```
CORRECTO: .github/agents/
INCORRECTO: docs/agents/ o docs/ai/agents/

Razón: Definiciones de agentes van en .github/ para CI/CD integration
       Documentación de uso/arquitectura de agentes va en docs/ai/
```

#### Ejecuciones SDLC de Proyectos Backend
```
CORRECTO: docs/backend/planning/planning_output.md
INCORRECTO: docs/agent/SDLC_*.md

Razón: El SDLC documenta desarrollo de código backend
       Cada fase tiene su carpeta en el dominio
```

#### Procedimientos Operacionales
```
CORRECTO (Dominio): docs/devops/procedimientos/rollback_deployment.md
CORRECTO (Transversal): docs/procedimientos/incident_response.md

Razón: Procedimientos específicos van en el dominio.
       Procedimientos generales pueden estar en docs/procedimientos/
```

---

## Lecciones Aprendidas

### LL-001: Verificar Estructura Antes de Crear Directorios

**Fecha**: 2025-11-14

**Problema**: Documentación SDLC creada en `docs/agent/` cuando debía estar en `docs/backend/`.

**Causa Raíz**: No verificar la estructura existente de `docs/` antes de crear nuevas carpetas.

**Impacto**:
- 8 archivos en ubicación incorrecta
- Referencias incorrectas en documentos
- Tiempo perdido en corrección

**Solución Aplicada**:
1. Mover todos los archivos a `docs/backend/`
2. Actualizar todas las referencias
3. Documentar convención

**Prevención Futura**:

**ANTES** de crear una nueva carpeta en `docs/`:

1. **Verificar estructura existente**:
   ```bash
   ls -la docs/
   ```

2. **Preguntarse**:
   - ¿Qué tipo de código documenta esto?
   - ¿Ya existe una carpeta para ese tipo?
   - ¿Dónde están documentos similares?

3. **Si hay duda, PREGUNTAR al usuario**:
   ```
   "Voy a crear documentación para X.
    ¿Debería ir en docs/backend/, docs/frontend/,
    u otra ubicación?"
   ```

4. **Verificar ejemplos existentes**:
   ```bash
   find docs/ -name "README.md" -o -name "*testing*"
   ```

**Regla**: Si no estás 100% seguro, pregunta antes de crear.

---

### LL-002: Nomenclatura sin Números

**Fecha**: 2025-11-14

**Problema**: Documentos creados con números prefijos (01_, 02_, etc.) cuando el proyecto no usa números.

**Causa Raíz**: Asumir convención de numeración sin verificar el proyecto.

**Solución**:
- Documentos renombrados sin números
- Usar nombres descriptivos: `planning_output.md` no `01_planning_output.md`

**Prevención**:
1. Verificar nomenclatura en carpeta destino primero
2. Usar nombres descriptivos, no secuenciales
3. Preguntar sobre convenciones si hay duda

---

### LL-003: Validación Automática de Documentación en SDLC

**Fecha**: 2025-11-14

**Problema**: Errores en documentación solo se detectan manualmente después de generarla (ubicación incorrecta, emojis, números, etc.).

**Causa Raíz**: No hay validación automática cuando agentes SDLC generan documentación.

**Solución Propuesta**: Integrar DocumentationValidatorAgent en el pipeline SDLC

**Arquitectura del Agente**:

```python
# Patrón: Agente Genérico + Componentes Especializados + Configuración por Dominio

class DocumentationValidatorAgent(Agent):
    """
    Valida documentación generada por agentes SDLC.
    Se ejecuta automáticamente después de cada fase que genere docs.
    """

    def __init__(self, config):
        # Componentes especializados (Strategy Pattern)
        self.validators = [
            LocationValidator(),      # Verifica docs/backend/ vs docs/agent/
            ConventionValidator(),    # Sin emojis, sin números
            StructureValidator(),     # H1 único, jerarquía
            ConstitutionValidator()   # Principios 2, 7, etc.
        ]

    def run(self, input_data):
        domain = self._classify_domain(input_data["doc_path"])
        rules = self._load_domain_rules(domain)

        results = []
        for validator in self.validators:
            result = validator.validate(doc_content, rules)
            results.append(result)

        return self._generate_report(results)
```

**Integración en SDLC**:

```python
# En cada agente SDLC (Planning, Feasibility, Design, Testing, Deployment)

class SDLCPlannerAgent(SDLCAgent):
    def run(self, input_data):
        # 1. Generar documentación
        doc_path = self._generate_planning_doc(input_data)

        # 2. VALIDAR automáticamente
        validator = DocumentationValidatorAgent()
        validation = validator.run({
            "doc_path": doc_path,
            "domain": "backend"  # o detectar automáticamente
        })

        # 3. Si hay errores CRÍTICOS, fallar
        if validation["critical_errors"] > 0:
            raise DocumentationError(validation["errors"])

        return {"status": "success", "doc_path": doc_path}
```

**Configuración por Dominio**:

```yaml
# .github/agents/configs/documentation_rules.yaml
# DOCUMENTO VIVO: Actualizar cuando se agreguen nuevos dominios

backend:
  location: "docs/backend/"
  naming: "snake_case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Planning"
    - "Feasibility"
    - "Design"
    - "Testing"
    - "Deployment"

frontend:
  location: "docs/frontend/"
  naming: "kebab-case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Components"
    - "State Management"
    - "Testing"

infrastructure:
  location: "docs/infraestructura/"
  naming: "kebab-case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Architecture"
    - "Configuration"
    - "Deployment"

devops:
  location: "docs/devops/"
  naming: "snake_case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Pipeline"
    - "Monitoring"
    - "Deployment"

operaciones:
  location: "docs/operaciones/"
  naming: "snake_case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Procedures"
    - "Runbooks"
    - "Incidents"

gobernanza:
  location: "docs/gobernanza/"
  naming: "snake_case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Policies"
    - "Standards"
    - "Compliance"

ai:
  location: "docs/ai/"
  naming: "snake_case"
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Agents"
    - "Prompting"
    - "Models"

agents_definition:
  location: ".github/agents/"
  naming: "SCREAMING_SNAKE_CASE"  # README.md, CONVENTIONS_AND_LESSONS_LEARNED.md
  no_numbers: true
  no_emojis: true
  required_sections:
    - "Description"
    - "Usage"
```

**Cuándo se ejecuta**:

| Fase SDLC | Genera Docs | Valida con |
|-----------|-------------|------------|
| Planning | planning_output.md | DocumentationValidatorAgent |
| Feasibility | feasibility_analysis.md | DocumentationValidatorAgent |
| Design | design_hld_lld.md | DocumentationValidatorAgent |
| Testing | testing_strategy.md | DocumentationValidatorAgent |
| Deployment | deployment_plan.md | DocumentationValidatorAgent |

**Beneficios**:
- Detecta errores inmediatamente (no después)
- Previene ubicaciones incorrectas (docs/agent/ vs docs/backend/)
- Valida convenciones automáticamente
- Falla rápido si hay errores críticos

**Estado**: PROPUESTO (pendiente implementación)

**Issue**: Crear FEATURE-DOC-VALIDATOR-SDLC-001

---

## Checklist Pre-Documentación

Antes de crear documentación nueva, verificar:

- [ ] Revisé `docs/` para ver estructura existente
- [ ] Identifiqué el tipo de código (backend/frontend/infra)
- [ ] Verifiqué nomenclatura en carpeta destino
- [ ] Si hay duda, pregunté al usuario
- [ ] Confirmé que la ubicación es consistente con docs similares

---

## Mapeo Rápido: Código → Documentación

DOCUMENTO VIVO: Actualizar cuando se agreguen nuevos dominios

### Dominios Principales

| Dominio | Código | Documentación | Scripts |
|---------|--------|---------------|---------|
| **AI/ML** | `scripts/coding/ai/agents/` | `docs/ai/` | `scripts/examples/`, `scripts/coding/ai/` |
| **Backend** | `api/`, `scripts/coding/` | `docs/backend/` | `scripts/coding/` |
| **Frontend** | `ui/`, `frontend/` | `docs/frontend/` | N/A |
| **Infraestructura** | `infrastructure/`, `terraform/` | `docs/infraestructura/` | `scripts/infrastructure/` |
| **DevOps** | Pipelines, CI/CD | `docs/devops/` | `scripts/ci/`, `scripts/git-hooks/` |
| **Operaciones** | Runbooks, procedures | `docs/operaciones/` | `scripts/health_check.sh`, `scripts/backup_*` |
| **QA** | Tests | `docs/qa/` | `scripts/validation/`, `scripts/tests/` |
| **DORA** | Métricas | `docs/dora/` | `scripts/dora_metrics.py` |

### Documentación Transversal (Nivel Padre)

| Tipo | Ubicación | Propósito |
|------|-----------|-----------|
| Gobernanza Padre | `docs/gobernanza/` | Matriz de relación con gobernanzas de dominios |
| ADRs Alto Nivel | `docs/adr/` | Decisiones arquitectónicas transversales |
| Análisis General | `docs/analisis/` | Análisis del proyecto |
| Visión | `docs/vision_y_alcance/` | Visión y alcance |
| Planificación | `docs/planificacion_y_releases/` | Planificación general |
| Guías | `docs/guias/` | Guías transversales |
| Anexos | `docs/anexos/` | Material complementario |

### Subcarpetas por Dominio

Cada dominio puede tener:
- `{dominio}/gobernanza/` - Gobernanza específica
- `{dominio}/adr/` - ADRs del dominio
- `{dominio}/procedimientos/` - Procedimientos del dominio
- `{dominio}/testing/` - Tests del dominio
- `{dominio}/README.md` - Índice del dominio

### Casos Especiales

| Tipo | Ubicación | Razón |
|------|-----------|-------|
| Definiciones Agentes | `.github/agents/` | CI/CD integration |
| Tests Backend | `docs/backend/testing/` | Tests son código backend |
| Tests Frontend | `docs/frontend/testing/` | Tests son código frontend |
| SDLC Backend | `docs/backend/{planning,feasibility,design,deployment}/` | SDLC es proceso de desarrollo |

---

## Preguntas Frecuentes

### P: ¿Dónde va documentación de tests TDD para código backend?
**R**: `docs/backend/testing/`

### P: ¿Dónde va documentación de definiciones de agentes?
**R**: `.github/agents/` (para definiciones) o `docs/ai/` (para sistema AI)

### P: ¿Dónde va un SDLC pipeline para desarrollo backend?
**R**: `docs/backend/` con subdirectorios por fase

### P: Si no estoy seguro, ¿qué hago?
**R**: **PREGUNTA** antes de crear. Mejor preguntar que corregir después.

---

## Commits de Referencia

- `162087c`: Move SDLC documentation from docs/agent to docs/backend (esta lección)
- `00a3a70`: Remove numbers from document names

---

## Actualizaciones de Este Documento

**2025-11-14**: Documento inicial
- LL-001: Verificar estructura antes de crear directorios
- LL-002: Nomenclatura sin números
- LL-003: Validación automática de documentación en SDLC (patrón de arquitectura)
- Convenciones de ubicación de documentación
- Estructura multinivel: Gobernanza Padre + Dominios Autónomos
- Mapeo completo de 8 dominios (ai, backend, frontend, infraestructura, devops, operaciones, qa, dora)
- Documentación transversal (gobernanza, adr, analisis, vision, planificacion, guias, anexos)

---

**Nota**: Este documento es VIVO. Actualizar cuando se aprendan nuevas lecciones.

**Propósito**: Evitar errores repetidos y mantener consistencia en el proyecto.
