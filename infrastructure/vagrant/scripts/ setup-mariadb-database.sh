#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - MariaDB Database Setup
# =============================================================================
# Description: Create and configure MariaDB application database
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
source "${PROJECT_ROOT}/infrastructure/utils/core.sh"

# Cargar módulos adicionales
iact_source_module "validation"
iact_source_module "database"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# Database configuration (with defaults)
readonly IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
readonly IVR_DB_USER="${IVR_DB_USER:-django_user}"
readonly IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-django_pass}"
readonly DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"

# =============================================================================
# MARIADB DATABASE SETUP FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# wait_for_mariadb_service
# Description: Wait for MariaDB service to be ready
# NO SILENT FAILURES: Reports wait time and status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on timeout
# -----------------------------------------------------------------------------
wait_for_mariadb_service() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Esperando servicio MariaDB"

    local max_wait=60
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
            iact_log_success "MariaDB disponible despues de ${counter}s"
            return 0
        fi

        sleep 1
        ((counter++))

        if [[ $((counter % 10)) -eq 0 ]]; then
            iact_log_info "Esperando MariaDB... ${counter}s/${max_wait}s"
        fi
    done

    iact_log_error "MariaDB no respondio despues de ${max_wait}s"
    return 1
}

# -----------------------------------------------------------------------------
# check_database_exists
# Description: Check if database already exists
# NO SILENT FAILURES: Reports existence status
# IDEMPOTENT: Safe to run multiple times
# Arguments: None
# Returns: 0 if exists, 1 if not exists
# -----------------------------------------------------------------------------
check_database_exists() {
    local db_count
    db_count=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='$IVR_DB_NAME';" 2>/dev/null | tail -n 1)

    if [[ "$db_count" -eq 1 ]]; then
        return 0
    else
        return 1
    fi
}

# -----------------------------------------------------------------------------
# create_database
# Description: Create MariaDB database
# NO SILENT FAILURES: Reports creation status
# IDEMPOTENT: Checks if database exists before creating
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
create_database() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Creando base de datos: $IVR_DB_NAME"

    # Check if database already exists
    if check_database_exists; then
        iact_log_info "Base de datos '$IVR_DB_NAME' ya existe"
        return 0
    fi

    iact_log_info "Creando base de datos '$IVR_DB_NAME'..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS \`$IVR_DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Base de datos '$IVR_DB_NAME' creada"
        return 0
    else
        iact_log_error "Error creando base de datos '$IVR_DB_NAME'"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# check_user_exists
# Description: Check if database user already exists
# NO SILENT FAILURES: Reports user existence status
# IDEMPOTENT: Safe to run multiple times
# Arguments: None
# Returns: 0 if exists, 1 if not exists
# -----------------------------------------------------------------------------
check_user_exists() {
    local user_count
    user_count=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT COUNT(*) FROM mysql.user WHERE User='$IVR_DB_USER';" 2>/dev/null | tail -n 1)

    if [[ "$user_count" -gt 0 ]]; then
        return 0
    else
        return 1
    fi
}

# -----------------------------------------------------------------------------
# create_database_user
# Description: Create database user with privileges
# NO SILENT FAILURES: Reports user creation status
# IDEMPOTENT: Checks if user exists, updates privileges if needed
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
create_database_user() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando usuario: $IVR_DB_USER"

    # Check if user already exists
    if check_user_exists; then
        iact_log_info "Usuario '$IVR_DB_USER' ya existe, actualizando privilegios..."
    else
        iact_log_info "Creando usuario '$IVR_DB_USER'..."
        if ! mysql -u root -p"$DB_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS '$IVR_DB_USER'@'%' IDENTIFIED BY '$IVR_DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_error "Error creando usuario '$IVR_DB_USER'"
            return 1
        fi
    fi

    # Grant privileges
    iact_log_info "Otorgando privilegios a '$IVR_DB_USER' en '$IVR_DB_NAME'..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON \`$IVR_DB_NAME\`.* TO '$IVR_DB_USER'@'%';" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Privilegios otorgados a '$IVR_DB_USER'"
    else
        iact_log_error "Error otorgando privilegios"
        return 1
    fi

    # Flush privileges
    iact_log_info "Aplicando cambios de privilegios..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Privilegios actualizados"
        return 0
    else
        iact_log_error "Error aplicando privilegios"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_database_setup
# Description: Verify database and user configuration
# NO SILENT FAILURES: Reports verification results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_database_setup() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando configuracion de MariaDB"

    # Verify database exists
    if ! check_database_exists; then
        iact_log_error "Base de datos '$IVR_DB_NAME' no existe"
        return 1
    fi
    iact_log_success "Base de datos '$IVR_DB_NAME' existe"

    # Verify user exists
    if ! check_user_exists; then
        iact_log_error "Usuario '$IVR_DB_USER' no existe"
        return 1
    fi
    iact_log_success "Usuario '$IVR_DB_USER' existe"

    # Test user connection
    iact_log_info "Probando conexion con usuario '$IVR_DB_USER'..."
    if mysql -u "$IVR_DB_USER" -p"$IVR_DB_PASSWORD" -e "USE \`$IVR_DB_NAME\`; SELECT 1;" >/dev/null 2>&1; then
        iact_log_success "Conexion con '$IVR_DB_USER' exitosa"
        return 0
    else
        iact_log_error "No se puede conectar con usuario '$IVR_DB_USER'"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# display_mariadb_info
# Description: Display MariaDB setup information
# NO SILENT FAILURES: Shows complete configuration
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_mariadb_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de configuracion"

    echo ""
    echo "=================================================================="
    echo "           CONFIGURACION DE BASE DE DATOS MARIADB"
    echo "=================================================================="
    echo ""
    echo "Base de datos: $IVR_DB_NAME"
    echo "Usuario: $IVR_DB_USER"
    echo "Password: $IVR_DB_PASSWORD"
    echo ""
    echo "Comando de conexion:"
    echo "  mysql -u $IVR_DB_USER -p'$IVR_DB_PASSWORD' $IVR_DB_NAME"
    echo ""
    echo "Charset: utf8mb4"
    echo "Collation: utf8mb4_unicode_ci"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN
# =============================================================================

main() {
    iact_log_header "MARIADB DATABASE SETUP - VAGRANT"
    iact_log_info "Configurando base de datos de aplicacion: $IVR_DB_NAME"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        wait_for_mariadb_service
        create_database
        create_database_user
        verify_database_setup
        display_mariadb_info
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
        iact_log_success "Configuracion de MariaDB completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Base de datos '$IVR_DB_NAME' lista para usar"
        return 0
    else
        iact_log_error "Configuracion completada con ${#failed_steps[@]} error(es):"
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