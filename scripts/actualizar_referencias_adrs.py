#!/usr/bin/env python3
"""
Script para actualizar referencias a ADRs en todos los documentos
"""

import re
from pathlib import Path

# Mapeo de nombres viejos a nuevos
REFERENCE_MAPPING = {
    # Nombres de archivo
    "adr_2025_001_vagrant_mod_wsgi": "ADR-2025-001-vagrant-mod-wsgi",
    "adr_2025_002_suite_calidad_codigo": "ADR-2025-002-suite-calidad-codigo",
    "adr_2025_003_dora_sdlc_integration": "ADR-2025-003-dora-sdlc-integration",
    "adr_2025_004_centralized_log_storage": "ADR-2025-004-centralized-log-storage",
    "adr_2025_005_grupos_funcionales_sin_jerarquia": "ADR-2025-005-grupos-funcionales-sin-jerarquia",
    "adr_2025_006_configuracion_dinamica_sistema": "ADR-2025-006-configuracion-dinamica-sistema",
    "adr_2025_007_git_hooks_validation_strategy": "ADR-2025-007-git-hooks-validation-strategy",
    "adr_2025_008_workflow_validation_shell_migration": "ADR-2025-008-workflow-validation-shell-migration",
    "adr_2025_009_frontend_postponement": "ADR-2025-009-frontend-postponement",
    "adr_2025_010_orm_sql_hybrid_permissions": "ADR-2025-010-orm-sql-hybrid-permissions",
    "adr_2025_011_wasi_style_virtualization": "ADR-2025-011-wasi_style_virtualization",
    "ADR_008_cpython_features_vs_imagen_base": "ADR-2025-012-cpython-features-vs-imagen-base",
    "ADR_009_distribucion_artefactos_strategy": "ADR-2025-013-distribucion-artefactos-strategy",
    "ADR_010_organizacion_proyecto_por_dominio": "ADR-2025-014-organizacion-proyecto-por-dominio",
    "ADR_011_frontend_modular_monolith": "ADR-2025-015-frontend-modular-monolith",
    "ADR_012_redux_toolkit_state_management": "ADR-2025-016-redux-toolkit-state-management",
    "ADR-012-sistema-permisos-sin-roles-jerarquicos": "ADR-2025-017-sistema-permisos-sin-roles-jerarquicos",
    "ADR_013_webpack_bundler": "ADR-2025-018-webpack-bundler",
    "ADR_014_testing_strategy_jest_testing_library": "ADR-2025-019-testing-strategy-jest-testing-library",
    "ADR-0001-servicios-resilientes": "ADR-2025-020-servicios-resilientes",
    "ADR-0002-arquitectura-microfrontends": "ADR-2025-021-arquitectura-microfrontends",

    # IDs referenciados (sin .md)
    "ADR-2025-001": "ADR-2025-001",  # Ya correcto
    "ADR-2025-002": "ADR-2025-002",
    "ADR-2025-003": "ADR-2025-003",
    "ADR-2025-004": "ADR-2025-004",
    "ADR-2025-005": "ADR-2025-005",
    "ADR-2025-006": "ADR-2025-006",
    "ADR-2025-007": "ADR-2025-007",
    "ADR-2025-008": "ADR-2025-008",
    "ADR-2025-009": "ADR-2025-009",
    "ADR-2025-010": "ADR-2025-010",
    "ADR-2025-011": "ADR-2025-011",
    "ADR-012": "ADR-2025-017",  # Conflicto resuelto
}

def update_file_references(file_path: Path) -> int:
    """Actualiza referencias a ADRs en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes = 0

        # Actualizar referencias en enlaces markdown, rutas, etc.
        for old_name, new_name in REFERENCE_MAPPING.items():
            if old_name in content:
                # Reemplazar con .md
                content = content.replace(f"{old_name}.md", f"{new_name}.md")
                # Reemplazar sin .md (en IDs, referencias, etc.)
                content = content.replace(old_name, new_name)
                changes += 1

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes

        return 0
    except Exception as e:
        print(f"  ERROR procesando {file_path}: {e}")
        return 0

def main():
    project_root = Path("/home/user/IACT---project")
    docs_dir = project_root / "docs"

    print("=" * 80)
    print("ACTUALIZANDO REFERENCIAS A ADRs")
    print("=" * 80)
    print()

    total_files = 0
    total_changes = 0

    # Buscar todos los archivos .md en docs/ (excluyendo docs_analysis_report)
    for md_file in docs_dir.rglob("*.md"):
        # Saltar docs_analysis_report
        if "docs_analysis_report" in str(md_file):
            continue

        changes = update_file_references(md_file)
        if changes > 0:
            total_files += 1
            total_changes += changes
            print(f"Actualizado: {md_file.relative_to(project_root)} ({changes} cambios)")

    print()
    print("=" * 80)
    print(f"RESUMEN: {total_files} archivos actualizados, {total_changes} cambios totales")
    print("=" * 80)

if __name__ == "__main__":
    main()
