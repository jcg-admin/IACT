#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Logging Utilities
# =============================================================================
# Description: Logging utilities for DevContainer environment
# Author: IACT Team
# Version: 1.0.0
# Context: DevContainer-specific logging
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
if [[ -n "${WORKSPACE_FOLDER:-}" ]]; then
    readonly IACT_LOG_PROJECT_ROOT="$WORKSPACE_FOLDER"
elif [[ -d "/workspaces" ]]; then
    # Buscar primer directorio en /workspaces
    IACT_LOG_PROJECT_ROOT=$(find /workspaces -maxdepth 1 -type d ! -path /workspaces | head -n 1)
    if [[ -z "$IACT_LOG_PROJECT_ROOT" ]]; then
        IACT_LOG_PROJECT_ROOT="/workspaces"
    fi
    readonly IACT_LOG_PROJECT_ROOT
else
    readonly IACT_LOG_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
fi

# Directorio de logs
readonly IACT_LOGS_DIR="${IACT_LOG_PROJECT_ROOT}/infrastructure/devcontainer/logs"

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
IACT_LOG_INITIALIZED=0

# =============================================================================
# INICIALIZACION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_init_logging
# Description: Initialize logging for a script (idempotent)
# Arguments: $1 - script name (without extension)
# Returns: 0 on success, 1 on failure
# Note: Can be called multiple times safely - only initializes once per script
# -----------------------------------------------------------------------------
iact_init_logging() {
    local script_name="$1"

    if [[ -z "$script_name" ]]; then
        echo "Error: iact_init_logging requiere nombre de script" >&2
        return 1
    fi

    # Si ya está inicializado para este script, no hacer nada (idempotencia)
    if [[ "$IACT_LOG_INITIALIZED" -eq 1 ]] && [[ "$IACT_LOG_SCRIPT_NAME" == "$script_name" ]]; then
        return 0
    fi

    # Crear directorio de logs si no existe
    if ! mkdir -p "$IACT_LOGS_DIR"; then
        echo "Error: No se pudo crear directorio de logs: $IACT_LOGS_DIR" >&2
        return 1
    fi

    # Configurar archivo de log
    IACT_LOG_SCRIPT_NAME="$script_name"
    IACT_LOG_FILE="${IACT_LOGS_DIR}/${script_name}.log"

    # Crear archivo de log si no existe, o append si existe
    if [[ ! -f "$IACT_LOG_FILE" ]]; then
        # Primera vez - crear con header
        {
            echo "=================================================================="
            echo "Log creado: $(date '+%Y-%m-%d %H:%M:%S')"
            echo "Script: $script_name"
            echo "Host: $(hostname)"
            echo "User: $(whoami)"
            echo "Project Root: $IACT_LOG_PROJECT_ROOT"
            echo "=================================================================="
            echo ""
        } > "$IACT_LOG_FILE" 2>/dev/null || {
            echo "Error: No se pudo crear archivo de log: $IACT_LOG_FILE" >&2
            return 1
        }
    else
        # Log existente - agregar separador de sesión
        {
            echo ""
            echo "=================================================================="
            echo "Nueva sesión: $(date '+%Y-%m-%d %H:%M:%S')"
            echo "=================================================================="
            echo ""
        } >> "$IACT_LOG_FILE" 2>/dev/null || {
            echo "Warning: No se pudo escribir en log existente: $IACT_LOG_FILE" >&2
            # No es fatal, podemos continuar sin logging a archivo
        }
    fi

    IACT_LOG_INITIALIZED=1
    return 0
}

# -----------------------------------------------------------------------------
# iact_log_init
# Description: Alias for iact_init_logging (backward compatibility)
# Arguments: $1 - script name (without extension)
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_log_init() {
    iact_init_logging "$@"
}

# -----------------------------------------------------------------------------
# iact_get_log_file
# Description: Get current log file path
# Returns: Log file path via stdout, or empty if not initialized
# -----------------------------------------------------------------------------
iact_get_log_file() {
    if [[ -n "$IACT_LOG_FILE" ]]; then
        echo "$IACT_LOG_FILE"
    else
        echo ""
    fi
}

# -----------------------------------------------------------------------------
# iact_log_get_file
# Description: Alias for iact_get_log_file (backward compatibility)
# Returns: Log file path via stdout
# -----------------------------------------------------------------------------
iact_log_get_file() {
    iact_get_log_file
}

# -----------------------------------------------------------------------------
# iact_is_logging_initialized
# Description: Check if logging is initialized
# Returns: 0 if initialized, 1 otherwise
# -----------------------------------------------------------------------------
iact_is_logging_initialized() {
    [[ "$IACT_LOG_INITIALIZED" -eq 1 ]]
}

# =============================================================================
# FUNCIONES DE LOGGING INTERNAS
# =============================================================================

# -----------------------------------------------------------------------------
# iact_log
# Description: Write a log message to file
# Arguments: $1 - level, $2+ - message
# Note: Fails silently if logging not initialized (graceful degradation)
# -----------------------------------------------------------------------------
iact_log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Log a archivo solo si está inicializado
    if [[ -n "$IACT_LOG_FILE" ]] && [[ -f "$IACT_LOG_FILE" ]]; then
        echo "[$timestamp] [$level] $message" >> "$IACT_LOG_FILE" 2>/dev/null || true
        # No fallar si no puede escribir a log - es mejor continuar
    fi
}

# =============================================================================
# FUNCIONES DE LOGGING PUBLICAS
# =============================================================================

# -----------------------------------------------------------------------------
# iact_log_header
# Description: Print a header message
# Arguments: $@ - header text
# -----------------------------------------------------------------------------
iact_log_header() {
    local message="$*"

    if [[ -z "$message" ]]; then
        echo "Warning: iact_log_header llamado sin mensaje" >&2
        return 0
    fi

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
# Arguments: $1 - current step, $2 - total steps, $3+ - message
# -----------------------------------------------------------------------------
iact_log_step() {
    if [[ $# -lt 3 ]]; then
        echo "Error: iact_log_step requiere al menos 3 argumentos (current, total, message)" >&2
        return 1
    fi

    local current="$1"
    local total="$2"
    shift 2
    local message="$*"

    # Validar que current y total son números
    if ! [[ "$current" =~ ^[0-9]+$ ]] || ! [[ "$total" =~ ^[0-9]+$ ]]; then
        echo "Error: current ($current) y total ($total) deben ser números" >&2
        return 1
    fi

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

    if [[ -z "$message" ]]; then
        return 0
    fi

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

    if [[ -z "$message" ]]; then
        return 0
    fi

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

    if [[ -z "$message" ]]; then
        return 0
    fi

    echo -e "${IACT_COLOR_YELLOW}[WARN]${IACT_COLOR_RESET} $message"
    iact_log "WARNING" "$message"
}

# -----------------------------------------------------------------------------
# iact_log_error
# Description: Print an error message
# Arguments: $@ - message
# Note: Writes to stderr as expected for errors
# -----------------------------------------------------------------------------
iact_log_error() {
    local message="$*"

    if [[ -z "$message" ]]; then
        return 0
    fi

    echo -e "${IACT_COLOR_RED}[ERROR]${IACT_COLOR_RESET} $message" >&2
    iact_log "ERROR" "$message"
}

# -----------------------------------------------------------------------------
# iact_log_separator
# Description: Print a simple separator line
# -----------------------------------------------------------------------------
iact_log_separator() {
    echo "======================================================================"
}

# -----------------------------------------------------------------------------
# iact_log_subseparator
# Description: Print a subsection separator line
# -----------------------------------------------------------------------------
iact_log_subseparator() {
    echo "----------------------------------------------------------------------"
}

# =============================================================================
# UTILIDADES DE LOG
# =============================================================================

# -----------------------------------------------------------------------------
# iact_log_command_output
# Description: Log command output with proper formatting
# Arguments: $1 - command description, $2+ - command to execute
# Returns: Exit code of the command
# Example: iact_log_command_output "Installing packages" apt-get install -y python3
# -----------------------------------------------------------------------------
iact_log_command_output() {
    if [[ $# -lt 2 ]]; then
        echo "Error: iact_log_command_output requiere descripcion y comando" >&2
        return 1
    fi

    local description="$1"
    shift
    local command=("$@")

    iact_log_info "Ejecutando: $description"
    iact_log "COMMAND" "${command[*]}"

    # Ejecutar comando y capturar exit code
    local exit_code=0
    "${command[@]}" 2>&1 | while IFS= read -r line; do
        iact_log "OUTPUT" "$line"
    done
    exit_code=${PIPESTATUS[0]}

    if [[ $exit_code -eq 0 ]]; then
        iact_log_success "$description - completado exitosamente"
    else
        iact_log_error "$description - falló con código $exit_code"
    fi

    return $exit_code
}

# -----------------------------------------------------------------------------
# iact_log_file_operation
# Description: Log a file operation
# Arguments: $1 - operation type, $2 - file path
# Example: iact_log_file_operation "created" "/path/to/file"
# -----------------------------------------------------------------------------
iact_log_file_operation() {
    if [[ $# -lt 2 ]]; then
        echo "Warning: iact_log_file_operation requiere operation y file" >&2
        return 0
    fi

    local operation="$1"
    local file="$2"

    iact_log "FILE_OP" "$operation: $file"
}

# =============================================================================
# EXPORT
# =============================================================================

export -f iact_init_logging
export -f iact_log_init
export -f iact_get_log_file
export -f iact_log_get_file
export -f iact_is_logging_initialized
export -f iact_log_header
export -f iact_log_step
export -f iact_log_info
export -f iact_log_success
export -f iact_log_warning
export -f iact_log_error
export -f iact_log_separator
export -f iact_log_subseparator
export -f iact_log_command_output
export -f iact_log_file_operation