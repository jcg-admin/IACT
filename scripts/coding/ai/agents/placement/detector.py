"""
Detectores de tipo y dominio de artefactos.
"""

from typing import List


def detectar_tipo(nombre: str, contenido: str) -> str:
    """
    Detecta tipo de artefacto basado en nombre y contenido.

    Args:
        nombre: Nombre del archivo
        contenido: Contenido del archivo

    Returns:
        Tipo detectado (task, adr, analisis, etc.)
    """
    # Patrones de nombres
    if nombre.startswith("TASK-"):
        return "task"
    elif nombre.startswith("ADR-"):
        return "adr"
    elif nombre.startswith("REQ-"):
        return "solicitud"
    elif nombre.startswith("ANALISIS_"):
        return "analisis"
    elif nombre.startswith("SESSION_"):
        return "sesion"
    elif nombre.startswith("CLEANUP_REPORT_"):
        return "reporte_limpieza"
    elif nombre.startswith("README_") and "Agent" in contenido:
        return "documentacion_agente"
    elif nombre.endswith("_config.json"):
        return "configuracion_agente"
    elif nombre.endswith(".sh") or nombre.endswith(".py"):
        return "script"
    elif "GUIA" in nombre.upper():
        return "guia"
    elif nombre == "INDEX.md":
        return "indice"

    # Análisis de contenido
    if "## Sub-Agentes" in contenido and "## Arquitectura" in contenido:
        return "documentacion_agente"
    elif "## Descripción" in contenido and "## Contexto" in contenido:
        return "analisis"
    elif "## Status" in contenido and "## Decisión" in contenido:
        return "adr"

    # Default
    return "documento_general"


def detectar_dominios_en_contenido(contenido: str) -> List[str]:
    """
    Detecta qué dominios se mencionan en el contenido.

    Args:
        contenido: Contenido del archivo

    Returns:
        Lista de dominios mencionados
    """
    DOMINIOS = ["backend", "frontend", "infraestructura", "ai"]
    mencionados = []

    contenido_lower = contenido.lower()
    for dominio in DOMINIOS:
        if dominio in contenido_lower:
            mencionados.append(dominio)

    return mencionados
