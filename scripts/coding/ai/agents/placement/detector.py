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
    elif ("## Status" in contenido or "## Estado" in contenido) and ("## Decision" in contenido or "## Decisión" in contenido):
        return "adr"
    elif ("## Casos de Prueba" in contenido or "## Test Cases" in contenido) and ("## Cobertura" in contenido or "## Coverage" in contenido):
        return "plan_testing"

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
    # Palabras clave por dominio
    KEYWORDS_POR_DOMINIO = {
        "backend": ["django", "rest api", "postgresql", "python", "flask", "fastapi", "sql", "database"],
        "frontend": ["react", "redux", "typescript", "javascript", "vue", "angular", "component", "jsx"],
        "infraestructura": ["docker", "kubernetes", "devops", "ci/cd", "deployment", "infrastructure"],
        "ai": ["machine learning", "llm", "model", "agent", "training", "neural"]
    }

    mencionados = []
    contenido_lower = contenido.lower()

    for dominio, keywords in KEYWORDS_POR_DOMINIO.items():
        for keyword in keywords:
            if keyword in contenido_lower:
                if dominio not in mencionados:
                    mencionados.append(dominio)
                break

    return mencionados
