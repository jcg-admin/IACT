---
title: ADR-043 CoherenceAnalyzerAgent
date: 2025-11-13
status: Implemented
decision_makers: DevOps Team, SDLC Agent
---

# ADR-043: CoherenceAnalyzerAgent

**Date**: 2025-11-13
**Status**: Implemented
**Decision Makers**: DevOps Team, SDLC Agent
**Related**: ADR-042 (Automation System Architecture)

---

## Context

The IACT project requires advanced UI/API coherence analysis to ensure frontend and backend stay synchronized during development. Manual verification of coherence between:

- API endpoints (Django REST Framework ViewSets)
- UI services (TypeScript/JavaScript)
- UI tests (Jest/Jasmine)

...is time-consuming, error-prone, and does not scale. The existing `check_ui_api_coherence.sh` script (75 lines) performs basic checks but lacks:

1. **AST-level parsing** of Python and JavaScript/TypeScript code
2. **Intelligent correlation** between API endpoints, UI services, and tests
3. **Gap detection** (missing services, missing tests)
4. **Confidence scoring** for correlations (0-100%)
5. **Change detection** via git diff analysis
6. **Comprehensive reporting** in JSON format

### Problem Statement

When API endpoints change (new endpoints, modified actions, deleted endpoints), we need to:

- Detect which UI services need updates
- Identify missing UI service implementations
- Find untested UI services
- Calculate confidence that UI and API are aligned
- Generate actionable reports for developers

### Business Impact

- **Reduced bugs**: Catch UI/API mismatches before production
- **Faster development**: Automated analysis vs manual code review
- **Better test coverage**: Identify gaps in UI testing
- **CI/CD integration**: Block merges when coherence < threshold

---

## Decision

We decided to implement **CoherenceAnalyzerAgent** as a Python-based intelligent agent using:

### 1. Architecture

```
CoherenceAnalyzerAgent
├── AST Parsing Layer
│   ├── API Files (views.py, serializers.py, urls.py)
│   └── UI Files (services/*.ts, components/*.tsx, __tests__/*.test.js)
├── Analysis Layer
│   ├── Endpoint Change Detection (REST, GraphQL)
│   ├── Correlation Analysis (API → Service → Test)
│   ├── Gap Detection (missing services, missing tests)
│   └── Confidence Scoring (0-100%)
├── Integration Layer
│   ├── Git Diff Analysis
│   └── CLI Interface (--git-diff, --base-branch, --output)
└── Reporting Layer
    └── JSON Report Generation
```

### 2. Technology Stack

- **Python 3.11+**: Mature AST parsing library
- **ast module**: Parse Python code (Django views, serializers)
- **regex**: Parse JavaScript/TypeScript (UI services, tests)
- **subprocess**: Git integration
- **argparse**: CLI interface
- **json**: Report generation

### 3. Key Features

#### A. AST Parsing - API Files

```python
# Parse Django ViewSets
def parse_api_views(code: str) -> List[APIEndpoint]:
    # AST parsing to extract:
    # - ViewSet classes (ModelViewSet, ReadOnlyModelViewSet)
    # - @action decorators
    # - HTTP methods (GET, POST, PUT, DELETE)
    # - Endpoint names
```

**Why AST vs Regex?**

- AST is syntax-aware, handles nested classes, decorators correctly
- Regex fails on complex Python syntax, comments, strings
- AST provides line numbers for better error reporting

#### B. Correlation Analysis

```python
def correlate_full_chain(
    api_endpoints: List[APIEndpoint],
    ui_services: List[UIService],
    ui_tests: List[UITest]
) -> List[CorrelationResult]:
    # Build chains: API → Service → Test
    # Calculate confidence scores
    # Detect complete vs partial chains
```

**Correlation Algorithm**:

1. **Name similarity**: Compare endpoint names to service names
   - Exact match (normalized): 95% confidence
   - Contains match: 70-80% confidence (length ratio)
   - Prefix match (3+ chars): 60%+ confidence
2. **Field matching**: Compare serializer fields to service methods
3. **Endpoint-to-service mapping**: Match URL patterns to service API calls

#### C. Gap Detection

```python
def detect_gaps(
    api_endpoints: List[APIEndpoint],
    ui_services: List[UIService],
    ui_tests: List[UITest]
) -> GapDetectionResult:
    # Find:
    # - API endpoints without UI services (warning)
    # - UI services without tests (error)
    # - Orphaned UI services (info)
```

**Severity Levels**:

- `error`: Blocks merge (service without tests)
- `warning`: Review required (endpoint without service)
- `info`: Informational (orphaned code)

#### D. Confidence Scoring

```python
def calculate_confidence_score(
    api_name: str,
    ui_name: str,
    has_common_fields: bool,
    common_field_count: int
) -> float:
    # Base score: name similarity (0-95)
    # Boost: +2 per common field (max +20)
    # Returns: 0-100 confidence score
```

**Confidence Interpretation**:

- 80-100%: Strong correlation, high confidence
- 50-79%: Medium correlation, review recommended
- 0-49%: Weak/no correlation, manual verification needed

### 4. CLI Interface

```bash
# Analyze git diff
python coherence_analyzer_agent.py \
    --git-diff HEAD~1 \
    --base-branch main \
    --output /tmp/coherence_report.json \
    --threshold 70.0

# Exit codes:
# 0: Success (confidence >= threshold)
# 1: Failed (confidence < threshold)
# 2: Warnings
# 3: Configuration error
```

### 5. JSON Report Format

```json
{
  "status": "success",
  "timestamp": "2025-11-13T12:00:00",
  "summary": {
    "total_api_endpoints": 25,
    "total_ui_services": 20,
    "total_ui_tests": 45,
    "correlation_rate": 80.0,
    "test_coverage_rate": 90.0
  },
  "correlations": [
    {
      "api_endpoint": "UserViewSet",
      "ui_service": "UserService",
      "service_method": "getUsers",
      "test_name": "should fetch users",
      "confidence": 95.0,
      "has_api": true,
      "has_service": true,
      "has_test": true
    }
  ],
  "gaps": {
    "missing_ui_services": [
      {
        "api_endpoint": "ProductViewSet",
        "severity": "warning",
        "message": "No UI service found for API endpoint"
      }
    ],
    "missing_ui_tests": [
      {
        "service_name": "OrderService",
        "severity": "error",
        "message": "No tests found for UI service"
      }
    ]
  },
  "confidence_score": 85.5,
  "changes": []
}
```

---

## Consequences

### Positive

1. **Automated Coherence Verification**
   - Detects UI/API mismatches automatically
   - Runs in CI/CD pipeline (pre-merge checks)
   - Saves ~2-4 hours/week of manual review

2. **High Test Coverage**
   - 50 unit tests (100% coverage of core logic)
   - Tests cover AST parsing, correlation, gap detection
   - Ensures agent reliability

3. **Intelligent Analysis**
   - AST-based parsing (robust vs regex)
   - Confidence scoring (data-driven decisions)
   - Gap detection (actionable insights)

4. **Developer-Friendly**
   - Clear JSON reports
   - Actionable gap messages
   - CLI integration

5. **Extensible**
   - Support for GraphQL (future)
   - Support for gRPC (future)
   - Support for OpenAPI schemas (future)

### Negative

1. **Python/JavaScript Coupling**
   - Assumes Django + React/Angular stack
   - Requires updates if stack changes (e.g., FastAPI, Vue)
   - **Mitigation**: Pluggable parsers via config

2. **Regex Limitations (UI Parsing)**
   - JavaScript/TypeScript parsed via regex (less robust than AST)
   - May miss complex service patterns
   - **Mitigation**: Use TypeScript compiler API (future enhancement)

3. **Maintenance Overhead**
   - Must update parser when Django/DRF APIs change
   - Must update regex patterns for new UI frameworks
   - **Mitigation**: Version-aware parsing, comprehensive tests

4. **Performance on Large Codebases**
   - AST parsing 1000+ files may be slow
   - **Mitigation**: Git diff filtering, parallel processing (future)

5. **False Positives/Negatives**
   - Name similarity may produce false correlations
   - Confidence thresholds require tuning per project
   - **Mitigation**: Configurable thresholds, manual override

---

## Implementation

### File Structure

```
scripts/coding/ai/automation/
├── coherence_analyzer_agent.py    (1200+ lines, implemented)
└── __init__.py

tests/ai/automation/
├── test_coherence_analyzer_agent.py (50 tests, all passing)
└── fixtures/
    ├── sample_constitucion.yaml
    ├── sample_ci_local.yaml
    └── sample_git_diff.txt

docs/adr/
└── ADR-043-coherence-analyzer-agent.md (this file)
```

### Key Classes

```python
@dataclass
class APIEndpoint:
    name: str
    endpoint_type: str  # viewset, view, graphql_query
    actions: List[str]
    methods: List[str]  # GET, POST, PUT, DELETE
    fields: List[str]

@dataclass
class UIService:
    name: str
    methods: List[UIServiceMethod]

@dataclass
class CorrelationResult:
    api_endpoint: str
    ui_service: str
    service_method: str
    test_name: str
    confidence: float
    has_api: bool
    has_service: bool
    has_test: bool

@dataclass
class GapDetectionResult:
    missing_ui_services: List[GapInfo]
    missing_ui_tests: List[GapInfo]
```

### Testing Strategy

**Test Coverage: 50 tests**

1. **AST Parsing (10 tests)**
   - test_parse_api_views_basic
   - test_parse_api_views_with_actions
   - test_parse_api_serializers
   - test_parse_api_urls
   - test_parse_ui_services
   - test_parse_ui_service_methods
   - test_parse_ui_tests
   - test_parse_ui_components
   - test_edge_case_very_large_file
   - test_edge_case_unicode_characters

2. **Endpoint Change Detection (5 tests)**
   - test_detect_rest_endpoint_changes_new
   - test_detect_rest_endpoint_changes_modified
   - test_detect_rest_endpoint_changes_deleted
   - test_detect_graphql_endpoint_changes
   - test_detect_endpoint_changes_no_changes

3. **Correlation Analysis (5 tests)**
   - test_correlation_api_to_ui_service
   - test_correlation_ui_service_to_test
   - test_correlation_full_chain
   - test_correlation_confidence_high
   - test_correlation_confidence_low

4. **Gap Detection (5 tests)**
   - test_gap_detection_missing_ui_service
   - test_gap_detection_missing_ui_test
   - test_gap_detection_missing_both
   - test_gap_detection_no_gaps
   - test_gap_detection_partial_coverage

5. **Confidence Scoring (5 tests)**
   - test_confidence_scoring_exact_match
   - test_confidence_scoring_partial_match
   - test_confidence_scoring_no_match
   - test_confidence_scoring_with_fields
   - test_confidence_scoring_edge_cases

6. **CLI Interface (5 tests)**
   - test_cli_argument_parsing_git_diff
   - test_cli_argument_parsing_base_branch
   - test_cli_argument_parsing_output
   - test_cli_argument_parsing_all_options
   - test_cli_argument_parsing_defaults

7. **Report Generation (5 tests)**
   - test_report_generation_structure
   - test_report_generation_gaps_section
   - test_report_generation_confidence_overall
   - test_report_export_json
   - test_report_summary_statistics

8. **Git Integration (5 tests)**
   - test_git_diff_integration
   - test_git_diff_file_filtering
   - test_git_diff_error_handling
   - test_analyze_git_changes
   - test_empty_git_diff

9. **Error Handling (5 tests)**
   - test_parse_api_invalid_syntax
   - test_error_handling_file_not_found
   - test_error_handling_empty_file
   - test_error_handling_malformed_code
   - test_parse_ui_tests_coverage

**Result**: 50/50 tests passing (100% success rate)

---

## Integration with Automation System

### 1. Invocation by Bash Script

```bash
# In check_ui_api_coherence.sh
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff "${GIT_DIFF_REF}" \
    --base-branch "${BASE_BRANCH}" \
    --output /tmp/coherence_report.json \
    --threshold 70.0

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "ERROR: UI/API coherence check failed"
    cat /tmp/coherence_report.json | jq '.gaps'
    exit 1
fi
```

### 2. CI/CD Pipeline Integration

```yaml
# .ci-local.yaml
jobs:
  - name: coherence-check
    stage: validation
    script: |
      python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
        --git-diff origin/main \
        --threshold 75.0
    allow_failure: false
    on:
      pattern: "**/*.{py,ts,tsx,js}"
```

### 3. Pre-commit Hook

```bash
# .git/hooks/pre-commit
changed_files=$(git diff --cached --name-only)

if echo "$changed_files" | grep -qE '\.(py|ts|tsx|js)$'; then
    python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
        --git-diff HEAD \
        --threshold 65.0 || exit 1
fi
```

---

## Alternatives Considered

### Alternative 1: OpenAPI Schema Comparison

**Approach**: Generate OpenAPI schemas from Django, compare to UI service contracts

**Pros**:

- Industry standard (OpenAPI 3.0)
- Tool support (Swagger, Redoc)

**Cons**:

- Doesn't cover UI tests
- Requires schema generation step
- No confidence scoring

**Decision**: Rejected (insufficient for test coverage analysis)

### Alternative 2: Runtime Instrumentation

**Approach**: Instrument API and UI at runtime, detect mismatches via monitoring

**Pros**:

- Detects real-world usage patterns
- No static analysis needed

**Cons**:

- Production risk
- Delayed detection (post-deployment)
- No pre-merge blocking

**Decision**: Rejected (not preventative)

### Alternative 3: Manual Code Review

**Approach**: Rely on developers to verify coherence during PR review

**Pros**:

- No tooling required
- Human judgment

**Cons**:

- Scales poorly
- Error-prone
- No metrics

**Decision**: Rejected (does not scale)

### Alternative 4: TypeScript Compiler API

**Approach**: Use TypeScript compiler API for UI parsing (vs regex)

**Pros**:

- Robust AST parsing for TypeScript
- Better accuracy than regex

**Cons**:

- Requires Node.js runtime
- Adds complexity (Python + Node)
- Performance overhead

**Decision**: Deferred (future enhancement)

---

## Metrics and Success Criteria

### Key Metrics

1. **Test Coverage**: 50 tests, 100% passing
2. **Code Coverage**: 90%+ (pytest-cov)
3. **Performance**: < 5 seconds for 100 files
4. **Accuracy**: < 5% false positives/negatives (manual validation)

### Success Criteria

- [x] All 50 tests passing
- [x] AST parsing for Python (Django)
- [x] Regex parsing for JavaScript/TypeScript
- [x] Correlation analysis (API → Service → Test)
- [x] Gap detection (missing services, tests)
- [x] Confidence scoring (0-100%)
- [x] CLI interface (--git-diff, --output)
- [x] JSON report generation
- [x] Git integration
- [x] Error handling (invalid syntax, missing files)
- [x] ADR documentation (this file)

---

## Future Enhancements

### Phase 2 (Q1 2026)

1. **TypeScript AST Parsing**
   - Replace regex with TypeScript compiler API
   - Improve accuracy for complex UI services

2. **GraphQL Support**
   - Parse GraphQL schemas (.graphql files)
   - Detect GraphQL query/mutation changes

3. **gRPC Support**
   - Parse .proto files
   - Correlate gRPC services to UI

4. **Parallel Processing**
   - Parse files in parallel (multiprocessing)
   - Improve performance on large codebases

5. **Machine Learning Enhancements**
   - Train model to improve confidence scoring
   - Learn from manual corrections

### Phase 3 (Q2 2026)

1. **Dashboard**
   - Visualize coherence trends over time
   - Track gap reduction progress

2. **Auto-remediation**
   - Generate missing UI services (templates)
   - Generate missing tests (TestingAgent integration)

3. **Multi-repository Support**
   - Analyze monorepos
   - Cross-repo coherence (microservices)

---

## References

- **Parent ADR**: ADR-042 (Automation System Architecture)
- **Architecture Doc**: docs/devops/automatizacion/planificacion/AGENTS_ARCHITECTURE.md
- **Implementation**: scripts/coding/ai/automation/coherence_analyzer_agent.py
- **Tests**: tests/ai/automation/test_coherence_analyzer_agent.py
- **Related Scripts**: scripts/check_ui_api_coherence.sh

---

## Approval

**Date**: 2025-11-13
**Approved by**: DevOps Team, SDLC Agent
**Status**: Implemented
**Review date**: 2026-01-13 (quarterly review)

---

## Changelog

| Date       | Version | Changes                                  |
| ---------- | ------- | ---------------------------------------- |
| 2025-11-13 | 1.0     | Initial implementation, 50 tests passing |
