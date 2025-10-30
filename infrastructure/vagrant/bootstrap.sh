#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Bootstrap Script
# =============================================================================
# Description: Main orchestrator for Vagrant provisioning
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant provisioning
# Pattern: Idempotent execution, No silent failures
# =============================================================================

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

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
    readonly PROJECT_ROOT="$SCRIPT_DIR"
fi

# Configuration
readonly LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
readonly DEBUG="${DEBUG:-false}"

# Export variables for child scripts
export LOGS_DIR DEBUG

# Cargar core (que auto-carga logging)
source "${PROJECT_ROOT}/utils/core.sh"

# Cargar modulos adicionales
iact_source_module "validation"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# CONFIGURATION FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# apply_apt_sources
# Description: Apply custom APT sources configuration
# NO SILENT FAILURES: Reports configuration status
# IDEMPOTENT: File copy is idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
apply_apt_sources() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Aplicando configuracion de APT sources"

    local source_file="$PROJECT_ROOT/config/apt/sources.list"
    local target_file="/etc/apt/sources.list"

    if [[ ! -f "$source_file" ]]; then
        iact_log_warning "Archivo de configuracion no encontrado: $source_file"
        return 0  # Non-critical
    fi

    # Backup del archivo original si existe
    if [[ -f "$target_file" ]]; then
        local backup_file="${target_file}.backup.$(date +%Y%m%d_%H%M%S)"
        iact_log_info "Creando backup: $backup_file"
        if ! cp "$target_file" "$backup_file"; then
            iact_log_warning "No se pudo crear backup de sources.list original"
        fi
    fi

    iact_log_info "Copiando configuracion desde: $source_file"
    if cp "$source_file" "$target_file"; then
        iact_log_success "Configuracion de APT sources aplicada"
        return 0
    else
        iact_log_error "Error aplicando configuracion de APT sources"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# apply_dns_configuration
# Description: Apply DNS configuration
# NO SILENT FAILURES: Reports configuration status
# IDEMPOTENT: File copy is idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success (warnings are non-critical)
# -----------------------------------------------------------------------------
apply_dns_configuration() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Aplicando configuracion de DNS"

    # Apply systemd-resolved configuration
    local resolved_source="$PROJECT_ROOT/config/systemd/resolved.conf"
    local resolved_target="/etc/systemd/resolved.conf"

    if [[ -f "$resolved_source" ]]; then
        # Backup del archivo original si existe
        if [[ -f "$resolved_target" ]]; then
            local backup_file="${resolved_target}.backup.$(date +%Y%m%d_%H%M%S)"
            iact_log_info "Creando backup: $backup_file"
            cp "$resolved_target" "$backup_file" 2>/dev/null || true
        fi

        iact_log_info "Aplicando configuracion de systemd-resolved..."
        if cp "$resolved_source" "$resolved_target"; then
            iact_log_success "Configuracion de systemd-resolved aplicada"
        else
            iact_log_warning "Error aplicando configuracion de systemd-resolved"
        fi
    else
        iact_log_warning "Archivo de configuracion no encontrado: $resolved_source"
    fi

    # Apply resolv.conf backup
    local resolv_source="$PROJECT_ROOT/config/network/resolv.conf"
    local resolv_target="/etc/resolv.conf"

    if [[ -f "$resolv_source" ]]; then
        # Backup del archivo original si existe
        if [[ -f "$resolv_target" ]]; then
            local backup_file="${resolv_target}.backup.$(date +%Y%m%d_%H%M%S)"
            iact_log_info "Creando backup: $backup_file"
            cp "$resolv_target" "$backup_file" 2>/dev/null || true
        fi

        iact_log_info "Aplicando configuracion de resolv.conf..."
        if cp "$resolv_source" "$resolv_target"; then
            iact_log_success "Configuracion de resolv.conf aplicada"
        else
            iact_log_warning "Error aplicando configuracion de resolv.conf"
        fi
    else
        iact_log_warning "Archivo de configuracion no encontrado: $resolv_source"
    fi

    # Restart DNS service
    iact_log_info "Reiniciando servicio systemd-resolved..."
    if systemctl restart systemd-resolved 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Servicio systemd-resolved reiniciado"
    else
        iact_log_warning "Error reiniciando systemd-resolved (no critico)"
    fi

    return 0
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

    iact_log_step "$current" "$total" "Actualizando cache de paquetes"

    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Cache de paquetes actualizado correctamente"
        return 0
    else
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# execute_installation_script
# Description: Execute an installation script
# NO SILENT FAILURES: Reports script execution status
# Arguments: $1 - script path, $2 - current step, $3 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
execute_installation_script() {
    local script_path="$1"
    local current="$2"
    local total="$3"
    local script_name
    script_name=$(basename "$script_path")

    iact_log_step "$current" "$total" "Ejecutando: $script_name"

    # Verify script exists
    if [[ ! -f "$script_path" ]]; then
        iact_log_error "Script no encontrado: $script_path"
        return 1
    fi

    # Make script executable
    if ! chmod +x "$script_path"; then
        iact_log_error "No se pueden establecer permisos de ejecucion: $script_path"
        return 1
    fi

    iact_log_info "Ejecutando: $script_path"

    # Execute script and capture result
    if bash "$script_path" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "$script_name completado exitosamente"
        return 0
    else
        local exit_code=$?
        iact_log_error "$script_name fallo con codigo de salida: $exit_code"
        return $exit_code
    fi
}

# -----------------------------------------------------------------------------
# display_bootstrap_header
# Description: Display bootstrap header information
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_bootstrap_header() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de bootstrap"

    echo ""
    echo "=================================================================="
    echo "            MARIADB + POSTGRESQL BOOTSTRAP"
    echo "=================================================================="
    echo ""
    echo "Sistema objetivo: Ubuntu 18.04 LTS (Bionic Beaver)"
    echo "Project Root: $PROJECT_ROOT"
    echo "Logs Directory: $LOGS_DIR"
    echo "Context: $(iact_get_context)"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# -----------------------------------------------------------------------------
# display_credentials_info
# Description: Display database credentials information
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_credentials_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de credenciales"

    echo ""
    echo "=================================================================="
    echo "                  CREDENCIALES DE BASES DE DATOS"
    echo "=================================================================="
    echo ""
    echo "IMPORTANTE: Guarde estas credenciales de forma segura"
    echo ""
    echo "MariaDB:"
    echo "  Usuario: root"
    echo "  Password: \$DB_ROOT_PASSWORD (definido en variables de entorno)"
    echo ""
    echo "PostgreSQL:"
    echo "  Usuario: postgres"
    echo "  Password: \$DB_PASSWORD (definido en variables de entorno)"
    echo ""
    echo "Estas credenciales estan registradas en: $(iact_get_log_file)"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# -----------------------------------------------------------------------------
# display_access_information
# Description: Display access information
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_access_information() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de acceso"

    echo ""
    echo "=================================================================="
    echo "                  INFORMACION DE ACCESO"
    echo "=================================================================="
    echo ""
    echo "Acceso SSH:"
    echo "  vagrant ssh (si usa Vagrant)"
    echo ""
    echo "Bases de datos:"
    echo "  MariaDB: mysql -u root -p"
    echo "  PostgreSQL: psql -U postgres -h localhost"
    echo ""
    echo "Logs:"
    echo "  $(iact_get_log_file)"
    echo ""
    echo "Proyecto:"
    echo "  $PROJECT_ROOT"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN
# =============================================================================

main() {
    iact_log_header "VAGRANT BOOTSTRAP - IACT INFRASTRUCTURE"
    iact_log_info "Iniciando aprovisionamiento de Vagrant"
    iact_log_info "Context: $(iact_get_context)"

    # Define installation scripts
    local scripts=(
        "$PROJECT_ROOT/scripts/system-prepare.sh"
        "$PROJECT_ROOT/scripts/mariadb-install.sh"
        "$PROJECT_ROOT/scripts/postgres-install.sh"
        "$PROJECT_ROOT/scripts/setup-mariadb-database.sh"
        "$PROJECT_ROOT/scripts/setup-postgres-database.sh"
    )

    # Build steps array dynamically
    local steps=(
        display_bootstrap_header
        apply_apt_sources
        apply_dns_configuration
        update_package_cache
    )

    # Add installation scripts to steps
    for script in "${scripts[@]}"; do
        steps+=("execute_installation_script $script")
    done

    # Add final information steps
    steps+=(
        display_credentials_info
        display_access_information
    )

    # Auto-ejecutar con patron
    local total=${#steps[@]}
    local current=0
    local failed_steps=()

    for step_func in "${steps[@]}"; do
        ((current++))

        # Handle scripts with parameters vs regular functions
        if [[ "$step_func" == execute_installation_script* ]]; then
            local script_path
            script_path=$(echo "$step_func" | cut -d' ' -f2-)
            if ! execute_installation_script "$script_path" "$current" "$total"; then
                failed_steps+=("$(basename "$script_path")")
            fi
        else
            if ! $step_func "$current" "$total"; then
                failed_steps+=("$step_func")
            fi
        fi
    done

    # Report final results
    echo ""
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Bootstrap completado exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "MariaDB y PostgreSQL instalados y configurados"
        iact_log_info "Todos los servicios estan en ejecucion"
        return 0
    else
        iact_log_error "Bootstrap completado con ${#failed_steps[@]} error(es):"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Pasos exitosos: $((total - ${#failed_steps[@]}))"
        iact_log_info "Revise los logs para mas detalles: $(iact_get_log_file)"
        return 1
    fi
}

# =============================================================================
# SCRIPT EXECUTION
# =============================================================================

# Ensure script is run with appropriate privileges
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: Este script debe ejecutarse con privilegios de root"
    echo "Intente: sudo $0"
    exit 1
fi

# Execute main function
main "$@"