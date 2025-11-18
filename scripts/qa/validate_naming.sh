#!/bin/bash
# Script: validate_naming.sh
# Proposito: Validar nomenclatura snake_case en archivos y carpetas
# Uso: ./validate_naming.sh <directorio> [--strict] [--verbose]
# Ejemplo: ./scripts/qa/validate_naming.sh /home/user/IACT/docs/infraestructura

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Help
show_help() {
    cat << EOF
validate_naming.sh - Validador de Nomenclatura

Uso:
    $0 <directorio> [--strict] [--verbose] [--fix]

Opciones:
    -h, --help        Mostrar esta ayuda
    --strict          Modo estricto (rechazar mayusculas)
    --verbose         Mostrar detalles de procesamiento
    --fix             Sugerir correcciones (sin aplicar)

Proposito:
    Verifica que archivos y carpetas sigan convenciones:
    - snake_case: lowercase-with-dashes
    - Excepciones: README, LICENSE, .git*, etc.

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
STRICT=false
VERBOSE=false
FIX=false

# Procesar argumentos adicionales
shift
while [ $# -gt 0 ]; do
    case "$1" in
        --strict) STRICT=true ;;
        --verbose) VERBOSE=true ;;
        --fix) FIX=true ;;
    esac
    shift
done

if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}ERROR: Directorio no existe: $TARGET_DIR${NC}"
    exit 1
fi

echo -e "${GREEN}[INFO] Validando nomenclatura en: $TARGET_DIR${NC}"

VALID_COUNT=0
INVALID_COUNT=0
INVALID_NAMES=""

# Excepciones permitidas (MAYUSCULAS o caracteres especiales)
is_exception() {
    local filename=$1

    # Permitir archivos especiales
    case "$filename" in
        README*)         return 0 ;;
        LICENSE*)        return 0 ;;
        CHANGELOG*)      return 0 ;;
        CONTRIBUTING*)   return 0 ;;
        AUTHORS*)        return 0 ;;
        CONTRIBUTORS*)   return 0 ;;
        HISTORY*)        return 0 ;;
        MANIFEST*)       return 0 ;;
        Makefile*)       return 0 ;;
        Dockerfile*)     return 0 ;;
        docker-compose*) return 0 ;;
        .gitkeep)        return 0 ;;
        .git*)           return 0 ;;
        .env*)           return 0 ;;
        .*)              return 0 ;;
    esac

    # Archivos generados (log, tmp, etc)
    case "$filename" in
        *.log|*.tmp|*.bak) return 0 ;;
    esac

    return 1
}

# Validar nombre
validate_name() {
    local name=$1

    if is_exception "$name"; then
        return 0
    fi

    # Pattern: lowercase, numeros, guiones, puntos
    # Debe empezar y terminar con alphanumerico
    # Puede contener: a-z, 0-9, guiones (-), puntos (.)
    if [[ "$name" =~ ^[a-z0-9]+([a-z0-9._-]*[a-z0-9])?$ ]]; then
        return 0  # Valido
    fi

    return 1  # Invalido
}

# Normalizar nombre (sugerencia de cambio)
suggest_correction() {
    local name=$1

    # Convertir a minusculas
    local corrected=$(echo "$name" | tr '[:upper:]' '[:lower:]')

    # Reemplazar espacios y caracteres especiales con guiones
    corrected=$(echo "$corrected" | sed 's/[^a-z0-9._-]/-/g')

    # Eliminar guiones multiples
    corrected=$(echo "$corrected" | sed 's/-\+/-/g')

    # Eliminar puntos multiples
    corrected=$(echo "$corrected" | sed 's/\.\+/\./g')

    # Eliminar guiones y puntos al inicio/final
    corrected=$(echo "$corrected" | sed 's/^[-\.]*//;s/[-\.]*$//')

    echo "$corrected"
}

# Procesador de archivos y carpetas
process_items() {
    local type=$1
    local find_type=$2

    find "$TARGET_DIR" -type "$find_type" | while read -r item; do
        name=$(basename "$item")

        # Ignorar .git y directorios punto al inicio
        if [[ "$name" == "." || "$name" == ".." ]]; then
            continue
        fi

        if [ "$VERBOSE" = true ]; then
            echo -e "${BLUE}[VALIDANDO]${NC} $name ($type)"
        fi

        if ! validate_name "$name"; then
            INVALID_COUNT=$((INVALID_COUNT + 1))
            suggestion=$(suggest_correction "$name")

            echo -e "${YELLOW}[WARNING]${NC} $item"
            echo -e "  ${BLUE}Sugerencia:${NC} $(dirname "$item")/$suggestion"

            if [ "$FIX" = true ]; then
                echo -e "  ${YELLOW}(Para aplicar: mv \"$item\" \"$(dirname "$item")/$suggestion\")${NC}"
            fi

            INVALID_NAMES="$INVALID_NAMES\n    $item -> $suggestion"
        else
            VALID_COUNT=$((VALID_COUNT + 1))
        fi
    done
}

# Procesar archivos
if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}[INFO] Procesando archivos...${NC}"
fi
process_items "archivo" "f"

# Procesar carpetas (excluir .git)
if [ "$VERBOSE" = true ]; then
    echo -e "${BLUE}[INFO] Procesando carpetas...${NC}"
fi
find "$TARGET_DIR" -type d \( -name ".git" -prune \) -o -type d -print | while read -r dir; do
    name=$(basename "$dir")

    if [[ "$name" == "." || "$name" == ".." ]]; then
        continue
    fi

    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[VALIDANDO]${NC} $name (carpeta)"
    fi

    if ! validate_name "$name"; then
        INVALID_COUNT=$((INVALID_COUNT + 1))
        suggestion=$(suggest_correction "$name")

        echo -e "${YELLOW}[WARNING]${NC} $dir/"
        echo -e "  ${BLUE}Sugerencia:${NC} $(dirname "$dir")/$suggestion/"

        if [ "$FIX" = true ]; then
            echo -e "  ${YELLOW}(Para aplicar: mv \"$dir\" \"$(dirname "$dir")/$suggestion\")${NC}"
        fi

        INVALID_NAMES="$INVALID_NAMES\n    $dir/ -> $suggestion/"
    else
        VALID_COUNT=$((VALID_COUNT + 1))
    fi
done

# Mostrar resumen
echo ""
echo -e "${GREEN}===============================================${NC}"
echo -e "${GREEN}REPORTE DE VALIDACION DE NOMENCLATURA${NC}"
echo -e "${GREEN}===============================================${NC}"

TOTAL=$((VALID_COUNT + INVALID_COUNT))

if [ "$TOTAL" -gt 0 ]; then
    echo -e "${GREEN}Total procesados:${NC} $TOTAL"
    echo -e "${GREEN}Nombres validos:${NC} $VALID_COUNT"

    if [ $INVALID_COUNT -gt 0 ]; then
        echo -e "${RED}Nombres invalidos:${NC} $INVALID_COUNT"
        echo ""
        echo -e "${RED}Detalle de cambios sugeridos:${NC}"
        echo -e "$INVALID_NAMES" | sed 's/^    /  /'
    else
        echo -e "${GREEN}Nombres invalidos:${NC} 0"
    fi
else
    echo -e "${YELLOW}Sin archivos o carpetas procesados${NC}"
fi

echo ""
echo -e "${GREEN}===============================================${NC}"

if [ "$INVALID_COUNT" -gt 0 ]; then
    exit 1
else
    exit 0
fi
