#!/usr/bin/env python3
"""
CLI para clasificar y ubicar artefactos.

Uso:
    python cli.py <archivo> [--tipo TIPO] [--dominio DOMINIO] [--temporal]

Ejemplos:
    python cli.py analisis_docs.md --tipo analisis
    python cli.py task_nueva.md --tipo tarea --dominio backend
    python cli.py script.sh --temporal
"""

import argparse
import json
import sys
from pathlib import Path
from classifier import clasificar_y_ubicar_artefacto


def main():
    parser = argparse.ArgumentParser(
        description="Clasifica artefacto y determina ubicación canónica"
    )
    parser.add_argument("archivo", help="Ruta al archivo a clasificar")
    parser.add_argument("--tipo", help="Tipo declarado (opcional)")
    parser.add_argument("--dominio", help="Dominio (backend, frontend, infraestructura, ai)")
    parser.add_argument("--temporal", action="store_true", help="Marcar como temporal")
    parser.add_argument("--tema", help="Tema para análisis/sesión/guía")
    parser.add_argument("--descripcion", help="Descripción para TASK/ADR/REQ")
    parser.add_argument("--id", help="ID para TASK/ADR/REQ")
    parser.add_argument("--json", action="store_true", help="Output en formato JSON")

    args = parser.parse_args()

    # Leer archivo
    archivo_path = Path(args.archivo)
    if not archivo_path.exists():
        print(f"Error: Archivo '{args.archivo}' no existe", file=sys.stderr)
        sys.exit(1)

    contenido = archivo_path.read_text(encoding='utf-8')
    nombre_archivo = archivo_path.name

    # Construir contexto
    contexto = {}
    if args.dominio:
        contexto["dominio"] = args.dominio
    if args.temporal:
        contexto["temporal"] = True
    if args.tema:
        contexto["tema"] = args.tema
    if args.descripcion:
        contexto["descripcion"] = args.descripcion
    if args.id:
        contexto["id"] = args.id

    # Clasificar
    resultado = clasificar_y_ubicar_artefacto(
        nombre_archivo=nombre_archivo,
        contenido=contenido,
        tipo_declarado=args.tipo,
        contexto=contexto
    )

    # Output
    if args.json:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(f"Tipo detectado: {resultado['tipo']}")
        print(f"Ubicación canónica: {resultado['ubicacion']}")
        print(f"Nombre sugerido: {resultado['nombre_sugerido']}")
        print(f"Confianza: {resultado['confianza']:.0%}")
        print(f"\nFrontmatter sugerido:")
        print("---")
        for key, value in resultado['frontmatter'].items():
            if isinstance(value, list):
                print(f"{key}: {json.dumps(value)}")
            else:
                print(f"{key}: {value}")
        print("---")


if __name__ == "__main__":
    main()
