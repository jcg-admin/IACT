"""
Decisiones contextuales para placement.
"""

from typing import Dict, Optional


def decidir_por_contexto(tipo: str, contexto_detectado: Dict) -> str:
    """
    Decide ubicación basada en contexto específico.

    Contexto incluye:
    - dominio: backend|frontend|infraestructura|ai
    - afecta_multiples_dominios: bool
    - temporal: bool
    - reutilizable: bool
    - categoria: git|ci_cd|testing|etc

    Args:
        tipo: Tipo de artefacto
        contexto_detectado: Contexto detectado

    Returns:
        Ubicación canónica o "ANALIZAR_MANUAL"
    """
    reglas_contextuales = {
        # (tipo, afecta_múltiples, dominio) → ubicación
        ("task", True, None): "docs/gobernanza/",
        ("task", False, "backend"): "docs/backend/",
        ("task", False, "frontend"): "docs/frontend/",

        ("solicitud", True, None): "docs/gobernanza/solicitudes/",
        ("solicitud", False, "backend"): "docs/backend/solicitudes/",

        ("guia", True, None): "docs/gobernanza/guias/",
        ("guia", False, "backend"): "docs/backend/guias/",

        ("script", None, "git"): "docs/devops/git/",
        ("script", None, "ci_cd"): "docs/devops/automatizacion/",
        ("script", None, "agente"): "scripts/gobernanza_sdlc/automation/",

        ("diagrama", True, None): "docs/gobernanza/anexos/diagramas/",
        ("diagrama", False, "backend"): "docs/backend/diseno_detallado/diagramas/",

        # Siempre en ubicación fija
        ("adr", None, None): "docs/gobernanza/adr/",
        ("plantilla", None, None): "docs/gobernanza/plantillas/",
        ("documentacion_agente", None, None): "scripts/coding/ai/agents/",
    }

    # Construir key
    key = (
        tipo,
        contexto_detectado.get("afecta_multiples_dominios"),
        contexto_detectado.get("dominio") or contexto_detectado.get("categoria")
    )

    return reglas_contextuales.get(key, "ANALIZAR_MANUAL")
