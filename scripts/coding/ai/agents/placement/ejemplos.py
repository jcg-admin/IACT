"""
Ejemplos de uso del módulo de placement.

Ejecutar con:
    cd /home/user/IACT---project
    python3 -m scripts.coding.ai.agents.placement.ejemplos
"""

import sys
from pathlib import Path

# Agregar root del proyecto al path
project_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(project_root))

from scripts.coding.ai.agents.placement import clasificar_y_ubicar_artefacto
import json


def print_resultado(titulo, resultado):
    """Helper para imprimir resultados."""
    print(f"\n{'='*60}")
    print(f"{titulo}")
    print('='*60)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


# Ejemplo 1: Análisis de documentación
print("EJEMPLO 1: Usuario pide 'genera un análisis de documentación'")
resultado1 = clasificar_y_ubicar_artefacto(
    nombre_archivo="analisis_docs.md",
    contenido="## Análisis de Estructura\n\n...",
    tipo_declarado="análisis",
    contexto={
        "tema": "DOCS_ESTRUCTURA",
        "autor": "agente-cleanup"
    }
)
print_resultado("Análisis de Documentación", resultado1)


# Ejemplo 2: TASK transversal
print("\n\nEJEMPLO 2: Usuario pide 'crea una TASK para implementar autenticación en backend y frontend'")
resultado2 = clasificar_y_ubicar_artefacto(
    nombre_archivo="task_autenticacion.md",
    contenido="## Implementar Autenticación\n\nAfecta backend (API) y frontend (UI)...",
    tipo_declarado="tarea",
    contexto={
        "id": "050",
        "descripcion": "implementar autenticacion",
        "dominio": None,  # Afecta múltiples dominios
        "afecta_multiples_dominios": True
    }
)
print_resultado("TASK Transversal", resultado2)


# Ejemplo 3: Script temporal
print("\n\nEJEMPLO 3: Script temporal de análisis")
resultado3 = clasificar_y_ubicar_artefacto(
    nombre_archivo="analyze_structure.sh",
    contenido="#!/bin/bash\nfind docs -name '*.md'...",
    tipo_declarado="script",
    contexto={
        "accion": "analyze",
        "objeto": "domain_structure",
        "temporal": True,
        "reutilizable": False
    }
)
print_resultado("Script Temporal", resultado3)


# Ejemplo 4: Documentación de agente
print("\n\nEJEMPLO 4: Documentación de agente")
resultado4 = clasificar_y_ubicar_artefacto(
    nombre_archivo="README_PLACEMENT.md",
    contenido="## Arquitectura\n\nEl agente está compuesto por 5 sub-agentes...\n\n## Sub-Agentes\n\n...",
    tipo_declarado=None,  # Detectar automáticamente
    contexto={
        "nombre_agente": "PLACEMENT",
        "id": "AGENT-PLACEMENT"
    }
)
print_resultado("Documentación de Agente", resultado4)


# Ejemplo 5: TASK específica de dominio
print("\n\nEJEMPLO 5: TASK específica de backend")
resultado5 = clasificar_y_ubicar_artefacto(
    nombre_archivo="TASK-051-implementar_api_graphql.md",
    contenido="## Implementar API GraphQL\n\nEsta tarea es específica del backend...",
    tipo_declarado=None,  # Detectar por nombre
    contexto={
        "dominio": "backend"
    }
)
print_resultado("TASK Específica de Backend", resultado5)


if __name__ == "__main__":
    print("\n\n" + "="*60)
    print("EJEMPLOS COMPLETADOS")
    print("="*60)
