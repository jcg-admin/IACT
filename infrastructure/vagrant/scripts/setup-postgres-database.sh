#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - PostgreSQL Database Setup
# =============================================================================
# Description: Create and configure PostgreSQL application database
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
iact_source_module "database"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# Database configuration (with defaults)
readonly DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
readonly DJANGO_DB_USER="${DJANGO_DB_USER:-django_user}"
readonly DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-django_pass}"
readonly DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"

# =============================================================================
# POSTGRESQL DATABASE SETUP FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# wait_for_postgres_service
# Description: Wait for PostgreSQL service to be ready
# NO SILENT FAILURES: Reports wait time and status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on timeout
# -----------------------------------------------------------------------------
wait_for_postgres_service() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Esperando servicio PostgreSQL"

    local max_wait=60
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
            iact_log_success "PostgreSQL disponible despues de ${counter}s"
            return 0
        fi

        sleep 1
        ((counter++))

        if [[ $((counter % 10)) -eq 0 ]]; then
            iact_log_info "Esperando PostgreSQL... ${counter}s/${max_wait}s"
        fi
    done

    iact_log_error "PostgreSQL no respondio despues de ${max_wait}s"
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
    db_count=$(PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -tAc "SELECT COUNT(*) FROM pg_database WHERE datname='$DJANGO_DB_NAME';" 2>/dev/null)

    if [[ "$db_count" -eq 1 ]]; then
        return 0
    else
        return 1
    fi
}

# -----------------------------------------------------------------------------
# create_database
# Description: Create PostgreSQL database
# NO SILENT FAILURES: Reports creation status
# IDEMPOTENT: Checks if database exists before creating
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
create_database() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Creando base de datos: $DJANGO_DB_NAME"

    # Check if database already exists
    if check_database_exists; then
        iact_log_info "Base de datos '$DJANGO_DB_NAME' ya existe"
        return 0
    fi

    iact_log_info "Creando base de datos '$DJANGO_DB_NAME'..."
    if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "CREATE DATABASE $DJANGO_DB_NAME WITH ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8' TEMPLATE=template0;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Base de datos '$DJANGO_DB_NAME' creada"
        return 0
    else
        iact_log_error "Error creando base de datos '$DJANGO_DB_NAME'"
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
    user_count=$(PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -tAc "SELECT COUNT(*) FROM pg_user WHERE usename='$DJANGO_DB_USER';" 2>/dev/null)

    if [[ "$user_count" -eq 1 ]]; then
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

    iact_log_step "$current" "$total" "Configurando usuario: $DJANGO_DB_USER"

    # Check if user already exists
    if check_user_exists; then
        iact_log_info "Usuario '$DJANGO_DB_USER' ya existe, actualizando password..."
        if ! PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "ALTER USER $DJANGO_DB_USER WITH PASSWORD '$DJANGO_DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_error "Error actualizando password de '$DJANGO_DB_USER'"
            return 1
        fi
    else
        iact_log_info "Creando usuario '$DJANGO_DB_USER'..."
        if ! PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "CREATE USER $DJANGO_DB_USER WITH PASSWORD '$DJANGO_DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_error "Error creando usuario '$DJANGO_DB_USER'"
            return 1
        fi
    fi

    # Grant privileges
    iact_log_info "Otorgando privilegios a '$DJANGO_DB_USER' en '$DJANGO_DB_NAME'..."
    if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "GRANT ALL PRIVILEGES ON DATABASE $DJANGO_DB_NAME TO $DJANGO_DB_USER;" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Privilegios otorgados a '$DJANGO_DB_USER'"
        return 0
    else
        iact_log_error "Error otorgando privilegios"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# check_extension_exists
# Description: Check if a PostgreSQL extension exists
# Arguments: $1 - extension name
# Returns: 0 if exists, 1 if not exists
# -----------------------------------------------------------------------------
check_extension_exists() {
    local extension="$1"
    local ext_count
    ext_count=$(PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -d "$DJANGO_DB_NAME" -tAc "SELECT COUNT(*) FROM pg_extension WHERE extname='$extension';" 2>/dev/null)

    if [[ "$ext_count" -eq 1 ]]; then
        return 0
    else
        return 1
    fi
}

# -----------------------------------------------------------------------------
# create_extensions
# Description: Create required PostgreSQL extensions
# NO SILENT FAILURES: Reports extension creation status
# IDEMPOTENT: Checks if extensions exist before creating
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success (warnings for optional extensions)
# -----------------------------------------------------------------------------
create_extensions() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando extensiones de PostgreSQL"

    local required_extensions=("pg_trgm" "unaccent")
    local created=0
    local skipped=0

    for extension in "${required_extensions[@]}"; do
        if check_extension_exists "$extension"; then
            iact_log_info "Extension '$extension' ya existe"
            ((skipped++))
        else
            iact_log_info "Creando extension '$extension'..."
            if PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -d "$DJANGO_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS $extension;" 2>&1 | tee -a "$(iact_get_log_file)"; then
                iact_log_success "Extension '$extension' creada"
                ((created++))
            else
                iact_log_warning "No se pudo crear extension '$extension' (puede no estar disponible)"
            fi
        fi
    done

    iact_log_info "Extensiones creadas: $created, ya existian: $skipped"
    iact_log_success "Configuracion de extensiones completada"
    return 0
}

# -----------------------------------------------------------------------------
# verify_database_setup
# Description: Verify database, user, and extensions configuration
# NO SILENT FAILURES: Reports verification results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_database_setup() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando configuracion de PostgreSQL"

    # Verify database exists
    if ! check_database_exists; then
        iact_log_error "Base de datos '$DJANGO_DB_NAME' no existe"
        return 1
    fi
    iact_log_success "Base de datos '$DJANGO_DB_NAME' existe"

    # Verify user exists
    if ! check_user_exists; then
        iact_log_error "Usuario '$DJANGO_DB_USER' no existe"
        return 1
    fi
    iact_log_success "Usuario '$DJANGO_DB_USER' existe"

    # Test user connection
    iact_log_info "Probando conexion con usuario '$DJANGO_DB_USER'..."
    if PGPASSWORD="$DJANGO_DB_PASSWORD" psql -U "$DJANGO_DB_USER" -h localhost -d "$DJANGO_DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        iact_log_success "Conexion con '$DJANGO_DB_USER' exitosa"
    else
        iact_log_error "No se puede conectar con usuario '$DJANGO_DB_USER'"
        return 1
    fi

    # Verify extensions
    local required_extensions=("pg_trgm" "unaccent")
    local missing_extensions=()

    for extension in "${required_extensions[@]}"; do
        if check_extension_exists "$extension"; then
            iact_log_success "Extension '$extension' disponible"
        else
            iact_log_warning "Extension '$extension' no disponible"
            missing_extensions+=("$extension")
        fi
    done

    if [[ ${#missing_extensions[@]} -gt 0 ]]; then
        iact_log_warning "Extensiones faltantes: ${missing_extensions[*]}"
        iact_log_info "Algunas funcionalidades pueden no estar disponibles"
    fi

    return 0
}

# -----------------------------------------------------------------------------
# display_postgres_info
# Description: Display PostgreSQL setup information
# NO SILENT FAILURES: Shows complete configuration
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_postgres_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de configuracion"

    echo ""
    echo "=================================================================="
    echo "          CONFIGURACION DE BASE DE DATOS POSTGRESQL"
    echo "=================================================================="
    echo ""
    echo "Base de datos: $DJANGO_DB_NAME"
    echo "Usuario: $DJANGO_DB_USER"
    echo "Password: $DJANGO_DB_PASSWORD"
    echo ""
    echo "Comando de conexion:"
    echo "  PGPASSWORD='$DJANGO_DB_PASSWORD' psql -U $DJANGO_DB_USER -h localhost -d $DJANGO_DB_NAME"
    echo ""
    echo "Encoding: UTF8"
    echo "LC_COLLATE: en_US.UTF-8"
    echo "LC_CTYPE: en_US.UTF-8"
    echo ""
    echo "Extensiones instaladas:"
    echo "  - pg_trgm (busqueda de texto)"
    echo "  - unaccent (normalizacion de texto)"
    echo ""
    echo "Desde aplicacion Django:"
    echo "  'ENGINE': 'django.db.backends.postgresql'"
    echo "  'NAME': '$DJANGO_DB_NAME'"
    echo "  'USER': '$DJANGO_DB_USER'"
    echo "  'PASSWORD': '$DJANGO_DB_PASSWORD'"
    echo "  'HOST': 'localhost'"
    echo "  'PORT': '5432'"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN
# =============================================================================

main() {
    iact_log_header "POSTGRESQL DATABASE SETUP - VAGRANT"
    iact_log_info "Configurando base de datos de aplicacion: $DJANGO_DB_NAME"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        wait_for_postgres_service
        create_database
        create_database_user
        create_extensions
        verify_database_setup
        display_postgres_info
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
        iact_log_success "Configuracion de PostgreSQL completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Base de datos '$DJANGO_DB_NAME' lista para usar"
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