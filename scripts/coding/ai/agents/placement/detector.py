"""
Detectores de tipo y dominio de artefactos.

IMPORTANTE: Este módulo usa auto-discovery dinámico.
No asume nombres específicos de dominios ni keywords hardcodeadas.
Es portable a cualquier proyecto.
"""

from typing import Dict, List, Optional

from .config_loader import PlacementConfig
from .content_analyzer import DomainContentAnalyzer
from .structure_discovery import ProjectStructureDiscovery


# Singleton para cache
_keyword_map_cache: Optional[Dict[str, List[str]]] = None
_config_cache: Optional[PlacementConfig] = None


def _get_config() -> PlacementConfig:
    """Obtiene configuración (cached)."""
    global _config_cache
    if _config_cache is None:
        _config_cache = PlacementConfig()
    return _config_cache


def _get_keyword_map() -> Dict[str, List[str]]:
    """
    Obtiene mapa de keywords por dominio (cached).

    Returns:
        Diccionario {dominio: [keywords]}
    """
    global _keyword_map_cache

    if _keyword_map_cache is not None:
        return _keyword_map_cache

    config = _get_config()

    # Usar keywords personalizadas si existen
    if not config.should_auto_discover_domains():
        custom = config.get_custom_keywords()
        if custom:
            _keyword_map_cache = custom
            return _keyword_map_cache

    # Auto-discovery de keywords
    analyzer = DomainContentAnalyzer()
    _keyword_map_cache = analyzer.build_domain_keyword_map(top_n=15)

    return _keyword_map_cache


def detectar_tipo(nombre: str, contenido: str) -> str:
    """
    Detecta tipo de artefacto basado en nombre y contenido.

    Args:
        nombre: Nombre del archivo
        contenido: Contenido del archivo

    Returns:
        Tipo detectado (task, adr, analisis, etc.)

    Example:
        >>> detectar_tipo("TASK-001-feature.md", "# Feature")
        'task'
    """
    # Patrones de nombres (universales)
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

    # Análisis de contenido (universales)
    if "## Sub-Agentes" in contenido and "## Arquitectura" in contenido:
        return "documentacion_agente"
    elif "## Descripción" in contenido and "## Contexto" in contenido:
        return "analisis"
    elif ("## Status" in contenido or "## Estado" in contenido) and (
        "## Decision" in contenido or "## Decisión" in contenido
    ):
        return "adr"
    elif ("## Casos de Prueba" in contenido or "## Test Cases" in contenido) and (
        "## Cobertura" in contenido or "## Coverage" in contenido
    ):
        return "plan_testing"

    # Default
    return "documento_general"


def detectar_dominios_en_contenido(contenido: str) -> List[str]:
    """
    Detecta qué dominios se mencionan en el contenido.

    IMPORTANTE: Usa auto-discovery dinámico de keywords.
    No hardcodea nombres de dominios ni keywords.

    Args:
        contenido: Contenido del archivo

    Returns:
        Lista de dominios mencionados

    Example:
        >>> contenido = "Django REST API with PostgreSQL"
        >>> detectar_dominios_en_contenido(contenido)
        ['backend']  # Asumiendo que backend tiene keywords django, postgresql
    """
    # Obtener keyword map (auto-discovery o config)
    keyword_map = _get_keyword_map()

    # Usar analyzer para detectar
    analyzer = DomainContentAnalyzer()
    detected = analyzer.detect_domains_in_content(contenido, keyword_map)

    return detected


def get_available_domains() -> List[str]:
    """
    Obtiene lista de dominios disponibles en el proyecto.

    Returns:
        Lista de nombres de dominios

    Example:
        >>> get_available_domains()
        ['ai', 'backend', 'frontend', 'infraestructura']
    """
    discovery = ProjectStructureDiscovery()
    return discovery.discover_domains()


def get_domain_keywords(domain: str) -> List[str]:
    """
    Obtiene keywords asociadas a un dominio.

    Args:
        domain: Nombre del dominio

    Returns:
        Lista de keywords para ese dominio

    Example:
        >>> get_domain_keywords('backend')
        ['django', 'rest api', 'postgresql', ...]
    """
    keyword_map = _get_keyword_map()
    return keyword_map.get(domain, [])
