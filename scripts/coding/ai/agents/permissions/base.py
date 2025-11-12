"""
Base Permission Agent

Clase base que provee funcionalidad común para todos los agentes de
análisis de permisos.

Funcionalidad provista:
- Carga de prompts desde markdown
- Logging estructurado
- Métricas de ejecución
- Formato de output consistente
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class BasePermissionAgent:
    """
    Clase base para agentes de análisis de permisos.

    Atributos:
        name: Nombre del agente (ej: "route-lint")
        prompt_path: Ruta al archivo de prompt markdown
        verbose: Si True, muestra output detallado
    """

    def __init__(self, name: str, prompt_path: str, verbose: bool = False):
        """
        Inicializa el agente base.

        Args:
            name: Nombre identificador del agente
            prompt_path: Ruta relativa al prompt markdown
            verbose: Activar logging verbose
        """
        self.name = name
        self.prompt_path = Path(prompt_path)
        self.verbose = verbose

        # Setup logging
        self.logger = logging.getLogger(f"promptops.{name}")
        level = logging.DEBUG if verbose else logging.INFO
        self.logger.setLevel(level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Métricas
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def load_prompt(self) -> str:
        """
        Carga el prompt desde archivo markdown.

        Returns:
            Contenido del prompt como string

        Raises:
            FileNotFoundError: Si el prompt no existe
        """
        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt not found: {self.prompt_path}\n"
                f"Expected at: {self.prompt_path.absolute()}"
            )

        with open(self.prompt_path) as f:
            content = f.read()

        self.logger.debug(f"Loaded prompt from {self.prompt_path}")
        return content

    def start_execution(self):
        """Marca el inicio de la ejecución."""
        self.start_time = time.perf_counter()
        self.logger.info(f"Starting {self.name} agent")

    def end_execution(self):
        """Marca el fin de la ejecución."""
        self.end_time = time.perf_counter()
        duration = self.get_duration()
        self.logger.info(f"Completed {self.name} agent in {duration:.2f}s")

    def get_duration(self) -> float:
        """
        Calcula duración de la ejecución.

        Returns:
            Duración en segundos
        """
        if self.start_time is None:
            return 0.0

        end = self.end_time or time.perf_counter()
        return end - self.start_time

    def log_metric(self, metric_name: str, value: Any):
        """
        Registra una métrica.

        Args:
            metric_name: Nombre de la métrica
            value: Valor de la métrica
        """
        self.logger.info(
            f"Metric: {metric_name} = {value}",
            extra={
                "agent": self.name,
                "metric": metric_name,
                "value": value
            }
        )

    def log_violation(
        self,
        file: str,
        line: int,
        severity: str,
        message: str,
        **kwargs
    ):
        """
        Registra una violación detectada.

        Args:
            file: Archivo donde se detectó la violación
            line: Número de línea
            severity: Nivel de severidad (critical/high/medium/low)
            message: Descripción de la violación
            **kwargs: Metadatos adicionales
        """
        self.logger.warning(
            f"Violation: {file}:{line} - {message}",
            extra={
                "agent": self.name,
                "file": file,
                "line": line,
                "severity": severity,
                # message ya está en el log message, no se incluye en extra
                # para evitar KeyError (message es reservado por logging)
                **kwargs
            }
        )

    def format_summary(
        self,
        status: str,
        total_analyzed: int,
        violations_found: int,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Formatea resumen de ejecución.

        Args:
            status: "pass" | "fail"
            total_analyzed: Total de elementos analizados
            violations_found: Total de violaciones encontradas
            **kwargs: Metadatos adicionales

        Returns:
            Diccionario con resumen estructurado
        """
        duration = self.get_duration()

        summary = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "duration_seconds": round(duration, 2),
            "analyzed": total_analyzed,
            "violations": violations_found,
            **kwargs
        }

        return summary

    def get_project_root(self) -> Path:
        """
        Obtiene la ruta raíz del proyecto.

        Busca marcadores de proyecto (.git, pyproject.toml, api/callcentersite)
        para encontrar el root de forma robusta.

        Returns:
            Path al directorio raíz del proyecto
        """
        current = Path(__file__).resolve()

        # Subir hasta encontrar marcador de proyecto
        for parent in [current] + list(current.parents):
            # Buscar marcadores de root
            if (parent / ".git").exists():
                return parent
            if (parent / "pyproject.toml").exists():
                return parent
            if (parent / "setup.py").exists():
                return parent
            # Marcador específico IACT
            if (parent / "api" / "callcentersite").exists():
                return parent

        # Fallback: asumir estructura estándar
        # base.py -> permissions/ -> agents/ -> ai/ -> scripts/ -> root/
        return current.parent.parent.parent.parent.parent

    def validate_prerequisites(self) -> bool:
        """
        Valida que los prerequisitos estén cumplidos.

        Returns:
            True si todos los prerequisitos están OK

        Raises:
            RuntimeError: Si falta algún prerequisito crítico
        """
        project_root = self.get_project_root()

        # Validar que exista la estructura del proyecto
        api_path = project_root / "api" / "callcentersite"
        if not api_path.exists():
            raise RuntimeError(
                f"API directory not found: {api_path}\n"
                f"Are you running from project root?"
            )

        # Validar que exista el app de permisos
        permissions_app = api_path / "callcentersite" / "apps" / "permissions"
        if not permissions_app.exists():
            raise RuntimeError(
                f"Permissions app not found: {permissions_app}"
            )

        self.logger.debug("Prerequisites validated successfully")
        return True

    def format_output_table(
        self,
        headers: list,
        rows: list
    ) -> str:
        """
        Formatea datos como tabla ASCII.

        Args:
            headers: Lista de headers
            rows: Lista de listas con datos

        Returns:
            String con tabla formateada
        """
        if not rows:
            return "No data to display"

        # Calcular anchos de columnas
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        # Generar separador
        separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"

        # Generar tabla
        lines = [separator]

        # Headers
        header_line = "|"
        for h, w in zip(headers, col_widths):
            header_line += f" {h:<{w}} |"
        lines.append(header_line)
        lines.append(separator)

        # Rows
        for row in rows:
            row_line = "|"
            for cell, w in zip(row, col_widths):
                row_line += f" {str(cell):<{w}} |"
            lines.append(row_line)

        lines.append(separator)

        return "\n".join(lines)

    def run(self) -> int:
        """
        Ejecuta el agente.

        Este método debe ser implementado por las subclases.

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        raise NotImplementedError(
            f"Agent {self.name} must implement run() method"
        )
