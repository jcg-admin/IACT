"""
PlanValidationAgent - SDLC Phase 1.5: Plan Validation

Validates issue documents from Phase 1 (Planning) using Self-Consistency
with 5 independent reasoning paths before proceeding to Phase 2 (Feasibility).

Reasoning Paths:
1. Completeness Check
2. Technical Feasibility
3. Timeline & Effort
4. Risk Analysis
5. Integration & Dependencies

Trazabilidad: IMPROVEMENT-SDLC-VALIDATION-001
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import time
import logging
import re
from statistics import mean
import sys

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

from scripts.coding.ai.sdlc.base_agent import SDLCAgent  # noqa: E402

logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class Decision(Enum):
    """Validation decision types"""
    GO = "GO"
    GO_WITH_ADJUSTMENTS = "GO con ajustes"
    REVISE = "REVISE"
    NO_GO = "NO-GO"

    @property
    def numeric_value(self) -> int:
        """Map decision to numeric value for consensus calculation"""
        mapping = {
            Decision.GO: 2,
            Decision.GO_WITH_ADJUSTMENTS: 1,
            Decision.REVISE: 0,
            Decision.NO_GO: -1
        }
        return mapping[self]


@dataclass
class IssueDocument:
    """Parsed issue document structure"""
    issue_id: str
    title: str
    tipo: str
    priority: str
    story_points: Optional[int]
    fecha_creacion: str
    estado: str
    acceptance_criteria: List[str] = field(default_factory=list)
    functional_requirements: List[str] = field(default_factory=list)
    non_functional_requirements: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    timeline: Optional[str] = None
    raw_content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReasoningPathResult:
    """Result from a single reasoning path"""
    path_name: str
    path_number: int
    decision: Decision
    confidence: float
    findings: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['decision'] = self.decision.value
        return data


@dataclass
class ConsensusResult:
    """Final consensus decision from all reasoning paths"""
    decision: Decision
    confidence: float
    reasoning_results: List[ReasoningPathResult]
    recommended_adjustments: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def should_proceed(self) -> bool:
        """Should we proceed to Phase 2 (Feasibility)?"""
        return self.decision in [Decision.GO, Decision.GO_WITH_ADJUSTMENTS]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "confidence": self.confidence,
            "reasoning_results": [r.to_dict() for r in self.reasoning_results],
            "recommended_adjustments": self.recommended_adjustments,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }


@dataclass
class ValidationResult:
    """Final output from PlanValidationAgent"""
    consensus: ConsensusResult
    validation_report_path: str
    issue_document_path: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.consensus.decision.value,
            "confidence": self.consensus.confidence,
            "recommended_adjustments": self.consensus.recommended_adjustments,
            "validation_report": self.validation_report_path,
            "issue_document": self.issue_document_path,
            "timestamp": self.timestamp
        }


# ============================================================================
# Issue Document Parser
# ============================================================================

class IssueDocumentParser:
    """Parse issue_*.md files into IssueDocument dataclass"""

    @staticmethod
    def parse(file_path: str) -> IssueDocument:
        """
        Parse issue document from Markdown file

        Args:
            file_path: Path to issue_*.md file

        Returns:
            IssueDocument with parsed content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If parsing fails
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Issue document not found: {file_path}")

        content = path.read_text(encoding='utf-8')

        # Extract metadata from header
        issue_id = IssueDocumentParser._extract_field(content, r'\*\*Issue ID\*\*:\s*([^\n]+)')
        title = IssueDocumentParser._extract_field(content, r'^#\s+Issue:\s+(.+)$', multiline=True)
        tipo = IssueDocumentParser._extract_field(content, r'\*\*Tipo\*\*:\s*([^\n]+)')
        priority = IssueDocumentParser._extract_field(content, r'\*\*Prioridad\*\*:\s*([^\n]+)')
        story_points_str = IssueDocumentParser._extract_field(content, r'\*\*Story Points\*\*:\s*(\d+)')
        story_points = int(story_points_str) if story_points_str else None
        fecha_creacion = IssueDocumentParser._extract_field(content, r'\*\*Fecha Creaci[oó]n\*\*:\s*([^\n]+)')
        estado = IssueDocumentParser._extract_field(content, r'\*\*Estado\*\*:\s*([^\n]+)')

        # Extract acceptance criteria (special handling)
        acceptance_criteria = IssueDocumentParser._extract_acceptance_criteria(content)

        # Extract functional requirements
        functional_requirements = IssueDocumentParser._extract_requirements(content, 'RF')

        # Extract non-functional requirements
        non_functional_requirements = IssueDocumentParser._extract_requirements(content, 'RNF')

        # Extract dependencies
        dependencies = IssueDocumentParser._extract_list_items(
            content,
            r'##\s+\d+\.\s+Dependencies(.*?)(?=##|\Z)'
        )

        # Extract risks (special handling)
        risks = IssueDocumentParser._extract_risks(content)

        # Extract timeline
        timeline = IssueDocumentParser._extract_field(
            content,
            r'##\s+\d+\.\s+Timeline.*?\n\n(.*?)(?=##|\Z)',
            re.DOTALL
        )

        return IssueDocument(
            issue_id=issue_id or "UNKNOWN",
            title=title or "Untitled",
            tipo=tipo or "UNKNOWN",
            priority=priority or "P2",
            story_points=story_points,
            fecha_creacion=fecha_creacion or "UNKNOWN",
            estado=estado or "UNKNOWN",
            acceptance_criteria=acceptance_criteria,
            functional_requirements=functional_requirements,
            non_functional_requirements=non_functional_requirements,
            dependencies=dependencies,
            risks=risks,
            timeline=timeline,
            raw_content=content,
            metadata={
                "file_path": str(path),
                "file_size": len(content)
            }
        )

    @staticmethod
    def _extract_field(content: str, pattern: str, flags: int = 0, multiline: bool = False) -> Optional[str]:
        """Extract single field using regex"""
        if multiline:
            flags |= re.MULTILINE
        match = re.search(pattern, content, flags)
        return match.group(1).strip() if match else None

    @staticmethod
    def _extract_acceptance_criteria(content: str) -> List[str]:
        """Extract acceptance criteria - handles both AC-X: subsections and numbered lists"""
        # First, try to find AC-X: subsections
        ac_pattern = r'###\s+(AC-\d+:[^\n]*)'
        ac_matches = re.findall(ac_pattern, content)
        if ac_matches:
            return [ac.strip() for ac in ac_matches]

        # Fall back to finding numbered list in Acceptance Criteria section
        section_pattern = r'##\s+(?:\d+\.\s+)?Acceptance Criteria\s*\n+(.*?)(?=\n##|\Z)'
        section_match = re.search(section_pattern, content, re.DOTALL)
        if section_match:
            section_text = section_match.group(1)
            # Extract numbered items
            items = []
            for line in section_text.split('\n'):
                line = line.strip()
                if re.match(r'^(\d+\.|-|\*)\s+', line):
                    item = re.sub(r'^(\d+\.|-|\*)\s+', '', line)
                    items.append(item.strip())
            if items:
                return items

        return []

    @staticmethod
    def _extract_requirements(content: str, req_type: str) -> List[str]:
        """Extract requirements (RF or RNF) from document"""
        # Pattern to match ### RF-XXX: or ### RNF-XXX:
        req_pattern = rf'###\s+{req_type}-\d+:\s*([^\n]+)'
        req_matches = re.findall(req_pattern, content)
        return [req.strip() for req in req_matches]

    @staticmethod
    def _extract_risks(content: str) -> List[str]:
        """Extract risks - handles ### Risk X: format"""
        # Pattern to match ### Risk 1:, ### Risk 2:, etc.
        risk_pattern = r'###\s+Risk\s+\d+:\s*([^\n]+)'
        risk_matches = re.findall(risk_pattern, content)
        if risk_matches:
            return [risk.strip() for risk in risk_matches]

        # Fall back to generic list extraction
        return IssueDocumentParser._extract_list_items(
            content,
            r'##\s+\d+\.\s+Risks(.*?)(?=##|\Z)'
        )

    @staticmethod
    def _extract_list_items(content: str, section_pattern: str, item_pattern: str = None) -> List[str]:
        """Extract list items from a section"""
        section_match = re.search(section_pattern, content, re.DOTALL)
        if not section_match:
            return []

        section_text = section_match.group(1) if section_match.lastindex and section_match.lastindex >= 1 else section_match.group(0)

        # Extract numbered or bulleted list items
        if item_pattern:
            items = re.split(item_pattern, section_text)
            items = [item.strip() for item in items if item.strip()]
        else:
            # Default: extract lines starting with - or numbers, OR AC-X: subsections
            items = []

            # First, try to extract AC-X: subsections
            ac_pattern = r'###\s+(AC-\d+:.*?)(?=###|$)'
            ac_matches = re.findall(ac_pattern, section_text, re.DOTALL)
            if ac_matches:
                for ac_match in ac_matches:
                    # Extract AC title
                    ac_title = ac_match.split('\n')[0].strip()
                    items.append(ac_title)
            else:
                # Fall back to regular list extraction
                lines = section_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'^(-|\d+\.|\*)\s+', line):
                        # Remove bullet/number
                        item = re.sub(r'^(-|\d+\.|\*)\s+', '', line)
                        # Remove checkbox markers
                        item = re.sub(r'^\[.\]\s+', '', item)
                        items.append(item.strip())

        return items


# ============================================================================
# Reasoning Paths
# ============================================================================

class CompletenessChecker:
    """
    Reasoning Path 1: Completeness Check

    Validates completeness and clarity of issue document
    """

    @staticmethod
    def analyze(issue: IssueDocument) -> ReasoningPathResult:
        """Analyze issue document completeness"""
        start_time = time.time()

        findings = []
        issues = []
        suggestions = []

        # Check 1: Acceptance Criteria
        if not issue.acceptance_criteria:
            issues.append("No acceptance criteria defined")
            suggestions.append("Add at least 3 acceptance criteria")
        elif len(issue.acceptance_criteria) < 3:
            issues.append(f"Too few acceptance criteria ({len(issue.acceptance_criteria)}, recommended: >=3)")
            suggestions.append("Add more acceptance criteria to cover all functional aspects")
        else:
            findings.append(f"{len(issue.acceptance_criteria)} acceptance criteria defined")

        # Check 2: Story Points
        if issue.story_points is None:
            issues.append("Story points not defined")
            suggestions.append("Estimate story points for effort planning")
        elif issue.story_points <= 0:
            issues.append(f"Invalid story points: {issue.story_points}")
        else:
            findings.append(f"Story points defined: {issue.story_points}")

        # Check 3: Requirements
        if not issue.functional_requirements:
            issues.append("No functional requirements (RF-*) defined")
            suggestions.append("Add functional requirements section")
        else:
            findings.append(f"{len(issue.functional_requirements)} functional requirements")

        if not issue.non_functional_requirements:
            issues.append("No non-functional requirements (RNF-*) defined")
            suggestions.append("Add non-functional requirements (performance, security, etc.)")
        else:
            findings.append(f"{len(issue.non_functional_requirements)} non-functional requirements")

        # Check 4: Basic Metadata
        if issue.priority not in ["P0", "P1", "P2", "P3"]:
            issues.append(f"Invalid priority: {issue.priority}")
        else:
            findings.append(f"Priority set: {issue.priority}")

        if issue.issue_id == "UNKNOWN":
            issues.append("Issue ID not found")
        else:
            findings.append(f"Issue ID: {issue.issue_id}")

        # Check 5: SMART Criteria (simplified)
        smart_issues = CompletenessChecker._check_smart_criteria(issue)
        issues.extend(smart_issues)

        # Calculate score
        total_checks = 10
        passed_checks = total_checks - len(issues)
        score = max(0.0, min(1.0, passed_checks / total_checks))

        # Determine decision
        if score >= 0.90:
            decision = Decision.GO
        elif score >= 0.70:
            decision = Decision.GO_WITH_ADJUSTMENTS
        else:
            decision = Decision.REVISE

        execution_time = time.time() - start_time

        return ReasoningPathResult(
            path_name="Completeness Check",
            path_number=1,
            decision=decision,
            confidence=score,
            findings=findings,
            issues=issues,
            suggestions=suggestions,
            execution_time=execution_time
        )

    @staticmethod
    def _check_smart_criteria(issue: IssueDocument) -> List[str]:
        """Check if acceptance criteria meet SMART criteria (simplified)"""
        issues = []

        for i, ac in enumerate(issue.acceptance_criteria, 1):
            ac_lower = ac.lower()

            # Specific: Contains action verbs (only flag if also very short)
            has_action_verb = any(verb in ac_lower for verb in ['implement', 'create', 'generate', 'validate', 'support', 'analyze'])

            # Measurable: Too short to be measurable
            if len(ac) < 10:
                if not has_action_verb:
                    issues.append(f"AC{i} may not be specific enough (very short and missing action verb)")
                else:
                    issues.append(f"AC{i} is very short ({len(ac)} chars), may lack measurability")

        return issues[:2]  # Limit to top 2 SMART issues


class TechnicalFeasibilityAnalyzer:
    """
    Reasoning Path 2: Technical Feasibility

    Validates technical feasibility of proposed approach
    """

    @staticmethod
    def analyze(issue: IssueDocument) -> ReasoningPathResult:
        """Analyze technical feasibility"""
        start_time = time.time()

        findings = []
        issues = []
        suggestions = []

        # Check 1: Dependencies documented
        if not issue.dependencies and len(issue.raw_content) > 1000:
            # Large project likely has dependencies
            issues.append("No dependencies documented (expected for project of this size)")
            suggestions.append("Document technical dependencies (libraries, services, APIs)")
        elif issue.dependencies:
            findings.append(f"{len(issue.dependencies)} dependencies documented")

        # Check 2: Technical requirements present
        tech_keywords = ['api', 'database', 'library', 'framework', 'service', 'component', 'class', 'agent']
        tech_mentions = sum(1 for keyword in tech_keywords if keyword in issue.raw_content.lower())

        if tech_mentions == 0:
            issues.append("No technical implementation details mentioned")
            suggestions.append("Add technical approach section describing implementation")
        else:
            findings.append(f"Technical details mentioned ({tech_mentions} technical keywords)")

        # Check 3: Architecture considerations
        arch_keywords = ['architecture', 'design', 'integration', 'hld', 'lld', 'component']
        arch_mentions = sum(1 for keyword in arch_keywords if keyword in issue.raw_content.lower())

        if arch_mentions == 0:
            issues.append("No architecture/design considerations mentioned")
            suggestions.append("Reference HLD/LLD or describe architectural approach")
        else:
            findings.append("Architecture considerations present")

        # Check 4: Similar projects referenced
        if 'similar' in issue.raw_content.lower() or 'pattern' in issue.raw_content.lower():
            findings.append("References to similar projects or patterns")
        else:
            suggestions.append("Consider referencing similar successful projects as patterns")

        # Calculate score
        total_checks = 5
        passed_checks = total_checks - len(issues)
        score = max(0.4, min(1.0, passed_checks / total_checks))  # Min 0.4 (benefit of doubt)

        # Determine decision
        if score >= 0.85:
            decision = Decision.GO
        elif score >= 0.65:
            decision = Decision.GO_WITH_ADJUSTMENTS
        elif score >= 0.40:
            decision = Decision.REVISE
        else:
            decision = Decision.NO_GO

        execution_time = time.time() - start_time

        return ReasoningPathResult(
            path_name="Technical Feasibility",
            path_number=2,
            decision=decision,
            confidence=score,
            findings=findings,
            issues=issues,
            suggestions=suggestions,
            execution_time=execution_time
        )


class TimelineEffortValidator:
    """
    Reasoning Path 3: Timeline & Effort

    Validates reasonableness of timeline and effort estimates
    """

    @staticmethod
    def analyze(issue: IssueDocument) -> ReasoningPathResult:
        """Analyze timeline and effort estimates"""
        start_time = time.time()

        findings = []
        issues = []
        suggestions = []

        # Check 1: Story points defined
        if issue.story_points is None:
            issues.append("Story points not defined")
            suggestions.append("Estimate story points based on complexity and scope")
            score_sp = 0.0
        elif issue.story_points <= 0:
            issues.append(f"Invalid story points: {issue.story_points}")
            score_sp = 0.0
        elif issue.story_points > 21:
            issues.append(f"Story points very high ({issue.story_points}), consider breaking down")
            suggestions.append("Consider splitting into smaller issues if SP > 21")
            score_sp = 0.7
        elif issue.story_points >= 13:
            findings.append(f"Story points: {issue.story_points} (large story)")
            score_sp = 0.85
        else:
            findings.append(f"Story points: {issue.story_points} (reasonable)")
            score_sp = 1.0

        # Check 2: Timeline documented
        if issue.timeline:
            findings.append("Timeline documented")
            score_timeline = 1.0
        elif 'timeline' in issue.raw_content.lower() or 'duration' in issue.raw_content.lower():
            findings.append("Timeline mentioned")
            score_timeline = 0.8
        else:
            issues.append("No timeline or duration estimates")
            suggestions.append("Add timeline section with estimated duration")
            score_timeline = 0.5

        # Check 3: Scope vs Effort alignment (heuristic)
        num_acs = len(issue.acceptance_criteria)

        if issue.story_points and num_acs > 0:
            # Heuristic: ~1-2 story points per AC is reasonable
            expected_sp_min = num_acs * 0.5
            expected_sp_max = num_acs * 3

            if issue.story_points < expected_sp_min:
                issues.append(f"Story points ({issue.story_points}) seem low for {num_acs} ACs")
                suggestions.append(f"Consider if {num_acs} ACs can be done in {issue.story_points} SP")
                score_alignment = 0.6
            elif issue.story_points > expected_sp_max:
                issues.append(f"Story points ({issue.story_points}) seem high for {num_acs} ACs")
                suggestions.append("Consider if scope is well-defined or if ACs are too few")
                score_alignment = 0.7
            else:
                findings.append(f"Story points ({issue.story_points}) align with {num_acs} ACs")
                score_alignment = 1.0
        else:
            score_alignment = 0.5  # Neutral

        # Calculate overall score
        score = (score_sp * 0.4 + score_timeline * 0.3 + score_alignment * 0.3)

        # Determine decision
        if score >= 0.85:
            decision = Decision.GO
        elif score >= 0.65:
            decision = Decision.GO_WITH_ADJUSTMENTS
        else:
            decision = Decision.REVISE

        execution_time = time.time() - start_time

        return ReasoningPathResult(
            path_name="Timeline & Effort",
            path_number=3,
            decision=decision,
            confidence=score,
            findings=findings,
            issues=issues,
            suggestions=suggestions,
            execution_time=execution_time
        )


class RiskAnalyzer:
    """
    Reasoning Path 4: Risk Analysis

    Validates risk identification and mitigation
    """

    @staticmethod
    def analyze(issue: IssueDocument) -> ReasoningPathResult:
        """Analyze risk identification and mitigation"""
        start_time = time.time()

        findings = []
        issues = []
        suggestions = []

        # Check 1: Risks documented
        if not issue.risks:
            # Check if risks section exists in document
            if 'risk' in issue.raw_content.lower():
                findings.append("Risks section present")
                score_risks = 0.7
            else:
                issues.append("No risks identified or documented")
                suggestions.append("Add Risks section identifying potential blockers and mitigations")
                score_risks = 0.5
        elif len(issue.risks) < 2:
            issues.append(f"Only {len(issue.risks)} risk(s) identified, consider more thorough analysis")
            suggestions.append("Identify at least 3 risks (technical, timeline, integration)")
            score_risks = 0.7
        else:
            findings.append(f"{len(issue.risks)} risks identified")
            score_risks = 1.0

        # Check 2: Mitigation strategies
        mitigation_keywords = ['mitigation', 'mitigate', 'address', 'plan', 'strategy', 'fallback']
        mitigation_mentions = sum(1 for keyword in mitigation_keywords if keyword in issue.raw_content.lower())

        if mitigation_mentions == 0:
            issues.append("No risk mitigation strategies mentioned")
            suggestions.append("Add mitigation plans for identified risks")
            score_mitigation = 0.5
        elif mitigation_mentions < 2:
            suggestions.append("Consider adding more detailed mitigation strategies")
            score_mitigation = 0.75
        else:
            findings.append("Risk mitigations documented")
            score_mitigation = 1.0

        # Check 3: External dependencies risk
        if issue.dependencies:
            if any('external' in dep.lower() or 'api' in dep.lower() for dep in issue.dependencies):
                findings.append("External dependencies identified (good risk awareness)")
                score_external = 1.0
            else:
                score_external = 0.8
        else:
            score_external = 0.8  # Neutral if no dependencies

        # Calculate overall score
        score = (score_risks * 0.5 + score_mitigation * 0.35 + score_external * 0.15)

        # Determine decision
        if score >= 0.85:
            decision = Decision.GO
        elif score >= 0.65:
            decision = Decision.GO_WITH_ADJUSTMENTS
        else:
            decision = Decision.REVISE

        execution_time = time.time() - start_time

        return ReasoningPathResult(
            path_name="Risk Analysis",
            path_number=4,
            decision=decision,
            confidence=score,
            findings=findings,
            issues=issues,
            suggestions=suggestions,
            execution_time=execution_time
        )


class IntegrationValidator:
    """
    Reasoning Path 5: Integration Validator

    Validates integration with existing system
    """

    @staticmethod
    def analyze(issue: IssueDocument) -> ReasoningPathResult:
        """Analyze integration with existing system"""
        start_time = time.time()

        findings = []
        issues = []
        suggestions = []

        # Check 1: Integration points mentioned
        integration_keywords = ['integration', 'integrate', 'orchestrator', 'pipeline', 'workflow', 'connect']
        integration_mentions = sum(1 for keyword in integration_keywords if keyword in issue.raw_content.lower())

        if integration_mentions == 0:
            issues.append("No integration points or strategy mentioned")
            suggestions.append("Describe how this integrates with existing system")
            score_integration = 0.6
        elif integration_mentions < 3:
            findings.append("Integration mentioned")
            score_integration = 0.8
        else:
            findings.append("Integration strategy well-documented")
            score_integration = 1.0

        # Check 2: Backward compatibility
        compat_keywords = ['backward compatible', 'compatibility', 'breaking change', 'migration']
        compat_mentions = sum(1 for keyword in compat_keywords if keyword in issue.raw_content.lower())

        if compat_mentions > 0:
            findings.append("Backward compatibility considered")
            score_compat = 1.0
        else:
            suggestions.append("Consider backward compatibility and migration path")
            score_compat = 0.7

        # Check 3: Related components identified
        if 'related' in issue.raw_content.lower() or 'references' in issue.raw_content.lower():
            findings.append("Related components/issues referenced")
            score_related = 1.0
        else:
            suggestions.append("Reference related components, issues, or projects")
            score_related = 0.75

        # Calculate overall score
        score = (score_integration * 0.5 + score_compat * 0.3 + score_related * 0.2)

        # Determine decision
        if score >= 0.85:
            decision = Decision.GO
        elif score >= 0.65:
            decision = Decision.GO_WITH_ADJUSTMENTS
        else:
            decision = Decision.REVISE

        execution_time = time.time() - start_time

        return ReasoningPathResult(
            path_name="Integration & Dependencies",
            path_number=5,
            decision=decision,
            confidence=score,
            findings=findings,
            issues=issues,
            suggestions=suggestions,
            execution_time=execution_time
        )


# ============================================================================
# Consensus Decider
# ============================================================================

class ConsensusDecider:
    """
    Aggregates reasoning path results into consensus decision

    Uses majority voting with average confidence
    """

    @staticmethod
    def decide(results: List[ReasoningPathResult], threshold: float = 0.80) -> ConsensusResult:
        """
        Make consensus decision from reasoning path results

        Args:
            results: List of ReasoningPathResult (n=5)
            threshold: Minimum confidence threshold for GO decision

        Returns:
            ConsensusResult with final decision
        """
        start_time = time.time()

        if not results:
            raise ValueError("Cannot make consensus with no results")

        # Extract numeric decisions and confidences
        numeric_decisions = [r.decision.numeric_value for r in results]
        confidences = [r.confidence for r in results]

        # Calculate averages
        avg_decision = mean(numeric_decisions)
        avg_confidence = mean(confidences)

        # Apply consensus logic (from ADR-003)
        if avg_decision >= 1.5 and avg_confidence >= threshold:
            final_decision = Decision.GO
        elif avg_decision >= 1.5:
            final_decision = Decision.GO_WITH_ADJUSTMENTS
        elif avg_decision >= 0.5:
            if avg_confidence >= 0.70:
                final_decision = Decision.GO_WITH_ADJUSTMENTS
            else:
                final_decision = Decision.REVISE
        elif avg_decision >= -0.5:
            final_decision = Decision.REVISE
        else:
            final_decision = Decision.NO_GO

        # Aggregate recommendations
        recommended_adjustments = ConsensusDecider._aggregate_suggestions(results)

        execution_time = time.time() - start_time

        return ConsensusResult(
            decision=final_decision,
            confidence=avg_confidence,
            reasoning_results=results,
            recommended_adjustments=recommended_adjustments,
            execution_time=sum(r.execution_time for r in results) + execution_time
        )

    @staticmethod
    def _aggregate_suggestions(results: List[ReasoningPathResult]) -> List[str]:
        """Aggregate unique suggestions from all paths"""
        all_suggestions = []
        for result in results:
            all_suggestions.extend(result.suggestions)

        # Deduplicate while preserving order
        unique_suggestions = []
        seen = set()
        for suggestion in all_suggestions:
            suggestion_lower = suggestion.lower()
            if suggestion_lower not in seen:
                seen.add(suggestion_lower)
                unique_suggestions.append(suggestion)

        return unique_suggestions[:10]  # Limit to top 10


# ============================================================================
# Validation Report Generator
# ============================================================================

class ValidationReportGenerator:
    """
    Generates Markdown validation report from consensus result
    """

    @staticmethod
    def generate(consensus: ConsensusResult, issue: IssueDocument, output_dir: str) -> str:
        """
        Generate validation report

        Args:
            consensus: ConsensusResult with final decision
            issue: Original IssueDocument
            output_dir: Directory to save report

        Returns:
            Path to generated report
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        report_filename = f"validation_report_{issue.issue_id}.md"
        report_path = output_path / report_filename

        # Generate report content
        content = ValidationReportGenerator._generate_content(consensus, issue)

        # Write report
        report_path.write_text(content, encoding='utf-8')

        return str(report_path)

    @staticmethod
    def _generate_content(consensus: ConsensusResult, issue: IssueDocument) -> str:
        """Generate Markdown content for validation report"""

        proceed_text = "YES" if consensus.should_proceed() else "NO"

        # Build reasoning table
        table_rows = []
        for result in consensus.reasoning_results:
            key_findings = "; ".join(result.findings[:2]) if result.findings else "N/A"
            table_rows.append(
                f"| Path {result.path_number}: {result.path_name} | {result.decision.value} | "
                f"{result.confidence*100:.0f}% | {key_findings} |"
            )

        reasoning_table = "\n".join(table_rows)

        # Build recommendations list
        if consensus.recommended_adjustments:
            recommendations = "\n".join(f"{i}. {adj}" for i, adj in enumerate(consensus.recommended_adjustments, 1))
        else:
            recommendations = "None - plan is ready to proceed"

        # Build issues summary
        all_issues = []
        for result in consensus.reasoning_results:
            if result.issues:
                all_issues.append(f"**{result.path_name}**:")
                for issue_item in result.issues:
                    all_issues.append(f"  - {issue_item}")

        issues_section = "\n".join(all_issues) if all_issues else "No major issues found"

        report = f"""# Plan Validation Report: {issue.title}

**Issue ID**: {issue.issue_id}
**Validation Date**: {consensus.timestamp}
**Validation Method**: Self-Consistency (n=5 reasoning paths)

---

## Consensus Analysis

| Reasoning Path | Decision | Confidence | Key Findings |
|----------------|----------|------------|--------------|
{reasoning_table}

**Overall Decision**: {consensus.decision.value}
**Confidence**: {consensus.confidence*100:.0f}%
**Execution Time**: {consensus.execution_time:.2f}s

---

## Issues Found

{issues_section}

---

## Recommended Adjustments

{recommendations}

---

## Proceed to Phase 2 (Feasibility)?

**{proceed_text}**

"""

        if consensus.should_proceed():
            if consensus.decision == Decision.GO:
                report += "Confidence threshold met. Plan is solid and ready for Feasibility phase.\n"
            else:
                report += f"Proceed with adjustments. Address {len(consensus.recommended_adjustments)} recommendations before or during Feasibility phase.\n"
        else:
            report += f"Plan requires revision. Address {len(consensus.recommended_adjustments)} issues before proceeding to Feasibility phase.\n"

        report += f"""
---

**Trazabilidad**: {issue.issue_id}
**Metodologia**: Self-Consistency (Phase 1.5: Plan Validation)
**Validated By**: PlanValidationAgent
"""

        return report


# ============================================================================
# Main Agent Implementation
# ============================================================================

class SDLCPlanValidationAgent(SDLCAgent):
    """
    SDLC Phase 1.5: Plan Validation Agent

    Validates issue documents from Phase 1 (Planning) using Self-Consistency
    with 5 independent reasoning paths before proceeding to Phase 2 (Feasibility).

    Reasoning Paths:
    1. Completeness Check
    2. Technical Feasibility
    3. Timeline & Effort
    4. Risk Analysis
    5. Integration & Dependencies

    Decision: GO | GO con ajustes | REVISE | NO-GO
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="SDLCPlanValidationAgent",
            phase="planning_validation",
            config=config
        )

        # Configuration
        self.n_reasoning_paths = self.config.get("n_reasoning_paths", 5)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.80)
        self.parallel_execution = self.config.get("parallel_execution", False)

        # Output directory
        self.output_dir = self._detect_output_dir()
        self.validation_dir = self.output_dir / "validacion"

        logger.info(f"Initialized {self.name}")
        logger.info(f"  n_reasoning_paths: {self.n_reasoning_paths}")
        logger.info(f"  confidence_threshold: {self.confidence_threshold}")
        logger.info(f"  output_dir: {self.validation_dir}")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plan validation

        Args:
            input_data: {
                "issue_document": "path/to/issue.md",
                "project_context": {} (optional)
            }

        Returns:
            {
                "decision": "GO" | "GO con ajustes" | "REVISE" | "NO-GO",
                "confidence": 0.0-1.0,
                "recommended_adjustments": [...],
                "validation_report": "path/to/report.md",
                "issue_document": "path/to/issue.md"
            }

        Raises:
            ValueError: If input is invalid
            FileNotFoundError: If issue document not found
        """
        logger.info(f"Starting {self.name} execution")

        # Extract input
        issue_doc_path = input_data.get("issue_document")
        if not issue_doc_path:
            raise ValueError("Missing required input: issue_document")

        # Step 1: Load and parse issue document
        logger.info(f"Loading issue document: {issue_doc_path}")
        issue = IssueDocumentParser.parse(issue_doc_path)
        logger.info(f"Parsed issue: {issue.issue_id} - {issue.title}")

        # Step 2: Execute reasoning paths
        logger.info(f"Executing {self.n_reasoning_paths} reasoning paths...")
        reasoning_results = self._execute_reasoning_paths(issue)

        # Log individual results
        for result in reasoning_results:
            logger.info(f"  Path {result.path_number}: {result.decision.value} ({result.confidence*100:.0f}%)")

        # Step 3: Make consensus decision
        logger.info("Making consensus decision...")
        consensus = ConsensusDecider.decide(reasoning_results, self.confidence_threshold)
        logger.info(f"Consensus: {consensus.decision.value} ({consensus.confidence*100:.0f}%)")

        # Step 4: Generate validation report
        logger.info("Generating validation report...")
        report_path = ValidationReportGenerator.generate(consensus, issue, str(self.validation_dir))
        logger.info(f"Report generated: {report_path}")

        # Return result
        return {
            "decision": consensus.decision.value,
            "confidence": consensus.confidence,
            "recommended_adjustments": consensus.recommended_adjustments,
            "validation_report": report_path,
            "issue_document": issue_doc_path,
            "timestamp": consensus.timestamp
        }

    def _execute_reasoning_paths(self, issue: IssueDocument) -> List[ReasoningPathResult]:
        """Execute all reasoning paths (sequential or parallel)"""
        if self.parallel_execution:
            return self._execute_parallel(issue)
        else:
            return self._execute_sequential(issue)

    def _execute_sequential(self, issue: IssueDocument) -> List[ReasoningPathResult]:
        """Execute reasoning paths sequentially"""
        results = []

        # Path 1: Completeness
        results.append(CompletenessChecker.analyze(issue))

        # Path 2: Technical Feasibility
        results.append(TechnicalFeasibilityAnalyzer.analyze(issue))

        # Path 3: Timeline & Effort
        results.append(TimelineEffortValidator.analyze(issue))

        # Path 4: Risk Analysis
        results.append(RiskAnalyzer.analyze(issue))

        # Path 5: Integration
        results.append(IntegrationValidator.analyze(issue))

        return results

    def _execute_parallel(self, issue: IssueDocument) -> List[ReasoningPathResult]:
        """Execute reasoning paths in parallel (future enhancement)"""
        from concurrent.futures import ThreadPoolExecutor

        paths = [
            CompletenessChecker.analyze,
            TechnicalFeasibilityAnalyzer.analyze,
            TimelineEffortValidator.analyze,
            RiskAnalyzer.analyze,
            IntegrationValidator.analyze
        ]

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(path, issue) for path in paths]
            results = [future.result() for future in futures]

        return results

    def _detect_output_dir(self) -> Path:
        """Detect output directory using Pattern Recognition"""
        project_root = Path.cwd()
        docs_dir = project_root / "docs"

        # Check if docs/agent structure exists
        agent_dir = docs_dir / "agent"
        if agent_dir.exists():
            return agent_dir

        # Fallback
        return docs_dir / "sdlc_outputs"


# CLI Entry Point (for testing)
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python plan_validation_agent.py <issue_document_path>")
        sys.exit(1)

    issue_path = sys.argv[1]

    agent = SDLCPlanValidationAgent(config={
        "confidence_threshold": 0.80,
        "parallel_execution": False
    })

    result = agent.run({"issue_document": issue_path})

    print(f"\nDecision: {result['decision']}")
    print(f"Confidence: {result['confidence']*100:.0f}%")
    print(f"Report: {result['validation_report']}")
