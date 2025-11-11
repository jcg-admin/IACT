# TDD Agent

Agente que automatiza el ciclo Test-Driven Development completo.

## Propósito

Automatizar el flujo TDD para acelerar desarrollo de nuevos componentes:

1. **Generar tests** desde requisitos del usuario
2. **Ejecutar pytest** y capturar resultados
3. **Analizar fallos** con root cause analysis
4. **Documentar errores** en formato markdown
5. **Iterar** hasta 100% tests passing

## Arquitectura

```
TDD Agent (MVP)
├── Prompt: docs/backend/permisos/promptops/meta/tdd-agent.md
├── Agent: scripts/ai/agents/tdd/tdd_agent.py
└── Shell: scripts/ci/run-tdd-cycle.sh
```

### Componentes

**TDDAgent**
- `run_tdd_cycle()`: Orquesta ciclo completo
- `generate_test_template()`: Genera template de tests
- `run_tests()`: Ejecuta pytest y parsea output
- `analyze_failures()`: Analiza errores con root cause
- `generate_documentation()`: Crea docs markdown

**Dataclasses**
- `TDDRequirements`: Requisitos del componente
- `TestResult`: Resultado de ejecución pytest
- `TDDCycleReport`: Reporte final del ciclo

## Uso

### Opción 1: CLI directa

```bash
python3 scripts/ai/agents/tdd/tdd_agent.py \
    --component audit_validator \
    --requirements "Validar que todos los campos de audit log están presentes" \
    --type gate \
    --verbose
```

### Opción 2: Con archivo de requisitos JSON

```bash
# 1. Crear archivo de requisitos
cat > requirements/audit_validator.json <<EOF
{
  "component_name": "audit_validator",
  "requirements": "Validar que todos los campos de audit log están presentes",
  "agent_type": "gate",
  "expected_behavior": {
    "happy_path": "Detecta logs válidos correctamente",
    "edge_cases": [
      "Logs con campos opcionales missing",
      "Logs con timestamps en formatos diferentes"
    ],
    "error_cases": [
      "Logs sin campo 'action'",
      "Logs sin campo 'user_id'"
    ]
  },
  "dependencies": ["AuditLog model", "PermisoService"]
}
EOF

# 2. Ejecutar TDD Agent con shell script
./scripts/ci/run-tdd-cycle.sh audit_validator requirements/audit_validator.json gate
```

### Opción 3: Integración en pipeline CI/CD

```yaml
# .github/workflows/tdd.yml (si usáramos GitHub Actions)
# NOTA: Por restricciones del proyecto, usamos shell scripts en lugar de GitHub Actions

# Alternativa: scripts/ci/ci-pipeline.sh
stages:
  - name: "TDD Cycle"
    command: "./scripts/ci/run-tdd-cycle.sh audit_validator requirements/audit_validator.json gate"
```

## Workflow

```
[1. Parse Requirements]
        |
        v
[2. Generate Test Template]
        |
        v
[3. Run pytest (initial)]
        |
        v
[4. Analyze Failures]
        |
        v
[5. Generate Documentation]
        |
        v
[6. Exit (manual fixes)]
```

### Estado MVP

En la versión MVP actual:

- [OK] Genera template de tests desde requisitos
- [OK] Ejecuta pytest y parsea resultados
- [OK] Analiza fallos con información básica
- [OK] Genera documentación markdown detallada
- [WARNING] Requiere implementación manual de tests (TODOs generados)
- [WARNING] Requiere fixes manuales de errores

### Extensiones Futuras (Roadmap)

Ver: `docs/backend/permisos/promptops/ROADMAP_TDD_AGENT.md`

- Auto-generación de código de tests completo (no solo templates)
- Auto-fix de errores comunes
- Integración con LLM para sugerencias de solución
- Refactoring automático después de tests passing
- Análisis de cobertura de código

## Output

### Archivos Generados

**1. Test Template**
```
scripts/ai/agents/{component}/tests/test_{component}.py
```

Estructura:
- Test{Component}Basics: Tests básicos de funcionalidad
- Test{Component}EdgeCases: Tests de casos edge
- Test{Component}ErrorHandling: Tests de manejo de errores
- Test{Component}Integration: Tests end-to-end

**2. Documentación de Errores**
```
docs/backend/permisos/promptops/TDD_{COMPONENT}_ERRORS.md
```

Contiene:
- Summary de ejecución (passed/failed/skipped)
- Root cause analysis de cada error
- Soluciones propuestas para cada error
- Next steps para continuar ciclo TDD
- Métricas del ciclo (coverage, duration)

### Exit Codes

- `0`: Todos los tests pasaron (éxito completo)
- `1`: Tests fallaron, requiere intervención manual (MVP expected)
- `2`: Error de argumentos o configuración
- `3`: Error de ejecución (pytest no encontrado, etc.)

## Ejemplos

### Caso 1: Nuevo Gate Agent

```bash
# Requisitos: Gate que valida permisos en ViewSets
python3 scripts/ai/agents/tdd/tdd_agent.py \
    --component route_linter \
    --requirements "Detectar ViewSets sin permission_classes definidas" \
    --type gate

# Output:
# [OK] Test template generated: scripts/ai/agents/route_linter/tests/test_route_linter.py
# [WARNING] Initial run: 0/15 passing
# [ERROR] 15 errors discovered
# [OK] Documentation generated: docs/backend/permisos/promptops/TDD_ROUTE_LINTER_ERRORS.md
# [INFO] MVP Mode: Manual fixes required
```

### Caso 2: Nuevo Chain Agent

```bash
# Requisitos: Chain que valida múltiples condiciones en secuencia
python3 scripts/ai/agents/tdd/tdd_agent.py \
    --component permission_validator_chain \
    --requirements "Validar que usuario tiene permiso, luego validar que recurso existe, luego validar que acción está permitida" \
    --type chain

# Output:
# [OK] Test template generated: scripts/ai/agents/permission_validator_chain/tests/test_permission_validator_chain.py
# [WARNING] Initial run: 0/22 passing
# [ERROR] 22 errors discovered
# [OK] Documentation generated: docs/backend/permisos/promptops/TDD_PERMISSION_VALIDATOR_CHAIN_ERRORS.md
```

### Caso 3: Iteración Manual Post-TDD Agent

```bash
# 1. TDD Agent generó template y documentación
# 2. Revisar docs/backend/permisos/promptops/TDD_COMPONENT_ERRORS.md
# 3. Implementar tests según TODOs
# 4. Ejecutar tests manualmente

pytest scripts/ai/agents/route_linter/tests/test_route_linter.py -v

# Output esperado:
# test_agent_initialization PASSED
# test_happy_path FAILED  <- Fix code
# test_edge_case_1 FAILED <- Fix code
# ...

# 5. Fix errores
# 6. Re-run hasta 100% passing
# 7. Commit
```

## Integración con PromptOps

El TDD Agent sigue la metodología PromptOps:

**Estructura:**
```
Prompt (MD) + Agent (Python) + Shell (Bash)
```

**Ubicación:**
- Prompt: `docs/backend/permisos/promptops/meta/tdd-agent.md`
- Agent: `scripts/ai/agents/tdd/tdd_agent.py`
- Shell: `scripts/ci/run-tdd-cycle.sh`

**Proceso:**
1. Definir requisitos en JSON o CLI
2. TDD Agent genera tests y documentación
3. Desarrollador implementa fixes
4. Ciclo se repite hasta 100% passing

Ver: `docs/backend/permisos/promptops/CONTRIBUTING.md` para más detalles sobre metodología PromptOps.

## Requisitos

**Python:**
- Python 3.8+
- pytest
- pathlib (stdlib)
- dataclasses (stdlib)
- subprocess (stdlib)

**Sistema:**
- Bash (para shell script)
- Git (para detección de project root)

## Limitaciones MVP

1. **No genera código completo de tests**: Solo genera templates con TODOs
2. **No auto-fix errores**: Requiere intervención manual
3. **Parsing básico de pytest output**: Puede mejorar con pytest-json-report
4. **Sin integración LLM**: No usa AI para sugerencias (futuro)
5. **Sin refactoring automático**: Requiere refactor manual después de tests passing

## Roadmap

Ver archivo completo: `docs/backend/permisos/promptops/ROADMAP_TDD_AGENT.md`

**Versión 1.1 (Next):**
- Generación completa de tests (no templates)
- Uso de pytest-json-report para mejor parsing
- Auto-fix de errores comunes (imports, paths)

**Versión 2.0 (Future):**
- Integración con LLM local
- Análisis semántico de código
- Sugerencias de soluciones basadas en context

**Versión 3.0 (Vision):**
- Zero-intervention TDD cycle
- Auto-refactoring post-tests
- Coverage-driven test generation

---

**Generado por:** TDD Agent MVP v1.0
**Fecha:** 2025-11-11
**Proyecto:** IACT - Sistema de Permisos Granular
