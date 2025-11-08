# Guía Completa: TDD Feature Agent

Documentación detallada del agente de implementación TDD con garantías de calidad y compliance.

## Tabla de Contenidos

- [Introducción](#introducción)
- [Arquitectura](#arquitectura)
- [Componentes del Sistema](#componentes-del-sistema)
- [Constitution TDD](#constitution-tdd)
- [Uso desde CLI](#uso-desde-cli)
- [Sistema de Scoring](#sistema-de-scoring)
- [Ejemplos de Output](#ejemplos-de-output)
- [Integración con DORA Metrics](#integración-con-dora-metrics)
- [Configuración](#configuración)
- [Troubleshooting](#troubleshooting)
- [Mejores Prácticas](#mejores-prácticas)

## Introducción

El **TDD Feature Agent** es un agente SDLC especializado que implementa features automáticamente siguiendo estrictamente la metodología TDD (Test-Driven Development) con garantías de calidad y compliance.

**Path:** `scripts/ai/agents/tdd_feature_agent.py`

**Propósito:**
- Implementar features siguiendo el ciclo RED-GREEN-REFACTOR
- Garantizar compliance mediante constitution checks
- Validar calidad con herramientas automatizadas (pytest, ruff, mypy, bandit)
- Generar audit trail completo e inmutable
- Producir reportes y dashboards visuales

**Beneficios:**
- 100% compliance con metodología TDD
- Cero vulnerabilidades en código generado
- Cobertura de tests ≥ 90%
- Audit trail inmutable con SHA256 hashes
- Reportes automáticos en JSON y Markdown
- Dashboards visuales con badges

## Arquitectura

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                    TDD Feature Agent                        │
│                                                             │
│  Orquesta ciclo RED-GREEN-REFACTOR                         │
│  Valida constitution compliance                             │
│  Genera reportes y dashboards                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Utiliza
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   TDD Constitution                          │
│                                                             │
│  ✓ RED_BEFORE_GREEN         (CRITICAL)                     │
│  ✓ TESTS_MUST_FAIL_FIRST    (CRITICAL)                     │
│  ✓ ALL_TESTS_MUST_PASS      (CRITICAL)                     │
│  ✓ TESTS_STAY_GREEN         (CRITICAL)                     │
│  ✓ MINIMUM_COVERAGE ≥90%    (HIGH)                         │
│  ✓ NO_SECURITY_ISSUES       (HIGH)                         │
│  ✓ CODE_QUALITY_PASSING     (MEDIUM)                       │
│  ✓ DOCUMENTATION_REQUIRED   (MEDIUM)                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Ejecuta
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Code Quality Validator                         │
│                                                             │
│  • pytest + coverage  → Test execution & coverage           │
│  • ruff              → Code linting                         │
│  • mypy              → Type checking                        │
│  • bandit            → Security scanning                    │
│  • AST parser        → Docstring validation                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Registra en
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              TDD Execution Logger                           │
│                                                             │
│  • Timestamps de cada fase                                  │
│  • SHA256 hashes de artifacts                              │
│  • Resultados de test executions                           │
│  • Métricas de calidad                                     │
│  • Constitution compliance result                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ Genera
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              TDD Metrics Dashboard                          │
│                                                             │
│  • Badges de shields.io                                    │
│  • Tablas de métricas                                      │
│  • Timeline de ejecución                                   │
│  • Resumen de violations                                   │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de Ejecución

```
Issue Data (JSON)
      │
      ▼
┌─────────────────┐
│   RED PHASE     │  ← Generar tests que fallen
│                 │    Log: red_phase
│ • Generate tests│    Test execution: debe fallar
│ • Run tests     │
│ • Must fail     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GREEN PHASE    │  ← Implementar código
│                 │    Log: green_phase
│ • Generate code │    Test execution: debe pasar
│ • Run tests     │    Quality checks: coverage, security
│ • Must pass     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ REFACTOR PHASE  │  ← Optimizar código
│                 │    Log: refactor_phase
│ • Auto-fix lint │    Test execution: sigue pasando
│ • Optimize code │    Quality recheck
│ • Tests pass    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   VALIDATION    │  ← Validar constitution
│                 │
│ • Check rules   │    Compliance score: 0-100
│ • Calculate     │    FAIL if CRITICAL violated
│   score         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   REPORTING     │  ← Generar reportes
│                 │
│ • JSON log      │    • execution_<feature>.json
│ • Markdown      │    • execution_<feature>.md
│ • Dashboard     │    • dashboard_<feature>.md
└─────────────────┘
```

## Componentes del Sistema

### 1. TDD Constitution (`tdd_constitution.py`)

Reglas inmutables de compliance TDD.

**Reglas CRITICAL** (fallo inmediato):
- `RED_BEFORE_GREEN`: Tests escritos antes del código
- `TESTS_MUST_FAIL_FIRST`: Tests fallan en fase RED
- `ALL_TESTS_MUST_PASS`: Tests pasan en fase GREEN
- `TESTS_STAY_GREEN_AFTER_REFACTOR`: Tests pasan después de REFACTOR

**Reglas HIGH** (deben corregirse):
- `MINIMUM_COVERAGE`: Cobertura ≥ 90%
- `NO_SECURITY_ISSUES`: Sin vulnerabilidades

**Reglas MEDIUM** (advertencias):
- `CODE_QUALITY_PASSING`: Linting y type checking
- `DOCUMENTATION_REQUIRED`: Docstrings en funciones públicas

**API:**
```python
from agents.tdd_constitution import TDDConstitution

result = TDDConstitution.validate_tdd_compliance(execution_log)
# Returns:
# {
#   "compliant": bool,
#   "violations": List[ConstitutionViolation],
#   "score": float (0-100),
#   "evidence": Dict[str, Dict]
# }
```

### 2. Code Quality Validator (`code_quality_validator.py`)

Ejecuta herramientas automatizadas de QA.

**Herramientas:**
- **pytest + coverage**: Cobertura de tests
- **ruff**: Linting
- **mypy**: Type checking
- **bandit**: Seguridad
- **AST parser**: Docstrings

**API:**
```python
from agents.code_quality_validator import CodeQualityValidator

validator = CodeQualityValidator(project_root)
results = validator.run_all_checks(
    test_files=[Path("tests/test_auth.py")],
    source_files=[Path("apps/users/auth.py")],
    minimum_coverage=90.0
)
```

### 3. TDD Execution Logger (`tdd_execution_logger.py`)

Audit trail completo.

**Registra:**
- Timestamps de cada fase
- SHA256 hashes de artifacts
- Test executions
- Métricas de calidad
- Constitution result

**API:**
```python
from agents.tdd_execution_logger import TDDExecutionLogger

logger = TDDExecutionLogger(
    feature_name="user_authentication",
    output_dir=Path("docs/sdlc_outputs/tdd_logs")
)

logger.log_phase("red_phase", {"status": "started", ...})
logger.log_artifact(file_path, "unit_test")
logger.log_test_execution("red_phase", test_result)
log_path = logger.finalize(constitution_result)
```

### 4. TDD Metrics Dashboard (`tdd_metrics_dashboard.py`)

Dashboards visuales.

**Genera:**
- Badges de shields.io
- Tablas de métricas
- Timeline
- Violations summary

**API:**
```python
from agents.tdd_metrics_dashboard import TDDMetricsDashboard

TDDMetricsDashboard.generate_dashboard(
    execution_log=Path("logs/execution.json"),
    output_path=Path("logs/dashboard.md")
)
```

### 5. TDD Feature Agent (`tdd_feature_agent.py`)

Agente principal que orquesta todo.

**API:**
```python
from agents.tdd_feature_agent import TDDFeatureAgent

agent = TDDFeatureAgent(config={
    "project_root": "/path/to/project",
    "output_dir": "docs/sdlc_outputs",
    "minimum_coverage": 90.0
})

result = agent.execute({
    "issue_title": "Implement user authentication",
    "acceptance_criteria": [...],
    "technical_requirements": [...],
    "target_module": "apps.users"
})
```

## Constitution TDD

### Sistema de Reglas

| Regla | Severidad | Descripción | Auto-fix |
|-------|-----------|-------------|----------|
| RED_BEFORE_GREEN | CRITICAL | Tests antes del código | No |
| TESTS_MUST_FAIL_FIRST | CRITICAL | Tests fallan en RED | No |
| ALL_TESTS_MUST_PASS | CRITICAL | Tests pasan en GREEN | No |
| TESTS_STAY_GREEN_AFTER_REFACTOR | CRITICAL | Tests pasan después de REFACTOR | No |
| MINIMUM_COVERAGE | HIGH | Cobertura ≥ 90% | No |
| NO_SECURITY_ISSUES | HIGH | Sin vulnerabilidades | No |
| CODE_QUALITY_PASSING | MEDIUM | Pasa linting/types | Sí |
| DOCUMENTATION_REQUIRED | MEDIUM | Docstrings presentes | No |

### Evidencias Requeridas

Cada regla valida evidencias específicas:

**RED_BEFORE_GREEN:**
- Timestamp de red_phase < timestamp de green_phase

**TESTS_MUST_FAIL_FIRST:**
- Test execution en red_phase con failed > 0

**ALL_TESTS_MUST_PASS:**
- Test execution en green_phase con failed = 0

**TESTS_STAY_GREEN_AFTER_REFACTOR:**
- Test execution en refactor_phase con failed = 0

## Uso desde CLI

### Preparar Issue Data

```bash
cat > issue_data.json << EOF
{
  "issue_title": "Implement user authentication with 2FA",
  "acceptance_criteria": [
    "Users can register with email and password",
    "Users can login with email and password",
    "Users can enable 2FA with TOTP",
    "Failed login attempts are logged"
  ],
  "technical_requirements": [
    "Use Django authentication backend",
    "Implement TOTP with pyotp library",
    "Add audit logging for auth events",
    "Minimum 90% test coverage"
  ],
  "target_module": "callcentersite.apps.users"
}
EOF
```

### Ejecutar TDD Agent

```bash
# Ejecución básica
python scripts/sdlc_agent.py \
  --phase implementation \
  --issue-file issue_data.json

# Con verbose
python scripts/sdlc_agent.py \
  --phase implementation \
  --issue-file issue_data.json \
  --verbose

# Dry-run (no guarda artefactos)
python scripts/sdlc_agent.py \
  --phase implementation \
  --issue-file issue_data.json \
  --dry-run

# Output en JSON
python scripts/sdlc_agent.py \
  --phase implementation \
  --issue-file issue_data.json \
  --format json
```

### Outputs Generados

```
docs/sdlc_outputs/tdd_logs/
├── tdd_execution_user_authentication_20250115_143025.json
├── tdd_execution_user_authentication_20250115_143025.md
└── dashboard_user_authentication.md
```

## Sistema de Scoring

### Cálculo del Score (0-100)

**Pesos por Severidad:**
- **CRITICAL**: 40 puntos (4 reglas × 10 pts)
- **HIGH**: 30 puntos (2 reglas × 15 pts)
- **MEDIUM**: 30 puntos (4 reglas × 7.5 pts)

**Fórmula:**
```
score = 100 - Σ(penalties)

penalty(CRITICAL) = 10 puntos
penalty(HIGH) = 15 puntos
penalty(MEDIUM) = 7.5 puntos
```

### Clasificación

| Score | Clasificación | Resultado |
|-------|---------------|-----------|
| 100 | Perfect | ✅ COMPLIANT |
| 90-99 | Excellent | ✅ COMPLIANT |
| 75-89 | Good | ⚠️ COMPLIANT (con warnings) |
| 50-74 | Fair | ❌ NOT COMPLIANT |
| <50 | Poor | ❌ NOT COMPLIANT |

### Condiciones de Fallo

El agente **FALLA inmediatamente** si:
- Cualquier regla CRITICAL es violada
- Score < 100 Y existe al menos 1 violación CRITICAL

## Ejemplos de Output

### Dashboard Visual

```markdown
# TDD Metrics Dashboard: user_authentication

**Generated:** 2025-01-15 14:30:25

## Quick Status

![TDD_Compliance](https://img.shields.io/badge/TDD_Compliance-95.5%-green)
![Test_Coverage](https://img.shields.io/badge/Test_Coverage-92.3%-green)
![Security_Issues](https://img.shields.io/badge/Security_Issues-0-green)
![Code_Quality](https://img.shields.io/badge/Code_Quality-Pass-green)

## Overall Status

### ✅ TDD COMPLIANT

All CRITICAL rules passed. Compliance score: **95.5/100**

## Detailed Metrics

| Metric | Value | Status |
|--------|-------|--------|
| Test Coverage | 92.3% (234/254 lines) | ✅ Pass |
| Security Issues | 0 | ✅ Pass |
| Code Quality | 2 issues | ✅ Pass |
| Type Checking | 0 issues | ✅ Pass |
| Documentation | 15/15 functions | ✅ Pass |
```

### Execution Log (JSON)

```json
{
  "feature_name": "user_authentication",
  "start_timestamp": "2025-01-15T14:25:10.123456",
  "end_timestamp": "2025-01-15T14:30:25.789012",
  "duration_seconds": 315.67,
  "phases": {
    "red_phase": {
      "duration_seconds": 95.11,
      "status": "completed",
      "details": {
        "tests_total": 15,
        "tests_failed": 15
      }
    },
    "green_phase": {
      "duration_seconds": 147.11,
      "status": "completed",
      "details": {
        "tests_passed": 15,
        "coverage_percent": 92.3
      }
    }
  },
  "constitution_result": {
    "compliant": true,
    "score": 95.5,
    "violations": []
  }
}
```

## Integración con DORA Metrics

El TDD Feature Agent se integra con el sistema DORA metrics:

**Métricas Calculadas:**

1. **Lead Time for Changes**
   - Desde `start_timestamp` hasta `end_timestamp`
   - Almacenado en `duration_seconds`

2. **Deployment Frequency**
   - Features implementados por día
   - Calculado desde execution logs

3. **Change Failure Rate**
   - 0% si `constitution_result.compliant = true`
   - 100% si `constitution_result.compliant = false`

4. **Mean Time to Recovery**
   - N/A (agente previene fallos)

**Uso:**
```python
from dora_metrics import DORAMetricsCalculator

calculator = DORAMetricsCalculator(repo_path)
calculator.add_tdd_execution_log(execution_log_path)
metrics = calculator.calculate_all_metrics()
```

## Configuración

### Archivo de Configuración

```json
{
  "project_root": "/home/user/IACT---project",
  "output_dir": "docs/sdlc_outputs",
  "minimum_coverage": 90.0,
  "llm_provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022"
}
```

### Variables de Entorno

```bash
# API keys para LLM
export ANTHROPIC_API_KEY="sk-..."

# Coverage threshold
export TDD_MINIMUM_COVERAGE=90.0

# Output directory
export TDD_OUTPUT_DIR="docs/sdlc_outputs"
```

## Troubleshooting

### Problema: Tests no fallan en RED phase

**Síntomas:**
- Violation: `TESTS_MUST_FAIL_FIRST`
- Score reducido

**Causa:**
- Tests demasiado genéricos
- Implementación ya existe

**Solución:**
1. Revisar que tests sean específicos
2. Verificar que no exista código previo
3. Regenerar tests más estrictos

### Problema: Coverage bajo (<90%)

**Síntomas:**
- Violation: `MINIMUM_COVERAGE`
- Score: -15 puntos

**Causa:**
- Tests incompletos
- Edge cases no cubiertos

**Solución:**
1. Generar tests adicionales para edge cases
2. Verificar coverage report
3. Agregar tests para code paths no cubiertos

### Problema: Violations CRITICAL

**Síntomas:**
- `status: "failed"`
- Agent termina inmediatamente

**Causa:**
- Proceso TDD no seguido correctamente
- Timestamps incorrectos
- Tests no ejecutados

**Solución:**
1. Revisar execution log
2. Verificar evidencias de cada fase
3. Re-ejecutar fase problemática

## Mejores Prácticas

### 1. Preparación de Issues

✅ **DO:**
- Especificar acceptance criteria claros
- Incluir technical requirements
- Definir target_module específico

❌ **DON'T:**
- Issues vagos sin criterios
- Mezclar múltiples features
- Omitir technical requirements

### 2. Ejecución del Agent

✅ **DO:**
- Ejecutar con `--verbose` para debugging
- Revisar execution log después
- Verificar dashboard antes de merge

❌ **DON'T:**
- Ignorar violations
- Modificar código manualmente después
- Skippear validaciones

### 3. Mantenimiento

✅ **DO:**
- Archivar execution logs
- Trackear compliance score over time
- Integrar con CI/CD

❌ **DON'T:**
- Eliminar logs
- Bajar threshold de coverage
- Deshabilitar constitution checks

## Referencias

- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [DORA Metrics](https://www.devops-research.com/research.html)
- [Python Testing with pytest](https://docs.pytest.org/)
- [Code Coverage](https://coverage.readthedocs.io/)
- [Shields.io Badges](https://shields.io/)

---

**Documentación generada:** 2025-01-15
**Versión TDD Feature Agent:** 1.0.0
**Proyecto:** IACT - Internal Audit Compliance Tool
