"""
Base classes para agentes SDLC (Software Development Life Cycle).

Este módulo define las clases base para agentes que asisten en cada
fase del SDLC del proyecto IACT.

Documentación: scripts/ai/agents/ARCHITECTURE_SDLC_AGENTS.md
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Agent, AgentResult, AgentStatus, Pipeline


@dataclass
class SDLCPhaseResult:
    """Resultado de una fase SDLC."""
    phase: str  # planning, feasibility, design, testing, deployment, maintenance
    decision: str  # go, no-go, review, blocked
    confidence: float  # 0.0 - 1.0
    artifacts: List[str] = field(default_factory=list)  # Rutas a archivos generados
    recommendations: List[str] = field(default_factory=list)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


class SDLCAgent(Agent):
    """
    Clase base para todos los agentes SDLC.

    Cada agente representa una fase del SDLC y produce outputs
    específicos de esa fase.
    """

    def __init__(self, name: str, phase: str, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el agente SDLC.

        Args:
            name: Nombre del agente
            phase: Fase SDLC (planning, feasibility, design, testing, deployment, maintenance)
            config: Configuración específica
        """
        super().__init__(name, config)
        self.phase = phase
        self.project_root = Path(self.config.get("project_root", "."))
        self.output_dir = Path(self.config.get("output_dir", "docs/sdlc_outputs"))

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Aplica guardrails a los resultados SDLC.

        Los agentes SDLC generan documentación de planificación/diseño, no código,
        por lo que los guardrails de constitution (diseñados para código) no aplican.

        En su lugar, usamos guardrails personalizados específicos de cada fase SDLC.

        Args:
            output_data: Datos de salida a validar

        Returns:
            Lista de errores de guardrails (vacía si pasa)
        """
        # Solo aplicar guardrails personalizados, no constitution
        return self._custom_guardrails(output_data)

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la lógica del agente SDLC.

        Args:
            input_data: Datos de entrada (feature_request, issue, etc.)

        Returns:
            Diccionario con los resultados de la fase
        """
        pass

    def create_phase_result(
        self,
        decision: str,
        confidence: float,
        **kwargs
    ) -> SDLCPhaseResult:
        """
        Crea un resultado de fase SDLC.

        Args:
            decision: Decisión (go, no-go, review, blocked)
            confidence: Nivel de confianza (0.0 - 1.0)
            **kwargs: Campos adicionales (artifacts, recommendations, risks, next_steps)

        Returns:
            SDLCPhaseResult
        """
        return SDLCPhaseResult(
            phase=self.phase,
            decision=decision,
            confidence=confidence,
            artifacts=kwargs.get("artifacts", []),
            recommendations=kwargs.get("recommendations", []),
            risks=kwargs.get("risks", []),
            next_steps=kwargs.get("next_steps", [])
        )

    def save_artifact(self, content: str, filename: str) -> Path:
        """
        Guarda un artefacto generado por el agente.

        Args:
            content: Contenido del artefacto
            filename: Nombre del archivo

        Returns:
            Path al archivo guardado
        """
        artifact_dir = self.output_dir / self.phase
        artifact_dir.mkdir(parents=True, exist_ok=True)

        filepath = artifact_dir / filename
        filepath.write_text(content, encoding="utf-8")

        self.logger.info(f"Artefacto guardado: {filepath}")
        return filepath


class SDLCPipeline(Pipeline):
    """
    Pipeline especializado para ejecutar agentes SDLC en secuencia.

    Implementa lógica de Go/No-Go decisions y escalación humana.
    """

    def __init__(self, name: str, agents: List[SDLCAgent], auto_proceed: bool = False):
        """
        Inicializa el pipeline SDLC.

        Args:
            name: Nombre del pipeline
            agents: Lista de agentes SDLC en orden de ejecución
            auto_proceed: Si True, no pide confirmación humana en decisiones críticas
        """
        super().__init__(name, agents)
        self.auto_proceed = auto_proceed

    def execute(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el pipeline SDLC completo con decisiones Go/No-Go.

        Args:
            initial_data: Datos iniciales (feature_request, etc.)

        Returns:
            Diccionario con resultados del pipeline completo
        """
        self.logger.info(f"Iniciando pipeline SDLC: {self.name}")
        self.results = []

        current_data = initial_data.copy()

        for agent in self.agents:
            self.logger.info(f"Ejecutando fase: {agent.phase} ({agent.name})")
            result = agent.execute(current_data)
            self.results.append(result)

            # Check si falló
            if result.is_failed():
                self.logger.error(f"Fase {agent.phase} falló: {result.errors}")
                return {
                    "status": "failed",
                    "failed_phase": agent.phase,
                    "failed_agent": agent.name,
                    "errors": result.errors,
                    "completed_phases": [r.agent_name for r in self.results[:-1]]
                }

            # Check si está bloqueado
            if result.is_blocked():
                self.logger.warning(f"Fase {agent.phase} bloqueada: {result.errors}")
                return {
                    "status": "blocked",
                    "blocked_phase": agent.phase,
                    "blocked_agent": agent.name,
                    "errors": result.errors,
                    "completed_phases": [r.agent_name for r in self.results[:-1]]
                }

            # Check Go/No-Go decision
            phase_result = result.data.get("phase_result")
            if phase_result and isinstance(phase_result, SDLCPhaseResult):
                if phase_result.decision == "no-go":
                    self.logger.warning(f"Decisión NO-GO en fase {agent.phase}")
                    return {
                        "status": "stopped",
                        "stopped_phase": agent.phase,
                        "reason": phase_result.recommendations,
                        "risks": phase_result.risks,
                        "completed_phases": [r.agent_name for r in self.results[:-1]]
                    }

                # Escalación humana para decisiones críticas
                if phase_result.decision == "review" and not self.auto_proceed:
                    self.logger.info(f"ESCALACIÓN HUMANA requerida en fase {agent.phase}")
                    return {
                        "status": "requires_approval",
                        "phase": agent.phase,
                        "recommendations": phase_result.recommendations,
                        "artifacts": phase_result.artifacts,
                        "next_steps": phase_result.next_steps,
                        "completed_phases": [r.agent_name for r in self.results[:-1]]
                    }

            # Propagar datos al siguiente agente
            current_data.update(result.data)

        self.logger.info(f"Pipeline SDLC {self.name} completado exitosamente")

        return {
            "status": "success",
            "data": current_data,
            "results": [r.to_dict() for r in self.results],
            "phases_completed": [agent.phase for agent in self.agents]
        }
