#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Logging Utilities
# =============================================================================
# Description: Logging utilities for Vagrant environment
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant-specific logging
# =============================================================================

# Prevenir ejecucion directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    exit 1
fi

# =============================================================================
# CONFIGURACION
# =============================================================================

# Detectar project root
if [[ -d "/vagrant" ]]; then
    readonly IACT_LOG_PROJECT_ROOT="/vagrant"
else
    readonly IACT_LOG_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
fi

# Directorio de logs
readonly IACT_LOGS_DIR="${IACT_LOG_PROJECT_ROOT}/logs"

# Colores
readonly IACT_COLOR_RED='\033[0;31m'
readonly IACT_COLOR_GREEN='\033[0;32m'
readonly IACT_COLOR_YELLOW='\033[1;33m'
readonly IACT_COLOR_BLUE='\033[0;34m'
readonly IACT_COLOR_CYAN='\033[0;36m'
readonly IACT_COLOR_RESET='\033[0m'

# Variables globales
IACT_LOG_FILE=""
IACT_LOG_SCRIPT_NAME=""

# =============================================================================
# INICIALIZACION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_init_logging
# Description: Initialize logging for a script
# Arguments: $1 - script name (without extension)
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_init_logging() {
    local script_name="$1"

    # Crear directorio de logs si no existe
    mkdir -p "$IACT_LOGS_DIR"

    # Configurar archivo de log
    IACT_LOG_SCRIPT_NAME="$script_name"
    IACT_LOG_FILE="${IACT_LOGS_DIR}/${script_name}.log"

    # Crear/limpiar archivo de log
    : > "$IACT_LOG_FILE"

    # Log inicial
    {
        echo "=================================================================="
        echo "Log iniciado: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Script: $script_name"
        echo "Host: $(hostname)"
        echo "User: $(whoami)"
        echo "=================================================================="
        echo ""
    } >> "$IACT_LOG_FILE"

    return 0
}

# -----------------------------------------------------------------------------
# iact_log_init
# Description: Alias for iact_init_logging (backward compatibility)
# Arguments: $1 - script name (without extension)
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_log_init() {
    iact_init_logging "$1"
}

# -----------------------------------------------------------------------------
# iact_get_log_file
# Description: Get current log file path
# Returns: Log file path via stdout
# -----------------------------------------------------------------------------
iact_get_log_file() {
    echo "$IACT_LOG_FILE"
}

# -----------------------------------------------------------------------------
# iact_log_get_file
# Description: Alias for iact_get_log_file (backward compatibility)
# Returns: Log file path via stdout
# -----------------------------------------------------------------------------
iact_log_get_file() {
    iact_get_log_file
}

# =============================================================================
# FUNCIONES DE LOGGING
# =============================================================================

# -----------------------------------------------------------------------------
# iact_log
# Description: Write a log message
# Arguments: $1 - level, $2 - message
# -----------------------------------------------------------------------------
iact_log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log a archivo
    if [[ -n "$IACT_LOG_FILE" ]]; then
        echo "[$timestamp] [$level] $message" >> "$IACT_LOG_FILE"
    fi
}

# -----------------------------------------------------------------------------
# iact_log_header
# Description: Print a header message
# Arguments: $@ - header text
# -----------------------------------------------------------------------------
iact_log_header() {
    local message="$*"
    echo ""
    echo -e "${IACT_COLOR_CYAN}=================================================================="
    echo -e "$message"
    echo -e "==================================================================${IACT_COLOR_RESET}"
    echo ""

    iact_log "HEADER" "$message"
}

# -----------------------------------------------------------------------------
# iact_log_step
# Description: Print a step message
# Arguments: $1 - current step, $2 - total steps, $3 - message
# -----------------------------------------------------------------------------
iact_log_step() {
    local current="$1"
    local total="$2"
    shift 2
    local message="$*"

    echo ""
    echo -e "${IACT_COLOR_BLUE}[PASO $current/$total] $message${IACT_COLOR_RESET}"
    echo "----------------------------------------------------------------------"

    iact_log "STEP" "[$current/$total] $message"
}

# -----------------------------------------------------------------------------
# iact_log_info
# Description: Print an info message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
iact_log_info() {
    local message="$*"
    echo -e "${IACT_COLOR_CYAN}[INFO]${IACT_COLOR_RESET} $message"
    iact_log "INFO" "$message"
}

# -----------------------------------------------------------------------------
# iact_log_success
# Description: Print a success message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
iact_log_success() {
    local message="$*"
    echo -e "${IACT_COLOR_GREEN}[OK]${IACT_COLOR_RESET} $message"
    iact_log "SUCCESS" "$message"
}

# -----------------------------------------------------------------------------
# iact_log_warning
# Description: Print a warning message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
iact_log_warning() {
    local message="$*"
    echo -e "${IACT_COLOR_YELLOW}[WARNING]${IACT_COLOR_RESET} $message"
    iact_log "WARNING" "$message"
}

# -----------------------------------------------------------------------------
# iact_log_error
# Description: Print an error message
# Arguments: $@ - message
# -----------------------------------------------------------------------------
iact_log_error() {
    local message="$*"
    echo -e "${IACT_COLOR_RED}[ERROR]${IACT_COLOR_RESET} $message" >&2
    iact_log "ERROR" "$message"
}

# =============================================================================
# EXPORT
# =============================================================================

export -f iact_init_logging
export -f iact_log_init
export -f iact_get_log_file
export -f iact_log_get_file
export -f iact_log_header
export -f iact_log_step
export -f iact_log_info
export -f iact_log_success
export -f iact_log_warning
export -f iact_log_error