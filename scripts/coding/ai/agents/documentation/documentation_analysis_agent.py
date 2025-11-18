"""
DocumentationAnalysisAgent - Comprehensive documentation quality analysis

Analyzes Markdown documentation across 5 dimensions:
1. Structure compliance (hierarchy, sections)
2. Quality metrics (readability, completeness, formatting)
3. Constitution compliance (no emojis, security)
4. Traceability (issue links, ADR links)
5. Link validation (internal, external)

**Issue**: FEATURE-DOCS-ANALYSIS-001
**Methodology**: TDD + Auto-CoT + Self-Consistency
**Pattern**: Based on ShellScriptAnalysisAgent
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import re
import time
import json
import hashlib
from statistics import mean

try:
    import textstat
except ImportError:
    textstat = None

try:
    import requests
except ImportError:
    requests = None

from scripts.coding.ai.shared.agent_base import Agent


# ============================================================================
# DATA MODELS
# ============================================================================

class AnalysisMode(Enum):
    """Analysis mode enumeration"""
    QUICK = "QUICK"
    STANDARD = "STANDARD"
    DEEP = "DEEP"


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class AnalysisIssue:
    """Single analysis issue"""
    type: str  # "structure", "quality", "constitution", "traceability", "link"
    severity: IssueSeverity
    message: str
    line_number: Optional[int] = None
    recommendation: Optional[str] = None


@dataclass
class StructureResult:
    """Structure analysis result"""
    score: float  # 0-100
    has_h1: bool
    heading_hierarchy_valid: bool
    has_frontmatter: bool
    required_sections_present: List[str]
    issues: List[AnalysisIssue] = field(default_factory=list)


@dataclass
class QualityResult:
    """Quality analysis result"""
    score: float  # 0-100
    readability_score: float  # Flesch-Kincaid
    completeness_score: float
    formatting_score: float
    metrics: Dict[str, Any] = field(default_factory=dict)
    issues: List[AnalysisIssue] = field(default_factory=list)


@dataclass
class ConstitutionResult:
    """Constitution compliance result"""
    score: float  # 0-100
    violations: List[AnalysisIssue] = field(default_factory=list)
    applicable_principles: List[int] = field(default_factory=list)


@dataclass
class TraceabilityResult:
    """Traceability analysis result"""
    score: float  # 0-100
    issue_links: List[str] = field(default_factory=list)
    adr_links: List[str] = field(default_factory=list)
    spec_links: List[str] = field(default_factory=list)
    issues: List[AnalysisIssue] = field(default_factory=list)


@dataclass
class LinkValidationResult:
    """Link validation result"""
    score: float  # 0-100
    total_links: int = 0
    valid_links: int = 0
    broken_links: List[str] = field(default_factory=list)
    issues: List[AnalysisIssue] = field(default_factory=list)


@dataclass
class DocumentAnalysis:
    """Complete document analysis"""
    file_path: Path
    domain: str
    overall_score: float
    structure: StructureResult
    quality: QualityResult
    constitution: ConstitutionResult
    traceability: TraceabilityResult
    links: LinkValidationResult
    analysis_time: float
    cache_hit: bool = False


@dataclass
class DomainSummary:
    """Domain-level summary"""
    domain: str
    owner: str
    priority: str
    doc_count: int
    average_score: float
    critical_issues: int
    top_issues: List[AnalysisIssue] = field(default_factory=list)


# ============================================================================
# STRUCTURE ANALYZER
# ============================================================================

class StructureAnalyzer:
    """Analyzes Markdown document structure"""

    def analyze(self, content: str, metadata: Dict[str, Any]) -> StructureResult:
        """
        Analyze document structure.

        Args:
            content: Raw Markdown content
            metadata: Document metadata (domain, required_sections, etc.)

        Returns:
            StructureResult with score and issues
        """
        issues = []

        # Check H1 title
        has_h1 = self._check_h1_title(content)
        if not has_h1:
            issues.append(AnalysisIssue(
                type="structure",
                severity=IssueSeverity.HIGH,
                message="Missing H1 title",
                recommendation="Add single H1 title at document top"
            ))

        # Check heading hierarchy
        hierarchy_valid = self._check_heading_hierarchy(content)
        if not hierarchy_valid:
            issues.append(AnalysisIssue(
                type="structure",
                severity=IssueSeverity.MEDIUM,
                message="Invalid heading hierarchy",
                recommendation="Ensure headings follow H1→H2→H3 order"
            ))

        # Check frontmatter (if required)
        domain = metadata.get("domain", "")
        has_frontmatter = self._check_frontmatter(content)
        if self._requires_frontmatter(domain) and not has_frontmatter:
            issues.append(AnalysisIssue(
                type="structure",
                severity=IssueSeverity.LOW,
                message="Missing frontmatter",
                recommendation="Add YAML frontmatter with metadata"
            ))

        # Check required sections
        required_sections = metadata.get("required_sections", [])
        present_sections = self._find_sections(content)

        # Calculate score
        score = self._calculate_structure_score(
            has_h1, hierarchy_valid, has_frontmatter, present_sections, required_sections
        )

        return StructureResult(
            score=score,
            has_h1=has_h1,
            heading_hierarchy_valid=hierarchy_valid,
            has_frontmatter=has_frontmatter,
            required_sections_present=present_sections,
            issues=issues
        )

    def _check_h1_title(self, content: str) -> bool:
        """Check for single H1 title at top"""
        h1_pattern = r'^#\s+.+$'
        h1_matches = re.findall(h1_pattern, content, re.MULTILINE)
        return len(h1_matches) == 1

    def _check_heading_hierarchy(self, content: str) -> bool:
        """Check heading hierarchy (no skips)"""
        heading_pattern = r'^(#{1,6})\s+.+$'
        headings = re.findall(heading_pattern, content, re.MULTILINE)

        prev_level = 0
        for heading in headings:
            level = len(heading)
            if level > prev_level + 1:
                return False  # Skip detected
            prev_level = level
        return True

    def _check_frontmatter(self, content: str) -> bool:
        """Check for YAML frontmatter"""
        frontmatter_pattern = r'^---\n.*?\n---'
        return bool(re.match(frontmatter_pattern, content, re.DOTALL))

    def _requires_frontmatter(self, domain: str) -> bool:
        """Check if domain requires frontmatter"""
        # Most domains don't strictly require it
        return False

    def _find_sections(self, content: str) -> List[str]:
        """Extract all section titles"""
        section_pattern = r'^##\s+(.+)$'
        return re.findall(section_pattern, content, re.MULTILINE)

    def _calculate_structure_score(
        self, has_h1: bool, hierarchy: bool, frontmatter: bool,
        present: List[str], required: List[str]
    ) -> float:
        """Calculate weighted structure score"""
        required_present = sum(1 for r in required if r in present) if required else 1
        required_total = len(required) if required else 1

        return (
            (1.0 if has_h1 else 0.0) * 0.20 +
            (1.0 if hierarchy else 0.0) * 0.25 +
            (1.0 if frontmatter else 0.5) * 0.15 +
            (required_present / required_total) * 0.30 +
            0.10  # Basic Markdown syntax (always passes for now)
        ) * 100


# ============================================================================
# QUALITY ANALYZER
# ============================================================================

class QualityAnalyzer:
    """Analyzes documentation quality metrics"""

    def analyze(self, content: str) -> QualityResult:
        """
        Analyze document quality.

        Args:
            content: Raw Markdown content

        Returns:
            QualityResult with scores and metrics
        """
        issues = []

        # Readability (Flesch-Kincaid)
        readability_score = self._calculate_readability(content)
        if readability_score < 40:
            issues.append(AnalysisIssue(
                type="quality",
                severity=IssueSeverity.MEDIUM,
                message=f"Low readability score: {readability_score:.1f}",
                recommendation="Simplify sentences, use shorter words"
            ))

        # Completeness
        completeness_score = self._check_completeness(content)

        # Formatting
        formatting_score = self._check_formatting(content, issues)

        # Overall quality score
        quality_score = (
            (readability_score / 100) * 0.30 +
            completeness_score * 0.25 +
            formatting_score * 0.45
        ) * 100

        return QualityResult(
            score=quality_score,
            readability_score=readability_score,
            completeness_score=completeness_score,
            formatting_score=formatting_score,
            metrics={
                "readability": readability_score,
                "completeness": completeness_score,
                "formatting": formatting_score
            },
            issues=issues
        )

    def _calculate_readability(self, content: str) -> float:
        """Calculate Flesch-Kincaid Reading Ease"""
        # Remove code blocks (don't affect readability)
        text = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        # Remove inline code
        text = re.sub(r'`[^`]+`', '', text)

        if textstat is None:
            return 50.0  # Default if textstat not available

        try:
            score = textstat.flesch_reading_ease(text)
            return max(0, min(100, score))  # Clamp to 0-100
        except Exception:
            return 50.0  # Default if calculation fails

    def _check_completeness(self, content: str) -> float:
        """Check document completeness"""
        has_intro = bool(re.search(r'##\s+(Introduction|Overview|About)', content, re.IGNORECASE))
        has_body = len(content) > 500  # Substantial content
        has_conclusion = bool(re.search(r'##\s+(Conclusion|Summary|Next Steps)', content, re.IGNORECASE))

        return (
            (1.0 if has_intro else 0.0) * 0.33 +
            (1.0 if has_body else 0.0) * 0.34 +
            (1.0 if has_conclusion else 0.0) * 0.33
        )

    def _check_formatting(self, content: str, issues: List[AnalysisIssue]) -> float:
        """Check Markdown formatting quality"""
        score = 1.0

        # Check code blocks have language identifiers
        code_blocks = re.findall(r'```(\w*)\n', content)
        unidentified = sum(1 for lang in code_blocks if not lang)
        if unidentified > 0:
            issues.append(AnalysisIssue(
                type="quality",
                severity=IssueSeverity.LOW,
                message=f"{unidentified} code blocks missing language identifier",
                recommendation="Add language: ```python, ```bash, etc."
            ))
            score -= 0.2

        # Check table formatting (basic)
        tables = re.findall(r'\|.*\|', content)
        if tables:
            malformed = [t for t in tables if not re.match(r'\|[\s\w\-]+\|', t)]
            if malformed:
                issues.append(AnalysisIssue(
                    type="quality",
                    severity=IssueSeverity.LOW,
                    message="Possibly malformed tables detected",
                    recommendation="Ensure tables have proper | separators"
                ))
                score -= 0.1

        return max(0, score)


# ============================================================================
# CONSTITUTION ANALYZER
# ============================================================================

class ConstitutionAnalyzer:
    """Analyzes Constitution principles compliance"""

    def __init__(self, constitution: Dict[str, Any]):
        self.constitution = constitution

    def analyze(self, content: str) -> ConstitutionResult:
        """
        Analyze Constitution compliance.

        Args:
            content: Raw Markdown content

        Returns:
            ConstitutionResult with score and violations
        """
        violations = []
        principle_scores = []
        applicable = []

        # Principle 2: No Emojis
        applicable.append(2)
        emoji_violations = self._check_emojis(content)
        if emoji_violations:
            violations.extend(emoji_violations)
            principle_scores.append(0.0)
        else:
            principle_scores.append(1.0)

        # Principle 7: Security (no secrets)
        applicable.append(7)
        security_violations = self._check_security(content)
        if security_violations:
            violations.extend(security_violations)
            principle_scores.append(0.0)
        else:
            principle_scores.append(1.0)

        # Calculate score
        score = (sum(principle_scores) / len(principle_scores)) * 100 if principle_scores else 100

        return ConstitutionResult(
            score=score,
            violations=violations,
            applicable_principles=applicable
        )

    def _check_emojis(self, content: str) -> List[AnalysisIssue]:
        """Check for emoji presence"""
        emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]'
        emojis = re.findall(emoji_pattern, content)

        if emojis:
            return [AnalysisIssue(
                type="constitution",
                severity=IssueSeverity.HIGH,
                message=f"Found {len(emojis)} emojis (Principle 2 violation)",
                recommendation="Remove all emojis from documentation"
            )]
        return []

    def _check_security(self, content: str) -> List[AnalysisIssue]:
        """Check for sensitive data exposure"""
        violations = []

        patterns = {
            "password": r'password\s*=\s*["\'].*["\']',
            "api_key": r'api_key\s*=\s*["\'].*["\']',
            "token": r'token\s*=\s*["\'].*["\']',
        }

        for name, pattern in patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                violations.append(AnalysisIssue(
                    type="constitution",
                    severity=IssueSeverity.CRITICAL,
                    message=f"Possible {name} exposure detected (Principle 7)",
                    recommendation=f"Remove {name}, use environment variables"
                ))

        return violations


# ============================================================================
# TRACEABILITY ANALYZER
# ============================================================================

class TraceabilityAnalyzer:
    """Analyzes traceability links"""

    def analyze(self, content: str) -> TraceabilityResult:
        """Analyze traceability links"""
        issues = []

        # Find issue links (handles multi-part like FEATURE-DOCS-ANALYSIS-001)
        issue_links = re.findall(r'(FEATURE-[\w-]+-\d+|BUG-[\w-]+-\d+|IMPROVEMENT-[\w-]+-\d+)', content)

        # Find ADR links
        adr_links = re.findall(r'ADR-\d{4}-\d{3}', content)

        # Find spec links (generic)
        spec_links = re.findall(r'\[.*?\]\(.*?/specs?/.*?\)', content)

        # Calculate score
        has_issues = len(issue_links) > 0
        has_adrs = len(adr_links) > 0
        has_specs = len(spec_links) > 0

        if not has_issues:
            issues.append(AnalysisIssue(
                type="traceability",
                severity=IssueSeverity.MEDIUM,
                message="No issue links found",
                recommendation="Add links to related issues (FEATURE-*, BUG-*, etc.)"
            ))

        score = (
            (1.0 if has_issues else 0.0) * 0.40 +
            (1.0 if has_adrs else 0.3) * 0.30 +
            (1.0 if has_specs else 0.3) * 0.20 +
            0.10  # Cross-refs (always partial credit)
        ) * 100

        return TraceabilityResult(
            score=score,
            issue_links=list(set(issue_links)),
            adr_links=list(set(adr_links)),
            spec_links=spec_links,
            issues=issues
        )


# ============================================================================
# LINK VALIDATOR
# ============================================================================

class LinkValidator:
    """Validates internal and external links"""

    def __init__(self, base_path: Path, check_external: bool = False):
        self.base_path = base_path
        self.check_external = check_external

    def analyze(self, content: str, doc_path: Path) -> LinkValidationResult:
        """Validate all links in document"""
        issues = []

        # Extract all links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)

        total = len(links)
        valid = 0
        broken = []

        for text, url in links:
            if url.startswith('http://') or url.startswith('https://'):
                # External link
                if self.check_external:
                    if self._check_external_link(url):
                        valid += 1
                    else:
                        broken.append(url)
                        issues.append(AnalysisIssue(
                            type="link",
                            severity=IssueSeverity.MEDIUM,
                            message=f"Broken external link: {url}",
                            recommendation="Update or remove broken link"
                        ))
                else:
                    valid += 1  # Assume valid if not checking
            else:
                # Internal link
                if self._check_internal_link(url, doc_path):
                    valid += 1
                else:
                    broken.append(url)
                    issues.append(AnalysisIssue(
                        type="link",
                        severity=IssueSeverity.HIGH,
                        message=f"Broken internal link: {url}",
                        recommendation="Fix path or create missing file"
                    ))

        score = (valid / total * 100) if total > 0 else 100

        return LinkValidationResult(
            score=score,
            total_links=total,
            valid_links=valid,
            broken_links=broken,
            issues=issues
        )

    def _check_internal_link(self, url: str, doc_path: Path) -> bool:
        """Check if internal link is valid"""
        # Remove anchor
        path = url.split('#')[0]
        if not path:
            return True  # Anchor only (assume valid)

        # Resolve relative to document
        target = (doc_path.parent / path).resolve()
        return target.exists()

    def _check_external_link(self, url: str) -> bool:
        """Check if external link is reachable"""
        if requests is None:
            return True  # Assume valid if requests not available

        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            return False


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """Generates analysis reports"""

    def generate_document_report(self, analysis: DocumentAnalysis, output_path: Path):
        """Generate per-document report (MD + JSON)"""
        # Generate Markdown
        md_content = self._generate_markdown_report(analysis)
        md_path = output_path / f"{analysis.file_path.stem}_analysis.md"
        md_path.write_text(md_content, encoding='utf-8')

        # Generate JSON
        json_content = self._generate_json_report(analysis)
        json_path = output_path / f"{analysis.file_path.stem}_analysis.json"
        json_path.write_text(json.dumps(json_content, indent=2), encoding='utf-8')

    def _generate_markdown_report(self, analysis: DocumentAnalysis) -> str:
        """Generate Markdown report"""
        return f"""# Analysis Report: {analysis.file_path.name}

**Domain**: {analysis.domain}
**Overall Score**: {analysis.overall_score:.1f}/100
**Analysis Time**: {analysis.analysis_time:.2f}s

## Scores

| Component | Score |
|-----------|-------|
| Structure | {analysis.structure.score:.1f}/100 |
| Quality | {analysis.quality.score:.1f}/100 |
| Constitution | {analysis.constitution.score:.1f}/100 |
| Traceability | {analysis.traceability.score:.1f}/100 |
| Links | {analysis.links.score:.1f}/100 |

## Issues

{self._format_issues(analysis)}

## Recommendations

{self._format_recommendations(analysis)}
"""

    def _format_issues(self, analysis: DocumentAnalysis) -> str:
        """Format all issues"""
        all_issues = (
            analysis.structure.issues +
            analysis.quality.issues +
            analysis.constitution.violations +
            analysis.traceability.issues +
            analysis.links.issues
        )

        if not all_issues:
            return "No issues found."

        lines = []
        for issue in sorted(all_issues, key=lambda x: x.severity.value):
            lines.append(f"- [{issue.severity.value}] {issue.message}")

        return "\n".join(lines)

    def _format_recommendations(self, analysis: DocumentAnalysis) -> str:
        """Format recommendations"""
        all_issues = (
            analysis.structure.issues +
            analysis.quality.issues +
            analysis.constitution.violations +
            analysis.traceability.issues +
            analysis.links.issues
        )

        recommendations = [issue.recommendation for issue in all_issues if issue.recommendation]

        if not recommendations:
            return "No specific recommendations."

        return "\n".join([f"- {rec}" for rec in recommendations])

    def _generate_json_report(self, analysis: DocumentAnalysis) -> Dict[str, Any]:
        """Generate JSON report"""
        data = asdict(analysis)
        # Convert non-serializable types (Path, Enum) to strings
        return self._make_json_serializable(data)

    def _make_json_serializable(self, obj: Any) -> Any:
        """Recursively convert non-JSON-serializable objects to serializable types"""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj


# ============================================================================
# MAIN AGENT
# ============================================================================

class DocumentationAnalysisAgent(Agent):
    """Main documentation analysis agent"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="DocumentationAnalysisAgent", config=config)

        self.mode = AnalysisMode(self.config.get("mode", "STANDARD"))
        self.workers = self.config.get("workers", 10)
        self.cache_enabled = self.config.get("cache_enabled", True)
        self.external_links = self.config.get("external_links", False)

        # Initialize components
        self.structure_analyzer = StructureAnalyzer()
        self.quality_analyzer = QualityAnalyzer()
        self.constitution_analyzer = ConstitutionAnalyzer(self.constitution)
        self.traceability_analyzer = TraceabilityAnalyzer()
        self.report_generator = ReportGenerator()

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation analysis"""
        docs_path = Path(input_data["docs_path"])
        output_dir = Path(input_data.get("output_dir", "docs_analysis_reports"))

        if not docs_path.exists():
            raise FileNotFoundError(f"Documentation path not found: {docs_path}")

        # Discover Markdown files
        docs = list(docs_path.rglob("*.md"))

        # Analyze documents (parallel)
        analyses = self._analyze_documents_parallel(docs)

        # Generate reports
        output_dir.mkdir(parents=True, exist_ok=True)
        for analysis in analyses:
            self.report_generator.generate_document_report(analysis, output_dir)

        # Calculate summary
        summary = self._calculate_summary(analyses)

        return {
            "status": "success",
            "summary": summary,
            "analyses": [asdict(a) for a in analyses]
        }

    def _analyze_documents_parallel(self, docs: List[Path]) -> List[DocumentAnalysis]:
        """Analyze documents in parallel"""
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = [executor.submit(self._analyze_document, doc) for doc in docs]
            return [f.result() for f in futures]

    def _analyze_document(self, doc_path: Path) -> DocumentAnalysis:
        """Analyze single document"""
        content = doc_path.read_text(encoding='utf-8')

        # Check cache
        if self.cache_enabled:
            cached = self._load_from_cache(doc_path, content)
            if cached:
                return cached

        # Analyze components
        start_time = time.time()

        domain = self._classify_domain(doc_path)
        metadata = {"domain": domain}

        structure = self.structure_analyzer.analyze(content, metadata)
        quality = self.quality_analyzer.analyze(content)
        constitution = self.constitution_analyzer.analyze(content)
        traceability = self.traceability_analyzer.analyze(content)

        link_validator = LinkValidator(doc_path.parent, self.external_links)
        links = link_validator.analyze(content, doc_path)

        # Calculate overall score
        overall_score = (
            structure.score * 0.25 +
            quality.score * 0.30 +
            constitution.score * 0.20 +
            traceability.score * 0.15 +
            links.score * 0.10
        )

        analysis_time = time.time() - start_time

        analysis = DocumentAnalysis(
            file_path=doc_path,
            domain=domain,
            overall_score=overall_score,
            structure=structure,
            quality=quality,
            constitution=constitution,
            traceability=traceability,
            links=links,
            analysis_time=analysis_time
        )

        # Save to cache
        if self.cache_enabled:
            self._save_to_cache(doc_path, content, analysis)

        return analysis

    def _classify_domain(self, doc_path: Path) -> str:
        """Classify document by domain"""
        path_str = str(doc_path)

        DOMAIN_MAPPING = {
            "docs/backend": "Backend",
            "docs/frontend": "Frontend",
            "docs/infrastructure": "Infrastructure",
            "docs/agent": "AI Agent",
            "docs/api": "API",
            "docs/scripts": "Scripts",
            "docs/gobernanza": "Governance",
            "docs/analisis": "Analysis",
        }

        for pattern, name in DOMAIN_MAPPING.items():
            if pattern in path_str:
                return name

        return "Other"

    def _load_from_cache(self, doc_path: Path, content: str) -> Optional[DocumentAnalysis]:
        """Load analysis from cache"""
        cache_key = hashlib.sha256(content.encode()).hexdigest()
        cache_file = Path(".cache") / "docs_analysis" / f"{cache_key}.json"

        if cache_file.exists():
            try:
                # For now, return None (cache deserialization not implemented)
                return None
            except Exception:
                return None
        return None

    def _save_to_cache(self, doc_path: Path, content: str, analysis: DocumentAnalysis):
        """Save analysis to cache"""
        cache_key = hashlib.sha256(content.encode()).hexdigest()
        cache_dir = Path(".cache") / "docs_analysis"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"{cache_key}.json"
        try:
            cache_file.write_text(json.dumps(asdict(analysis), default=str), encoding='utf-8')
        except Exception:
            pass  # Silent fail on cache save

    def _calculate_summary(self, analyses: List[DocumentAnalysis]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not analyses:
            return {
                "total_docs": 0,
                "average_score": 0.0,
                "domains": {}
            }

        scores = [a.overall_score for a in analyses]

        # Group by domain
        domains: Dict[str, List[DocumentAnalysis]] = {}
        for analysis in analyses:
            if analysis.domain not in domains:
                domains[analysis.domain] = []
            domains[analysis.domain].append(analysis)

        domain_summaries = {}
        for domain, domain_analyses in domains.items():
            domain_scores = [a.overall_score for a in domain_analyses]
            domain_summaries[domain] = {
                "count": len(domain_analyses),
                "average_score": mean(domain_scores)
            }

        return {
            "total_docs": len(analyses),
            "average_score": mean(scores),
            "domains": domain_summaries
        }
