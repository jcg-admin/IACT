---
title: High-Level Design: ShellScriptAnalysisAgent
date: 2025-11-13
domain: ai
status: active
---

# High-Level Design: ShellScriptAnalysisAgent

**Issue ID**: FEATURE-SHELL-ANALYSIS-001
**Fecha**: 2025-11-13
**Fase SDLC**: Design (HLD)
**Autor**: Claude (SDLCDesignAgent)
**Versión**: 1.0.0

---

## 1. Executive Summary

El **ShellScriptAnalysisAgent** es un agente AI especializado que analiza scripts shell del proyecto IACT (253 scripts) y genera reportes exhaustivos de calidad, compliance constitucional y recomendaciones de refactoring.

**Arquitectura**: Basada en Agent framework existente (`scripts/coding/ai/shared/agent_base.py`)

**Técnicas de Prompting**:
- Chain-of-Verification (análisis constitucional)
- Auto-CoT (razonamiento sobre complejidad)
- Search Optimization (detección de code smells)

**Estrategia de Implementación**: 3 fases (MVP heuristics → LLM integration → Optimizations)

---

## 2. System Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    ShellScriptAnalysisAgent                     │
│                   (Main Orchestrator Component)                 │
│                                                                 │
│  Responsibilities:                                              │
│  - Orchestrate analysis pipeline                               │
│  - Coordinate sub-analyzers                                    │
│  - Consolidate results                                         │
│  - Generate reports                                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             │ Uses
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Base Class                           │
│               (scripts/coding/ai/shared/agent_base.py)          │
│                                                                 │
│  Provides:                                                      │
│  - Constitution loading                                         │
│  - Guardrails (no emojis, traceability)                        │
│  - execute() lifecycle                                          │
│  - Logging and metrics                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Analysis Components                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  ┌──────────────────────┐  ┌─────────────┐
│ Constitutional       │  │ Code Quality         │  │ Security    │
│ Analyzer             │  │ Analyzer             │  │ Analyzer    │
│                      │  │                      │  │             │
│ - 8 rules validation│  │ - Code smells        │  │ - Cmd inject│
│ - Compliance scoring │  │ - Metrics (LOC, CC)  │  │ - Eval usage│
│ - Violation tracking │  │ - Refactoring opps   │  │ - Input san │
└──────────────────────┘  └──────────────────────┘  └─────────────┘
         │                         │                       │
         └─────────────────────────┼───────────────────────┘
                                   │
                                   ▼
                    ┌──────────────────────────┐
                    │   Result Consolidator    │
                    │                          │
                    │ - Merge results          │
                    │ - Prioritize issues      │
                    │ - Calculate overall score│
                    └──────────┬───────────────┘
                               │
                               ▼
                    ┌──────────────────────────┐
                    │   Report Generator       │
                    │                          │
                    │ - Markdown reports       │
                    │ - JSON data export       │
                    │ - Summary dashboard      │
                    └──────────────────────────┘
```

### 2.2 Data Flow

```
Input (Script Path)
      │
      ▼
┌─────────────────┐
│ Script Loader   │──> Read script file
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Preprocessor    │──> Normalize, extract metadata
└────────┬────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│Constitutional│ │ Quality  │ │ Security │ │ Metrics  │
│ Analysis     │ │ Analysis │ │ Analysis │ │ Collector│
└──────┬───────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
       │              │            │            │
       │              │            │            │
       └──────────────┴────────────┴────────────┘
                      │
                      ▼
              ┌───────────────┐
              │ Consolidator  │──> Merge, prioritize
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ Report Gen    │──> Markdown + JSON
              └───────┬───────┘
                      │
                      ▼
                  Output Files
```

---

## 3. Core Components

### 3.1 ShellScriptAnalysisAgent (Main Class)

**Responsibility**: Orchestrate the entire analysis pipeline

**Inherits From**: `Agent` (from `scripts/coding/ai/shared/agent_base.py`)

**Key Methods**:
```python
class ShellScriptAnalysisAgent(Agent):
    def __init__(self, config: Optional[Dict] = None)
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]
    def _load_script(self, path: str) -> str
    def _preprocess(self, script: str) -> PreprocessedScript
    def _analyze_constitutional(self, script: PreprocessedScript) -> ConstitutionalResult
    def _analyze_quality(self, script: PreprocessedScript) -> QualityResult
    def _analyze_security(self, script: PreprocessedScript) -> SecurityResult
    def _consolidate_results(self, *results) -> ConsolidatedResult
    def _generate_report(self, result: ConsolidatedResult) -> ReportOutput
```

**Configuration Options**:
```python
{
    "analysis_depth": "quick" | "standard" | "deep",
    "constitutional_rules": [1,2,3,4,5,6,7,8],  # Which rules to check
    "include_security": bool,
    "include_llm_analysis": bool,  # Only for "deep" mode
    "parallel_workers": int,  # For batch analysis
    "output_format": "markdown" | "json" | "both",
    "cache_enabled": bool
}
```

### 3.2 ConstitutionalAnalyzer

**Responsibility**: Validate scripts against 8 constitutional rules

**Technique**: Chain-of-Verification

**Process**:
1. **Baseline Analysis**: Initial compliance check per rule
2. **Verification Questions**: Generate specific questions for each rule
3. **Independent Verifications**: Execute each verification independently
4. **Synthesis**: Consolidate verified results
5. **Scoring**: Calculate compliance score (0-100)

**Rules Validated** (from `docs/SHELL_SCRIPTS_CONSTITUTION.md`):
1. Single Responsibility Principle
2. Backward Compatibility
3. Explicit Error Handling
4. Tests Without External Dependencies
5. Clean Code Naming Conventions
6. Size Limits (functions <50 lines, modules <200 lines)
7. Inline Documentation
8. Idempotence

**Output Schema**:
```python
@dataclass
class ConstitutionalResult:
    overall_compliance: bool
    compliance_score: float  # 0-100
    rule_results: Dict[int, RuleResult]
    violations: List[Violation]

@dataclass
class RuleResult:
    rule_number: int
    compliant: bool
    score: float
    violations: List[Violation]
    recommendations: List[str]

@dataclass
class Violation:
    rule_number: int
    line_number: Optional[int]
    severity: str  # "low" | "medium" | "high" | "critical"
    description: str
    recommendation: str
```

### 3.3 CodeQualityAnalyzer

**Responsibility**: Detect code smells and calculate quality metrics

**Technique**: Search Optimization + Pattern Matching

**Metrics Calculated**:
- Lines of Code (LOC)
- Number of functions
- Max function length
- Cyclomatic complexity (estimated)
- Comment ratio
- Function naming consistency

**Code Smells Detected**:
- Long functions (>50 lines)
- Deep nesting (>4 levels)
- Duplicated code blocks
- Magic numbers
- Global variables
- Missing error handling
- Unused functions
- Complex conditionals

**Refactoring Opportunities**:
- Extract function
- Simplify conditionals
- Remove duplication
- Add documentation
- Split large scripts

**Output Schema**:
```python
@dataclass
class QualityResult:
    metrics: CodeMetrics
    code_smells: List[CodeSmell]
    refactoring_opportunities: List[RefactoringOpportunity]
    quality_score: float  # 0-100

@dataclass
class CodeMetrics:
    lines_of_code: int
    lines_of_comments: int
    number_of_functions: int
    max_function_length: int
    average_function_length: float
    cyclomatic_complexity: float
    comment_ratio: float

@dataclass
class CodeSmell:
    type: str  # "long_function", "deep_nesting", etc.
    location: str  # "line 45-120"
    severity: str
    description: str
    recommendation: str
    priority: int  # 1-5

@dataclass
class RefactoringOpportunity:
    type: str  # "extract_function", "simplify_conditional", etc.
    location: str
    effort: str  # "low", "medium", "high"
    impact: str  # "low", "medium", "high"
    description: str
    example: Optional[str]
```

### 3.4 SecurityAnalyzer

**Responsibility**: Detect security vulnerabilities

**Patterns Detected**:
1. Command injection (unquoted variables in commands)
2. SQL injection (dynamic SQL construction)
3. Path traversal (user input in file paths)
4. Eval usage (eval, exec with external input)
5. Unsafe temp file creation
6. Missing input sanitization
7. Hard-coded credentials
8. Insecure permissions

**Output Schema**:
```python
@dataclass
class SecurityResult:
    issues: List[SecurityIssue]
    severity_counts: Dict[str, int]
    security_score: float  # 0-100

@dataclass
class SecurityIssue:
    type: str
    severity: str  # "critical", "high", "medium", "low"
    location: str
    description: str
    cwe_id: Optional[str]  # CWE-78 for command injection, etc.
    recommendation: str
    exploitability: str  # "easy", "medium", "hard"
```

### 3.5 ReportGenerator

**Responsibility**: Generate human-readable and machine-readable reports

**Formats Supported**:
- Markdown (`.md`) - Human-readable
- JSON (`.json`) - Machine-readable
- Summary dashboard - Consolidated view

**Report Types**:

#### Individual Script Report
```
docs/scripts/analisis/
└── individual/
    └── script_name_analysis.md
    └── script_name_analysis.json
```

#### Consolidated Report (All Scripts)
```
docs/scripts/analisis/
└── consolidated_analysis.md
└── consolidated_analysis.json
└── dashboard.md
```

**Markdown Report Structure**:
```markdown
# Script Analysis: script_name.sh

## Summary
- Overall Score: 85/100
- Compliance: COMPLIANT
- Security: SECURE
- Quality: GOOD

## Constitutional Compliance
[Table of 8 rules with scores]

## Code Quality Metrics
[Metrics table]

## Issues Found
[Prioritized list]

## Recommendations
[Prioritized refactoring opportunities]

## Details
[Full analysis per category]
```

---

## 4. Analysis Modes

### 4.1 Quick Mode (Heuristic)

**Duration**: ~0.5 seconds/script
**Use Case**: CI/CD pre-commit hooks

**What it does**:
- Syntax validation (bash -n)
- Basic constitutional checks (set -e, function length)
- Simple metrics (LOC, function count)
- Pattern-based security checks

**What it skips**:
- Deep semantic analysis
- LLM-based reasoning
- Complex refactoring suggestions

### 4.2 Standard Mode (Heuristic + Analysis)

**Duration**: ~2 seconds/script
**Use Case**: Regular quality checks

**What it does**:
- Full constitutional analysis
- Complete code quality metrics
- Security vulnerability scanning
- Refactoring opportunity detection
- Pattern-based code smell detection

**What it skips**:
- LLM-based analysis
- Semantic understanding

### 4.3 Deep Mode (Heuristic + LLM)

**Duration**: ~10-15 seconds/script
**Use Case**: Comprehensive audits

**What it does**:
- Everything from Standard mode
- Chain-of-Verification for constitutional rules
- Auto-CoT for complexity reasoning
- LLM-based code smell detection
- Semantic analysis of intent
- Context-aware recommendations

**Requirements**:
- ANTHROPIC_API_KEY configured
- Internet connectivity

---

## 5. Integration Points

### 5.1 Integration with Existing Tools

**Reuse Existing Validators**:
```python
# Constitutional validation
subprocess.run([
    "bash",
    "scripts/validation/quality/validate_shell_constitution.sh",
    script_path
])

# Syntax validation
subprocess.run([
    "bash",
    "scripts/ci/infrastructure/validate-scripts.sh",
    script_path
])
```

**Parse and Consolidate Results**: Agent parses output and consolidates with own analysis

### 5.2 Integration with Constitution Framework

**Automatic Integration** (from Agent base class):
- Constitution loader
- Guardrails validation
- Traceability enforcement
- No-emoji enforcement

### 5.3 CI/CD Integration

**Pre-commit Hook**:
```bash
# .git/hooks/pre-commit
python scripts/coding/ai/agents/quality/shell_analysis_agent.py \
  --mode quick \
  --changed-only \
  --fail-on-critical
```

**GitHub Actions**:
```yaml
- name: Analyze Shell Scripts
  run: |
    python scripts/coding/ai/agents/quality/shell_analysis_agent.py \
      --mode standard \
      --output-dir reports/ \
      --format json
```

---

## 6. Data Persistence

### 6.1 Analysis Cache

**Location**: `.cache/shell_analysis/`

**Structure**:
```
.cache/shell_analysis/
├── script_hash_map.json
└── results/
    ├── <sha256_of_script>.json
    └── ...
```

**Cache Invalidation**: Based on script content hash (SHA256)

### 6.2 Historical Trending

**Location**: `docs/scripts/analisis/history/`

**Structure**:
```
docs/scripts/analisis/history/
├── 2025-11-13/
│   └── consolidated_analysis.json
├── 2025-11-14/
│   └── consolidated_analysis.json
└── trending.json
```

**Trending Metrics**:
- Overall quality score over time
- Number of violations over time
- Most improved scripts
- Most degraded scripts

---

## 7. Error Handling

### 7.1 Failure Modes

**Scenario 1: Script not found**
- Error: FileNotFoundError
- Handling: Log error, skip script, continue with others
- Report: Mark as "NOT_FOUND" in results

**Scenario 2: Script not parseable**
- Error: SyntaxError from bash -n
- Handling: Mark as "SYNTAX_ERROR", include error message
- Report: Show syntax error in report

**Scenario 3: LLM API failure (deep mode)**
- Error: API timeout, rate limit, auth error
- Handling: Fallback to standard mode (heuristic)
- Report: Note that LLM analysis was skipped

**Scenario 4: Analysis timeout**
- Error: Script analysis exceeds timeout (30s)
- Handling: Kill analysis, mark as "TIMEOUT"
- Report: Partial results if available

### 7.2 Graceful Degradation

**Priority Levels**:
1. **CRITICAL**: Must succeed (script loading, basic parsing)
2. **HIGH**: Should succeed (constitutional analysis, security)
3. **MEDIUM**: Nice to have (LLM analysis, detailed recommendations)

**Degradation Strategy**:
- If CRITICAL fails → Abort that script, continue with others
- If HIGH fails → Log warning, use fallback, continue
- If MEDIUM fails → Log info, skip feature, continue

---

## 8. Performance Considerations

### 8.1 Optimization Strategies

**1. Parallel Processing**:
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(analyze_script, script_paths)
```

**2. Caching**:
- Cache results by script content hash
- Only re-analyze if script changed
- Cache validity: Until script modification

**3. Incremental Analysis**:
```bash
# Analyze only changed scripts in git
git diff --name-only HEAD~1 | grep '.sh$' | \
  python agent.py --stdin --mode standard
```

**4. Progressive Enhancement**:
- Quick mode first (fast)
- Standard mode on-demand
- Deep mode for critical scripts only

### 8.2 Performance Targets

| Mode | Time/Script | Total (253 scripts) | Use Case |
|------|-------------|---------------------|----------|
| Quick | 0.5s | ~2 minutes | CI/CD |
| Standard | 2s | ~8.5 minutes | Regular audits |
| Deep | 10s | ~42 min (6 min parallel) | Comprehensive |

---

## 9. Security Considerations

### 9.1 Script Execution Safety

**CRITICAL**: Agent must **NEVER execute** analyzed scripts

**Safety Measures**:
- Static analysis only (AST parsing, pattern matching)
- No `bash script.sh` execution
- No eval of script content
- Sandbox subprocess calls (read-only filesystem)

### 9.2 Sensitive Data Handling

**API Keys**:
- Never log API keys
- Use environment variables only
- Redact keys in reports

**Script Content**:
- May contain secrets
- Don't include full script content in logs
- Sanitize before LLM API calls

---

## 10. Testing Strategy

### 10.1 Unit Tests

**Coverage Target**: ≥90%

**Test Cases**:
```python
# test_constitutional_analyzer.py
def test_rule_1_single_responsibility()
def test_rule_2_backward_compatibility()
# ... tests for all 8 rules

# test_quality_analyzer.py
def test_calculate_metrics()
def test_detect_long_functions()
def test_detect_code_duplication()

# test_security_analyzer.py
def test_detect_command_injection()
def test_detect_eval_usage()

# test_report_generator.py
def test_generate_markdown_report()
def test_generate_json_report()
```

### 10.2 Integration Tests

**Test with Real Scripts**:
- 10 sample scripts (good, bad, mixed)
- Validate analysis results against expected outcomes
- Test all 3 modes (quick, standard, deep)

### 10.3 Performance Tests

**Load Testing**:
- Analyze 253 scripts in parallel
- Measure total time
- Verify < 10 minutes for standard mode

---

## 11. Deployment

### 11.1 Installation

```bash
# Install dependencies
pip install -r scripts/coding/ai/requirements.txt

# Verify installation
python scripts/coding/ai/agents/quality/shell_analysis_agent.py --version
```

### 11.2 Configuration

**Environment Variables**:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."  # For deep mode
export SHELL_ANALYSIS_CACHE_DIR=".cache/shell_analysis"
export SHELL_ANALYSIS_MODE="standard"
```

**Configuration File** (optional):
```json
{
  "analysis_depth": "standard",
  "constitutional_rules": [1,2,3,4,5,6,7,8],
  "parallel_workers": 10,
  "cache_enabled": true,
  "output_dir": "docs/scripts/analisis"
}
```

---

## 12. Monitoring and Observability

### 12.1 Metrics

**Agent Metrics**:
- Total scripts analyzed
- Analysis duration (avg, p50, p95, p99)
- Failure rate
- Cache hit rate

**Quality Metrics**:
- Overall quality score (avg across all scripts)
- Compliance rate (% of compliant scripts)
- Security issue count (by severity)

### 12.2 Logging

**Log Levels**:
- DEBUG: Detailed analysis steps
- INFO: Analysis start/end, summary
- WARNING: Fallbacks, degraded mode
- ERROR: Analysis failures

**Log Format**:
```
[2025-11-13T08:30:00] ShellScriptAnalysisAgent - INFO - Analyzing script: validate.sh
[2025-11-13T08:30:01] ConstitutionalAnalyzer - INFO - Rule 3 violation detected: line 45
[2025-11-13T08:30:02] ShellScriptAnalysisAgent - INFO - Analysis complete: score=85/100
```

---

## 13. Future Enhancements

### Phase 2 Enhancements (Post-MVP)

1. **Interactive Mode**: CLI with prompts for configuration
2. **Watch Mode**: Auto-analyze on file changes
3. **Diff Mode**: Compare analysis between git commits
4. **Recommendation Auto-Apply**: Automatically fix simple issues
5. **Custom Rules**: User-defined validation rules
6. **Integration with IDEs**: VSCode extension
7. **Web Dashboard**: Interactive HTML reports
8. **Slack/Discord Notifications**: Alert on critical issues

---

## 14. Success Criteria

### 14.1 Functional Requirements ✓

- [ ] Analyzes all 253 scripts successfully
- [ ] Validates all 8 constitutional rules
- [ ] Generates markdown and JSON reports
- [ ] Supports 3 analysis modes (quick/standard/deep)
- [ ] Integrates with existing validation tools

### 14.2 Non-Functional Requirements ✓

- [ ] Performance: <10 minutes for 253 scripts (standard mode)
- [ ] Accuracy: <10% false positive rate
- [ ] Reliability: 99% success rate
- [ ] Test Coverage: ≥90%
- [ ] Documentation: Complete user guide and API docs

---

## 15. Traceability

**Issue**: FEATURE-SHELL-ANALYSIS-001
**Planning Doc**: `docs/sdlc_outputs/planning/issue-shell-script-analysis-agent.md`
**Feasibility Doc**: `docs/sdlc_outputs/feasibility/feasibility-shell-script-analysis-agent.md`
**This Document**: `docs/sdlc_outputs/design/hld-shell-script-analysis-agent.md`

**References**:
- Agent Framework: `scripts/coding/ai/shared/agent_base.py`
- Shell Constitution: `docs/SHELL_SCRIPTS_CONSTITUTION.md`
- Validation Tools: `scripts/validation/quality/validate_shell_constitution.sh`
- SDLC Methodology: `docs/scripts/sdlc-agent-guide.md`

---

**Generado por**: Claude (SDLCDesignAgent)
**Timestamp**: 2025-11-13T08:25:00Z
**Metodología**: SDLC Design Phase (HLD)
**Próximo paso**: Low-Level Design (LLD)
