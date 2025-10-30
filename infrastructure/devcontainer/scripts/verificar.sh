#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Verification Script
# =============================================================================
# Description: Comprehensive manual verification of the DevContainer
# Author: IACT Team
# Version: 2.0.0
# Usage: ./verificar.sh
# Pattern: Idempotent execution, No silent failures
# =============================================================================

set -euo pipefail

# =============================================================================
# SETUP
# =============================================================================

# Obtener directorio del script
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cargar core (que auto-carga logging)
source "${SCRIPT_DIR}/../../utils/core.sh"

# Cargar módulos adicionales
iact_source_module "validation"
iact_source_module "database"
iact_source_module "python"

# Configurar logging
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# VERIFICATION FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# verify_docker_environment
# Description: Verify running in Docker
# NO SILENT FAILURES: Reports detection explicitly
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if in Docker, 1 otherwise
# -----------------------------------------------------------------------------
verify_docker_environment() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando entorno Docker"

    if iact_validate_docker_environment; then
        iact_log_success "Ejecutando en contenedor Docker"
        iact_log_info "Context: $(iact_get_context)"
        return 0
    else
        iact_log_warning "No se detectó entorno Docker (ejecutando en: $(iact_get_context))"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_essential_commands
# Description: Verify essential command availability
# NO SILENT FAILURES: Reports each command status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if all found, 1 if any missing
# -----------------------------------------------------------------------------
verify_essential_commands() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando comandos esenciales"

    local commands=("python3" "pip" "git" "curl" "psql" "mysql")
    local missing=()

    for cmd in "${commands[@]}"; do
        if iact_check_command_exists "$cmd"; then
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
# verify_project_structure
# Description: Verify project directory structure
# NO SILENT FAILURES: Reports each directory status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if all found, 1 if any missing
# -----------------------------------------------------------------------------
verify_project_structure() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando estructura del proyecto"

    local required_dirs=(
        "$IACT_PROJECT_ROOT/api"
        "$IACT_PROJECT_ROOT/api/callcentersite"
        "$IACT_INFRASTRUCTURE_DIR"
        "$IACT_UTILS_DIR"
    )

    local missing=()

    for dir in "${required_dirs[@]}"; do
        if iact_check_directory_exists "$dir"; then
            iact_log_success "Directorio encontrado: $dir"
        else
            iact_log_error "Directorio no encontrado: $dir"
            missing+=("$dir")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        iact_log_success "Estructura del proyecto validada"
        return 0
    else
        iact_log_error "Directorios faltantes: ${#missing[@]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_environment_variables
# Description: Verify required environment variables
# NO SILENT FAILURES: Reports each variable with its value
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if all set, 1 if any missing
# -----------------------------------------------------------------------------
verify_environment_variables() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando variables de entorno"

    local required_vars=(
        "DJANGO_DB_HOST"
        "DJANGO_DB_PORT"
        "DJANGO_DB_NAME"
        "DJANGO_DB_USER"
        "IVR_DB_HOST"
        "IVR_DB_PORT"
        "IVR_DB_NAME"
        "IVR_DB_USER"
    )

    local missing=()

    for var in "${required_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            iact_log_success "Variable definida: $var=${!var}"
        else
            iact_log_error "Variable no definida: $var"
            missing+=("$var")
        fi
    done

    if [[ ${#missing[@]} -eq 0 ]]; then
        iact_log_success "Todas las variables de entorno configuradas"
        return 0
    else
        iact_log_error "Variables faltantes: ${missing[*]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_python_installation
# Description: Verify Python and pip installation
# NO SILENT FAILURES: Reports versions explicitly
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if requirements met, 1 otherwise
# -----------------------------------------------------------------------------
verify_python_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalación de Python"

    if ! iact_check_python_version "3.11"; then
        iact_log_error "Python 3.11+ requerido"
        return 1
    fi

    local py_version
    py_version=$(iact_get_python_version)
    iact_log_success "Python $py_version instalado (requisito: >= 3.11)"

    if ! iact_check_pip_installed; then
        iact_log_error "pip no encontrado"
        return 1
    fi

    local pip_version
    pip_version=$(iact_get_pip_version)
    iact_log_success "pip $pip_version instalado"

    return 0
}

# -----------------------------------------------------------------------------
# verify_django_installation
# Description: Verify Django installation and configuration
# NO SILENT FAILURES: Reports Django status and version
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if Django OK, 1 otherwise
# -----------------------------------------------------------------------------
verify_django_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalación de Django"

    if ! iact_check_django_installed; then
        iact_log_error "Django no instalado"
        return 1
    fi

    local django_version
    django_version=$(iact_get_django_version)
    iact_log_success "Django $django_version instalado"

    # Check if project exists
    if ! iact_check_django_project_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_error "Django project not found at: $DJANGO_PROJECT_DIR"
        return 1
    fi

    iact_log_success "Django project encontrado en: $DJANGO_PROJECT_DIR"

    # Check settings
    if iact_check_django_settings; then
        iact_log_success "Django settings configurados correctamente"
        return 0
    else
        iact_log_error "Django settings no configurados o inválidos"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_postgres_connection
# Description: Verify PostgreSQL connection and database
# NO SILENT FAILURES: Reports connection status and table count
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if connected, 1 otherwise
# -----------------------------------------------------------------------------
verify_postgres_connection() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando PostgreSQL"

    # Wait for service
    iact_log_info "Esperando PostgreSQL..."
    if ! iact_wait_for_postgres 30; then
        iact_log_error "PostgreSQL no disponible después de 30s"
        return 1
    fi

    # Test connection
    if ! iact_check_postgres_connect; then
        iact_log_error "No se pudo conectar a PostgreSQL"
        return 1
    fi

    iact_log_success "PostgreSQL conectado: ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}"

    # Check database exists
    if iact_check_postgres_database_exists "$DJANGO_DB_NAME"; then
        iact_log_success "Base de datos existe: $DJANGO_DB_NAME"

        # Count tables
        local tables
        tables=$(iact_check_postgres_tables_count "$DJANGO_DB_NAME")
        iact_log_info "Tablas en la base de datos: $tables"
        return 0
    else
        iact_log_warning "Base de datos no existe: $DJANGO_DB_NAME"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_mariadb_connection
# Description: Verify MariaDB connection and database
# NO SILENT FAILURES: Reports connection status and table count
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if connected, 1 otherwise
# -----------------------------------------------------------------------------
verify_mariadb_connection() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando MariaDB"

    # Wait for service
    iact_log_info "Esperando MariaDB..."
    if ! iact_wait_for_mariadb 30; then
        iact_log_error "MariaDB no disponible después de 30s"
        return 1
    fi

    # Test connection
    if ! iact_check_mariadb_connect; then
        iact_log_error "No se pudo conectar a MariaDB"
        return 1
    fi

    iact_log_success "MariaDB conectado: ${IVR_DB_HOST}:${IVR_DB_PORT}"

    # Check database exists
    if iact_check_mariadb_database_exists "$IVR_DB_NAME"; then
        iact_log_success "Base de datos existe: $IVR_DB_NAME"

        # Count tables
        local tables
        tables=$(iact_check_mariadb_tables_count "$IVR_DB_NAME")
        iact_log_info "Tablas en la base de datos: $tables"
        return 0
    else
        iact_log_warning "Base de datos no existe: $IVR_DB_NAME"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_django_system_check
# Description: Run Django system check
# NO SILENT FAILURES: Reports check output
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 if check passes, 1 otherwise
# -----------------------------------------------------------------------------
verify_django_system_check() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Ejecutando Django system check"

    if ! iact_check_django_project_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_error "Django project not found at: $DJANGO_PROJECT_DIR"
        return 1
    fi

    iact_log_info "Ejecutando: python manage.py check --deploy"
    if iact_django_manage check --deploy 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Django system check pasó correctamente"
        return 0
    else
        iact_log_error "Django system check falló"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# display_summary
# Description: Display verification summary
# NO SILENT FAILURES: Shows complete system status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_summary() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Resumen de verificación"

    echo ""
    echo "=================================================================="
    echo "                    RESUMEN DE VERIFICACION"
    echo "=================================================================="
    echo ""
    echo "Contexto: $(iact_get_context)"
    echo "Proyecto: $IACT_PROJECT_ROOT"
    echo "Python: $(iact_get_python_version)"
    echo "Django: $(iact_get_django_version 2>/dev/null || echo 'No instalado')"
    echo ""
    echo "PostgreSQL: ${DJANGO_DB_HOST}:${DJANGO_DB_PORT} / ${DJANGO_DB_NAME}"
    echo "MariaDB: ${IVR_DB_HOST}:${IVR_DB_PORT} / ${IVR_DB_NAME}"
    echo ""
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
    iact_log_header "DEVCONTAINER VERIFICATION"
    iact_log_info "Iniciando verificación completa del sistema"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        verify_docker_environment
        verify_essential_commands
        verify_project_structure
        verify_environment_variables
        verify_python_installation
        verify_django_installation
        verify_postgres_connection
        verify_mariadb_connection
        verify_django_system_check
        display_summary
    )

    # Auto-ejecutar con patrón
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
        iact_log_success "Todas las verificaciones pasaron correctamente"
        iact_log_info "Total verificaciones: $total"
        return 0
    else
        iact_log_error "Verificación completada con ${#failed_steps[@]} error(es):"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        iact_log_info "Total verificaciones: $total"
        iact_log_info "Verificaciones exitosas: $((total - ${#failed_steps[@]}))"
        return 1
    fi
}

# Execute main
main "$@"