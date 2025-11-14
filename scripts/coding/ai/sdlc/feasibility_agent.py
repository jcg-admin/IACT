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

import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base_agent import SDLCAgent, SDLCPhaseResult

# Add parent paths for LLMGenerator import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from scripts.coding.ai.generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLMGenerator = None

# Analysis method constants
ANALYSIS_METHOD_LLM = "llm"
ANALYSIS_METHOD_HEURISTIC = "heuristic"


class SDLCFeasibilityAgent(SDLCAgent):
    """
    Agente para la fase de Feasibility Analysis del SDLC.

    Evalua viabilidad tecnica, de negocio y financiera de un feature.
    """

    def __init__(
        self,
        config: Dict[str, Any] = None,
        use_llm: bool = True,
        llm_provider: str = "anthropic",
        model: str = "claude-sonnet-4-5-20250929"
    ):
        super().__init__(
            name="SDLCFeasibilityAgent",
            phase="feasibility",
            config=config
        )

        self.use_llm = use_llm and LLM_AVAILABLE

        if self.use_llm:
            llm_config = {
                "llm_provider": llm_provider,
                "model": model
            }
            self.llm = LLMGenerator(config=llm_config)
            self.logger.info(f"LLMGenerator initialized with {llm_provider}/{model}")
        else:
            self.llm = None
            if use_llm and not LLM_AVAILABLE:
                self.logger.warning("LLM requested but not available, falling back to heuristics")

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

        # Determine analysis method
        analysis_method = ANALYSIS_METHOD_LLM if self.use_llm and self.llm else ANALYSIS_METHOD_HEURISTIC

        # Analisis de viabilidad tecnica
        technical_feasibility = self._analyze_technical_feasibility(
            issue,
            technical_constraints,
            project_context
        )

        # Analisis de riesgos
        risks = self._assess_risks(issue, technical_feasibility, project_context)

        # Analisis de esfuerzo/costo
        effort_analysis = self._analyze_effort(issue, project_context)

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
            "analysis_method": analysis_method,
            "phase_result": phase_result
        }

    def _analyze_technical_feasibility(
        self,
        issue: Dict[str, Any],
        technical_constraints: Dict[str, Any],
        project_context: str = ""
    ) -> Dict[str, Any]:
        """Analiza viabilidad tecnica usando LLM con fallback a heurísticas."""
        if self.use_llm and self.llm:
            try:
                return self._analyze_technical_feasibility_with_llm(
                    issue, technical_constraints, project_context
                )
            except Exception as e:
                self.logger.warning(f"LLM analysis failed: {e}, falling back to heuristics")
                return self._analyze_technical_feasibility_heuristic(
                    issue, technical_constraints
                )
        else:
            return self._analyze_technical_feasibility_heuristic(
                issue, technical_constraints
            )

    def _analyze_technical_feasibility_heuristic(
        self,
        issue: Dict[str, Any],
        technical_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analiza viabilidad tecnica con heurísticas (fallback)."""
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

    def _analyze_technical_feasibility_with_llm(
        self,
        issue: Dict[str, Any],
        technical_constraints: Dict[str, Any],
        project_context: str = ""
    ) -> Dict[str, Any]:
        """Analiza viabilidad tecnica usando LLM."""
        title = issue.get("issue_title", "")
        technical_requirements = issue.get("technical_requirements", [])
        acceptance_criteria = issue.get("acceptance_criteria", [])

        prompt = f"""Analiza la viabilidad técnica del siguiente feature para el proyecto IACT.

**Feature**: {title}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Criterios de Aceptación**:
{chr(10).join(f"- {crit}" for crit in acceptance_criteria)}

**Restricciones Técnicas del Proyecto**:
- No Redis permitido (usar SQLite/Postgres)
- No Email externo (usar InternalMessage)
- Stack: Python 3.11+, Django 4.2+, PostgreSQL

**Contexto del Proyecto**: {project_context}

Evalúa la viabilidad técnica considerando:
1. Si el feature viola restricciones críticas del proyecto
2. Complejidad técnica (arquitectura, refactoring, integraciones)
3. Dependencias externas o coordinación requerida
4. Riesgos técnicos potenciales

Responde en formato JSON:
{{
  "is_feasible": true/false,
  "score": 0.0-1.0,
  "blockers": ["lista de bloqueadores críticos"],
  "concerns": ["lista de preocupaciones técnicas"],
  "reasoning": "explicación detallada"
}}"""

        llm_response = self.llm._call_llm(prompt)
        return self._parse_llm_technical_feasibility(llm_response, issue, technical_constraints)

    def _parse_llm_technical_feasibility(
        self,
        llm_response: str,
        issue: Dict[str, Any],
        technical_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response para extraer análisis de viabilidad técnica."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                # Validate and normalize
                feasibility = {
                    "is_feasible": result.get("is_feasible", True),
                    "score": float(result.get("score", 0.8)),
                    "blockers": result.get("blockers", []),
                    "concerns": result.get("concerns", []),
                    "reasoning": result.get("reasoning", "")
                }

                # Ensure score is in valid range
                feasibility["score"] = max(0.0, min(1.0, feasibility["score"]))

                return feasibility
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM response as JSON: {e}")

        # Fallback: parse as text
        feasibility = {
            "is_feasible": "no es viable" not in llm_response.lower() and "not feasible" not in llm_response.lower(),
            "score": 0.7,  # Default moderate score
            "blockers": [],
            "concerns": [],
            "reasoning": llm_response
        }

        # Extract blockers from text
        if "blocker" in llm_response.lower():
            lines = llm_response.split('\n')
            for line in lines:
                if "blocker" in line.lower():
                    feasibility["blockers"].append(line.strip())

        # Extract concerns
        if "concern" in llm_response.lower() or "preocupación" in llm_response.lower():
            lines = llm_response.split('\n')
            for line in lines:
                if "concern" in line.lower() or "preocupación" in line.lower():
                    feasibility["concerns"].append(line.strip())

        return feasibility

    def _assess_risks(
        self,
        issue: Dict[str, Any],
        technical_feasibility: Dict[str, Any],
        project_context: str = ""
    ) -> List[Dict[str, Any]]:
        """Identifica y clasifica riesgos usando LLM con fallback a heurísticas."""
        if self.use_llm and self.llm:
            try:
                return self._assess_risks_with_llm(
                    issue, technical_feasibility, project_context
                )
            except Exception as e:
                self.logger.warning(f"LLM risk assessment failed: {e}, falling back to heuristics")
                return self._assess_risks_heuristic(issue, technical_feasibility)
        else:
            return self._assess_risks_heuristic(issue, technical_feasibility)

    def _assess_risks_heuristic(
        self,
        issue: Dict[str, Any],
        technical_feasibility: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identifica y clasifica riesgos con heurísticas (fallback)."""
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

    def _assess_risks_with_llm(
        self,
        issue: Dict[str, Any],
        technical_feasibility: Dict[str, Any],
        project_context: str = ""
    ) -> List[Dict[str, Any]]:
        """Identifica y clasifica riesgos usando LLM."""
        title = issue.get("issue_title", "")
        story_points = issue.get("story_points", 0)
        priority = issue.get("priority", "P2")
        acceptance_criteria = issue.get("acceptance_criteria", [])

        prompt = f"""Identifica y evalúa riesgos para el siguiente feature del proyecto IACT.

**Feature**: {title}
**Prioridad**: {priority}
**Story Points**: {story_points}
**Criterios de Aceptación**: {len(acceptance_criteria)} definidos

**Análisis de Viabilidad Técnica**:
- Score: {technical_feasibility.get('score', 0.0):.1%}
- Es Viable: {'Sí' if technical_feasibility.get('is_feasible', True) else 'No'}
- Bloqueadores: {', '.join(technical_feasibility.get('blockers', [])) or 'Ninguno'}
- Preocupaciones: {', '.join(technical_feasibility.get('concerns', [])) or 'Ninguna'}

**Contexto del Proyecto**: {project_context}

Identifica riesgos considerando:
1. Riesgos técnicos (complejidad, arquitectura, dependencias)
2. Riesgos de cronograma (presión de tiempo, recursos)
3. Riesgos de requisitos (claridad, completitud)
4. Probabilidad e impacto de cada riesgo
5. Estrategias de mitigación

Responde en formato JSON con array de riesgos:
{{
  "risks": [
    {{
      "type": "technical|schedule|requirements|business",
      "severity": "critical|high|medium|low",
      "probability": "high|medium|low",
      "description": "descripción del riesgo",
      "mitigation": "estrategia de mitigación",
      "impact": "impacto si ocurre"
    }}
  ]
}}"""

        llm_response = self.llm._call_llm(prompt)
        return self._parse_llm_risks(llm_response, issue, technical_feasibility)

    def _parse_llm_risks(
        self,
        llm_response: str,
        issue: Dict[str, Any],
        technical_feasibility: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response para extraer riesgos identificados."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                risks = result.get("risks", [])

                # Validate and normalize each risk
                normalized_risks = []
                for risk in risks:
                    if isinstance(risk, dict) and "description" in risk:
                        normalized_risk = {
                            "type": risk.get("type", "technical"),
                            "severity": risk.get("severity", "medium"),
                            "probability": risk.get("probability", "medium"),
                            "description": risk.get("description", ""),
                            "mitigation": risk.get("mitigation", ""),
                            "impact": risk.get("impact", "")
                        }
                        normalized_risks.append(normalized_risk)

                if normalized_risks:
                    return normalized_risks

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM risks as JSON: {e}")

        # Fallback: parse as text
        risks = []
        lines = llm_response.split('\n')

        current_risk = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect risk markers
            if any(marker in line.lower() for marker in ['risk:', 'riesgo:', 'risk -', 'riesgo -']):
                if current_risk:
                    risks.append(current_risk)

                # Extract severity from line
                severity = "medium"
                if "critical" in line.lower() or "crítico" in line.lower():
                    severity = "critical"
                elif "high" in line.lower() or "alto" in line.lower():
                    severity = "high"
                elif "low" in line.lower() or "bajo" in line.lower():
                    severity = "low"

                current_risk = {
                    "type": "technical",
                    "severity": severity,
                    "probability": "medium",
                    "description": line,
                    "mitigation": "",
                    "impact": ""
                }
            elif current_risk and ("mitigation" in line.lower() or "mitigación" in line.lower()):
                current_risk["mitigation"] = line
            elif current_risk and ("impact" in line.lower() or "impacto" in line.lower()):
                current_risk["impact"] = line

        if current_risk:
            risks.append(current_risk)

        # If no risks parsed, return at least one generic risk
        if not risks:
            risks.append({
                "type": "requirements",
                "severity": "medium",
                "probability": "medium",
                "description": "Análisis de riesgos requiere refinamiento",
                "mitigation": "Revisar con stakeholders y expertos técnicos",
                "impact": "Posibles sorpresas durante implementación"
            })

        return risks

    def _analyze_effort(self, issue: Dict[str, Any], project_context: str = "") -> Dict[str, Any]:
        """Analiza esfuerzo y costo usando LLM con fallback a heurísticas."""
        if self.use_llm and self.llm:
            try:
                return self._analyze_effort_with_llm(issue, project_context)
            except Exception as e:
                self.logger.warning(f"LLM effort analysis failed: {e}, falling back to heuristics")
                return self._analyze_effort_heuristic(issue)
        else:
            return self._analyze_effort_heuristic(issue)

    def _analyze_effort_heuristic(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza esfuerzo y costo con heurísticas (fallback)."""
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

    def _analyze_effort_with_llm(
        self,
        issue: Dict[str, Any],
        project_context: str = ""
    ) -> Dict[str, Any]:
        """Analiza esfuerzo y costo usando LLM."""
        title = issue.get("issue_title", "")
        story_points = issue.get("story_points", 0)
        technical_requirements = issue.get("technical_requirements", [])

        prompt = f"""Estima el esfuerzo y costo para implementar el siguiente feature del proyecto IACT.

**Feature**: {title}
**Story Points Estimados**: {story_points}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Contexto del Proyecto**: {project_context}

Considera:
1. Story points ya estimados (1 SP ≈ 4 horas ideales)
2. Complejidad técnica adicional (arquitectura, refactoring, testing)
3. Riesgo de subestimación
4. Tamaño de equipo recomendado
5. Factores de ajuste (migraciones, integraciones, etc)

Responde en formato JSON:
{{
  "story_points": {story_points},
  "estimated_hours": X,
  "estimated_days": Y,
  "complexity_multiplier": 1.0-2.0,
  "team_size_recommended": 1-3,
  "reasoning": "explicación de la estimación"
}}"""

        llm_response = self.llm._call_llm(prompt)
        return self._parse_llm_effort(llm_response, issue)

    def _parse_llm_effort(
        self,
        llm_response: str,
        issue: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response para extraer análisis de esfuerzo."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                # Validate and normalize
                effort = {
                    "story_points": int(result.get("story_points", issue.get("story_points", 0))),
                    "estimated_hours": float(result.get("estimated_hours", 40)),
                    "estimated_days": float(result.get("estimated_days", 5)),
                    "complexity_multiplier": float(result.get("complexity_multiplier", 1.0)),
                    "team_size_recommended": int(result.get("team_size_recommended", 1)),
                    "reasoning": result.get("reasoning", "")
                }

                # Ensure reasonable ranges
                effort["complexity_multiplier"] = max(1.0, min(3.0, effort["complexity_multiplier"]))
                effort["team_size_recommended"] = max(1, min(5, effort["team_size_recommended"]))

                return effort

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM effort as JSON: {e}")

        # Fallback: extract numbers from text
        story_points = issue.get("story_points", 0)
        hours_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:horas|hours)', llm_response, re.IGNORECASE)
        days_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:días|days)', llm_response, re.IGNORECASE)

        estimated_hours = float(hours_match.group(1)) if hours_match else story_points * 4
        estimated_days = float(days_match.group(1)) if days_match else estimated_hours / 8

        return {
            "story_points": story_points,
            "estimated_hours": estimated_hours,
            "estimated_days": estimated_days,
            "complexity_multiplier": 1.0,
            "team_size_recommended": 1 if story_points <= 5 else 2,
            "reasoning": llm_response[:200]
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
