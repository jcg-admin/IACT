#!/usr/bin/env bash
#
# script-name.sh - Descripción breve de una línea
#
# Descripción detallada de lo que hace este script
#
# Usage: script-name.sh [OPTIONS] ARGS
# Options:
#   -h, --help     Mostrar este mensaje de ayuda
#   -v, --verbose  Habilitar salida verbose
#
# Examples:
#   script-name.sh --verbose arg1
#
# Dependencies: command1, command2
# Exit Codes:
#   0 - Éxito
#   1 - Error general
#   2 - Argumentos inválidos

set -euo pipefail

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly VERSION="1.0.0"

# Valores por defecto
VERBOSE=false

# -----------------------------------------------------------------------------
# FUNCIONES DE LOGGING
# -----------------------------------------------------------------------------

log_info() {
    printf '[INFO] %s\n' "$*"
}

log_error() {
    printf '[ERROR] %s\n' "$*" >&2
}

log_debug() {
    if [ "$VERBOSE" = true ]; then
        printf '[DEBUG] %s\n' "$*"
    fi
}

log_success() {
    printf '[SUCCESS] %s\n' "$*"
}

# -----------------------------------------------------------------------------
# MANEJO DE ERRORES
# -----------------------------------------------------------------------------

error_handler() {
    local line_no=$1
    log_error "Script falló en línea $line_no"
    exit 1
}

trap 'error_handler ${LINENO}' ERR

CLEANUP_DONE=false

cleanup() {
    if [ "$CLEANUP_DONE" = true ]; then
        return
    fi
    log_debug "Limpiando recursos temporales"
    # Agregar lógica de limpieza aquí
    CLEANUP_DONE=true
}

trap cleanup EXIT
trap 'log_error "Interrumpido por usuario"; cleanup; exit 130' INT
trap 'log_error "Terminado"; cleanup; exit 143' TERM

# -----------------------------------------------------------------------------
# FUNCIONES DE VALIDACIÓN
# -----------------------------------------------------------------------------

require_command() {
    local cmd="${1:?ERROR: Nombre de comando requerido}"
    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_error "Comando requerido no encontrado: $cmd"
        exit 1
    fi
}

require_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_error "Este script requiere privilegios de root"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------

show_help() {
    grep '^#' "$0" | grep -v '#!/' | cut -c 3-
    exit 0
}

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                show_help
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            *)
                log_error "Opción desconocida: $1"
                show_help
                ;;
        esac
    done
}

# -----------------------------------------------------------------------------
# LÓGICA PRINCIPAL
# -----------------------------------------------------------------------------

main() {
    log_info "Iniciando ejecución"

    # Validar dependencias
    require_command "curl"
    require_command "jq"

    # Lógica principal del script
    log_info "Ejecutando tarea principal"

    log_success "Ejecución completada exitosamente"
}

# -----------------------------------------------------------------------------
# PUNTO DE ENTRADA
# -----------------------------------------------------------------------------

parse_args "$@"
main
exit 0
