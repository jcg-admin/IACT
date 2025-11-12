#!/usr/bin/env python3
"""Tests for the DRFArchitectureAgent.

These tests validate that the agent detects Django REST Framework anti-patterns
and rewards ViewSets that follow the documented best practices. The agent is a
specialised meta-agent used by the backend analysis tooling to focus on DRF
concerns such as permissions, serializers, filters and action bloat.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[6]
MODULE_PATH = (
    PROJECT_ROOT
    / "scripts"
    / "coding"
    / "ai"
    / "agents"
    / "meta"
    / "drf_architecture_agent.py"
)


def _load_agent_module():
    """Load the agent module without importing legacy packages."""

    spec = importlib.util.spec_from_file_location(
        "drf_architecture_agent", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "Unable to load drf_architecture_agent module"
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


drf_module = _load_agent_module()
DRFArchitectureAgent = drf_module.DRFArchitectureAgent
DRFAnalysisResult = drf_module.DRFAnalysisResult
DRFIssueSeverity = drf_module.DRFIssueSeverity


@pytest.fixture
def agent() -> DRFArchitectureAgent:
    """Provide a configured agent for the tests."""

    return DRFArchitectureAgent()


@pytest.fixture
def viewset_missing_core_components() -> str:
    """DRF ViewSet code lacking key architectural requirements."""

    return '''
from rest_framework.viewsets import ModelViewSet


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def cancel(self, request, *args, **kwargs):
        """Custom action without permissions or serializer"""
        pass
'''


@pytest.fixture
def well_structured_viewset() -> str:
    """DRF ViewSet that follows recommended practices."""

    return '''
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.select_related("profile").all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "segment"]
    search_fields = ["name", "email"]
    ordering_fields = ["created_at", "updated_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
'''


@pytest.fixture
def fat_viewset() -> str:
    """ViewSet with many bespoke actions and missing structure."""

    return '''
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated


class TicketViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def list(self, request):
        pass

    def retrieve(self, request, pk=None):
        pass

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        pass

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        pass

    @action(detail=False, methods=["post"])
    def bulk_close(self, request):
        pass

    def assign(self, request, pk=None):
        pass

    def transfer(self, request, pk=None):
        pass
'''


class TestDRFArchitectureAgent:
    """Behavioural tests for the DRF architecture agent."""

    def test_detects_missing_permissions_and_serializer(
        self,
        agent: DRFArchitectureAgent,
        viewset_missing_core_components: str,
    ) -> None:
        """The agent should highlight missing DRF building blocks."""

        result = agent.analyze_code(viewset_missing_core_components)
        assert isinstance(result, DRFAnalysisResult)
        assert result.passed is False

        permission_issues = result.get_issues_by_category("permissions")
        assert permission_issues
        assert permission_issues[0].severity == DRFIssueSeverity.CRITICAL

        serializer_issues = result.get_issues_by_category("serializers")
        assert serializer_issues
        assert serializer_issues[0].severity == DRFIssueSeverity.HIGH

        filter_issues = result.get_issues_by_category("filters")
        assert filter_issues

        pagination_issues = result.get_issues_by_category("pagination")
        assert pagination_issues

    def test_viewset_with_good_practices_passes(
        self,
        agent: DRFArchitectureAgent,
        well_structured_viewset: str,
    ) -> None:
        """A well configured ViewSet should pass all checks."""

        result = agent.analyze_code(well_structured_viewset)
        assert isinstance(result, DRFAnalysisResult)
        assert result.passed is True
        assert not result.issues
        assert result.viewsets[0].score == pytest.approx(1.0)
        assert "permissions" in result.viewsets[0].checks

    def test_detects_fat_viewset_custom_actions(
        self,
        agent: DRFArchitectureAgent,
        fat_viewset: str,
    ) -> None:
        """The agent flags ViewSets with excessive bespoke actions."""

        result = agent.analyze_code(fat_viewset)
        action_issues = result.get_issues_by_category("actions")
        assert action_issues
        assert any("custom action" in issue.detail.lower() for issue in action_issues)
        assert any(issue.severity in {DRFIssueSeverity.HIGH, DRFIssueSeverity.MEDIUM} for issue in action_issues)

