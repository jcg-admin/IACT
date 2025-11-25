"""
Constructor de ubicaciones canónicas.
"""

from datetime import datetime
from typing import Dict


def construir_ubicacion(tipo: str, ownership: str, temporalidad: str, contexto: Dict) -> str:
    """
    Construye ubicación canónica del artefacto.

    Args:
        tipo: Tipo de artefacto
        ownership: Ownership (transversal, dominio:X, etc.)
        temporalidad: Temporalidad (temporal, permanente, historico)
        contexto: Contexto adicional

    Returns:
        Ubicación canónica (ruta relativa desde root del proyecto)
    """
    # Mapeo de tipos a ubicaciones
    UBICACIONES = {
        # Análisis y reportes (históricos)
        "analisis": lambda: f"docs/gobernanza/sesiones/analisis_{datetime.now().strftime('%Y_%m')}/",
        "reporte_limpieza": lambda: f"docs/gobernanza/sesiones/analisis_{datetime.now().strftime('%Y_%m')}/",
        "sesion": lambda: "docs/gobernanza/sesiones/",

        # Arquitectura y decisiones
        "adr": lambda: "docs/gobernanza/adr/",

        # Guías y procedimientos
        "guia": lambda: "docs/gobernanza/guias/" if ownership == "transversal"
                        else f"docs/{ownership.split(':')[1]}/guias/",
        "procedimiento": lambda: "docs/gobernanza/procedimientos/" if ownership == "transversal"
                                 else f"docs/{ownership.split(':')[1]}/procedimientos/",

        # TASKs y solicitudes
        "task": lambda: "docs/gobernanza/" if ownership == "transversal"
                        else f"docs/{ownership.split(':')[1]}/",
        "solicitud": lambda: "docs/gobernanza/solicitudes/" if ownership == "transversal"
                             else f"docs/{ownership.split(':')[1]}/solicitudes/",

        # Diseño
        "diseno_detallado": lambda: f"docs/{ownership.split(':')[1]}/diseno_detallado/",
        "diagrama": lambda: "docs/gobernanza/anexos/diagramas/" if ownership == "transversal"
                            else f"docs/{ownership.split(':')[1]}/diseno_detallado/diagramas/",

        # Testing
        "plan_testing": lambda: f"docs/{ownership.split(':')[1]}/testing/",
        "registro_qa": lambda: "docs/gobernanza/qa/registros/",

        # Agentes
        "documentacion_agente": lambda: "scripts/coding/ai/agents/",
        "configuracion_agente": lambda: "scripts/coding/ai/config/",
        "script": lambda: "/tmp/" if temporalidad == "temporal"
                          else "scripts/gobernanza_sdlc/automation/",

        # DevOps
        "pipeline_ci_cd": lambda: "docs/devops/ci_cd/",
        "script_devops": lambda: "docs/devops/git/" if "git" in contexto.get("categoria", "")
                                 else "docs/devops/automatizacion/",

        # Plantillas
        "plantilla": lambda: "docs/gobernanza/plantillas/",

        # Índices
        "indice": lambda: f"docs/{contexto.get('dominio')}/" if contexto.get('dominio')
                          else "docs/",
    }

    if tipo in UBICACIONES:
        return UBICACIONES[tipo]()

    # Default
    return "docs/"
