#!/usr/bin/env python3
"""
TDD Metrics Dashboard - Visualizacion de metricas y compliance.

Este modulo genera dashboards visuales con badges para:
- TDD Compliance score
- Test Coverage
- Security Issues
- Code Quality
- Documentation

Genera archivos Markdown con badges de shields.io.

Referencia: TDD Feature Agent - Dashboard visual de metricas
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class TDDMetricsDashboard:
    """
    Generador de dashboards visuales para metricas TDD.

    Crea badges y reportes visuales usando shields.io badges.
    """

    @staticmethod
    def generate_badge(
        label: str,
        value: str,
        color: str,
    ) -> str:
        """
        Genera markdown para un badge de shields.io.

        Args:
            label: Etiqueta del badge
            value: Valor a mostrar
            color: Color (green, yellow, red, blue, etc.)

        Returns:
            Markdown del badge
        """
        # Escapar espacios en label y value
        label_escaped = label.replace(" ", "_")
        value_escaped = value.replace(" ", "_")

        # Generar URL de shields.io
        badge_url = f"https://img.shields.io/badge/{label_escaped}-{value_escaped}-{color}"

        return f"![{label}]({badge_url})"

    @classmethod
    def generate_dashboard(
        cls,
        execution_log: Path,
        output_path: Path,
    ) -> None:
        """
        Genera dashboard visual desde execution log.

        Args:
            execution_log: Path al JSON de execution log
            output_path: Path donde guardar el dashboard.md
        """
        logger.info(f"Generating dashboard from {execution_log}")

        # Leer execution log
        with open(execution_log, encoding="utf-8") as f:
            log_data = json.load(f)

        # Generar dashboard
        lines = []

        # Header
        feature_name = log_data.get("feature_name", "Unknown")
        lines.append(f"# TDD Metrics Dashboard: {feature_name}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Badges principales
        lines.append("## Quick Status")
        lines.append("")

        constitution = log_data.get("constitution_result", {})
        score = constitution.get("score", 0.0)
        compliant = constitution.get("compliant", False)

        # Badge de compliance
        compliance_color = cls._get_score_color(score)
        compliance_badge = cls.generate_badge(
            "TDD_Compliance",
            f"{score:.1f}%",
            compliance_color,
        )
        lines.append(compliance_badge)

        # Badge de cobertura
        metrics = log_data.get("metrics", {})
        coverage = metrics.get("coverage", {})
        coverage_percent = coverage.get("percent", 0.0)
        coverage_color = cls._get_coverage_color(coverage_percent)
        coverage_badge = cls.generate_badge(
            "Test_Coverage",
            f"{coverage_percent:.1f}%",
            coverage_color,
        )
        lines.append(" " + coverage_badge)

        # Badge de seguridad
        security = metrics.get("security", {})
        security_issues = security.get("issues_count", 0)
        security_color = "green" if security_issues == 0 else "red"
        security_badge = cls.generate_badge(
            "Security_Issues",
            str(security_issues),
            security_color,
        )
        lines.append(" " + security_badge)

        # Badge de calidad
        quality = metrics.get("quality", {})
        quality_passed = quality.get("passed", False)
        quality_color = "green" if quality_passed else "red"
        quality_status = "Pass" if quality_passed else "Fail"
        quality_badge = cls.generate_badge(
            "Code_Quality",
            quality_status,
            quality_color,
        )
        lines.append(" " + quality_badge)

        lines.append("")
        lines.append("")

        # Status general
        lines.append("## Overall Status")
        lines.append("")

        if compliant:
            lines.append("### ✅ TDD COMPLIANT")
            lines.append("")
            lines.append(f"All CRITICAL rules passed. Compliance score: **{score}/100**")
        else:
            lines.append("### ❌ TDD NOT COMPLIANT")
            lines.append("")
            lines.append(f"Constitution violations found. Compliance score: **{score}/100**")

            # Mostrar violaciones criticas
            violations = constitution.get("violations", [])
            critical_violations = [
                v for v in violations
                if v.get("severity") == "CRITICAL"
            ]
            if critical_violations:
                lines.append("")
                lines.append("**CRITICAL Violations:**")
                for violation in critical_violations:
                    lines.append(f"- 🔴 {violation.get('rule_code')}: {violation.get('message')}")

        lines.append("")
        lines.append("")

        # Metricas detalladas
        lines.append("## Detailed Metrics")
        lines.append("")

        # Tabla de metricas
        lines.append("| Metric | Value | Status |")
        lines.append("|--------|-------|--------|")

        # Coverage
        coverage_status = "✅ Pass" if coverage.get("passed", False) else "❌ Fail"
        lines.append(
            f"| Test Coverage | {coverage_percent:.1f}% "
            f"({coverage.get('covered_lines', 0)}/{coverage.get('total_lines', 0)} lines) "
            f"| {coverage_status} |"
        )

        # Security
        security_status = "✅ Pass" if security_issues == 0 else "❌ Fail"
        lines.append(f"| Security Issues | {security_issues} | {security_status} |")

        # Code Quality
        quality_status_text = "✅ Pass" if quality_passed else "❌ Fail"
        quality_issues = quality.get("issues_count", 0)
        lines.append(f"| Code Quality | {quality_issues} issues | {quality_status_text} |")

        # Type Check
        type_check = metrics.get("type_check", {})
        type_check_passed = type_check.get("passed", False)
        type_check_status = "✅ Pass" if type_check_passed else "❌ Fail"
        type_check_issues = type_check.get("issues_count", 0)
        lines.append(f"| Type Checking | {type_check_issues} issues | {type_check_status} |")

        # Documentation
        documentation = metrics.get("documentation", {})
        doc_passed = documentation.get("passed", False)
        doc_status = "✅ Pass" if doc_passed else "❌ Fail"
        missing_docs = documentation.get("missing_count", 0)
        total_funcs = documentation.get("total_public_functions", 0)
        lines.append(
            f"| Documentation | {total_funcs - missing_docs}/{total_funcs} functions "
            f"| {doc_status} |"
        )

        lines.append("")
        lines.append("")

        # Constitution Rules
        lines.append("## Constitution Rules")
        lines.append("")

        evidence = constitution.get("evidence", {})

        lines.append("| Rule | Status | Details |")
        lines.append("|------|--------|---------|")

        rule_names = [
            "RED_BEFORE_GREEN",
            "TESTS_MUST_FAIL_FIRST",
            "ALL_TESTS_MUST_PASS",
            "TESTS_STAY_GREEN_AFTER_REFACTOR",
            "MINIMUM_COVERAGE",
            "NO_SECURITY_ISSUES",
            "CODE_QUALITY_PASSING",
            "DOCUMENTATION_REQUIRED",
        ]

        for rule_code in rule_names:
            rule_evidence = evidence.get(rule_code, {})
            passed = rule_evidence.get("passed", False)
            status = "✅ Pass" if passed else "❌ Fail"
            message = rule_evidence.get("message", "No data")

            # Truncar mensaje si es muy largo
            if len(message) > 60:
                message = message[:57] + "..."

            lines.append(f"| {rule_code} | {status} | {message} |")

        lines.append("")
        lines.append("")

        # Test Executions
        lines.append("## Test Execution Summary")
        lines.append("")

        test_executions = log_data.get("test_executions", [])
        if test_executions:
            lines.append("| Phase | Total | Passed | Failed | Duration |")
            lines.append("|-------|-------|--------|--------|----------|")

            for test_exec in test_executions:
                phase = test_exec.get("phase", "unknown")
                result = test_exec.get("result", {})

                total = result.get("total", 0)
                passed_count = result.get("passed", 0)
                failed = result.get("failed", 0)
                duration = result.get("duration_seconds", 0)

                lines.append(
                    f"| {phase.replace('_', ' ').title()} | {total} | "
                    f"{passed_count} | {failed} | {duration:.2f}s |"
                )

            lines.append("")
        else:
            lines.append("No test executions recorded.")
            lines.append("")

        lines.append("")

        # Timeline
        lines.append("## Execution Timeline")
        lines.append("")

        phases = log_data.get("phases", {})
        if phases:
            lines.append("| Phase | Duration | Status |")
            lines.append("|-------|----------|--------|")

            for phase_name, phase_data in phases.items():
                duration = phase_data.get("duration_seconds", 0)
                status = phase_data.get("status", "unknown")

                status_emoji = (
                    "✅" if status == "completed"
                    else "❌" if status == "failed"
                    else "🔄"
                )

                lines.append(
                    f"| {phase_name.replace('_', ' ').title()} | "
                    f"{duration:.2f}s | {status_emoji} {status} |"
                )

            lines.append("")
            lines.append(f"**Total Duration:** {log_data.get('duration_seconds', 0):.2f}s")
        else:
            lines.append("No phase data recorded.")

        lines.append("")
        lines.append("")

        # Artifacts
        lines.append("## Generated Artifacts")
        lines.append("")

        artifacts = log_data.get("artifacts", [])
        if artifacts:
            lines.append("| File | Type | Size |")
            lines.append("|------|------|------|")

            for artifact in artifacts:
                file_path = Path(artifact["file_path"]).name
                artifact_type = artifact["artifact_type"]
                size = artifact["size_bytes"]

                # Convertir size a KB si es grande
                if size > 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size} bytes"

                lines.append(f"| `{file_path}` | {artifact_type} | {size_str} |")

            lines.append("")
        else:
            lines.append("No artifacts recorded.")
            lines.append("")

        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("**Dashboard generated by TDDFeatureAgent**")
        lines.append("")
        lines.append(f"Execution Log: `{execution_log.name}`")

        # Escribir dashboard
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Dashboard saved to {output_path}")

    @staticmethod
    def _get_score_color(score: float) -> str:
        """
        Determina color del badge basado en score.

        Args:
            score: Score de 0-100

        Returns:
            Color para el badge (green, yellow, orange, red)
        """
        if score >= 90:
            return "green"
        elif score >= 75:
            return "yellow"
        elif score >= 50:
            return "orange"
        else:
            return "red"

    @staticmethod
    def _get_coverage_color(coverage_percent: float) -> str:
        """
        Determina color del badge basado en cobertura.

        Args:
            coverage_percent: Porcentaje de cobertura

        Returns:
            Color para el badge
        """
        if coverage_percent >= 90:
            return "green"
        elif coverage_percent >= 80:
            return "yellow"
        elif coverage_percent >= 70:
            return "orange"
        else:
            return "red"
