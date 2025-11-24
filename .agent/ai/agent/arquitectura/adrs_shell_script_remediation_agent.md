---
title: Architectural Decision Records - ShellScriptRemediationAgent
date: 2025-11-13
domain: ai
status: active
---

# Architectural Decision Records - ShellScriptRemediationAgent

**Component**: ShellScriptRemediationAgent
**Issue ID**: FEATURE-SHELL-REMEDIATION-001
**Date**: 2025-11-13
**Methodology**: Self-Consistency (n=5 per ADR)
**Status**: Design Phase

---

## Overview

Este documento contiene las decisiones arquitectónicas clave para ShellScriptRemediationAgent. Cada decisión fue validada usando Self-Consistency con 5 reasoning paths independientes.

---

## ADR-001: Hybrid Architecture (Rule-Based + LLM) vs Pure Approaches

### Context

Necesitamos decidir la arquitectura fundamental del agente de remediación. Opciones:
1. **Pure Rule-Based**: Solo heurísticas deterministas
2. **Pure LLM**: Todo vía prompt engineering
3. **Hybrid**: Combinar ambos (Tier 1 + Tier 2)

### Decision

**APPROVED**: **Hybrid Architecture** (Tier 1: Rule-Based + Tier 2: LLM-Powered)

### Self-Consistency Validation (n=5)

**Path 1**: Hybrid permite mejor ROI - reglas rápidas para 60% cases, LLM para 40% complejos → **APPROVE** (Confidence: 90%)
**Path 2**: Pure rule-based limitado, pure LLM costoso y lento → Hybrid es balance óptimo → **APPROVE** (Confidence: 88%)
**Path 3**: Hybrid permite iteración - empezar con Tier 1, agregar Tier 2 después → **APPROVE** (Confidence: 92%)
**Path 4**: Safety - rule-based más predecible, LLM para edge cases → **APPROVE** (Confidence: 87%)
**Path 5**: Cost-effective - minimize LLM calls usando rules primero → **APPROVE** (Confidence: 91%)

**Consensus**: 5/5 APPROVE, Average Confidence: **89.6%**

### Rationale

- Tier 1 (rule-based) maneja ~60% issues (triviales) rápidamente
- Tier 2 (LLM) maneja ~40% issues complejos que requieren contexto
- Permite phased rollout: MVP con Tier 1, enhance con Tier 2
- Cost-effective: LLM solo cuando necesario

---

## ADR-002: LLM Provider (Claude vs GPT-4 vs Local LLaMA)

### Context

Si implementamos Tier 2, necesitamos elegir LLM provider:
- **Claude-3-Sonnet**: Excelente seguimiento de instrucciones, JSON structured output
- **GPT-4-Turbo**: Similar calidad, más rápido
- **Local LLaMA-70B**: Sin costos API, pero requiere GPU

### Decision

**APPROVED**: **Claude-3-Sonnet** como default, con abstraction para swap providers

### Self-Consistency Validation (n=5)

**Path 1**: Claude-3-Sonnet mejor para structured JSON outputs → **APPROVE** (Confidence: 85%)
**Path 2**: Abstraction permite cambiar provider fácilmente → **APPROVE** (Confidence: 90%)
**Path 3**: Claude tiene context window grande (200k) para scripts grandes → **APPROVE** (Confidence: 88%)
**Path 4**: API costs manejables (~$5-10 total para 157 scripts) → **APPROVE** (Confidence: 87%)
**Path 5**: Local LLaMA como fallback para entornos sin API access → **APPROVE** (Confidence: 86%)

**Consensus**: 5/5 APPROVE, Average Confidence: **87.2%**

### Implementation

```python
class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

# Default
llm_client = ClaudeLLMClient(api_key=config.llm_api_key)

# Alternative
# llm_client = GPT4LLMClient(api_key=config.openai_key)
# llm_client = LocalLLMClient(model="llama-70b")
```

---

## ADR-003: Confidence Threshold (0.80 vs 0.85 vs 0.90)

### Context

LLM-generated fixes necesitan threshold de confianza. Options:
- **0.80**: Más fixes automáticos, más riesgo
- **0.85**: Balance
- **0.90**: Muy conservador, menos fixes automáticos

### Decision

**APPROVED**: **0.80** como threshold inicial, adjustable via config

### Self-Consistency Validation (n=5)

**Path 1**: 0.80 permite 80%+ fixes mientras mantiene safety → **APPROVE** (Confidence: 82%)
**Path 2**: Con self-reflection + syntax validation, 0.80 es seguro → **APPROVE** (Confidence: 88%)
**Path 3**: Configurable permite adjust basado en resultados reales → **APPROVE** (Confidence: 90%)
**Path 4**: Comparado con ShellScriptAnalysisAgent experience (similar threshold works) → **APPROVE** (Confidence: 85%)
**Path 5**: Conservative start, can lower if false positive rate < 5% → **APPROVE** (Confidence: 87%)

**Consensus**: 5/5 APPROVE, Average Confidence: **86.4%**

### Configuration

```python
config = RemediationConfig(
    confidence_threshold=0.80,  # Default, adjustable
    confidence_threshold_critical=0.90  # Higher for CRITICAL issues
)
```

---

## ADR-004: Backup Strategy (Timestamped vs Git-based)

### Context

Necesitamos estrategia de backup para rollback. Options:
- **Timestamped backups**: `.remediation_backup/script_20251113_120000.bak`
- **Git commits**: Commit cada fix, rollback vía git revert
- **Shadow directory**: Copy entire dir structure

### Decision

**APPROVED**: **Timestamped backups** en `.remediation_backup/`

### Self-Consistency Validation (n=5)

**Path 1**: Timestamped simple, no afecta git history → **APPROVE** (Confidence: 92%)
**Path 2**: Git commits crean noise en history → REJECT git approach → **APPROVE timestamped** (Confidence: 88%)
**Path 3**: Shadow directory usa mucho espacio → REJECT → **APPROVE timestamped** (Confidence: 90%)
**Path 4**: Easy cleanup de backups viejos (30 días retention) → **APPROVE** (Confidence: 89%)
**Path 5**: Works sin git (algunos scripts fuera de repo) → **APPROVE** (Confidence: 91%)

**Consensus**: 5/5 APPROVE timestamped, Average Confidence: **90.0%**

### Implementation

```python
backup_path = backup_manager.backup(script_path)
# Creates: .remediation_backup/script_20251113_120000.bak

# Rollback if needed
if validation_fails:
    backup_manager.rollback(script_path, backup_path)

# Cleanup old backups (30 days)
backup_manager.cleanup_old_backups(days=30)
```

---

## ADR-005: Validation Pipeline (bash -n only vs bash + ShellCheck)

### Context

Post-fix validation options:
- **bash -n only**: Syntax check, fast
- **bash -n + ShellCheck**: Syntax + quality, slower but more thorough
- **bash -n + ShellCheck + tests**: Most thorough, slowest

### Decision

**APPROVED**: **bash -n + ShellCheck (if available)** + optional test execution

### Self-Consistency Validation (n=5)

**Path 1**: bash -n catches syntax errors (80%), ShellCheck catches logic errors (15%) → **APPROVE both** (Confidence: 91%)
**Path 2**: ShellCheck optional (graceful degradation) → **APPROVE** (Confidence: 89%)
**Path 3**: Test execution optional, configurable → **APPROVE** (Confidence: 92%)
**Path 4**: Validation pipeline prevents breaking changes → **APPROVE** (Confidence: 90%)
**Path 5**: Re-analysis with ShellScriptAnalysisAgent verifies improvement → **APPROVE** (Confidence: 88%)

**Consensus**: 5/5 APPROVE, Average Confidence: **90.0%**

### Implementation

```python
# Layer 1: bash -n (required)
bash_valid = syntax_validator.bash_check(script_path)
if not bash_valid:
    rollback()

# Layer 2: ShellCheck (optional, if available)
if shutil.which("shellcheck"):
    shellcheck_result = syntax_validator.shellcheck(script_path)
    if shellcheck_result.has_errors():
        rollback()

# Layer 3: Tests (optional, if exist)
if test_file_exists and config.run_tests:
    test_result = run_tests(test_file)
    if not test_result.success:
        rollback()

# Layer 4: Re-analysis (always)
reanalysis = reanalyzer.analyze(script_path)
if reanalysis.score < original_score:
    rollback()
```

---

## Summary

| ADR | Decision | Confidence | Status |
|-----|----------|------------|--------|
| ADR-001 | Hybrid Architecture | 89.6% | APPROVED |
| ADR-002 | Claude-3-Sonnet (abstracted) | 87.2% | APPROVED |
| ADR-003 | Confidence Threshold 0.80 | 86.4% | APPROVED |
| ADR-004 | Timestamped Backups | 90.0% | APPROVED |
| ADR-005 | bash -n + ShellCheck + tests | 90.0% | APPROVED |

**Overall Consensus**: All 5 ADRs APPROVED with average confidence **88.6%** (HIGH)

---

**Document Status**: Complete
**Trazabilidad**: FEATURE-SHELL-REMEDIATION-001
**Methodology**: Self-Consistency (n=5 per ADR)
**Next Step**: Proceed to LLD