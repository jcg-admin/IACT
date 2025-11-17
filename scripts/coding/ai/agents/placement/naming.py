"""
Constructor de nombres según convenciones.
"""

import re
from datetime import datetime
from typing import Dict


def construir_nombre(tipo: str, nombre_original: str, contexto: Dict) -> str:
    """
    Construye nombre siguiendo convenciones del tipo.

    Args:
        tipo: Tipo de artefacto
        nombre_original: Nombre original del archivo
        contexto: Contexto adicional

    Returns:
        Nombre sugerido siguiendo convenciones
    """
    FORMATOS = {
        "task": lambda: f"TASK-{contexto.get('id', '001')}-{normalizar_descripcion(contexto.get('descripcion', 'nueva_tarea'))}.md",
        "adr": lambda: f"ADR-{contexto.get('id', '001')}-{normalizar_descripcion(contexto.get('descripcion', 'nueva_decision'))}.md",
        "solicitud": lambda: f"REQ-{contexto.get('id', '001')}-{normalizar_descripcion(contexto.get('descripcion', 'nueva_solicitud'))}.md",
        "analisis": lambda: f"ANALISIS_{contexto.get('tema', 'GENERAL').upper()}_{datetime.now().strftime('%Y%m%d')}.md",
        "reporte_limpieza": lambda: f"CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d')}.md",
        "sesion": lambda: f"SESSION_{contexto.get('tema', 'GENERAL').upper()}_{datetime.now().strftime('%Y_%m_%d')}.md",
        "documentacion_agente": lambda: f"README_{contexto.get('nombre_agente', 'NEW_AGENT').upper()}.md",
        "configuracion_agente": lambda: f"{contexto.get('nombre_agente', 'agent')}_config.json",
        "guia": lambda: f"GUIA_{contexto.get('tema', 'GENERAL').upper()}.md",
        "indice": lambda: "INDEX.md",
        "script": lambda: f"{contexto.get('accion', 'process')}_{contexto.get('objeto', 'data')}.{contexto.get('extension', 'sh')}",
    }

    if tipo in FORMATOS:
        return FORMATOS[tipo]()

    # Default: snake_case
    return normalizar_nombre(nombre_original)


def normalizar_descripcion(desc: str) -> str:
    """
    Normaliza descripción a snake_case sin emojis.

    Args:
        desc: Descripción a normalizar

    Returns:
        Descripción normalizada
    """
    # Eliminar emojis y caracteres especiales
    desc = re.sub(r'[^\w\s-]', '', desc)
    # Convertir a lowercase y reemplazar espacios/guiones por underscores
    desc = desc.lower().replace(' ', '_').replace('-', '_')
    # Eliminar underscores múltiples
    desc = re.sub(r'_+', '_', desc)
    return desc.strip('_')


def normalizar_nombre(nombre: str) -> str:
    """
    Normaliza nombre de archivo a snake_case.

    Args:
        nombre: Nombre a normalizar

    Returns:
        Nombre normalizado
    """
    # Mantener extensión
    partes = nombre.rsplit('.', 1)
    base = partes[0]
    ext = partes[1] if len(partes) > 1 else ''

    # Normalizar base
    base = normalizar_descripcion(base)

    return f"{base}.{ext}" if ext else base


def normalizar_tipo(tipo_declarado: str) -> str:
    """
    Normaliza tipo declarado por usuario a tipo canónico.

    Args:
        tipo_declarado: Tipo declarado por usuario

    Returns:
        Tipo canónico
    """
    ALIASES = {
        "análisis": "analisis",
        "reporte": "analisis",
        "report": "analisis",
        "cleanup": "reporte_limpieza",
        "limpieza": "reporte_limpieza",
        "tarea": "task",
        "decision": "adr",
        "agente": "documentacion_agente",
        "script": "script",
        "guía": "guia",
        "guide": "guia",
        "índice": "indice",
        "index": "indice",
    }

    return ALIASES.get(tipo_declarado.lower(), tipo_declarado.lower())
