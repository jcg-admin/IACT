"""
Test suite for DevContainerValidatorAgent.

Tests validation of DevContainer environment including:
- Service health checks (PostgreSQL, MariaDB)
- Version validation (Python, Node)
- Dependency verification (yq, jq, git, npm, pip)
- Port availability
- Environment variables
- devcontainer.json schema validation

TDD Approach: RED phase - tests written before implementation.
"""

import json
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from scripts.coding.ai.automation.devcontainer_validator_agent import (
    DevContainerValidatorAgent,
    ValidationResult,
    CheckStatus
)


@pytest.fixture
def sample_devcontainer_json():
    """Load sample devcontainer.json fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_devcontainer.json"
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def agent():
    """Create DevContainerValidatorAgent instance."""
    config = {
        "project_root": "/workspace",
        "strict_mode": False
    }
    return DevContainerValidatorAgent(name="test_devcontainer_validator", config=config)


@pytest.fixture
def agent_strict():
    """Create DevContainerValidatorAgent instance in strict mode."""
    config = {
        "project_root": "/workspace",
        "strict_mode": True
    }
    return DevContainerValidatorAgent(name="test_devcontainer_validator_strict", config=config)


class TestDevContainerValidatorAgentInit:
    """Test agent initialization."""

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.name == "test_devcontainer_validator"
        assert agent.config["project_root"] == "/workspace"
        assert not agent.config["strict_mode"]

    def test_agent_strict_mode(self, agent_strict):
        """Test agent initializes with strict mode."""
        assert agent_strict.config["strict_mode"] is True


class TestPostgreSQLValidation:
    """Test PostgreSQL service validation."""

    @patch('subprocess.run')
    def test_postgresql_availability_success(self, mock_run, agent):
        """Test PostgreSQL service is available and responding."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="PostgreSQL 15.3",
            stderr=""
        )

        result = agent.check_postgresql_availability(port=5432)

        assert result.status == CheckStatus.PASS
        assert "PostgreSQL" in result.message
        assert result.port == 5432

    @patch('subprocess.run')
    def test_postgresql_availability_failure(self, mock_run, agent):
        """Test PostgreSQL service is not available."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pg_isready")

        result = agent.check_postgresql_availability(port=5432)

        assert result.status == CheckStatus.FAIL
        assert result.port == 5432

    @patch('socket.socket')
    def test_postgresql_port_check(self, mock_socket, agent):
        """Test PostgreSQL port availability check."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0

        result = agent.check_port_available(5432, "PostgreSQL")

        assert result.status == CheckStatus.PASS
        assert result.port == 5432


class TestMariaDBValidation:
    """Test MariaDB service validation."""

    @patch('subprocess.run')
    def test_mariadb_availability_success(self, mock_run, agent):
        """Test MariaDB service is available and responding."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="MariaDB 10.11.2",
            stderr=""
        )

        result = agent.check_mariadb_availability(port=3306)

        assert result.status == CheckStatus.PASS
        assert "MariaDB" in result.message
        assert result.port == 3306

    @patch('subprocess.run')
    def test_mariadb_availability_failure(self, mock_run, agent):
        """Test MariaDB service is not available."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "mysqladmin")

        result = agent.check_mariadb_availability(port=3306)

        assert result.status == CheckStatus.FAIL
        assert result.port == 3306

    @patch('subprocess.run')
    def test_mariadb_connection_timeout(self, mock_run, agent):
        """Test MariaDB connection timeout handling."""
        mock_run.side_effect = subprocess.TimeoutExpired("mysqladmin", 5)

        result = agent.check_mariadb_availability(port=3306)

        assert result.status == CheckStatus.FAIL
        assert "timeout" in result.message.lower()


class TestPythonVersionValidation:
    """Test Python version validation."""

    @patch('subprocess.run')
    def test_python_version_valid(self, mock_run, agent):
        """Test Python 3.12.x version is valid."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Python 3.12.0",
            stderr=""
        )

        result = agent.check_python_version(required_version="3.12")

        assert result.status == CheckStatus.PASS
        assert "3.12" in result.message

    @patch('subprocess.run')
    def test_python_version_invalid(self, mock_run, agent):
        """Test Python version mismatch."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Python 3.11.5",
            stderr=""
        )

        result = agent.check_python_version(required_version="3.12")

        assert result.status == CheckStatus.FAIL
        assert "3.11" in result.message

    @patch('subprocess.run')
    def test_python_version_patch_level(self, mock_run, agent):
        """Test Python version with patch level (3.12.1, 3.12.2, etc)."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Python 3.12.2",
            stderr=""
        )

        result = agent.check_python_version(required_version="3.12")

        assert result.status == CheckStatus.PASS
        assert "3.12.2" in result.message


class TestNodeVersionValidation:
    """Test Node.js version validation."""

    @patch('subprocess.run')
    def test_node_version_valid(self, mock_run, agent):
        """Test Node 18.x version is valid."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="v18.20.0",
            stderr=""
        )

        result = agent.check_node_version(required_version="18")

        assert result.status == CheckStatus.PASS
        assert "18" in result.message

    @patch('subprocess.run')
    def test_node_version_invalid(self, mock_run, agent):
        """Test Node version mismatch."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="v20.10.0",
            stderr=""
        )

        result = agent.check_node_version(required_version="18")

        assert result.status == CheckStatus.FAIL

    @patch('subprocess.run')
    def test_node_not_installed(self, mock_run, agent):
        """Test Node.js not installed."""
        mock_run.side_effect = FileNotFoundError()

        result = agent.check_node_version(required_version="18")

        assert result.status == CheckStatus.FAIL
        assert "not found" in result.message.lower()


class TestDependencyChecks:
    """Test dependency verification."""

    @patch('subprocess.run')
    def test_yq_dependency_available(self, mock_run, agent):
        """Test yq command is available."""
        mock_run.return_value = Mock(returncode=0, stdout="yq version 4.30.8")

        result = agent.check_dependency("yq")

        assert result.status == CheckStatus.PASS
        assert result.dependency == "yq"

    @patch('subprocess.run')
    def test_jq_dependency_available(self, mock_run, agent):
        """Test jq command is available."""
        mock_run.return_value = Mock(returncode=0, stdout="jq-1.6")

        result = agent.check_dependency("jq")

        assert result.status == CheckStatus.PASS
        assert result.dependency == "jq"

    @patch('subprocess.run')
    def test_git_dependency_available(self, mock_run, agent):
        """Test git command is available."""
        mock_run.return_value = Mock(returncode=0, stdout="git version 2.39.0")

        result = agent.check_dependency("git")

        assert result.status == CheckStatus.PASS

    @patch('subprocess.run')
    def test_npm_dependency_available(self, mock_run, agent):
        """Test npm command is available."""
        mock_run.return_value = Mock(returncode=0, stdout="10.2.4")

        result = agent.check_dependency("npm")

        assert result.status == CheckStatus.PASS

    @patch('subprocess.run')
    def test_pip_dependency_available(self, mock_run, agent):
        """Test pip command is available."""
        mock_run.return_value = Mock(returncode=0, stdout="pip 23.3.1")

        result = agent.check_dependency("pip")

        assert result.status == CheckStatus.PASS

    @patch('subprocess.run')
    def test_missing_dependency(self, mock_run, agent):
        """Test missing dependency detection."""
        mock_run.side_effect = FileNotFoundError()

        result = agent.check_dependency("nonexistent")

        assert result.status == CheckStatus.FAIL
        assert result.dependency == "nonexistent"


class TestPortAvailability:
    """Test port availability checks."""

    @patch('socket.socket')
    def test_port_5432_available(self, mock_socket, agent):
        """Test PostgreSQL port 5432 is available."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0

        result = agent.check_port_available(5432, "PostgreSQL")

        assert result.status == CheckStatus.PASS
        assert result.port == 5432

    @patch('socket.socket')
    def test_port_3306_available(self, mock_socket, agent):
        """Test MariaDB port 3306 is available."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0

        result = agent.check_port_available(3306, "MariaDB")

        assert result.status == CheckStatus.PASS
        assert result.port == 3306

    @patch('socket.socket')
    def test_port_not_available(self, mock_socket, agent):
        """Test port is not available."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 1

        result = agent.check_port_available(9999, "TestService")

        assert result.status == CheckStatus.FAIL
        assert result.port == 9999

    @patch('socket.socket')
    def test_multiple_ports_check(self, mock_socket, agent):
        """Test checking multiple ports."""
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0

        ports = [5432, 3306, 8000, 3000]
        results = agent.check_multiple_ports(ports)

        assert len(results) == 4
        assert all(r.status == CheckStatus.PASS for r in results)


class TestEnvironmentVariables:
    """Test environment variables verification."""

    @patch.dict('os.environ', {'DATABASE_URL': 'postgresql://localhost/test'})
    def test_database_url_present(self, agent):
        """Test DATABASE_URL environment variable is set."""
        result = agent.check_environment_variable("DATABASE_URL")

        assert result.status == CheckStatus.PASS
        assert result.variable == "DATABASE_URL"

    @patch.dict('os.environ', {}, clear=True)
    def test_environment_variable_missing(self, agent):
        """Test missing environment variable detection."""
        result = agent.check_environment_variable("MISSING_VAR")

        assert result.status == CheckStatus.FAIL
        assert result.variable == "MISSING_VAR"

    @patch.dict('os.environ', {
        'DATABASE_URL': 'postgresql://localhost/test',
        'MARIADB_URL': 'mysql://localhost/test',
        'NODE_ENV': 'development'
    })
    def test_multiple_environment_variables(self, agent):
        """Test checking multiple environment variables."""
        required_vars = ["DATABASE_URL", "MARIADB_URL", "NODE_ENV"]
        results = agent.check_environment_variables(required_vars)

        assert len(results) == 3
        assert all(r.status == CheckStatus.PASS for r in results)

    @patch.dict('os.environ', {'DATABASE_URL': ''})
    def test_empty_environment_variable(self, agent_strict):
        """Test empty environment variable in strict mode."""
        result = agent_strict.check_environment_variable("DATABASE_URL")

        assert result.status == CheckStatus.FAIL
        assert "empty" in result.message.lower()


class TestDevContainerJSONValidation:
    """Test devcontainer.json schema validation."""

    def test_valid_devcontainer_json(self, agent, sample_devcontainer_json):
        """Test valid devcontainer.json structure."""
        result = agent.validate_devcontainer_json(sample_devcontainer_json)

        assert result.status == CheckStatus.PASS

    def test_missing_required_fields(self, agent):
        """Test devcontainer.json missing required fields."""
        invalid_config = {}  # Empty config missing "name" field

        result = agent.validate_devcontainer_json(invalid_config)

        assert result.status == CheckStatus.FAIL
        assert "empty" in result.message.lower() or "required" in result.message.lower()

    def test_invalid_json_structure(self, agent):
        """Test invalid devcontainer.json structure."""
        invalid_config = {"invalid": "structure"}

        result = agent.validate_devcontainer_json(invalid_config)

        assert result.status == CheckStatus.FAIL

    def test_python_version_extraction(self, agent, sample_devcontainer_json):
        """Test extracting Python version from devcontainer.json."""
        version = agent.extract_python_version(sample_devcontainer_json)

        assert version == "3.12.0"

    def test_node_version_extraction(self, agent, sample_devcontainer_json):
        """Test extracting Node version from devcontainer.json."""
        version = agent.extract_node_version(sample_devcontainer_json)

        assert version == "18.20.0"

    def test_port_extraction(self, agent, sample_devcontainer_json):
        """Test extracting ports from devcontainer.json."""
        ports = agent.extract_ports(sample_devcontainer_json)

        assert 5432 in ports
        assert 3306 in ports
        assert 8000 in ports
        assert 3000 in ports


class TestJSONReportGeneration:
    """Test JSON report generation."""

    def test_generate_json_report_all_pass(self, agent):
        """Test JSON report generation with all checks passing."""
        checks = [
            ValidationResult(status=CheckStatus.PASS, message="PostgreSQL OK", port=5432),
            ValidationResult(status=CheckStatus.PASS, message="MariaDB OK", port=3306),
            ValidationResult(status=CheckStatus.PASS, message="Python 3.12.0 OK", dependency="python")
        ]

        report = agent.generate_json_report(checks)

        assert report["status"] == "success"
        assert report["summary"]["total_checks"] == 3
        assert report["summary"]["passed"] == 3
        assert report["summary"]["failed"] == 0
        assert len(report["checks"]) == 3

    def test_generate_json_report_with_failures(self, agent):
        """Test JSON report generation with failures."""
        checks = [
            ValidationResult(status=CheckStatus.PASS, message="PostgreSQL OK", port=5432),
            ValidationResult(status=CheckStatus.FAIL, message="MariaDB FAIL", port=3306),
            ValidationResult(status=CheckStatus.FAIL, message="Python version mismatch", dependency="python")
        ]

        report = agent.generate_json_report(checks)

        assert report["status"] == "failure"
        assert report["summary"]["total_checks"] == 3
        assert report["summary"]["passed"] == 1
        assert report["summary"]["failed"] == 2

    def test_json_report_structure(self, agent):
        """Test JSON report has correct structure."""
        checks = [ValidationResult(status=CheckStatus.PASS, message="Test OK")]

        report = agent.generate_json_report(checks)

        assert "status" in report
        assert "summary" in report
        assert "checks" in report
        assert "timestamp" in report
        assert isinstance(report["checks"], list)


class TestCLIInterface:
    """Test CLI interface."""

    def test_cli_parser_creation(self, agent):
        """Test CLI argument parser is created correctly."""
        parser = agent.create_cli_parser()

        assert parser is not None

    @patch('sys.argv', ['agent.py', '--devcontainer-json', '/path/to/config.json', '--output', '/tmp/report.json'])
    def test_cli_arguments_parsing(self, agent):
        """Test CLI arguments are parsed correctly."""
        parser = agent.create_cli_parser()
        args = parser.parse_args(['--devcontainer-json', '/path/to/config.json', '--output', '/tmp/report.json'])

        assert args.devcontainer_json == '/path/to/config.json'
        assert args.output == '/tmp/report.json'

    def test_cli_exit_code_success(self, agent):
        """Test CLI returns exit code 0 on success."""
        checks = [ValidationResult(status=CheckStatus.PASS, message="All OK")]

        exit_code = agent.determine_exit_code(checks)

        assert exit_code == 0

    def test_cli_exit_code_failure(self, agent):
        """Test CLI returns exit code 1 on validation failure."""
        checks = [
            ValidationResult(status=CheckStatus.PASS, message="OK"),
            ValidationResult(status=CheckStatus.FAIL, message="FAIL")
        ]

        exit_code = agent.determine_exit_code(checks)

        assert exit_code == 1

    def test_cli_exit_code_config_error(self, agent):
        """Test CLI returns exit code 3 on configuration error."""
        exit_code = agent.handle_config_error("Invalid config")

        assert exit_code == 3


class TestIntegration:
    """Integration tests for complete validation workflow."""

    @patch('subprocess.run')
    @patch('socket.socket')
    @patch.dict('os.environ', {
        'DATABASE_URL': 'postgresql://localhost/test',
        'MARIADB_URL': 'mysql://localhost/test',
        'NODE_ENV': 'development',
        'DJANGO_DEBUG': 'True'
    })
    def test_full_validation_success(self, mock_socket, mock_run, agent, sample_devcontainer_json):
        """Test complete validation workflow with all checks passing."""
        # Mock subprocess calls with proper responses
        def run_side_effect(*args, **kwargs):
            cmd = args[0] if args else []
            if not cmd:
                return Mock(returncode=0, stdout="Success", stderr="")

            cmd_str = ' '.join(cmd) if isinstance(cmd, list) else str(cmd)

            if 'pg_isready' in cmd_str:
                return Mock(returncode=0, stdout="PostgreSQL is ready", stderr="")
            elif 'mysqladmin' in cmd_str or 'ping' in cmd_str:
                return Mock(returncode=0, stdout="mysqld is alive", stderr="")
            elif 'python' in cmd_str:
                return Mock(returncode=0, stdout="Python 3.12.0", stderr="")
            elif 'node' in cmd_str:
                return Mock(returncode=0, stdout="v18.20.0", stderr="")
            elif '--version' in cmd_str:
                return Mock(returncode=0, stdout="version 1.0", stderr="")
            else:
                return Mock(returncode=0, stdout="Success", stderr="")

        mock_run.side_effect = run_side_effect

        # Mock socket connections to succeed
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock
        mock_sock.connect_ex.return_value = 0

        input_data = {
            "devcontainer_json": sample_devcontainer_json,
            "check_services": True,
            "check_versions": True,
            "check_dependencies": True,
            "check_ports": True,
            "check_env": True
        }

        result = agent.run(input_data)

        assert "validation_results" in result
        assert result["status"] == "success"

    @patch('subprocess.run')
    def test_partial_validation_failure(self, mock_run, agent, sample_devcontainer_json):
        """Test validation with some checks failing."""
        # Mock PostgreSQL to succeed but MariaDB to fail
        def run_side_effect(*args, **kwargs):
            if 'pg_isready' in str(args):
                return Mock(returncode=0, stdout="OK", stderr="")
            elif 'mysqladmin' in str(args):
                raise subprocess.CalledProcessError(1, "mysqladmin")
            else:
                return Mock(returncode=0, stdout="OK", stderr="")

        mock_run.side_effect = run_side_effect

        input_data = {
            "devcontainer_json": sample_devcontainer_json,
            "check_services": True
        }

        result = agent.run(input_data)

        assert "validation_results" in result
        # Should have some failures
        assert any(r.status == CheckStatus.FAIL for r in result["validation_results"])


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_invalid_port_number(self, agent):
        """Test handling of invalid port numbers."""
        with pytest.raises(ValueError):
            agent.check_port_available(70000, "Invalid")

    def test_negative_port_number(self, agent):
        """Test handling of negative port numbers."""
        with pytest.raises(ValueError):
            agent.check_port_available(-1, "Invalid")

    def test_none_devcontainer_json(self, agent):
        """Test handling of None devcontainer.json."""
        result = agent.validate_devcontainer_json(None)

        assert result.status == CheckStatus.FAIL
        assert "None" in result.message or "null" in result.message.lower()

    def test_empty_devcontainer_json(self, agent):
        """Test handling of empty devcontainer.json."""
        result = agent.validate_devcontainer_json({})

        assert result.status == CheckStatus.FAIL

    @patch('subprocess.run')
    def test_command_timeout_handling(self, mock_run, agent):
        """Test handling of command timeouts."""
        mock_run.side_effect = subprocess.TimeoutExpired("test", 5)

        result = agent.check_dependency("slow_command")

        assert result.status == CheckStatus.FAIL
        assert "timeout" in result.message.lower()


class TestValidationResult:
    """Test ValidationResult data structure."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult instance."""
        result = ValidationResult(
            status=CheckStatus.PASS,
            message="Test passed",
            port=5432,
            dependency="test"
        )

        assert result.status == CheckStatus.PASS
        assert result.message == "Test passed"
        assert result.port == 5432
        assert result.dependency == "test"

    def test_validation_result_to_dict(self):
        """Test converting ValidationResult to dict."""
        result = ValidationResult(
            status=CheckStatus.FAIL,
            message="Test failed",
            variable="TEST_VAR"
        )

        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert result_dict["status"] == "fail"
        assert result_dict["message"] == "Test failed"
        assert result_dict["variable"] == "TEST_VAR"
