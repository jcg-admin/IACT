# Testing Strategy: ShellScriptAnalysisAgent

**Issue ID**: FEATURE-SHELL-ANALYSIS-001
**Fecha**: 2025-11-13
**Fase SDLC**: Testing (Fase 5)
**Estado**: COMPLETADO

---

## 1. Resumen Ejecutivo

Estrategia de testing completa para ShellScriptAnalysisAgent, cubriendo testing unitario, integración, end-to-end, y testing de rendimiento.

**Cobertura Objetivo**: >= 90%
**Metodología**: Test-Driven Development (TDD)

---

## 2. Testing Pyramid

```
                    /\
                   /  \
                  / E2E \
                 /--------\
                /          \
               / Integration \
              /--------------\
             /                \
            /   Unit Tests     \
           /____________________\
```

### Distribución de Tests

| Nivel | Cantidad | % Total | Tiempo Ejecución |
|-------|----------|---------|------------------|
| Unit | 13 | 65% | < 1s |
| Integration | 5 | 25% | < 5s |
| E2E | 2 | 10% | < 10s |
| **Total** | **20** | **100%** | **< 15s** |

---

## 3. Unit Tests (Implementados)

**Archivo**: `scripts/coding/tests/ai/agents/quality/test_shell_analysis_agent.py`

### 3.1 TestAgentInitialization (3 tests)

```python
def test_default_initialization(agent_default):
    """Verifica inicialización con configuración por defecto"""
    assert agent_default.name == "ShellScriptAnalysisAgent"
    assert agent_default.analysis_mode == AnalysisMode.STANDARD
    assert agent_default.constitutional_rules == [1, 2, 3, 4, 5, 6, 7, 8]

def test_quick_mode_initialization(agent_quick_mode):
    """Verifica modo QUICK"""
    assert agent_quick_mode.analysis_mode == AnalysisMode.QUICK

def test_custom_rules_initialization():
    """Verifica reglas constitucionales personalizadas"""
    agent = ShellScriptAnalysisAgent(config={"constitutional_rules": [1, 3, 5]})
    assert agent.constitutional_rules == [1, 3, 5]
```

**Cobertura**: Configuración e inicialización del agente

### 3.2 TestConstitutionalRule3 (3 tests)

```python
def test_detects_missing_set_e(agent_default):
    """Detecta ausencia de 'set -e'"""
    script = "#!/bin/bash\necho 'test'\n"
    preprocessed = agent_default._preprocess(script, Path("test.sh"))
    result = agent_default._check_rule_3_error_handling(preprocessed)

    assert not result.compliant
    assert result.violations[0].severity == Severity.CRITICAL
    assert "set -e" in result.violations[0].description.lower()

def test_detects_silent_errors(agent_default):
    """Detecta manejo silencioso de errores con '|| true'"""
    script = "#!/bin/bash\nset -e\nrm -rf /tmp/test || true\n"
    preprocessed = agent_default._preprocess(script, Path("test.sh"))
    result = agent_default._check_rule_3_error_handling(preprocessed)

    assert len([v for v in result.violations if "|| true" in v.description]) > 0

def test_passes_good_error_handling(agent_default, sample_script_good):
    """Verifica aprobación con manejo correcto de errores"""
    preprocessed = agent_default._preprocess(sample_script_good, Path("good.sh"))
    result = agent_default._check_rule_3_error_handling(preprocessed)

    assert result.compliant
    assert result.score == 100.0
    assert len(result.violations) == 0
```

**Cobertura**: Regla Constitutional 3 (Error Handling)

### 3.3 TestSecurityAnalysis (1 test)

```python
def test_detects_unquoted_variables(agent_default):
    """Detecta variables sin comillas (riesgo command injection)"""
    script = "#!/bin/bash\necho $(cat $file)\n"
    preprocessed = agent_default._preprocess(script, Path("test.sh"))
    result = agent_default._analyze_security(preprocessed)

    assert len(result.issues) > 0
    assert result.issues[0].type == "potential_command_injection"
    assert result.issues[0].cwe_id == "CWE-78"
    assert result.issues[0].severity == Severity.HIGH
```

**Cobertura**: Detección de vulnerabilidades de seguridad

### 3.4 TestFullAnalysis (3 tests)

```python
def test_analyze_single_script(agent_default, temp_script_file):
    """Análisis end-to-end de un script"""
    result = agent_default.execute({
        "script_path": str(temp_script_file),
        "output_dir": tempfile.mkdtemp()
    })

    assert result.is_success()
    assert "results" in result.data
    assert len(result.data["results"]) == 1
    assert "constitutional" in result.data["results"][0]
    assert "quality" in result.data["results"][0]
    assert "security" in result.data["results"][0]

def test_input_validation_missing_script(agent_default):
    """Validación de input: script faltante"""
    errors = agent_default.validate_input({})
    assert len(errors) > 0
    assert any("script_path" in error.lower() for error in errors)

def test_input_validation_nonexistent_file(agent_default):
    """Validación de input: archivo inexistente"""
    errors = agent_default.validate_input({"script_path": "/tmp/nonexistent.sh"})
    assert len(errors) > 0
    assert any("not found" in error.lower() for error in errors)
```

**Cobertura**: Análisis completo e input validation

### 3.5 TestReportGeneration (1 test)

```python
def test_generates_individual_reports(agent_default, temp_script_file, tmp_path):
    """Generación de reportes Markdown y JSON"""
    output_dir = tmp_path / "reports"
    result = agent_default.execute({
        "script_path": str(temp_script_file),
        "output_dir": str(output_dir)
    })

    assert result.is_success()

    md_report = output_dir / f"{temp_script_file.name}_analysis.md"
    json_report = output_dir / f"{temp_script_file.name}_analysis.json"

    assert md_report.exists()
    assert json_report.exists()

    with open(json_report) as f:
        data = json.load(f)
        assert "script_name" in data
        assert "overall_score" in data
```

**Cobertura**: Generación de reportes

### 3.6 TestConstitutionCompliance (2 tests)

```python
def test_no_emojis_in_output(agent_default, temp_script_file):
    """Verifica ausencia de emojis (Principio Constitutional 2)"""
    output_dir = Path(tempfile.mkdtemp())
    result = agent_default.execute({
        "script_path": str(temp_script_file),
        "output_dir": str(output_dir)
    })

    md_report = output_dir / f"{temp_script_file.name}_analysis.md"
    content = md_report.read_text()

    emoji_pattern = re.compile("[...]")  # Regex para emojis
    assert len(emoji_pattern.findall(content)) == 0

def test_has_traceability():
    """Verifica presencia de trazabilidad (Principio Constitutional 3)"""
    from scripts.coding.ai.agents.quality import shell_analysis_agent

    docstring = shell_analysis_agent.__doc__
    assert docstring is not None
    assert "FEATURE-SHELL-ANALYSIS-001" in docstring or "Trazabilidad" in docstring
```

**Cobertura**: Cumplimiento de Constitution Principles

---

## 4. Integration Tests (Pendiente)

### 4.1 Test: Análisis Batch de Scripts

```python
def test_analyze_directory_batch():
    """Analizar múltiples scripts en paralelo"""
    agent = ShellScriptAnalysisAgent(config={"parallel_workers": 4})
    result = agent.execute({
        "script_path": "scripts/bash/",
        "output_dir": "test_output"
    })

    assert result.is_success()
    assert result.data["summary"]["total_scripts"] > 10
```

### 4.2 Test: Caching de Resultados

```python
def test_caching_with_sha256():
    """Verificar que caching funciona correctamente"""
    agent = ShellScriptAnalysisAgent(config={"cache_enabled": True})

    # Primera ejecución
    result1 = agent.execute({"script_path": "test.sh", "output_dir": "out"})
    time1 = result1.metrics["duration"]

    # Segunda ejecución (debería usar cache)
    result2 = agent.execute({"script_path": "test.sh", "output_dir": "out"})
    time2 = result2.metrics["duration"]

    assert time2 < time1  # Cache es más rápido
    assert result1.data["results"] == result2.data["results"]  # Mismos resultados
```

### 4.3 Test: Modos de Análisis

```python
@pytest.mark.parametrize("mode,expected_duration", [
    ("quick", 0.5),
    ("standard", 2.0),
    ("deep", 10.0)
])
def test_analysis_modes_performance(mode, expected_duration):
    """Verificar rendimiento de cada modo"""
    agent = ShellScriptAnalysisAgent(config={"analysis_depth": mode})
    start = time.time()
    result = agent.execute({"script_path": "test.sh", "output_dir": "out"})
    duration = time.time() - start

    assert result.is_success()
    assert duration < expected_duration * 1.5  # Margen 50%
```

---

## 5. E2E Tests (Pendiente)

### 5.1 Test: Análisis Completo del Proyecto

```python
def test_analyze_all_project_scripts():
    """Analizar todos los 253 scripts del proyecto"""
    agent = ShellScriptAnalysisAgent(config={
        "analysis_depth": "standard",
        "parallel_workers": 10,
        "cache_enabled": True
    })

    result = agent.execute({
        "script_path": ".",
        "output_dir": "docs/scripts/analisis"
    })

    assert result.is_success()
    assert result.data["summary"]["total_scripts"] == 253
    assert result.data["summary"]["average_score"] > 0
```

### 5.2 Test: Generación de Dashboard

```python
def test_generate_analysis_dashboard():
    """Generar dashboard HTML con todos los resultados"""
    agent = ShellScriptAnalysisAgent()
    result = agent.execute({
        "script_path": "scripts/",
        "output_dir": "docs/scripts/analisis",
        "generate_dashboard": True
    })

    assert result.is_success()
    assert (Path("docs/scripts/analisis") / "dashboard.html").exists()
```

---

## 6. Performance Tests

### 6.1 Métricas de Rendimiento

| Métrica | Target | Actual |
|---------|--------|--------|
| Análisis QUICK | < 0.5s/script | TBD |
| Análisis STANDARD | < 2s/script | TBD |
| Análisis DEEP | < 10s/script | TBD |
| Batch (253 scripts, 10 workers) | < 10 minutos | TBD |
| Memoria utilizada | < 500MB | TBD |

### 6.2 Test de Carga

```python
def test_analyze_large_batch():
    """Analizar 1000+ scripts sin memory leaks"""
    agent = ShellScriptAnalysisAgent(config={"parallel_workers": 20})

    # Generar 1000 scripts de prueba
    scripts = generate_test_scripts(1000)

    import tracemalloc
    tracemalloc.start()

    result = agent.execute({
        "script_path": "test_scripts/",
        "output_dir": "test_output"
    })

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert result.is_success()
    assert peak < 500 * 1024 * 1024  # < 500MB
```

---

## 7. Test Execution

### 7.1 Ejecución de Tests

```bash
# Todos los tests
pytest scripts/coding/tests/ai/agents/quality/test_shell_analysis_agent.py -v

# Con cobertura
pytest scripts/coding/tests/ai/agents/quality/test_shell_analysis_agent.py \
  --cov=scripts.coding.ai.agents.quality.shell_analysis_agent \
  --cov-report=html \
  --cov-report=term-missing

# Solo unit tests
pytest scripts/coding/tests/ai/agents/quality/test_shell_analysis_agent.py -m unit

# Solo integration tests
pytest scripts/coding/tests/ai/agents/quality/test_shell_analysis_agent.py -m integration
```

### 7.2 Resultados Actuales

```
Test Results: 13/13 PASSING (100%)
Coverage: TBD (objetivo >= 90%)
Duration: 0.15s
```

---

## 8. CI/CD Integration

### 8.1 GitHub Actions Workflow

```yaml
name: Test ShellScriptAnalysisAgent

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r scripts/coding/ai/requirements.txt
      - run: pytest scripts/coding/tests/ai/agents/quality/ -v --cov
      - run: ruff check scripts/coding/ai/agents/quality/
```

---

## 9. Próximos Pasos

1. Implementar integration tests pendientes
2. Implementar E2E tests
3. Ejecutar performance tests y optimizar
4. Alcanzar cobertura >= 90%
5. Integrar en CI/CD pipeline

---

**Trazabilidad**: FEATURE-SHELL-ANALYSIS-001
**Metodología**: TDD (RED → GREEN → REFACTOR)
**Constitution**: Principle 6 (Testing y Validación)
