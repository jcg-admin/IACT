"""
Determinador de temporalidad de artefactos.
"""

from typing import Dict


def determinar_temporalidad(tipo: str, contexto: Dict) -> str:
    """
    Determina si es temporal, permanente, o histórico.

    Args:
        tipo: Tipo de artefacto
        contexto: Contexto adicional

    Returns:
        Temporalidad (temporal, permanente, historico)
    """
    TIPOS_TEMPORALES = ["script"]  # Scripts por defecto temporales
    TIPOS_HISTORICOS = ["analisis", "reporte_limpieza", "sesion"]

    if contexto.get("temporal") is True:
        return "temporal"
    elif tipo in TIPOS_HISTORICOS:
        return "historico"
    elif tipo in TIPOS_TEMPORALES and not contexto.get("reutilizable"):
        return "temporal"
    else:
        return "permanente"
