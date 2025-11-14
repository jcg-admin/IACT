#!/usr/bin/env python3
"""
DevContainerValidatorAgent - Validates DevContainer environment.

Performs comprehensive validation of DevContainer environment including:
- Service health checks (PostgreSQL, MariaDB)
- Version validation (Python 3.12.x, Node 18.x)
- Dependency verification (yq, jq, git, npm, pip)
- Port availability (5432, 3306, 8000, 3000)
- Environment variables verification
- devcontainer.json schema validation

Location: scripts/coding/ai/automation/devcontainer_validator_agent.py
Responsibility: Complete DevContainer environment validation
Invoked by: validate_devcontainer_env.sh

Exit codes:
- 0: All validations passed
- 1: Validation failures detected
- 3: Configuration error

Author: SDLC Agent / DevOps Team
Date: 2025-11-13
"""

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.coding.ai.shared.agent_base import Agent, AgentStatus


class CheckStatus(Enum):
    """Status of individual validation check."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    status: CheckStatus
    message: str
    port: Optional[int] = None
    dependency: Optional[str] = None
    variable: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "status": self.status.value,
            "message": self.message,
            "details": self.details
        }
        if self.port is not None:
            result["port"] = self.port
        if self.dependency is not None:
            result["dependency"] = self.dependency
        if self.variable is not None:
            result["variable"] = self.variable
        return result


class DevContainerValidatorAgent(Agent):
    """
    Agent for validating DevContainer environment.

    Performs comprehensive checks to ensure development environment
    is properly configured and all required services are available.
    """

    def __init__(self, name: str = "devcontainer_validator", config: Optional[Dict[str, Any]] = None):
        """
        Initialize DevContainerValidatorAgent.

        Args:
            name: Agent name
            config: Configuration dictionary with optional keys:
                - project_root: Project root directory
                - strict_mode: Enable strict validation
                - timeout: Command timeout in seconds
        """
        super().__init__(name, config)
        self.project_root = Path(self.config.get("project_root", "."))
        self.strict_mode = self.config.get("strict_mode", False)
        self.timeout = self.config.get("timeout", 5)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute DevContainer validation.

        Args:
            input_data: Dictionary with:
                - devcontainer_json: DevContainer configuration
                - check_services: Enable service checks (default: True)
                - check_versions: Enable version checks (default: True)
                - check_dependencies: Enable dependency checks (default: True)
                - check_ports: Enable port checks (default: True)
                - check_env: Enable environment variable checks (default: True)

        Returns:
            Dictionary with validation results
        """
        devcontainer_json = input_data.get("devcontainer_json")
        check_services = input_data.get("check_services", True)
        check_versions = input_data.get("check_versions", True)
        check_dependencies = input_data.get("check_dependencies", True)
        check_ports = input_data.get("check_ports", True)
        check_env = input_data.get("check_env", True)

        validation_results = []

        # Validate devcontainer.json structure
        if devcontainer_json is not None:
            validation_results.append(self.validate_devcontainer_json(devcontainer_json))

        # Service health checks
        if check_services:
            validation_results.append(self.check_postgresql_availability())
            validation_results.append(self.check_mariadb_availability())

        # Version checks
        if check_versions:
            if devcontainer_json:
                python_version = self.extract_python_version(devcontainer_json)
                if python_version:
                    required_version = ".".join(python_version.split(".")[:2])  # e.g., "3.12"
                    validation_results.append(self.check_python_version(required_version))

                node_version = self.extract_node_version(devcontainer_json)
                if node_version:
                    required_version = node_version.split(".")[0]  # e.g., "18"
                    validation_results.append(self.check_node_version(required_version))

        # Dependency checks
        if check_dependencies:
            for dep in ["yq", "jq", "git", "npm", "pip"]:
                validation_results.append(self.check_dependency(dep))

        # Port availability checks
        if check_ports and devcontainer_json:
            ports = self.extract_ports(devcontainer_json)
            port_results = self.check_multiple_ports(ports)
            validation_results.extend(port_results)

        # Environment variable checks
        if check_env and devcontainer_json:
            env_vars = self.extract_environment_variables(devcontainer_json)
            env_results = self.check_environment_variables(env_vars)
            validation_results.extend(env_results)

        # Generate summary
        passed = sum(1 for r in validation_results if r.status == CheckStatus.PASS)
        failed = sum(1 for r in validation_results if r.status == CheckStatus.FAIL)

        status = "success" if failed == 0 else "failure"

        return {
            "status": status,
            "validation_results": validation_results,
            "summary": {
                "total_checks": len(validation_results),
                "passed": passed,
                "failed": failed
            }
        }

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Validate input data.

        Args:
            input_data: Input data to validate

        Returns:
            List of validation errors
        """
        errors = []

        if not isinstance(input_data, dict):
            errors.append("Input data must be a dictionary")

        return errors

    # Service Health Checks

    def check_postgresql_availability(self, port: int = 5432) -> ValidationResult:
        """
        Check PostgreSQL service availability.

        Args:
            port: PostgreSQL port (default: 5432)

        Returns:
            ValidationResult
        """
        try:
            result = subprocess.run(
                ["pg_isready", "-p", str(port)],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                return ValidationResult(
                    status=CheckStatus.PASS,
                    message=f"PostgreSQL is available on port {port}",
                    port=port
                )
            else:
                return ValidationResult(
                    status=CheckStatus.FAIL,
                    message=f"PostgreSQL is not responding on port {port}",
                    port=port
                )

        except FileNotFoundError:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message="pg_isready command not found (PostgreSQL client not installed)",
                port=port
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"PostgreSQL check timeout on port {port}",
                port=port
            )
        except subprocess.CalledProcessError as e:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"PostgreSQL check failed: {e}",
                port=port
            )

    def check_mariadb_availability(self, port: int = 3306) -> ValidationResult:
        """
        Check MariaDB service availability.

        Args:
            port: MariaDB port (default: 3306)

        Returns:
            ValidationResult
        """
        try:
            result = subprocess.run(
                ["mysqladmin", "-P", str(port), "ping"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0 or "mysqld is alive" in result.stdout:
                return ValidationResult(
                    status=CheckStatus.PASS,
                    message=f"MariaDB is available on port {port}",
                    port=port
                )
            else:
                return ValidationResult(
                    status=CheckStatus.FAIL,
                    message=f"MariaDB is not responding on port {port}",
                    port=port
                )

        except FileNotFoundError:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message="mysqladmin command not found (MariaDB client not installed)",
                port=port
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"MariaDB check timeout on port {port}",
                port=port
            )
        except subprocess.CalledProcessError as e:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"MariaDB check failed: {e}",
                port=port
            )

    # Version Validation

    def check_python_version(self, required_version: str = "3.12") -> ValidationResult:
        """
        Check Python version.

        Args:
            required_version: Required Python version (e.g., "3.12")

        Returns:
            ValidationResult
        """
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            version_output = result.stdout.strip()
            # Extract version number (e.g., "Python 3.12.0" -> "3.12.0")
            version = version_output.split()[-1]

            # Check if major.minor matches
            version_parts = version.split(".")
            required_parts = required_version.split(".")

            if version_parts[:len(required_parts)] == required_parts:
                return ValidationResult(
                    status=CheckStatus.PASS,
                    message=f"Python version {version} matches required {required_version}",
                    dependency="python",
                    details={"version": version}
                )
            else:
                return ValidationResult(
                    status=CheckStatus.FAIL,
                    message=f"Python version {version} does not match required {required_version}",
                    dependency="python",
                    details={"version": version, "required": required_version}
                )

        except Exception as e:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"Failed to check Python version: {e}",
                dependency="python"
            )

    def check_node_version(self, required_version: str = "18") -> ValidationResult:
        """
        Check Node.js version.

        Args:
            required_version: Required Node major version (e.g., "18")

        Returns:
            ValidationResult
        """
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            version_output = result.stdout.strip()
            # Extract version (e.g., "v18.20.0" -> "18")
            version = version_output.lstrip("v")
            major_version = version.split(".")[0]

            if major_version == required_version:
                return ValidationResult(
                    status=CheckStatus.PASS,
                    message=f"Node.js version {version} matches required {required_version}.x",
                    dependency="node",
                    details={"version": version}
                )
            else:
                return ValidationResult(
                    status=CheckStatus.FAIL,
                    message=f"Node.js version {version} does not match required {required_version}.x",
                    dependency="node",
                    details={"version": version, "required": required_version}
                )

        except FileNotFoundError:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message="Node.js not found",
                dependency="node"
            )
        except Exception as e:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"Failed to check Node.js version: {e}",
                dependency="node"
            )

    # Dependency Checks

    def check_dependency(self, command: str) -> ValidationResult:
        """
        Check if a command/dependency is available.

        Args:
            command: Command name to check

        Returns:
            ValidationResult
        """
        try:
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                version_info = result.stdout.strip().split("\n")[0]
                return ValidationResult(
                    status=CheckStatus.PASS,
                    message=f"{command} is available: {version_info}",
                    dependency=command,
                    details={"version_info": version_info}
                )
            else:
                return ValidationResult(
                    status=CheckStatus.FAIL,
                    message=f"{command} check failed",
                    dependency=command
                )

        except FileNotFoundError:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"{command} not found",
                dependency=command
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"{command} check timeout",
                dependency=command
            )
        except Exception as e:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"Failed to check {command}: {e}",
                dependency=command
            )

    # Port Availability

    def check_port_available(self, port: int, service_name: str = "Service") -> ValidationResult:
        """
        Check if a port is available (service is listening).

        Args:
            port: Port number to check
            service_name: Name of service for reporting

        Returns:
            ValidationResult

        Raises:
            ValueError: If port number is invalid
        """
        if port < 0 or port > 65535:
            raise ValueError(f"Invalid port number: {port}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex(("localhost", port))

                if result == 0:
                    return ValidationResult(
                        status=CheckStatus.PASS,
                        message=f"{service_name} port {port} is available",
                        port=port
                    )
                else:
                    return ValidationResult(
                        status=CheckStatus.FAIL,
                        message=f"{service_name} port {port} is not available",
                        port=port
                    )

        except Exception as e:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"Failed to check port {port}: {e}",
                port=port
            )

    def check_multiple_ports(self, ports: List[int]) -> List[ValidationResult]:
        """
        Check multiple ports.

        Args:
            ports: List of port numbers

        Returns:
            List of ValidationResult
        """
        results = []
        for port in ports:
            service_name = self._get_service_name_for_port(port)
            results.append(self.check_port_available(port, service_name))
        return results

    def _get_service_name_for_port(self, port: int) -> str:
        """Get service name for common ports."""
        port_mapping = {
            5432: "PostgreSQL",
            3306: "MariaDB",
            8000: "Django",
            3000: "React",
            6379: "Redis"
        }
        return port_mapping.get(port, f"Service@{port}")

    # Environment Variables

    def check_environment_variable(self, var_name: str) -> ValidationResult:
        """
        Check if environment variable is set.

        Args:
            var_name: Variable name

        Returns:
            ValidationResult
        """
        value = os.environ.get(var_name)

        if value is None:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"Environment variable {var_name} is not set",
                variable=var_name
            )

        if self.strict_mode and not value:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"Environment variable {var_name} is empty",
                variable=var_name
            )

        return ValidationResult(
            status=CheckStatus.PASS,
            message=f"Environment variable {var_name} is set",
            variable=var_name,
            details={"value_length": len(value)}
        )

    def check_environment_variables(self, var_names: List[str]) -> List[ValidationResult]:
        """
        Check multiple environment variables.

        Args:
            var_names: List of variable names

        Returns:
            List of ValidationResult
        """
        return [self.check_environment_variable(var) for var in var_names]

    # DevContainer JSON Validation

    def validate_devcontainer_json(self, config: Optional[Dict[str, Any]]) -> ValidationResult:
        """
        Validate devcontainer.json structure.

        Args:
            config: DevContainer configuration

        Returns:
            ValidationResult
        """
        if config is None:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message="devcontainer.json is None"
            )

        if not isinstance(config, dict):
            return ValidationResult(
                status=CheckStatus.FAIL,
                message="devcontainer.json must be a dictionary"
            )

        if not config:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message="devcontainer.json is empty"
            )

        # Check for required fields
        required_fields = ["name"]
        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            return ValidationResult(
                status=CheckStatus.FAIL,
                message=f"devcontainer.json missing required fields: {', '.join(missing_fields)}"
            )

        return ValidationResult(
            status=CheckStatus.PASS,
            message="devcontainer.json structure is valid"
        )

    def extract_python_version(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Extract Python version from devcontainer.json.

        Args:
            config: DevContainer configuration

        Returns:
            Python version string or None
        """
        try:
            build = config.get("build", {})
            args = build.get("args", {})
            return args.get("PYTHON_VERSION")
        except Exception:
            return None

    def extract_node_version(self, config: Dict[str, Any]) -> Optional[str]:
        """
        Extract Node version from devcontainer.json.

        Args:
            config: DevContainer configuration

        Returns:
            Node version string or None
        """
        try:
            build = config.get("build", {})
            args = build.get("args", {})
            return args.get("NODE_VERSION")
        except Exception:
            return None

    def extract_ports(self, config: Dict[str, Any]) -> List[int]:
        """
        Extract forwarded ports from devcontainer.json.

        Args:
            config: DevContainer configuration

        Returns:
            List of port numbers
        """
        try:
            return config.get("forwardPorts", [])
        except Exception:
            return []

    def extract_environment_variables(self, config: Dict[str, Any]) -> List[str]:
        """
        Extract environment variable names from devcontainer.json.

        Args:
            config: DevContainer configuration

        Returns:
            List of environment variable names
        """
        try:
            container_env = config.get("containerEnv", {})
            return list(container_env.keys())
        except Exception:
            return []

    # Report Generation

    def generate_json_report(self, checks: List[ValidationResult]) -> Dict[str, Any]:
        """
        Generate JSON report from validation results.

        Args:
            checks: List of validation results

        Returns:
            JSON report dictionary
        """
        passed = sum(1 for c in checks if c.status == CheckStatus.PASS)
        failed = sum(1 for c in checks if c.status == CheckStatus.FAIL)

        status = "success" if failed == 0 else "failure"

        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_checks": len(checks),
                "passed": passed,
                "failed": failed
            },
            "checks": [check.to_dict() for check in checks]
        }

    # CLI Interface

    def create_cli_parser(self) -> argparse.ArgumentParser:
        """
        Create CLI argument parser.

        Returns:
            ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="DevContainer Environment Validator"
        )
        parser.add_argument(
            "--devcontainer-json",
            type=str,
            help="Path to devcontainer.json file"
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Path to output JSON report"
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict validation mode"
        )
        return parser

    def determine_exit_code(self, checks: List[ValidationResult]) -> int:
        """
        Determine exit code based on validation results.

        Args:
            checks: List of validation results

        Returns:
            Exit code (0=success, 1=failure)
        """
        failed = sum(1 for c in checks if c.status == CheckStatus.FAIL)
        return 0 if failed == 0 else 1

    def handle_config_error(self, error_message: str) -> int:
        """
        Handle configuration error.

        Args:
            error_message: Error message

        Returns:
            Exit code 3 for configuration error
        """
        self.logger.error(f"Configuration error: {error_message}")
        return 3


def main():
    """CLI entry point."""
    agent = DevContainerValidatorAgent()
    parser = agent.create_cli_parser()
    args = parser.parse_args()

    try:
        # Load devcontainer.json if provided
        devcontainer_json = None
        if args.devcontainer_json:
            devcontainer_path = Path(args.devcontainer_json)
            if not devcontainer_path.exists():
                print(f"Error: devcontainer.json not found at {args.devcontainer_json}", file=sys.stderr)
                sys.exit(3)

            with open(devcontainer_path) as f:
                devcontainer_json = json.load(f)

        # Update agent config if strict mode
        if args.strict:
            agent.config["strict_mode"] = True
            agent.strict_mode = True

        # Run validation
        input_data = {
            "devcontainer_json": devcontainer_json,
            "check_services": True,
            "check_versions": True,
            "check_dependencies": True,
            "check_ports": True,
            "check_env": True
        }

        result = agent.execute(input_data)

        if result.is_failed():
            print(f"Agent execution failed: {result.errors}", file=sys.stderr)
            sys.exit(3)

        # Generate report
        validation_results = result.data.get("validation_results", [])
        report = agent.generate_json_report(validation_results)

        # Output report
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            print(json.dumps(report, indent=2))

        # Determine exit code
        exit_code = agent.determine_exit_code(validation_results)
        sys.exit(exit_code)

    except json.JSONDecodeError as e:
        print(f"Error parsing devcontainer.json: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
