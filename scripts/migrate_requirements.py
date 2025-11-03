#!/usr/bin/env python3
"""
Script de Migración de Requisitos Legacy
Migra requisitos de estructura antigua a docs/implementacion/
Agrega frontmatter YAML si falta
Detecta tipo de requisito automáticamente
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

# Paths
DOCS_PATH = Path("docs")
LEGACY_PATHS = [
    DOCS_PATH / "backend" / "requisitos",
    DOCS_PATH / "frontend" / "requisitos",
    DOCS_PATH / "infrastructure" / "requisitos",
    DOCS_PATH / "requisitos",
]
TARGET_PATH = DOCS_PATH / "implementacion"

# Files to skip
SKIP_FILES = ["readme.md", "README.md", "_MOVIDO_A_IMPLEMENTACION.md", "rq_plantilla.md", "trazabilidad.md"]

# Regex patterns para detectar tipo de requisito
PATTERNS = {
    'necesidad': r'necesidad|business\s+need|problema|oportunidad',
    'negocio': r'requisito\s+de\s+negocio|business\s+requirement|objetivo.*negocio',
    'stakeholder': r'stakeholder|usuario|cliente.*necesita',
    'funcional': r'el\s+sistema\s+deber[aá]|functional\s+requirement|RF-|API|endpoint',
    'no_funcional': r'performance|seguridad|disponibilidad|RNF-|no\s+funcional|non-functional',
}

def extract_frontmatter(filepath: Path) -> Tuple[Dict, str]:
    """Extrae frontmatter y contenido de un archivo."""
    try:
        content = filepath.read_text(encoding='utf-8')
        match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)), match.group(2)
        return {}, content
    except Exception as e:
        print(f"⚠️  Error leyendo {filepath}: {e}")
        return {}, ""

def detect_requirement_type(content: str, filename: str) -> str:
    """Detecta el tipo de requisito basado en contenido y nombre."""
    content_lower = content.lower()
    filename_lower = filename.lower()

    # Check filename first
    if any(x in filename_lower for x in ['necesidad', 'need']):
        return 'necesidades'
    if any(x in filename_lower for x in ['negocio', 'business']):
        return 'negocio'
    if any(x in filename_lower for x in ['stakeholder', 'usuario', 'cliente']):
        return 'stakeholders'
    if any(x in filename_lower for x in ['funcional', 'functional', 'rf']):
        return 'funcionales'
    if any(x in filename_lower for x in ['no_funcional', 'nonfunctional', 'rnf', 'performance', 'security']):
        return 'no_funcionales'

    # Check content
    for req_type, pattern in PATTERNS.items():
        if re.search(pattern, content_lower, re.IGNORECASE):
            # Map to folder names
            if req_type == 'necesidad':
                return 'necesidades'
            elif req_type == 'negocio':
                return 'negocio'
            elif req_type == 'stakeholder':
                return 'stakeholders'
            elif req_type == 'funcional':
                return 'funcionales'
            elif req_type == 'no_funcional':
                return 'no_funcionales'

    # Default to funcionales if can't detect
    return 'funcionales'

def detect_domain(source_path: Path) -> str:
    """Detecta el dominio (backend/frontend/infrastructure) basado en ruta."""
    path_str = str(source_path)
    if 'backend' in path_str:
        return 'backend'
    elif 'frontend' in path_str:
        return 'frontend'
    elif 'infrastructure' in path_str:
        return 'infrastructure'
    else:
        return 'backend'  # Default

def generate_frontmatter(filepath: Path, content: str, domain: str, req_type_folder: str) -> str:
    """Genera frontmatter YAML si no existe."""
    # Detect ID from filename or generate
    filename = filepath.stem

    # Try to extract ID from filename
    id_match = re.search(r'(N|RN|RS|RF|RNF)-?\d+', filename, re.IGNORECASE)
    if id_match:
        req_id = id_match.group(0).upper()
        if '-' not in req_id:
            req_id = req_id[0:2] + '-' + req_id[2:]  # RN001 → RN-001
    else:
        # Generate ID based on type
        type_prefix = {
            'necesidades': 'N',
            'negocio': 'RN',
            'stakeholders': 'RS',
            'funcionales': 'RF',
            'no_funcionales': 'RNF',
        }.get(req_type_folder, 'RF')
        req_id = f"{type_prefix}-XXX"  # User must update

    # Map folder to type
    tipo_map = {
        'necesidades': 'necesidad',
        'negocio': 'negocio',
        'stakeholders': 'stakeholder',
        'funcionales': 'funcional',
        'no_funcionales': 'no_funcional',
    }
    tipo = tipo_map.get(req_type_folder, 'funcional')

    # Extract title from first heading or filename
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        titulo = title_match.group(1).strip()
    else:
        titulo = filename.replace('_', ' ').replace('-', ' ').title()

    frontmatter = f"""---
id: {req_id}
tipo: {tipo}
titulo: {titulo}
dominio: {domain}
owner: equipo-{domain}
prioridad: media
estado: migrado_legacy
fecha_creacion: {filepath.stat().st_mtime}
fecha_migracion: AUTO

# IMPORTANTE: Actualizar trazabilidad manualmente
trazabilidad_upward:
  - # PENDIENTE: Agregar requisitos de nivel superior

trazabilidad_downward:
  - # PENDIENTE: Agregar tests o tareas

stakeholders:
  - # PENDIENTE: Agregar stakeholders

# Conformidad ISO 29148
iso29148_clause: "9.6"
verificacion_metodo: # test|inspection|analysis|demonstration

# Nota: Archivo migrado automáticamente desde estructura legacy
# Revisar y completar todos los campos marcados como PENDIENTE
---

"""
    return frontmatter

def migrate_file(source: Path, dry_run: bool = True) -> Dict:
    """Migra un archivo individual."""
    result = {
        'source': str(source),
        'target': None,
        'status': 'skipped',
        'reason': None,
    }

    # Skip certain files
    if source.name in SKIP_FILES:
        result['reason'] = f"Archivo en lista de exclusión: {source.name}"
        return result

    # Extract frontmatter and content
    frontmatter, content = extract_frontmatter(source)

    # Detect domain and type
    domain = detect_domain(source)
    req_type_folder = detect_requirement_type(content, source.name)

    # Construct target path
    target = TARGET_PATH / domain / "requisitos" / req_type_folder / source.name
    result['target'] = str(target)

    # Check if target already exists
    if target.exists():
        result['status'] = 'exists'
        result['reason'] = "Archivo ya existe en destino"
        return result

    # Generate or update frontmatter
    if not frontmatter:
        full_content = generate_frontmatter(source, content, domain, req_type_folder) + content
    else:
        # Keep existing frontmatter but add migration note
        existing_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
        full_content = f"---\n{existing_yaml}---\n\n{content}"

    if not dry_run:
        # Create target directory
        target.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        target.write_text(full_content, encoding='utf-8')
        result['status'] = 'migrated'
        result['reason'] = f"Migrado a {domain}/{req_type_folder}/"
    else:
        result['status'] = 'dry_run'
        result['reason'] = f"Sería migrado a {domain}/{req_type_folder}/"

    return result

def main(dry_run: bool = True):
    """Función principal de migración."""
    print("=" * 70)
    print("🔄 SCRIPT DE MIGRACIÓN DE REQUISITOS LEGACY")
    print("=" * 70)
    print()

    if dry_run:
        print("⚠️  MODO DRY-RUN: No se modificarán archivos")
        print("    Ejecutar con --execute para realizar migración real")
    else:
        print("✅ MODO EJECUCIÓN: Se migrarán archivos")

    print()

    # Collect files to migrate
    files_to_migrate = []
    for legacy_path in LEGACY_PATHS:
        if legacy_path.exists():
            for md_file in legacy_path.rglob('*.md'):
                if md_file.is_file() and md_file.name not in SKIP_FILES:
                    files_to_migrate.append(md_file)

    if not files_to_migrate:
        print("ℹ️  No se encontraron archivos para migrar")
        print()
        print("Archivos excluidos automáticamente:")
        for skip in SKIP_FILES:
            print(f"   - {skip}")
        return

    print(f"📄 Encontrados {len(files_to_migrate)} archivos para analizar")
    print()

    # Migrate files
    results = []
    for source_file in files_to_migrate:
        result = migrate_file(source_file, dry_run=dry_run)
        results.append(result)

    # Report
    print()
    print("=" * 70)
    print("📊 REPORTE DE MIGRACIÓN")
    print("=" * 70)
    print()

    migrated = [r for r in results if r['status'] in ['migrated', 'dry_run']]
    skipped = [r for r in results if r['status'] == 'skipped']
    exists = [r for r in results if r['status'] == 'exists']

    print(f"✅ Archivos a migrar: {len(migrated)}")
    print(f"⏭️  Archivos omitidos: {len(skipped)}")
    print(f"📁 Ya existen en destino: {len(exists)}")
    print()

    if migrated:
        print("📝 Detalles de archivos migrados:")
        for r in migrated:
            print(f"   {Path(r['source']).name}")
            print(f"      → {r['target']}")
            print(f"      {r['reason']}")
            print()

    if skipped:
        print("⏭️  Archivos omitidos:")
        for r in skipped:
            print(f"   {Path(r['source']).name}: {r['reason']}")

    if not dry_run and migrated:
        print()
        print("=" * 70)
        print("✅ MIGRACIÓN COMPLETADA")
        print("=" * 70)
        print()
        print("🔍 PRÓXIMOS PASOS:")
        print("   1. Revisar archivos migrados en docs/implementacion/")
        print("   2. Completar campos marcados como PENDIENTE en frontmatter")
        print("   3. Validar que la trazabilidad es correcta")
        print("   4. Ejecutar: python .github/workflows/scripts/generate_requirements_index.py")
        print("   5. Commit y push de cambios")
        print()

if __name__ == "__main__":
    import sys

    # Check for --execute flag
    execute = "--execute" in sys.argv or "-e" in sys.argv

    main(dry_run=not execute)
