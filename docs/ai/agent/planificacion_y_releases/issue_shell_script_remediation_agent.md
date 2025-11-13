---
title: Issue: ShellScriptRemediationAgent
date: 2025-11-13
domain: ai
status: active
---

# Issue: ShellScriptRemediationAgent

**Issue ID**: FEATURE-SHELL-REMEDIATION-001
**Tipo**: Feature Request
**Prioridad**: P0 (Critical)
**Story Points**: 21
**Fecha Creación**: 2025-11-13
**Estado**: PLANNING
**Asignado**: AI Agent Development Team

---

## 1. Descripción

Crear un agente de remediación automática que corrija violations de Shell Constitution encontradas por ShellScriptAnalysisAgent. El agente debe aplicar fixes automáticos, validar cambios, y generar reports de remediación.

### 1.1 Contexto

El proyecto cuenta con:
- ShellScriptAnalysisAgent implementado y funcional
- 157 scripts analizados con 503 issues identificados
- Plan de remediación por dominios (DDD) generado
- Score actual: 91.9/100, target: 98.0+

**Issues Identificados**:
- 387 Security issues (unquoted variables) - HIGH
- 116 Constitutional violations (|| true, missing set -e) - 21 CRITICAL + 95 HIGH
- Distribuidos en 17 dominios funcionales

### 1.2 Motivación

**Problema Actual**:
- Remediación manual de 503 issues requiere ~20 días de trabajo
- Alto riesgo de errores humanos en fixes repetitivos
- Difícil mantener consistencia en 157 scripts
- Testing manual propenso a errores
- **Limitación de agentes rule-based**: Solo arreglan patterns conocidos

**Solución Propuesta (LLM-Powered)**:
Crear ShellScriptRemediationAgent **inteligente** que use:
- **LLM + Prompt Engineering**: Para remediar CUALQUIER tipo de issue (no solo predefinidos)
- **Chain-of-Thought (CoT)**: Razonamiento paso a paso del fix correcto
- **Few-shot Learning**: Ejemplos de remediaciones exitosas
- **Auto-Context Detection**: Identificación automática de dominio/propósito del script
- **Self-Reflection**: Validación LLM del fix antes de aplicar
- **Constitutional AI**: Asegurar que fixes siguen Shell Constitution

**Ventaja clave**: Agente generalizable que puede remediar issues **nunca vistos antes**

---

## 2. Requisitos Funcionales

### RF-001: Análisis de Input
El agente DEBE:
- Leer análisis de ShellScriptAnalysisAgent (JSON)
- Clasificar issues por tipo (constitutional, security, quality)
- Priorizar issues por severidad (CRITICAL → HIGH → MEDIUM → LOW)
- Agrupar issues por script

### RF-002: Auto-Fixing de Constitutional Issues
El agente DEBE aplicar fixes automáticos para:

**Fix 1: Add set -euo pipefail**
- Detectar scripts sin `set -e` o `set -euo pipefail`
- Insertar después de shebang y antes de primer comando
- Preservar comentarios existentes

**Fix 2: Replace || true patterns**
- Detectar `command || true` patterns
- Reemplazar con error handling explícito:
  ```bash
  # BEFORE
  rm file.txt || true

  # AFTER
  if ! rm file.txt; then
      log_warning "Failed to remove file.txt, continuing..."
  fi
  ```
- Preservar intentionalidad original

**Fix 3: Remove unnecessary || true**
- Detectar casos donde || true es innecesario
- Remover pattern completamente

### RF-003: Auto-Fixing de Security Issues
El agente DEBE aplicar fixes automáticos para:

**Fix 1: Quote variables**
- Detectar variables sin comillas: `$var`, `${var}`
- Reemplazar con: `"$var"`, `"${var}"`
- Excepciones: arrays (`"${array[@]}"`), arithmetic contexts

**Fix 2: Quote command substitutions**
- Detectar: `$(command)` sin comillas
- Reemplazar con: `"$(command)"`

**Fix 3: Quote glob patterns**
- Detectar: `*.txt` sin comillas en contextos inseguros
- Agregar comillas donde necesario

### RF-004: Validación Post-Fix
El agente DEBE validar cada fix:
- Syntax check con `bash -n script.sh`
- ShellCheck validation (si disponible)
- Re-analysis con ShellScriptAnalysisAgent
- Rollback automático si validación falla

### RF-005: Backup y Rollback
El agente DEBE:
- Crear backup de script original antes de modificar
- Guardar en `.remediation_backup/`
- Permitir rollback automático en caso de error
- Mantener historial de cambios

### RF-006: Report Generation
El agente DEBE generar:
- Per-script remediation report (MD + JSON)
- Domain-level summary
- Consolidated remediation report
- Before/After comparison statistics

### RF-007: Dry-Run Mode
El agente DEBE soportar modo dry-run:
- Mostrar fixes propuestos sin aplicarlos
- Generar report de "what would be fixed"
- Permitir revisión manual antes de aplicar

### RF-008: Selective Remediation
El agente DEBE permitir:
- Remediar solo scripts específicos
- Remediar solo dominios específicos
- Remediar solo tipos de issues específicos (constitutional vs security)
- Remediar solo severidades específicas (CRITICAL only, etc.)

---

## 3. Requisitos No Funcionales

### RNF-001: Safety
- **Zero Breaking Changes**: Validación exhaustiva antes de commitear
- **Backup obligatorio**: Todos los scripts modificados tienen backup
- **Rollback automático**: Si tests fallan, revertir cambios

### RNF-002: Performance
- **Batch processing**: Remediar múltiples scripts en paralelo (10 workers)
- **Incremental**: Solo remediar scripts con issues pendientes
- **Caching**: No re-remediar scripts ya procesados

### RNF-003: Correctness
- **Syntax validation**: 100% de scripts modificados pasan `bash -n`
- **Re-analysis**: Score improvement verificado post-remediación
- **Test execution**: Tests del script pasan después de remediation

### RNF-004: Observability
- **Logging detallado**: Cada fix aplicado loggeado
- **Metrics**: Issues fixed, scripts modified, success rate
- **Reports**: Before/After comparison clara

### RNF-005: Constitution Compliance
- Seguir Principles 1-8
- Sin emojis en output
- Trazabilidad completa
- Testing exhaustivo (TDD)

---

## 4. Acceptance Criteria

### AC-1: Componentes Implementados
- [x] ShellScriptRemediationAgent class (hereda de Agent)
- [x] ConstitutionalFixer component (set -e, || true)
- [x] SecurityFixer component (quote variables)
- [x] SyntaxValidator component (bash -n, ShellCheck)
- [x] BackupManager component (backup/rollback)
- [x] ReportGenerator component (MD + JSON reports)

### AC-2: Auto-Fixing Exitoso
El agente remueve TODOS los issues automáticamente fixables:
- Add `set -euo pipefail`: 21 scripts → 0
- Quote variables: 387 issues → 0
- Replace `|| true`: 95 HIGH + others → manejo explícito

### AC-3: Score Improvement
Post-remediación:
- Average score: 91.9 → 98.0+ (target achieved)
- CRITICAL issues: 21 → 0
- HIGH issues: 482 → <50
- Total issues: 503 → <50

### AC-4: Safety Validation
- 100% de scripts modificados pasan `bash -n`
- 100% de scripts con tests existentes pasan tests
- 0 breaking changes introducidos
- Backup de 100% de scripts modificados

### AC-5: Selective Remediation
El agente soporta:
- `--domain infrastructure/vagrant` (solo ese dominio)
- `--severity CRITICAL` (solo critical issues)
- `--type constitutional` (solo constitutional)
- `--dry-run` (preview sin aplicar)

### AC-6: Integration con Ecosystem
- CLI interface (`python -m scripts.cli.shell_remediation_agent`)
- Importable como library
- Compatible con CI/CD pipelines
- Integra con ShellScriptAnalysisAgent

### AC-7: Testing Coverage
- Unit tests: >= 20 tests
- Integration tests: >= 5 tests
- E2E test: Remediation completa de domain sample
- Coverage: >= 90%

### AC-8: Documentation Completa
- SDLC Phase 1: Planning (este documento)
- SDLC Phase 2: Feasibility study
- SDLC Phase 3: HLD, ADRs, LLD
- SDLC Phase 4: Implementation + Tests
- SDLC Phase 5: Testing strategy
- SDLC Phase 6: Deployment plan

---

## 5. Tipos de Fixes Soportados

### 5.1 Constitutional Fixes (Priority 1)

**CRITICAL: Missing set -e**
```bash
# BEFORE
#!/bin/bash
# Script without error handling

# AFTER
#!/bin/bash
set -euo pipefail
# Script with strict error handling
```

**HIGH: || true patterns**
```bash
# BEFORE
mkdir /tmp/dir || true
rm file.txt || true

# AFTER
if ! mkdir /tmp/dir; then
    log_warning "Directory already exists or cannot be created"
fi
if ! rm file.txt; then
    log_warning "File does not exist or cannot be removed"
fi
```

### 5.2 Security Fixes (Priority 2)

**HIGH: Unquoted variables**
```bash
# BEFORE
echo $HOME
cd $DIR
rm $FILE

# AFTER
echo "$HOME"
cd "$DIR"
rm "$FILE"
```

**HIGH: Unquoted command substitutions**
```bash
# BEFORE
FILES=$(ls *.txt)
echo $FILES

# AFTER
FILES="$(ls *.txt)"
echo "$FILES"
```

**MEDIUM: Unquoted glob patterns**
```bash
# BEFORE
for file in *.txt; do
    process $file
done

# AFTER
for file in *.txt; do
    process "$file"
done
```

### 5.3 Quality Fixes (Priority 3)

**LOW: Code formatting**
- Consistent indentation
- Spacing around operators
- Blank lines between functions

---

## 6. Fix Strategies por Tipo

### Strategy 1: Conservative (Default)
- Only apply fixes with HIGH confidence (>95%)
- Skip ambiguous cases
- Manual review queue for uncertain fixes

### Strategy 2: Aggressive
- Apply all possible fixes (>80% confidence)
- More comprehensive but riskier
- Requires thorough post-validation

### Strategy 3: Surgical
- Apply only specific fix types
- User-selected patterns
- Maximum control, minimum risk

---

## 7. Validation Pipeline

```
1. Parse analysis results
   ↓
2. Classify issues by type
   ↓
3. Generate fix plan
   ↓
4. Backup original script
   ↓
5. Apply fixes (in order: CRITICAL → HIGH → MEDIUM → LOW)
   ↓
6. Syntax validation (bash -n)
   ↓ PASS
7. Re-analysis (ShellScriptAnalysisAgent)
   ↓ IMPROVED
8. Test execution (if tests exist)
   ↓ PASS
9. Generate report
   ↓
10. Commit changes

   ↓ FAIL at any step
   → Rollback from backup
   → Log failure
   → Move to manual review queue
```

---

## 8. Prompt Engineering Strategy (LLM-Powered Remediation)

### 8.1 Architecture: Hybrid LLM + Rule-Based

**Two-Tier Approach**:
1. **Tier 1 (Rule-Based)**: Fast, deterministic fixes para patterns bien conocidos
   - Quote unquoted variables
   - Add `set -euo pipefail`
   - Syntax validation
   - **Coverage**: ~60% de issues (triviales)

2. **Tier 2 (LLM-Powered)**: Intelligent fixes para cases complejos
   - Context-dependent fixes
   - Domain-specific logic
   - Ambiguous cases
   - **Coverage**: ~40% de issues (no-triviales)

### 8.2 Context Detection Prompt (Auto-Domain Classification)

```python
CONTEXT_DETECTION_PROMPT = """
Analyze this shell script and identify its context:

SCRIPT PATH: {script_path}
SCRIPT CONTENT:
```bash
{script_content}
```

Provide:
1. **Domain**: Which domain does this script belong to?
   Options: infrastructure/vagrant, infrastructure/cpython, infrastructure/devcontainer,
            scripts/validation, scripts/ci, scripts/git-hooks, scripts/root, etc.

2. **Purpose**: What is the primary purpose of this script? (1-2 sentences)

3. **Dependencies**: What external systems/commands does this script depend on?
   Examples: apt, yum, docker, vagrant, python, npm, etc.

4. **Risk Level**: How risky is it to modify this script?
   Options: LOW (dev scripts), MEDIUM (CI scripts), HIGH (production deployment)

5. **Testing Strategy**: How should fixes be tested?
   Examples: "Run script with --dry-run", "Check docker container starts", etc.

Respond in JSON format:
{
  "domain": "...",
  "purpose": "...",
  "dependencies": ["...", "..."],
  "risk_level": "LOW|MEDIUM|HIGH",
  "testing_strategy": "..."
}
"""
```

### 8.3 Chain-of-Thought Remediation Prompt

```python
COT_REMEDIATION_PROMPT = """
You are an expert shell script remediation agent. Your task is to fix violations found in a shell script.

CONTEXT:
- Script Path: {script_path}
- Domain: {domain}
- Purpose: {purpose}
- Risk Level: {risk_level}

SCRIPT CONTENT:
```bash
{script_content}
```

VIOLATIONS FOUND:
{violations_json}

Example Violation:
{
  "line": 42,
  "type": "security",
  "severity": "HIGH",
  "rule": "unquoted_variable",
  "message": "Variable $DIR is unquoted (potential word splitting)",
  "context": "cd $DIR && rm file.txt"
}

TASK:
For EACH violation, provide a fix using Chain-of-Thought reasoning:

1. **Understand**: What is the violation and why is it problematic?
2. **Analyze**: What is the script trying to do in this context?
3. **Consider**: Are there edge cases or special handling needed?
4. **Fix**: What is the correct remediation?
5. **Validate**: Will this fix break anything?

OUTPUT FORMAT (JSON):
{
  "fixes": [
    {
      "violation_line": 42,
      "reasoning": {
        "understand": "Variable $DIR is unquoted, can cause issues if path contains spaces",
        "analyze": "Script is changing directory to $DIR then removing a file",
        "consider": "If DIR contains spaces, cd will fail. Need to quote.",
        "fix": "Change 'cd $DIR' to 'cd \"$DIR\"'",
        "validate": "Quoting preserves spaces. No breaking change expected."
      },
      "fix_type": "quote_variable",
      "original_line": "cd $DIR && rm file.txt",
      "fixed_line": "cd \"$DIR\" && rm file.txt",
      "confidence": 0.99,
      "risk": "LOW"
    }
  ]
}

IMPORTANT:
- Be conservative. If unsure (confidence < 0.80), mark for manual review
- Consider the domain and purpose when fixing
- Preserve original functionality
- Follow Shell Constitution principles
"""
```

### 8.4 Few-Shot Learning Examples

```python
FEW_SHOT_EXAMPLES = """
Here are examples of GOOD remediations:

EXAMPLE 1: Quote variable in command
BEFORE:
```bash
rm $FILE
```
VIOLATION: Unquoted variable $FILE
AFTER:
```bash
rm "$FILE"
```
REASONING: Quoting prevents word splitting if filename contains spaces

---

EXAMPLE 2: Add error handling to || true
BEFORE:
```bash
mkdir /tmp/build || true
```
VIOLATION: Silent error with || true (Constitutional Rule 3)
AFTER:
```bash
if ! mkdir /tmp/build; then
    log_warning "Build directory already exists or cannot be created"
fi
```
REASONING: Explicit error handling makes failures visible and debuggable

---

EXAMPLE 3: Add set -euo pipefail
BEFORE:
```bash
#!/bin/bash
# Script content
```
VIOLATION: Missing set -e (CRITICAL)
AFTER:
```bash
#!/bin/bash
set -euo pipefail
# Script content
```
REASONING: Fail fast on errors, undefined variables, pipe failures

---

EXAMPLE 4: Context-dependent fix (DON'T quote in array context)
BEFORE:
```bash
files=("file1.txt" "file2.txt")
for f in "${files[@]}"; do
    echo $f  # VIOLATION: Unquoted variable
done
```
AFTER:
```bash
files=("file1.txt" "file2.txt")
for f in "${files[@]}"; do
    echo "$f"  # FIXED: Quote variable in echo
done
```
REASONING: Array expansion "${files[@]}" is correct (don't change), but $f in echo needs quotes

---

EXAMPLE 5: Domain-specific fix (Vagrant provisioning)
BEFORE:
```bash
# In vagrant provision script
apt-get install -y python3 || true
```
VIOLATION: || true hides errors
CONTEXT: Domain = infrastructure/vagrant, Purpose = provision VM
AFTER:
```bash
# Retry logic for transient network failures in Vagrant
for attempt in 1 2 3; do
    if apt-get install -y python3; then
        break
    fi
    if [ $attempt -lt 3 ]; then
        echo "Retrying apt-get install (attempt $attempt/3)..."
        sleep 5
    else
        echo "ERROR: Failed to install python3 after 3 attempts"
        exit 1
    fi
done
```
REASONING: In vagrant domain, apt-get can fail due to network issues. Retry with backoff is appropriate fix, not just error logging.
"""
```

### 8.5 Self-Reflection Validation Prompt

```python
SELF_REFLECTION_PROMPT = """
You proposed the following fix for a shell script violation:

ORIGINAL LINE:
{original_line}

PROPOSED FIX:
{fixed_line}

CONTEXT:
- Script: {script_path}
- Domain: {domain}
- Violation Type: {violation_type}

TASK: Validate your own fix by answering these questions:

1. **Correctness**: Is the fixed line syntactically correct bash?
2. **Functionality**: Does it preserve the original functionality?
3. **Edge Cases**: Are there edge cases where this fix could break?
4. **Constitution**: Does it comply with Shell Constitution principles?
5. **Domain Fit**: Is this fix appropriate for the {domain} domain?

OUTPUT (JSON):
{
  "validation": {
    "correct_syntax": true|false,
    "preserves_functionality": true|false,
    "edge_cases": ["list any edge cases"],
    "constitution_compliant": true|false,
    "domain_appropriate": true|false
  },
  "confidence": 0.0-1.0,
  "recommendation": "APPLY" | "MANUAL_REVIEW" | "SKIP"
}

If ANY validation fails OR confidence < 0.80, recommend MANUAL_REVIEW.
"""
```

### 8.6 Constitutional AI Prompt

```python
CONSTITUTIONAL_PROMPT = """
Verify that this remediation complies with Shell Constitution:

CONSTITUTION PRINCIPLES:
1. Fail fast: Use set -euo pipefail
2. Quote variables: Always quote variables to prevent word splitting
3. Explicit error handling: No silent || true patterns
4. Traceability: Comments explain WHY, code explains WHAT
5. Logging: Important operations logged
6. Idempotency: Scripts can be re-run safely
7. Security: No hardcoded secrets, validate inputs
8. Testing: Scripts are testable

FIX APPLIED:
```bash
{fixed_code}
```

QUESTION: Does this fix comply with ALL applicable principles?

OUTPUT (JSON):
{
  "compliant": true|false,
  "principles_checked": [1, 2, 3, ...],
  "violations": [
    {
      "principle": 3,
      "issue": "Still uses || true pattern",
      "suggestion": "Replace with explicit if-statement"
    }
  ]
}
"""
```

### 8.7 Adaptive Strategy Selection

```python
def select_remediation_strategy(violation, context, script_complexity):
    """
    Adaptive strategy selection based on violation type, context, and complexity
    """

    # TIER 1: Rule-based (fast, deterministic)
    RULE_BASED_PATTERNS = {
        "unquoted_variable_simple": r'\$\w+',  # $VAR without quotes
        "missing_set_e": "#!/bin/bash\n(?!set -)",
        "basic_or_true": r'\|\|\s*true\s*$'
    }

    if violation matches RULE_BASED_PATTERNS and context.risk_level == "LOW":
        return "RULE_BASED"

    # TIER 2: LLM-powered (intelligent, context-aware)
    LLM_REQUIRED_CONDITIONS = [
        script_complexity > 100,  # Complex scripts
        context.risk_level in ["MEDIUM", "HIGH"],  # Risky changes
        violation.type == "context_dependent",  # Needs understanding
        context.domain in ["infrastructure/vagrant", "production"],  # Critical domains
        violation.ambiguous == True  # Not clear-cut fix
    ]

    if any(LLM_REQUIRED_CONDITIONS):
        return "LLM_COT"  # Use Chain-of-Thought

    # TIER 1.5: Hybrid (rule-based + LLM validation)
    return "HYBRID"  # Apply rule fix, then LLM validates
```

### 8.8 Prompt Engineering Benefits

1. **Generalization**: Puede remediar CUALQUIER issue, no solo predefinidos
2. **Context-Awareness**: Entiende dominio y propósito del script
3. **Safety**: Self-reflection previene fixes incorrectos
4. **Adaptability**: Aprende de ejemplos (few-shot)
5. **Compliance**: Constitutional AI asegura adherencia a principios

### 8.9 Fallback Strategy

```
1. Try LLM remediation (CoT + Self-Reflection)
   ↓ confidence >= 0.80
2. Apply fix
   ↓ validation fails
3. Try alternative LLM fix (different reasoning)
   ↓ still fails
4. Add to MANUAL_REVIEW queue
   ↓
5. Log reason for manual review
   ↓
6. Generate detailed report for human reviewer
```

---

## 9. Dominios Target (Auto-CoT)

Basado en análisis de ShellScriptAnalysisAgent, priorizar:

**P0 (Critical Impact)**:
1. infrastructure/vagrant (69 issues, score 83.8)
2. infrastructure/cpython (67 issues, score 90.2)
3. infrastructure/devcontainer (60 issues, score 87.8)
4. scripts/validation (56 issues, score 93.2)
5. infrastructure/other (52 issues, score 92.1)
6. scripts/root (51 issues, score 92.6)

**P1 (High Impact)**:
7. scripts/git-hooks (45 issues, score 85.2)
8. scripts/coding (39 issues, score 91.5)

**P2 (Medium Impact)**:
9. infrastructure/box (19 issues, score 94.4)
10. scripts/ci (18 issues, score 96.3)
11. scripts/workflows (11 issues, score 94.5)

**P3 (Low Impact)**:
12-17. Remaining domains (<10 issues each)

---

## 9. Success Metrics

| Metric | Baseline | Target | How to Measure |
|--------|----------|--------|----------------|
| Average Score | 91.9/100 | 98.0+/100 | Re-analysis post-remediation |
| Total Issues | 503 | <50 | Issue count delta |
| CRITICAL Issues | 21 | 0 | Severity breakdown |
| Security HIGH Issues | 387 | <20 | Security category |
| Scripts Auto-Fixed | 0 | 120+ (80%+) | Success count |
| Breaking Changes | N/A | 0 | Test execution |
| Remediation Time | ~20 days manual | <4 hours automated | Wall clock time |

---

## 10. Risks and Mitigations

### Risk 1: Breaking Changes por Auto-Fixing
**Impact**: CRITICAL
**Probability**: MEDIUM
**Mitigation**:
- Comprehensive syntax validation
- Re-run all tests post-remediation
- Rollback automático on failure
- Conservative fix strategy por default
- Manual review queue for ambiguous cases

### Risk 2: False Positives en Fixes
**Impact**: HIGH
**Probability**: MEDIUM
**Mitigation**:
- Whitelist de patterns seguros (>95% confidence)
- Blacklist de patterns peligrosos (skip)
- Context-aware fixing (considerar scope, etc.)
- Manual review de fixes no-triviales

### Risk 3: Performance con 157 Scripts
**Impact**: MEDIUM
**Probability**: LOW
**Mitigation**:
- Parallel processing (10 workers)
- Batch por dominios
- Caching de resultados
- Incremental remediation

### Risk 4: Backup Storage
**Impact**: LOW
**Probability**: LOW
**Mitigation**:
- Usar .remediation_backup/ (gitignored)
- Límite de 30 días de retention
- Cleanup automático de backups antiguos

---

## 11. Timeline (Estimated)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Planning (Phase 1) | 0.5 day | This document |
| Feasibility (Phase 2) | 0.5 day | Feasibility study with Self-Consistency |
| Design (Phase 3) | 1 day | HLD, ADRs, LLD |
| Implementation RED (Phase 4) | 0.5 day | Tests written (failing) |
| Implementation GREEN (Phase 4) | 3 days | Agent implemented, tests passing |
| Implementation REFACTOR (Phase 4) | 0.5 day | Code cleanup, 0 ruff issues |
| Testing Strategy (Phase 5) | 0.5 day | Testing documentation |
| Deployment Plan (Phase 6) | 0.5 day | Deployment documentation |
| **TOTAL** | **7 days** | Fully functional agent |

---

## 12. Related Issues & Traceability

- **Parent**: FEATURE-SHELL-ANALYSIS-001 (ShellScriptAnalysisAgent)
- **Related**: REMEDIATION-SHELL-SCRIPTS-001 (Manual remediation plan)
- **Blocks**: Domain-specific remediation initiatives
- **References**:
  - `docs/scripts/analisis/REMEDIATION_PLAN.md`
  - `docs/scripts/analisis/SUMMARY.json`
  - `scripts/coding/ai/agents/quality/shell_analysis_agent.py`

---

## 13. Example Usage

### Example 1: Dry-Run Preview
```python
from scripts.coding.ai.agents.quality.shell_remediation_agent import ShellScriptRemediationAgent

agent = ShellScriptRemediationAgent(config={
    "dry_run": True,
    "analysis_path": "docs/scripts/analisis/SUMMARY.json"
})

result = agent.run({
    "domain": "infrastructure/vagrant"
})

print(f"Would fix {result['summary']['fixable_issues']} issues")
print(f"Manual review needed: {result['summary']['manual_review_count']}")
```

### Example 2: Remediate Single Domain
```python
agent = ShellScriptRemediationAgent(config={
    "dry_run": False,
    "backup_enabled": True,
    "validation_strict": True
})

result = agent.run({
    "domain": "infrastructure/vagrant",
    "severity": "CRITICAL"  # Only CRITICAL issues
})

print(f"Fixed {result['summary']['issues_fixed']} CRITICAL issues")
print(f"Score: {result['before']['score']} → {result['after']['score']}")
```

### Example 3: Full Project Remediation
```bash
# CLI usage
python -m scripts.cli.shell_remediation_agent \
    --analysis docs/scripts/analisis/SUMMARY.json \
    --strategy conservative \
    --parallel 10 \
    --backup \
    --output-dir docs/remediation_reports
```

---

## 14. Approval & Sign-Off

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | TBD | Pending | - |
| Tech Lead | TBD | Pending | - |
| AI Agent Developer | Claude | Proposed | 2025-11-13 |

---

**Trazabilidad**: FEATURE-SHELL-REMEDIATION-001
**Parent Issue**: FEATURE-SHELL-ANALYSIS-001
**Metodología**: SDLC + TDD + Auto-CoT + Self-Consistency + DDD
**Inspirado en**: ShellScriptAnalysisAgent pattern
**Estado**: PLANNING - Listo para Feasibility Phase

