# TDD Feature Agent

Sistema automatizado para implementar features siguiendo la metodología TDD (Test-Driven Development) con garantías de calidad y compliance.

## Descripción

El **TDD Feature Agent** es un agente SDLC especializado que implementa features automáticamente siguiendo estrictamente el ciclo RED-GREEN-REFACTOR de TDD. El agente garantiza compliance mediante un sistema de constitution checks, validación de calidad automatizada y generación de reportes completos.

## Arquitectura

El sistema está compuesto por 5 módulos principales:

### 1. TDD Constitution (`tdd_constitution.py`)

Reglas inmutables que NO PUEDEN ser violadas durante la ejecución TDD.

**Reglas CRITICAL** (causan fallo inmediato):
- `RED_BEFORE_GREEN`: Tests deben escribirse ANTES del código
- `TESTS_MUST_FAIL_FIRST`: Tests deben fallar inicialmente (RED phase)
- `ALL_TESTS_MUST_PASS`: Todos los tests deben pasar después de GREEN
- `TESTS_STAY_GREEN_AFTER_REFACTOR`: Tests deben seguir pasando después de REFACTOR

**Reglas HIGH** (deben corregirse):
- `MINIMUM_COVERAGE`: Cobertura ≥ 90%
- `NO_SECURITY_ISSUES`: Sin vulnerabilidades detectadas

**Reglas MEDIUM** (advertencias):
- `CODE_QUALITY_PASSING`: Código pasa linting y type checking
- `DOCUMENTATION_REQUIRED`: Funciones públicas tienen docstrings

**API Principal:**
```python
from tdd_constitution import TDDConstitution

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

Ejecuta herramientas automatizadas de QA:

**Herramientas integradas:**
- **pytest + coverage**: Cobertura de tests
- **ruff**: Linting y calidad de código
- **mypy**: Type checking
- **bandit**: Escaneo de seguridad
- **AST parser**: Verificación de docstrings

**API Principal:**
```python
from code_quality_validator import CodeQualityValidator

validator = CodeQualityValidator(project_root)

# Ejecutar todas las verificaciones
results = validator.run_all_checks(
    test_files=[...],
    source_files=[...],
    minimum_coverage=90.0
)
# Returns:
# {
#   "coverage": Dict,
#   "quality": Dict,
#   "type_check": Dict,
#   "security": Dict,
#   "documentation": Dict,
#   "overall_passed": bool
# }
```

### 3. TDD Execution Logger (`tdd_execution_logger.py`)

Audit trail completo con timestamps y file hashes.

**Funcionalidades:**
- Log de cada fase (RED, GREEN, REFACTOR)
- Tracking de artifacts con SHA256 hashes
- Registro de test executions
- Métricas de calidad
- Generación de reportes JSON y Markdown

**API Principal:**
```python
from tdd_execution_logger import TDDExecutionLogger

logger = TDDExecutionLogger(
    feature_name="user_authentication",
    output_dir=Path("logs")
)

# Log fase
logger.log_phase("red_phase", {
    "status": "started",
    "timestamp": datetime.now().isoformat()
})

# Log artifact
logger.log_artifact(
    file_path=Path("tests/test_auth.py"),
    artifact_type="unit_test"
)

# Log test execution
logger.log_test_execution("red_phase", {
    "total": 5,
    "passed": 0,
    "failed": 5
})

# Finalizar y generar reportes
log_path = logger.finalize(constitution_result)
```

### 4. TDD Metrics Dashboard (`tdd_metrics_dashboard.py`)

Dashboards visuales con badges.

**Funcionalidades:**
- Badges de shields.io para status rápido
- Tablas de métricas
- Timeline de ejecución
- Resumen de violations

**API Principal:**
```python
from tdd_metrics_dashboard import TDDMetricsDashboard

# Generar dashboard
TDDMetricsDashboard.generate_dashboard(
    execution_log=Path("logs/execution.json"),
    output_path=Path("logs/dashboard.md")
)

# Generar badge individual
badge = TDDMetricsDashboard.generate_badge(
    label="TDD_Compliance",
    value="95.5%",
    color="green"
)
```

### 5. TDD Feature Agent (`tdd_feature_agent.py`)

Agente principal que orquesta todo el proceso.

**Flujo de ejecución:**
1. **RED Phase**: Genera tests unitarios que fallan
2. **GREEN Phase**: Implementa código para pasar tests
3. **REFACTOR Phase**: Optimiza código manteniendo tests verdes
4. **Validation**: Valida constitution compliance
5. **Reporting**: Genera reportes y dashboard

**API Principal:**
```python
from tdd_feature_agent import TDDFeatureAgent

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

# Returns:
# {
#   "status": "success" | "failed",
#   "constitution_result": {...},
#   "metrics": {...},
#   "execution_log": "path/to/log.json",
#   "dashboard": "path/to/dashboard.md",
#   "artifacts": [...]
# }
```

## Uso desde CLI

### Ejecutar fase de implementación TDD

```bash
# Preparar issue data
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

# Ejecutar TDD agent
python scripts/sdlc_agent.py \
  --phase implementation \
  --issue-file issue_data.json \
  --verbose
```

### Resultado

El agente genera:

1. **Execution Log** (`tdd_execution_<feature>_<timestamp>.json`)
   - Log completo en JSON
   - Timestamps de cada fase
   - SHA256 hashes de artifacts
   - Test executions
   - Métricas de calidad

2. **Markdown Report** (`tdd_execution_<feature>_<timestamp>.md`)
   - Reporte human-readable
   - Constitution violations
   - Test summaries
   - Metrics tables

3. **Dashboard** (`dashboard_<feature>.md`)
   - Badges visuales
   - Status rápido
   - Timeline de ejecución
   - Artifacts generados

## Constitution Compliance

### Sistema de Scoring

El score de compliance (0-100) se calcula con pesos por severidad:

- **CRITICAL**: 40 puntos (4 reglas × 10 puntos)
- **HIGH**: 30 puntos (2 reglas × 15 puntos)
- **MEDIUM**: 30 puntos (4 reglas × 7.5 puntos)

**Clasificación:**
- `100`: Perfect compliance
- `90-99`: Excellent
- `75-89`: Good
- `50-74`: Fair
- `<50`: Poor

### Fallo del agente

El agente **FALLA inmediatamente** si:
- Cualquier regla CRITICAL es violada
- Tests no se escriben antes del código (RED_BEFORE_GREEN)
- Tests no fallan en fase RED (TESTS_MUST_FAIL_FIRST)
- Tests no pasan en fase GREEN (ALL_TESTS_MUST_PASS)
- Tests se rompen en REFACTOR (TESTS_STAY_GREEN_AFTER_REFACTOR)

## Ejemplo de Output

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
      "start_timestamp": "2025-01-15T14:25:10.123456",
      "end_timestamp": "2025-01-15T14:26:45.234567",
      "duration_seconds": 95.11,
      "status": "completed",
      "details": {
        "test_files_generated": 3,
        "tests_total": 15,
        "tests_failed": 15
      }
    },
    "green_phase": {
      "start_timestamp": "2025-01-15T14:26:45.345678",
      "end_timestamp": "2025-01-15T14:29:12.456789",
      "duration_seconds": 147.11,
      "status": "completed",
      "details": {
        "source_files_generated": 2,
        "tests_passed": 15,
        "tests_total": 15,
        "coverage_percent": 92.3
      }
    },
    "refactor_phase": {
      "start_timestamp": "2025-01-15T14:29:12.567890",
      "end_timestamp": "2025-01-15T14:30:15.678901",
      "duration_seconds": 63.11,
      "status": "completed",
      "details": {
        "refactoring_applied": true,
        "tests_still_passing": true
      }
    }
  },
  "constitution_result": {
    "compliant": true,
    "score": 95.5,
    "violations": [
      {
        "rule_code": "DOCUMENTATION_REQUIRED",
        "severity": "MEDIUM",
        "message": "1/15 funciones públicas sin docstrings"
      }
    ]
  }
}
```

## Integración con DORA Metrics

El TDD Feature Agent se integra con el sistema DORA metrics existente:

**Métricas calculadas:**
- **Lead Time**: Desde inicio hasta fin de implementación
- **Deployment Frequency**: Features implementados por día
- **Change Failure Rate**: 0% si constitution pasa
- **Quality Score**: Constitution score como métrica de calidad

## Roadmap

### Implementado ✅
- [x] Constitution checks con 8 reglas
- [x] Execution logger con audit trail
- [x] Code quality validator (pytest, ruff, mypy, bandit)
- [x] Metrics dashboard con badges
- [x] CLI integration

### Por implementar 🚧
- [ ] Generación de tests usando LLM
- [ ] Generación de código usando LLM
- [ ] Refactoring inteligente usando LLM
- [ ] Auto-fix de violations cuando sea posible
- [ ] Integration tests generation
- [ ] E2E tests generation

## Configuración

### Archivo de configuración

```json
{
  "project_root": "/path/to/project",
  "output_dir": "docs/sdlc_outputs",
  "minimum_coverage": 90.0,
  "llm_provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022"
}
```

### Variables de entorno

```bash
# API keys para LLM
export ANTHROPIC_API_KEY="sk-..."

# Coverage threshold
export TDD_MINIMUM_COVERAGE=90.0

# Output directory
export TDD_OUTPUT_DIR="docs/sdlc_outputs"
```

## Testing

Para ejecutar los tests del TDD Feature Agent:

```bash
# Tests unitarios
pytest scripts/ai/agents/tests/test_tdd_constitution.py
pytest scripts/ai/agents/tests/test_code_quality_validator.py
pytest scripts/ai/agents/tests/test_tdd_execution_logger.py

# Tests de integración
pytest scripts/ai/agents/tests/test_tdd_feature_agent.py
```

## Troubleshooting

### Problema: Tests no fallan en RED phase

**Causa**: Tests demasiado genéricos o implementación ya existente

**Solución**: Revisar que tests sean específicos y que no haya código previo

### Problema: Coverage bajo (<90%)

**Causa**: Tests incompletos o código no testeado

**Solución**: Generar tests adicionales para edge cases

### Problema: Constitution violations

**Causa**: No se siguió el proceso TDD correctamente

**Solución**: Revisar execution log y corregir violaciones

## Referencias

- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [DORA Metrics](https://www.devops-research.com/research.html)
- [Python Testing with pytest](https://docs.pytest.org/)
- [Code Coverage](https://coverage.readthedocs.io/)

## Licencia

Parte del proyecto IACT - Internal Audit Compliance Tool
