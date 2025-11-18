"""
Validación y cálculo de confianza.
"""

from typing import Dict, Optional


def calcular_confianza(tipo_declarado: Optional[str], tipo_detectado: str, matches: Dict) -> float:
    """
    Calcula confianza en la clasificación (0.0-1.0).

    Args:
        tipo_declarado: Tipo declarado por usuario (puede ser None)
        tipo_detectado: Tipo detectado automáticamente
        matches: Coincidencias encontradas

    Returns:
        Score de confianza entre 0.0 y 1.0
    """
    confianza = 0.5  # Base

    # Boost si tipo declarado coincide con detectado
    if tipo_declarado and tipo_declarado == tipo_detectado:
        confianza += 0.3

    # Boost por matches en contenido
    if matches.get("nombre_correcto"):
        confianza += 0.1
    if matches.get("frontmatter_presente"):
        confianza += 0.1
    if matches.get("estructura_correcta"):
        confianza += 0.1

    return min(confianza, 1.0)


def analizar_coincidencias(contenido: str, tipo: str) -> Dict:
    """
    Analiza coincidencias entre contenido y tipo esperado.

    Args:
        contenido: Contenido del archivo
        tipo: Tipo esperado

    Returns:
        Diccionario con coincidencias encontradas
    """
    return {
        "nombre_correcto": True,  # Simplificado
        "frontmatter_presente": contenido.startswith("---"),
        "estructura_correcta": "##" in contenido,
    }
