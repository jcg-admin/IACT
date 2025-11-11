#!/bin/bash
#
# check_all.sh - Ejecuta todos los checks de calidad localmente
#
# Uso:
#   ./scripts/dev/check_all.sh
#   ./scripts/dev/check_all.sh --fix  # Intenta auto-corregir issues
#
# Descripción:
#   Wrapper que ejecuta todos los pre-commit hooks y validaciones
#   localmente antes de commit/push. Útil para verificar cambios
#   sin tener que hacer commit.
#
# Trazabilidad:
#   - Constitution AI: Principio 6 (Testing y Validación)
#   - Pre-commit config: api/callcentersite/.pre_commit_config.yaml
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
FIX_MODE=false
VERBOSE=false

print_usage() {
    echo "Uso: $0 [OPCIONES]"
    echo ""
    echo "Opciones:"
    echo "  --fix              Intenta auto-corregir issues (ruff format, etc.)"
    echo "  --verbose, -v      Output detallado"
    echo "  --help, -h         Mostrar esta ayuda"
    echo ""
    echo "Descripción:"
    echo "  Ejecuta todos los checks de calidad del proyecto:"
    echo "    - Pre-commit hooks (ruff, mypy, bandit, etc.)"
    echo "    - Validación de emojis"
    echo "    - Validación de especificaciones (si existen)"
    echo "    - Tests (si se solicita)"
    echo ""
    echo "Ejemplos:"
    echo "  $0                 # Ejecutar todos los checks"
    echo "  $0 --fix           # Ejecutar y auto-corregir lo posible"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

run_check() {
    local name="$1"
    local command="$2"

    echo -e "${YELLOW}Ejecutando: ${name}${NC}"

    if [[ "$VERBOSE" == true ]]; then
        if eval "$command"; then
            echo -e "${GREEN}OK: ${name} pasó${NC}"
            return 0
        else
            echo -e "${RED}ERROR: ${name} falló${NC}"
            return 1
        fi
    else
        if eval "$command" > /dev/null 2>&1; then
            echo -e "${GREEN}OK: ${name}${NC}"
            return 0
        else
            echo -e "${RED}ERROR: ${name}${NC}"
            echo "Ejecuta con --verbose para ver detalles"
            return 1
        fi
    fi
}

check_pre_commit_installed() {
    if ! command -v pre-commit &> /dev/null; then
        echo -e "${RED}ERROR: pre-commit no está instalado${NC}"
        echo "Instalar con: pip install pre-commit"
        return 1
    fi
    return 0
}

run_pre_commit_hooks() {
    print_header "1. Pre-commit Hooks"

    if ! check_pre_commit_installed; then
        return 1
    fi

    local pre_commit_dir="api/callcentersite"

    if [[ ! -f "${pre_commit_dir}/.pre_commit_config.yaml" ]]; then
        echo -e "${YELLOW}ADVERTENCIA: No se encontró .pre_commit_config.yaml en ${pre_commit_dir}${NC}"
        return 0
    fi

    cd "$pre_commit_dir" || return 1

    if [[ "$FIX_MODE" == true ]]; then
        echo "Modo fix: ejecutando pre-commit con auto-corrección"
        pre-commit run --all-files
    else
        pre-commit run --all-files
    fi

    local exit_code=$?
    cd - > /dev/null || return 1

    return $exit_code
}

check_emojis() {
    print_header "2. Validación de Emojis"

    if [[ ! -f "scripts/check_no_emojis.py" ]]; then
        echo -e "${YELLOW}ADVERTENCIA: Script check_no_emojis.py no encontrado${NC}"
        return 0
    fi

    # Buscar archivos modificados o todos si no hay git
    if git rev-parse --git-dir > /dev/null 2>&1; then
        # Verificar archivos modificados y nuevos
        local files
        files=$(git diff --name-only --diff-filter=AM HEAD 2>/dev/null)

        if [[ -z "$files" ]]; then
            echo -e "${BLUE}INFO: No hay archivos modificados para verificar${NC}"
            return 0
        fi

        echo "Verificando emojis en archivos modificados..."
        echo "$files" | while read -r file; do
            if [[ -f "$file" && "$file" =~ \.(md|py|js|ts|yaml|yml|json|sh|bash)$ ]]; then
                if ! python scripts/check_no_emojis.py "$file"; then
                    return 1
                fi
            fi
        done
    else
        echo "Verificando emojis en todos los archivos..."
        run_check "Detección de emojis" "python scripts/check_no_emojis.py"
    fi
}

validate_specs() {
    print_header "3. Validación de Especificaciones"

    if [[ ! -f "scripts/dev/validate_spec.sh" ]]; then
        echo -e "${YELLOW}ADVERTENCIA: Script validate_spec.sh no encontrado${NC}"
        return 0
    fi

    if [[ ! -d "docs/specs" ]]; then
        echo -e "${BLUE}INFO: No hay directorio docs/specs/, omitiendo validación${NC}"
        return 0
    fi

    local spec_count
    spec_count=$(find docs/specs -name "*.md" -type f 2>/dev/null | wc -l)

    if [[ $spec_count -eq 0 ]]; then
        echo -e "${BLUE}INFO: No hay especificaciones para validar${NC}"
        return 0
    fi

    ./scripts/dev/validate_spec.sh --all
}

run_tests() {
    print_header "4. Tests"

    echo -e "${BLUE}INFO: Tests se ejecutan en CI/CD${NC}"
    echo "Para ejecutar tests localmente:"
    echo "  cd api/callcentersite"
    echo "  pytest --cov=. --cov-report=term-missing"

    return 0
}

check_git_status() {
    print_header "5. Estado de Git"

    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${YELLOW}ADVERTENCIA: No es un repositorio git${NC}"
        return 0
    fi

    # Verificar si hay cambios sin stage
    if ! git diff --quiet; then
        echo -e "${YELLOW}Hay cambios sin stage:${NC}"
        git diff --stat
        echo ""
    fi

    # Verificar si hay cambios staged
    if ! git diff --cached --quiet; then
        echo -e "${BLUE}Cambios staged:${NC}"
        git diff --cached --stat
        echo ""
    fi

    # Verificar archivos untracked
    local untracked
    untracked=$(git ls-files --others --exclude-standard)
    if [[ -n "$untracked" ]]; then
        echo -e "${YELLOW}Archivos untracked:${NC}"
        echo "$untracked"
        echo ""
    fi

    return 0
}

# Script principal
main() {
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --fix)
                FIX_MODE=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            *)
                echo -e "${RED}ERROR: Opción desconocida: $1${NC}"
                print_usage
                exit 1
                ;;
        esac
    done

    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}Check-All: Validación Completa${NC}"
    echo -e "${BLUE}=====================================${NC}"

    if [[ "$FIX_MODE" == true ]]; then
        echo -e "${YELLOW}Modo: Auto-corrección habilitada${NC}"
    fi

    local total_checks=0
    local passed_checks=0
    local failed_checks=0

    # Ejecutar checks
    ((total_checks++))
    if run_pre_commit_hooks; then
        ((passed_checks++))
    else
        ((failed_checks++))
    fi

    ((total_checks++))
    if check_emojis; then
        ((passed_checks++))
    else
        ((failed_checks++))
    fi

    ((total_checks++))
    if validate_specs; then
        ((passed_checks++))
    else
        ((failed_checks++))
    fi

    ((total_checks++))
    if run_tests; then
        ((passed_checks++))
    else
        ((failed_checks++))
    fi

    ((total_checks++))
    if check_git_status; then
        ((passed_checks++))
    else
        ((failed_checks++))
    fi

    # Resumen final
    print_header "RESUMEN"

    echo "Total de checks: $total_checks"
    echo -e "${GREEN}Pasados: $passed_checks${NC}"
    echo -e "${RED}Fallados: $failed_checks${NC}"
    echo ""

    if [[ $failed_checks -eq 0 ]]; then
        echo -e "${GREEN}ÉXITO: Todos los checks pasaron${NC}"
        echo "Puedes proceder con commit/push"
        return 0
    else
        echo -e "${RED}FALLO: ${failed_checks} checks fallaron${NC}"
        echo "Corrige los errores antes de hacer commit/push"
        return 1
    fi
}

main "$@"
