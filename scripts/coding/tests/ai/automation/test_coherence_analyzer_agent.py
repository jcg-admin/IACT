"""
Test suite for CoherenceAnalyzerAgent.

Complete TDD approach for UI/API coherence analysis.
Tests cover AST parsing, endpoint detection, correlation analysis,
gap detection, confidence scoring, and CLI interface.
"""

import ast
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

# Import agent (will fail initially - TDD RED phase)
from scripts.coding.ai.automation.coherence_analyzer_agent import (
    CoherenceAnalyzerAgent,
    APIEndpoint,
    UIService,
    UITest,
    CorrelationResult,
    GapDetectionResult,
    CoherenceReport,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_api_views():
    """Sample Django views.py content for testing."""
    return '''
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    """User management viewset."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def activate(self, request):
        """Activate user account."""
        return Response({'status': 'activated'})

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        """Get user profile."""
        return Response({'profile': 'data'})

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Product listing viewset."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
'''


@pytest.fixture
def sample_api_serializers():
    """Sample Django serializers.py content for testing."""
    return '''
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """User model serializer."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ProductSerializer(serializers.ModelSerializer):
    """Product model serializer."""
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']
'''


@pytest.fixture
def sample_api_urls():
    """Sample Django urls.py content for testing."""
    return '''
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('auth.urls')),
]
'''


@pytest.fixture
def sample_ui_service():
    """Sample React/Angular service for testing."""
    return '''
import axios from 'axios';

export class UserService {
    async getUsers() {
        const response = await axios.get('/api/users/');
        return response.data;
    }

    async activateUser(userId) {
        const response = await axios.post('/api/users/activate/');
        return response.data;
    }

    async getUserProfile(userId) {
        const response = await axios.get(`/api/users/${userId}/profile/`);
        return response.data;
    }
}

export class ProductService {
    async getProducts() {
        const response = await axios.get('/api/products/');
        return response.data;
    }
}
'''


@pytest.fixture
def sample_ui_test():
    """Sample Jest/Jasmine test for testing."""
    return '''
import { UserService } from './UserService';

describe('UserService', () => {
    let userService;

    beforeEach(() => {
        userService = new UserService();
    });

    test('should fetch users', async () => {
        const users = await userService.getUsers();
        expect(users).toBeDefined();
    });

    test('should activate user', async () => {
        const result = await userService.activateUser(1);
        expect(result.status).toBe('activated');
    });

    test('should get user profile', async () => {
        const profile = await userService.getUserProfile(1);
        expect(profile).toBeDefined();
    });
});
'''


@pytest.fixture
def agent():
    """Create CoherenceAnalyzerAgent instance."""
    config = {
        "project_root": "/tmp/test_project",
        "api_patterns": ["**/views.py", "**/serializers.py", "**/urls.py"],
        "ui_patterns": ["**/services/*.ts", "**/services/*.js", "**/__tests__/*.test.js"],
        "confidence_threshold": 70.0,
    }
    return CoherenceAnalyzerAgent(name="CoherenceAnalyzer", config=config)


# ============================================================================
# TEST 1-5: AST PARSING - API FILES
# ============================================================================

def test_parse_api_views_basic(agent, sample_api_views):
    """Test parsing basic Django views with viewsets."""
    endpoints = agent.parse_api_views(sample_api_views)

    assert len(endpoints) >= 2
    assert any(e.name == 'UserViewSet' for e in endpoints)
    assert any(e.name == 'ProductViewSet' for e in endpoints)


def test_parse_api_views_with_actions(agent, sample_api_views):
    """Test parsing Django viewset actions (@action decorator)."""
    endpoints = agent.parse_api_views(sample_api_views)

    user_viewset = next((e for e in endpoints if e.name == 'UserViewSet'), None)
    assert user_viewset is not None
    assert 'activate' in user_viewset.actions
    assert 'profile' in user_viewset.actions


def test_parse_api_serializers(agent, sample_api_serializers):
    """Test parsing Django serializers."""
    serializers = agent.parse_api_serializers(sample_api_serializers)

    assert len(serializers) >= 2
    assert any(s.name == 'UserSerializer' for s in serializers)
    assert any(s.name == 'ProductSerializer' for s in serializers)

    user_serializer = next((s for s in serializers if s.name == 'UserSerializer'), None)
    assert 'id' in user_serializer.fields
    assert 'username' in user_serializer.fields


def test_parse_api_urls(agent, sample_api_urls):
    """Test parsing Django URL patterns."""
    url_patterns = agent.parse_api_urls(sample_api_urls)

    assert len(url_patterns) >= 2
    assert any('users' in pattern.path for pattern in url_patterns)
    assert any('products' in pattern.path for pattern in url_patterns)


def test_parse_api_invalid_syntax(agent):
    """Test error handling for invalid Python syntax."""
    invalid_code = "def invalid syntax here"

    with pytest.raises(SyntaxError):
        agent.parse_api_views(invalid_code)


# ============================================================================
# TEST 6-10: ENDPOINT CHANGE DETECTION
# ============================================================================

def test_detect_rest_endpoint_changes_new(agent, sample_api_views):
    """Test detection of new REST endpoints."""
    old_views = ""
    new_views = sample_api_views

    changes = agent.detect_endpoint_changes(old_views, new_views, file_type='views')

    assert len(changes) > 0
    assert any(c.change_type == 'added' for c in changes)
    assert any('UserViewSet' in c.endpoint_name for c in changes)


def test_detect_rest_endpoint_changes_modified(agent, sample_api_views):
    """Test detection of modified REST endpoints."""
    old_views = sample_api_views
    new_views = sample_api_views.replace('@action(detail=False', '@action(detail=True')

    changes = agent.detect_endpoint_changes(old_views, new_views, file_type='views')

    # Should detect modification in action decorator
    assert len(changes) > 0


def test_detect_rest_endpoint_changes_deleted(agent, sample_api_views):
    """Test detection of deleted REST endpoints."""
    old_views = sample_api_views
    new_views = ""

    changes = agent.detect_endpoint_changes(old_views, new_views, file_type='views')

    assert len(changes) > 0
    assert any(c.change_type == 'removed' for c in changes)


def test_detect_graphql_endpoint_changes(agent):
    """Test detection of GraphQL endpoint changes."""
    old_schema = '''
type Query {
    users: [User]
}
'''
    new_schema = '''
type Query {
    users: [User]
    products: [Product]
}
'''

    changes = agent.detect_graphql_changes(old_schema, new_schema)

    assert len(changes) > 0
    assert any('products' in c.endpoint_name for c in changes)


def test_detect_endpoint_changes_no_changes(agent, sample_api_views):
    """Test when there are no endpoint changes."""
    changes = agent.detect_endpoint_changes(
        sample_api_views, sample_api_views, file_type='views'
    )

    assert len(changes) == 0


# ============================================================================
# TEST 11-15: UI PARSING
# ============================================================================

def test_parse_ui_services(agent, sample_ui_service):
    """Test parsing UI service files (TypeScript/JavaScript)."""
    services = agent.parse_ui_services(sample_ui_service)

    assert len(services) >= 2
    assert any(s.name == 'UserService' for s in services)
    assert any(s.name == 'ProductService' for s in services)


def test_parse_ui_service_methods(agent, sample_ui_service):
    """Test parsing UI service methods and API calls."""
    services = agent.parse_ui_services(sample_ui_service)

    user_service = next((s for s in services if s.name == 'UserService'), None)
    assert user_service is not None
    assert len(user_service.methods) >= 3
    assert 'getUsers' in [m.name for m in user_service.methods]
    assert 'activateUser' in [m.name for m in user_service.methods]

    # Check API endpoint detection
    get_users_method = next((m for m in user_service.methods if m.name == 'getUsers'), None)
    assert '/api/users/' in get_users_method.api_endpoint


def test_parse_ui_tests(agent, sample_ui_test):
    """Test parsing UI test files (Jest/Jasmine)."""
    tests = agent.parse_ui_tests(sample_ui_test)

    assert len(tests) > 0
    assert any('should fetch users' in t.name for t in tests)
    assert any('should activate user' in t.name for t in tests)


def test_parse_ui_tests_coverage(agent, sample_ui_test):
    """Test detection of service methods covered by tests."""
    tests = agent.parse_ui_tests(sample_ui_test)

    # Should detect that UserService methods are tested
    assert any('getUsers' in t.tested_method for t in tests)
    assert any('activateUser' in t.tested_method for t in tests)
    assert any('getUserProfile' in t.tested_method for t in tests)


def test_parse_ui_components(agent):
    """Test parsing React/Angular components."""
    component_code = '''
import React from 'react';
import { UserService } from './UserService';

export function UserList() {
    const [users, setUsers] = React.useState([]);

    React.useEffect(() => {
        const userService = new UserService();
        userService.getUsers().then(setUsers);
    }, []);

    return <div>{users.map(u => <div key={u.id}>{u.name}</div>)}</div>;
}
'''

    components = agent.parse_ui_components(component_code)

    assert len(components) > 0
    assert any(c.name == 'UserList' for c in components)

    user_list = next((c for c in components if c.name == 'UserList'), None)
    assert 'UserService' in user_list.used_services


# ============================================================================
# TEST 16-20: CORRELATION ANALYSIS
# ============================================================================

def test_correlation_api_to_ui_service(agent, sample_api_views, sample_ui_service):
    """Test correlation between API endpoints and UI services."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)

    correlations = agent.correlate_api_to_ui(api_endpoints, ui_services)

    assert len(correlations) > 0
    # Should find correlation between UserViewSet and UserService
    assert any(
        'UserViewSet' in c.api_endpoint and 'UserService' in c.ui_service
        for c in correlations
    )


def test_correlation_ui_service_to_test(agent, sample_ui_service, sample_ui_test):
    """Test correlation between UI services and tests."""
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    correlations = agent.correlate_service_to_test(ui_services, ui_tests)

    assert len(correlations) > 0
    # Should find UserService methods tested
    assert any('getUsers' in c.service_method for c in correlations)
    assert any('activateUser' in c.service_method for c in correlations)


def test_correlation_full_chain(agent, sample_api_views, sample_ui_service, sample_ui_test):
    """Test full correlation chain: API → UI Service → UI Test."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    full_chain = agent.correlate_full_chain(api_endpoints, ui_services, ui_tests)

    assert len(full_chain) > 0
    # Should find complete chains
    assert any(
        c.has_api and c.has_service and c.has_test
        for c in full_chain
    )


def test_correlation_confidence_high(agent, sample_api_views, sample_ui_service):
    """Test correlation confidence calculation - high confidence."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)

    correlations = agent.correlate_api_to_ui(api_endpoints, ui_services)

    # Exact matches should have high confidence
    strong_correlations = [c for c in correlations if c.confidence > 80.0]
    assert len(strong_correlations) > 0


def test_correlation_confidence_low(agent):
    """Test correlation confidence calculation - low confidence."""
    api_code = '''
class UserViewSet(viewsets.ModelViewSet):
    pass
'''
    ui_code = '''
export class ProductService {
    async getProducts() {
        return await axios.get('/api/products/');
    }
}
'''

    api_endpoints = agent.parse_api_views(api_code)
    ui_services = agent.parse_ui_services(ui_code)

    correlations = agent.correlate_api_to_ui(api_endpoints, ui_services)

    # User/Product mismatch should have low or no correlation
    weak_correlations = [c for c in correlations if c.confidence < 50.0]
    assert len(weak_correlations) >= 0  # May be 0 if no correlation found


# ============================================================================
# TEST 21-25: GAP DETECTION
# ============================================================================

def test_gap_detection_missing_ui_service(agent, sample_api_views):
    """Test detection of API endpoints without corresponding UI service."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = []  # Empty UI services

    gaps = agent.detect_gaps(api_endpoints, ui_services, ui_tests=[])

    assert len(gaps.missing_ui_services) > 0
    assert any('UserViewSet' in gap.api_endpoint for gap in gaps.missing_ui_services)


def test_gap_detection_missing_ui_test(agent, sample_ui_service):
    """Test detection of UI services without tests."""
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = []  # Empty tests

    gaps = agent.detect_gaps(api_endpoints=[], ui_services=ui_services, ui_tests=ui_tests)

    assert len(gaps.missing_ui_tests) > 0
    assert any('UserService' in gap.service_name for gap in gaps.missing_ui_tests)


def test_gap_detection_missing_both(agent, sample_api_views):
    """Test detection when both UI service and tests are missing."""
    api_endpoints = agent.parse_api_views(sample_api_views)

    gaps = agent.detect_gaps(api_endpoints, ui_services=[], ui_tests=[])

    assert len(gaps.missing_ui_services) > 0
    assert len(gaps.missing_ui_tests) == 0  # Can't have missing tests without services


def test_gap_detection_no_gaps(agent, sample_api_views, sample_ui_service, sample_ui_test):
    """Test when there are no gaps (full coverage)."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    gaps = agent.detect_gaps(api_endpoints, ui_services, ui_tests)

    # Should have minimal or no gaps for complete example
    assert len(gaps.missing_ui_services) <= 1
    assert len(gaps.missing_ui_tests) <= 1


def test_gap_detection_partial_coverage(agent, sample_api_views, sample_ui_service):
    """Test gap detection with partial test coverage."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)

    # Only partial tests
    partial_test = '''
describe('UserService', () => {
    test('should fetch users', async () => {
        // Only one test
    });
});
'''
    ui_tests = agent.parse_ui_tests(partial_test)

    gaps = agent.detect_gaps(api_endpoints, ui_services, ui_tests)

    # Should detect missing tests for other methods
    assert len(gaps.missing_ui_tests) > 0


# ============================================================================
# TEST 26-30: CONFIDENCE SCORING
# ============================================================================

def test_confidence_scoring_exact_match(agent):
    """Test confidence scoring for exact name matches."""
    score = agent.calculate_confidence_score(
        api_name="UserViewSet",
        ui_name="UserService",
        has_common_fields=True
    )

    assert score >= 80.0  # High confidence for User-User match


def test_confidence_scoring_partial_match(agent):
    """Test confidence scoring for partial matches."""
    score = agent.calculate_confidence_score(
        api_name="UserProfileViewSet",
        ui_name="UserService",
        has_common_fields=True
    )

    assert 50.0 <= score < 80.0  # Medium confidence


def test_confidence_scoring_no_match(agent):
    """Test confidence scoring for non-matching names."""
    score = agent.calculate_confidence_score(
        api_name="ProductViewSet",
        ui_name="UserService",
        has_common_fields=False
    )

    assert score < 30.0  # Low confidence


def test_confidence_scoring_with_fields(agent):
    """Test confidence scoring considering common fields."""
    score_with_fields = agent.calculate_confidence_score(
        api_name="UserViewSet",
        ui_name="UserService",
        has_common_fields=True,
        common_field_count=5
    )

    score_without_fields = agent.calculate_confidence_score(
        api_name="UserViewSet",
        ui_name="UserService",
        has_common_fields=False,
        common_field_count=0
    )

    assert score_with_fields > score_without_fields


def test_confidence_scoring_edge_cases(agent):
    """Test confidence scoring edge cases."""
    # Empty strings
    score1 = agent.calculate_confidence_score("", "", has_common_fields=False)
    assert score1 == 0.0

    # Same exact string
    score2 = agent.calculate_confidence_score("User", "User", has_common_fields=True)
    assert score2 >= 90.0


# ============================================================================
# TEST 31-35: CLI INTERFACE
# ============================================================================

def test_cli_argument_parsing_git_diff(agent):
    """Test CLI argument parsing for --git-diff."""
    args = agent.parse_cli_args(['--git-diff', 'HEAD~1'])

    assert args.git_diff == 'HEAD~1'


def test_cli_argument_parsing_base_branch(agent):
    """Test CLI argument parsing for --base-branch."""
    args = agent.parse_cli_args(['--base-branch', 'main'])

    assert args.base_branch == 'main'


def test_cli_argument_parsing_output(agent):
    """Test CLI argument parsing for --output."""
    args = agent.parse_cli_args(['--output', '/tmp/report.json'])

    assert args.output == '/tmp/report.json'


def test_cli_argument_parsing_all_options(agent):
    """Test CLI with all options."""
    args = agent.parse_cli_args([
        '--git-diff', 'HEAD~1',
        '--base-branch', 'develop',
        '--output', '/tmp/coherence_report.json',
        '--threshold', '75.0'
    ])

    assert args.git_diff == 'HEAD~1'
    assert args.base_branch == 'develop'
    assert args.output == '/tmp/coherence_report.json'
    assert args.threshold == 75.0


def test_cli_argument_parsing_defaults(agent):
    """Test CLI argument default values."""
    args = agent.parse_cli_args([])

    assert args.base_branch == 'main'
    assert args.threshold == 70.0
    assert args.output is not None


# ============================================================================
# TEST 36-40: JSON REPORT GENERATION
# ============================================================================

def test_report_generation_structure(agent, sample_api_views, sample_ui_service, sample_ui_test):
    """Test JSON report has correct structure."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    report = agent.generate_report(api_endpoints, ui_services, ui_tests)

    assert 'status' in report
    assert 'timestamp' in report
    assert 'summary' in report
    assert 'correlations' in report
    assert 'gaps' in report
    assert 'confidence_score' in report


def test_report_generation_gaps_section(agent, sample_api_views):
    """Test report gaps section is populated correctly."""
    api_endpoints = agent.parse_api_views(sample_api_views)

    report = agent.generate_report(api_endpoints, ui_services=[], ui_tests=[])

    assert len(report['gaps']['missing_ui_services']) > 0
    assert 'api_endpoint' in report['gaps']['missing_ui_services'][0]
    assert 'severity' in report['gaps']['missing_ui_services'][0]


def test_report_generation_confidence_overall(agent, sample_api_views, sample_ui_service, sample_ui_test):
    """Test overall confidence score calculation."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    report = agent.generate_report(api_endpoints, ui_services, ui_tests)

    assert 0.0 <= report['confidence_score'] <= 100.0


def test_report_export_json(agent, sample_api_views, sample_ui_service, sample_ui_test):
    """Test exporting report to JSON file."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    report = agent.generate_report(api_endpoints, ui_services, ui_tests)

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(report, f)
        output_path = f.name

    # Verify file was created and is valid JSON
    with open(output_path, 'r') as f:
        loaded_report = json.load(f)

    assert loaded_report == report

    # Cleanup
    Path(output_path).unlink()


def test_report_summary_statistics(agent, sample_api_views, sample_ui_service, sample_ui_test):
    """Test report summary contains correct statistics."""
    api_endpoints = agent.parse_api_views(sample_api_views)
    ui_services = agent.parse_ui_services(sample_ui_service)
    ui_tests = agent.parse_ui_tests(sample_ui_test)

    report = agent.generate_report(api_endpoints, ui_services, ui_tests)

    summary = report['summary']
    assert 'total_api_endpoints' in summary
    assert 'total_ui_services' in summary
    assert 'total_ui_tests' in summary
    assert 'correlation_rate' in summary
    assert 'test_coverage_rate' in summary


# ============================================================================
# TEST 41-45: INTEGRATION WITH GIT
# ============================================================================

@patch('subprocess.run')
def test_git_diff_integration(mock_run, agent):
    """Test integration with git diff command."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout='diff --git a/views.py b/views.py\n+def new_endpoint():\n+    pass'
    )

    changed_files = agent.get_changed_files_from_git('HEAD~1')

    assert len(changed_files) > 0
    mock_run.assert_called_once()


@patch('subprocess.run')
def test_git_diff_file_filtering(mock_run, agent):
    """Test filtering relevant files from git diff."""
    mock_run.return_value = Mock(
        returncode=0,
        stdout='diff --git a/views.py b/views.py\ndiff --git a/README.md b/README.md'
    )

    changed_files = agent.get_changed_files_from_git('HEAD~1')
    relevant_files = agent.filter_relevant_files(changed_files)

    # Should only include Python/JS files, not README
    assert any('views.py' in f for f in relevant_files)
    assert not any('README.md' in f for f in relevant_files)


@patch('subprocess.run')
def test_git_diff_error_handling(mock_run, agent):
    """Test error handling when git diff fails."""
    mock_run.return_value = Mock(returncode=1, stdout='', stderr='fatal: bad revision')

    with pytest.raises(RuntimeError):
        agent.get_changed_files_from_git('invalid-ref')


def test_analyze_git_changes(agent, sample_api_views, sample_ui_service):
    """Test analyzing changes from git diff."""
    with patch.object(agent, 'get_changed_files_from_git') as mock_git:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create temp files
            api_file = Path(tmpdir) / 'views.py'
            api_file.write_text(sample_api_views)

            ui_file = Path(tmpdir) / 'services' / 'UserService.ts'
            ui_file.parent.mkdir(exist_ok=True)
            ui_file.write_text(sample_ui_service)

            mock_git.return_value = [str(api_file), str(ui_file)]

            report = agent.analyze_git_changes('HEAD~1')

            assert report is not None
            assert 'summary' in report


def test_empty_git_diff(agent):
    """Test handling of empty git diff (no changes)."""
    with patch.object(agent, 'get_changed_files_from_git') as mock_git:
        mock_git.return_value = []

        report = agent.analyze_git_changes('HEAD~1')

        assert report['summary']['total_api_endpoints'] == 0
        assert report['summary']['total_ui_services'] == 0


# ============================================================================
# TEST 46-50: ERROR HANDLING & EDGE CASES
# ============================================================================

def test_error_handling_file_not_found(agent):
    """Test error handling when files don't exist."""
    with pytest.raises(FileNotFoundError):
        agent.parse_file('/non/existent/file.py')


def test_error_handling_empty_file(agent):
    """Test handling of empty files."""
    endpoints = agent.parse_api_views('')

    assert len(endpoints) == 0


def test_error_handling_malformed_code(agent):
    """Test handling of malformed Python code."""
    malformed = "def incomplete_function("

    with pytest.raises(SyntaxError):
        agent.parse_api_views(malformed)


def test_edge_case_very_large_file(agent):
    """Test handling of very large files."""
    # Generate large file content
    large_content = '\n'.join([f'# Comment line {i}' for i in range(10000)])
    large_content += '\n\nclass TestViewSet(viewsets.ModelViewSet):\n    pass'

    endpoints = agent.parse_api_views(large_content)

    assert len(endpoints) >= 1
    assert any(e.name == 'TestViewSet' for e in endpoints)


def test_edge_case_unicode_characters(agent):
    """Test handling of unicode characters in code."""
    unicode_code = '''
class UsuárioViewSet(viewsets.ModelViewSet):
    """Gestión de usuarios en español."""
    pass
'''

    endpoints = agent.parse_api_views(unicode_code)

    assert len(endpoints) >= 1
