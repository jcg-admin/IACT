"""
Determinador de ownership de artefactos.
"""

from typing import Dict
from .detector import detectar_dominios_en_contenido


def determinar_ownership(tipo: str, contexto: Dict, contenido: str) -> str:
    """
    Determina si es transversal, dominio-específico, o agente.

    Args:
        tipo: Tipo de artefacto
        contexto: Contexto adicional
        contenido: Contenido del archivo

    Returns:
        Ownership (transversal, dominio:X, agente, devops)
    """
    TIPOS_SIEMPRE_TRANSVERSALES = ["adr", "guia_transversal", "plantilla"]
    TIPOS_SIEMPRE_AGENTE = ["documentacion_agente", "configuracion_agente", "script"]
    TIPOS_SIEMPRE_DEVOPS = ["pipeline_ci_cd", "script_devops"]

    # Verificar tipos fijos
    if tipo in TIPOS_SIEMPRE_TRANSVERSALES:
        return "transversal"
    elif tipo in TIPOS_SIEMPRE_AGENTE:
        return "agente"
    elif tipo in TIPOS_SIEMPRE_DEVOPS:
        return "devops"

    # Verificar contexto
    if contexto.get("dominio"):
        return f"dominio:{contexto['dominio']}"

    # Análisis de contenido
    dominios_mencionados = detectar_dominios_en_contenido(contenido)

    if len(dominios_mencionados) == 1:
        return f"dominio:{dominios_mencionados[0]}"
    elif len(dominios_mencionados) > 1:
        return "transversal"

    # Default: preguntar
    return "REQUIERE_CLARIFICACION"
