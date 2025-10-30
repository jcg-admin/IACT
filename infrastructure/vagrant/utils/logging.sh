#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Logging Utilities
# =============================================================================
# Description: Logging utilities for Vagrant environment
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant-specific logging
# =============================================================================

# Prevenir ejecución directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    exit 1
fi

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

# Detectar project root
if [[ -d "/vagrant" ]]; then
    readonly VAGRANT_LOG_PROJECT_ROOT="/vagrant"
else
    readonly VAGRANT_LOG_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
fi

# Directorio de logs
readonly VAGRANT_LOGS_DIR="${VAGRANT_LOG_PROJECT_ROOT}/infrastructure/logs"

# Colores
readonly VAGRANT_COLOR_RED='\033[0;31m'
readonly VAGRANT_COLOR_GREEN='\033[0;32m'
readonly VAGRANT_COLOR_YELLOW='\033[1;33m'
readonly VAGRANT_COLOR_BLUE='\033[0;34m'
readonly VAGRANT_COLOR_CYAN='\033[0;36m'
readonly VAGRANT_COLOR_RESET='\033[0m'

# Variables globales
VAGRANT_LOG_FILE=""
VAGRANT_LOG_SCRIPT_NAME=""

# =============================================================================
# INICIALIZACIÓN
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_log_init
# Description: Initialize logging for a script
# Arguments: $1 - script name (without extension)
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
vagrant_log_init() {
    local script_name="$1"

    # Crear directorio de logs si no existe
    mkdir -p "$VAGRANT_LOGS_DIR"

    # Configurar archivo de log
    VAGRANT_LOG_SCRIPT_NAME="$script_name"
    VAGRANT_LOG_FILE="${VAGRANT_LOGS_DIR}/${script_name}.log"

    # Crear/limpiar archivo de log
    : > "$VAGRANT_LOG_FILE"

    # Log inicial
    {
        echo "=================================================================="
        echo "Log iniciado: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Script: $script_name"
        echo "Host: $(hostname)"
        echo "User: $(whoami)"
        echo "=================================================================="
        echo ""
    } >> "$VAGRANT_LOG_FILE"

    return 0
}

# -----------------------------------------------------------------------------
# vagrant_log_get_file
# Description: Get current log file path
# Returns: Log file path via stdout
# -----------------------------------------------------------------------------
vagrant_log_get_file() {
    echo "$VAGRANT_LOG_FILE"
}

# =============================================================================
# FUNCIONES DE LOGGING
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_log
# Description: Write a log message
# Arguments: $1 - level, $2 - message
# -----------------------------------------------------------------------------
vagrant_log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log a archivo
    if [[ -n "$VAGRANT_LOG_FILE" ]]; then
        echo "[$timestamp] [$level] $message" >> "$VAGRANT_LOG_FILE"
    fi
}

# -----------------------------------------------------------------------------
# vagrant_log_header
# Description: Print a header message
# Arguments: $@ - header text
# -----------------------------------------------------------------------------
vagrant_log_header() {
    local message="$*"
    echo ""
    echo -e "${VAGRANT_COLOR_CYAN}=================================================================="
    echo -e "$message"
    echo -e "==================================================================${VAGRANT_COLOR_RESET}"
    echo ""

    vagrant_log "HEADER" "$message"
}

# -----------------------------------------------------------------------------
# vagrant_log_step
# Description: Print a step message
# Arguments: $1 - current step, $2 - total steps, $3 - message
# -----------------------------------------------------------------------------
vagrant_log_step() {
    local current="$1"
    local total="$2"
    shift 2
    local message="$*"

    echo ""
    echo -e "${VAGRANT_COLOR_BLUE}[PASO $current/$total] $message${VAGRANT_COLOR_RESET}"
    echo "----------------------------------------------------------------------"

    vagrant_log "STEP" "[$current/$total] $message"
}

# -----------------------------------------------------------------------------
# vagrant_log_info
# Description: Print an info message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
vagrant_log_info() {
    local message="$*"
    echo -e "${VAGRANT_COLOR_CYAN}[INFO]${VAGRANT_COLOR_RESET} $message"
    vagrant_log "INFO" "$message"
}

# -----------------------------------------------------------------------------
# vagrant_log_success
# Description: Print a success message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
vagrant_log_success() {
    local message="$*"
    echo -e "${VAGRANT_COLOR_GREEN}[OK]${VAGRANT_COLOR_RESET} $message"
    vagrant_log "SUCCESS" "$message"
}

# -----------------------------------------------------------------------------
# vagrant_log_warning
# Description: Print a warning message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
vagrant_log_warning() {
    local message="$*"
    echo -e "${VAGRANT_COLOR_YELLOW}[WARNING]${VAGRANT_COLOR_RESET} $message"
    vagrant_log "WARNING" "$message"
}

# -----------------------------------------------------------------------------
# vagrant_log_error
# Description: Print an error message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
vagrant_log_error() {
    local message="$*"
    echo -e "${VAGRANT_COLOR_RED}[ERROR]${VAGRANT_COLOR_RESET} $message" >&2
    vagrant_log "ERROR" "$message"
}

# =============================================================================
# EXPORT
# =============================================================================

export -f vagrant_log_init
export -f vagrant_log_get_file
export -f vagrant_log_header
export -f vagrant_log_step
export -f vagrant_log_info
export -f vagrant_log_success
export -f vagrant_log_warning
export -f vagrant_log_error