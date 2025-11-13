#!/usr/bin/env python3
"""
Script para corregir nomenclatura de ADRs de guiones (-) a guiones bajos (_)
"""

import os
import re
from pathlib import Path

# Mapeo de corrección: guiones a guiones bajos
CORRECTIONS = [
    ("docs/infraestructura/ADR-2025-001-vagrant-mod-wsgi.md",
     "docs/infraestructura/ADR_2025_001_vagrant_mod_wsgi.md"),

    ("docs/infraestructura/ADR-2025-002-suite-calidad-codigo.md",
     "docs/infraestructura/ADR_2025_002_suite_calidad_codigo.md"),

    ("docs/ai/ADR-2025-003-dora-sdlc-integration.md",
     "docs/ai/ADR_2025_003_dora_sdlc_integration.md"),

    ("docs/backend/ADR-2025-004-centralized-log-storage.md",
     "docs/backend/ADR_2025_004_centralized_log_storage.md"),

    ("docs/backend/ADR-2025-005-grupos-funcionales-sin-jerarquia.md",
     "docs/backend/ADR_2025_005_grupos_funcionales_sin_jerarquia.md"),

    ("docs/backend/ADR-2025-006-configuracion-dinamica-sistema.md",
     "docs/backend/ADR_2025_006_configuracion_dinamica_sistema.md"),

    ("docs/infraestructura/ADR-2025-007-git-hooks-validation-strategy.md",
     "docs/infraestructura/ADR_2025_007_git_hooks_validation_strategy.md"),

    ("docs/gobernanza/ADR-2025-008-workflow-validation-shell-migration.md",
     "docs/gobernanza/ADR_2025_008_workflow_validation_shell_migration.md"),

    ("docs/backend/ADR-2025-009-frontend-postponement.md",
     "docs/backend/ADR_2025_009_frontend_postponement.md"),

    ("docs/backend/ADR-2025-010-orm-sql-hybrid-permissions.md",
     "docs/backend/ADR_2025_010_orm_sql_hybrid_permissions.md"),

    ("docs/infraestructura/ADR-2025-011-wasi_style_virtualization.md",
     "docs/infraestructura/ADR_2025_011_wasi_style_virtualization.md"),

    ("docs/infraestructura/ADR-2025-012-cpython-features-vs-imagen-base.md",
     "docs/infraestructura/ADR_2025_012_cpython_features_vs_imagen_base.md"),

    ("docs/infraestructura/ADR-2025-013-distribucion-artefactos-strategy.md",
     "docs/infraestructura/ADR_2025_013_distribucion_artefactos_strategy.md"),

    ("docs/backend/ADR-2025-014-organizacion-proyecto-por-dominio.md",
     "docs/backend/ADR_2025_014_organizacion_proyecto_por_dominio.md"),

    ("docs/frontend/ADR-2025-015-frontend-modular-monolith.md",
     "docs/frontend/ADR_2025_015_frontend_modular_monolith.md"),

    ("docs/backend/ADR-2025-016-redux-toolkit-state-management.md",
     "docs/backend/ADR_2025_016_redux_toolkit_state_management.md"),

    ("docs/ai/ADR-2025-017-sistema-permisos-sin-roles-jerarquicos.md",
     "docs/ai/ADR_2025_017_sistema_permisos_sin_roles_jerarquicos.md"),

    ("docs/frontend/ADR-2025-018-webpack-bundler.md",
     "docs/frontend/ADR_2025_018_webpack_bundler.md"),

    ("docs/frontend/ADR-2025-019-testing-strategy-jest-testing-library.md",
     "docs/frontend/ADR_2025_019_testing_strategy_jest_testing_library.md"),

    ("docs/frontend/arquitectura/adr/ADR-2025-020-servicios-resilientes.md",
     "docs/frontend/arquitectura/adr/ADR_2025_020_servicios_resilientes.md"),

    ("docs/frontend/arquitectura/adr/ADR-2025-021-arquitectura-microfrontends.md",
     "docs/frontend/arquitectura/adr/ADR_2025_021_arquitectura_microfrontends.md"),
]

def update_adr_id(file_path: Path, new_id: str) -> str:
    """Actualiza el ID dentro del ADR con guiones bajos"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Actualizar id: en frontmatter
    content = re.sub(
        r'^id:\s*ADR-2025-[0-9]+.*$',
        f'id: {new_id}',
        content,
        flags=re.MULTILINE
    )

    # Actualizar título si contiene ADR-2025-XXX
    content = re.sub(
        r'^#\s*ADR-2025-([0-9]+):',
        f'# {new_id}:',
        content,
        flags=re.MULTILINE
    )

    return content

def main():
    project_root = Path("/home/user/IACT---project")
    os.chdir(project_root)

    print("=" * 80)
    print("CORRIGIENDO NOMENCLATURA DE ADRs: guiones (-) a guiones bajos (_)")
    print("=" * 80)
    print()

    renamed = []

    for old_path_str, new_path_str in CORRECTIONS:
        old_path = Path(old_path_str)
        new_path = Path(new_path_str)

        if not old_path.exists():
            print(f"SKIP: {old_path} (no existe)")
            continue

        # Extraer nuevo ID (ej: ADR_2025_001)
        new_id = new_path.stem.split('_')[:3]  # ADR_2025_001
        new_id = '_'.join(new_id)

        print(f"Renombrando: {old_path.name}")
        print(f"  -> {new_path.name}")
        print(f"  ID: {new_id}")

        try:
            # Actualizar contenido
            new_content = update_adr_id(old_path, new_id)

            # Escribir nuevo archivo
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Eliminar viejo
            old_path.unlink()

            renamed.append((old_path_str, new_path_str))
            print(f"  OK")
        except Exception as e:
            print(f"  ERROR: {e}")

        print()

    print("=" * 80)
    print(f"RESUMEN: {len(renamed)} ADRs corregidos")
    print("=" * 80)

    return renamed

if __name__ == "__main__":
    main()
