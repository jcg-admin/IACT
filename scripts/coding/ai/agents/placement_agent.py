"""
Placement Agent - Agente que clasifica y ubica artefactos automáticamente.

Este agente determina la ubicación canónica de cualquier artefacto
(documentos, scripts, configuraciones) siguiendo la guía:
docs/gobernanza/guias/GUIA_UBICACIONES_ARTEFACTOS.md
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# Agregar root del proyecto al path
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

from scripts.coding.ai.shared.agent_base import Agent, AgentResult, AgentStatus
from scripts.coding.ai.agents.placement import clasificar_y_ubicar_artefacto


logger = logging.getLogger(__name__)


@dataclass
class PlacementResult:
    """
    Resultado del placement de un artefacto.
    """
    archivo_original: str
    tipo_detectado: str
    ubicacion_canonica: str
    nombre_sugerido: str
    frontmatter: Dict[str, Any]
    confianza: float
    requiere_clarificacion: bool = False
    warnings: List[str] = field(default_factory=list)


class PlacementAgent(Agent):
    """
    Agente que clasifica artefactos y determina su ubicación canónica.

    Responsabilidades:
    1. Analizar archivo (nombre y contenido)
    2. Detectar tipo de artefacto
    3. Determinar ownership (transversal vs dominio)
    4. Construir ubicación canónica
    5. Generar nombre siguiendo convenciones
    6. Generar frontmatter YAML
    7. Calcular confianza

    Guardrails:
    - Confianza mínima configurable (default: 0.6)
    - Validación de ubicaciones existentes
    - Detección de conflictos de naming
    - Prevención de placement en ubicaciones prohibidas
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el Placement Agent.

        Args:
            config: Configuración del agente
                - min_confidence: Confianza mínima (default: 0.6)
                - dry_run: No mover archivos (default: True)
                - project_root: Raíz del proyecto
        """
        super().__init__("PlacementAgent", config)
        self.min_confidence = self.config.get("min_confidence", 0.6)
        self.dry_run = self.config.get("dry_run", True)
        self.project_root = Path(self.config.get("project_root", "."))

    def run(self, input_data: Dict[str, Any]) -> AgentResult:
        """
        Ejecuta el placement de un artefacto.

        Args:
            input_data:
                - archivo: Ruta al archivo (requerido)
                - contenido: Contenido del archivo (opcional, se lee si no se provee)
                - tipo_declarado: Tipo declarado por usuario (opcional)
                - contexto: Contexto adicional (opcional)
                    - dominio: backend|frontend|infraestructura|ai
                    - temporal: bool
                    - tema: str
                    - descripcion: str
                    - id: str

        Returns:
            AgentResult con resultado del placement
        """
        try:
            # Validar input
            archivo_path = input_data.get("archivo")
            if not archivo_path:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    timestamp=datetime.now().isoformat(),
                    data={},
                    errors=["Campo 'archivo' es requerido"]
                )

            archivo = Path(archivo_path)

            # Leer contenido si no se provee
            contenido = input_data.get("contenido")
            if contenido is None:
                if not archivo.exists():
                    return AgentResult(
                        agent_name=self.name,
                        status=AgentStatus.FAILED,
                        timestamp=datetime.now().isoformat(),
                        data={},
                        errors=[f"Archivo '{archivo}' no existe"]
                    )
                contenido = archivo.read_text(encoding='utf-8')

            # Ejecutar clasificación
            resultado = clasificar_y_ubicar_artefacto(
                nombre_archivo=archivo.name,
                contenido=contenido,
                tipo_declarado=input_data.get("tipo_declarado"),
                contexto=input_data.get("contexto", {})
            )

            # Crear PlacementResult
            placement = PlacementResult(
                archivo_original=str(archivo),
                tipo_detectado=resultado["tipo"],
                ubicacion_canonica=resultado["ubicacion"],
                nombre_sugerido=resultado["nombre_sugerido"],
                frontmatter=resultado["frontmatter"],
                confianza=resultado["confianza"]
            )

            # Aplicar guardrails
            guardrail_errors = self.apply_guardrails(resultado)
            if guardrail_errors:
                return AgentResult(
                    agent_name=self.name,
                    status=AgentStatus.FAILED,
                    timestamp=datetime.now().isoformat(),
                    data=placement.__dict__,
                    errors=guardrail_errors
                )

            # Detectar warnings
            warnings = self._detect_warnings(placement, archivo)
            placement.warnings = warnings

            # Verificar si requiere clarificación
            ownership = input_data.get("contexto", {}).get("ownership", "")
            if "REQUIERE_CLARIFICACION" in ownership or resultado["confianza"] < self.min_confidence:
                placement.requiere_clarificacion = True

            # Ejecutar movimiento si no es dry_run
            if not self.dry_run and placement.confianza >= self.min_confidence:
                self._mover_artefacto(archivo, placement)

            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.SUCCESS,
                timestamp=datetime.now().isoformat(),
                data=placement.__dict__,
                warnings=warnings,
                metrics={
                    "dry_run": self.dry_run,
                    "min_confidence": self.min_confidence,
                    "guardrails_passed": True
                }
            )

        except Exception as e:
            logger.error(f"Error en PlacementAgent: {e}", exc_info=True)
            return AgentResult(
                agent_name=self.name,
                status=AgentStatus.FAILED,
                timestamp=datetime.now().isoformat(),
                data={},
                errors=[f"Error inesperado: {str(e)}"]
            )

    def apply_guardrails(self, resultado: Dict[str, Any]) -> List[str]:
        """
        Aplica guardrails al resultado del placement.

        Guardrails:
        1. Confianza mínima
        2. Ubicación no prohibida
        3. Tipo válido

        Args:
            resultado: Resultado de clasificar_y_ubicar_artefacto

        Returns:
            Lista de errores (vacía si pasa guardrails)
        """
        errors = []

        # Guardrail 1: Confianza mínima
        if resultado["confianza"] < self.min_confidence:
            errors.append(
                f"Confianza muy baja: {resultado['confianza']:.0%} < {self.min_confidence:.0%}"
            )

        # Guardrail 2: Ubicación no prohibida
        UBICACIONES_PROHIBIDAS = ["/home/", "/root/", "/etc/", "/var/"]
        ubicacion = resultado["ubicacion"]
        if any(ubicacion.startswith(prohibida) for prohibida in UBICACIONES_PROHIBIDAS):
            errors.append(f"Ubicación prohibida: {ubicacion}")

        # Guardrail 3: Tipo válido
        TIPOS_VALIDOS = [
            "task", "adr", "solicitud", "analisis", "sesion", "reporte_limpieza",
            "documentacion_agente", "configuracion_agente", "script", "guia",
            "indice", "procedimiento", "diseno_detallado", "diagrama",
            "plan_testing", "registro_qa", "pipeline_ci_cd", "script_devops",
            "plantilla", "documento_general"
        ]
        if resultado["tipo"] not in TIPOS_VALIDOS:
            errors.append(f"Tipo no válido: {resultado['tipo']}")

        return errors

    def _detect_warnings(self, placement: PlacementResult, archivo: Path) -> List[str]:
        """
        Detecta warnings (no bloqueantes) sobre el placement.

        Args:
            placement: Resultado del placement
            archivo: Archivo original

        Returns:
            Lista de warnings
        """
        warnings = []

        # Warning 1: Ubicación no existe
        ubicacion_path = self.project_root / placement.ubicacion_canonica
        if not ubicacion_path.exists():
            warnings.append(f"Directorio de destino no existe: {placement.ubicacion_canonica}")

        # Warning 2: Archivo ya existe en destino
        destino = ubicacion_path / placement.nombre_sugerido
        if destino.exists() and destino != archivo.resolve():
            warnings.append(f"Archivo ya existe en destino: {destino}")

        # Warning 3: Confianza media (0.6-0.8)
        if 0.6 <= placement.confianza < 0.8:
            warnings.append(f"Confianza media: {placement.confianza:.0%}. Revisar manualmente.")

        return warnings

    def _mover_artefacto(self, origen: Path, placement: PlacementResult):
        """
        Mueve el artefacto a su ubicación canónica.

        Args:
            origen: Archivo original
            placement: Resultado del placement

        Raises:
            Exception si falla el movimiento
        """
        destino_dir = self.project_root / placement.ubicacion_canonica
        destino_dir.mkdir(parents=True, exist_ok=True)

        destino = destino_dir / placement.nombre_sugerido

        # Usar git mv si es un repositorio git
        if (self.project_root / ".git").exists():
            import subprocess
            try:
                subprocess.run(
                    ["git", "mv", str(origen), str(destino)],
                    check=True,
                    cwd=self.project_root,
                    capture_output=True
                )
                logger.info(f"Movido con git: {origen} → {destino}")
            except subprocess.CalledProcessError:
                # Fallback a movimiento normal
                origen.rename(destino)
                logger.info(f"Movido: {origen} → {destino}")
        else:
            origen.rename(destino)
            logger.info(f"Movido: {origen} → {destino}")


def main():
    """
    CLI para ejecutar PlacementAgent.

    Ejemplos:
        python placement_agent.py analisis_docs.md --tipo analisis --tema DOCS
        python placement_agent.py task.md --dominio backend
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Placement Agent - Clasifica y ubica artefactos")
    parser.add_argument("archivo", help="Archivo a clasificar")
    parser.add_argument("--tipo", help="Tipo declarado")
    parser.add_argument("--dominio", help="Dominio (backend, frontend, infraestructura, ai)")
    parser.add_argument("--temporal", action="store_true", help="Marcar como temporal")
    parser.add_argument("--tema", help="Tema (para análisis/guía/sesión)")
    parser.add_argument("--descripcion", help="Descripción (para TASK/ADR/REQ)")
    parser.add_argument("--id", help="ID (para TASK/ADR/REQ)")
    parser.add_argument("--dry-run", action="store_true", default=True, help="No mover archivos")
    parser.add_argument("--execute", action="store_true", help="Ejecutar movimiento real")
    parser.add_argument("--min-confidence", type=float, default=0.6, help="Confianza mínima")
    parser.add_argument("--json", action="store_true", help="Output en JSON")

    args = parser.parse_args()

    # Configurar agente
    config = {
        "dry_run": not args.execute,
        "min_confidence": args.min_confidence,
        "project_root": "/home/user/IACT---project"
    }

    agent = PlacementAgent(config)

    # Preparar input
    contexto = {}
    if args.dominio:
        contexto["dominio"] = args.dominio
    if args.temporal:
        contexto["temporal"] = True
    if args.tema:
        contexto["tema"] = args.tema
    if args.descripcion:
        contexto["descripcion"] = args.descripcion
    if args.id:
        contexto["id"] = args.id

    input_data = {
        "archivo": args.archivo,
        "tipo_declarado": args.tipo,
        "contexto": contexto
    }

    # Ejecutar
    resultado = agent.run(input_data)

    # Output
    if args.json:
        output = {
            "agent_name": resultado.agent_name,
            "status": resultado.status.value,
            "timestamp": resultado.timestamp,
            "data": resultado.data,
            "errors": resultado.errors,
            "warnings": resultado.warnings,
            "metrics": resultado.metrics
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if resultado.status == AgentStatus.SUCCESS:
            data = resultado.data
            print(f"Tipo detectado: {data['tipo_detectado']}")
            print(f"Ubicación canónica: {data['ubicacion_canonica']}")
            print(f"Nombre sugerido: {data['nombre_sugerido']}")
            print(f"Confianza: {data['confianza']:.0%}")

            if data.get('warnings'):
                print(f"\nAdvertencias:")
                for warn in data['warnings']:
                    print(f"  - {warn}")

            if data.get('requiere_clarificacion'):
                print(f"\nREQUIERE CLARIFICACIÓN - Por favor especificar dominio/contexto")

            print(f"\nFrontmatter:")
            print("---")
            for key, value in data['frontmatter'].items():
                print(f"{key}: {value}")
            print("---")
        else:
            print(f"ERROR: {', '.join(resultado.errors)}")


if __name__ == "__main__":
    main()
