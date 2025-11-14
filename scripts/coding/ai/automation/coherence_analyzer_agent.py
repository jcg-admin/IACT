#!/usr/bin/env python3
"""
CoherenceAnalyzerAgent - UI/API Coherence Analysis Agent.

This agent performs advanced coherence analysis between API endpoints
and UI services/tests using AST parsing, correlation analysis, and
gap detection.

Implements TDD approach with comprehensive test coverage.

Author: SDLC Agent / DevOps Team
Date: 2025-11-13
ADR: ADR-043-coherence-analyzer-agent.md
"""

import argparse
import ast
import json
import logging
import re
import subprocess
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from scripts.coding.ai.sdlc.base_agent import SDLCAgent


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class APIEndpoint:
    """Represents an API endpoint (REST or GraphQL)."""
    name: str
    endpoint_type: str  # viewset, view, graphql_query, graphql_mutation
    actions: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)  # GET, POST, PUT, DELETE
    fields: List[str] = field(default_factory=list)
    source_file: str = ""
    line_number: int = 0


@dataclass
class APISerializer:
    """Represents a Django REST serializer."""
    name: str
    model: str = ""
    fields: List[str] = field(default_factory=list)
    source_file: str = ""


@dataclass
class URLPattern:
    """Represents a URL pattern."""
    path: str
    viewset: str = ""
    name: str = ""
    source_file: str = ""


@dataclass
class UIService:
    """Represents a UI service (TypeScript/JavaScript)."""
    name: str
    methods: List['UIServiceMethod'] = field(default_factory=list)
    source_file: str = ""


@dataclass
class UIServiceMethod:
    """Represents a method in a UI service."""
    name: str
    api_endpoint: str = ""
    http_method: str = ""  # GET, POST, PUT, DELETE


@dataclass
class UIComponent:
    """Represents a UI component."""
    name: str
    used_services: List[str] = field(default_factory=list)
    source_file: str = ""


@dataclass
class UITest:
    """Represents a UI test."""
    name: str
    tested_method: str = ""
    service_name: str = ""
    source_file: str = ""


@dataclass
class EndpointChange:
    """Represents a change in an endpoint."""
    change_type: str  # added, removed, modified
    endpoint_name: str
    details: str = ""


@dataclass
class CorrelationResult:
    """Result of correlation analysis."""
    api_endpoint: str
    ui_service: str
    service_method: str = ""
    test_name: str = ""
    confidence: float = 0.0
    has_api: bool = False
    has_service: bool = False
    has_test: bool = False


@dataclass
class GapInfo:
    """Information about a detected gap."""
    api_endpoint: str = ""
    service_name: str = ""
    severity: str = "warning"  # error, warning, info
    message: str = ""


@dataclass
class GapDetectionResult:
    """Result of gap detection analysis."""
    missing_ui_services: List[GapInfo] = field(default_factory=list)
    missing_ui_tests: List[GapInfo] = field(default_factory=list)
    missing_api_endpoints: List[GapInfo] = field(default_factory=list)


@dataclass
class CoherenceReport:
    """Complete coherence analysis report."""
    status: str
    timestamp: str
    summary: Dict[str, Any] = field(default_factory=dict)
    correlations: List[CorrelationResult] = field(default_factory=list)
    gaps: GapDetectionResult = field(default_factory=GapDetectionResult)
    confidence_score: float = 0.0
    changes: List[EndpointChange] = field(default_factory=list)


# ============================================================================
# COHERENCE ANALYZER AGENT
# ============================================================================

class CoherenceAnalyzerAgent(SDLCAgent):
    """
    Agent for analyzing UI/API coherence.

    Responsibilities:
    - Parse API files (views.py, serializers.py, urls.py) using AST
    - Parse UI files (services, components, tests) using AST/regex
    - Detect endpoint changes (REST, GraphQL)
    - Perform correlation analysis (API → Service → Test)
    - Detect gaps (missing services, missing tests)
    - Calculate confidence scores
    - Generate JSON reports
    """

    def __init__(self, name: str = "CoherenceAnalyzer", config: Optional[Dict[str, Any]] = None):
        """Initialize the CoherenceAnalyzerAgent."""
        default_config = {
            "project_root": ".",
            "api_patterns": ["**/views.py", "**/serializers.py", "**/urls.py"],
            "ui_patterns": ["**/services/*.ts", "**/services/*.js", "**/__tests__/*.test.js"],
            "confidence_threshold": 70.0,
        }
        if config:
            default_config.update(config)

        super().__init__(name=name, phase="testing", config=default_config)
        self.logger.info(f"Initialized {name} with config: {self.config}")

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the coherence analysis.

        Args:
            input_data: Dictionary with analysis parameters
                - git_diff: Git diff reference (optional)
                - base_branch: Base branch for comparison (optional)
                - files: List of files to analyze (optional)

        Returns:
            Dictionary with analysis results
        """
        self.logger.info("Starting coherence analysis")

        git_diff = input_data.get('git_diff')
        base_branch = input_data.get('base_branch', 'main')
        files = input_data.get('files', [])

        if git_diff:
            report = self.analyze_git_changes(git_diff)
        elif files:
            report = self.analyze_files(files)
        else:
            # Analyze entire project
            report = self.analyze_project()

        return {
            'report': report,
            'status': report['status'],
            'confidence_score': report['confidence_score']
        }

    # ========================================================================
    # AST PARSING - API FILES
    # ========================================================================

    def parse_api_views(self, code: str, source_file: str = "") -> List[APIEndpoint]:
        """
        Parse Django views.py using AST.

        Args:
            code: Python code to parse
            source_file: Source file path

        Returns:
            List of APIEndpoint objects
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.logger.error(f"Syntax error parsing views: {e}")
            raise

        endpoints = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it's a ViewSet or APIView
                is_viewset = self._is_viewset_class(node)

                if is_viewset:
                    endpoint = self._parse_viewset(node, source_file)
                    endpoints.append(endpoint)

        return endpoints

    def _is_viewset_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a ViewSet."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                if 'ViewSet' in base.id or 'APIView' in base.id:
                    return True
            elif isinstance(base, ast.Attribute):
                # Handle viewsets.ModelViewSet
                if 'ViewSet' in base.attr or 'APIView' in base.attr:
                    return True
        return False

    def _parse_viewset(self, node: ast.ClassDef, source_file: str) -> APIEndpoint:
        """Parse a Django ViewSet class."""
        actions = []
        methods = []

        # Find @action decorators
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name) and decorator.func.id == 'action':
                            actions.append(item.name)

                            # Extract HTTP methods from decorator
                            for keyword in decorator.keywords:
                                if keyword.arg == 'methods':
                                    if isinstance(keyword.value, ast.List):
                                        for elt in keyword.value.elts:
                                            if isinstance(elt, ast.Constant):
                                                methods.append(elt.value.upper())

        # Default CRUD methods for ModelViewSet
        is_model_viewset = any(
            (isinstance(base, ast.Name) and 'ModelViewSet' in base.id) or
            (isinstance(base, ast.Attribute) and 'ModelViewSet' in base.attr)
            for base in node.bases
        )

        is_readonly_viewset = any(
            (isinstance(base, ast.Name) and 'ReadOnlyModelViewSet' in base.id) or
            (isinstance(base, ast.Attribute) and 'ReadOnlyModelViewSet' in base.attr)
            for base in node.bases
        )

        if is_model_viewset:
            methods.extend(['GET', 'POST', 'PUT', 'DELETE'])
        elif is_readonly_viewset:
            methods.extend(['GET'])

        return APIEndpoint(
            name=node.name,
            endpoint_type='viewset',
            actions=actions,
            methods=list(set(methods)),
            source_file=source_file,
            line_number=node.lineno
        )

    def parse_api_serializers(self, code: str, source_file: str = "") -> List[APISerializer]:
        """
        Parse Django serializers.py using AST.

        Args:
            code: Python code to parse
            source_file: Source file path

        Returns:
            List of APISerializer objects
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.logger.error(f"Syntax error parsing serializers: {e}")
            raise

        serializers = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_serializer = self._is_serializer_class(node)

                if is_serializer:
                    serializer = self._parse_serializer(node, source_file)
                    serializers.append(serializer)

        return serializers

    def _is_serializer_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is a Serializer."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                if 'Serializer' in base.id:
                    return True
            elif isinstance(base, ast.Attribute):
                # Handle serializers.ModelSerializer
                if 'Serializer' in base.attr:
                    return True
        return False

    def _parse_serializer(self, node: ast.ClassDef, source_file: str) -> APISerializer:
        """Parse a Django Serializer class."""
        fields = []
        model = ""

        # Find Meta class
        for item in node.body:
            if isinstance(item, ast.ClassDef) and item.name == 'Meta':
                for meta_item in item.body:
                    if isinstance(meta_item, ast.Assign):
                        for target in meta_item.targets:
                            if isinstance(target, ast.Name):
                                if target.id == 'fields':
                                    # Extract fields list
                                    if isinstance(meta_item.value, ast.List):
                                        for elt in meta_item.value.elts:
                                            if isinstance(elt, ast.Constant):
                                                fields.append(elt.value)
                                elif target.id == 'model':
                                    if isinstance(meta_item.value, ast.Name):
                                        model = meta_item.value.id

        return APISerializer(
            name=node.name,
            model=model,
            fields=fields,
            source_file=source_file
        )

    def parse_api_urls(self, code: str, source_file: str = "") -> List[URLPattern]:
        """
        Parse Django urls.py using AST.

        Args:
            code: Python code to parse
            source_file: Source file path

        Returns:
            List of URLPattern objects
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.logger.error(f"Syntax error parsing URLs: {e}")
            raise

        url_patterns = []

        # Look for router.register() calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Attribute):
                    if call.func.attr == 'register':
                        # Extract path and viewset
                        if len(call.args) >= 2:
                            path = call.args[0].value if isinstance(call.args[0], ast.Constant) else ""
                            viewset = call.args[1].id if isinstance(call.args[1], ast.Name) else ""

                            url_patterns.append(URLPattern(
                                path=path,
                                viewset=viewset,
                                source_file=source_file
                            ))

        return url_patterns

    # ========================================================================
    # ENDPOINT CHANGE DETECTION
    # ========================================================================

    def detect_endpoint_changes(
        self,
        old_code: str,
        new_code: str,
        file_type: str = 'views'
    ) -> List[EndpointChange]:
        """
        Detect changes in API endpoints between two versions.

        Args:
            old_code: Old version of code
            new_code: New version of code
            file_type: Type of file (views, serializers, urls)

        Returns:
            List of EndpointChange objects
        """
        changes = []

        if file_type == 'views':
            old_endpoints = self.parse_api_views(old_code)
            new_endpoints = self.parse_api_views(new_code)

            old_names = {e.name for e in old_endpoints}
            new_names = {e.name for e in new_endpoints}

            # Detect additions
            for name in new_names - old_names:
                changes.append(EndpointChange(
                    change_type='added',
                    endpoint_name=name,
                    details=f"New endpoint added: {name}"
                ))

            # Detect deletions
            for name in old_names - new_names:
                changes.append(EndpointChange(
                    change_type='removed',
                    endpoint_name=name,
                    details=f"Endpoint removed: {name}"
                ))

            # Detect modifications
            for name in old_names & new_names:
                old_ep = next(e for e in old_endpoints if e.name == name)
                new_ep = next(e for e in new_endpoints if e.name == name)

                if old_ep.actions != new_ep.actions or old_ep.methods != new_ep.methods:
                    changes.append(EndpointChange(
                        change_type='modified',
                        endpoint_name=name,
                        details=f"Actions/methods changed: {old_ep.actions}/{old_ep.methods} -> {new_ep.actions}/{new_ep.methods}"
                    ))
                # Also detect changes in the code itself (decorator parameters, etc.)
                elif old_code != new_code:
                    # Check if this specific class changed
                    old_class_code = self._extract_class_code(old_code, name)
                    new_class_code = self._extract_class_code(new_code, name)
                    if old_class_code != new_class_code:
                        changes.append(EndpointChange(
                            change_type='modified',
                            endpoint_name=name,
                            details=f"Endpoint implementation changed: {name}"
                        ))

        return changes

    def _extract_class_code(self, code: str, class_name: str) -> str:
        """Extract the code for a specific class."""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    return ast.get_source_segment(code, node) or ""
        except:
            pass
        return ""

    def detect_graphql_changes(self, old_schema: str, new_schema: str) -> List[EndpointChange]:
        """
        Detect changes in GraphQL schema.

        Args:
            old_schema: Old GraphQL schema
            new_schema: New GraphQL schema

        Returns:
            List of EndpointChange objects
        """
        changes = []

        # Simple regex-based detection for type Query/Mutation
        old_queries = set(re.findall(r'(\w+):\s*\[?\w+\]?', old_schema))
        new_queries = set(re.findall(r'(\w+):\s*\[?\w+\]?', new_schema))

        for query in new_queries - old_queries:
            changes.append(EndpointChange(
                change_type='added',
                endpoint_name=query,
                details=f"New GraphQL query/mutation: {query}"
            ))

        for query in old_queries - new_queries:
            changes.append(EndpointChange(
                change_type='removed',
                endpoint_name=query,
                details=f"GraphQL query/mutation removed: {query}"
            ))

        return changes

    # ========================================================================
    # UI PARSING
    # ========================================================================

    def parse_ui_services(self, code: str, source_file: str = "") -> List[UIService]:
        """
        Parse UI service files (TypeScript/JavaScript).

        Args:
            code: JavaScript/TypeScript code
            source_file: Source file path

        Returns:
            List of UIService objects
        """
        services = []

        # Regex to find class declarations
        class_pattern = r'(?:export\s+)?class\s+(\w+Service)\s*\{'
        classes = re.finditer(class_pattern, code)

        for class_match in classes:
            service_name = class_match.group(1)
            class_start = class_match.start()

            # Find methods in this class
            methods = self._parse_service_methods(code, class_start)

            services.append(UIService(
                name=service_name,
                methods=methods,
                source_file=source_file
            ))

        return services

    def _parse_service_methods(self, code: str, class_start: int) -> List[UIServiceMethod]:
        """Parse methods from a service class."""
        methods = []

        # Regex to find async methods with axios calls
        method_pattern = r'async\s+(\w+)\s*\([^)]*\)\s*\{[^}]*axios\.(get|post|put|delete)\([\'"]([^\'"]+)'
        method_matches = re.finditer(method_pattern, code[class_start:])

        for match in method_matches:
            method_name = match.group(1)
            http_method = match.group(2).upper()
            api_endpoint = match.group(3)

            methods.append(UIServiceMethod(
                name=method_name,
                api_endpoint=api_endpoint,
                http_method=http_method
            ))

        return methods

    def parse_ui_components(self, code: str, source_file: str = "") -> List[UIComponent]:
        """
        Parse UI components (React/Angular).

        Args:
            code: JavaScript/TypeScript code
            source_file: Source file path

        Returns:
            List of UIComponent objects
        """
        components = []

        # Regex to find React function components
        func_pattern = r'(?:export\s+)?function\s+(\w+)\s*\('
        func_matches = re.finditer(func_pattern, code)

        for match in func_matches:
            component_name = match.group(1)

            # Find service usage
            used_services = self._find_used_services(code, match.start())

            components.append(UIComponent(
                name=component_name,
                used_services=used_services,
                source_file=source_file
            ))

        return components

    def _find_used_services(self, code: str, start_pos: int) -> List[str]:
        """Find services used in a component."""
        services = []

        # Look for "new SomeService()" patterns
        service_pattern = r'new\s+(\w+Service)\s*\('
        matches = re.finditer(service_pattern, code[start_pos:start_pos+2000])

        for match in matches:
            services.append(match.group(1))

        return list(set(services))

    def parse_ui_tests(self, code: str, source_file: str = "") -> List[UITest]:
        """
        Parse UI test files (Jest/Jasmine).

        Args:
            code: JavaScript test code
            source_file: Source file path

        Returns:
            List of UITest objects
        """
        tests = []

        # Regex to find test cases
        test_pattern = r'(?:test|it)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        test_matches = re.finditer(test_pattern, code)

        # Find service name from describe block
        service_pattern = r'describe\s*\(\s*[\'"](\w+)[\'"]'
        service_match = re.search(service_pattern, code)
        service_name = service_match.group(1) if service_match else ""

        for match in test_matches:
            test_name = match.group(1)
            test_start = match.start()

            # Try to find tested method
            tested_method = self._find_tested_method(code, test_start, test_name)

            tests.append(UITest(
                name=test_name,
                tested_method=tested_method,
                service_name=service_name,
                source_file=source_file
            ))

        return tests

    def _find_tested_method(self, code: str, test_start: int, test_name: str) -> str:
        """Find which method is being tested."""
        # Look for method calls in the test - more flexible pattern
        # Matches: userService.methodName( or new Service().methodName(
        method_pattern = r'(?:\w+Service|\w+service)\s*\.\s*(\w+)\s*\('
        method_matches = re.finditer(method_pattern, code[test_start:test_start+500])

        for match in method_matches:
            return match.group(1)

        # Alternative pattern: await service.method()
        await_pattern = r'await\s+\w+\.\s*(\w+)\s*\('
        await_matches = re.finditer(await_pattern, code[test_start:test_start+500])

        for match in await_matches:
            return match.group(1)

        # Fallback: try to infer from test name
        words = test_name.lower().split()
        if 'fetch' in words or 'get' in words:
            return 'get' + ''.join(word.capitalize() for word in words if word not in ['should', 'fetch', 'get'])
        elif 'activate' in words:
            return 'activate' + ''.join(word.capitalize() for word in words if word not in ['should', 'activate'])

        return ""

    # ========================================================================
    # CORRELATION ANALYSIS
    # ========================================================================

    def correlate_api_to_ui(
        self,
        api_endpoints: List[APIEndpoint],
        ui_services: List[UIService]
    ) -> List[CorrelationResult]:
        """
        Correlate API endpoints to UI services.

        Args:
            api_endpoints: List of API endpoints
            ui_services: List of UI services

        Returns:
            List of CorrelationResult objects
        """
        correlations = []

        for api_endpoint in api_endpoints:
            for ui_service in ui_services:
                # Calculate confidence score
                confidence = self._calculate_name_similarity(
                    api_endpoint.name,
                    ui_service.name
                )

                if confidence > 30.0:  # Minimum threshold
                    correlations.append(CorrelationResult(
                        api_endpoint=api_endpoint.name,
                        ui_service=ui_service.name,
                        confidence=confidence,
                        has_api=True,
                        has_service=True,
                        has_test=False
                    ))

        return correlations

    def correlate_service_to_test(
        self,
        ui_services: List[UIService],
        ui_tests: List[UITest]
    ) -> List[CorrelationResult]:
        """
        Correlate UI services to UI tests.

        Args:
            ui_services: List of UI services
            ui_tests: List of UI tests

        Returns:
            List of CorrelationResult objects
        """
        correlations = []

        for service in ui_services:
            for method in service.methods:
                for test in ui_tests:
                    if (test.service_name == service.name or
                        test.tested_method == method.name):
                        correlations.append(CorrelationResult(
                            api_endpoint="",
                            ui_service=service.name,
                            service_method=method.name,
                            test_name=test.name,
                            confidence=90.0,  # High confidence for direct matches
                            has_api=False,
                            has_service=True,
                            has_test=True
                        ))

        return correlations

    def correlate_full_chain(
        self,
        api_endpoints: List[APIEndpoint],
        ui_services: List[UIService],
        ui_tests: List[UITest]
    ) -> List[CorrelationResult]:
        """
        Correlate full chain: API → Service → Test.

        Args:
            api_endpoints: List of API endpoints
            ui_services: List of UI services
            ui_tests: List of UI tests

        Returns:
            List of CorrelationResult objects with complete chains
        """
        chains = []

        api_to_service = self.correlate_api_to_ui(api_endpoints, ui_services)
        service_to_test = self.correlate_service_to_test(ui_services, ui_tests)

        # Build complete chains
        for api_corr in api_to_service:
            for test_corr in service_to_test:
                if api_corr.ui_service == test_corr.ui_service:
                    chains.append(CorrelationResult(
                        api_endpoint=api_corr.api_endpoint,
                        ui_service=api_corr.ui_service,
                        service_method=test_corr.service_method,
                        test_name=test_corr.test_name,
                        confidence=(api_corr.confidence + test_corr.confidence) / 2,
                        has_api=True,
                        has_service=True,
                        has_test=True
                    ))

        return chains

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity between two names.

        Args:
            name1: First name
            name2: Second name

        Returns:
            Similarity score (0-100)
        """
        if not name1 or not name2:
            return 0.0

        # Normalize names
        n1 = name1.lower().replace('viewset', '').replace('service', '')
        n2 = name2.lower().replace('viewset', '').replace('service', '')

        # Exact match (after normalization)
        if n1 == n2:
            return 95.0

        # Check if one contains the other - but penalize if lengths are very different
        if n1 in n2 or n2 in n1:
            # Calculate length ratio
            min_len = min(len(n1), len(n2))
            max_len = max(len(n1), len(n2))
            length_ratio = min_len / max_len if max_len > 0 else 0

            # If length ratio is good (e.g., "User" in "UserService" = 0.5+), high score
            # If length ratio is poor (e.g., "User" in "UserProfileService" = 0.25), lower score
            if length_ratio >= 0.7:
                return 80.0
            elif length_ratio >= 0.5:
                return 70.0
            else:
                return 55.0

        # Check common prefix
        common_prefix_len = 0
        for c1, c2 in zip(n1, n2):
            if c1 == c2:
                common_prefix_len += 1
            else:
                break

        if common_prefix_len >= 3:
            return 60.0 + (common_prefix_len * 2)

        return 20.0

    # ========================================================================
    # GAP DETECTION
    # ========================================================================

    def detect_gaps(
        self,
        api_endpoints: List[APIEndpoint],
        ui_services: List[UIService],
        ui_tests: List[UITest]
    ) -> GapDetectionResult:
        """
        Detect gaps in coverage.

        Args:
            api_endpoints: List of API endpoints
            ui_services: List of UI services
            ui_tests: List of UI tests

        Returns:
            GapDetectionResult with detected gaps
        """
        result = GapDetectionResult()

        # Find API endpoints without UI services
        service_names = {s.name for s in ui_services}

        for endpoint in api_endpoints:
            # Check if there's a corresponding service
            has_service = any(
                self._calculate_name_similarity(endpoint.name, sn) > 50.0
                for sn in service_names
            )

            if not has_service:
                result.missing_ui_services.append(GapInfo(
                    api_endpoint=endpoint.name,
                    severity='warning',
                    message=f"No UI service found for API endpoint: {endpoint.name}"
                ))

        # Find UI services without tests
        tested_services = {t.service_name for t in ui_tests}

        for service in ui_services:
            if service.name not in tested_services:
                result.missing_ui_tests.append(GapInfo(
                    service_name=service.name,
                    severity='error',
                    message=f"No tests found for UI service: {service.name}"
                ))

        return result

    # ========================================================================
    # CONFIDENCE SCORING
    # ========================================================================

    def calculate_confidence_score(
        self,
        api_name: str,
        ui_name: str,
        has_common_fields: bool,
        common_field_count: int = 0
    ) -> float:
        """
        Calculate confidence score for correlation.

        Args:
            api_name: API endpoint name
            ui_name: UI service name
            has_common_fields: Whether they have common fields
            common_field_count: Number of common fields

        Returns:
            Confidence score (0-100)
        """
        base_score = self._calculate_name_similarity(api_name, ui_name)

        # Boost score if common fields exist
        if has_common_fields:
            field_boost = min(common_field_count * 2, 20)
            base_score = min(base_score + field_boost, 100.0)

        return base_score

    # ========================================================================
    # CLI INTERFACE
    # ========================================================================

    def parse_cli_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parse CLI arguments.

        Args:
            args: List of arguments (for testing)

        Returns:
            Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description='Analyze UI/API coherence'
        )

        parser.add_argument(
            '--git-diff',
            help='Git diff reference (e.g., HEAD~1)'
        )

        parser.add_argument(
            '--base-branch',
            default='main',
            help='Base branch for comparison (default: main)'
        )

        parser.add_argument(
            '--output',
            default='/tmp/coherence_report.json',
            help='Output file for JSON report'
        )

        parser.add_argument(
            '--threshold',
            type=float,
            default=70.0,
            help='Confidence threshold (0-100, default: 70.0)'
        )

        return parser.parse_args(args)

    # ========================================================================
    # REPORT GENERATION
    # ========================================================================

    def generate_report(
        self,
        api_endpoints: List[APIEndpoint],
        ui_services: List[UIService],
        ui_tests: List[UITest],
        changes: Optional[List[EndpointChange]] = None
    ) -> Dict[str, Any]:
        """
        Generate coherence analysis report.

        Args:
            api_endpoints: List of API endpoints
            ui_services: List of UI services
            ui_tests: List of UI tests
            changes: List of endpoint changes (optional)

        Returns:
            Report dictionary
        """
        correlations = self.correlate_full_chain(api_endpoints, ui_services, ui_tests)
        gaps = self.detect_gaps(api_endpoints, ui_services, ui_tests)

        # Calculate overall confidence
        if correlations:
            overall_confidence = sum(c.confidence for c in correlations) / len(correlations)
        else:
            overall_confidence = 0.0

        # Calculate coverage rates
        total_endpoints = len(api_endpoints)
        endpoints_with_services = len([c for c in correlations if c.has_service])
        service_coverage = (endpoints_with_services / total_endpoints * 100) if total_endpoints else 0.0

        total_services = len(ui_services)
        services_with_tests = len(set(c.ui_service for c in correlations if c.has_test))
        test_coverage = (services_with_tests / total_services * 100) if total_services else 0.0

        report = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_api_endpoints': total_endpoints,
                'total_ui_services': total_services,
                'total_ui_tests': len(ui_tests),
                'correlation_rate': service_coverage,
                'test_coverage_rate': test_coverage,
            },
            'correlations': [asdict(c) for c in correlations],
            'gaps': {
                'missing_ui_services': [asdict(g) for g in gaps.missing_ui_services],
                'missing_ui_tests': [asdict(g) for g in gaps.missing_ui_tests],
                'missing_api_endpoints': [asdict(g) for g in gaps.missing_api_endpoints],
            },
            'confidence_score': overall_confidence,
            'changes': [asdict(c) for c in (changes or [])],
        }

        return report

    # ========================================================================
    # GIT INTEGRATION
    # ========================================================================

    def get_changed_files_from_git(self, git_ref: str) -> List[str]:
        """
        Get changed files from git diff.

        Args:
            git_ref: Git reference (e.g., HEAD~1, main)

        Returns:
            List of changed file paths
        """
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', git_ref],
                capture_output=True,
                text=True,
                check=False  # Don't auto-raise, we'll check manually
            )

            # Check for errors manually
            if result.returncode != 0:
                error_msg = result.stderr.strip() if result.stderr else f"Git command failed with code {result.returncode}"
                self.logger.error(f"Git diff failed: {error_msg}")
                raise RuntimeError(f"Git diff failed: {error_msg}")

            files = result.stdout.strip().split('\n')
            return [f for f in files if f]

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') else str(e)
            self.logger.error(f"Git diff failed: {error_msg}")
            raise RuntimeError(f"Git diff failed: {error_msg}")

    def filter_relevant_files(self, files: List[str]) -> List[str]:
        """
        Filter relevant files for analysis.

        Args:
            files: List of all files

        Returns:
            List of relevant files (Python, JS, TS)
        """
        relevant_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx'}
        return [
            f for f in files
            if Path(f).suffix in relevant_extensions
        ]

    def analyze_git_changes(self, git_ref: str) -> Dict[str, Any]:
        """
        Analyze changes from git diff.

        Args:
            git_ref: Git reference

        Returns:
            Analysis report
        """
        changed_files = self.get_changed_files_from_git(git_ref)
        relevant_files = self.filter_relevant_files(changed_files)

        return self.analyze_files(relevant_files)

    def analyze_files(self, files: List[str]) -> Dict[str, Any]:
        """
        Analyze specific files.

        Args:
            files: List of file paths

        Returns:
            Analysis report
        """
        api_endpoints = []
        ui_services = []
        ui_tests = []

        for file_path in files:
            try:
                content = Path(file_path).read_text()

                if file_path.endswith('views.py'):
                    api_endpoints.extend(self.parse_api_views(content, file_path))
                elif file_path.endswith(('.ts', '.js')) and 'service' in file_path.lower():
                    ui_services.extend(self.parse_ui_services(content, file_path))
                elif file_path.endswith(('.test.js', '.test.ts', '.spec.js', '.spec.ts')):
                    ui_tests.extend(self.parse_ui_tests(content, file_path))

            except Exception as e:
                self.logger.warning(f"Error parsing {file_path}: {e}")

        return self.generate_report(api_endpoints, ui_services, ui_tests)

    def analyze_project(self) -> Dict[str, Any]:
        """
        Analyze entire project.

        Returns:
            Analysis report
        """
        project_root = Path(self.config.get('project_root', '.'))

        api_endpoints = []
        ui_services = []
        ui_tests = []

        # Find all relevant files
        for pattern in self.config['api_patterns']:
            for file_path in project_root.glob(pattern):
                try:
                    content = file_path.read_text()
                    if 'views' in file_path.name:
                        api_endpoints.extend(self.parse_api_views(content, str(file_path)))
                except Exception as e:
                    self.logger.warning(f"Error parsing {file_path}: {e}")

        for pattern in self.config['ui_patterns']:
            for file_path in project_root.glob(pattern):
                try:
                    content = file_path.read_text()
                    if 'test' in file_path.name:
                        ui_tests.extend(self.parse_ui_tests(content, str(file_path)))
                    else:
                        ui_services.extend(self.parse_ui_services(content, str(file_path)))
                except Exception as e:
                    self.logger.warning(f"Error parsing {file_path}: {e}")

        return self.generate_report(api_endpoints, ui_services, ui_tests)

    def parse_file(self, file_path: str) -> Any:
        """
        Parse a single file.

        Args:
            file_path: Path to file

        Returns:
            Parsed result

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return path.read_text()


# ============================================================================
# MAIN / CLI ENTRY POINT
# ============================================================================

def main():
    """Main entry point for CLI."""
    agent = CoherenceAnalyzerAgent()
    args = agent.parse_cli_args()

    logging.basicConfig(level=logging.INFO)

    # Run analysis
    input_data = {
        'git_diff': args.git_diff,
        'base_branch': args.base_branch,
    }

    result = agent.run(input_data)
    report = result['report']

    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to: {output_path}")
    print(f"Confidence score: {report['confidence_score']:.2f}%")
    print(f"Gaps found: {len(report['gaps']['missing_ui_services']) + len(report['gaps']['missing_ui_tests'])}")

    # Exit code based on confidence threshold
    if report['confidence_score'] < args.threshold:
        print(f"WARNING: Confidence score below threshold ({args.threshold})")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
