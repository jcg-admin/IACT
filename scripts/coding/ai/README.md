---
id: DOC-AI-AGENTS
tipo: documentacion
categoria: desarrollo
version: 1.0.0
fecha_creacion: 2025-11-04
---

# Agentes Especializados para Generación de Tests

Sistema de 7 agentes especializados que generan tests automáticamente usando LLM.

## Descripción

Pipeline automatizado que:
1. Analiza gaps de cobertura
2. Planifica tests necesarios
3. Genera código con LLM
4. Valida sintaxis y estilo
5. Ejecuta tests
6. Verifica incremento de cobertura
7. Crea Pull Request

## Arquitectura

```
CoverageAnalyzer → TestPlanner → LLMGenerator → SyntaxValidator
                                                       ↓
PRCreator ← CoverageVerifier ← TestRunner ←──────────┘
```

Cada agente tiene una única responsabilidad (SRP).

## Instalación

```bash
# Dependencias Python
pip install anthropic openai pytest pytest-cov ruff black isort mypy

# GitHub CLI (para crear PRs)
# Ver: https://cli.github.com/
```

## Configuración

### Variables de Entorno

```bash
# Para usar Anthropic Claude (Recomendado)
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# O para usar OpenAI (próximamente)
export OPENAI_API_KEY="sk-..."
```

### Configuraciones Predefinidas

El sistema incluye 4 configuraciones listas para usar:

1. **test_generation.json** - Por defecto (85% cobertura, 5 tests)
2. **test_generation_aggressive.json** - Agresiva (90% cobertura, 10 tests)
3. **test_generation_conservative.json** - Conservadora (80% cobertura, 3 tests)
4. **test_generation_dry_run.json** - Simulación (sin modificar código)

### Personalizar Configuración

Editar `scripts/ai/config/test_generation.json`:

```json
{
  "agents": {
    "coverage_analyzer": {
      "min_coverage": 85,
      "threshold_low": 70
    },
    "test_planner": {
      "max_tests_per_run": 5
    },
    "llm_generator": {
      "llm_provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    },
    "coverage_verifier": {
      "min_coverage_increase": 5.0
    }
  }
}
```

## Inicio Rápido

### La Forma Más Fácil (Recomendado)

```bash
cd scripts/ai/examples

# Validar entorno
./quickstart.sh check

# Ejecutar demo (sin modificar código)
./quickstart.sh demo

# Ejecución real
./quickstart.sh basic
```

### Modo Avanzado

#### Ejecución Directa

```bash
cd scripts/ai
python test_generation_orchestrator.py --project-path ../../api/callcentersite
```

#### Dry Run (sin crear PR)

```bash
python test_generation_orchestrator.py \
  --project-path ../../api/callcentersite \
  --dry-run
```

#### Con Configuración Custom

```bash
python test_generation_orchestrator.py \
  --project-path ../../api/callcentersite \
  --config config/my_custom_config.json
```

Ver más ejemplos en: [`examples/`](./examples/README.md)

## Salida

El pipeline genera:

- `output/test_generation/01_CoverageAnalyzer.json` - Análisis de gaps
- `output/test_generation/02_TestPlanner.json` - Plan de tests
- `output/test_generation/03_LLMGenerator.json` - Tests generados
- `output/test_generation/04_SyntaxValidator.json` - Validación
- `output/test_generation/05_TestRunner.json` - Resultados ejecución
- `output/test_generation/06_CoverageVerifier.json` - Verificación cobertura
- `output/test_generation/07_PRCreator.json` - Info del PR

## Guardrails

Cada agente implementa guardrails:

### LLMGenerator
- NO permite eval(), exec(), compile()
- NO permite open() directo
- Valida estructura pytest
- Máximo 500 líneas por archivo

### SyntaxValidator
- AST parsing (sintaxis)
- ruff (lint)
- black (formato)
- mypy (tipos - opcional)

### TestRunner
- Timeout 2 minutos por archivo
- Tests deben pasar

### CoverageVerifier
- Incremento mínimo 5%
- No permite regresión
- Al menos 1 archivo mejorado

## Los 7 Agentes

### 1. CoverageAnalyzer
**Responsabilidad**: Analizar cobertura e identificar gaps

**Input**: project_path
**Output**: prioritized_targets (archivos con baja cobertura)

### 2. TestPlanner
**Responsabilidad**: Planificar tests a generar

**Input**: prioritized_targets
**Output**: test_plans (funciones, casos edge, casos error)

### 3. LLMGenerator
**Responsabilidad**: Generar código de tests con LLM

**Input**: test_plans
**Output**: generated_tests (código Python)

### 4. SyntaxValidator
**Responsabilidad**: Validar sintaxis y estilo

**Input**: generated_tests
**Output**: validated_tests (código validado y formateado)

### 5. TestRunner
**Responsabilidad**: Ejecutar tests

**Input**: validated_tests
**Output**: test_results (tests que pasaron)

### 6. CoverageVerifier
**Responsabilidad**: Verificar incremento de cobertura

**Input**: test_results + current_coverage
**Output**: new_coverage + coverage_increase

### 7. PRCreator
**Responsabilidad**: Crear Pull Request

**Input**: test_results + coverage metrics
**Output**: pr_url

## Ejemplo de Ejecución

```
[2025-11-04 10:00:00] CoverageAnalyzer - INFO - Analizando cobertura en /proyecto
[2025-11-04 10:00:05] CoverageAnalyzer - INFO - Encontrados 12 archivos con <70% cobertura
[2025-11-04 10:00:05] TestPlanner - INFO - Planificando tests para 5 archivos
[2025-11-04 10:00:06] TestPlanner - INFO - Generados 15 casos de prueba
[2025-11-04 10:00:06] LLMGenerator - INFO - Generando tests con Anthropic Claude
[2025-11-04 10:00:45] LLMGenerator - INFO - 5 archivos generados
[2025-11-04 10:00:45] SyntaxValidator - INFO - Validando sintaxis y estilo
[2025-11-04 10:00:48] SyntaxValidator - INFO - 5/5 archivos validados (100%)
[2025-11-04 10:00:48] TestRunner - INFO - Ejecutando tests
[2025-11-04 10:01:20] TestRunner - INFO - 5/5 archivos pasaron (100%)
[2025-11-04 10:01:20] CoverageVerifier - INFO - Verificando cobertura
[2025-11-04 10:01:35] CoverageVerifier - INFO - 72.3% → 78.5% (+6.2%)
[2025-11-04 10:01:35] PRCreator - INFO - Creando Pull Request
[2025-11-04 10:01:42] PRCreator - INFO - PR creado: https://github.com/...

RESULTADO: EXITOSO

COBERTURA:
  Anterior: 72.30%
  Nueva:    78.50%
  Incremento: +6.20%

TESTS:
  Generados: 5
  Validados: 5
  Pasaron:   5

PULL REQUEST:
  URL: https://github.com/org/repo/pull/123
  Branch: bot/generated-tests-1730725302
  Archivos: 5
```

## Documentación Completa

Ver: `docs/desarrollo/arquitectura_agentes_especializados.md`

## Ejemplos y Guías

Este directorio incluye ejemplos completos de uso:

- **[GUIA_INICIO_RAPIDO.md](./examples/GUIA_INICIO_RAPIDO.md)** - Guía paso a paso para principiantes
- **[examples/README.md](./examples/README.md)** - Catálogo completo de ejemplos
- **quickstart.sh** - Script interactivo de inicio rápido
- **validate_environment.sh** - Validación exhaustiva del entorno
- **example_single_file.sh** - Tests para un archivo específico
- **example_specific_module.py** - Uso programático avanzado
- **example_ci_integration.sh** - Integración con CI/CD

### Casos de Uso Comunes

```bash
# Primera vez usando el sistema
cd examples && ./quickstart.sh demo

# Generar tests para todo el proyecto
cd examples && ./quickstart.sh basic

# Tests para un archivo específico
cd examples && ./example_single_file.sh ../../api/app/models.py

# Integrar en CI/CD
cd examples && ./example_ci_integration.sh

# Validación completa del entorno
cd examples && ./validate_environment.sh
```

## Troubleshooting

### Error: "ANTHROPIC_API_KEY no encontrada"
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Validar
cd examples && ./quickstart.sh check
```

### Error: Dependencias Faltantes
```bash
pip install pytest pytest-cov anthropic ruff black isort mypy
```

### Error: "gh not found"
**Opción 1**: Instalar GitHub CLI: https://cli.github.com/

**Opción 2**: Deshabilitar PR creation en configuración:
```json
{
  "agents": {
    "pr_creator": { "enabled": false }
  }
}
```

### Tests generados no pasan
El agente LLM puede generar tests incorrectos ocasionalmente.

**Solución**:
1. Revisar logs: `output/test_generation/03_LLMGenerator.json`
2. Bajar temperature: `"temperature": 0.2` en configuración
3. Agregar few-shot examples
4. Usar configuración conservadora

### Cobertura no aumenta
**Causas comunes**:
- Los archivos priorizados ya tienen buena cobertura
- Tests generados no cubren las líneas correctas

**Solución**:
1. Revisar: `output/test_generation/01_CoverageAnalyzer.json`
2. Bajar `threshold_low` para incluir más archivos
3. Aumentar `max_tests_per_run`
4. Usar filtros `include_patterns`, `exclude_patterns`

### Más Ayuda

- Ver [Guía de Inicio Rápido](./examples/GUIA_INICIO_RAPIDO.md) completa
- Ejecutar validación: `./examples/validate_environment.sh`
- Revisar [ejemplos](./examples/README.md)

## Mejoras Futuras

- [ ] Soporte para más LLMs (Gemini, Llama)
- [ ] Generación incremental (reintentos)
- [ ] Cache de resultados LLM
- [ ] Integración con GitHub Actions
- [ ] Métricas de calidad de tests generados
- [ ] Auto-review con LLM
