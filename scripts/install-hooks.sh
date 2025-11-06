#!/bin/bash
#
# install-hooks.sh - Instala git hooks del proyecto
#
# Uso:
#   ./scripts/install-hooks.sh
#   ./scripts/install-hooks.sh --uninstall
#
# Descripción:
#   Instala hooks de git personalizados desde .github/hooks/ a .git/hooks/
#   Los hooks instalados mejoran la calidad del código y previenen errores.
#
# Trazabilidad:
#   - Fase 3: Pre-push Validation
#   - Constitution AI: Principio 6 (Testing y Validación)
#

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorios
HOOKS_SOURCE_DIR=".github/hooks"
HOOKS_TARGET_DIR=".git/hooks"

# Hooks disponibles
AVAILABLE_HOOKS=(
    "pre-push"
)

print_usage() {
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --uninstall        Desinstalar hooks del proyecto"
    echo "  --help, -h         Mostrar esta ayuda"
    echo ""
    echo "Descripción:"
    echo "  Instala git hooks personalizados del proyecto IACT."
    echo "  Los hooks mejoran calidad de código y previenen errores comunes."
    echo ""
    echo "Hooks disponibles:"
    echo "  - pre-push: Validaciones antes de push (specs, secrets, emojis, tests)"
    echo ""
}

check_git_repo() {
    if [[ ! -d ".git" ]]; then
        echo -e "${RED}ERROR: No es un repositorio git${NC}"
        echo "Ejecutar este script desde la raíz del repositorio"
        exit 1
    fi
}

check_hooks_source() {
    if [[ ! -d "$HOOKS_SOURCE_DIR" ]]; then
        echo -e "${RED}ERROR: Directorio de hooks no encontrado: $HOOKS_SOURCE_DIR${NC}"
        exit 1
    fi
}

backup_existing_hook() {
    local hook_name="$1"
    local target_path="$HOOKS_TARGET_DIR/$hook_name"

    if [[ -f "$target_path" ]] && [[ ! -L "$target_path" ]]; then
        local backup_path="${target_path}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}Respaldando hook existente: ${backup_path}${NC}"
        mv "$target_path" "$backup_path"
    fi
}

install_hook() {
    local hook_name="$1"
    local source_path="$HOOKS_SOURCE_DIR/${hook_name}.sample"
    local target_path="$HOOKS_TARGET_DIR/$hook_name"

    if [[ ! -f "$source_path" ]]; then
        echo -e "${YELLOW}ADVERTENCIA: Hook source no encontrado: ${source_path}${NC}"
        return 1
    fi

    echo -e "${BLUE}Instalando hook: ${hook_name}${NC}"

    # Backup si existe
    backup_existing_hook "$hook_name"

    # Copiar hook
    cp "$source_path" "$target_path"

    # Hacer ejecutable
    chmod +x "$target_path"

    echo -e "${GREEN}OK: ${hook_name} instalado${NC}"
    return 0
}

install_all_hooks() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Instalando Git Hooks - Proyecto IACT${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    local installed=0
    local failed=0

    for hook in "${AVAILABLE_HOOKS[@]}"; do
        if install_hook "$hook"; then
            ((installed++))
        else
            ((failed++))
        fi
    done

    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Resumen de Instalación${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Hooks instalados: $installed"
    echo "Hooks fallidos: $failed"
    echo ""

    if [[ $failed -eq 0 ]]; then
        echo -e "${GREEN}ÉXITO: Todos los hooks instalados correctamente${NC}"
        echo ""
        echo "Los hooks instalados ejecutarán validaciones automáticas:"
        echo "  - pre-push: Antes de git push"
        echo ""
        echo "Para omitir un hook temporalmente:"
        echo "  git push --no-verify"
        echo ""
        echo -e "${YELLOW}NOTA: Usar --no-verify solo cuando sea absolutamente necesario${NC}"
        return 0
    else
        echo -e "${YELLOW}ADVERTENCIA: Algunos hooks no se instalaron${NC}"
        return 1
    fi
}

uninstall_hook() {
    local hook_name="$1"
    local target_path="$HOOKS_TARGET_DIR/$hook_name"

    if [[ ! -f "$target_path" ]]; then
        echo -e "${YELLOW}Hook no instalado: ${hook_name}${NC}"
        return 0
    fi

    echo -e "${BLUE}Desinstalando hook: ${hook_name}${NC}"

    # Verificar si es nuestro hook (contiene comentario específico)
    if grep -q "proyecto IACT" "$target_path" 2>/dev/null; then
        rm "$target_path"
        echo -e "${GREEN}OK: ${hook_name} desinstalado${NC}"

        # Restaurar backup si existe
        local latest_backup
        latest_backup=$(ls -t "${target_path}.backup."* 2>/dev/null | head -1 || true)
        if [[ -n "$latest_backup" ]]; then
            echo -e "${BLUE}Restaurando backup: ${latest_backup}${NC}"
            mv "$latest_backup" "$target_path"
        fi
    else
        echo -e "${YELLOW}ADVERTENCIA: ${hook_name} no parece ser del proyecto IACT${NC}"
        echo "No se eliminará automáticamente por seguridad"
    fi

    return 0
}

uninstall_all_hooks() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Desinstalando Git Hooks${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    for hook in "${AVAILABLE_HOOKS[@]}"; do
        uninstall_hook "$hook"
    done

    echo ""
    echo -e "${GREEN}Desinstalación completada${NC}"
}

verify_installation() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Verificando Instalación de Hooks${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    for hook in "${AVAILABLE_HOOKS[@]}"; do
        local target_path="$HOOKS_TARGET_DIR/$hook"

        if [[ -f "$target_path" ]]; then
            if [[ -x "$target_path" ]]; then
                echo -e "${GREEN}OK: ${hook} instalado y ejecutable${NC}"
            else
                echo -e "${YELLOW}ADVERTENCIA: ${hook} instalado pero no ejecutable${NC}"
            fi
        else
            echo -e "${RED}ERROR: ${hook} no instalado${NC}"
        fi
    done

    echo ""
}

# Script principal
main() {
    # Parsear argumentos
    case "${1:-}" in
        --uninstall)
            check_git_repo
            uninstall_all_hooks
            exit 0
            ;;
        --verify)
            check_git_repo
            verify_installation
            exit 0
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        "")
            # Instalación normal
            check_git_repo
            check_hooks_source
            install_all_hooks
            exit $?
            ;;
        *)
            echo -e "${RED}ERROR: Opción desconocida: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
