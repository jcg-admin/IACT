#!/usr/bin/env python3
"""
Script para generar workflows CI/CD basados en templates.

Uso:
    python scripts/generate_workflow_from_template.py --template plantilla_django_app.md --workflow backend-ci
    python scripts/generate_workflow_from_template.py --list-mappings
    python scripts/generate_workflow_from_template.py --validate

Funcionalidad:
1. Lee workflow_template_mapping.json
2. Cuando creas codigo con un template, sugiere el workflow
3. Valida que workflows tengan los templates correctos
4. Actualiza metadata en headers YAML
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MAPPING_FILE = PROJECT_ROOT / ".claude" / "workflow_template_mapping.json"
WORKFLOWS_DIR = PROJECT_ROOT / ".github" / "workflows"
TEMPLATES_DIR = PROJECT_ROOT / "docs" / "plantillas"
PROCEDIMIENTOS_DIR = PROJECT_ROOT / "docs" / "gobernanza" / "procesos" / "procedimientos"


def load_mapping() -> Dict:
    """Cargar archivo de mapeo."""
    if not MAPPING_FILE.exists():
        print(f"ERROR: Archivo de mapeo no encontrado: {MAPPING_FILE}")
        sys.exit(1)

    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_mappings(mapping: Dict) -> None:
    """Listar todos los mapeos disponibles."""
    print("=" * 80)
    print("MAPEOS DISPONIBLES: TEMPLATE -> WORKFLOW")
    print("=" * 80)

    for template, workflows in mapping['reverse_mappings']['by_template'].items():
        print(f"\nTemplate: {template}")
        print(f"  Workflows: {', '.join(workflows)}")

        # Buscar metadata
        if template in mapping.get('template_metadata', {}):
            meta = mapping['template_metadata'][template]
            print(f"  Fase SDLC: {meta.get('fase_sdlc', 'N/A')}")
            print(f"  Categoria: {meta.get('categoria', 'N/A')}")
            print(f"  Genera: {meta.get('genera_artefacto', 'N/A')}")


def get_workflow_for_template(mapping: Dict, template_name: str) -> List[str]:
    """Obtener workflows asociados a un template."""
    by_template = mapping['reverse_mappings']['by_template']

    # Buscar con nombre exacto o parcial
    for template, workflows in by_template.items():
        if template_name in template or template in template_name:
            return workflows

    return []


def get_templates_for_workflow(mapping: Dict, workflow_name: str) -> List[str]:
    """Obtener templates asociados a un workflow."""
    if workflow_name in mapping['mappings']:
        return mapping['mappings'][workflow_name]['templates']
    return []


def generate_template_header_comment(mapping: Dict, template_name: str) -> str:
    """Generar comentario para agregar al template."""
    workflows = get_workflow_for_template(mapping, template_name)

    if not workflows:
        return ""

    comment = "\n<!-- WORKFLOWS ASOCIADOS -->\n"
    comment += "<!-- Al usar este template, los siguientes workflows validaran el codigo: -->\n"

    for wf in workflows:
        if wf in mapping['mappings']:
            wf_data = mapping['mappings'][wf]
            comment += f"<!-- - {wf}: {', '.join(wf_data.get('validations', []))} -->\n"

    comment += "<!-- Ver: .claude/workflow_template_mapping.json para detalles -->\n"

    return comment


def generate_workflow_comment(mapping: Dict, workflow_name: str) -> str:
    """Generar comentario para agregar al workflow."""
    templates = get_templates_for_workflow(mapping, workflow_name)

    if not templates:
        return ""

    comment = "\n# TEMPLATES ASOCIADOS\n"
    comment += "# Este workflow valida codigo generado con los siguientes templates:\n"

    for tmpl in templates:
        comment += f"#   - {tmpl}\n"

    procedimientos = mapping['mappings'][workflow_name].get('procedimientos', [])
    if procedimientos:
        comment += "#\n# PROCEDIMIENTOS RELACIONADOS:\n"
        for proc in procedimientos:
            proc_name = os.path.basename(proc)
            comment += f"#   - {proc_name}\n"

    comment += "#\n# Ver: .claude/workflow_template_mapping.json para mapeo completo\n"

    return comment


def generate_procedimiento_section(mapping: Dict, procedimiento_name: str) -> str:
    """Generar seccion 'Templates a Usar' para procedimiento."""
    # Buscar procedimiento en reverse mappings
    by_proc = mapping['reverse_mappings']['by_procedimiento']

    workflows = []
    for proc, wfs in by_proc.items():
        if procedimiento_name in proc:
            workflows = wfs
            break

    if not workflows:
        return ""

    # Obtener templates de esos workflows
    all_templates = set()
    for wf in workflows:
        if wf in mapping['mappings']:
            all_templates.update(mapping['mappings'][wf]['templates'])

    if not all_templates:
        return ""

    section = "\n## Templates a Usar\n\n"
    section += "Al seguir este procedimiento, usa los siguientes templates:\n\n"

    for tmpl in sorted(all_templates):
        tmpl_name = os.path.basename(tmpl)
        section += f"- [{tmpl_name}](../../plantillas/{tmpl_name})\n"

    section += "\n**Workflows que validaran el codigo:**\n\n"
    for wf in sorted(workflows):
        if wf in mapping['mappings']:
            validations = mapping['mappings'][wf].get('validations', [])
            section += f"- `{wf}.yml`: {', '.join(validations)}\n"

    return section


def validate_mappings(mapping: Dict) -> None:
    """Validar que todos los archivos referenciados existen."""
    print("=" * 80)
    print("VALIDANDO MAPEOS")
    print("=" * 80)

    errors = []
    warnings = []

    # Validar workflows
    for wf_name, wf_data in mapping['mappings'].items():
        wf_path = PROJECT_ROOT / wf_data['workflow']
        if not wf_path.exists():
            errors.append(f"Workflow no existe: {wf_path}")

        # Validar templates
        for tmpl in wf_data.get('templates', []):
            tmpl_path = PROJECT_ROOT / tmpl
            if not tmpl_path.exists():
                warnings.append(f"Template no existe: {tmpl_path}")

        # Validar procedimientos
        for proc in wf_data.get('procedimientos', []):
            proc_path = PROJECT_ROOT / proc
            if not proc_path.exists():
                warnings.append(f"Procedimiento no existe: {proc_path}")

        # Validar scripts
        for script in wf_data.get('scripts', []):
            script_path = PROJECT_ROOT / script
            if not script_path.exists():
                warnings.append(f"Script no existe: {script_path}")

    # Resultados
    if errors:
        print("\n[ERRORES]")
        for err in errors:
            print(f"  - {err}")

    if warnings:
        print("\n[ADVERTENCIAS]")
        for warn in warnings:
            print(f"  - {warn}")

    if not errors and not warnings:
        print("\n[OK] Todos los mapeos son validos")

    print("=" * 80)


def suggest_workflow_for_file(mapping: Dict, file_path: str) -> None:
    """Sugerir workflow basado en archivo creado."""
    file_path_obj = Path(file_path)

    print(f"\nArchivo: {file_path}")
    print("Workflows sugeridos:")

    # Verificar contra paths de workflows
    for wf_name, wf_data in mapping['mappings'].items():
        for path_pattern in wf_data.get('paths', []):
            # Simplificada: solo verificar si el path coincide aproximadamente
            if any(part in str(file_path_obj) for part in path_pattern.split('**')):
                print(f"  - {wf_name}.yml")
                print(f"    Validaciones: {', '.join(wf_data.get('validations', []))}")

                templates = wf_data.get('templates', [])
                if templates:
                    print(f"    Templates relacionados: {', '.join([os.path.basename(t) for t in templates])}")


def interactive_mode(mapping: Dict) -> None:
    """Modo interactivo para consultar mapeos."""
    print("=" * 80)
    print("MODO INTERACTIVO - Consulta de Mapeos")
    print("=" * 80)
    print("\nComandos:")
    print("  template <nombre>    - Buscar workflows para un template")
    print("  workflow <nombre>    - Buscar templates para un workflow")
    print("  procedimiento <nombre> - Buscar info de procedimiento")
    print("  file <path>          - Sugerir workflow para archivo")
    print("  list                 - Listar todos los mapeos")
    print("  quit                 - Salir")
    print()

    while True:
        try:
            cmd = input(">>> ").strip()

            if not cmd:
                continue

            if cmd == "quit":
                break

            parts = cmd.split(maxsplit=1)
            action = parts[0]
            arg = parts[1] if len(parts) > 1 else ""

            if action == "template":
                workflows = get_workflow_for_template(mapping, arg)
                if workflows:
                    print(f"\nWorkflows para '{arg}': {', '.join(workflows)}")
                else:
                    print(f"\nNo se encontraron workflows para '{arg}'")

            elif action == "workflow":
                templates = get_templates_for_workflow(mapping, arg)
                if templates:
                    print(f"\nTemplates para '{arg}':")
                    for t in templates:
                        print(f"  - {os.path.basename(t)}")
                else:
                    print(f"\nNo se encontraron templates para '{arg}'")

            elif action == "procedimiento":
                section = generate_procedimiento_section(mapping, arg)
                if section:
                    print(section)
                else:
                    print(f"\nNo se encontro info para '{arg}'")

            elif action == "file":
                suggest_workflow_for_file(mapping, arg)

            elif action == "list":
                list_mappings(mapping)

            else:
                print(f"Comando desconocido: {action}")

        except KeyboardInterrupt:
            print("\n\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Generador y validador de workflows basados en templates"
    )

    parser.add_argument(
        '--list-mappings',
        action='store_true',
        help='Listar todos los mapeos template -> workflow'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validar que todos los archivos referenciados existen'
    )

    parser.add_argument(
        '--template',
        type=str,
        help='Nombre del template para consultar workflows asociados'
    )

    parser.add_argument(
        '--workflow',
        type=str,
        help='Nombre del workflow para consultar templates asociados'
    )

    parser.add_argument(
        '--file',
        type=str,
        help='Path de archivo para sugerir workflow'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Modo interactivo'
    )

    args = parser.parse_args()

    # Cargar mapeo
    mapping = load_mapping()

    # Ejecutar acciones
    if args.list_mappings:
        list_mappings(mapping)

    elif args.validate:
        validate_mappings(mapping)

    elif args.template:
        workflows = get_workflow_for_template(mapping, args.template)
        if workflows:
            print(f"Workflows para template '{args.template}':")
            for wf in workflows:
                print(f"  - {wf}.yml")
                if wf in mapping['mappings']:
                    print(f"    Validaciones: {', '.join(mapping['mappings'][wf].get('validations', []))}")
        else:
            print(f"No se encontraron workflows para template '{args.template}'")

    elif args.workflow:
        templates = get_templates_for_workflow(mapping, args.workflow)
        if templates:
            print(f"Templates para workflow '{args.workflow}':")
            for t in templates:
                print(f"  - {os.path.basename(t)}")
        else:
            print(f"No se encontraron templates para workflow '{args.workflow}'")

    elif args.file:
        suggest_workflow_for_file(mapping, args.file)

    elif args.interactive:
        interactive_mode(mapping)

    else:
        parser.print_help()
        print("\nEjemplos de uso:")
        print("  python scripts/generate_workflow_from_template.py --list-mappings")
        print("  python scripts/generate_workflow_from_template.py --template plantilla_django_app.md")
        print("  python scripts/generate_workflow_from_template.py --workflow backend-ci")
        print("  python scripts/generate_workflow_from_template.py --file api/callcentersite/apps/myapp/models.py")
        print("  python scripts/generate_workflow_from_template.py --interactive")


if __name__ == "__main__":
    main()
