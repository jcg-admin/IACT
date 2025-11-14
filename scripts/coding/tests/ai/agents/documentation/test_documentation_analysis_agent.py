"""
Tests for DocumentationAnalysisAgent

Test-Driven Development (TDD) - RED Phase
These tests are written BEFORE implementation.

Coverage:
- Data models and enums
- StructureAnalyzer
- QualityAnalyzer
- ConstitutionAnalyzer
- TraceabilityAnalyzer
- LinkValidator
- ReportGenerator
- DocumentationAnalysisAgent main class
"""

import pytest
from pathlib import Path
import tempfile
import json

# Import components (will fail initially - expected in RED phase)
from scripts.coding.ai.agents.documentation.documentation_analysis_agent import (
    AnalysisMode,
    IssueSeverity,
    AnalysisIssue,
    StructureResult,
    QualityResult,
    ConstitutionResult,
    TraceabilityResult,
    LinkValidationResult,
    DocumentAnalysis,
    StructureAnalyzer,
    QualityAnalyzer,
    ConstitutionAnalyzer,
    TraceabilityAnalyzer,
    LinkValidator,
    ReportGenerator,
    DocumentationAnalysisAgent,
)


# ============================================================================
# TEST DATA
# ============================================================================

SAMPLE_GOOD_DOC = """# Good Documentation

## Introduction

This is a well-structured document with proper hierarchy.

## Content

The content is clear and concise. It follows best practices.

## Conclusion

This document demonstrates good documentation practices.
"""

SAMPLE_BAD_DOC = """## Missing H1

### Skipped H2

Bad hierarchy and structure.
"""

SAMPLE_DOC_WITH_EMOJIS = """# Document with Emojis

This document has emojis which violate Constitution Principle 2.

Status: All tests passing ✅
Feature complete 🎉
"""

SAMPLE_DOC_WITH_TRACEABILITY = """# Feature Documentation

**Issue**: FEATURE-DOCS-ANALYSIS-001
**ADR**: ADR-2025-001

This document has good traceability.
"""

SAMPLE_DOC_WITH_LINKS = """# Document with Links

Internal link: [Other Doc](./other.md)
External link: [Example](https://example.com)
Broken link: [Missing](./missing.md)
"""


# ============================================================================
# TEST ENUMS AND DATA MODELS
# ============================================================================

class TestAnalysisMode:
    """Test AnalysisMode enum"""

    def test_analysis_mode_values(self):
        """Test all analysis mode values exist"""
        assert AnalysisMode.QUICK.value == "QUICK"
        assert AnalysisMode.STANDARD.value == "STANDARD"
        assert AnalysisMode.DEEP.value == "DEEP"

    def test_analysis_mode_from_string(self):
        """Test creating mode from string"""
        mode = AnalysisMode("STANDARD")
        assert mode == AnalysisMode.STANDARD


class TestIssueSeverity:
    """Test IssueSeverity enum"""

    def test_severity_values(self):
        """Test all severity levels exist"""
        assert IssueSeverity.CRITICAL.value == "CRITICAL"
        assert IssueSeverity.HIGH.value == "HIGH"
        assert IssueSeverity.MEDIUM.value == "MEDIUM"
        assert IssueSeverity.LOW.value == "LOW"
        assert IssueSeverity.INFO.value == "INFO"


class TestAnalysisIssue:
    """Test AnalysisIssue dataclass"""

    def test_create_basic_issue(self):
        """Test creating basic issue"""
        issue = AnalysisIssue(
            type="structure",
            severity=IssueSeverity.HIGH,
            message="Missing H1 title"
        )
        assert issue.type == "structure"
        assert issue.severity == IssueSeverity.HIGH
        assert issue.message == "Missing H1 title"
        assert issue.line_number is None
        assert issue.recommendation is None

    def test_create_issue_with_all_fields(self):
        """Test creating issue with all fields"""
        issue = AnalysisIssue(
            type="quality",
            severity=IssueSeverity.MEDIUM,
            message="Low readability",
            line_number=42,
            recommendation="Simplify sentences"
        )
        assert issue.line_number == 42
        assert issue.recommendation == "Simplify sentences"


class TestStructureResult:
    """Test StructureResult dataclass"""

    def test_create_structure_result(self):
        """Test creating structure result"""
        result = StructureResult(
            score=85.0,
            has_h1=True,
            heading_hierarchy_valid=True,
            has_frontmatter=False,
            required_sections_present=["Introduction", "Content"]
        )
        assert result.score == 85.0
        assert result.has_h1 is True
        assert len(result.issues) == 0


# ============================================================================
# TEST STRUCTURE ANALYZER
# ============================================================================

class TestStructureAnalyzer:
    """Test StructureAnalyzer component"""

    def test_good_structure_high_score(self):
        """Test that good structure gets high score"""
        analyzer = StructureAnalyzer()
        result = analyzer.analyze(SAMPLE_GOOD_DOC, {"domain": "docs/backend"})

        assert result.score >= 80.0
        assert result.has_h1 is True
        assert result.heading_hierarchy_valid is True
        assert len(result.issues) <= 1  # May have frontmatter warning

    def test_missing_h1_detected(self):
        """Test that missing H1 is detected"""
        analyzer = StructureAnalyzer()
        result = analyzer.analyze(SAMPLE_BAD_DOC, {})

        assert result.has_h1 is False
        assert any(issue.message == "Missing H1 title" for issue in result.issues)
        assert result.score < 80.0

    def test_bad_hierarchy_detected(self):
        """Test that bad heading hierarchy is detected"""
        analyzer = StructureAnalyzer()
        result = analyzer.analyze(SAMPLE_BAD_DOC, {})

        assert result.heading_hierarchy_valid is False
        assert any("hierarchy" in issue.message.lower() for issue in result.issues)

    def test_frontmatter_detection(self):
        """Test frontmatter detection"""
        doc_with_frontmatter = """---
title: Test
date: 2025-11-13
---

# Document
"""
        analyzer = StructureAnalyzer()
        result = analyzer.analyze(doc_with_frontmatter, {})

        assert result.has_frontmatter is True


# ============================================================================
# TEST QUALITY ANALYZER
# ============================================================================

class TestQualityAnalyzer:
    """Test QualityAnalyzer component"""

    def test_quality_analysis_basic(self):
        """Test basic quality analysis"""
        analyzer = QualityAnalyzer()
        result = analyzer.analyze(SAMPLE_GOOD_DOC)

        assert 0 <= result.score <= 100
        assert 0 <= result.readability_score <= 100
        assert 0 <= result.completeness_score <= 1.0
        assert 0 <= result.formatting_score <= 1.0

    def test_readability_score_calculated(self):
        """Test readability score is calculated"""
        analyzer = QualityAnalyzer()
        result = analyzer.analyze(SAMPLE_GOOD_DOC)

        assert result.readability_score > 0
        assert "readability" in result.metrics

    def test_completeness_checks(self):
        """Test completeness checks"""
        analyzer = QualityAnalyzer()
        result = analyzer.analyze(SAMPLE_GOOD_DOC)

        # Has intro, content, conclusion
        assert result.completeness_score > 0.5

    def test_code_block_formatting_check(self):
        """Test code block formatting check"""
        doc_with_code = """# Test

```python
code here
```

```
no language identifier
```
"""
        analyzer = QualityAnalyzer()
        result = analyzer.analyze(doc_with_code)

        # Should detect missing language identifier
        assert any("code block" in issue.message.lower() for issue in result.issues)


# ============================================================================
# TEST CONSTITUTION ANALYZER
# ============================================================================

class TestConstitutionAnalyzer:
    """Test ConstitutionAnalyzer component"""

    def test_no_violations_clean_doc(self):
        """Test clean document has no violations"""
        constitution = {"principles": []}
        analyzer = ConstitutionAnalyzer(constitution)
        result = analyzer.analyze(SAMPLE_GOOD_DOC)

        assert result.score >= 90.0
        assert len(result.violations) == 0

    def test_emoji_detection(self):
        """Test emoji detection (Principle 2)"""
        constitution = {"principles": []}
        analyzer = ConstitutionAnalyzer(constitution)
        result = analyzer.analyze(SAMPLE_DOC_WITH_EMOJIS)

        assert result.score < 100.0
        assert any("emoji" in v.message.lower() for v in result.violations)
        assert 2 in result.applicable_principles

    def test_security_check_passwords(self):
        """Test security check detects passwords"""
        doc_with_password = """# Config

```python
password = "secret123"
```
"""
        constitution = {"principles": []}
        analyzer = ConstitutionAnalyzer(constitution)
        result = analyzer.analyze(doc_with_password)

        assert any("password" in v.message.lower() for v in result.violations)
        assert 7 in result.applicable_principles


# ============================================================================
# TEST TRACEABILITY ANALYZER
# ============================================================================

class TestTraceabilityAnalyzer:
    """Test TraceabilityAnalyzer component"""

    def test_finds_issue_links(self):
        """Test finding issue links"""
        analyzer = TraceabilityAnalyzer()
        result = analyzer.analyze(SAMPLE_DOC_WITH_TRACEABILITY)

        assert len(result.issue_links) > 0
        assert "FEATURE-DOCS-ANALYSIS-001" in result.issue_links
        assert result.score > 50.0

    def test_finds_adr_links(self):
        """Test finding ADR links"""
        analyzer = TraceabilityAnalyzer()
        result = analyzer.analyze(SAMPLE_DOC_WITH_TRACEABILITY)

        assert len(result.adr_links) > 0
        assert "ADR-2025-001" in result.adr_links

    def test_no_traceability_low_score(self):
        """Test document without traceability gets low score"""
        analyzer = TraceabilityAnalyzer()
        result = analyzer.analyze(SAMPLE_GOOD_DOC)

        assert result.score < 50.0
        assert any("issue link" in issue.message.lower() for issue in result.issues)


# ============================================================================
# TEST LINK VALIDATOR
# ============================================================================

class TestLinkValidator:
    """Test LinkValidator component"""

    def test_no_links_perfect_score(self):
        """Test document with no links gets perfect score"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            doc_path.write_text("# No Links\n\nJust text.")

            validator = LinkValidator(Path(tmpdir), check_external=False)
            result = validator.analyze(doc_path.read_text(), doc_path)

            assert result.score == 100.0
            assert result.total_links == 0

    def test_valid_internal_link(self):
        """Test valid internal link detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            other_path = Path(tmpdir) / "other.md"
            other_path.write_text("# Other")

            content = "[Other Doc](./other.md)"
            doc_path.write_text(content)

            validator = LinkValidator(Path(tmpdir), check_external=False)
            result = validator.analyze(content, doc_path)

            assert result.total_links == 1
            assert result.valid_links == 1
            assert len(result.broken_links) == 0
            assert result.score == 100.0

    def test_broken_internal_link(self):
        """Test broken internal link detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            content = "[Missing](./missing.md)"
            doc_path.write_text(content)

            validator = LinkValidator(Path(tmpdir), check_external=False)
            result = validator.analyze(content, doc_path)

            assert result.total_links == 1
            assert result.valid_links == 0
            assert len(result.broken_links) == 1
            assert "./missing.md" in result.broken_links
            assert result.score == 0.0

    def test_external_links_not_checked_by_default(self):
        """Test external links assumed valid when not checking"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            content = "[Example](https://example.com)"

            validator = LinkValidator(Path(tmpdir), check_external=False)
            result = validator.analyze(content, doc_path)

            assert result.total_links == 1
            assert result.valid_links == 1


# ============================================================================
# TEST REPORT GENERATOR
# ============================================================================

class TestReportGenerator:
    """Test ReportGenerator component"""

    def test_generate_markdown_report(self):
        """Test Markdown report generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample analysis
            analysis = DocumentAnalysis(
                file_path=Path("test.md"),
                domain="Backend",
                overall_score=85.5,
                structure=StructureResult(
                    score=90.0,
                    has_h1=True,
                    heading_hierarchy_valid=True,
                    has_frontmatter=False,
                    required_sections_present=[]
                ),
                quality=QualityResult(
                    score=80.0,
                    readability_score=70.0,
                    completeness_score=0.8,
                    formatting_score=0.9
                ),
                constitution=ConstitutionResult(
                    score=100.0,
                    violations=[],
                    applicable_principles=[2, 7]
                ),
                traceability=TraceabilityResult(
                    score=75.0,
                    issue_links=["FEATURE-001"],
                    adr_links=[],
                    spec_links=[]
                ),
                links=LinkValidationResult(
                    score=100.0,
                    total_links=2,
                    valid_links=2,
                    broken_links=[]
                ),
                analysis_time=1.23
            )

            generator = ReportGenerator()
            generator.generate_document_report(analysis, Path(tmpdir))

            # Check MD file created
            md_file = Path(tmpdir) / "test_analysis.md"
            assert md_file.exists()

            md_content = md_file.read_text()
            assert "Overall Score" in md_content
            assert "85.5" in md_content
            assert "Backend" in md_content

    def test_generate_json_report(self):
        """Test JSON report generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analysis = DocumentAnalysis(
                file_path=Path("test.md"),
                domain="Backend",
                overall_score=85.5,
                structure=StructureResult(
                    score=90.0,
                    has_h1=True,
                    heading_hierarchy_valid=True,
                    has_frontmatter=False,
                    required_sections_present=[]
                ),
                quality=QualityResult(
                    score=80.0,
                    readability_score=70.0,
                    completeness_score=0.8,
                    formatting_score=0.9
                ),
                constitution=ConstitutionResult(
                    score=100.0,
                    violations=[],
                    applicable_principles=[2, 7]
                ),
                traceability=TraceabilityResult(
                    score=75.0,
                    issue_links=["FEATURE-001"],
                    adr_links=[],
                    spec_links=[]
                ),
                links=LinkValidationResult(
                    score=100.0,
                    total_links=2,
                    valid_links=2,
                    broken_links=[]
                ),
                analysis_time=1.23
            )

            generator = ReportGenerator()
            generator.generate_document_report(analysis, Path(tmpdir))

            # Check JSON file created
            json_file = Path(tmpdir) / "test_analysis.json"
            assert json_file.exists()

            json_data = json.loads(json_file.read_text())
            assert json_data["overall_score"] == 85.5
            assert json_data["domain"] == "Backend"


# ============================================================================
# TEST MAIN AGENT
# ============================================================================

class TestDocumentationAnalysisAgent:
    """Test DocumentationAnalysisAgent main class"""

    def test_agent_initialization_default(self):
        """Test agent initialization with defaults"""
        agent = DocumentationAnalysisAgent()

        assert agent.name == "DocumentationAnalysisAgent"
        assert agent.mode == AnalysisMode.STANDARD
        assert agent.workers == 10
        assert agent.cache_enabled is True
        assert agent.external_links is False

    def test_agent_initialization_custom_config(self):
        """Test agent initialization with custom config"""
        config = {
            "mode": "QUICK",
            "workers": 5,
            "cache_enabled": False,
            "external_links": True
        }
        agent = DocumentationAnalysisAgent(config=config)

        assert agent.mode == AnalysisMode.QUICK
        assert agent.workers == 5
        assert agent.cache_enabled is False
        assert agent.external_links is True

    def test_domain_classification(self):
        """Test domain classification logic"""
        agent = DocumentationAnalysisAgent()

        assert agent._classify_domain(Path("docs/backend/api.md")) == "Backend"
        assert agent._classify_domain(Path("docs/frontend/ui.md")) == "Frontend"
        assert agent._classify_domain(Path("docs/agent/plan.md")) == "AI Agent"
        assert agent._classify_domain(Path("docs/other/file.md")) == "Other"

    def test_analyze_single_document(self):
        """Test analyzing single document"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            doc_path.write_text(SAMPLE_GOOD_DOC)

            agent = DocumentationAnalysisAgent(config={"cache_enabled": False})
            analysis = agent._analyze_document(doc_path)

            assert analysis.file_path == doc_path
            assert 0 <= analysis.overall_score <= 100
            assert analysis.analysis_time > 0

    def test_agent_run_success(self):
        """Test full agent run"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test documents
            doc1 = Path(tmpdir) / "doc1.md"
            doc1.write_text(SAMPLE_GOOD_DOC)

            doc2 = Path(tmpdir) / "doc2.md"
            doc2.write_text(SAMPLE_GOOD_DOC)

            output_dir = Path(tmpdir) / "reports"

            agent = DocumentationAnalysisAgent(config={
                "cache_enabled": False,
                "external_links": False
            })

            result = agent.run({
                "docs_path": tmpdir,
                "output_dir": str(output_dir)
            })

            assert result["status"] == "success"
            assert "summary" in result
            assert len(result["analyses"]) == 2

    def test_parallel_processing(self):
        """Test parallel document processing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple test documents
            for i in range(5):
                doc = Path(tmpdir) / f"doc{i}.md"
                doc.write_text(SAMPLE_GOOD_DOC)

            agent = DocumentationAnalysisAgent(config={
                "workers": 3,
                "cache_enabled": False
            })

            docs = list(Path(tmpdir).glob("*.md"))
            analyses = agent._analyze_documents_parallel(docs)

            assert len(analyses) == 5
            assert all(isinstance(a, DocumentAnalysis) for a in analyses)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDocumentationAnalysisIntegration:
    """Integration tests for full workflow"""

    def test_end_to_end_analysis(self):
        """Test complete end-to-end analysis workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup test directory structure
            docs_dir = Path(tmpdir) / "docs"
            docs_dir.mkdir()

            backend_dir = docs_dir / "backend"
            backend_dir.mkdir()

            # Create test docs
            (backend_dir / "api.md").write_text(SAMPLE_DOC_WITH_TRACEABILITY)
            (backend_dir / "guide.md").write_text(SAMPLE_GOOD_DOC)

            output_dir = Path(tmpdir) / "reports"

            # Run agent
            agent = DocumentationAnalysisAgent(config={
                "mode": "STANDARD",
                "cache_enabled": False,
                "external_links": False
            })

            result = agent.run({
                "docs_path": str(docs_dir),
                "output_dir": str(output_dir)
            })

            # Verify results
            assert result["status"] == "success"
            assert len(result["analyses"]) == 2

            # Verify reports generated
            assert output_dir.exists()
            report_files = list(output_dir.glob("*.md"))
            assert len(report_files) >= 2

    def test_caching_mechanism(self):
        """Test that caching works correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            doc_path.write_text(SAMPLE_GOOD_DOC)

            agent = DocumentationAnalysisAgent(config={
                "cache_enabled": True
            })

            # First analysis (cache miss)
            analysis1 = agent._analyze_document(doc_path)
            assert analysis1.cache_hit is False

            # Second analysis (should be cache hit if caching works)
            # Note: Actual cache hit depends on implementation
            analysis2 = agent._analyze_document(doc_path)
            assert analysis1.overall_score == analysis2.overall_score

    def test_error_handling_invalid_path(self):
        """Test error handling for invalid paths"""
        agent = DocumentationAnalysisAgent()

        with pytest.raises(Exception):
            agent.run({
                "docs_path": "/nonexistent/path",
                "output_dir": "/tmp/reports"
            })

    def test_multiple_domains_classification(self):
        """Test correct classification across multiple domains"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multi-domain structure
            docs_dir = Path(tmpdir) / "docs"
            (docs_dir / "backend").mkdir(parents=True)
            (docs_dir / "frontend").mkdir(parents=True)
            (docs_dir / "agent").mkdir(parents=True)

            (docs_dir / "backend" / "api.md").write_text(SAMPLE_GOOD_DOC)
            (docs_dir / "frontend" / "ui.md").write_text(SAMPLE_GOOD_DOC)
            (docs_dir / "agent" / "plan.md").write_text(SAMPLE_GOOD_DOC)

            agent = DocumentationAnalysisAgent(config={"cache_enabled": False})

            result = agent.run({
                "docs_path": str(docs_dir),
                "output_dir": str(Path(tmpdir) / "reports")
            })

            domains = {a["domain"] for a in result["analyses"]}
            assert "Backend" in domains
            assert "Frontend" in domains
            assert "AI Agent" in domains

    def test_constitution_violations_reported(self):
        """Test that constitution violations are properly reported"""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc_path = Path(tmpdir) / "test.md"
            doc_path.write_text(SAMPLE_DOC_WITH_EMOJIS)

            agent = DocumentationAnalysisAgent(config={"cache_enabled": False})
            analysis = agent._analyze_document(doc_path)

            # Should have violations
            assert len(analysis.constitution.violations) > 0
            assert analysis.constitution.score < 100.0
