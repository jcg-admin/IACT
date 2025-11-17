"""
Módulo de clasificación y placement de artefactos.

Este módulo implementa el algoritmo descrito en:
docs/gobernanza/guias/GUIA_UBICACIONES_ARTEFACTOS.md
"""

from .classifier import clasificar_y_ubicar_artefacto
from .detector import detectar_tipo, detectar_dominios_en_contenido
from .ownership import determinar_ownership
from .temporalidad import determinar_temporalidad
from .ubicacion import construir_ubicacion
from .naming import construir_nombre, normalizar_descripcion, normalizar_nombre, normalizar_tipo
from .frontmatter import generar_frontmatter
from .contexto import decidir_por_contexto
from .validacion import calcular_confianza, analizar_coincidencias

__all__ = [
    'clasificar_y_ubicar_artefacto',
    'detectar_tipo',
    'detectar_dominios_en_contenido',
    'determinar_ownership',
    'determinar_temporalidad',
    'construir_ubicacion',
    'construir_nombre',
    'normalizar_descripcion',
    'normalizar_nombre',
    'normalizar_tipo',
    'generar_frontmatter',
    'decidir_por_contexto',
    'calcular_confianza',
    'analizar_coincidencias',
]
