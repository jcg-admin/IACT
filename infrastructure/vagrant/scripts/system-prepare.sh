#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - System Preparation Script
# =============================================================================
# Description: Prepare Ubuntu 18.04 system for database installation
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
    readonly PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
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
# update_package_cache
# Description: Update APT package cache
# NO SILENT FAILURES: Reports update result explicitly
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
update_package_cache() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualizando cache de paquetes APT"

    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Cache de paquetes actualizado correctamente"
        return 0
    else
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_essential_packages
# Description: Install essential system packages
# NO SILENT FAILURES: Reports each package installation
# IDEMPOTENT: APT handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
install_essential_packages() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes esenciales"

    local packages=(
        "software-properties-common"
        "curl"
        "wget"
        "gnupg2"
        "ca-certificates"
        "lsb-release"
        "apt-transport-https"
        "build-essential"
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
# NO SILENT FAILURES: Reports each command status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if all found, 1 if any missing
# -----------------------------------------------------------------------------
verify_essential_commands() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando comandos esenciales"

    local commands=("curl" "wget" "apt-get" "systemctl" "gpg")
    local missing=()

    for cmd in "${commands[@]}"; do
        if iact_command_exists "$cmd"; then
            iact_log_success "Comando disponible: $cmd"
        else
            iact_log_error "Comando no encontrado: $cmd"
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        iact_log_success "Todos los comandos esenciales disponibles"
        return 0
    else
        iact_log_error "Comandos faltantes: ${missing[*]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_ubuntu_version
# Description: Verify Ubuntu 18.04 (Bionic Beaver)
# NO SILENT FAILURES: Reports OS version explicitly
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if Ubuntu 18.04, 1 otherwise
# -----------------------------------------------------------------------------
verify_ubuntu_version() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando version de Ubuntu"

    if [[ ! -f /etc/os-release ]]; then
        iact_log_error "Archivo /etc/os-release no encontrado"
        return 1
    fi

    source /etc/os-release

    iact_log_info "Sistema operativo: $NAME $VERSION"
    iact_log_info "Codename: $VERSION_CODENAME"

    if [[ "$VERSION_CODENAME" != "bionic" ]]; then
        iact_log_error "Este script requiere Ubuntu 18.04 (Bionic Beaver)"
        iact_log_error "Version detectada: $NAME $VERSION"
        return 1
    fi

    iact_log_success "Ubuntu 18.04 (Bionic Beaver) verificado"
    return 0
}

# -----------------------------------------------------------------------------
# verify_internet_connectivity
# Description: Verify internet connectivity
# NO SILENT FAILURES: Reports connectivity test result
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if connected, 1 otherwise
# -----------------------------------------------------------------------------
verify_internet_connectivity() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando conectividad a Internet"

    local test_hosts=("8.8.8.8" "1.1.1.1")

    for host in "${test_hosts[@]}"; do
        iact_log_info "Probando conectividad a $host..."
        if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
            iact_log_success "Conectividad a Internet verificada (host: $host)"
            return 0
        fi
    done

    iact_log_error "No se pudo verificar conectividad a Internet"
    iact_log_error "Hosts probados: ${test_hosts[*]}"
    return 1
}

# -----------------------------------------------------------------------------
# verify_disk_space
# Description: Verify sufficient disk space
# NO SILENT FAILURES: Reports disk space status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if sufficient space, 1 otherwise
# -----------------------------------------------------------------------------
verify_disk_space() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando espacio en disco"

    local required_gb=5
    local available_gb
    available_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')

    iact_log_info "Espacio disponible: ${available_gb}GB"
    iact_log_info "Espacio requerido: ${required_gb}GB"

    if [[ "$available_gb" -lt "$required_gb" ]]; then
        iact_log_error "Espacio insuficiente en disco"
        iact_log_error "Se requieren al menos ${required_gb}GB, disponibles: ${available_gb}GB"
        return 1
    fi

    iact_log_success "Espacio en disco suficiente: ${available_gb}GB disponibles"
    return 0
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
    echo "                    INFORMACION DEL SISTEMA"
    echo "=================================================================="
    echo ""

    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        echo "Sistema Operativo: $NAME $VERSION"
        echo "Codename: $VERSION_CODENAME"
    fi

    echo "Kernel: $(uname -r)"
    echo "Arquitectura: $(uname -m)"
    echo "Hostname: $(hostname)"

    local available_gb
    available_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    echo "Espacio disponible: ${available_gb}GB"

    local mem_total
    mem_total=$(free -h | awk '/^Mem:/ {print $2}')
    echo "Memoria total: $mem_total"

    echo ""
    echo "Project Root: $PROJECT_ROOT"
    echo "Logs: $(iact_get_log_file)"
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

    for step_func in "${steps[@]}"; do
        ((current++))

        if ! $step_func "$current" "$total"; then
            failed_steps+=("$step_func")
        fi
    done

    # Report final results
    echo ""
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Preparacion del sistema completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Siguiente paso: Instalacion de MariaDB"
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