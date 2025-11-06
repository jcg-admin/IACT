#!/usr/bin/env python3
"""
Script para detectar emojis en archivos del proyecto.

Este script se ejecuta como pre-commit hook para prevenir
el uso de emojis en documentación y código.

Uso:
    python scripts/check_no_emojis.py [archivos...]
    python scripts/check_no_emojis.py --all

Exit codes:
    0: No se encontraron emojis
    1: Se encontraron emojis (falla el hook)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


# Rangos Unicode de emojis más comunes
EMOJI_PATTERNS = [
    r'[\U0001F600-\U0001F64F]',  # Emoticons
    r'[\U0001F300-\U0001F5FF]',  # Símbolos y pictogramas
    r'[\U0001F680-\U0001F6FF]',  # Transporte y símbolos de mapa
    r'[\U0001F1E0-\U0001F1FF]',  # Banderas
    r'[\U00002702-\U000027B0]',  # Dingbats
    r'[\U000024C2-\U0001F251]',  # Símbolos y caracteres varios
    r'[\U0001F900-\U0001F9FF]',  # Símbolos y pictogramas suplementarios
    r'[\U0001FA00-\U0001FA6F]',  # Símbolos extendidos-A
    r'[\U00002600-\U000026FF]',  # Símbolos varios
    r'[\U0001F170-\U0001F189]',  # Símbolos alfanuméricos encerrados suplementarios
]

# Combinar todos los patrones
EMOJI_REGEX = re.compile('|'.join(EMOJI_PATTERNS))

# Emojis comunes adicionales (algunos pueden no estar en rangos Unicode)
COMMON_EMOJIS = [
    '✅', '❌', '⚠️', '🚀', '🔧', '📝', '💡', '🚨', '🔒', '🔐',
    '👍', '👎', '✓', '✗', '♻️', '🎯', '🏆', '📊', '📈', '📉',
    '🔴', '🟢', '🟡', '🔵', '⚪', '⚫', '🟠', '🟣', '🟤',
]

# Extensiones de archivo a validar
VALID_EXTENSIONS = {
    '.md', '.txt', '.py', '.js', '.ts', '.jsx', '.tsx',
    '.yaml', '.yml', '.json', '.sh', '.bash'
}

# Directorios a excluir
EXCLUDE_DIRS = {
    '.git', '.venv', 'venv', 'node_modules', '__pycache__',
    '.pytest_cache', 'htmlcov', '.mypy_cache', 'dist', 'build'
}


def detect_emojis_in_line(line: str, line_num: int) -> List[Tuple[int, str, str]]:
    """
    Detectar emojis en una línea de texto.

    Args:
        line: Línea de texto a analizar.
        line_num: Número de línea en el archivo.

    Returns:
        Lista de tuplas (line_num, emoji, contexto)
    """
    findings = []

    # Buscar con regex
    matches = EMOJI_REGEX.finditer(line)
    for match in matches:
        emoji = match.group()
        context = line.strip()
        findings.append((line_num, emoji, context))

    # Buscar emojis comunes específicos
    for emoji in COMMON_EMOJIS:
        if emoji in line:
            context = line.strip()
            findings.append((line_num, emoji, context))

    return findings


def check_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """
    Verificar un archivo en busca de emojis.

    Args:
        file_path: Ruta del archivo a verificar.

    Returns:
        Lista de emojis encontrados con su ubicación.
    """
    findings = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                emojis = detect_emojis_in_line(line, line_num)
                findings.extend(emojis)
    except UnicodeDecodeError:
        # Archivo binario, skip
        pass
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}", file=sys.stderr)

    return findings


def should_check_file(file_path: Path) -> bool:
    """
    Determinar si un archivo debe ser verificado.

    Args:
        file_path: Ruta del archivo.

    Returns:
        True si el archivo debe verificarse.
    """
    # Verificar extensión
    if file_path.suffix not in VALID_EXTENSIONS:
        return False

    # Verificar directorios excluidos
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False

    return True


def main():
    """Función principal."""
    if len(sys.argv) < 2:
        print("Uso: python scripts/check_no_emojis.py <archivos...>")
        print("     python scripts/check_no_emojis.py --all")
        sys.exit(1)

    files_to_check = []

    if sys.argv[1] == '--all':
        # Verificar todos los archivos del proyecto
        project_root = Path(__file__).parent.parent
        for file_path in project_root.rglob('*'):
            if file_path.is_file() and should_check_file(file_path):
                files_to_check.append(file_path)
    else:
        # Verificar archivos específicos (desde git staged)
        for arg in sys.argv[1:]:
            file_path = Path(arg)
            if file_path.exists() and file_path.is_file() and should_check_file(file_path):
                files_to_check.append(file_path)

    if not files_to_check:
        print("No hay archivos para verificar.")
        sys.exit(0)

    total_emojis = 0
    files_with_emojis = []

    for file_path in files_to_check:
        findings = check_file(file_path)
        if findings:
            files_with_emojis.append(file_path)
            total_emojis += len(findings)

            print(f"\nERROR: Emojis detectados en {file_path}")
            print("=" * 70)
            for line_num, emoji, context in findings:
                print(f"  Línea {line_num}: {emoji}")
                print(f"    Contexto: {context[:60]}...")

    if total_emojis > 0:
        print("\n" + "=" * 70)
        print(f"TOTAL: {total_emojis} emojis encontrados en {len(files_with_emojis)} archivos")
        print("=" * 70)
        print("\nEl proyecto NO permite emojis en documentación o código.")
        print("Ver: docs/gobernanza/GUIA_ESTILO.md para más información.")
        print("\nAlternativas recomendadas:")
        print("  - En lugar de ✅ usar: [x] o 'Completado'")
        print("  - En lugar de ❌ usar: [ ] o 'Pendiente'")
        print("  - En lugar de 🚀 usar: simplemente omitir")
        print("  - En lugar de ⚠️  usar: 'ADVERTENCIA:' o 'Nota:'")
        sys.exit(1)
    else:
        print(f"OK: No se encontraron emojis en {len(files_to_check)} archivos verificados.")
        sys.exit(0)


if __name__ == '__main__':
    main()
