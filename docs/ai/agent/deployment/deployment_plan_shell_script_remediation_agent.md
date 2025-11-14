---
title: Deployment Plan - ShellScriptRemediationAgent
date: 2025-11-13
domain: ai
status: active
---

# Deployment Plan - ShellScriptRemediationAgent

**Component**: ShellScriptRemediationAgent
**Issue ID**: FEATURE-SHELL-REMEDIATION-001
**Date**: 2025-11-13
**Status**: Ready for Deployment
**Implementation**: Tier 1 (Rule-Based MVP)

---

## 1. Overview

Este documento describe el plan de despliegue completo para ShellScriptRemediationAgent Tier 1 (Rule-Based MVP).

**Deployment Scope**:
- Tier 1: Rule-based fixes (4 fix rules)
- Auto-backup and rollback
- Syntax validation (bash -n + ShellCheck)
- Dry-run mode

**Coverage**: ~60% of 503 issues (simple patterns)

---

## 2. Pre-Deployment Checklist

### 2.1 Code Verification

- [x] Implementation complete: 576 lines
- [x] All tests passing: 39/39 (100%)
- [x] Code quality: 0 ruff issues
- [x] Documentation complete: HLD, ADRs, LLD, Testing, Deployment

### 2.2 Dependencies

**Required**:
- Python 3.11+
- bash (for validation)
- scripts.coding.ai.shared.agent_base

**Optional**:
- ShellCheck (for enhanced validation)

**Installation**:
```bash
# ShellCheck (optional but recommended)
sudo apt-get install shellcheck  # Ubuntu/Debian
brew install shellcheck          # macOS
```

### 2.3 Testing Verification

```bash
# Run full test suite
python -m pytest scripts/coding/tests/ai/agents/quality/test_shell_remediation_agent.py -v

# Expected output:
# 39 passed in 0.27s
```

---

## 3. Configuration

### 3.1 Agent Configuration Options

```python
config = {
    # Execution Mode
    "dry_run": False,              # If True, preview fixes without applying

    # Safety Features
    "backup_enabled": True,        # Enable automatic backups

    # Future Options (Tier 2)
    # "llm_provider": "claude-3-sonnet",
    # "confidence_threshold": 0.80,
}
```

### 3.2 Configuration Profiles

**Production Profile** (Recommended):
```python
config = {
    "dry_run": False,
    "backup_enabled": True,
}
```

**Safe Testing Profile**:
```python
config = {
    "dry_run": True,
    "backup_enabled": True,
}
```

**Aggressive Profile** (Not Recommended):
```python
config = {
    "dry_run": False,
    "backup_enabled": False,  # Only if you have external backups
}
```

---

## 4. Deployment Steps

### 4.1 Phase 1: Dry-Run Testing (1 day)

**Objective**: Validate fixes without modifying files

**Steps**:
1. Run agent with `dry_run: True` on sample scripts
2. Review generated fix reports
3. Verify fix correctness manually
4. Check for edge cases

**Command**:
```python
from scripts.coding.ai.agents.quality.shell_remediation_agent import ShellScriptRemediationAgent
from pathlib import Path

agent = ShellScriptRemediationAgent(config={"dry_run": True})

# Test on single script
result = agent._remediate_script(script_issues)
print(f"Fixes proposed: {len(result.fixes_applied)}")
```

**Success Criteria**:
- Fixes are correct
- No false positives
- Edge cases handled

### 4.2 Phase 2: Pilot Rollout (2 days)

**Objective**: Apply fixes to low-risk domain

**Target Domain**: `scripts/examples` (lowest risk)

**Steps**:
1. Enable backup and apply fixes
2. Verify all scripts pass bash -n validation
3. Run any existing tests
4. Manual spot-check of 100% scripts

**Command**:
```python
agent = ShellScriptRemediationAgent(config={
    "dry_run": False,
    "backup_enabled": True
})

# Load analysis results for scripts/examples
analysis_path = Path("docs/scripts/analisis/analysis_results.json")
result = agent.run({
    "analysis_path": analysis_path,
    "output_dir": "remediation_reports"
})

print(f"Scripts remediated: {result['summary']['scripts_processed']}")
print(f"Fixes applied: {result['summary']['fixes_applied']}")
print(f"Validation passed: {result['summary']['validation_passed']}")
```

**Success Criteria**:
- All scripts pass validation
- No test failures
- Backup/rollback works as expected

### 4.3 Phase 3: Gradual Rollout (3 days)

**Objective**: Apply fixes to all domains in risk order

**Rollout Order**:
1. LOW risk: `scripts/examples`, `scripts/validation`
2. MEDIUM risk: `scripts/ci`, `scripts/utils`
3. HIGH risk: `infrastructure/vagrant`, `cpython`

**Per-Domain Process**:
```bash
# 1. Backup current state (git)
git add .
git commit -m "Pre-remediation snapshot for {domain}"

# 2. Run remediation
python -c "
from scripts.coding.ai.agents.quality.shell_remediation_agent import ShellScriptRemediationAgent
agent = ShellScriptRemediationAgent(config={'dry_run': False})
# Filter for specific domain
"

# 3. Verify changes
git diff

# 4. Run tests
pytest tests/related_to_domain

# 5. Commit or rollback
git add . && git commit -m "Remediate {domain} scripts"
# OR
git reset --hard HEAD  # If issues found
```

**Success Criteria per Domain**:
- All domain scripts pass validation
- Domain-specific tests pass
- Manual review approves changes

### 4.4 Phase 4: Full Production (1 day)

**Objective**: Complete remediation of all 157 scripts

**Command**:
```bash
# Run full remediation
python scripts/cli/shell_remediation_cli.py \
    --analysis-path docs/scripts/analisis/analysis_results.json \
    --output-dir remediation_reports \
    --backup-enabled
```

**Post-Remediation Verification**:
```bash
# 1. Re-analyze all scripts
python -m scripts.coding.ai.agents.quality.shell_analysis_agent

# 2. Verify score improvement
# Expected: 91.9 → 95.0+ (Tier 1 only)

# 3. Run full test suite
pytest scripts/coding/tests/

# 4. Commit changes
git add .
git commit -m "feat(quality): remediate 157 shell scripts with ShellScriptRemediationAgent Tier 1"
```

---

## 5. Usage Examples

### 5.1 Basic Usage

```python
from scripts.coding.ai.agents.quality.shell_remediation_agent import (
    ShellScriptRemediationAgent,
    ScriptIssues,
    Issue
)
from pathlib import Path

# Initialize agent
agent = ShellScriptRemediationAgent(config={
    "dry_run": False,
    "backup_enabled": True
})

# Create script issues
script_issues = ScriptIssues(
    script_path=Path("scripts/example.sh"),
    domain="examples",
    issues=[
        Issue(
            line=1,
            type="constitutional",
            severity="CRITICAL",
            rule="missing_set_e",
            message="Missing set -e",
            context="#!/bin/bash"
        )
    ],
    current_score=85.0
)

# Remediate
result = agent._remediate_script(script_issues)

print(f"Fixes applied: {len(result.fixes_applied)}")
print(f"Validation passed: {result.validation_passed}")
```

### 5.2 Dry-Run Mode

```python
# Preview fixes without applying
agent = ShellScriptRemediationAgent(config={"dry_run": True})
result = agent._remediate_script(script_issues)

# File remains unchanged, but result shows proposed fixes
for fix in result.fixes_applied:
    print(f"Would fix: {fix.issue.rule} at line {fix.issue.line}")
    print(f"Confidence: {fix.confidence}")
```

### 5.3 Manual Rollback

```python
from scripts.coding.ai.agents.quality.shell_remediation_agent import BackupManager
from pathlib import Path

# If automatic rollback failed, manual rollback:
backup_manager = BackupManager()
script_path = Path("scripts/example.sh")
backup_path = Path(".remediation_backup/example_20251113_103045.bak")

backup_manager.rollback(script_path, backup_path)
print(f"Rolled back {script_path}")
```

---

## 6. Integration Points

### 6.1 Input: ShellScriptAnalysisAgent

**Data Flow**:
```
ShellScriptAnalysisAgent
  → analysis_results.json
  → ShellScriptRemediationAgent
  → remediation_reports/
```

**Analysis JSON Format** (Expected):
```json
{
  "scripts": [
    {
      "script_path": "scripts/example.sh",
      "domain": "examples",
      "issues": [
        {
          "line": 1,
          "type": "constitutional",
          "severity": "CRITICAL",
          "rule": "missing_set_e",
          "message": "Missing set -e",
          "context": "#!/bin/bash"
        }
      ],
      "current_score": 85.0
    }
  ]
}
```

### 6.2 Output: Remediation Reports

**Output Format**:
```json
{
  "status": "success",
  "summary": {
    "scripts_processed": 157,
    "fixes_applied": 312,
    "validation_passed": 157
  },
  "results": [
    {
      "script_path": "scripts/example.sh",
      "original_score": 85.0,
      "new_score": 95.0,
      "fixes_applied": [...],
      "validation_passed": true,
      "remediation_time": 0.15
    }
  ]
}
```

### 6.3 Validation: Re-Analysis

After remediation, re-run ShellScriptAnalysisAgent:
```python
from scripts.coding.ai.agents.quality.shell_analysis_agent import ShellScriptAnalysisAgent

analyzer = ShellScriptAnalysisAgent()
new_results = analyzer.execute({
    "script_path": ".",
    "output_dir": "docs/scripts/analisis_post_remediation"
})

print(f"New score: {new_results.data['summary']['average_score']}")
```

---

## 7. Monitoring and Observability

### 7.1 Success Metrics

| Metric | Target | Actual (Post-Deploy) |
|--------|--------|----------------------|
| Scripts Remediated | 157 | _TBD_ |
| Fixes Applied | 300+ | _TBD_ |
| Validation Pass Rate | 100% | _TBD_ |
| Score Improvement | 91.9 → 95.0+ | _TBD_ |
| CRITICAL Issues Resolved | 21 → <5 | _TBD_ |
| HIGH Security Issues | 387 → <100 | _TBD_ |

### 7.2 Logging

Agent logs to stdout:
```
[2025-11-13 10:45:48] ShellScriptRemediationAgent - INFO - Starting remediation...
[2025-11-13 10:45:48] ShellScriptRemediationAgent - INFO - Processing scripts/example.sh
[2025-11-13 10:45:48] ShellScriptRemediationAgent - INFO - Applied 2 fixes
[2025-11-13 10:45:48] ShellScriptRemediationAgent - INFO - Validation passed
```

### 7.3 Error Handling

**Automatic Rollback Triggers**:
- Syntax validation failure (bash -n)
- ShellCheck error level issues (if enabled)

**Manual Intervention Required**:
- Repeated validation failures
- Domain-specific test failures

---

## 8. Rollback Plan

### 8.1 Automatic Rollback

Built into agent - triggers on validation failure:
```python
if not validation.valid:
    # Automatic rollback
    if backup_path:
        self.backup_manager.rollback(script_path, backup_path)
```

### 8.2 Manual Rollback (Single Script)

```bash
# Find backup
ls .remediation_backup/example_*.bak

# Restore manually
cp .remediation_backup/example_20251113_103045.bak scripts/example.sh
```

### 8.3 Full Rollback (Git)

```bash
# If remediation introduced issues
git log --oneline  # Find pre-remediation commit
git reset --hard <commit-hash>
```

---

## 9. Post-Deployment Validation

### 9.1 Immediate Checks (Within 1 hour)

- [ ] All 157 scripts exist
- [ ] All scripts pass bash -n
- [ ] No git merge conflicts
- [ ] Backups created successfully

### 9.2 Short-term Validation (Within 1 day)

- [ ] Re-analysis shows score improvement
- [ ] CRITICAL issues reduced
- [ ] HIGH security issues reduced
- [ ] All tests passing

### 9.3 Long-term Monitoring (1 week)

- [ ] No production incidents related to scripts
- [ ] No rollback requests
- [ ] Team feedback positive

---

## 10. Known Limitations (Tier 1)

### 10.1 Coverage Limitations

**Fixed by Tier 1** (~60%):
- ✓ Missing `set -euo pipefail`
- ✓ Unquoted variables (simple patterns)
- ✓ `|| true` patterns (basic)
- ✓ Unnecessary `|| true` for idempotent commands

**NOT Fixed by Tier 1** (~40%, requires Tier 2 LLM):
- Complex control flow error handling
- Domain-specific logic
- Multi-line command quoting
- Advanced pattern matching

### 10.2 Edge Cases

**Manual Review Required**:
- Scripts with complex heredocs
- Scripts with intentional `set +e` blocks
- Scripts with embedded Python/Ruby/etc.

---

## 11. Future Enhancements (Tier 2)

**Tier 2 Deployment** (Future):
- LLM-powered fixes for complex patterns
- Context-aware remediation
- Self-reflection validation
- Adaptive strategy selection

**Expected Additional Coverage**: +35% (total 95%)

---

## 12. Support and Maintenance

### 12.1 Common Issues

**Issue**: Validation fails after remediation
**Solution**: Check backup and rollback, investigate specific fix

**Issue**: Fix introduces breaking change
**Solution**: Automatic rollback triggered, manual review needed

**Issue**: ShellCheck not available
**Solution**: Falls back to bash -n only (graceful degradation)

### 12.2 Adding New Fix Rules

To extend Tier 1 with new rules:
1. Create new `FixRule` subclass
2. Implement `matches()`, `apply()`, `get_confidence()`
3. Add to `RuleBasedFixer.__init__()`
4. Write tests (TDD)
5. Update documentation

---

## 13. Summary

**Deployment Readiness**: ✓ READY

**Implementation Status**:
- Planning: ✓ Complete
- Feasibility: ✓ Approved (87.4% confidence)
- Design: ✓ Complete (HLD, ADRs, LLD)
- Implementation: ✓ Complete (576 lines, 39/39 tests)
- Testing: ✓ Complete (100% pass rate)
- Deployment: ✓ Documented

**Recommended Rollout**:
1. Dry-run testing (1 day)
2. Pilot (LOW risk domains) (2 days)
3. Gradual rollout (MEDIUM/HIGH risk) (3 days)
4. Full production (1 day)
**Total**: 7 days

**Expected Impact**:
- 503 issues → ~312 fixed (Tier 1)
- Score: 91.9 → 95.0+
- CRITICAL: 21 → <5
- Time saved: 19.8 days (vs manual)

---

**Document Status**: Complete
**Deployment Status**: Ready for Phase 1 (Dry-Run)
**Trazabilidad**: FEATURE-SHELL-REMEDIATION-001
**Approval**: Pending rollout initiation
