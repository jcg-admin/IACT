"""
Clasificador principal de artefactos.

Función principal que orquesta todo el proceso de clasificación.
"""

from typing import Dict, Optional
from .detector import detectar_tipo
from .ownership import determinar_ownership
from .temporalidad import determinar_temporalidad
from .ubicacion import construir_ubicacion
from .naming import construir_nombre, normalizar_tipo
from .frontmatter import generar_frontmatter
from .validacion import calcular_confianza, analizar_coincidencias


def clasificar_y_ubicar_artefacto(
    nombre_archivo: str,
    contenido: str,
    tipo_declarado: Optional[str] = None,
    contexto: Optional[Dict] = None
) -> Dict:
    """
    Clasifica artefacto y determina ubicación canónica.

    Args:
        nombre_archivo: Nombre del archivo
        contenido: Contenido del archivo (para análisis)
        tipo_declarado: Tipo declarado por usuario (opcional)
        contexto: Contexto adicional (dominio, temporal, etc.)

    Returns:
        {
            "tipo": str,  # Tipo de artefacto
            "ubicacion": str,  # Ubicación canónica
            "nombre_sugerido": str,  # Nombre siguiendo convenciones
            "frontmatter": dict,  # Frontmatter sugerido
            "confianza": float  # 0.0-1.0
        }
    """
    contexto = contexto or {}

    # 1. Detectar tipo si no está declarado
    if not tipo_declarado:
        tipo_detectado = detectar_tipo(nombre_archivo, contenido)
    else:
        tipo_detectado = normalizar_tipo(tipo_declarado)

    # 2. Determinar ownership (transversal vs dominio)
    ownership = determinar_ownership(tipo_detectado, contexto, contenido)

    # 3. Determinar temporalidad
    temporalidad = determinar_temporalidad(tipo_detectado, contexto)

    # 4. Construir ubicación
    ubicacion = construir_ubicacion(
        tipo=tipo_detectado,
        ownership=ownership,
        temporalidad=temporalidad,
        contexto=contexto
    )

    # 5. Construir nombre siguiendo convenciones
    nombre_sugerido = construir_nombre(
        tipo=tipo_detectado,
        nombre_original=nombre_archivo,
        contexto=contexto
    )

    # 6. Generar frontmatter
    frontmatter = generar_frontmatter(
        tipo=tipo_detectado,
        contexto=contexto
    )

    # 7. Calcular confianza
    confianza = calcular_confianza(
        tipo_declarado=tipo_declarado,
        tipo_detectado=tipo_detectado,
        matches=analizar_coincidencias(contenido, tipo_detectado)
    )

    return {
        "tipo": tipo_detectado,
        "ubicacion": ubicacion,
        "nombre_sugerido": nombre_sugerido,
        "frontmatter": frontmatter,
        "confianza": confianza
    }
