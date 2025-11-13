# High-Level Design - DocumentationAnalysisAgent

**Component**: DocumentationAnalysisAgent
**Issue ID**: FEATURE-DOCS-ANALYSIS-001
**Date**: 2025-11-13
**Status**: Design Phase
**Version**: 1.0

---

## 1. Overview

DocumentationAnalysisAgent es un agente de analisis exhaustivo de documentacion Markdown que evalua calidad, estructura, cumplimiento de Constitution, trazabilidad y validez de links en toda la documentacion del proyecto.

### 1.1 Purpose

Proporcionar analisis automatico y sistematico de documentacion Markdown con:
- Scoring cuantitativo (0-100) de calidad
- Validacion de estructura y formato
- Verificacion de Constitution compliance
- Deteccion de links rotos (internal/external)
- Analisis de trazabilidad (issues, ADRs, specs)
- Reportes agrupados por dominio (DDD-based)
- Remediation planning automatico

### 1.2 Design Principles

1. **Modular Architecture**: 6 componentes independientes y reusables
2. **Pattern Reuse**: Seguir patron exitoso de ShellScriptAnalysisAgent
3. **Performance**: Parallel processing con caching SHA256
4. **Extensibility**: Facil agregar nuevos analyzers o metrics
5. **DDD-Aligned**: Organizacion por dominios del proyecto
6. **Constitution Compliance**: Principles 1-8 aplicados sistematicamente

---

## 2. System Architecture

### 2.1 Component Diagram

```
DocumentationAnalysisAgent
├── StructureAnalyzer
│   ├── HeadingValidator
│   ├── FrontmatterValidator
│   └── SectionValidator
├── QualityAnalyzer
│   ├── ReadabilityMetrics (Flesch-Kincaid)
│   ├── CompletenessChecker
│   └── FormattingValidator
├── ConstitutionAnalyzer
│   ├── PrincipleChecker (1-8)
│   ├── EmojiDetector
│   └── SecurityScanner
├── TraceabilityAnalyzer
│   ├── IssueLinksValidator
│   ├── ADRLinksValidator
│   └── SpecLinksValidator
├── LinkValidator
│   ├── InternalLinkChecker
│   └── ExternalLinkChecker (optional)
└── ReportGenerator
    ├── PerDocumentReport (MD + JSON)
    ├── DomainSummary (DDD-grouped)
    └── RemediationPlanner
```

### 2.2 Data Flow

```
Input: docs/**/*.md files
  ↓
[1] File Discovery & Filtering
  ↓
[2] Parallel Analysis (ThreadPoolExecutor)
  ├─→ StructureAnalyzer → structure_score
  ├─→ QualityAnalyzer → quality_score
  ├─→ ConstitutionAnalyzer → constitution_score
  ├─→ TraceabilityAnalyzer → traceability_score
  └─→ LinkValidator → link_validation_results
  ↓
[3] Score Aggregation (weighted average)
  ↓
[4] Domain Classification (DDD)
  ↓
[5] Report Generation
  ├─→ Per-document reports (MD + JSON)
  ├─→ Domain summaries
  ├─→ Consolidated report
  └─→ Remediation plan
  ↓
Output: reports/ directory
```

### 2.3 Technology Stack

**Language**: Python 3.11+
**Libraries**:
- `textstat`: Readability metrics (Flesch-Kincaid)
- `mistune`: Markdown parsing to AST
- `requests`: External link checking (optional)
- `pathlib`: File system operations
- `re`: Pattern matching
- `concurrent.futures`: Parallel processing
- `hashlib`: SHA256 caching
- `json`: Report serialization

**Base Class**: `Agent` (scripts.coding.ai.shared.agent_base)

---

## 3. Component Specifications

### 3.1 StructureAnalyzer

**Purpose**: Validate Markdown structure and format

**Checks**:
1. Has H1 title (single, at top)
2. Heading hierarchy correct (no skips: H1→H2→H3, not H1→H3)
3. Has frontmatter (if required by domain)
4. Has required sections (domain-specific)
5. Proper Markdown syntax

**Scoring**:
```python
structure_score = (
    h1_present * 0.20 +
    heading_hierarchy * 0.25 +
    frontmatter_valid * 0.15 +
    required_sections * 0.30 +
    markdown_syntax * 0.10
) * 100
```

**Output**: StructureResult(score, issues, recommendations)

### 3.2 QualityAnalyzer

**Purpose**: Analyze documentation quality metrics

**Metrics**:
1. **Readability**: Flesch-Kincaid Reading Ease (target: > 40)
2. **Completeness**: Has intro, body, conclusion
3. **Clarity**: No undefined acronyms, clear language
4. **Formatting**: Code blocks with lang, tables formatted, consistent lists
5. **Length**: Appropriate length for content type

**Scoring**:
```python
quality_score = (
    readability * 0.30 +
    completeness * 0.25 +
    clarity * 0.20 +
    formatting * 0.15 +
    length_appropriateness * 0.10
) * 100
```

**Output**: QualityResult(score, metrics, issues, recommendations)

### 3.3 ConstitutionAnalyzer

**Purpose**: Verify Constitution principles compliance

**Principles Checked**:
1. **Principle 1 (Clarity)**: Clear titles, well-structured
2. **Principle 2 (No Emojis)**: Zero emojis in content
3. **Principle 3 (Traceability)**: Links to issues/ADRs/specs
4. **Principle 5 (Documentation)**: Meta-documentation present
5. **Principle 7 (Security)**: No secrets, no sensitive info

**Scoring**:
```python
constitution_score = (
    sum(principle_scores) / applicable_principles_count
) * 100
```

**Output**: ConstitutionResult(score, violations, applicable_principles)

### 3.4 TraceabilityAnalyzer

**Purpose**: Verify traceability to requirements and decisions

**Checks**:
1. Links to issues (FEATURE-*, BUG-*, IMPROVEMENT-*)
2. Links to ADRs (ADR-YYYY-NNN format)
3. Links to specs/requirements
4. Cross-references to related docs

**Scoring**:
```python
traceability_score = (
    has_issue_links * 0.40 +
    has_adr_links * 0.30 +
    has_spec_links * 0.20 +
    has_cross_refs * 0.10
) * 100
```

**Output**: TraceabilityResult(score, links_found, missing_links)

### 3.5 LinkValidator

**Purpose**: Validate internal and external links

**Validation**:
1. **Internal Links**: File exists, path correct
2. **Internal Anchors**: Heading/ID exists in target
3. **External Links**: HTTP status (optional, rate-limited)

**Implementation**:
```python
class LinkValidator:
    def validate_internal(self, link: str, base_path: Path) -> LinkResult
    def validate_external(self, url: str) -> LinkResult  # optional
    def validate_anchor(self, link: str, target: Path) -> LinkResult
```

**Output**: LinkValidationResult(valid_count, broken_count, issues)

### 3.6 ReportGenerator

**Purpose**: Generate comprehensive reports

**Report Types**:
1. **Per-Document Report** (MD + JSON):
   - Overall score
   - Component scores (structure, quality, constitution, traceability)
   - Issues list with severity
   - Recommendations with priority

2. **Domain Summary**:
   - Aggregate stats per domain
   - Priority issues
   - Domain owner identified

3. **Consolidated Report**:
   - Project-wide statistics
   - Top issues across domains
   - Trend analysis (if cached data available)

4. **Remediation Plan**:
   - DDD-grouped action items
   - Estimated effort
   - Priority assignments

**Output**: Reports written to `docs_analysis_reports/`

---

## 4. Domain Classification (DDD)

### 4.1 Domain Mapping

```python
DOMAIN_MAPPING = {
    "docs/backend": {
        "owner": "Backend Team",
        "priority": "P0",
        "required_sections": ["Architecture", "API", "Database"]
    },
    "docs/frontend": {
        "owner": "Frontend Team",
        "priority": "P0",
        "required_sections": ["Components", "State Management", "Routing"]
    },
    "docs/infrastructure": {
        "owner": "Infrastructure Team",
        "priority": "P0",
        "required_sections": ["Setup", "Configuration", "Deployment"]
    },
    "docs/agent": {
        "owner": "AI Team",
        "priority": "P1",
        "required_sections": ["Architecture", "Design", "Implementation"]
    },
    "docs/api": {
        "owner": "API Team",
        "priority": "P1",
        "required_sections": ["Endpoints", "Authentication", "Examples"]
    },
    "docs/scripts": {
        "owner": "DevOps Team",
        "priority": "P2",
        "required_sections": ["Purpose", "Usage", "Examples"]
    },
    "docs/gobernanza": {
        "owner": "Architecture Team",
        "priority": "P1",
        "required_sections": ["Principles", "Guidelines", "ADRs"]
    },
    "docs/analisis": {
        "owner": "QA Team",
        "priority": "P2",
        "required_sections": ["Methodology", "Results", "Recommendations"]
    },
}
```

### 4.2 Domain Classification Logic

```python
def classify_domain(file_path: Path) -> str:
    for domain_pattern, config in DOMAIN_MAPPING.items():
        if file_path.match(f"{domain_pattern}/**/*.md"):
            return domain_pattern
    return "docs/otros"  # Fallback
```

---

## 5. Scoring System

### 5.1 Weighted Average

```python
def calculate_overall_score(
    structure_score: float,
    quality_score: float,
    constitution_score: float,
    traceability_score: float,
    link_validation_score: float
) -> float:
    """
    Calculate weighted overall score.

    Weights:
    - Structure: 25%
    - Quality: 30%
    - Constitution: 20%
    - Traceability: 15%
    - Links: 10%
    """
    return (
        structure_score * 0.25 +
        quality_score * 0.30 +
        constitution_score * 0.20 +
        traceability_score * 0.15 +
        link_validation_score * 0.10
    )
```

### 5.2 Score Thresholds

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| 90-100 | Excellent | Production-ready, minimal issues |
| 80-89 | Good | Minor improvements needed |
| 70-79 | Acceptable | Moderate improvements needed |
| 60-69 | Poor | Significant improvements needed |
| 0-59 | Critical | Major issues, needs rework |

---

## 6. Performance Optimization

### 6.1 Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_documents_parallel(
    docs: List[Path],
    workers: int = 10
) -> List[AnalysisResult]:
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(analyze_document, doc)
            for doc in docs
        ]
        return [future.result() for future in futures]
```

### 6.2 Caching Strategy

```python
import hashlib

def get_cache_key(file_path: Path) -> str:
    content = file_path.read_text(encoding='utf-8')
    return hashlib.sha256(content.encode()).hexdigest()

def is_cached(file_path: Path, cache_dir: Path) -> bool:
    cache_key = get_cache_key(file_path)
    cache_file = cache_dir / f"{cache_key}.json"
    return cache_file.exists()
```

**Cache Invalidation**: When content changes (different SHA256), re-analyze

### 6.3 Performance Targets

| Mode | Time/Doc | Total (300 docs) | Memory |
|------|----------|------------------|--------|
| QUICK | < 0.5s | < 5 min | < 200MB |
| STANDARD | < 2s | < 10 min | < 500MB |
| DEEP | < 10s | < 50 min | < 800MB |

---

## 7. API Design

### 7.1 Main Interface

```python
class DocumentationAnalysisAgent(Agent):
    """
    Agent for comprehensive Markdown documentation analysis.

    Attributes:
        mode: Analysis mode (QUICK/STANDARD/DEEP)
        workers: Number of parallel workers
        cache_enabled: Enable SHA256-based caching
        external_links: Check external links (optional)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="DocumentationAnalysisAgent", config=config)
        self.mode = self.config.get("mode", "STANDARD")
        self.workers = self.config.get("workers", 10)
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.external_links = self.config.get("external_links", False)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute documentation analysis.

        Args:
            input_data: {
                "docs_path": str,  # Path to docs directory
                "output_dir": str,  # Output directory for reports
                "domains": List[str],  # Optional: specific domains to analyze
            }

        Returns:
            {
                "status": str,
                "summary": {
                    "total_docs": int,
                    "average_score": float,
                    "critical_issues": int,
                    "by_domain": Dict[str, DomainStats]
                },
                "report_paths": {
                    "consolidated": str,
                    "domain_summaries": List[str],
                    "remediation_plan": str
                }
            }
        """
        pass
```

### 7.2 CLI Interface

```bash
# Analyze all docs
python -m scripts.cli.docs_analysis_agent docs/ --mode STANDARD --workers 10

# Analyze specific domain
python -m scripts.cli.docs_analysis_agent docs/backend --output reports/backend

# Quick analysis (CI/CD)
python -m scripts.cli.docs_analysis_agent docs/ --mode QUICK --no-cache

# With external link checking
python -m scripts.cli.docs_analysis_agent docs/ --check-external-links
```

### 7.3 Library Usage

```python
from scripts.coding.ai.agents.documentation.documentation_analysis_agent import (
    DocumentationAnalysisAgent
)

# Initialize agent
agent = DocumentationAnalysisAgent(config={
    "mode": "STANDARD",
    "workers": 10,
    "cache_enabled": True,
    "external_links": False
})

# Execute analysis
result = agent.execute({
    "docs_path": "docs/",
    "output_dir": "docs_analysis_reports/"
})

# Access results
print(f"Average Score: {result.data['summary']['average_score']:.1f}/100")
print(f"Critical Issues: {result.data['summary']['critical_issues']}")
```

---

## 8. Integration Points

### 8.1 With Existing Agents

**ETACodexAgent**:
- DocumentationAnalysisAgent is superset
- Can replace or complement ETACodexAgent
- Backward compatible API

**DocsStructureGate**:
- DocumentationAnalysisAgent extends functionality
- Can use DocsStructureGate as StructureAnalyzer component
- Migration path defined

**ShellScriptAnalysisAgent**:
- Shared patterns (reporting, caching, DDD)
- Consistent CLI interface
- Similar output format

### 8.2 CI/CD Integration

```yaml
# .github/workflows/docs-quality.yml
docs-quality-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Analyze Documentation
      run: |
        python -m scripts.cli.docs_analysis_agent docs/ \
          --mode STANDARD \
          --threshold 80 \
          --output reports/
    - name: Upload Reports
      uses: actions/upload-artifact@v3
      with:
        name: docs-analysis-reports
        path: reports/
```

### 8.3 Gate Integration

```python
# scripts/ci/gates/docs_quality_gate.py
from scripts.coding.ai.agents.documentation.documentation_analysis_agent import (
    DocumentationAnalysisAgent
)

def run_gate(threshold: float = 85.0) -> int:
    agent = DocumentationAnalysisAgent(config={"mode": "QUICK"})
    result = agent.execute({"docs_path": "docs/"})

    avg_score = result.data["summary"]["average_score"]
    if avg_score < threshold:
        print(f"FAIL: Documentation quality {avg_score:.1f} below threshold {threshold}")
        return 1

    print(f"PASS: Documentation quality {avg_score:.1f}")
    return 0
```

---

## 9. Error Handling

### 9.1 Graceful Degradation

```python
def analyze_document(doc_path: Path) -> AnalysisResult:
    try:
        # Full analysis
        return full_analysis(doc_path)
    except MarkdownParsingError as e:
        logger.warning(f"Markdown parsing failed for {doc_path}: {e}")
        return partial_analysis(doc_path)  # Fallback to basic checks
    except Exception as e:
        logger.error(f"Analysis failed for {doc_path}: {e}")
        return error_result(doc_path, str(e))
```

### 9.2 Timeout Handling

```python
from concurrent.futures import TimeoutError

def analyze_with_timeout(doc: Path, timeout: int = 30) -> AnalysisResult:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(analyze_document, doc)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            logger.warning(f"Analysis timeout for {doc}")
            return timeout_result(doc)
```

---

## 10. Security Considerations

### 10.1 Sensitive Data Detection

```python
SENSITIVE_PATTERNS = [
    r'password\s*=\s*["\'].*["\']',
    r'api_key\s*=\s*["\'].*["\']',
    r'secret\s*=\s*["\'].*["\']',
    r'token\s*=\s*["\'].*["\']',
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
]

def scan_for_sensitive_data(content: str) -> List[SecurityIssue]:
    issues = []
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(SecurityIssue(
                type="sensitive_data",
                pattern=pattern,
                severity="HIGH"
            ))
    return issues
```

### 10.2 External Link Safety

```python
def check_external_link(url: str) -> LinkResult:
    # Whitelist safe domains
    SAFE_DOMAINS = ["github.com", "docs.python.org", "stackoverflow.com"]

    domain = urlparse(url).netloc
    if domain not in SAFE_DOMAINS:
        logger.warning(f"External link to non-whitelisted domain: {domain}")

    # Rate limiting: max 10 requests/second
    with rate_limiter:
        response = requests.get(url, timeout=5)
        return LinkResult(url=url, status=response.status_code)
```

---

## 11. Extensibility

### 11.1 Custom Analyzers

```python
class CustomAnalyzer(ABC):
    @abstractmethod
    def analyze(self, content: str, metadata: Dict) -> AnalysisResult:
        pass

# Users can add custom analyzers
agent = DocumentationAnalysisAgent(config={
    "custom_analyzers": [MyCustomAnalyzer(), AnotherAnalyzer()]
})
```

### 11.2 Custom Metrics

```python
class QualityAnalyzer:
    def __init__(self, custom_metrics: List[QualityMetric] = None):
        self.metrics = DEFAULT_METRICS + (custom_metrics or [])

    def analyze(self, doc: Document) -> QualityResult:
        metric_results = [metric.calculate(doc) for metric in self.metrics]
        return aggregate_results(metric_results)
```

---

## 12. Non-Functional Requirements

### 12.1 Performance

- STANDARD mode: < 2s per document
- Batch (300 docs): < 10 minutes
- Memory: < 500MB
- Parallel workers: 10 (configurable)

### 12.2 Reliability

- Graceful degradation on errors
- Timeout protection (30s per document)
- Cache corruption recovery
- Partial results on failures

### 12.3 Maintainability

- Modular architecture (6 independent components)
- Well-documented code
- Comprehensive tests (>= 15 unit + 5 integration)
- Consistent with ShellScriptAnalysisAgent patterns

### 12.4 Scalability

- Handles 1000+ documents
- Incremental analysis (SHA256 caching)
- Configurable parallelism
- Memory-efficient streaming

---

## 13. Testing Strategy

### 13.1 Unit Tests

- StructureAnalyzer: 3+ tests
- QualityAnalyzer: 3+ tests
- ConstitutionAnalyzer: 3+ tests
- TraceabilityAnalyzer: 2+ tests
- LinkValidator: 3+ tests
- ReportGenerator: 2+ tests

### 13.2 Integration Tests

- End-to-end analysis of sample docs
- Parallel processing validation
- Caching validation
- Report generation validation
- Domain classification validation

### 13.3 Performance Tests

- Batch analysis (100+ docs)
- Memory profiling
- Timeout handling
- Concurrent execution

**Target Coverage**: >= 90%

---

## 14. Deployment

### 14.1 Installation

```bash
# Install dependencies
pip install textstat mistune requests

# Verify installation
python -m scripts.coding.ai.agents.documentation.documentation_analysis_agent --version
```

### 14.2 Configuration

```yaml
# config/docs_analysis.yml
agent:
  mode: STANDARD
  workers: 10
  cache_enabled: true
  external_links: false

scoring:
  weights:
    structure: 0.25
    quality: 0.30
    constitution: 0.20
    traceability: 0.15
    links: 0.10

domains:
  backend:
    owner: Backend Team
    priority: P0
  frontend:
    owner: Frontend Team
    priority: P0
```

### 14.3 Monitoring

```python
# Metrics to track
- documents_analyzed_total
- average_score_by_domain
- critical_issues_count
- analysis_duration_seconds
- cache_hit_rate
```

---

## 15. Future Enhancements

### 15.1 Phase 3 (Optional)

- DEEP mode con LLM (quality assessment)
- Machine learning para detectar low-quality docs
- Automated fix suggestions (similar a ShellCheck --fix)
- Interactive remediation wizard
- Trend analysis over time

### 15.2 Integration Opportunities

- GitHub Actions auto-comments on PRs
- Slack notifications for critical issues
- Dashboard visualization (Grafana)
- IDE integration (VSCode extension)

---

## 16. Conclusion

Este High-Level Design define una arquitectura modular, escalable y mantenible para DocumentationAnalysisAgent, siguiendo los patrones exitosos de ShellScriptAnalysisAgent y cumpliendo con todos los requisitos funcionales y no funcionales definidos en FEATURE-DOCS-ANALYSIS-001.

**Next Steps**: Proceder a ADRs (Architectural Decision Records) para validar decisiones criticas con Self-Consistency.

---

**Trazabilidad**: FEATURE-DOCS-ANALYSIS-001
**Pattern**: ShellScriptAnalysisAgent-inspired
**Status**: Design Complete - Ready for ADRs
**Date**: 2025-11-13
