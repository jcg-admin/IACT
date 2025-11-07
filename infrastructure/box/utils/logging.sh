#!/bin/bash

# ============================================================================
# LOGGING UTILITIES
# ============================================================================
# Propósito: Estilo uniforme, trazabilidad y claridad en todos los scripts
# Uso: source utils/logging.sh
# ============================================================================

log_info()    { echo -e "[INFO]    $*"; }
log_warn()    { echo -e "[WARNING] $*"; }
log_error()   { echo -e "[ERROR]   $*" >&2; }
log_success() { echo -e "[OK]      $*"; }

log_header() {
    echo -e "\n========== $* =========="
}

log_box() {
    local msg="$1"
    echo "======================================"
    echo "$msg"
    echo "======================================"
}

log_step() {
    echo -e "\n--> Paso $1: $2"
}

log_summary_start() { echo -e "\n--- RESUMEN FINAL ---"; }
log_summary_item()  { printf "  %-20s: %s\n" "$1" "$2"; }
log_summary_end()   { echo "------------------------"; }

log_confirm() {
    local prompt="${1:-¿Continuar?} [y/N]: "
    read -rp "$prompt" response
    [[ "$response" =~ ^[Yy]$ ]]
}
