"""
Generador de frontmatter YAML.
"""

from datetime import datetime
from typing import Dict


def generar_frontmatter(tipo: str, contexto: Dict) -> Dict:
    """
    Genera frontmatter YAML apropiado para el tipo.

    Args:
        tipo: Tipo de artefacto
        contexto: Contexto adicional

    Returns:
        Diccionario con frontmatter sugerido
    """
    BASE = {
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "tipo": tipo,
    }

    FRONTMATTER_POR_TIPO = {
        "task": {
            "id": contexto.get("id", "TASK-001"),
            "categoria": contexto.get("categoria", "desarrollo"),
            "dominio": contexto.get("dominio", "transversal"),
            "prioridad": contexto.get("prioridad", "media"),
            "estado": "pendiente",
            "asignado": contexto.get("asignado", ""),
            "relacionado": contexto.get("relacionado", []),
        },
        "adr": {
            "id": contexto.get("id", "ADR-001"),
            "categoria": "arquitectura",
            "estado": "propuesto",
            "supersede": [],
            "superseded_by": [],
        },
        "analisis": {
            "categoria": contexto.get("categoria", "documentacion"),
            "autor": contexto.get("autor", "agente-cleanup"),
            "relacionado": contexto.get("relacionado", []),
        },
        "documentacion_agente": {
            "id": contexto.get("id", "AGENT-NEW"),
            "categoria": contexto.get("categoria", "documentacion"),
            "version": "1.0.0",
            "autor": "equipo-arquitectura",
            "status": "active",
        },
        "guia": {
            "id": f"GUIA-{contexto.get('tema', 'GENERAL').upper()}",
            "categoria": "gobernanza",
            "version": "1.0.0",
            "autor": "equipo-arquitectura",
        },
    }

    specific = FRONTMATTER_POR_TIPO.get(tipo, {})
    return {**BASE, **specific}
