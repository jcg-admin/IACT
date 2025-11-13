#!/usr/bin/env python3
"""
Script para estandarizar numeracion de ADRs al formato: ADR-2025-XXX-descripcion.md
"""

import os
import re
from pathlib import Path

# Mapeo de renombrado: (ruta_actual, nueva_ruta, nuevo_id, fecha)
# Orden cronologico basado en fechas de los documentos
ADR_MAPPING = [
    # 2025-01-15
    ("docs/infraestructura/adr_2025_001_vagrant_mod_wsgi.md",
     "docs/infraestructura/ADR-2025-001-vagrant-mod-wsgi.md",
     "ADR-2025-001",
     "2025-01-15"),

    # 2025-XX-XX (asumiendo orden secuencial)
    ("docs/infraestructura/adr_2025_002_suite_calidad_codigo.md",
     "docs/infraestructura/ADR-2025-002-suite-calidad-codigo.md",
     "ADR-2025-002",
     "2025-XX-XX"),

    # 2025-11-06
    ("docs/ai/adr_2025_003_dora_sdlc_integration.md",
     "docs/ai/ADR-2025-003-dora-sdlc-integration.md",
     "ADR-2025-003",
     "2025-11-06"),

    # 2025-XX-XX
    ("docs/backend/adr_2025_004_centralized_log_storage.md",
     "docs/backend/ADR-2025-004-centralized-log-storage.md",
     "ADR-2025-004",
     "2025-XX-XX"),

    # 2025-11-07
    ("docs/backend/adr_2025_005_grupos_funcionales_sin_jerarquia.md",
     "docs/backend/ADR-2025-005-grupos-funcionales-sin-jerarquia.md",
     "ADR-2025-005",
     "2025-11-07"),

    # 2025-XX-XX
    ("docs/backend/adr_2025_006_configuracion_dinamica_sistema.md",
     "docs/backend/ADR-2025-006-configuracion-dinamica-sistema.md",
     "ADR-2025-006",
     "2025-XX-XX"),

    # 2025-XX-XX
    ("docs/infraestructura/adr_2025_007_git_hooks_validation_strategy.md",
     "docs/infraestructura/ADR-2025-007-git-hooks-validation-strategy.md",
     "ADR-2025-007",
     "2025-XX-XX"),

    # 2025-XX-XX
    ("docs/gobernanza/adr_2025_008_workflow_validation_shell_migration.md",
     "docs/gobernanza/ADR-2025-008-workflow-validation-shell-migration.md",
     "ADR-2025-008",
     "2025-XX-XX"),

    # 2025-XX-XX
    ("docs/backend/adr_2025_009_frontend_postponement.md",
     "docs/backend/ADR-2025-009-frontend-postponement.md",
     "ADR-2025-009",
     "2025-XX-XX"),

    # 2025-XX-XX
    ("docs/backend/adr_2025_010_orm_sql_hybrid_permissions.md",
     "docs/backend/ADR-2025-010-orm-sql-hybrid-permissions.md",
     "ADR-2025-010",
     "2025-XX-XX"),

    # 2025-XX-XX
    ("docs/infraestructura/adr_2025_011_wasi_style_virtualization.md",
     "docs/infraestructura/ADR-2025-011-wasi_style_virtualization.md",
     "ADR-2025-011",
     "2025-XX-XX"),

    # ADRs con formato ADR_XXX (sin año) - asignar nuevos numeros
    ("docs/infraestructura/ADR_008_cpython_features_vs_imagen_base.md",
     "docs/infraestructura/ADR-2025-012-cpython-features-vs-imagen-base.md",
     "ADR-2025-012",
     "2025-XX-XX"),

    ("docs/infraestructura/ADR_009_distribucion_artefactos_strategy.md",
     "docs/infraestructura/ADR-2025-013-distribucion-artefactos-strategy.md",
     "ADR-2025-013",
     "2025-XX-XX"),

    ("docs/backend/ADR_010_organizacion_proyecto_por_dominio.md",
     "docs/backend/ADR-2025-014-organizacion-proyecto-por-dominio.md",
     "ADR-2025-014",
     "2025-XX-XX"),

    ("docs/frontend/ADR_011_frontend_modular_monolith.md",
     "docs/frontend/ADR-2025-015-frontend-modular-monolith.md",
     "ADR-2025-015",
     "2025-XX-XX"),

    # ADR-012 tiene CONFLICTO - hay 2 archivos diferentes
    # Renombrar el de backend (Redux) primero
    ("docs/backend/ADR_012_redux_toolkit_state_management.md",
     "docs/backend/ADR-2025-016-redux-toolkit-state-management.md",
     "ADR-2025-016",
     "2025-XX-XX"),

    # ADR-012 de AI (sistema permisos) - mantener numero logico
    ("docs/ai/ADR-012-sistema-permisos-sin-roles-jerarquicos.md",
     "docs/ai/ADR-2025-017-sistema-permisos-sin-roles-jerarquicos.md",
     "ADR-2025-017",
     "2025-11-07"),

    ("docs/frontend/ADR_013_webpack_bundler.md",
     "docs/frontend/ADR-2025-018-webpack-bundler.md",
     "ADR-2025-018",
     "2025-XX-XX"),

    ("docs/frontend/ADR_014_testing_strategy_jest_testing_library.md",
     "docs/frontend/ADR-2025-019-testing-strategy-jest-testing-library.md",
     "ADR-2025-019",
     "2025-XX-XX"),

    # ADRs con formato ADR-XXXX (frontend/arquitectura/adr/)
    ("docs/frontend/arquitectura/adr/ADR-0001-servicios-resilientes.md",
     "docs/frontend/arquitectura/adr/ADR-2025-020-servicios-resilientes.md",
     "ADR-2025-020",
     "2025-11-09"),

    ("docs/frontend/arquitectura/adr/ADR-0002-arquitectura-microfrontends.md",
     "docs/frontend/arquitectura/adr/ADR-2025-021-arquitectura-microfrontends.md",
     "ADR-2025-021",
     "2025-XX-XX"),
]

def update_adr_content(file_path: Path, new_id: str) -> str:
    """Actualiza el ID dentro del contenido del ADR"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Actualizar id: en frontmatter YAML
    content = re.sub(
        r'^id:\s*[A-Z]+-[0-9-]+.*$',
        f'id: {new_id}',
        content,
        flags=re.MULTILINE
    )

    # Actualizar titulo si contiene el ID viejo
    # Por ejemplo: # ADR-012: ... -> # ADR-2025-017: ...
    content = re.sub(
        r'^#\s*(ADR|adr)[-_]([0-9-]+):',
        f'# {new_id}:',
        content,
        flags=re.MULTILINE
    )

    return content

def main():
    project_root = Path("/home/user/IACT---project")
    os.chdir(project_root)

    print("=" * 80)
    print("ESTANDARIZACION DE ADRs")
    print("=" * 80)
    print()

    renamed_files = []

    for old_path_str, new_path_str, new_id, fecha in ADR_MAPPING:
        old_path = Path(old_path_str)
        new_path = Path(new_path_str)

        if not old_path.exists():
            print(f"SKIP: {old_path} (no existe)")
            continue

        print(f"Renombrando: {old_path.name}")
        print(f"  -> {new_path.name}")
        print(f"  ID: {new_id} | Fecha: {fecha}")

        # Actualizar contenido
        try:
            new_content = update_adr_content(old_path, new_id)

            # Escribir contenido actualizado al nuevo archivo
            new_path.parent.mkdir(parents=True, exist_ok=True)
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Eliminar archivo viejo
            old_path.unlink()

            renamed_files.append((old_path_str, new_path_str, new_id))
            print(f"  OK: Renombrado exitosamente")
        except Exception as e:
            print(f"  ERROR: {e}")

        print()

    print("=" * 80)
    print(f"RESUMEN: {len(renamed_files)} ADRs renombrados")
    print("=" * 80)
    print()

    # Generar mapeo para actualizar referencias
    print("Mapeo de referencias a actualizar:")
    print()
    for old_path, new_path, new_id in renamed_files:
        old_filename = Path(old_path).name
        new_filename = Path(new_path).name
        print(f"{old_filename} -> {new_filename}")

    return renamed_files

if __name__ == "__main__":
    main()
