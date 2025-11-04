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
# Para usar Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# O para usar OpenAI
export OPENAI_API_KEY="sk-..."
```

### Archivo de Configuración

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

## Uso

### Modo Básico

```bash
cd scripts/ai
python test_generation_orchestrator.py --project-path ../../api/callcentersite
```

### Dry Run (sin crear PR)

```bash
python test_generation_orchestrator.py \
  --project-path ../../api/callcentersite \
  --dry-run
```

### Con Configuración Custom

```bash
python test_generation_orchestrator.py \
  --project-path ../../api/callcentersite \
  --config my_config.json
```

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

## Troubleshooting

### Error: "ANTHROPIC_API_KEY no encontrada"
```bash
export ANTHROPIC_API_KEY="tu-api-key"
```

### Error: "gh not found"
Instalar GitHub CLI: https://cli.github.com/

### Tests generados no pasan
El agente LLM puede generar tests incorrectos. Revisar logs en `output/test_generation/`

### Cobertura no aumenta
- Verificar que los archivos target sean relevantes
- Ajustar `threshold_low` en configuración
- Revisar `max_tests_per_run`

## Mejoras Futuras

- [ ] Soporte para más LLMs (Gemini, Llama)
- [ ] Generación incremental (reintentos)
- [ ] Cache de resultados LLM
- [ ] Integración con GitHub Actions
- [ ] Métricas de calidad de tests generados
- [ ] Auto-review con LLM
