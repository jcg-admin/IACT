"""
SDLCOrchestratorAgent - Pipeline Orchestrator

Responsabilidad: Orquestar todo el pipeline SDLC de punta a punta,
coordinando todos los agentes y manejando Go/No-Go decisions.

Inputs:
- feature_request (str): Descripcion del feature a implementar
- project_context (str): Contexto del proyecto
- start_phase (str): Fase inicial (default: "planning")
- end_phase (str): Fase final (default: "deployment")

Outputs:
- Complete SDLC execution report
- Artifacts from all phases
- Final Go/No-Go recommendation
- Lessons learned
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import SDLCAgent, SDLCPhaseResult
from .planner_agent import SDLCPlannerAgent
from .feasibility_agent import SDLCFeasibilityAgent
from .design_agent import SDLCDesignAgent
from .testing_agent import SDLCTestingAgent
from .deployment_agent import SDLCDeploymentAgent

# Add parent paths for LLMGenerator import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLMGenerator = None

# Orchestration method constants
ORCHESTRATION_METHOD_LLM = "llm"
ORCHESTRATION_METHOD_HEURISTIC = "heuristic"


class SDLCOrchestratorAgent(SDLCAgent):
    """
    Agente orquestador del pipeline SDLC completo.

    Ejecuta todas las fases del SDLC en secuencia, manejando Go/No-Go decisions
    y generando reporte completo.
    """

    VALID_PHASES = ["planning", "feasibility", "design", "implementation", "testing", "deployment", "maintenance"]

    # Orchestration method constants (class-level)
    ORCHESTRATION_METHOD_LLM = ORCHESTRATION_METHOD_LLM
    ORCHESTRATION_METHOD_HEURISTIC = ORCHESTRATION_METHOD_HEURISTIC

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCOrchestratorAgent",
            phase="orchestration",
            config=config
        )

        # Initialize all SDLC agents
        self.planner_agent = SDLCPlannerAgent(config)
        self.feasibility_agent = SDLCFeasibilityAgent(config)
        self.design_agent = SDLCDesignAgent(config)
        self.testing_agent = SDLCTestingAgent(config)
        self.deployment_agent = SDLCDeploymentAgent(config)

        # Initialize LLM generator if config provided and LLM available
        self.llm_generator = None
        self.use_llm = False
        if config and LLM_AVAILABLE:
            try:
                self.llm_generator = LLMGenerator(config=config)
                self.use_llm = True
                self.logger.info(f"LLMGenerator initialized for orchestration with {config.get('llm_provider', 'default')}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize LLM for orchestration: {e}. Using heuristics only.")

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida inputs del orchestrator."""
        errors = []

        if "feature_request" not in input_data or not input_data["feature_request"]:
            errors.append("Falta 'feature_request' (descripcion del feature)")

        # Validar fases
        start_phase = input_data.get("start_phase", "planning")
        end_phase = input_data.get("end_phase", "deployment")

        if start_phase not in self.VALID_PHASES:
            errors.append(f"start_phase invalido: {start_phase}. Validos: {self.VALID_PHASES}")

        if end_phase not in self.VALID_PHASES:
            errors.append(f"end_phase invalido: {end_phase}. Validos: {self.VALID_PHASES}")

        # Validar orden de fases
        if start_phase in self.VALID_PHASES and end_phase in self.VALID_PHASES:
            start_idx = self.VALID_PHASES.index(start_phase)
            end_idx = self.VALID_PHASES.index(end_phase)
            if start_idx > end_idx:
                errors.append(f"start_phase ({start_phase}) debe ser antes de end_phase ({end_phase})")

        return errors

    def _should_proceed_to_next_phase(
        self,
        current_phase: str,
        phase_result: Dict[str, Any]
    ) -> bool:
        """Decide si proceder a siguiente fase usando LLM con fallback a heurísticas."""
        if self.use_llm and self.llm_generator:
            try:
                return self._should_proceed_to_next_phase_with_llm(current_phase, phase_result)
            except Exception as e:
                self.logger.warning(f"LLM phase decision failed: {e}, falling back to heuristics")
                return self._should_proceed_to_next_phase_heuristic(current_phase, phase_result)
        else:
            return self._should_proceed_to_next_phase_heuristic(current_phase, phase_result)

    def _should_proceed_to_next_phase_heuristic(
        self,
        current_phase: str,
        phase_result: Dict[str, Any]
    ) -> bool:
        """Decision heurística para proceder a siguiente fase."""
        # Simple heuristic: check decision and confidence
        decision = phase_result.get("decision", "go")
        confidence = phase_result.get("confidence", 1.0)

        if decision == "no-go":
            return False
        elif decision == "review" and confidence < 0.5:
            return False
        return True

    def _should_proceed_to_next_phase_with_llm(
        self,
        current_phase: str,
        phase_result: Dict[str, Any]
    ) -> bool:
        """Decision con LLM para proceder a siguiente fase."""
        decision = phase_result.get("decision", "go")
        confidence = phase_result.get("confidence", 1.0)
        risks = phase_result.get("risks", [])

        prompt = f"""Analiza si el pipeline SDLC debe proceder a la siguiente fase.

**Fase Actual**: {current_phase}
**Decisión de Fase**: {decision}
**Confianza**: {confidence * 100:.1f}%
**Riesgos Identificados**: {len(risks)}

**Detalles de Riesgos**:
{json.dumps(risks[:5], indent=2) if risks else "Ninguno"}

Considera:
1. Si la decisión es "no-go", NO debe proceder
2. Si hay riesgos críticos sin mitigación, debe detenerse
3. Si la confianza es muy baja (<40%), revisar antes de proceder
4. "review" puede proceder con precauciones

Responde en formato JSON:
{{
  "should_proceed": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "explicación de la decisión"
}}"""

        llm_response = self.llm_generator._call_llm(prompt)
        result = self._parse_llm_phase_decision(llm_response, phase_result)
        return result.get("should_proceed", True)

    def _parse_llm_phase_decision(
        self,
        llm_response: str,
        phase_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Parse LLM response para decisión de fase."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))
                return {
                    "should_proceed": result.get("should_proceed", True),
                    "confidence": float(result.get("confidence", 0.8)),
                    "reasoning": result.get("reasoning", "")
                }
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM phase decision: {e}")

        # Fallback: simple text analysis
        should_proceed = "no debe proceder" not in llm_response.lower() and "should not proceed" not in llm_response.lower()
        return {
            "should_proceed": should_proceed,
            "confidence": 0.7,
            "reasoning": llm_response[:200]
        }

    def _aggregate_risks_with_llm(
        self,
        phase_results: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Agrega y analiza riesgos de todas las fases usando LLM."""
        # Collect all risks from phases
        all_risks = []
        for phase, result in phase_results.items():
            risks = result.get("risks", [])
            for risk in risks:
                risk_with_phase = risk.copy()
                risk_with_phase["source_phase"] = phase
                all_risks.append(risk_with_phase)

        if not all_risks:
            return []

        prompt = f"""Agrega y analiza los riesgos identificados en múltiples fases del SDLC.

**Total de Riesgos**: {len(all_risks)}

**Riesgos por Fase**:
{json.dumps(all_risks, indent=2)}

Tarea:
1. Identifica riesgos duplicados o relacionados entre fases
2. Agrega riesgos similares en uno solo
3. Prioriza por severidad e impacto acumulado
4. Identifica patrones de riesgo cross-fase
5. Genera lista final de riesgos únicos con severidad ajustada

Responde en formato JSON:
{{
  "aggregated_risks": [
    {{
      "type": "technical|schedule|requirements|business",
      "severity": "critical|high|medium|low",
      "description": "descripción del riesgo agregado",
      "phases": ["lista de fases donde aparece"],
      "mitigation": "estrategia de mitigación combinada"
    }}
  ],
  "overall_risk_level": "critical|high|medium|low"
}}"""

        try:
            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_aggregated_risks(llm_response, all_risks)
        except Exception as e:
            self.logger.warning(f"LLM risk aggregation failed: {e}")
            return all_risks  # Return original risks as fallback

    def _parse_llm_aggregated_risks(
        self,
        llm_response: str,
        original_risks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response para riesgos agregados."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))
                aggregated_risks = result.get("aggregated_risks", [])
                if aggregated_risks:
                    return aggregated_risks
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM aggregated risks: {e}")

        # Fallback: return original risks
        return original_risks

    def _synthesize_recommendations_with_llm(
        self,
        phase_results: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Sintetiza recomendaciones de todas las fases usando LLM."""
        # Collect all recommendations
        all_recommendations = {}
        for phase, result in phase_results.items():
            recommendations = result.get("recommendations", [])
            if recommendations:
                all_recommendations[phase] = recommendations

        if not all_recommendations:
            return ["Pipeline ejecutado exitosamente. Proceder con siguiente fase."]

        prompt = f"""Sintetiza recomendaciones de múltiples fases del SDLC en un conjunto coherente de acciones.

**Recomendaciones por Fase**:
{json.dumps(all_recommendations, indent=2)}

**Resultados de Fases**:
{json.dumps({k: {"decision": v.get("decision"), "confidence": v.get("confidence")} for k, v in phase_results.items()}, indent=2)}

Tarea:
1. Elimina recomendaciones duplicadas o conflictivas
2. Prioriza recomendaciones por impacto
3. Agrupa recomendaciones relacionadas
4. Genera lista final de 3-7 recomendaciones accionables
5. Ordena por prioridad (más importante primero)

Responde en formato JSON:
{{
  "recommendations": [
    "Recomendación 1 (más importante)",
    "Recomendación 2",
    "Recomendación 3"
  ],
  "priority": "high|medium|low"
}}"""

        try:
            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_recommendations(llm_response, all_recommendations)
        except Exception as e:
            self.logger.warning(f"LLM recommendation synthesis failed: {e}")
            # Fallback: flatten all recommendations
            recommendations = []
            for recs in all_recommendations.values():
                recommendations.extend(recs)
            return recommendations[:7]  # Limit to 7

    def _parse_llm_recommendations(
        self,
        llm_response: str,
        original_recommendations: Dict[str, List[str]]
    ) -> List[str]:
        """Parse LLM response para recomendaciones sintetizadas."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))
                recommendations = result.get("recommendations", [])
                if recommendations:
                    return recommendations
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM recommendations: {e}")

        # Fallback: extract from text
        recommendations = []
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered lists
            if line.startswith('-') or line.startswith('•') or re.match(r'^\d+\.', line):
                recommendations.append(line.lstrip('-•0123456789. '))

        return recommendations[:7] if recommendations else ["Revisar resultados del pipeline"]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el pipeline SDLC completo.

        Args:
            input_data: {
                "feature_request": str,  # Descripcion del feature
                "project_context": str,  # Contexto del proyecto (optional)
                "technical_constraints": dict,  # Restricciones tecnicas (optional)
                "start_phase": str,  # Fase inicial (default: "planning")
                "end_phase": str,  # Fase final (default: "deployment")
                "skip_phases": list,  # Fases a saltar (optional)
            }

        Returns:
            Dict con resultados de todas las fases, artifacts, reporte final
        """
        feature_request = input_data["feature_request"]
        project_context = input_data.get("project_context", "")
        technical_constraints = input_data.get("technical_constraints", {
            "no_redis": True,
            "no_email": True
        })
        start_phase = input_data.get("start_phase", "planning")
        end_phase = input_data.get("end_phase", "deployment")
        skip_phases = input_data.get("skip_phases", [])

        self.logger.info(f"Iniciando SDLC pipeline: {start_phase} -> {end_phase}")
        feature_title = feature_request.get("title", "Unknown") if isinstance(feature_request, dict) else str(feature_request)[:100]
        self.logger.info(f"Feature: {feature_title}")

        # Track execution
        execution_log = []
        all_artifacts = []
        phase_results = {}

        # Execute phases in sequence
        try:
            # Phase 1: Planning
            if self._should_execute_phase("planning", start_phase, end_phase, skip_phases):
                self.logger.info("Ejecutando fase: Planning")
                planning_result = self._execute_planning(feature_request, project_context)
                phase_results["planning"] = planning_result
                all_artifacts.extend(planning_result.get("artifacts", []))
                execution_log.append({
                    "phase": "planning",
                    "status": "completed",
                    "decision": planning_result.get("phase_result", {}).decision if planning_result.get("phase_result") else "go"
                })

            # Phase 2: Feasibility
            if self._should_execute_phase("feasibility", start_phase, end_phase, skip_phases):
                if "planning" not in phase_results:
                    raise ValueError("Feasibility phase requiere Planning phase primero")

                self.logger.info("Ejecutando fase: Feasibility")
                feasibility_result = self._execute_feasibility(
                    phase_results["planning"],
                    technical_constraints
                )
                phase_results["feasibility"] = feasibility_result
                all_artifacts.extend(feasibility_result.get("artifacts", []))

                # Check Go/No-Go
                decision = feasibility_result.get("decision", "go")
                execution_log.append({
                    "phase": "feasibility",
                    "status": "completed",
                    "decision": decision
                })

                if decision == "no-go":
                    self.logger.warning("Feasibility: NO-GO. Deteniendo pipeline.")
                    return self._generate_early_stop_report(
                        feature_request,
                        phase_results,
                        all_artifacts,
                        execution_log,
                        "feasibility",
                        "Feature no es viable. Resolver blockers identificados."
                    )

            # Phase 3: Design
            if self._should_execute_phase("design", start_phase, end_phase, skip_phases):
                if "feasibility" not in phase_results:
                    raise ValueError("Design phase requiere Feasibility phase primero")

                self.logger.info("Ejecutando fase: Design")
                design_result = self._execute_design(
                    phase_results["planning"],
                    phase_results["feasibility"],
                    project_context
                )
                phase_results["design"] = design_result
                all_artifacts.extend(design_result.get("artifacts", []))
                execution_log.append({
                    "phase": "design",
                    "status": "completed",
                    "decision": "go"
                })

            # Phase 4: Implementation (Manual - Not executed by agent)
            if self._should_execute_phase("implementation", start_phase, end_phase, skip_phases):
                self.logger.info("Fase Implementation: MANUAL (no ejecutada por agent)")
                execution_log.append({
                    "phase": "implementation",
                    "status": "manual",
                    "decision": "n/a"
                })

            # Phase 5: Testing
            if self._should_execute_phase("testing", start_phase, end_phase, skip_phases):
                if "design" not in phase_results:
                    raise ValueError("Testing phase requiere Design phase primero")

                self.logger.info("Ejecutando fase: Testing")
                testing_result = self._execute_testing(
                    phase_results["planning"],
                    phase_results["design"]
                )
                phase_results["testing"] = testing_result
                all_artifacts.extend(testing_result.get("artifacts", []))
                execution_log.append({
                    "phase": "testing",
                    "status": "completed",
                    "decision": "go"
                })

            # Phase 6: Deployment
            if self._should_execute_phase("deployment", start_phase, end_phase, skip_phases):
                if "testing" not in phase_results:
                    raise ValueError("Deployment phase requiere Testing phase primero")

                self.logger.info("Ejecutando fase: Deployment")
                environment = input_data.get("environment", "staging")
                deployment_result = self._execute_deployment(
                    phase_results["planning"],
                    phase_results["design"],
                    phase_results["testing"],
                    environment
                )
                phase_results["deployment"] = deployment_result
                all_artifacts.extend(deployment_result.get("artifacts", []))
                execution_log.append({
                    "phase": "deployment",
                    "status": "completed",
                    "decision": "go"
                })

        except Exception as e:
            self.logger.error(f"Error en pipeline SDLC: {e}")
            execution_log.append({
                "phase": "error",
                "status": "failed",
                "error": str(e)
            })
            raise

        # Determine orchestration method
        orchestration_method = ORCHESTRATION_METHOD_LLM if self.use_llm and self.llm_generator else ORCHESTRATION_METHOD_HEURISTIC

        # Generate final report (optionally using LLM for synthesis)
        final_report = self._generate_final_report(
            feature_request,
            phase_results,
            all_artifacts,
            execution_log
        )

        # Save final report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.save_artifact(final_report, f"SDLC_PIPELINE_REPORT_{timestamp}.md")

        return {
            "status": "completed",
            "feature_request": feature_request,
            "phase_results": phase_results,
            "execution_log": execution_log,
            "all_artifacts": all_artifacts,
            "final_report": final_report,
            "report_path": str(report_path),
            "orchestration_method": orchestration_method
        }

    def _should_execute_phase(
        self,
        phase: str,
        start_phase: str,
        end_phase: str,
        skip_phases: List[str]
    ) -> bool:
        """Determina si una fase debe ejecutarse."""
        if phase in skip_phases:
            return False

        start_idx = self.VALID_PHASES.index(start_phase)
        end_idx = self.VALID_PHASES.index(end_phase)
        phase_idx = self.VALID_PHASES.index(phase)

        return start_idx <= phase_idx <= end_idx

    def _execute_planning(self, feature_request: str, project_context: str) -> Dict[str, Any]:
        """Ejecuta fase de Planning."""
        return self.planner_agent.execute({
            "feature_request": feature_request,
            "project_context": project_context
        }).data

    def _execute_feasibility(
        self,
        planning_result: Dict[str, Any],
        technical_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta fase de Feasibility."""
        return self.feasibility_agent.execute({
            "issue": planning_result.get("issue", {}),
            "project_context": "",
            "technical_constraints": technical_constraints
        }).data

    def _execute_design(
        self,
        planning_result: Dict[str, Any],
        feasibility_result: Dict[str, Any],
        project_context: str
    ) -> Dict[str, Any]:
        """Ejecuta fase de Design."""
        return self.design_agent.execute({
            "issue": planning_result.get("issue", {}),
            "feasibility_result": feasibility_result,
            "project_context": project_context
        }).data

    def _execute_testing(
        self,
        planning_result: Dict[str, Any],
        design_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta fase de Testing."""
        return self.testing_agent.execute({
            "issue": planning_result.get("issue", {}),
            "design_result": design_result,
            "implementation_status": "completed"  # Assume implementation done
        }).data

    def _execute_deployment(
        self,
        planning_result: Dict[str, Any],
        design_result: Dict[str, Any],
        testing_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Ejecuta fase de Deployment."""
        return self.deployment_agent.execute({
            "issue": planning_result.get("issue", {}),
            "design_result": design_result,
            "testing_result": testing_result,
            "environment": environment
        }).data

    def _generate_final_report(
        self,
        feature_request: str,
        phase_results: Dict[str, Dict[str, Any]],
        all_artifacts: List[str],
        execution_log: List[Dict[str, str]]
    ) -> str:
        """Genera reporte final del pipeline SDLC."""
        report = f"""# SDLC Pipeline Execution Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Orchestrator**: SDLCOrchestratorAgent
**Version**: 1.0

---

## Feature Request

{feature_request}

---

## Execution Summary

"""

        # Execution log
        report += "### Phases Executed\n\n"
        report += "| Phase | Status | Decision |\n"
        report += "|-------|--------|----------|\n"
        for log_entry in execution_log:
            phase = log_entry.get("phase", "Unknown")
            status = log_entry.get("status", "Unknown")
            decision = log_entry.get("decision", "N/A")
            report += f"| {phase.capitalize()} | {status.upper()} | {decision.upper()} |\n"

        report += "\n---\n\n"

        # Phase results summary
        report += "## Phase Results\n\n"

        if "planning" in phase_results:
            report += "### Planning Phase\n\n"
            planning = phase_results["planning"]
            issue = planning.get("issue", {})
            report += f"**Issue Title**: {issue.get('issue_title', 'N/A')}\n\n"
            report += f"**Priority**: {issue.get('priority', 'N/A')}\n\n"
            report += f"**Story Points**: {issue.get('story_points', 0)}\n\n"
            report += f"**Acceptance Criteria**: {len(issue.get('acceptance_criteria', []))}\n\n"
            report += "---\n\n"

        if "feasibility" in phase_results:
            report += "### Feasibility Phase\n\n"
            feasibility = phase_results["feasibility"]
            report += f"**Decision**: {feasibility.get('decision', 'N/A').upper()}\n\n"
            report += f"**Confidence**: {feasibility.get('confidence', 0) * 100:.1f}%\n\n"
            report += f"**Risks Identified**: {len(feasibility.get('risks', []))}\n\n"
            report += "---\n\n"

        if "design" in phase_results:
            report += "### Design Phase\n\n"
            design = phase_results["design"]
            report += f"**HLD Generated**: {self._format_artifact_link(design.get('hld_path'))}\n\n"
            report += f"**LLD Generated**: {self._format_artifact_link(design.get('lld_path'))}\n\n"
            report += f"**ADRs Generated**: {len(design.get('adrs', []))}\n\n"
            report += f"**Diagrams Generated**: {len(design.get('diagrams', {}))}\n\n"
            report += "---\n\n"

        if "testing" in phase_results:
            report += "### Testing Phase\n\n"
            testing = phase_results["testing"]
            test_pyramid = testing.get("test_pyramid", {})
            report += f"**Total Test Cases**: {test_pyramid.get('total_tests', 0)}\n\n"
            report += f"**Unit Tests**: {test_pyramid.get('unit_tests', {}).get('count', 0)} ({test_pyramid.get('unit_tests', {}).get('percentage', 0):.0f}%)\n\n"
            report += f"**Integration Tests**: {test_pyramid.get('integration_tests', {}).get('count', 0)} ({test_pyramid.get('integration_tests', {}).get('percentage', 0):.0f}%)\n\n"
            report += f"**E2E Tests**: {test_pyramid.get('e2e_tests', {}).get('count', 0)} ({test_pyramid.get('e2e_tests', {}).get('percentage', 0):.0f}%)\n\n"
            coverage = testing.get("coverage_requirements", {})
            report += f"**Target Coverage**: {coverage.get('overall_target', 80)}%\n\n"
            report += "---\n\n"

        if "deployment" in phase_results:
            report += "### Deployment Phase\n\n"
            deployment = phase_results["deployment"]
            report += f"**Environment**: {deployment.get('environment', 'N/A').upper()}\n\n"
            report += f"**Deployment Plan**: {self._format_artifact_link(deployment.get('deployment_path'))}\n\n"
            report += f"**Rollback Plan**: {self._format_artifact_link(deployment.get('rollback_path'))}\n\n"
            report += "---\n\n"

        # All artifacts
        report += "## Artifacts Generated\n\n"
        report += f"Total artifacts: {len(all_artifacts)}\n\n"
        for artifact in all_artifacts:
            report += f"- {artifact}\n"

        report += "\n---\n\n"

        # Recommendations
        report += "## Recommendations\n\n"
        report += self._generate_recommendations(phase_results, execution_log)

        report += "\n---\n\n"

        # Next steps
        report += "## Next Steps\n\n"
        report += self._generate_next_steps(phase_results, execution_log)

        report += "\n---\n\n"

        # Lessons learned
        report += "## Lessons Learned\n\n"
        report += self._generate_lessons_learned(phase_results, execution_log)

        report += f"""
---

*Generated by SDLCOrchestratorAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return report

    def _generate_early_stop_report(
        self,
        feature_request: str,
        phase_results: Dict[str, Dict[str, Any]],
        all_artifacts: List[str],
        execution_log: List[Dict[str, str]],
        stopped_at_phase: str,
        reason: str
    ) -> Dict[str, Any]:
        """Genera reporte cuando pipeline se detiene early."""
        report = f"""# SDLC Pipeline Early Stop Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Stopped At**: {stopped_at_phase.upper()}
**Reason**: {reason}

---

## Feature Request

{feature_request}

---

## Execution Summary

Pipeline stopped at {stopped_at_phase} phase.

### Phases Executed

"""

        for log_entry in execution_log:
            phase = log_entry.get("phase", "Unknown")
            status = log_entry.get("status", "Unknown")
            decision = log_entry.get("decision", "N/A")
            report += f"- **{phase.capitalize()}**: {status.upper()} (Decision: {decision.upper()})\n"

        report += f"""
---

## Reason for Stop

{reason}

---

## Artifacts Generated

Total artifacts: {len(all_artifacts)}

"""

        for artifact in all_artifacts:
            report += f"- {artifact}\n"

        report += """
---

## Recommendations

1. Review feasibility report for blockers
2. Address identified issues
3. Re-run pipeline after fixes

---

*Generated by SDLCOrchestratorAgent*
"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.save_artifact(report, f"SDLC_EARLY_STOP_REPORT_{timestamp}.md")

        return {
            "status": "early_stop",
            "stopped_at_phase": stopped_at_phase,
            "reason": reason,
            "phase_results": phase_results,
            "execution_log": execution_log,
            "all_artifacts": all_artifacts,
            "final_report": report,
            "report_path": str(report_path)
        }

    def _generate_recommendations(
        self,
        phase_results: Dict[str, Dict[str, Any]],
        execution_log: List[Dict[str, str]]
    ) -> str:
        """Genera recomendaciones basadas en resultados usando LLM con fallback."""
        # Try LLM-enhanced recommendations first
        if self.use_llm and self.llm_generator:
            try:
                llm_recommendations = self._synthesize_recommendations_with_llm(phase_results)
                if llm_recommendations:
                    return "\n".join([f"- {rec}" for rec in llm_recommendations])
            except Exception as e:
                self.logger.warning(f"LLM recommendation generation failed: {e}, using heuristics")

        # Fallback to heuristic recommendations
        recommendations = []

        # Check feasibility
        if "feasibility" in phase_results:
            confidence = phase_results["feasibility"].get("confidence", 1.0)
            if confidence < 0.7:
                recommendations.append("- Feasibility confidence es baja. Revisar riesgos identificados.")

        # Check testing
        if "testing" in phase_results:
            test_pyramid = phase_results["testing"].get("test_pyramid", {})
            unit_pct = test_pyramid.get("unit_tests", {}).get("percentage", 0)
            if unit_pct < 60:
                recommendations.append(f"- Aumentar cobertura de unit tests (actual: {unit_pct:.0f}%, target: 60%)")

        if not recommendations:
            recommendations.append("- Todos los indicadores son positivos. Proceder con confianza.")

        return "\n".join(recommendations)

    def _generate_next_steps(
        self,
        phase_results: Dict[str, Dict[str, Any]],
        execution_log: List[Dict[str, str]]
    ) -> str:
        """Genera next steps basados en donde quedo el pipeline."""
        last_phase = execution_log[-1]["phase"] if execution_log else "unknown"

        if last_phase == "deployment":
            return """
1. Execute pre-deployment checklist
2. Deploy to staging environment
3. Validate deployment
4. Execute post-deployment checklist
5. Monitor for 24 hours
6. Deploy to production (if staging successful)
"""
        elif last_phase == "testing":
            return """
1. Implement tests (unit, integration, E2E)
2. Validate coverage > 80%
3. Fix any failing tests
4. Proceed to deployment phase
"""
        elif last_phase == "design":
            return """
1. Review HLD/LLD with team
2. Approve ADRs
3. Begin implementation (TDD approach)
4. Write tests as you implement
"""
        else:
            return """
1. Complete remaining SDLC phases
2. Review artifacts generated so far
3. Continue with next phase
"""

    def _generate_lessons_learned(
        self,
        phase_results: Dict[str, Dict[str, Any]],
        execution_log: List[Dict[str, str]]
    ) -> str:
        """Genera lessons learned del pipeline execution."""
        lessons = []

        # Check for risks
        if "feasibility" in phase_results:
            risks = phase_results["feasibility"].get("risks", [])
            if risks:
                lessons.append(f"- {len(risks)} riesgos identificados en feasibility. Importante mitigarlos early.")

        # Check for design complexity
        if "design" in phase_results:
            adrs_count = len(phase_results["design"].get("adrs", []))
            if adrs_count > 0:
                lessons.append(f"- {adrs_count} ADRs generados. Decisiones arquitectonicas significativas documentadas.")

        # General lesson
        lessons.append("- Pipeline SDLC automatizado ayuda a mantener consistencia y calidad.")

        return "\n".join(lessons)

    def _format_artifact_link(self, artifact_path: Optional[str]) -> str:
        """Formatea link de artifact."""
        if not artifact_path:
            return "N/A"
        return f"`{artifact_path}`"

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Guardrails especificos para Orchestrator."""
        errors = []

        # Validar que se ejecuto al menos una fase
        execution_log = output_data.get("execution_log", [])
        if not execution_log:
            errors.append("No se ejecuto ninguna fase del pipeline")

        # Validar que se genero reporte final
        if "final_report" not in output_data or not output_data["final_report"]:
            errors.append("No se genero reporte final")

        return errors
