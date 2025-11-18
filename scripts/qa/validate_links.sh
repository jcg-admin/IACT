#!/bin/bash
# Script: validate_links.sh
# Proposito: Validar enlaces markdown en archivos .md
# Uso: ./validate_links.sh <directorio>
# Ejemplo: ./scripts/qa/validate_links.sh /home/user/IACT/docs/infraestructura

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Help
show_help() {
    cat << EOF
validate_links.sh - Validador de Enlaces Markdown

Uso:
    $0 <directorio> [--json] [--verbose]

Opciones:
    -h, --help          Mostrar esta ayuda
    --json              Output en formato JSON
    --verbose           Mostrar detalles de procesamiento
    --exclude-external  Ignorar enlaces externos (http, https, etc)

Proposito:
    Busca todos los enlaces markdown [texto](ruta) en archivos .md
    y verifica que las rutas apunten a archivos que existen.

Ejemplo:
    $0 /home/user/IACT/docs/infraestructura
    $0 /home/user/IACT/docs/infraestructura --verbose

EOF
}

if [ -z "$1" ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

TARGET_DIR="$1"
VERBOSE=false
JSON_OUTPUT=false
EXCLUDE_EXTERNAL=false

# Procesar argumentos adicionales
shift
while [ $# -gt 0 ]; do
    case "$1" in
        --verbose) VERBOSE=true ;;
        --json) JSON_OUTPUT=true ;;
        --exclude-external) EXCLUDE_EXTERNAL=true ;;
    esac
    shift
done

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}ERROR: Directorio no existe: $TARGET_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}[INFO] Validando enlaces en: $TARGET_DIR${NC}"

TOTAL_FILES=0
VALID_LINKS=0
BROKEN_LINKS=0
EXTERNAL_LINKS=0
ANCHOR_LINKS=0
BROKEN_LINKS_LIST=""
PROCESSED_FILES=""

# Procesar cada archivo markdown
while IFS= read -r file; do
    TOTAL_FILES=$((TOTAL_FILES + 1))
    PROCESSED_FILES="$PROCESSED_FILES\n    $file"

    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[PROCESANDO]${NC} $file"
    fi

    # Extraer enlaces markdown: [texto](ruta)
    # Pattern: [cualquier cosa](ruta)
    grep -oP '\[.*?\]\(\K[^)]+' "$file" 2>/dev/null || true | while read -r link; do
        [ -z "$link" ] && continue

        # Ignorar enlaces externos (http, https, mailto, ftp)
        if [[ "$link" =~ ^(http|https|mailto|ftp):// ]]; then
            if [ "$EXCLUDE_EXTERNAL" = false ]; then
                EXTERNAL_LINKS=$((EXTERNAL_LINKS + 1))
            fi
            [ "$VERBOSE" = true ] && echo -e "  ${YELLOW}[EXTERNAL]${NC} $link"
            continue
        fi

        # Ignorar enlaces a anclas internas (#)
        if [[ "$link" =~ ^#.* ]]; then
            ANCHOR_LINKS=$((ANCHOR_LINKS + 1))
            [ "$VERBOSE" = true ] && echo -e "  ${BLUE}[ANCHOR]${NC} $link"
            continue
        fi

        # Enlaces internos - validar que archivo existe
        file_dir=$(dirname "$file")

        # Resolver ruta relativa
        if [ -f "$file_dir/$link" ]; then
            VALID_LINKS=$((VALID_LINKS + 1))
            [ "$VERBOSE" = true ] && echo -e "  ${GREEN}[OK]${NC} $link"
        else
            BROKEN_LINKS=$((BROKEN_LINKS + 1))
            BROKEN_LINKS_LIST="$BROKEN_LINKS_LIST\n    $file -> $link"
            [ "$VERBOSE" = true ] && echo -e "  ${RED}[BROKEN]${NC} $link"
        fi
    done
done < <(find "$TARGET_DIR" -type f -name "*.md")

# Mostrar resultados
echo ""
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}REPORTE DE VALIDACION DE ENLACES${NC}"
echo -e "${GREEN}===============================================${NC}"

if [ "$JSON_OUTPUT" = true ]; then
    cat << EOF
{
  "timestamp": "$(date -Iseconds)",
  "directory": "$TARGET_DIR",
  "summary": {
    "total_files": $TOTAL_FILES,
    "valid_links": $VALID_LINKS,
    "broken_links": $BROKEN_LINKS,
    "external_links": $EXTERNAL_LINKS,
    "anchor_links": $ANCHOR_LINKS
  },
  "broken_links": [
EOF
    if [ -n "$BROKEN_LINKS_LIST" ]; then
        echo "$BROKEN_LINKS_LIST" | sed 's/^    //' | while read -r line; do
            [ -n "$line" ] && echo "    \"$line\","
        done | sed '$ s/,$//'
    fi
    cat << EOF
  ]
}
EOF
else
    echo -e "${GREEN}Archivos procesados:${NC} $TOTAL_FILES"
    echo -e "${GREEN}Enlaces validos:${NC} $VALID_LINKS"
    if [ $BROKEN_LINKS -gt 0 ]; then
        echo -e "${RED}Enlaces rotos:${NC} $BROKEN_LINKS"
        echo -e "${RED}Detalle:${NC}"
        echo "$BROKEN_LINKS_LIST" | sed 's/^    /  - /'
    else
        echo -e "${GREEN}Enlaces rotos:${NC} 0"
    fi
    echo -e "${YELLOW}Enlaces externos:${NC} $EXTERNAL_LINKS"
    echo -e "${BLUE}Enlaces a anclas:${NC} $ANCHOR_LINKS"
fi

echo ""
echo -e "${GREEN}===============================================${NC}"

# Retornar error si hay enlaces rotos
if [ $BROKEN_LINKS -gt 0 ]; then
    exit 1
else
    exit 0
fi
