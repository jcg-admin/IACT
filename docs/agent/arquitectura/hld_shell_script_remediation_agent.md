# High-Level Design - ShellScriptRemediationAgent

**Component**: ShellScriptRemediationAgent
**Issue ID**: FEATURE-SHELL-REMEDIATION-001
**Date**: 2025-11-13
**Status**: Design Phase
**Architecture**: Hybrid (Rule-Based + LLM-Powered)

---

## 1. Overview

ShellScriptRemediationAgent es un agente híbrido que automatiza la remediación de violations en shell scripts, combinando fixes deterministas (rule-based) con fixes inteligentes (LLM-powered con prompt engineering).

**Innovation**: Primer agente en el proyecto que combina rule-based heuristics con LLM reasoning para auto-remediation.

---

## 2. System Architecture

### 2.1 High-Level Component Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      ShellScriptRemediationAgent                             │
│                                                                              │
│  ┌────────────────────┐         ┌──────────────────────┐                  │
│  │  Input Parser      │────────▶│  Issue Classifier    │                  │
│  │  (JSON Loader)     │         │  (Tier 1 vs Tier 2)  │                  │
│  └────────────────────┘         └──────────────────────┘                  │
│            │                              │                                │
│            │                              ▼                                │
│            │              ┌───────────────────────────────┐              │
│            │              │   Strategy Selector           │              │
│            │              │   (Rule-based vs LLM)         │              │
│            │              └───────────────────────────────┘              │
│            │                      │              │                        │
│            │         ┌────────────┘              └─────────────┐         │
│            │         ▼                                         ▼          │
│            │  ┌──────────────────────┐       ┌──────────────────────┐  │
│            │  │  TIER 1              │       │  TIER 2              │  │
│            │  │  Rule-Based Fixer    │       │  LLM-Powered Fixer   │  │
│            │  │  - Quote variables   │       │  - Context detection │  │
│            │  │  - Add set -e        │       │  - CoT reasoning     │  │
│            │  │  - Simple patterns   │       │  - Few-shot learning │  │
│            │  └──────────────────────┘       │  - Self-reflection   │  │
│            │           │                      └──────────────────────┘  │
│            │           │                                 │               │
│            │           └─────────────┬───────────────────┘               │
│            │                         ▼                                   │
│            │              ┌──────────────────────┐                      │
│            │              │  Backup Manager      │                      │
│            │              │  (.remediation_bk/)  │                      │
│            │              └──────────────────────┘                      │
│            │                         │                                   │
│            │                         ▼                                   │
│            │              ┌──────────────────────┐                      │
│            │              │  Apply Fixes         │                      │
│            │              │  (File Writer)       │                      │
│            │              └──────────────────────┘                      │
│            │                         │                                   │
│            │                         ▼                                   │
│            │              ┌──────────────────────┐                      │
│            │              │  Syntax Validator    │                      │
│            │              │  (bash -n, ShellCheck)│                     │
│            │              └──────────────────────┘                      │
│            │                         │                                   │
│            │                   PASS  │  FAIL                            │
│            │                    ┌────┴────┐                             │
│            │                    ▼         ▼                              │
│            │          ┌──────────────┐  ┌──────────────┐              │
│            │          │  Re-Analyzer  │  │  Rollback    │              │
│            │          │  (Score check)│  │  (Restore)   │              │
│            │          └──────────────┘  └──────────────┘              │
│            │                 │                                           │
│            │                 ▼                                           │
│            │          ┌──────────────────┐                             │
│            └─────────▶│  Report Generator│                             │
│                       │  (MD + JSON)     │                             │
│                       └──────────────────┘                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Analysis Results (JSON)
        │
        ▼
[Input Parser] ──▶ IssueList
        │
        ▼
[Issue Classifier] ──▶ {Tier1: [...], Tier2: [...]}
        │
        ▼
[Strategy Selector] ──▶ Strategy (RULE_BASED | LLM_COT | HYBRID)
        │
        ├─▶ [Tier 1: Rule-Based Fixer] ──▶ SimpleFix
        │           │
        │           ▼
        └─▶ [Tier 2: LLM-Powered Fixer] ──▶ ComplexFix
                    │
                    ▼
              [Backup Manager] ──▶ Creates backup
                    │
                    ▼
              [Apply Fixes] ──▶ Modified script
                    │
                    ▼
              [Syntax Validator] ──▶ Valid? (Y/N)
                    │
              ┌─────┴─────┐
              ▼           ▼
            PASS        FAIL
              │           │
              ▼           ▼
        [Re-Analyzer]  [Rollback]
              │           │
              ▼           ▼
        [Report]      [Manual Review Queue]
```

---

## 3. Core Components

### 3.1 Input Parser

**Responsibility**: Leer y parsear análisis JSON de ShellScriptAnalysisAgent

**Input**: `docs/scripts/analisis/SUMMARY.json`
**Output**: List[ScriptIssues]

```python
@dataclass
class ScriptIssues:
    script_path: Path
    domain: str
    issues: List[Issue]
    current_score: float

@dataclass
class Issue:
    line: int
    type: str  # "constitutional" | "security" | "quality"
    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    rule: str  # "missing_set_e", "unquoted_variable", etc.
    message: str
    context: str  # Surrounding code
```

### 3.2 Issue Classifier

**Responsibility**: Clasificar issues en Tier 1 (rule-based) vs Tier 2 (LLM-powered)

**Logic**:
```python
def classify_issue(issue: Issue, script_complexity: int) -> str:
    # Tier 1: Simple, deterministic patterns
    TIER1_RULES = [
        "unquoted_variable_simple",  # $VAR without complex context
        "missing_set_e",  # Add set -euo pipefail
        "basic_or_true"  # || true at end of line
    ]

    if issue.rule in TIER1_RULES and script_complexity < 100:
        return "TIER1"

    # Tier 2: Complex, context-dependent
    TIER2_RULES = [
        "unquoted_variable_array",  # Arrays, special vars
        "context_dependent_or_true",  # || true with complex logic
        "domain_specific_pattern"  # Needs domain understanding
    ]

    if issue.rule in TIER2_RULES or script_complexity >= 100:
        return "TIER2"

    # Default: Tier 1 with LLM validation (Hybrid)
    return "HYBRID"
```

### 3.3 Tier 1: Rule-Based Fixer

**Responsibility**: Aplicar fixes deterministas para patterns simples

**Supported Fixes**:
1. **Quote unquoted variables**
   ```python
   Pattern: r'\$(\w+)'
   Fix: r'"$\1"'
   ```

2. **Add set -euo pipefail**
   ```python
   Pattern: r'^#!/bin/bash\n'
   Fix: '#!/bin/bash\nset -euo pipefail\n'
   ```

3. **Remove unnecessary || true**
   ```python
   Pattern: r'(mkdir|rm|touch) .* \|\| true$'
   Fix: '# Removed unnecessary || true\n\1 ...'
   ```

**Code Structure**:
```python
class RuleBasedFixer:
    def __init__(self):
        self.rules = [
            QuoteVariablesRule(),
            AddSetERule(),
            RemoveOrTrueRule()
        ]

    def fix(self, script_content: str, issues: List[Issue]) -> FixResult:
        fixes_applied = []
        modified_content = script_content

        for issue in issues:
            for rule in self.rules:
                if rule.matches(issue):
                    modified_content = rule.apply(modified_content, issue)
                    fixes_applied.append(issue)
                    break

        return FixResult(
            content=modified_content,
            fixes_applied=fixes_applied,
            confidence=0.99  # High confidence for rule-based
        )
```

### 3.4 Tier 2: LLM-Powered Fixer

**Responsibility**: Aplicar fixes inteligentes usando LLM + prompts

**Components**:
1. **Context Detector**: Identifica dominio y propósito del script
2. **CoT Reasoner**: Genera fix usando Chain-of-Thought
3. **Self-Reflector**: Valida el fix propuesto
4. **Constitutional Checker**: Verifica compliance

**Code Structure**:
```python
class LLMPoweredFixer:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.context_detector = ContextDetector(llm_client)
        self.cot_reasoner = CoTReasoner(llm_client)
        self.self_reflector = SelfReflector(llm_client)

    def fix(self, script_content: str, issues: List[Issue],
            script_path: Path) -> FixResult:
        # 1. Detect context
        context = self.context_detector.detect(script_path, script_content)

        # 2. Generate fixes using CoT
        proposed_fixes = self.cot_reasoner.reason(
            script_content, issues, context
        )

        # 3. Self-reflect on each fix
        validated_fixes = []
        for fix in proposed_fixes:
            validation = self.self_reflector.validate(fix, context)
            if validation.confidence >= 0.80:
                validated_fixes.append(fix)

        # 4. Apply validated fixes
        modified_content = self._apply_fixes(script_content, validated_fixes)

        return FixResult(
            content=modified_content,
            fixes_applied=validated_fixes,
            confidence=mean([f.confidence for f in validated_fixes])
        )

class ContextDetector:
    def detect(self, script_path: Path, content: str) -> ScriptContext:
        prompt = CONTEXT_DETECTION_PROMPT.format(
            script_path=script_path,
            script_content=content
        )
        response = self.llm.generate(prompt, response_format="json")
        return ScriptContext.from_json(response)

class CoTReasoner:
    def reason(self, content: str, issues: List[Issue],
               context: ScriptContext) -> List[ProposedFix]:
        prompt = COT_REMEDIATION_PROMPT.format(
            script_content=content,
            violations_json=json.dumps([i.to_dict() for i in issues]),
            domain=context.domain,
            purpose=context.purpose,
            risk_level=context.risk_level
        )
        # Add few-shot examples
        prompt += FEW_SHOT_EXAMPLES

        response = self.llm.generate(prompt, response_format="json")
        return [ProposedFix.from_json(f) for f in response["fixes"]]
```

### 3.5 Backup Manager

**Responsibility**: Crear backups y gestionar rollback

```python
class BackupManager:
    def __init__(self, backup_dir: Path = Path(".remediation_backup")):
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(exist_ok=True)

    def backup(self, script_path: Path) -> Path:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{script_path.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(script_path, backup_path)
        return backup_path

    def rollback(self, script_path: Path, backup_path: Path):
        """Restore from backup"""
        shutil.copy2(backup_path, script_path)

    def cleanup_old_backups(self, days: int = 30):
        """Remove backups older than N days"""
        cutoff = datetime.now() - timedelta(days=days)
        for backup in self.backup_dir.glob("*.bak"):
            if datetime.fromtimestamp(backup.stat().st_mtime) < cutoff:
                backup.unlink()
```

### 3.6 Syntax Validator

**Responsibility**: Validar sintaxis de scripts modificados

```python
class SyntaxValidator:
    def validate(self, script_path: Path) -> ValidationResult:
        # 1. bash -n (syntax check)
        bash_check = self._run_bash_n(script_path)

        # 2. ShellCheck (if available)
        shellcheck_result = self._run_shellcheck(script_path)

        return ValidationResult(
            valid=bash_check.success and shellcheck_result.success,
            bash_errors=bash_check.errors,
            shellcheck_issues=shellcheck_result.issues
        )

    def _run_bash_n(self, script_path: Path) -> BashCheckResult:
        result = subprocess.run(
            ["bash", "-n", str(script_path)],
            capture_output=True,
            text=True
        )
        return BashCheckResult(
            success=(result.returncode == 0),
            errors=result.stderr if result.returncode != 0 else None
        )
```

### 3.7 Re-Analyzer

**Responsibility**: Re-analizar script con ShellScriptAnalysisAgent post-remediation

```python
class ReAnalyzer:
    def __init__(self):
        self.analysis_agent = ShellScriptAnalysisAgent()

    def reanalyze(self, script_path: Path) -> ReAnalysisResult:
        result = self.analysis_agent.execute({
            "script_path": str(script_path),
            "output_dir": "/tmp/reanalysis"
        })

        return ReAnalysisResult(
            new_score=result.data["score"],
            remaining_issues=result.data["issues"],
            improvement=result.data["score"] - self.original_score
        )
```

### 3.8 Report Generator

**Responsibility**: Generar reports de remediación (MD + JSON)

```python
class RemediationReportGenerator:
    def generate(self, remediation_result: RemediationResult,
                 output_dir: Path):
        # Generate Markdown report
        md_report = self._generate_markdown(remediation_result)
        (output_dir / "remediation_report.md").write_text(md_report)

        # Generate JSON report
        json_report = self._generate_json(remediation_result)
        (output_dir / "remediation_report.json").write_text(
            json.dumps(json_report, indent=2)
        )

    def _generate_markdown(self, result: RemediationResult) -> str:
        return f"""# Remediation Report

## Summary

- **Scripts Processed**: {result.scripts_processed}
- **Issues Fixed**: {result.issues_fixed} / {result.total_issues}
- **Success Rate**: {result.success_rate:.1f}%
- **Score Improvement**: {result.score_before:.1f} → {result.score_after:.1f}

## Fixes Applied

{self._format_fixes(result.fixes_applied)}

## Manual Review Queue

{self._format_manual_review(result.manual_review_queue)}
"""
```

---

## 4. Workflow

### 4.1 Complete Remediation Flow

```
1. Load analysis results from ShellScriptAnalysisAgent
   ↓
2. FOR EACH script with issues:
   ↓
   2.1. Classify issues (Tier 1 vs Tier 2)
   ↓
   2.2. Select strategy (RULE_BASED | LLM_COT | HYBRID)
   ↓
   2.3. Create backup
   ↓
   2.4. Apply fixes (Tier 1 or Tier 2)
   ↓
   2.5. Syntax validation
   ↓         PASS │ FAIL
   ├──────────────┴──────────┐
   ↓                          ↓
   2.6. Re-analyze         Rollback from backup
   ↓                          ↓
   2.7. Verify improvement   Log failure
   ↓                          ↓
   2.8. Generate report      Add to manual review
   ↓
3. Generate consolidated report
   ↓
4. Cleanup old backups
```

### 4.2 Error Handling Flow

```
Error occurs during fix
   ↓
Is backup available?
   ├─ YES ──▶ Rollback to backup
   │          ↓
   │          Log error details
   │          ↓
   │          Add to manual review queue
   │          ↓
   │          Continue with next script
   │
   └─ NO ──▶ Log CRITICAL error
              ↓
              Stop processing (fail fast)
```

---

## 5. Configuration

### 5.1 Agent Configuration

```python
@dataclass
class RemediationConfig:
    # Input/Output
    analysis_path: Path
    output_dir: Path

    # Strategy
    strategy: str = "HYBRID"  # RULE_BASED | LLM_COT | HYBRID
    confidence_threshold: float = 0.80

    # LLM Settings
    llm_provider: str = "claude"  # claude | gpt4 | local
    llm_model: str = "claude-3-sonnet"
    llm_api_key: Optional[str] = None
    llm_max_retries: int = 3

    # Safety
    dry_run: bool = False
    backup_enabled: bool = True
    validation_strict: bool = True

    # Filters
    domain_filter: Optional[str] = None  # "infrastructure/vagrant"
    severity_filter: Optional[str] = None  # "CRITICAL"
    issue_type_filter: Optional[str] = None  # "constitutional"

    # Performance
    parallel_workers: int = 5  # Lower than analysis (more expensive)
    cache_enabled: bool = True
```

### 5.2 LLM Provider Abstraction

```python
class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class ClaudeLLMClient(LLMClient):
    def generate(self, prompt: str, response_format: str = "text") -> str:
        # Call Claude API
        pass

class GPT4LLMClient(LLMClient):
    def generate(self, prompt: str, response_format: str = "text") -> str:
        # Call OpenAI API
        pass

class LocalLLMClient(LLMClient):
    def generate(self, prompt: str, response_format: str = "text") -> str:
        # Call local LLaMA/Mistral
        pass
```

---

## 6. Performance Considerations

### 6.1 Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Tier 1 (rule-based) fix | <0.1s per issue | Fast, deterministic |
| Tier 2 (LLM) fix | 2-5s per issue | Depends on LLM API latency |
| Syntax validation | <0.5s per script | bash -n is fast |
| Re-analysis | <2s per script | Uses ShellScriptAnalysisAgent |
| **Total (157 scripts, 503 issues)** | **~2-4 hours** | With 5 parallel workers |

### 6.2 Optimization Strategies

1. **Batch Tier 1 fixes**: Process all rule-based fixes first (fast)
2. **Parallel Tier 2**: Run LLM calls in parallel (5 workers)
3. **Caching**: Cache LLM responses for identical issues
4. **Progressive rollout**: Start with low-risk domains first

---

## 7. Safety Mechanisms

### 7.1 Multi-Layer Validation

```
Layer 1: Rule confidence check (0.99 for rules, 0.80+ for LLM)
   ↓
Layer 2: Syntax validation (bash -n)
   ↓
Layer 3: ShellCheck validation (if available)
   ↓
Layer 4: Re-analysis score improvement check
   ↓
Layer 5: Test execution (if tests exist)
```

### 7.2 Rollback Triggers

- Syntax validation fails
- Re-analysis score decreases
- Test execution fails
- Manual abort signal

---

## 8. Integration Points

### 8.1 With ShellScriptAnalysisAgent

**Input**: Reads `SUMMARY.json` generated by analysis agent
**Output**: Generates `remediation_report.json` in same format
**Validation**: Re-runs analysis agent to verify improvements

### 8.2 With CI/CD

**Pre-commit hook**:
```bash
# Analyze + Remediate in one go
python -m scripts.cli.shell_analysis_agent .
python -m scripts.cli.shell_remediation_agent \
    --analysis docs/scripts/analisis/SUMMARY.json \
    --dry-run  # Preview only
```

**CI Pipeline**:
```yaml
remediation:
  stage: quality
  script:
    - python -m scripts.cli.shell_remediation_agent \
        --analysis docs/scripts/analisis/SUMMARY.json \
        --domain infrastructure/vagrant \
        --strategy HYBRID
  allow_failure: true  # Non-blocking initially
```

---

## 9. Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Auto-fix Rate | 0% (manual) | 80%+ | Issues fixed / Total issues |
| Score Improvement | 91.9/100 | 98.0+/100 | Re-analysis average |
| CRITICAL Issues | 21 | 0 | Severity count |
| Breaking Changes | N/A | 0 | Test failures |
| Remediation Time | 20 days | <4 hours | Wall clock |
| LLM Accuracy | N/A | 85%+ | Validated fixes / Total LLM fixes |

---

## 10. Next Steps

Phase 3 Design is complete. Next:
1. ✓ HLD Complete → Proceed to ADRs
2. Document key architectural decisions
3. Create LLD with implementation details
4. Begin Phase 4: Implementation (TDD)

---

**Document Status**: Complete
**Architecture**: Hybrid (Rule-Based + LLM-Powered)
**Complexity**: HIGH (LLM integration)
**Trazabilidad**: FEATURE-SHELL-REMEDIATION-001
**Methodology**: Auto-CoT + Self-Consistency
