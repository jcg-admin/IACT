#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - System Preparation Script
# =============================================================================
# Description: Prepare Ubuntu system for database installation
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant provisioning
# Pattern: Idempotent execution, No silent failures
# =============================================================================

set -euo pipefail

# =============================================================================
# SETUP
# =============================================================================

# Obtener directorio del script
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Detect Vagrant environment
if [[ -d "/vagrant" ]]; then
    readonly PROJECT_ROOT="/vagrant"
else
    readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

# Cargar core (que auto-carga logging)
source "${PROJECT_ROOT}/utils/core.sh"

# Cargar modulos adicionales
iact_source_module "validation"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# SYSTEM PREPARATION FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# verify_ubuntu_version
# Description: Verify Ubuntu version is 18.04
# NO SILENT FAILURES: Reports version check results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_ubuntu_version() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando version de Ubuntu"

    if iact_validate_ubuntu_version; then
        iact_log_success "Version de Ubuntu verificada: 18.04 LTS"
        return 0
    else
        iact_log_error "Version de Ubuntu no soportada"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_disk_space
# Description: Verify sufficient disk space
# NO SILENT FAILURES: Reports disk space status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_disk_space() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando espacio en disco"

    local required_gb=10

    if iact_validate_disk_space "$required_gb"; then
        iact_log_success "Espacio en disco suficiente (minimo: ${required_gb}GB)"
        return 0
    else
        iact_log_error "Espacio en disco insuficiente (minimo requerido: ${required_gb}GB)"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_internet_connectivity
# Description: Verify internet connectivity
# NO SILENT FAILURES: Reports connectivity status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_internet_connectivity() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando conectividad a Internet"

    if iact_validate_internet; then
        iact_log_success "Conectividad a Internet verificada"
        return 0
    else
        iact_log_error "No hay conectividad a Internet"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# update_package_cache
# Description: Update APT package cache
# NO SILENT FAILURES: Reports update status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
update_package_cache() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualizando cache de paquetes APT"

    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Cache de paquetes actualizado"
        return 0
    else
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_essential_packages
# Description: Install essential system packages
# NO SILENT FAILURES: Reports installation status
# IDEMPOTENT: APT handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
install_essential_packages() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes esenciales"

    local packages=(
        "curl"
        "wget"
        "gnupg"
        "lsb-release"
        "software-properties-common"
        "apt-transport-https"
        "ca-certificates"
        "build-essential"
        "git"
    )

    iact_log_info "Paquetes a instalar: ${packages[*]}"

    export DEBIAN_FRONTEND=noninteractive

    if apt-get install -y --no-install-recommends "${packages[@]}" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Paquetes esenciales instalados correctamente"
        return 0
    else
        iact_log_error "Error instalando paquetes esenciales"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_essential_commands
# Description: Verify essential commands are available
# NO SILENT FAILURES: Reports verification results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_essential_commands() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando comandos esenciales"

    local commands=(
        "curl"
        "wget"
        "gpg"
        "apt-get"
        "systemctl"
    )

    local missing_commands=()

    for cmd in "${commands[@]}"; do
        if iact_command_exists "$cmd"; then
            iact_log_info "Comando '$cmd' disponible"
        else
            iact_log_warning "Comando '$cmd' no encontrado"
            missing_commands+=("$cmd")
        fi
    done

    if [[ ${#missing_commands[@]} -eq 0 ]]; then
        iact_log_success "Todos los comandos esenciales estan disponibles"
        return 0
    else
        iact_log_error "Comandos faltantes: ${missing_commands[*]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# display_system_info
# Description: Display system information
# NO SILENT FAILURES: Shows complete system status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_system_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion del sistema"

    echo ""
    echo "=================================================================="
    echo "                  INFORMACION DEL SISTEMA"
    echo "=================================================================="
    echo ""
    echo "Sistema Operativo:"
    lsb_release -a 2>/dev/null | grep -E "Description|Release|Codename" || true
    echo ""
    echo "Kernel:"
    uname -r
    echo ""
    echo "Espacio en disco:"
    df -h / | tail -1
    echo ""
    echo "Memoria:"
    free -h | grep "Mem:" || true
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN
# =============================================================================

main() {
    iact_log_header "SYSTEM PREPARATION - UBUNTU 18.04"
    iact_log_info "Preparando sistema para instalacion de bases de datos"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        verify_ubuntu_version
        verify_disk_space
        verify_internet_connectivity
        update_package_cache
        install_essential_packages
        verify_essential_commands
        display_system_info
    )

    # Auto-ejecutar con patron
    local total=${#steps[@]}
    local current=0
    local failed_steps=()

    iact_log_info "Total de pasos a ejecutar: $total"

    for step_func in "${steps[@]}"; do
        ((current++))

        iact_log_info "DEBUG: Ejecutando funcion: $step_func"

        if ! $step_func "$current" "$total"; then
            failed_steps+=("$step_func")
            iact_log_warning "Paso $step_func fallo, continuando..."
        fi
    done

    # Report final results
    echo ""
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Preparacion del sistema completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Sistema listo para instalacion de bases de datos"
        return 0
    else
        iact_log_error "Preparacion completada con ${#failed_steps[@]} error(es):"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Pasos exitosos: $((total - ${#failed_steps[@]}))"
        return 1
    fi
}

# Execute main
main "$@"