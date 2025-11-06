#!/bin/bash
#
# validate-spec.sh - Valida especificaciones de features contra esquema
#
# Uso:
#   ./scripts/dev/validate-spec.sh [archivo-spec.md]
#   ./scripts/dev/validate-spec.sh --all
#
# Descripción:
#   Valida que especificaciones de features contengan todas las secciones
#   requeridas según la plantilla plantilla_spec.md
#
# Trazabilidad:
#   - Constitution AI: Principio 3 (Trazabilidad Completa)
#   - Plantilla: docs/plantillas/desarrollo/plantilla_spec.md
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Contadores
TOTAL_FILES=0
VALID_FILES=0
INVALID_FILES=0

# Secciones requeridas en una spec
REQUIRED_SECTIONS=(
    "## 1. Resumen Ejecutivo"
    "## 2. Contexto y Motivación"
    "## 3. Requisitos Funcionales"
    "## 4. Requisitos No Funcionales"
    "## 5. Diseño de Solución"
    "## 6. Dependencias"
    "## 7. Plan de Testing"
    "## 8. Plan de Despliegue"
    "## 12. Criterios de Completitud"
)

# Campos de metadata requeridos
REQUIRED_METADATA=(
    "id:"
    "tipo:"
    "version:"
    "fecha_creacion:"
)

print_usage() {
    echo "Uso: $0 [OPCIÓN] [ARCHIVO]"
    echo ""
    echo "Opciones:"
    echo "  --all              Validar todas las specs en docs/specs/"
    echo "  --help, -h         Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 docs/specs/authentication.md"
    echo "  $0 --all"
}

validate_file() {
    local file="$1"
    local errors=0
    local warnings=0

    echo -e "${BLUE}Validando: ${file}${NC}"

    # Verificar que el archivo existe
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}ERROR: Archivo no encontrado: ${file}${NC}"
        return 1
    fi

    # Verificar que es un archivo .md
    if [[ ! "$file" =~ \.md$ ]]; then
        echo -e "${YELLOW}ADVERTENCIA: No es un archivo Markdown (.md)${NC}"
        ((warnings++))
    fi

    # Extraer front matter YAML
    local has_frontmatter=false
    if head -n 1 "$file" | grep -q "^---$"; then
        has_frontmatter=true
    fi

    if [[ "$has_frontmatter" == false ]]; then
        echo -e "${RED}ERROR: Falta front matter YAML (debe empezar con ---)${NC}"
        ((errors++))
    else
        # Validar campos de metadata requeridos
        for field in "${REQUIRED_METADATA[@]}"; do
            if ! grep -q "^${field}" "$file"; then
                echo -e "${RED}ERROR: Falta campo de metadata: ${field}${NC}"
                ((errors++))
            fi
        done
    fi

    # Validar secciones requeridas
    for section in "${REQUIRED_SECTIONS[@]}"; do
        if ! grep -qF "$section" "$file"; then
            echo -e "${RED}ERROR: Falta sección requerida: ${section}${NC}"
            ((errors++))
        fi
    done

    # Validar ID de especificación
    if grep -q "^id: SPEC-" "$file"; then
        echo -e "${GREEN}OK: ID de especificación válido${NC}"
    else
        echo -e "${YELLOW}ADVERTENCIA: ID no sigue formato SPEC-XXX-NNN${NC}"
        ((warnings++))
    fi

    # Validar que tiene criterios de aceptación
    if grep -q "Given\|When\|Then" "$file"; then
        echo -e "${GREEN}OK: Contiene criterios de aceptación (Given-When-Then)${NC}"
    else
        echo -e "${YELLOW}ADVERTENCIA: No se encontraron criterios de aceptación en formato Given-When-Then${NC}"
        ((warnings++))
    fi

    # Validar que tiene trazabilidad
    if grep -q "REQ-\|SPEC-\|ADR-" "$file"; then
        echo -e "${GREEN}OK: Contiene trazabilidad a requisitos/specs/ADRs${NC}"
    else
        echo -e "${YELLOW}ADVERTENCIA: No se encontró trazabilidad (REQ-*, SPEC-*, ADR-*)${NC}"
        ((warnings++))
    fi

    # Verificar emojis (prohibidos)
    if python scripts/check_no_emojis.py "$file" 2>/dev/null; then
        echo -e "${GREEN}OK: Sin emojis detectados${NC}"
    else
        echo -e "${RED}ERROR: Emojis detectados (prohibidos)${NC}"
        ((errors++))
    fi

    echo ""

    if [[ $errors -eq 0 ]]; then
        if [[ $warnings -eq 0 ]]; then
            echo -e "${GREEN}VÁLIDO: Especificación completa sin errores ni advertencias${NC}"
        else
            echo -e "${GREEN}VÁLIDO: Especificación completa (${warnings} advertencias)${NC}"
        fi
        return 0
    else
        echo -e "${RED}INVÁLIDO: ${errors} errores, ${warnings} advertencias${NC}"
        return 1
    fi
}

validate_all() {
    local specs_dir="docs/specs"

    if [[ ! -d "$specs_dir" ]]; then
        echo -e "${YELLOW}ADVERTENCIA: Directorio ${specs_dir} no existe${NC}"
        echo "Creando directorio..."
        mkdir -p "$specs_dir"
        echo -e "${BLUE}INFO: No hay especificaciones para validar${NC}"
        return 0
    fi

    local spec_files
    spec_files=$(find "$specs_dir" -name "*.md" -type f 2>/dev/null)

    if [[ -z "$spec_files" ]]; then
        echo -e "${BLUE}INFO: No se encontraron especificaciones en ${specs_dir}${NC}"
        return 0
    fi

    echo -e "${BLUE}Validando todas las especificaciones en ${specs_dir}${NC}"
    echo ""

    while IFS= read -r file; do
        ((TOTAL_FILES++))
        if validate_file "$file"; then
            ((VALID_FILES++))
        else
            ((INVALID_FILES++))
        fi
        echo "----------------------------------------"
    done <<< "$spec_files"

    echo ""
    echo -e "${BLUE}=== RESUMEN ===${NC}"
    echo "Total de especificaciones: $TOTAL_FILES"
    echo -e "${GREEN}Válidas: $VALID_FILES${NC}"
    echo -e "${RED}Inválidas: $INVALID_FILES${NC}"

    if [[ $INVALID_FILES -eq 0 ]]; then
        return 0
    else
        return 1
    fi
}

# Script principal
main() {
    if [[ $# -eq 0 ]]; then
        echo -e "${RED}ERROR: Falta argumento${NC}"
        print_usage
        exit 1
    fi

    case "$1" in
        --help|-h)
            print_usage
            exit 0
            ;;
        --all)
            validate_all
            exit $?
            ;;
        *)
            validate_file "$1"
            exit $?
            ;;
    esac
}

main "$@"
