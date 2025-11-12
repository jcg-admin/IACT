"""DRFArchitectureAgent - specialised architecture checks for DRF ViewSets.

This agent focuses on Django REST Framework code and complements the
meta-development pipeline by validating concerns that are specific to DRF.
It applies a sequential chain of verification steps (permissions → serializers
→ querysets → filters → pagination → actions) to surface actionable
recommendations with severity levels.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Iterable, List, Optional, Tuple


class DRFIssueSeverity(Enum):
    """Severity levels assigned to the detected issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DRFIssue:
    """Single issue detected while analysing a ViewSet."""

    viewset: str
    category: str
    severity: DRFIssueSeverity
    detail: str
    recommendation: str
    location: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        """Serialize the issue to a dictionary for reporting purposes."""

        return {
            "viewset": self.viewset,
            "category": self.category,
            "severity": self.severity.value,
            "detail": self.detail,
            "recommendation": self.recommendation,
            "location": self.location or "",
        }


@dataclass
class ViewSetAnalysis:
    """Aggregated analysis data for a single ViewSet."""

    name: str
    issues: List[DRFIssue] = field(default_factory=list)
    checks: List[str] = field(default_factory=list)
    score: float = 1.0
    passed: bool = True

    def to_dict(self) -> Dict[str, object]:
        """Serialize the report to a dictionary."""

        return {
            "name": self.name,
            "issues": [issue.to_dict() for issue in self.issues],
            "checks": list(self.checks),
            "score": self.score,
            "passed": self.passed,
        }


@dataclass
class DRFAnalysisResult:
    """Result of running the DRFArchitectureAgent."""

    viewsets: List[ViewSetAnalysis] = field(default_factory=list)
    issues: List[DRFIssue] = field(default_factory=list)
    passed: bool = True
    summary: str = ""

    def get_issues_by_category(self, category: str) -> List[DRFIssue]:
        """Return the issues that match a specific category."""

        return [issue for issue in self.issues if issue.category == category]

    def to_dict(self) -> Dict[str, object]:
        """Serialize the whole analysis result."""

        return {
            "summary": self.summary,
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
            "viewsets": [report.to_dict() for report in self.viewsets],
        }


@dataclass
class ViewSetInfo:
    """Lightweight representation of a ViewSet AST node."""

    name: str
    node: ast.ClassDef
    attributes: Dict[str, ast.AST]
    methods: Dict[str, ast.FunctionDef]


class DRFArchitectureAgent:
    """Analyse Django REST Framework ViewSets for common anti-patterns."""

    VIEWSET_BASES = {
        "ViewSet",
        "ModelViewSet",
        "ReadOnlyModelViewSet",
        "GenericViewSet",
        "GenericAPIView",
        "APIView",
    }

    REST_METHODS = {
        "list",
        "create",
        "retrieve",
        "update",
        "partial_update",
        "destroy",
        "get_queryset",
        "get_permissions",
        "get_serializer",
        "get_serializer_class",
        "get_serializer_context",
        "perform_create",
        "perform_update",
        "perform_destroy",
        "paginate_queryset",
        "get_paginated_response",
        "get_object",
    }

    SEVERITY_WEIGHTS = {
        DRFIssueSeverity.CRITICAL: 0.35,
        DRFIssueSeverity.HIGH: 0.25,
        DRFIssueSeverity.MEDIUM: 0.15,
        DRFIssueSeverity.LOW: 0.05,
    }

    FAILING_SEVERITIES = {DRFIssueSeverity.CRITICAL, DRFIssueSeverity.HIGH}
    CUSTOM_METHOD_THRESHOLD = 3
    HIGH_ACTION_THRESHOLD = 5

    def __init__(self) -> None:
        self._check_sequence: Tuple[Tuple[str, Callable[[ViewSetInfo], List[DRFIssue]]], ...] = (
            ("permissions", self._check_permissions),
            ("serializers", self._check_serializers),
            ("querysets", self._check_querysets),
            ("filters", self._check_filters),
            ("pagination", self._check_pagination),
            ("actions", self._check_actions),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def analyze_code(self, code: str) -> DRFAnalysisResult:
        """Analyse Python source containing DRF ViewSets."""

        try:
            module = ast.parse(code)
        except SyntaxError as exc:  # pragma: no cover - defensive guard
            issue = DRFIssue(
                viewset="<module>",
                category="syntax",
                severity=DRFIssueSeverity.CRITICAL,
                detail=f"Syntax error: {exc.msg}",
                recommendation="Fix syntax errors before running the DRF analysis.",
                location=f"line {exc.lineno}" if exc.lineno else None,
            )
            return DRFAnalysisResult(
                viewsets=[],
                issues=[issue],
                passed=False,
                summary="Syntax error prevented DRF analysis.",
            )

        viewsets = self._find_viewsets(module)
        if not viewsets:
            return DRFAnalysisResult(
                viewsets=[],
                issues=[],
                passed=True,
                summary="No DRF ViewSets detected in the provided code.",
            )

        reports: List[ViewSetAnalysis] = []
        all_issues: List[DRFIssue] = []

        for info in viewsets:
            issues: List[DRFIssue] = []
            checks: List[str] = []
            score = 1.0

            for check_name, checker in self._check_sequence:
                checks.append(check_name)
                detected = checker(info)
                issues.extend(detected)
                for issue in detected:
                    score -= self.SEVERITY_WEIGHTS.get(issue.severity, 0.0)

            score = max(0.0, min(1.0, score))
            passed = not any(issue.severity in self.FAILING_SEVERITIES for issue in issues)

            report = ViewSetAnalysis(
                name=info.name,
                issues=issues,
                checks=checks,
                score=score,
                passed=passed,
            )
            reports.append(report)
            all_issues.extend(issues)

        overall_passed = not any(
            issue.severity in self.FAILING_SEVERITIES for issue in all_issues
        )
        summary = self._build_summary(reports, overall_passed)

        return DRFAnalysisResult(
            viewsets=reports,
            issues=all_issues,
            passed=overall_passed,
            summary=summary,
        )

    # ------------------------------------------------------------------
    # Check implementations
    # ------------------------------------------------------------------
    def _check_permissions(self, info: ViewSetInfo) -> List[DRFIssue]:
        has_permission_classes = self._attribute_has_values(
            info.attributes.get("permission_classes")
        )
        has_get_permissions = "get_permissions" in info.methods

        if has_permission_classes or has_get_permissions:
            return []

        return [
            DRFIssue(
                viewset=info.name,
                category="permissions",
                severity=DRFIssueSeverity.CRITICAL,
                detail="ViewSet does not declare permission_classes nor override get_permissions().",
                recommendation="Define permission_classes or implement get_permissions() to enforce access control.",
                location=info.name,
            )
        ]

    def _check_serializers(self, info: ViewSetInfo) -> List[DRFIssue]:
        serializer_attr = info.attributes.get("serializer_class")
        has_serializer = self._attribute_present(serializer_attr)
        has_get_serializer_class = "get_serializer_class" in info.methods

        if has_serializer or has_get_serializer_class:
            return []

        return [
            DRFIssue(
                viewset=info.name,
                category="serializers",
                severity=DRFIssueSeverity.HIGH,
                detail="Missing serializer_class definition or get_serializer_class override.",
                recommendation="Set serializer_class or provide a get_serializer_class() implementation.",
                location=info.name,
            )
        ]

    def _check_querysets(self, info: ViewSetInfo) -> List[DRFIssue]:
        queryset_attr = info.attributes.get("queryset")
        has_queryset = self._attribute_present(queryset_attr)
        has_get_queryset = "get_queryset" in info.methods

        if has_queryset or has_get_queryset:
            return []

        return [
            DRFIssue(
                viewset=info.name,
                category="querysets",
                severity=DRFIssueSeverity.MEDIUM,
                detail="ViewSet should declare queryset or implement get_queryset().",
                recommendation="Provide queryset or a dynamic get_queryset() for clarity and testability.",
                location=info.name,
            )
        ]

    def _check_filters(self, info: ViewSetInfo) -> List[DRFIssue]:
        filter_backends = info.attributes.get("filter_backends")
        has_filter_backends = self._attribute_has_values(filter_backends)
        has_filterset_fields = self._attribute_has_values(info.attributes.get("filterset_fields"))
        has_filterset_class = self._attribute_present(info.attributes.get("filterset_class"))
        has_search_fields = self._attribute_has_values(info.attributes.get("search_fields"))
        has_ordering = self._attribute_has_values(info.attributes.get("ordering_fields"))

        if has_filter_backends and not (
            has_filterset_fields or has_filterset_class or has_search_fields or has_ordering
        ):
            return [
                DRFIssue(
                    viewset=info.name,
                    category="filters",
                    severity=DRFIssueSeverity.HIGH,
                    detail="filter_backends configured but no filterset/search/order fields declared.",
                    recommendation="Add filterset_fields, filterset_class or search_fields to leverage filter_backends.",
                    location=info.name,
                )
            ]

        if any([has_filter_backends, has_filterset_fields, has_filterset_class, has_search_fields, has_ordering]):
            return []

        return [
            DRFIssue(
                viewset=info.name,
                category="filters",
                severity=DRFIssueSeverity.MEDIUM,
                detail="ViewSet does not configure filtering, search or ordering helpers.",
                recommendation="Configure filter_backends with filterset/search fields to provide API level filtering.",
                location=info.name,
            )
        ]

    def _check_pagination(self, info: ViewSetInfo) -> List[DRFIssue]:
        pagination_attr = info.attributes.get("pagination_class")
        has_pagination = self._attribute_present(pagination_attr)

        if has_pagination:
            return []

        return [
            DRFIssue(
                viewset=info.name,
                category="pagination",
                severity=DRFIssueSeverity.LOW,
                detail="No pagination_class configured for the ViewSet.",
                recommendation="Assign pagination_class or rely on a project default paginator and document the behaviour.",
                location=info.name,
            )
        ]

    def _check_actions(self, info: ViewSetInfo) -> List[DRFIssue]:
        custom_methods: List[Tuple[str, ast.FunctionDef]] = []
        action_methods: List[str] = []

        for name, func in info.methods.items():
            if name in self.REST_METHODS or name.startswith("_"):
                continue
            custom_methods.append((name, func))
            if self._has_action_decorator(func):
                action_methods.append(name)

        if len(custom_methods) < self.CUSTOM_METHOD_THRESHOLD:
            return []

        severity = (
            DRFIssueSeverity.HIGH
            if len(custom_methods) >= self.HIGH_ACTION_THRESHOLD
            else DRFIssueSeverity.MEDIUM
        )

        locations = ", ".join(f"{info.name}.{name}" for name, _ in custom_methods)
        detail_parts = [
            f"ViewSet defines {len(custom_methods)} custom action methods indicating a fat ViewSet."
        ]
        if action_methods:
            detail_parts.append(f"Custom @action methods: {', '.join(action_methods)}.")

        return [
            DRFIssue(
                viewset=info.name,
                category="actions",
                severity=severity,
                detail=" ".join(detail_parts),
                recommendation="Move complex workflows to services/use cases or split them into smaller ViewSets.",
                location=locations,
            )
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _find_viewsets(self, module: ast.AST) -> List[ViewSetInfo]:
        viewsets: List[ViewSetInfo] = []

        for node in ast.walk(module):
            if not isinstance(node, ast.ClassDef):
                continue

            base_names = {self._resolve_name(base) for base in node.bases}
            if not base_names.intersection(self.VIEWSET_BASES):
                continue

            attributes = self._collect_attributes(node)
            methods = self._collect_methods(node)
            viewsets.append(
                ViewSetInfo(
                    name=node.name,
                    node=node,
                    attributes=attributes,
                    methods=methods,
                )
            )

        return viewsets

    def _collect_attributes(self, node: ast.ClassDef) -> Dict[str, ast.AST]:
        attributes: Dict[str, ast.AST] = {}

        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        attributes[target.id] = stmt.value
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                attributes[stmt.target.id] = stmt.value

        return attributes

    def _collect_methods(self, node: ast.ClassDef) -> Dict[str, ast.FunctionDef]:
        methods: Dict[str, ast.FunctionDef] = {}

        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                methods[stmt.name] = stmt

        return methods

    def _resolve_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""

    def _attribute_present(self, value: Optional[ast.AST]) -> bool:
        if value is None:
            return False
        if isinstance(value, ast.Constant) and value.value is None:
            return False
        return True

    def _attribute_has_values(self, value: Optional[ast.AST]) -> bool:
        if value is None:
            return False
        if isinstance(value, ast.Constant):
            return value.value not in (None, "", False)
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            return len(value.elts) > 0
        return True

    def _has_action_decorator(self, func: ast.FunctionDef) -> bool:
        for decorator in func.decorator_list:
            target = decorator
            if isinstance(decorator, ast.Call):
                target = decorator.func

            if isinstance(target, ast.Name) and target.id == "action":
                return True
            if isinstance(target, ast.Attribute) and target.attr == "action":
                return True

        return False

    def _build_summary(self, reports: Iterable[ViewSetAnalysis], passed: bool) -> str:
        reports = list(reports)
        if not reports:
            return "No DRF ViewSets detected in the provided code."

        failing = [report for report in reports if not report.passed]
        parts = [f"Analysed {len(reports)} DRF ViewSet(s)."]
        parts.append(f"Passed: {len(reports) - len(failing)}")
        parts.append(f"Failed: {len(failing)}")

        if failing:
            parts.append("Failing ViewSets: " + ", ".join(report.name for report in failing))
        if passed:
            parts.append("All critical checks satisfied.")

        return " ".join(parts)


__all__ = [
    "DRFArchitectureAgent",
    "DRFAnalysisResult",
    "DRFIssue",
    "DRFIssueSeverity",
    "ViewSetAnalysis",
]

