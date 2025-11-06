#!/bin/bash
# Script para limpiar emojis de archivos markdown
# Uso: ./scripts/clean_emojis.sh <directorio>

set -e

if [ -z "$1" ]; then
    echo "Uso: $0 <directorio>"
    exit 1
fi

TARGET_DIR="$1"

if [ ! -d "$TARGET_DIR" ]; then
    echo "ERROR: Directorio no existe: $TARGET_DIR"
    exit 1
fi

echo "[INFO] Limpiando emojis en: $TARGET_DIR"

# Encontrar todos los archivos .md
find "$TARGET_DIR" -type f -name "*.md" | while read -r file; do
    # Hacer backup temporal
    cp "$file" "$file.bak"

    # Reemplazar emojis comunes
    sed -i 's/✅/[x]/g' "$file"          # Checkmark verde -> [x]
    sed -i 's/❌/[ ]/g' "$file"          # X roja -> [ ]
    sed -i 's/✓/[OK]/g' "$file"          # Checkmark -> [OK]
    sed -i 's/✗/[FAIL]/g' "$file"        # X -> [FAIL]
    sed -i 's/⚠️/[WARNING]/g' "$file"    # Warning -> [WARNING]
    sed -i 's/⚠/[WARNING]/g' "$file"     # Warning (sin variante) -> [WARNING]
    sed -i 's/🚀//g' "$file"              # Rocket -> (remover)
    sed -i 's/📝//g' "$file"              # Memo -> (remover)
    sed -i 's/🔧//g' "$file"              # Wrench -> (remover)
    sed -i 's/💡//g' "$file"              # Bulb -> (remover)
    sed -i 's/🔒//g' "$file"              # Lock -> (remover)
    sed -i 's/🔐//g' "$file"              # Lock with key -> (remover)
    sed -i 's/🚨//g' "$file"              # Police light -> (remover)
    sed -i 's/📊//g' "$file"              # Chart -> (remover)
    sed -i 's/📈//g' "$file"              # Chart increasing -> (remover)
    sed -i 's/📉//g' "$file"              # Chart decreasing -> (remover)
    sed -i 's/🎯//g' "$file"              # Target -> (remover)
    sed -i 's/✨//g' "$file"              # Sparkles -> (remover)
    sed -i 's/🔥//g' "$file"              # Fire -> (remover)
    sed -i 's/👍//g' "$file"              # Thumbs up -> (remover)
    sed -i 's/👎//g' "$file"              # Thumbs down -> (remover)
    sed -i 's/⭐//g' "$file"              # Star -> (remover)
    sed -i 's/🌟//g' "$file"              # Glowing star -> (remover)

    # Verificar si hubo cambios
    if ! diff -q "$file" "$file.bak" > /dev/null 2>&1; then
        echo "  [CLEANED] $file"
        rm "$file.bak"
    else
        # No hubo cambios, restaurar backup
        mv "$file.bak" "$file"
    fi
done

echo "[INFO] Limpieza completada"
