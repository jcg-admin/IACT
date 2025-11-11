"""
Módulo base para agentes especializados de generación de tests.

Este módulo define la clase base Agent que implementa el patrón
Single Responsibility Principle para agentes especializados.

Todos los agentes cargan y adhieren a los principios definidos en la
constitution (docs/gobernanza/agentes/constitution.md).
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from .constitution_loader import load_constitution, create_validator, Constitution, ConstitutionValidator
except ImportError:
    # Fallback si constitution_loader no está disponible
    Constitution = None
    ConstitutionValidator = None
    load_constitution = None
    create_validator = None


class AgentStatus(Enum):
    """Estados posibles de un agente."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class AgentResult:
    """Resultado de la ejecución de un agente."""
    agent_name: str
    status: AgentStatus
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics
        }

    def is_success(self) -> bool:
        """Verifica si la ejecución fue exitosa."""
        return self.status == AgentStatus.SUCCESS

    def is_failed(self) -> bool:
        """Verifica si la ejecución falló."""
        return self.status == AgentStatus.FAILED

    def is_blocked(self) -> bool:
        """Verifica si la ejecución está bloqueada."""
        return self.status == AgentStatus.BLOCKED


class Agent(ABC):
    """
    Clase base abstracta para todos los agentes especializados.

    Cada agente debe implementar una única responsabilidad siguiendo
    el Single Responsibility Principle.
    """

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el agente.

        Args:
            name: Nombre identificador del agente
            config: Configuración específica del agente
        """
        self.name = name
        self.config = config or {}
        self.logger = self._setup_logger()
        self.status = AgentStatus.IDLE
        self._result: Optional[AgentResult] = None

        # Cargar constitution y validator
        self.constitution: Optional[Constitution] = None
        self.constitution_validator: Optional[ConstitutionValidator] = None

        if load_constitution is not None and create_validator is not None:
            try:
                self.constitution = load_constitution()
                self.constitution_validator = create_validator(self.constitution)
                self.logger.info(f"Constitution cargada: {len(self.constitution.principles)} principios")
            except Exception as e:
                self.logger.warning(f"No se pudo cargar constitution: {e}")
        else:
            self.logger.warning("Constitution loader no disponible")

    def _setup_logger(self) -> logging.Logger:
        """Configura el logger del agente."""
        logger = logging.getLogger(f"agent.{self.name}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] {self.name} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Ejecuta el agente con los datos de entrada.

        Args:
            input_data: Datos de entrada para el agente

        Returns:
            AgentResult con el resultado de la ejecución
        """
        self.status = AgentStatus.RUNNING
        self.logger.info(f"Iniciando ejecución de {self.name}")

        result = AgentResult(
            agent_name=self.name,
            status=AgentStatus.RUNNING,
            timestamp=datetime.now().isoformat()
        )

        try:
            # Validar entrada
            validation_errors = self.validate_input(input_data)
            if validation_errors:
                result.status = AgentStatus.BLOCKED
                result.errors = validation_errors
                self.logger.error(f"Validación falló: {validation_errors}")
                return result

            # Ejecutar lógica del agente
            output_data = self.run(input_data)

            # Aplicar guardrails
            guardrail_errors = self.apply_guardrails(output_data)
            if guardrail_errors:
                result.status = AgentStatus.BLOCKED
                result.errors = guardrail_errors
                self.logger.error(f"Guardrails fallaron: {guardrail_errors}")
                return result

            # Éxito
            result.status = AgentStatus.SUCCESS
            result.data = output_data
            self.logger.info(f"Ejecución exitosa de {self.name}")

        except Exception as e:
            result.status = AgentStatus.FAILED
            result.errors = [str(e)]
            self.logger.exception(f"Error en ejecución: {e}")

        finally:
            self.status = result.status
            self._result = result

        return result

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lógica principal del agente.

        Args:
            input_data: Datos de entrada validados

        Returns:
            Diccionario con los resultados
        """
        pass

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Valida los datos de entrada.

        Args:
            input_data: Datos a validar

        Returns:
            Lista de errores de validación (vacía si es válido)
        """
        # Implementación por defecto: no valida nada
        return []

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Aplica guardrails a los resultados.

        Valida el output contra los principios de la constitution:
        - Calidad sobre velocidad (sin placeholders)
        - Trazabilidad completa (referencias a REQ/SPEC/ADR)
        - Sin emojis (prohibidos por GUIA_ESTILO.md)
        - Testing y validación (código con tests)

        Args:
            output_data: Datos de salida a validar

        Returns:
            Lista de errores de guardrails (vacía si pasa)
        """
        errors = []

        # Aplicar validaciones de constitution si está disponible
        if self.constitution_validator is not None:
            violations = self.constitution_validator.validate_all(output_data)

            for category, category_violations in violations.items():
                if category_violations:
                    errors.extend([f"[{category}] {v}" for v in category_violations])

        # Permitir que subclases agreguen validaciones adicionales
        custom_errors = self._custom_guardrails(output_data)
        errors.extend(custom_errors)

        return errors

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Guardrails personalizados específicos del agente.

        Subclases pueden override este método para agregar validaciones
        específicas adicionales.

        Args:
            output_data: Datos de salida a validar

        Returns:
            Lista de errores personalizados (vacía si pasa)
        """
        return []

    def get_result(self) -> Optional[AgentResult]:
        """Obtiene el último resultado del agente."""
        return self._result

    def get_config(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor de configuración."""
        return self.config.get(key, default)

    def check_authority(self, action: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Verifica si el agente tiene autoridad para realizar una acción.

        Según el Principio 4 de la constitution (Límites de Autoridad),
        ciertas acciones requieren escalación humana.

        Args:
            action: Acción a realizar
            context: Contexto adicional de la acción

        Returns:
            True si tiene autoridad, False si requiere escalación

        Example:
            >>> agent = Agent("test")
            >>> if not agent.check_authority("modificar_arquitectura"):
            ...     agent.logger.error("ESCALACIÓN REQUERIDA: Cambio arquitectónico")
            ...     return AgentResult(status=AgentStatus.BLOCKED)
        """
        if self.constitution_validator is None:
            self.logger.warning("Constitution validator no disponible, asumiendo autoridad")
            return True

        context = context or {}
        has_authority = self.constitution_validator.validate_authority_limits(action, context)

        if not has_authority:
            self.logger.warning(f"ESCALACIÓN REQUERIDA: Acción '{action}' fuera de autoridad")

        return has_authority

    def save_result(self, output_path: Path) -> None:
        """
        Guarda el resultado en un archivo JSON.

        Args:
            output_path: Ruta donde guardar el resultado
        """
        if self._result is None:
            raise ValueError("No hay resultado para guardar")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self._result.to_dict(), f, indent=2)

        self.logger.info(f"Resultado guardado en {output_path}")


class Pipeline:
    """
    Pipeline para ejecutar múltiples agentes en secuencia.

    Coordina la ejecución de agentes y gestiona el flujo de datos
    entre ellos.
    """

    def __init__(self, name: str, agents: List[Agent]):
        """
        Inicializa el pipeline.

        Args:
            name: Nombre del pipeline
            agents: Lista de agentes a ejecutar en orden
        """
        self.name = name
        self.agents = agents
        self.logger = logging.getLogger(f"pipeline.{name}")
        self.results: List[AgentResult] = []

    def execute(self, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo.

        Args:
            initial_data: Datos iniciales del pipeline

        Returns:
            Diccionario con los resultados finales
        """
        self.logger.info(f"Iniciando pipeline {self.name}")
        self.results = []

        current_data = initial_data.copy()

        for agent in self.agents:
            self.logger.info(f"Ejecutando agente: {agent.name}")
            result = agent.execute(current_data)
            self.results.append(result)

            if result.is_failed():
                self.logger.error(f"Agente {agent.name} falló: {result.errors}")
                return {
                    "status": "failed",
                    "failed_agent": agent.name,
                    "errors": result.errors,
                    "completed_agents": [r.agent_name for r in self.results[:-1]]
                }

            if result.is_blocked():
                self.logger.warning(f"Agente {agent.name} bloqueado: {result.errors}")
                return {
                    "status": "blocked",
                    "blocked_agent": agent.name,
                    "errors": result.errors,
                    "completed_agents": [r.agent_name for r in self.results[:-1]]
                }

            # Propagar datos al siguiente agente
            current_data.update(result.data)

        self.logger.info(f"Pipeline {self.name} completado exitosamente")

        return {
            "status": "success",
            "data": current_data,
            "results": [r.to_dict() for r in self.results]
        }

    def save_results(self, output_dir: Path) -> None:
        """
        Guarda todos los resultados del pipeline.

        Args:
            output_dir: Directorio donde guardar los resultados
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, result in enumerate(self.results):
            filename = f"{i+1:02d}_{result.agent_name}.json"
            filepath = output_dir / filename

            with open(filepath, 'w') as f:
                json.dump(result.to_dict(), f, indent=2)

        self.logger.info(f"Resultados guardados en {output_dir}")
