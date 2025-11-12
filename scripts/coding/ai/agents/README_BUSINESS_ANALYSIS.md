# Agentes de Análisis de Negocio

Sistema completo de agentes especializados para generación automática de documentación de análisis de negocio siguiendo estándares internacionales.

## Índice

1. [Visión General](#visión-general)
2. [Agentes Disponibles](#agentes-disponibles)
3. [Instalación y Uso](#instalación-y-uso)
4. [Pipeline Completo](#pipeline-completo)
5. [Ejemplos](#ejemplos)
6. [Estándares Aplicados](#estándares-aplicados)
7. [API Reference](#api-reference)

---

## Visión General

Este sistema de agentes automatiza la generación de documentación de análisis de negocio, transformando especificaciones de alto nivel en documentación completa y trazable.

### Características Principales

- Generación automática de análisis completo (Procesos → UC → Requisitos)
- Matrices de trazabilidad conformes a ISO 29148:2018
- Validación de completitud con checklists estructurados
- División inteligente de documentos grandes
- Generación de plantillas personalizables
- Sin emojis (estándar IACT)
- Guardrails para garantizar calidad

### Flujo de Trabajo

```
Especificación → BusinessAnalysisGenerator → Documento de Análisis
                 ↓
              TraceabilityMatrixGenerator → Matrices RTM + Gaps
                 ↓
              CompletenessValidator → Checklist + % Completitud
                 ↓
              DocumentSplitter (opcional) → Módulos Navegables
                 ↓
              TemplateGenerator (opcional) → Plantillas
```

---

## Agentes Disponibles

### 1. BusinessAnalysisGenerator

**Responsabilidad:** Genera documentación completa de análisis de negocio.

**Input:**
```python
{
    "component_name": "Sistema de Recuperación de Contraseña",
    "domain": "Seguridad",
    "business_objective": "Permitir recuperación segura...",
    "stakeholders": [
        {"rol": "Usuario", "interes": "Proceso simple"}
    ]
}
```

**Output:**
- Documento maestro en Markdown
- Procesos de negocio (PROC-XXX)
- Reglas de negocio (RN-XXX)
- Casos de uso (UC-XXX)
- Requisitos funcionales (RF-XXX)
- Requisitos no funcionales (RNF-XXX)
- Procedimientos operacionales

**Líneas de código:** 817
**Ubicación:** `scripts/ai/agents/business_analysis_generator.py`

### 2. TraceabilityMatrixGenerator

**Responsabilidad:** Genera matrices de trazabilidad (RTM) y análisis de gaps.

**Input:**
```python
{
    "use_cases": [...],
    "requirements_functional": [...],
    "processes": [...],
    "business_rules": [...]
}
```

**Output:**
- Matriz Principal (Proceso → UC → Req → Prueba → Impl)
- Matriz Proceso-UC-Requisito
- Matriz UC-Requisito-Prueba
- Matriz Reglas-Impacto
- Análisis de gaps (huérfanos, sin cobertura)
- Métricas (índices de trazabilidad, cobertura, implementación)

**Líneas de código:** 758
**Ubicación:** `scripts/ai/agents/traceability_matrix_generator.py`

### 3. CompletenessValidator

**Responsabilidad:** Valida completitud de análisis con checklist estructurado.

**Input:**
```python
{
    "document": "...",  # O artefactos estructurados
    "use_cases": [...],
    "requirements_functional": [...]
}
```

**Output:**
- Checklist por categorías (Secciones, Trazabilidad, Estándares, Nomenclatura, Calidad)
- Porcentaje de completitud
- Lista de items faltantes
- Recomendaciones de mejora

**Líneas de código:** 708
**Ubicación:** `scripts/ai/agents/completeness_validator.py`

### 4. TemplateGenerator

**Responsabilidad:** Genera plantillas reutilizables personalizadas.

**Input:**
```python
{
    "template_type": "master_document",  # O rtm_matrix, use_case, etc.
    "parameters": {"component_name": "Mi Componente"}
}
```

**Output:**
- Plantilla en Markdown con placeholders [COMPLETAR]
- 6 tipos disponibles:
  1. `master_document` - Documento Maestro
  2. `rtm_matrix` - Matriz RTM
  3. `completeness_checklist` - Checklist
  4. `business_rule` - Regla de Negocio
  5. `use_case` - Caso de Uso (UML 2.5)
  6. `requirement_spec` - Especificación de Requisito

**Líneas de código:** 716
**Ubicación:** `scripts/ai/agents/template_generator.py`

### 5. DocumentSplitter

**Responsabilidad:** Divide documentos grandes en módulos manejables.

**Input:**
```python
{
    "document": "...",  # Documento Markdown
    "component_name": "Sistema X"
}
```

**Output:**
- Múltiples módulos (00_modulo.md, 01_modulo.md, ...)
- Índice maestro navegable
- Cross-references automáticos (anterior/siguiente/índice)
- Balance de tamaño entre módulos

**Líneas de código:** 496
**Ubicación:** `scripts/ai/agents/document_splitter.py`

---

## Instalación y Uso

### Requisitos

```bash
Python >= 3.8
```

### Instalación

Los agentes están integrados en el proyecto IACT. No requieren instalación adicional.

### Uso Básico

#### Opción 1: Usar Pipeline Completo (Recomendado)

```python
from pathlib import Path
from scripts.ai.agents.business_analysis_pipeline import create_business_analysis_pipeline

# Configuración
config = {
    "generator": {"domain": "Seguridad"},
    "traceability": {"min_traceability_index": 0.95},
    "validator": {"min_completeness": 0.95},
    "split_large_docs": True
}

# Crear pipeline
pipeline = create_business_analysis_pipeline(
    output_dir=Path("output/analisis"),
    config=config
)

# Datos de entrada
input_data = {
    "component_name": "Sistema de Autenticación",
    "domain": "Seguridad",
    "business_objective": "Garantizar autenticación segura",
    "stakeholders": [
        {"rol": "Usuario", "interes": "Acceso rápido"},
        {"rol": "Admin", "interes": "Trazabilidad"}
    ]
}

# Ejecutar
result = pipeline.execute(input_data)
```

#### Opción 2: Usar Agentes Individualmente

```python
from scripts.ai.agents.business_analysis_generator import BusinessAnalysisGenerator

# Crear agente
generator = BusinessAnalysisGenerator(config={"domain": "Seguridad"})

# Ejecutar
result = generator.execute(input_data)

if result.is_success():
    print(result.data["document"])
else:
    print(f"Errores: {result.errors}")
```

### Uso desde Línea de Comando

```bash
# Ejecutar ejemplos interactivos
python scripts/generate_business_analysis.py

# Opciones:
#   1. Sistema de Recuperación de Contraseña
#   2. Sistema de Gestión de Usuarios
#   3. Generación de Plantillas
#   4. Ejecutar todos los ejemplos
```

---

## Pipeline Completo

### Configuración Detallada

```python
config = {
    # BusinessAnalysisGenerator
    "generator": {
        "domain": "Seguridad",           # Dominio del sistema
        "include_procedures": True,       # Generar procedimientos operacionales
        "include_nfr": True,              # Generar requisitos no funcionales
        "iso_29148": True,                # Conformidad ISO 29148
        "babok_v3": True,                 # Conformidad BABOK v3
        "uml_2_5": True                   # Conformidad UML 2.5
    },

    # TraceabilityMatrixGenerator
    "traceability": {
        "min_traceability_index": 0.95,  # Índice mínimo 95%
        "min_coverage_index": 0.90,      # Cobertura mínima 90%
        "include_implementation_status": True
    },

    # CompletenessValidator
    "validator": {
        "min_completeness": 0.95,        # Completitud mínima 95%
        "strict_mode": False,             # Modo estricto (100%)
        "validate_iso_29148": True,
        "validate_babok_v3": True,
        "validate_uml_2_5": True,
        "validate_iact_standards": True   # Sin emojis, nomenclatura
    },

    # DocumentSplitter (opcional)
    "split_large_docs": True,
    "splitter": {
        "max_lines": 1000,                # Máx líneas por módulo
        "min_lines": 200,                 # Mín líneas por módulo
        "preserve_metadata": True
    },

    # TemplateGenerator (opcional)
    "generate_templates": False,
    "templates": {
        "include_examples": True,
        "include_instructions": True
    }
}
```

### Flujo de Ejecución

1. **BusinessAnalysisGenerator**
   - Analiza especificación de entrada
   - Identifica procesos de negocio
   - Deriva reglas de negocio clasificadas
   - Genera casos de uso (UML 2.5)
   - Deriva requisitos funcionales y no funcionales
   - Crea procedimientos operacionales
   - Genera documento maestro

2. **TraceabilityMatrixGenerator**
   - Recibe artefactos del paso 1
   - Crea matriz principal de trazabilidad
   - Genera matrices especializadas
   - Analiza gaps (huérfanos, sin cobertura)
   - Calcula métricas de calidad

3. **CompletenessValidator**
   - Valida artefactos generados
   - Verifica secciones obligatorias
   - Valida trazabilidad bidireccional
   - Verifica conformidad con estándares
   - Valida nomenclatura y calidad
   - Genera checklist con % completitud

4. **DocumentSplitter** (opcional)
   - Analiza estructura del documento
   - Divide en módulos lógicos
   - Genera cross-references
   - Crea índice maestro

5. **TemplateGenerator** (opcional)
   - Genera plantillas personalizadas
   - Incluye instrucciones inline
   - Placeholders para completar

---

## Ejemplos

### Ejemplo 1: Análisis Completo de Sistema de Seguridad

```python
input_data = {
    "component_name": "Sistema de Recuperación de Contraseña",
    "domain": "Seguridad",
    "business_objective": "Permitir recuperación segura de acceso",
    "stakeholders": [
        {"rol": "Usuario", "interes": "Recuperar acceso rápido"},
        {"rol": "Admin Seguridad", "interes": "Trazabilidad"}
    ],
    "scope": {
        "includes": [
            "Solicitud vía email",
            "Token temporal",
            "Nueva contraseña"
        ],
        "excludes": ["SMS", "Preguntas de seguridad"]
    },
    "critical": True  # Genera RNF de disponibilidad
}

pipeline = create_business_analysis_pipeline(
    output_dir=Path("output/password_recovery"),
    config=config
)

result = pipeline.execute(input_data)
# Output:
#   - analisis_completo_20250106_143022.md
#   - matriz_trazabilidad_20250106_143022.md
#   - checklist_completitud_20250106_143022.md
#   - modulos_20250106_143022/ (si split_large_docs=True)
```

### Ejemplo 2: Generar Solo Plantillas

```python
from scripts.ai.agents.template_generator import TemplateGenerator

generator = TemplateGenerator()

# Plantilla de documento maestro
result = generator.execute({
    "template_type": "master_document",
    "parameters": {"component_name": "Mi Sistema", "domain": "Mi Dominio"}
})

with open("plantilla.md", "w") as f:
    f.write(result.data["template_content"])
```

### Ejemplo 3: Validar Análisis Existente

```python
from scripts.ai.agents.completeness_validator import CompletenessValidator

validator = CompletenessValidator(config={"min_completeness": 0.95})

with open("mi_analisis.md", "r") as f:
    document = f.read()

result = validator.execute({"document": document})

print(f"Completitud: {result.data['completeness_percentage']:.1%}")
print(f"Estado: {'COMPLETO' if result.data['is_complete'] else 'INCOMPLETO'}")
print(f"\nItems faltantes:")
for item in result.data['missing_items']:
    print(f"  - {item}")
```

---

## Estándares Aplicados

### ISO/IEC/IEEE 29148:2018

**Requirements Engineering Process**

- Trazabilidad bidireccional completa
- Upward: Requisito → UC → Proceso → Necesidad
- Downward: Requisito → Prueba → Implementación
- Matriz RTM conforme
- Análisis de gaps

### BABOK v3

**Business Analysis Body of Knowledge**

- Jerarquía de artefactos:
  * Necesidad de Negocio
  * Proceso de Negocio
  * Reglas de Negocio
  * Casos de Uso
  * Requisitos (Funcionales y No Funcionales)
- Clasificación de reglas: Hecho, Restricción, Desencadenador, Inferencia, Cálculo

### UML 2.5

**Use Case Modeling**

- Formato estándar de casos de uso
- Nombre: VERBO + OBJETO
- Estructura: Actor, Precondiciones, Postcondiciones, Flujos
- Tabla de dos columnas (Actor / Sistema)
- Flujos alternativos y de excepción

### Estándares IACT

**Proyecto Específico**

- Sin emojis en documentación
- Nomenclatura consistente:
  * PROC-[ÁREA]-[NNN]
  * RN-[ÁREA]-[NN]
  * UC-[NNN]
  * RF-[NNN]
  * RNF-[NNN]
- Formato Markdown
- Referencias cruzadas entre documentos

---

## API Reference

### BusinessAnalysisGenerator

```python
class BusinessAnalysisGenerator(Agent):
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    def execute(self, input_data: Dict[str, Any]) -> AgentResult
```

**Config:**
- `domain`: Dominio del sistema (default: "general")
- `include_procedures`: Generar procedimientos (default: True)
- `include_nfr`: Generar RNF (default: True)
- `iso_29148`, `babok_v3`, `uml_2_5`: Estándares (default: True)

**Input Data:**
- `component_name` (required): Nombre del componente
- `domain` (required): Dominio
- `business_objective` (required): Objetivo de negocio
- `stakeholders` (required): Lista de stakeholders
- `scope` (optional): Alcance (includes/excludes)
- `critical` (optional): Si es sistema crítico

**Output:**
- `document`: Documento Markdown
- `processes`: Lista de procesos
- `business_rules`: Lista de reglas
- `use_cases`: Lista de casos de uso
- `requirements_functional`: Lista de RF
- `requirements_nonfunctional`: Lista de RNF
- `procedures`: Lista de procedimientos
- `metrics`: Métricas de generación

### TraceabilityMatrixGenerator

```python
class TraceabilityMatrixGenerator(Agent):
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    def execute(self, input_data: Dict[str, Any]) -> AgentResult
```

**Config:**
- `min_traceability_index`: Índice mínimo (default: 0.95)
- `min_coverage_index`: Cobertura mínima (default: 0.90)
- `include_implementation_status`: Incluir estado impl (default: True)

**Input Data:**
- `use_cases` (required): Lista de UC
- `requirements_functional` (required): Lista de RF
- `processes` (optional): Lista de procesos
- `business_rules` (optional): Lista de reglas
- `test_cases` (optional): Lista de pruebas
- `implementations` (optional): Lista de implementaciones

**Output:**
- `rtm_document`: Documento RTM Markdown
- `main_matrix`: Matriz principal
- `process_uc_req_matrix`: Matriz Proceso-UC-Req
- `uc_req_test_matrix`: Matriz UC-Req-Test
- `rules_impact_matrix`: Matriz Reglas-Impacto
- `gaps`: Análisis de gaps
- `metrics`: Métricas (traceability_index, coverage_index, implementation_index)

### CompletenessValidator

```python
class CompletenessValidator(Agent):
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    def execute(self, input_data: Dict[str, Any]) -> AgentResult
```

**Config:**
- `min_completeness`: Completitud mínima (default: 0.95)
- `strict_mode`: Modo estricto 100% (default: False)
- `validate_iso_29148`, `validate_babok_v3`, `validate_uml_2_5`: Estándares (default: True)
- `validate_iact_standards`: Estándares IACT (default: True)

**Input Data:**
- `document` (optional): Documento Markdown
- `use_cases` (optional): Lista de UC
- `requirements_functional` (optional): Lista de RF
- Otros artefactos estructurados

**Output:**
- `checklist_document`: Checklist Markdown
- `completeness_percentage`: % completitud (0.0-1.0)
- `is_complete`: Boolean
- `checks`: Checks por categoría
- `missing_items`: Lista de items faltantes
- `recommendations`: Recomendaciones

### TemplateGenerator

```python
class TemplateGenerator(Agent):
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    def execute(self, input_data: Dict[str, Any]) -> AgentResult

    TEMPLATE_TYPES = [
        "master_document",
        "rtm_matrix",
        "completeness_checklist",
        "business_rule",
        "use_case",
        "requirement_spec"
    ]
```

**Config:**
- `include_examples`: Incluir ejemplos (default: True)
- `include_instructions`: Incluir instrucciones (default: True)

**Input Data:**
- `template_type` (required): Tipo de plantilla
- `parameters` (optional): Parámetros personalizados

**Output:**
- `template_content`: Plantilla Markdown
- `template_type`: Tipo generado
- `line_count`: Número de líneas
- `placeholder_count`: Cantidad de [COMPLETAR]

### DocumentSplitter

```python
class DocumentSplitter(Agent):
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    def execute(self, input_data: Dict[str, Any]) -> AgentResult
```

**Config:**
- `max_lines`: Máximo líneas por módulo (default: 1000)
- `min_lines`: Mínimo líneas por módulo (default: 200)
- `preserve_metadata`: Preservar metadata (default: True)

**Input Data:**
- `document` (required): Documento Markdown
- `component_name` (optional): Nombre del componente

**Output:**
- `modules`: Lista de módulos
- `module_count`: Cantidad de módulos
- `cross_references`: Referencias cruzadas
- `master_index`: Índice maestro
- `original_size_lines`: Líneas originales
- `average_module_size_lines`: Promedio por módulo

---

## Testing

### Ejecutar Tests

```bash
# Instalar pytest si no está instalado
pip install pytest

# Ejecutar todos los tests
python -m pytest scripts/ai/agents/test_business_analysis_agents.py -v

# Ejecutar tests de un agente específico
python -m pytest scripts/ai/agents/test_business_analysis_agents.py::TestBusinessAnalysisGenerator -v

# Ejecutar con cobertura
pip install pytest-cov
python -m pytest scripts/ai/agents/test_business_analysis_agents.py --cov=scripts.ai.agents --cov-report=html
```

### Tests Disponibles

- `TestBusinessAnalysisGenerator`: 5 tests
- `TestTraceabilityMatrixGenerator`: 4 tests
- `TestCompletenessValidator`: 3 tests
- `TestTemplateGenerator`: 8 tests (incluyendo parametrized)
- `TestDocumentSplitter`: 4 tests
- `TestBusinessAnalysisPipeline`: 2 tests
- `TestIntegration`: 1 test de flujo completo

---

## Casos de Uso Demostrados

### Caso Real 1: Marco Integrado IACT

**Proyecto:** `docs/gobernanza/marco_integrado/`

**Generado manualmente, ahora automatizable:**
- 8 documentos (00-06)
- 7,419 líneas totales
- Conformidad ISO 29148, BABOK v3, UML 2.5
- Sin emojis
- Trazabilidad completa

**Replicable con:**
```python
pipeline = create_business_analysis_pipeline(...)
result = pipeline.execute(input_data)
# Output similar a los 8 documentos manuales
```

### Caso Real 2: Sistema de Autenticación

**Documentado en:** `docs/implementacion/backend/requisitos/negocio/rn_c01_autenticacion_sesiones.md`

- 14 reglas de negocio (RN-C01-01 a RN-C01-14)
- 1,859 líneas
- Casos de uso: UC-001, UC-002
- Requisitos: RF-005, RF-006, RF-010

**Generado automáticamente con BusinessAnalysisGenerator**

---

## Constitution para Agentes AI

Todos los agentes en este sistema cargan y adhieren automáticamente a los principios definidos en la **Constitution** (`docs/gobernanza/agentes/constitution.md`).

### Principios Clave

Los agentes validan su comportamiento contra 12 principios fundamentales:

1. **Calidad sobre Velocidad**: Sin placeholders o código incompleto
2. **Adherencia a Estándares**: Cumplimiento de GUIA_ESTILO.md y estándares del proyecto
3. **Trazabilidad Completa**: Referencias a REQ-*, SPEC-*, ADR-* en todo output
4. **Límites de Autoridad**: Escalación para cambios arquitectónicos o críticos
5. **Documentación Obligatoria**: Docstrings completos con formato Google
6. **Testing y Validación**: Código siempre acompañado de tests

### Integración Automática

Todos los agentes heredan de `Agent` (base.py) que automáticamente:

- **Carga constitution** al inicializar
- **Valida output** contra principios en `apply_guardrails()`
- **Verifica autoridad** con `check_authority()` antes de acciones críticas
- **Bloquea ejecución** si hay violaciones a constitution

### Ejemplo de Uso

```python
from business_analysis_generator import BusinessAnalysisGenerator

# Agente carga constitution automáticamente
agent = BusinessAnalysisGenerator()

# Constitution cargada y disponible
print(f"Principios cargados: {len(agent.constitution.principles)}")

# Validación automática en execute()
result = agent.execute(input_data)

if result.is_blocked():
    # Output violó principios de constitution
    print(f"Bloqueado: {result.errors}")
```

### Validaciones Automáticas

Cuando un agente ejecuta `apply_guardrails()`, se valida:

- **Sin emojis**: Prohibidos por GUIA_ESTILO.md
- **Trazabilidad**: Output contiene referencias a requisitos
- **Calidad**: Sin placeholders (TODO, FIXME, etc.)
- **Testing**: Código incluye tests asociados
- **Documentación**: Docstrings presentes y completos

### Escalación de Autoridad

Acciones que requieren escalación humana:

- Modificar arquitectura del sistema
- Cambiar esquemas de base de datos
- Modificar APIs públicas
- Eliminar código o archivos
- Cambiar configuración de seguridad
- Merge a branches protegidas (main, develop)

```python
# Verificar antes de acción crítica
if not agent.check_authority("modificar_arquitectura"):
    agent.logger.error("ESCALACIÓN REQUERIDA: Cambio arquitectónico")
    return AgentResult(status=AgentStatus.BLOCKED)
```

### Referencias

- **Constitution completa**: `docs/gobernanza/agentes/constitution.md`
- **Constitution loader**: `scripts/ai/agents/constitution_loader.py`
- **Base class**: `scripts/ai/agents/base.py`
- **Tests de integración**: `scripts/ai/agents/test_constitution_integration.py`

---

## Contribuir

Para agregar nuevos agentes o mejorar existentes:

1. Seguir arquitectura base de `scripts/ai/agents/base.py`
2. Implementar métodos abstractos: `run()`, `validate_input()`, `apply_guardrails()`
3. Agregar tests en `test_business_analysis_agents.py`
4. Actualizar este README
5. Seguir estándares IACT (sin emojis, nomenclatura consistente)
6. **NUEVO**: Asegurar adherencia a constitution (cargada automáticamente)

---

## Licencia

Este código es parte del proyecto IACT y sigue la licencia del proyecto principal.

---

## Soporte

Para reportar bugs o solicitar features, crear issue en el repositorio del proyecto IACT.

**Documentación Generada:** 2025-01-06
**Versión:** 1.0
**Autores:** Sistema de Agentes de IA - IACT Project
