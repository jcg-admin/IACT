"""
SDLCFeasibilityAgent - Fase 2: Feasibility Analysis

Responsabilidad: Analizar viabilidad tecnica y de negocio de un feature,
identificar riesgos, estimar costos y generar recomendacion Go/No-Go.

Inputs:
- issue (dict): Issue generado por SDLCPlannerAgent
- project_context (str): Contexto del proyecto
- technical_constraints (dict): Restricciones tecnicas (RNF-002, etc)

Outputs:
- Feasibility report completo
- Risk assessment matrix
- Go/No-Go recommendation
- Alternative approaches si es No-Go
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .sdlc_base import SDLCAgent, SDLCPhaseResult


class SDLCFeasibilityAgent(SDLCAgent):
    """
    Agente para la fase de Feasibility Analysis del SDLC.

    Evalua viabilidad tecnica, de negocio y financiera de un feature.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCFeasibilityAgent",
            phase="feasibility",
            config=config
        )

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que exista un issue."""
        errors = []

        if "issue" not in input_data:
            errors.append("Falta 'issue' en input (del SDLCPlannerAgent)")

        if "issue" in input_data:
            issue = input_data["issue"]
            if not isinstance(issue, dict):
                errors.append("'issue' debe ser un diccionario")
            elif "issue_title" not in issue:
                errors.append("'issue' debe tener 'issue_title'")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la fase de Feasibility Analysis.

        Args:
            input_data: {
                "issue": dict,  # Output de SDLCPlannerAgent
                "project_context": str,
                "technical_constraints": dict
            }

        Returns:
            Dict con feasibility report, risk matrix, go/no-go
        """
        issue = input_data["issue"]
        project_context = input_data.get("project_context", "")
        technical_constraints = input_data.get("technical_constraints", {})

        self.logger.info(f"Analizando viabilidad de: {issue.get('issue_title', 'Unknown')}")

        # Analisis de viabilidad tecnica
        technical_feasibility = self._analyze_technical_feasibility(
            issue,
            technical_constraints
        )

        # Analisis de riesgos
        risks = self._assess_risks(issue, technical_feasibility)

        # Analisis de esfuerzo/costo
        effort_analysis = self._analyze_effort(issue)

        # Decision Go/No-Go
        decision = self._make_decision(
            technical_feasibility,
            risks,
            effort_analysis
        )

        # Generar report
        report = self._generate_report(
            issue,
            technical_feasibility,
            risks,
            effort_analysis,
            decision
        )

        # Guardar artefacto
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"FEASIBILITY_REPORT_{timestamp}.md"
        report_path = self.save_artifact(report, report_filename)

        # Crear resultado de fase
        phase_result = self.create_phase_result(
            decision=decision["decision"],
            confidence=decision["confidence"],
            artifacts=[str(report_path)],
            recommendations=decision["recommendations"],
            risks=risks,
            next_steps=decision["next_steps"]
        )

        return {
            "feasibility_report": report,
            "report_path": str(report_path),
            "technical_feasibility": technical_feasibility,
            "risks": risks,
            "effort_analysis": effort_analysis,
            "decision": decision["decision"],
            "confidence": decision["confidence"],
            "phase_result": phase_result
        }

    def _analyze_technical_feasibility(
        self,
        issue: Dict[str, Any],
        technical_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza viabilidad tecnica."""
        title = issue.get("issue_title", "")
        technical_requirements = issue.get("technical_requirements", [])

        feasibility = {
            "is_feasible": True,
            "score": 0.0,  # 0.0 - 1.0
            "concerns": [],
            "blockers": []
        }

        score_factors = []

        # Check restricciones criticas IACT
        if technical_constraints.get("no_redis", True):
            if any("redis" in req.lower() for req in technical_requirements):
                feasibility["blockers"].append(
                    "BLOCKER: Feature requiere Redis pero esta prohibido (RNF-002)"
                )
                feasibility["is_feasible"] = False
                score_factors.append(0.0)

        if technical_constraints.get("no_email", True):
            if any("email" in req.lower() or "smtp" in req.lower() for req in technical_requirements):
                feasibility["blockers"].append(
                    "BLOCKER: Feature requiere email pero esta prohibido. Usar InternalMessage"
                )
                score_factors.append(0.3)  # Mitigable con InternalMessage

        # Check complejidad tecnica
        if "arquitectura" in title.lower() or "refactor" in title.lower():
            feasibility["concerns"].append(
                "Alta complejidad: Cambios arquitectonicos requieren revision de arquitecto"
            )
            score_factors.append(0.6)
        else:
            score_factors.append(0.9)

        # Check dependencias externas
        if "integracion" in title.lower() or "api externa" in title.lower():
            feasibility["concerns"].append(
                "Dependencias externas: Requiere coordinacion con sistemas externos"
            )
            score_factors.append(0.7)
        else:
            score_factors.append(0.9)

        # Calcular score
        if score_factors:
            feasibility["score"] = sum(score_factors) / len(score_factors)

        return feasibility

    def _assess_risks(
        self,
        issue: Dict[str, Any],
        technical_feasibility: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identifica y clasifica riesgos."""
        risks = []

        story_points = issue.get("story_points", 0)
        priority = issue.get("priority", "P2")

        # Risk: Complejidad alta
        if story_points >= 13:
            risks.append({
                "type": "technical",
                "severity": "high",
                "probability": "medium",
                "description": f"Alta complejidad ({story_points} story points)",
                "mitigation": "Dividir en sub-features mas pequenos",
                "impact": "Retrasos en delivery, posible deuda tecnica"
            })

        # Risk: Restricciones tecnicas
        if technical_feasibility["blockers"]:
            risks.append({
                "type": "technical",
                "severity": "critical",
                "probability": "high",
                "description": "Violacion de restricciones criticas",
                "mitigation": "Redisenar feature para cumplir restricciones",
                "impact": "Feature no implementable sin cambios mayores"
            })

        # Risk: Prioridad critica pero complejidad alta
        if priority == "P0" and story_points >= 8:
            risks.append({
                "type": "schedule",
                "severity": "high",
                "probability": "medium",
                "description": "Feature critico con alta complejidad",
                "mitigation": "Asignar equipo dedicado, reducir scope inicial",
                "impact": "Presion en equipo, posible burnout"
            })

        # Risk: Falta de acceptance criteria claros
        acceptance_criteria = issue.get("acceptance_criteria", [])
        if len(acceptance_criteria) < 3:
            risks.append({
                "type": "requirements",
                "severity": "medium",
                "probability": "high",
                "description": "Acceptance criteria insuficientes",
                "mitigation": "Refinar requisitos con stakeholders antes de implementar",
                "impact": "Re-trabajo, expectativas no alineadas"
            })

        return risks

    def _analyze_effort(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza esfuerzo y costo estimado."""
        story_points = issue.get("story_points", 0)
        technical_requirements = issue.get("technical_requirements", [])

        # Estimacion simplificada: 1 SP = 4 horas de trabajo
        hours_estimate = story_points * 4

        # Ajustar por complejidad tecnica
        complexity_multiplier = 1.0
        if len(technical_requirements) > 5:
            complexity_multiplier = 1.3
        if any("migration" in req.lower() for req in technical_requirements):
            complexity_multiplier = 1.5

        adjusted_hours = hours_estimate * complexity_multiplier

        return {
            "story_points": story_points,
            "estimated_hours": adjusted_hours,
            "estimated_days": adjusted_hours / 8,
            "complexity_multiplier": complexity_multiplier,
            "team_size_recommended": 1 if story_points <= 5 else 2
        }

    def _make_decision(
        self,
        technical_feasibility: Dict[str, Any],
        risks: List[Dict[str, Any]],
        effort_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera decision Go/No-Go."""
        decision = {
            "decision": "go",
            "confidence": 0.0,
            "recommendations": [],
            "next_steps": []
        }

        # Calcular confidence
        confidence_factors = []

        # Factor 1: Viabilidad tecnica
        confidence_factors.append(technical_feasibility["score"])

        # Factor 2: Riesgos
        critical_risks = [r for r in risks if r["severity"] == "critical"]
        high_risks = [r for r in risks if r["severity"] == "high"]

        if critical_risks:
            confidence_factors.append(0.0)
            decision["decision"] = "no-go"
        elif high_risks:
            confidence_factors.append(0.5)
            if len(high_risks) >= 3:
                decision["decision"] = "review"
        else:
            confidence_factors.append(0.9)

        # Factor 3: Esfuerzo razonable
        if effort_analysis["estimated_days"] > 20:
            confidence_factors.append(0.4)
            decision["recommendations"].append(
                "Feature muy grande (>20 dias). Considerar dividir en fases."
            )
        else:
            confidence_factors.append(0.9)

        # Calcular confidence final
        decision["confidence"] = sum(confidence_factors) / len(confidence_factors)

        # Generar recomendaciones
        if decision["decision"] == "go":
            decision["recommendations"].append("Feature es viable tecnicamente")
            decision["recommendations"].append(
                f"Proceder con fase de Design (HLD/LLD)"
            )
            decision["next_steps"].append("Crear High-Level Design (HLD)")
            decision["next_steps"].append("Crear Low-Level Design (LLD)")
            decision["next_steps"].append("Generar ADRs si hay decisiones arquitectonicas")

        elif decision["decision"] == "review":
            decision["recommendations"].append(
                "Feature requiere revision por riesgos identificados"
            )
            decision["recommendations"].append(
                "Mitigar riesgos HIGH antes de proceder"
            )
            decision["next_steps"].append("Reunion con stakeholders para revisar riesgos")
            decision["next_steps"].append("Refinar requisitos y reducir scope si es necesario")

        else:  # no-go
            decision["recommendations"].append(
                "Feature NO es viable en estado actual"
            )
            decision["recommendations"].append(
                "Redisenar feature para cumplir restricciones"
            )
            decision["next_steps"].append("Identificar enfoques alternativos")
            decision["next_steps"].append("Reunir equipo para redefinir feature")

        return decision

    def _generate_report(
        self,
        issue: Dict[str, Any],
        technical_feasibility: Dict[str, Any],
        risks: List[Dict[str, Any]],
        effort_analysis: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> str:
        """Genera reporte de viabilidad en Markdown."""
        report = f"""# Feasibility Analysis Report

**Feature**: {issue.get('issue_title', 'Unknown')}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Analyst**: SDLCFeasibilityAgent

---

## Executive Summary

**Decision**: {decision["decision"].upper()}
**Confidence**: {decision["confidence"] * 100:.1f}%

{chr(10).join(f"- {rec}" for rec in decision["recommendations"])}

---

## Technical Feasibility

**Score**: {technical_feasibility["score"] * 100:.1f}%
**Is Feasible**: {"YES" if technical_feasibility["is_feasible"] else "NO"}

"""

        if technical_feasibility["blockers"]:
            report += "### BLOCKERS\n\n"
            for blocker in technical_feasibility["blockers"]:
                report += f"- {blocker}\n"
            report += "\n"

        if technical_feasibility["concerns"]:
            report += "### Concerns\n\n"
            for concern in technical_feasibility["concerns"]:
                report += f"- {concern}\n"
            report += "\n"

        report += """---

## Risk Assessment

"""

        if risks:
            report += "| Risk | Severity | Probability | Mitigation |\n"
            report += "|------|----------|-------------|------------|\n"
            for risk in risks:
                report += f"| {risk['description']} | {risk['severity'].upper()} | {risk['probability']} | {risk['mitigation']} |\n"
        else:
            report += "No significant risks identified.\n"

        report += f"""
---

## Effort Analysis

**Story Points**: {effort_analysis["story_points"]}
**Estimated Hours**: {effort_analysis["estimated_hours"]:.1f}h
**Estimated Days**: {effort_analysis["estimated_days"]:.1f} days
**Complexity Multiplier**: {effort_analysis["complexity_multiplier"]}x
**Recommended Team Size**: {effort_analysis["team_size_recommended"]} developer(s)

---

## Next Steps

"""

        for i, step in enumerate(decision["next_steps"], 1):
            report += f"{i}. {step}\n"

        report += f"""
---

## Original Issue Details

**Priority**: {issue.get('priority', 'N/A')}
**Story Points**: {issue.get('story_points', 0)}

**Technical Requirements**:
"""

        for req in issue.get("technical_requirements", []):
            report += f"- {req}\n"

        report += f"""
**Acceptance Criteria**: {len(issue.get('acceptance_criteria', []))} defined

---

*Generated by SDLCFeasibilityAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return report

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Guardrails especificos para Feasibility phase."""
        errors = []

        # Validar que se genero decision
        if "decision" not in output_data:
            errors.append("No se genero decision (go/no-go/review)")

        # Validar que hay risk assessment
        if "risks" not in output_data:
            errors.append("No se realizo risk assessment")

        # Validar confidence razonable
        confidence = output_data.get("confidence", 0)
        if confidence <= 0 or confidence > 1:
            errors.append(f"Confidence fuera de rango: {confidence}")

        return errors
