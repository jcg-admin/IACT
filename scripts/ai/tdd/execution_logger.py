#!/usr/bin/env python3
"""
TDD Execution Logger - Audit trail completo de ejecucion TDD.

Este modulo registra cada fase del proceso TDD, incluyendo:
- Timestamps de cada fase
- Archivos generados (con hashes SHA256)
- Resultados de tests
- Metricas de calidad
- Resultado de constitution checks

Al finalizar, genera reportes en JSON y Markdown.

Referencia: TDD Feature Agent - Sistema de auditoria completo
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TDDExecutionLogger:
    """
    Logger de ejecucion TDD con audit trail completo.

    Registra cada fase, artifact, test execution y metrica.
    Genera reportes JSON y Markdown al finalizar.
    """

    def __init__(
        self,
        feature_name: str,
        output_dir: Path,
    ):
        """
        Inicializa el logger.

        Args:
            feature_name: Nombre del feature siendo implementado
            output_dir: Directorio donde guardar logs y reportes
        """
        self.feature_name = feature_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Estructura del log
        self.log: Dict[str, object] = {
            "feature_name": feature_name,
            "start_timestamp": datetime.now().isoformat(),
            "end_timestamp": None,
            "duration_seconds": None,
            "phases": {},
            "artifacts": [],
            "test_executions": [],
            "metrics": {},
            "constitution_result": {},
        }

    def log_phase(
        self,
        phase_name: str,
        data: Dict,
    ) -> None:
        """
        Registra inicio/fin de una fase TDD.

        Args:
            phase_name: Nombre de la fase (red_phase, green_phase, refactor_phase)
            data: Datos de la fase:
                - timestamp: str (ISO format)
                - status: str (started, completed, failed)
                - details: Dict (detalles especificos de la fase)
        """
        logger.info(f"Logging phase: {phase_name} - {data.get('status')}")

        if phase_name not in self.log["phases"]:
            self.log["phases"][phase_name] = {
                "start_timestamp": None,
                "end_timestamp": None,
                "duration_seconds": None,
                "status": None,
                "details": {},
            }

        phase = self.log["phases"][phase_name]

        if data.get("status") == "started":
            phase["start_timestamp"] = data.get("timestamp", datetime.now().isoformat())
            phase["status"] = "in_progress"
        elif data.get("status") in ["completed", "failed"]:
            phase["end_timestamp"] = data.get("timestamp", datetime.now().isoformat())
            phase["status"] = data.get("status")

            # Calcular duracion
            if phase["start_timestamp"]:
                start = datetime.fromisoformat(phase["start_timestamp"])
                end = datetime.fromisoformat(phase["end_timestamp"])
                duration = (end - start).total_seconds()
                phase["duration_seconds"] = round(duration, 2)

        # Actualizar detalles
        if "details" in data:
            phase["details"].update(data["details"])

    def log_artifact(
        self,
        file_path: Path,
        artifact_type: str,
    ) -> None:
        """
        Registra un archivo generado con su hash SHA256.

        Args:
            file_path: Path al archivo generado
            artifact_type: Tipo (unit_test, integration_test, service, model, etc.)
        """
        logger.info(f"Logging artifact: {file_path} ({artifact_type})")

        # Calcular hash SHA256
        file_hash = self._calculate_file_hash(file_path)

        artifact = {
            "file_path": str(file_path),
            "artifact_type": artifact_type,
            "sha256_hash": file_hash,
            "timestamp": datetime.now().isoformat(),
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0,
        }

        self.log["artifacts"].append(artifact)

    def log_test_execution(
        self,
        phase: str,
        test_result: Dict,
    ) -> None:
        """
        Registra resultado de ejecucion de tests.

        Args:
            phase: Fase en la que se ejecutaron (red_phase, green_phase, refactor_phase)
            test_result: Resultado de pytest:
                - total: int (total de tests)
                - passed: int
                - failed: int
                - skipped: int
                - duration_seconds: float
                - details: str (output completo)
        """
        logger.info(
            f"Logging test execution for {phase}: "
            f"{test_result.get('passed')}/{test_result.get('total')} passed"
        )

        test_execution = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "result": test_result,
        }

        self.log["test_executions"].append(test_execution)

    def log_metrics(
        self,
        metrics: Dict,
    ) -> None:
        """
        Registra metricas de calidad.

        Args:
            metrics: Diccionario con metricas:
                - coverage: Dict (percent, total_lines, covered_lines)
                - quality: Dict (linting_passed, issues_count)
                - security: Dict (issues_count, issues)
                - type_check: Dict (type_check_passed, issues_count)
                - documentation: Dict (missing_docstrings, total_public_functions)
        """
        logger.info("Logging quality metrics")
        self.log["metrics"].update(metrics)

    def finalize(
        self,
        constitution_result: Dict,
    ) -> Path:
        """
        Finaliza el log y genera reportes.

        Args:
            constitution_result: Resultado de TDDConstitution.validate_tdd_compliance()

        Returns:
            Path al archivo JSON del log
        """
        logger.info("Finalizing execution log")

        # Registrar fin de ejecucion
        self.log["end_timestamp"] = datetime.now().isoformat()

        # Calcular duracion total
        start = datetime.fromisoformat(self.log["start_timestamp"])
        end = datetime.fromisoformat(self.log["end_timestamp"])
        self.log["duration_seconds"] = round((end - start).total_seconds(), 2)

        # Guardar resultado de constitution
        self.log["constitution_result"] = constitution_result

        # Generar reporte JSON
        json_path = self._generate_json_report()

        # Generar reporte Markdown
        markdown_path = self._generate_markdown_report()

        logger.info(f"Execution log saved to: {json_path}")
        logger.info(f"Markdown report saved to: {markdown_path}")

        return json_path

    def _generate_json_report(self) -> Path:
        """
        Genera reporte JSON completo.

        Returns:
            Path al archivo JSON
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tdd_execution_{self.feature_name}_{timestamp}.json"
        json_path = self.output_dir / filename

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)

        return json_path

    def _generate_markdown_report(self) -> Path:
        """
        Genera reporte Markdown human-readable.

        Returns:
            Path al archivo Markdown
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tdd_execution_{self.feature_name}_{timestamp}.md"
        md_path = self.output_dir / filename

        lines = []

        # Header
        lines.append(f"# TDD Execution Report: {self.feature_name}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Duration:** {self.log['duration_seconds']}s")
        lines.append("")

        # Constitution Result
        constitution = self.log.get("constitution_result", {})
        compliant = constitution.get("compliant", False)
        score = constitution.get("score", 0.0)

        lines.append("## Constitution Compliance")
        lines.append("")
        if compliant:
            lines.append(f"✅ **COMPLIANT** - Score: {score}/100")
        else:
            lines.append(f"❌ **NOT COMPLIANT** - Score: {score}/100")
        lines.append("")

        # Violations
        violations = constitution.get("violations", [])
        if violations:
            lines.append("### Violations")
            lines.append("")
            for violation in violations:
                severity = violation.get("severity")
                emoji = "🔴" if severity == "CRITICAL" else "🟡" if severity == "HIGH" else "🔵"
                lines.append(f"{emoji} **{severity}** - {violation.get('rule_code')}")
                lines.append(f"   - {violation.get('message')}")
            lines.append("")

        # Summary
        summary = constitution.get("summary", {})
        lines.append("### Summary")
        lines.append("")
        lines.append(f"- Total Rules: {summary.get('total_rules', 0)}")
        lines.append(f"- Passed Rules: {summary.get('passed_rules', 0)}")
        lines.append(f"- Critical Violations: {summary.get('critical_violations', 0)}")
        lines.append(f"- High Violations: {summary.get('high_violations', 0)}")
        lines.append(f"- Medium Violations: {summary.get('medium_violations', 0)}")
        lines.append("")

        # Phases
        lines.append("## TDD Phases")
        lines.append("")

        phases = self.log.get("phases", {})
        for phase_name, phase_data in phases.items():
            status_emoji = "✅" if phase_data["status"] == "completed" else "❌" if phase_data["status"] == "failed" else "🔄"
            lines.append(f"### {status_emoji} {phase_name.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"- **Status:** {phase_data['status']}")
            if phase_data.get("duration_seconds"):
                lines.append(f"- **Duration:** {phase_data['duration_seconds']}s")
            lines.append(f"- **Start:** {phase_data.get('start_timestamp', 'N/A')}")
            lines.append(f"- **End:** {phase_data.get('end_timestamp', 'N/A')}")
            lines.append("")

        # Test Executions
        lines.append("## Test Executions")
        lines.append("")

        test_executions = self.log.get("test_executions", [])
        for test_exec in test_executions:
            phase = test_exec.get("phase", "unknown")
            result = test_exec.get("result", {})

            total = result.get("total", 0)
            passed = result.get("passed", 0)
            failed = result.get("failed", 0)

            status_emoji = "✅" if failed == 0 else "❌"
            lines.append(f"### {status_emoji} {phase.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"- **Total Tests:** {total}")
            lines.append(f"- **Passed:** {passed}")
            lines.append(f"- **Failed:** {failed}")
            lines.append(f"- **Duration:** {result.get('duration_seconds', 0)}s")
            lines.append("")

        # Metrics
        lines.append("## Quality Metrics")
        lines.append("")

        metrics = self.log.get("metrics", {})

        # Coverage
        coverage = metrics.get("coverage", {})
        if coverage:
            percent = coverage.get("percent", 0.0)
            emoji = "✅" if coverage.get("passed", False) else "❌"
            lines.append(f"### {emoji} Test Coverage")
            lines.append("")
            lines.append(f"- **Coverage:** {percent}%")
            lines.append(f"- **Total Lines:** {coverage.get('total_lines', 0)}")
            lines.append(f"- **Covered Lines:** {coverage.get('covered_lines', 0)}")
            lines.append("")

        # Security
        security = metrics.get("security", {})
        if security:
            issues_count = security.get("issues_count", 0)
            emoji = "✅" if issues_count == 0 else "❌"
            lines.append(f"### {emoji} Security")
            lines.append("")
            lines.append(f"- **Issues Found:** {issues_count}")
            if issues_count > 0:
                for issue in security.get("issues", [])[:5]:
                    lines.append(f"   - {issue.get('severity')}: {issue.get('message')}")
            lines.append("")

        # Quality
        quality = metrics.get("quality", {})
        if quality:
            issues_count = quality.get("issues_count", 0)
            emoji = "✅" if quality.get("passed", False) else "❌"
            lines.append(f"### {emoji} Code Quality (Linting)")
            lines.append("")
            lines.append(f"- **Issues Found:** {issues_count}")
            lines.append("")

        # Documentation
        documentation = metrics.get("documentation", {})
        if documentation:
            missing = documentation.get("missing_count", 0)
            emoji = "✅" if missing == 0 else "❌"
            lines.append(f"### {emoji} Documentation")
            lines.append("")
            lines.append(f"- **Public Functions:** {documentation.get('total_public_functions', 0)}")
            lines.append(f"- **Missing Docstrings:** {missing}")
            lines.append("")

        # Artifacts
        lines.append("## Generated Artifacts")
        lines.append("")

        artifacts = self.log.get("artifacts", [])
        for artifact in artifacts:
            lines.append(f"- **{artifact['artifact_type']}**: `{artifact['file_path']}`")
            lines.append(f"  - SHA256: `{artifact['sha256_hash']}`")
            lines.append(f"  - Size: {artifact['size_bytes']} bytes")
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"Generated by TDDFeatureAgent on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Escribir archivo
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return md_path

    @staticmethod
    def _calculate_file_hash(file_path: Path) -> str:
        """
        Calcula hash SHA256 de un archivo.

        Args:
            file_path: Path al archivo

        Returns:
            Hash SHA256 en hexadecimal
        """
        if not file_path.exists():
            return ""

        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()
