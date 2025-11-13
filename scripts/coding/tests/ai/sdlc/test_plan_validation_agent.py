"""
Tests for PlanValidationAgent

TDD Approach: RED → GREEN → REFACTOR

Test Coverage:
- Data models
- Issue parser
- 5 Reasoning paths
- Consensus decision
- Report generation
- Agent execution
- Error handling

Target: >=90% coverage
"""

import pytest
import tempfile
from pathlib import Path
from dataclasses import asdict

# Import will fail initially (TDD RED phase) - expected
try:
    from scripts.coding.ai.sdlc.plan_validation_agent import (
        Decision,
        IssueDocument,
        ReasoningPathResult,
        ConsensusResult,
        ValidationResult,
        IssueDocumentParser,
        CompletenessChecker,
        TechnicalFeasibilityAnalyzer,
        TimelineEffortValidator,
        RiskAnalyzer,
        IntegrationValidator,
        ConsensusDecider,
        ValidationReportGenerator,
        SDLCPlanValidationAgent
    )
    IMPLEMENTATION_EXISTS = True
except ImportError:
    IMPLEMENTATION_EXISTS = False
    pytest.skip("Implementation not yet available (TDD RED phase)", allow_module_level=True)


# Test Data: Sample Issue Document
SAMPLE_ISSUE_CONTENT = """# Issue: DocumentationAnalysisAgent

**Issue ID**: FEATURE-DOCS-ANALYSIS-001
**Tipo**: Feature Request
**Prioridad**: P1
**Story Points**: 13
**Fecha Creacion**: 2025-11-13
**Estado**: PLANNING

---

## 1. Descripcion

Crear un agente de análisis exhaustivo de documentación Markdown.

## 2. Requisitos Funcionales

### RF-001: Análisis Multi-Dimensión
El agente DEBE analizar documentación en 4 dimensiones.

### RF-002: Scoring System
El agente DEBE asignar scores (0-100).

## 3. Requisitos No Funcionales

### RNF-001: Performance
- QUICK mode: < 0.5s por documento

### RNF-002: Escalabilidad
- Soportar análisis de 1000+ documentos

## 4. Acceptance Criteria

### AC-1: Componentes Implementados
- [x] DocumentationAnalysisAgent class
- [x] StructureAnalyzer component

### AC-2: Análisis Exhaustivo
El agente analiza CADA documento Markdown y genera reports.

### AC-3: Domain Organization
Resultados agrupados por dominio.

## 5. Dependencies

- Python 3.8+
- markdown library
- mistune for parsing

## 6. Risks and Mitigations

### Risk 1: External Link Checking Performance
**Impact**: HIGH
**Mitigation**: Make optional, implement rate limiting

### Risk 2: Large Documentation Base
**Impact**: MEDIUM
**Mitigation**: Parallel processing

## 7. Timeline

Phase 1: MVP (2 days)
Phase 2: Enhanced (2 days)
Phase 3: Optimizations (2 days)
Total: 6 days

## 8. Integration

Integrates with existing SDLC pipeline as new agent.

---

**Trazabilidad**: FEATURE-DOCS-ANALYSIS-001
"""

MINIMAL_ISSUE_CONTENT = """# Issue: Minimal Test Issue

**Issue ID**: TEST-MINIMAL-001
**Tipo**: Bug Fix
**Prioridad**: P2
**Story Points**: 3
**Fecha Creacion**: 2025-11-13
**Estado**: PLANNING

## Acceptance Criteria

1. Fix the bug
2. Add test
3. Deploy
"""


class TestDecisionEnum:
    """Test Decision enum"""

    def test_decision_values(self):
        """Test all decision enum values exist"""
        assert Decision.GO.value == "GO"
        assert Decision.GO_WITH_ADJUSTMENTS.value == "GO con ajustes"
        assert Decision.REVISE.value == "REVISE"
        assert Decision.NO_GO.value == "NO-GO"

    def test_numeric_values(self):
        """Test decision numeric mapping for consensus"""
        assert Decision.GO.numeric_value == 2
        assert Decision.GO_WITH_ADJUSTMENTS.numeric_value == 1
        assert Decision.REVISE.numeric_value == 0
        assert Decision.NO_GO.numeric_value == -1


class TestIssueDocument:
    """Test IssueDocument dataclass"""

    def test_create_issue_document(self):
        """Test creating IssueDocument"""
        issue = IssueDocument(
            issue_id="TEST-001",
            title="Test Issue",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING"
        )

        assert issue.issue_id == "TEST-001"
        assert issue.title == "Test Issue"
        assert issue.story_points == 8

    def test_to_dict(self):
        """Test converting IssueDocument to dict"""
        issue = IssueDocument(
            issue_id="TEST-001",
            title="Test",
            tipo="Feature",
            priority="P1",
            story_points=5,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            acceptance_criteria=["AC1", "AC2"]
        )

        data = issue.to_dict()
        assert data["issue_id"] == "TEST-001"
        assert data["acceptance_criteria"] == ["AC1", "AC2"]


class TestReasoningPathResult:
    """Test ReasoningPathResult dataclass"""

    def test_create_result(self):
        """Test creating ReasoningPathResult"""
        result = ReasoningPathResult(
            path_name="Test Path",
            path_number=1,
            decision=Decision.GO,
            confidence=0.85,
            findings=["Finding 1"],
            issues=["Issue 1"],
            suggestions=["Suggestion 1"]
        )

        assert result.path_name == "Test Path"
        assert result.confidence == 0.85
        assert result.decision == Decision.GO

    def test_to_dict(self):
        """Test converting result to dict"""
        result = ReasoningPathResult(
            path_name="Test",
            path_number=1,
            decision=Decision.GO,
            confidence=0.9
        )

        data = result.to_dict()
        assert data["decision"] == "GO"
        assert data["confidence"] == 0.9


class TestConsensusResult:
    """Test ConsensusResult dataclass"""

    def test_should_proceed_go(self):
        """Test should_proceed returns True for GO"""
        consensus = ConsensusResult(
            decision=Decision.GO,
            confidence=0.88,
            reasoning_results=[]
        )

        assert consensus.should_proceed() is True

    def test_should_proceed_go_with_adjustments(self):
        """Test should_proceed returns True for GO_WITH_ADJUSTMENTS"""
        consensus = ConsensusResult(
            decision=Decision.GO_WITH_ADJUSTMENTS,
            confidence=0.75,
            reasoning_results=[]
        )

        assert consensus.should_proceed() is True

    def test_should_proceed_revise(self):
        """Test should_proceed returns False for REVISE"""
        consensus = ConsensusResult(
            decision=Decision.REVISE,
            confidence=0.65,
            reasoning_results=[]
        )

        assert consensus.should_proceed() is False

    def test_should_proceed_no_go(self):
        """Test should_proceed returns False for NO_GO"""
        consensus = ConsensusResult(
            decision=Decision.NO_GO,
            confidence=0.40,
            reasoning_results=[]
        )

        assert consensus.should_proceed() is False


class TestIssueDocumentParser:
    """Test IssueDocumentParser"""

    def test_parse_full_issue(self, tmp_path):
        """Test parsing a complete issue document"""
        issue_file = tmp_path / "issue_test.md"
        issue_file.write_text(SAMPLE_ISSUE_CONTENT)

        issue = IssueDocumentParser.parse(str(issue_file))

        assert issue.issue_id == "FEATURE-DOCS-ANALYSIS-001"
        assert issue.title == "DocumentationAnalysisAgent"
        assert issue.tipo == "Feature Request"
        assert issue.priority == "P1"
        assert issue.story_points == 13
        assert issue.estado == "PLANNING"
        assert len(issue.acceptance_criteria) >= 3
        assert len(issue.functional_requirements) >= 2
        assert len(issue.non_functional_requirements) >= 2
        assert len(issue.dependencies) >= 3
        assert len(issue.risks) >= 2
        assert issue.timeline is not None

    def test_parse_minimal_issue(self, tmp_path):
        """Test parsing minimal issue"""
        issue_file = tmp_path / "issue_minimal.md"
        issue_file.write_text(MINIMAL_ISSUE_CONTENT)

        issue = IssueDocumentParser.parse(str(issue_file))

        assert issue.issue_id == "TEST-MINIMAL-001"
        assert issue.story_points == 3
        assert len(issue.acceptance_criteria) == 3

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file raises error"""
        with pytest.raises(FileNotFoundError):
            IssueDocumentParser.parse("/nonexistent/issue.md")


class TestCompletenessChecker:
    """Test CompletenessChecker reasoning path"""

    def test_complete_issue_gets_high_score(self):
        """Test complete issue gets GO decision"""
        issue = IssueDocument(
            issue_id="TEST-001",
            title="Complete Issue",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            acceptance_criteria=["AC1", "AC2", "AC3", "AC4"],
            functional_requirements=["RF1", "RF2"],
            non_functional_requirements=["RNF1", "RNF2"]
        )

        result = CompletenessChecker.analyze(issue)

        assert result.decision in [Decision.GO, Decision.GO_WITH_ADJUSTMENTS]
        assert result.confidence >= 0.80
        assert result.path_number == 1
        assert result.path_name == "Completeness Check"

    def test_incomplete_issue_gets_low_score(self):
        """Test incomplete issue gets REVISE decision"""
        issue = IssueDocument(
            issue_id="TEST-002",
            title="Incomplete",
            tipo="Feature",
            priority="P1",
            story_points=None,  # Missing
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            acceptance_criteria=[],  # Empty
            functional_requirements=[],  # Empty
            non_functional_requirements=[]  # Empty
        )

        result = CompletenessChecker.analyze(issue)

        assert result.decision in [Decision.REVISE, Decision.GO_WITH_ADJUSTMENTS]
        assert result.confidence < 0.90
        assert len(result.issues) > 0
        assert len(result.suggestions) > 0


class TestTechnicalFeasibilityAnalyzer:
    """Test TechnicalFeasibilityAnalyzer reasoning path"""

    def test_issue_with_dependencies(self):
        """Test issue with documented dependencies"""
        issue = IssueDocument(
            issue_id="TEST-003",
            title="Technical Issue",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            dependencies=["Python 3.8+", "FastAPI", "PostgreSQL"],
            raw_content="Integration with API using FastAPI framework and PostgreSQL database"
        )

        result = TechnicalFeasibilityAnalyzer.analyze(issue)

        assert result.path_number == 2
        assert result.path_name == "Technical Feasibility"
        assert result.confidence >= 0.60
        assert any("dependencies documented" in f.lower() for f in result.findings)

    def test_issue_without_technical_details(self):
        """Test issue lacking technical details"""
        issue = IssueDocument(
            issue_id="TEST-004",
            title="Vague Issue",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            dependencies=[],
            raw_content="Make it work better"
        )

        result = TechnicalFeasibilityAnalyzer.analyze(issue)

        assert result.confidence < 0.85
        assert len(result.issues) > 0 or len(result.suggestions) > 0


class TestTimelineEffortValidator:
    """Test TimelineEffortValidator reasoning path"""

    def test_reasonable_story_points(self):
        """Test reasonable story points get good score"""
        issue = IssueDocument(
            issue_id="TEST-005",
            title="Reasonable Effort",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            acceptance_criteria=["AC1", "AC2", "AC3", "AC4"],
            timeline="Phase 1: 2 days, Phase 2: 2 days, Total: 4 days"
        )

        result = TimelineEffortValidator.analyze(issue)

        assert result.path_number == 3
        assert result.path_name == "Timeline & Effort"
        assert result.confidence >= 0.70

    def test_missing_story_points(self):
        """Test missing story points flagged"""
        issue = IssueDocument(
            issue_id="TEST-006",
            title="No Effort",
            tipo="Feature",
            priority="P1",
            story_points=None,  # Missing
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            acceptance_criteria=["AC1", "AC2"]
        )

        result = TimelineEffortValidator.analyze(issue)

        assert any("story points not defined" in i.lower() for i in result.issues)

    def test_excessive_story_points(self):
        """Test excessive story points (>21) flagged"""
        issue = IssueDocument(
            issue_id="TEST-007",
            title="Too Large",
            tipo="Feature",
            priority="P1",
            story_points=34,  # Too high
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            acceptance_criteria=["AC1", "AC2"]
        )

        result = TimelineEffortValidator.analyze(issue)

        assert any("story points very high" in i.lower() or "breaking down" in s.lower()
                  for i in result.issues for s in result.suggestions)


class TestRiskAnalyzer:
    """Test RiskAnalyzer reasoning path"""

    def test_risks_documented(self):
        """Test issue with documented risks"""
        issue = IssueDocument(
            issue_id="TEST-008",
            title="Risky Project",
            tipo="Feature",
            priority="P1",
            story_points=13,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            risks=["Risk 1: Performance", "Risk 2: Security", "Risk 3: Integration"],
            raw_content="Mitigation: implement caching for performance. Mitigation: use HTTPS for security."
        )

        result = RiskAnalyzer.analyze(issue)

        assert result.path_number == 4
        assert result.path_name == "Risk Analysis"
        assert result.confidence >= 0.75
        assert any("risks identified" in f.lower() for f in result.findings)

    def test_no_risks_documented(self):
        """Test issue without risks flagged"""
        issue = IssueDocument(
            issue_id="TEST-009",
            title="Naive Project",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            risks=[],
            raw_content="Simple feature with no problems"
        )

        result = RiskAnalyzer.analyze(issue)

        assert result.confidence < 0.85
        assert len(result.issues) > 0 or len(result.suggestions) > 0


class TestIntegrationValidator:
    """Test IntegrationValidator reasoning path"""

    def test_integration_documented(self):
        """Test issue with integration strategy"""
        issue = IssueDocument(
            issue_id="TEST-010",
            title="Integrated Feature",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            raw_content="""
            Integration with SDLCOrchestrator as Phase 1.5.
            Backward compatible with existing pipeline.
            Related to FEATURE-SHELL-ANALYSIS-001.
            """
        )

        result = IntegrationValidator.analyze(issue)

        assert result.path_number == 5
        assert result.path_name == "Integration & Dependencies"
        assert result.confidence >= 0.75

    def test_no_integration_details(self):
        """Test issue without integration details"""
        issue = IssueDocument(
            issue_id="TEST-011",
            title="Isolated Feature",
            tipo="Feature",
            priority="P1",
            story_points=5,
            fecha_creacion="2025-11-13",
            estado="PLANNING",
            raw_content="Standalone feature"
        )

        result = IntegrationValidator.analyze(issue)

        assert result.confidence < 0.90
        assert len(result.suggestions) > 0


class TestConsensusDecider:
    """Test ConsensusDecider"""

    def test_all_go_decisions(self):
        """Test consensus with all GO decisions"""
        results = [
            ReasoningPathResult("Path1", 1, Decision.GO, 0.90),
            ReasoningPathResult("Path2", 2, Decision.GO, 0.88),
            ReasoningPathResult("Path3", 3, Decision.GO, 0.92),
            ReasoningPathResult("Path4", 4, Decision.GO, 0.85),
            ReasoningPathResult("Path5", 5, Decision.GO, 0.87)
        ]

        consensus = ConsensusDecider.decide(results, threshold=0.80)

        assert consensus.decision == Decision.GO
        assert consensus.confidence >= 0.85
        assert len(consensus.reasoning_results) == 5

    def test_mixed_decisions_above_threshold(self):
        """Test consensus with mixed decisions, avg >= threshold"""
        results = [
            ReasoningPathResult("Path1", 1, Decision.GO, 0.90),
            ReasoningPathResult("Path2", 2, Decision.GO, 0.85),
            ReasoningPathResult("Path3", 3, Decision.GO_WITH_ADJUSTMENTS, 0.75),
            ReasoningPathResult("Path4", 4, Decision.GO, 0.88),
            ReasoningPathResult("Path5", 5, Decision.GO, 0.82)
        ]

        consensus = ConsensusDecider.decide(results, threshold=0.80)

        assert consensus.decision in [Decision.GO, Decision.GO_WITH_ADJUSTMENTS]
        assert consensus.confidence >= 0.80

    def test_mostly_revise_decisions(self):
        """Test consensus with mostly REVISE decisions"""
        results = [
            ReasoningPathResult("Path1", 1, Decision.REVISE, 0.60),
            ReasoningPathResult("Path2", 2, Decision.REVISE, 0.65),
            ReasoningPathResult("Path3", 3, Decision.GO_WITH_ADJUSTMENTS, 0.72),
            ReasoningPathResult("Path4", 4, Decision.REVISE, 0.58),
            ReasoningPathResult("Path5", 5, Decision.REVISE, 0.62)
        ]

        consensus = ConsensusDecider.decide(results, threshold=0.80)

        assert consensus.decision in [Decision.REVISE, Decision.GO_WITH_ADJUSTMENTS]
        assert consensus.confidence < 0.75

    def test_no_go_decision(self):
        """Test consensus with NO_GO decisions"""
        results = [
            ReasoningPathResult("Path1", 1, Decision.NO_GO, 0.30),
            ReasoningPathResult("Path2", 2, Decision.REVISE, 0.45),
            ReasoningPathResult("Path3", 3, Decision.NO_GO, 0.35),
            ReasoningPathResult("Path4", 4, Decision.REVISE, 0.50),
            ReasoningPathResult("Path5", 5, Decision.NO_GO, 0.40)
        ]

        consensus = ConsensusDecider.decide(results, threshold=0.80)

        assert consensus.decision in [Decision.NO_GO, Decision.REVISE]
        assert consensus.confidence < 0.60

    def test_empty_results_raises_error(self):
        """Test consensus with empty results raises ValueError"""
        with pytest.raises(ValueError, match="Cannot make consensus with no results"):
            ConsensusDecider.decide([], threshold=0.80)

    def test_aggregates_suggestions(self):
        """Test consensus aggregates unique suggestions"""
        results = [
            ReasoningPathResult("Path1", 1, Decision.GO_WITH_ADJUSTMENTS, 0.75,
                              suggestions=["Add tests", "Update docs"]),
            ReasoningPathResult("Path2", 2, Decision.GO, 0.85,
                              suggestions=["Add tests", "Consider edge cases"]),
            ReasoningPathResult("Path3", 3, Decision.GO, 0.90,
                              suggestions=["Update docs"])
        ]

        consensus = ConsensusDecider.decide(results, threshold=0.80)

        assert len(consensus.recommended_adjustments) >= 2
        # Should deduplicate "Add tests" and "Update docs"


class TestValidationReportGenerator:
    """Test ValidationReportGenerator"""

    def test_generate_report(self, tmp_path):
        """Test generating validation report"""
        issue = IssueDocument(
            issue_id="TEST-REPORT-001",
            title="Test Report",
            tipo="Feature",
            priority="P1",
            story_points=8,
            fecha_creacion="2025-11-13",
            estado="PLANNING"
        )

        results = [
            ReasoningPathResult("Completeness", 1, Decision.GO, 0.90,
                              findings=["All ACs defined"], issues=[], suggestions=[]),
            ReasoningPathResult("Technical", 2, Decision.GO, 0.85,
                              findings=["Dependencies clear"], issues=[], suggestions=[]),
            ReasoningPathResult("Timeline", 3, Decision.GO_WITH_ADJUSTMENTS, 0.75,
                              findings=[], issues=["Timeline vague"],
                              suggestions=["Add detailed timeline"]),
            ReasoningPathResult("Risks", 4, Decision.GO, 0.88,
                              findings=["Risks identified"], issues=[], suggestions=[]),
            ReasoningPathResult("Integration", 5, Decision.GO, 0.87,
                              findings=["Integration clear"], issues=[], suggestions=[])
        ]

        consensus = ConsensusResult(
            decision=Decision.GO,
            confidence=0.85,
            reasoning_results=results,
            recommended_adjustments=["Add detailed timeline"]
        )

        report_path = ValidationReportGenerator.generate(consensus, issue, str(tmp_path))

        assert Path(report_path).exists()
        content = Path(report_path).read_text()

        # Verify content
        assert "TEST-REPORT-001" in content
        assert "Test Report" in content
        assert "Self-Consistency" in content
        assert "Completeness" in content
        assert "Technical" in content
        assert "GO" in content
        assert "85%" in content
        assert "Add detailed timeline" in content


class TestSDLCPlanValidationAgent:
    """Test SDLCPlanValidationAgent (full integration)"""

    def test_agent_initialization(self):
        """Test agent initializes correctly"""
        agent = SDLCPlanValidationAgent()

        assert agent.name == "SDLCPlanValidationAgent"
        assert agent.phase == "planning_validation"
        assert agent.n_reasoning_paths == 5
        assert agent.confidence_threshold == 0.80

    def test_agent_custom_config(self):
        """Test agent with custom configuration"""
        agent = SDLCPlanValidationAgent(config={
            "n_reasoning_paths": 5,
            "confidence_threshold": 0.75,
            "parallel_execution": True
        })

        assert agent.n_reasoning_paths == 5
        assert agent.confidence_threshold == 0.75
        assert agent.parallel_execution is True

    def test_agent_execute_with_valid_issue(self, tmp_path):
        """Test agent execution with valid issue"""
        issue_file = tmp_path / "issue_valid.md"
        issue_file.write_text(SAMPLE_ISSUE_CONTENT)

        agent = SDLCPlanValidationAgent(config={
            "confidence_threshold": 0.70  # Lower threshold for test
        })

        result_data = agent.run({"issue_document": str(issue_file)})

        assert "decision" in result_data
        assert "confidence" in result_data
        assert "recommended_adjustments" in result_data
        assert "validation_report" in result_data
        assert "issue_document" in result_data

        assert result_data["decision"] in ["GO", "GO con ajustes", "REVISE", "NO-GO"]
        assert 0.0 <= result_data["confidence"] <= 1.0
        assert Path(result_data["validation_report"]).exists()

    def test_agent_execute_missing_issue_path(self):
        """Test agent execution without issue_document raises error"""
        agent = SDLCPlanValidationAgent()

        with pytest.raises(ValueError, match="Missing required input: issue_document"):
            agent.run({})

    def test_agent_execute_nonexistent_file(self):
        """Test agent execution with nonexistent file raises error"""
        agent = SDLCPlanValidationAgent()

        with pytest.raises(FileNotFoundError):
            agent.run({"issue_document": "/nonexistent/issue.md"})


# Run pytest if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
