#!/usr/bin/env python3
"""
Validador de Frontmatter YAML en Requisitos
Verifica que todos los requisitos tengan frontmatter válido
"""

import re
import yaml
from pathlib import Path

IMPL_PATH = Path("docs/implementacion")
REQUIRED_FIELDS = ['id', 'tipo', 'titulo', 'dominio', 'owner', 'estado']

def validate_file(filepath):
    """Valida un archivo de requisito."""
    try:
        content = filepath.read_text(encoding='utf-8')

        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {
                'valid': False,
                'error': 'No tiene frontmatter YAML',
                'missing_fields': REQUIRED_FIELDS
            }

        # Parse YAML
        try:
            frontmatter = yaml.safe_load(match.group(1))
        except yaml.YAMLError as e:
            return {
                'valid': False,
                'error': f'YAML inválido: {str(e)}',
                'missing_fields': []
            }

        # Check required fields
        missing = [field for field in REQUIRED_FIELDS if field not in frontmatter]

        if missing:
            return {
                'valid': False,
                'error': 'Faltan campos obligatorios',
                'missing_fields': missing
            }

        return {
            'valid': True,
            'error': None,
            'missing_fields': []
        }

    except Exception as e:
        return {
            'valid': False,
            'error': f'Error leyendo archivo: {str(e)}',
            'missing_fields': []
        }

def main():
    print("=" * 70)
    print("🔍 VALIDADOR DE FRONTMATTER YAML")
    print("=" * 70)
    print()

    if not IMPL_PATH.exists():
        print(f"❌ Error: No existe {IMPL_PATH}")
        return

    # Find all requirement files
    files = []
    for md_file in IMPL_PATH.rglob('*.md'):
        if md_file.name not in ['README.md', 'readme.md'] and not md_file.name.startswith('_'):
            files.append(md_file)

    if not files:
        print("ℹ️  No se encontraron archivos de requisitos")
        print()
        print("Los requisitos deben estar en:")
        print("  - docs/implementacion/backend/requisitos/")
        print("  - docs/implementacion/frontend/requisitos/")
        print("  - docs/implementacion/infrastructure/requisitos/")
        return

    print(f"📄 Validando {len(files)} archivos...")
    print()

    valid_count = 0
    invalid_count = 0
    errors = []

    for filepath in files:
        result = validate_file(filepath)

        if result['valid']:
            valid_count += 1
            print(f"✅ {filepath.relative_to('docs')}")
        else:
            invalid_count += 1
            print(f"❌ {filepath.relative_to('docs')}")
            print(f"   Error: {result['error']}")
            if result['missing_fields']:
                print(f"   Faltan: {', '.join(result['missing_fields'])}")
            errors.append({
                'file': filepath,
                'result': result
            })

    print()
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"✅ Válidos:   {valid_count}")
    print(f"❌ Inválidos: {invalid_count}")
    print()

    if invalid_count > 0:
        print("⚠️  Archivos con errores:")
        for error in errors:
            print(f"   - {error['file'].relative_to('docs')}")
        print()
        print("Campos obligatorios:")
        for field in REQUIRED_FIELDS:
            print(f"   - {field}")
        print()
        print("Consulta las plantillas en: docs/plantillas/")
    else:
        print("🎉 Todos los requisitos tienen frontmatter válido!")

    print()

if __name__ == "__main__":
    main()
