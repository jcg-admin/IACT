#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Verification Script
# =============================================================================
# Description: Comprehensive manual verification of the DevContainer
# Author: IACT Team
# Version: 2.0.0
# Usage: ./verificar.sh
# =============================================================================

set -euo pipefail

# =============================================================================
# SETUP
# =============================================================================

# Obtener directorio del script
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cargar core (que auto-carga logging)
source "${SCRIPT_DIR}/../utils/core.sh"

# Cargar módulos adicionales
iact_source_module "validation"
iact_source_module "database"
iact_source_module "python"

# Configurar logging
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# VERIFICATION FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
# verify_docker_environment
# Description: Verify running in Docker
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_docker_environment() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando entorno Docker"

    if iact_validate_docker_environment; then
        iact_log_success "Ejecutando en contenedor Docker"
        return 0
    else
        iact_log_warning "No se detectó entorno Docker"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_essential_commands
# Description: Verify essential command availability
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_essential_commands() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando comandos esenciales"

    local commands=("python3" "pip" "git" "curl" "psql" "mysql")
    local missing=()

    for cmd in "${commands[@]}"; do
        if iact_command_exists "$cmd"; then
            iact_log_success "✓ $cmd"
        else
            iact_log_error "✗ $cmd (no encontrado)"
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
        return 0
    else
        iact_log_error "Comandos faltantes: ${missing[*]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_project_structure
# Description: Verify project directory structure
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_project_structure() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando estructura del proyecto"

    local required_dirs=(
        "$PROJECT_ROOT/api"
        "$PROJECT_ROOT/api/callcentersite"
        "$INFRASTRUCTURE_DIR"
        "$UTILS_DIR"
    )

    local missing=()

    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            iact_log_success "✓ $dir"
        else
            iact_log_error "✗ $dir (no encontrado)"
            missing+=("$dir")
        fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
        return 0
    else
        iact_log_error "Directorios faltantes: ${#missing[@]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_environment_variables
# Description: Verify required environment variables
# Arguments: $1 - current step, $2 - total steps
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
            iact_log_success "✓ $var=${!var}"
        else
            iact_log_error "✗ $var (no definida)"
            missing+=("$var")
        fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
        return 0
    else
        iact_log_error "Variables faltantes: ${missing[*]}"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_python_installation
# Description: Verify Python and pip installation
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_python_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalación de Python"

    if ! iact_check_python_version "3.11"; then
        iact_log_error "Python 3.11+ requerido"
        return 1
    fi

    iact_log_success "Python $(python --version 2>&1) instalado"

    if ! iact_command_exists "pip"; then
        iact_log_error "pip no encontrado"
        return 1
    fi

    iact_log_success "pip $(pip --version | awk '{print $2}') instalado"

    return 0
}

# -----------------------------------------------------------------------------
# verify_django_installation
# Description: Verify Django installation and configuration
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_django_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalación de Django"

    if ! python -c "import django" 2>/dev/null; then
        iact_log_error "Django no instalado"
        return 1
    fi

    local django_version=$(python -c "import django; print(django.get_version())")
    iact_log_success "Django $django_version instalado"

    # Check settings
    cd "$DJANGO_PROJECT_DIR" || return 1

    if python -c "from django.conf import settings" 2>/dev/null; then
        iact_log_success "Django settings configurados"
        return 0
    else
        iact_log_error "Django settings no configurados"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_postgres_connection
# Description: Verify PostgreSQL connection and database
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_postgres_connection() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando PostgreSQL"

    # Wait for service
    if ! iact_wait_for_postgres 30; then
        iact_log_error "PostgreSQL no disponible (timeout 30s)"
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
        iact_log_success "Base de datos '$DJANGO_DB_NAME' existe"

        # Count tables
        local tables=$(iact_postgres_count_tables "$DJANGO_DB_NAME")
        iact_log_info "Tablas en la base de datos: $tables"
        return 0
    else
        iact_log_warning "Base de datos '$DJANGO_DB_NAME' no existe"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_mariadb_connection
# Description: Verify MariaDB connection and database
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_mariadb_connection() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando MariaDB"

    # Wait for service
    if ! iact_wait_for_mariadb 30; then
        iact_log_error "MariaDB no disponible (timeout 30s)"
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
        iact_log_success "Base de datos '$IVR_DB_NAME' existe"

        # Count tables
        local tables=$(iact_mariadb_count_tables "$IVR_DB_NAME")
        iact_log_info "Tablas en la base de datos: $tables"
        return 0
    else
        iact_log_warning "Base de datos '$IVR_DB_NAME' no existe"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# verify_django_system_check
# Description: Run Django system check
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
verify_django_system_check() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Ejecutando Django system check"

    cd "$DJANGO_PROJECT_DIR" || return 1

    if python manage.py check --deploy; then
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
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
display_summary() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Resumen de verificación"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "                    RESUMEN DE VERIFICACIÓN"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "📍 Contexto: $(iact_get_context)"
    echo "📁 Proyecto: $PROJECT_ROOT"
    echo "🐍 Python: $(python --version 2>&1)"
    echo "🎯 Django: $(python -c 'import django; print(django.get_version())' 2>/dev/null || echo 'No instalado')"
    echo ""
    echo "🗄️  PostgreSQL: ${DJANGO_DB_HOST}:${DJANGO_DB_PORT} / ${DJANGO_DB_NAME}"
    echo "🗄️  MariaDB: ${IVR_DB_HOST}:${IVR_DB_PORT} / ${IVR_DB_NAME}"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    return 0
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    iact_log_header "DevContainer Verification"
    iact_log_info "Iniciando verificación completa del sistema"

    # Define steps array (auto-calculated)
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

    # Auto-calculate total and execute
    local total=${#steps[@]}
    local current=0
    local failed_steps=()

    for step_func in "${steps[@]}"; do
        ((current++))

        if ! $step_func "$current" "$total"; then
            failed_steps+=("$step_func")
        fi
    done

    # Report results
    echo ""
    if [ ${#failed_steps[@]} -eq 0 ]; then
        iact_log_success "✅ Todas las verificaciones pasaron correctamente"
        return 0
    else
        iact_log_error "❌ Verificación completada con ${#failed_steps[@]} errores:"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        return 1
    fi
}

# Execute main
main "$@"