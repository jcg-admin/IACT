#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Post-Start Hook
# =============================================================================
# Description: Executed every time the container starts
# Author: IACT Team
# Version: 2.0.0
# Pattern: Idempotent execution, No silent failures, Non-blocking
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

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# CHECK FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES & NON-BLOCKING
# =============================================================================

# -----------------------------------------------------------------------------
# check_python_environment
# Description: Quick check of Python environment
# NO SILENT FAILURES: Reports Python status explicitly
# IDEMPOTENT: Safe to run multiple times
# NON-BLOCKING: Always returns 0
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-blocking)
# -----------------------------------------------------------------------------
check_python_environment() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando entorno Python"

    if iact_check_python_version "3.11"; then
        local py_version
        py_version=$(iact_get_python_version)
        iact_log_success "Python $py_version disponible (requisito: >= 3.11)"
        return 0
    else
        iact_log_warning "Python 3.11+ no encontrado"
        return 0  # Non-blocking
    fi
}

# -----------------------------------------------------------------------------
# check_database_services
# Description: Quick check of database availability
# NO SILENT FAILURES: Reports each database status
# IDEMPOTENT: Safe to run multiple times
# NON-BLOCKING: Always returns 0
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-blocking)
# -----------------------------------------------------------------------------
check_database_services() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando servicios de base de datos"

    local all_ok=true

    # Check PostgreSQL (non-blocking)
    iact_log_info "Verificando PostgreSQL en ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}..."
    if iact_check_postgres_connect; then
        iact_log_success "PostgreSQL conectado y respondiendo"
    else
        iact_log_warning "PostgreSQL no disponible (puede estar iniciando)"
        all_ok=false
    fi

    # Check MariaDB (non-blocking)
    iact_log_info "Verificando MariaDB en ${IVR_DB_HOST}:${IVR_DB_PORT}..."
    if iact_check_mariadb_connect; then
        iact_log_success "MariaDB conectado y respondiendo"
    else
        iact_log_warning "MariaDB no disponible (puede estar iniciando)"
        all_ok=false
    fi

    if $all_ok; then
        iact_log_success "Todos los servicios de base de datos disponibles"
    else
        iact_log_info "Algunos servicios no están disponibles aún"
    fi

    return 0  # Non-blocking
}

# -----------------------------------------------------------------------------
# check_django_configuration
# Description: Verify Django configuration
# NO SILENT FAILURES: Reports Django status
# IDEMPOTENT: Safe to run multiple times
# NON-BLOCKING: Always returns 0
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-blocking)
# -----------------------------------------------------------------------------
check_django_configuration() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando configuración Django"

    if ! iact_check_django_installed; then
        iact_log_warning "Django no instalado o no disponible"
        return 0  # Non-blocking
    fi

    local django_version
    django_version=$(iact_get_django_version)
    iact_log_success "Django $django_version instalado"

    if ! iact_check_django_project_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_warning "Django project not found at: $DJANGO_PROJECT_DIR"
        return 0  # Non-blocking
    fi

    iact_log_success "Django project encontrado en: $DJANGO_PROJECT_DIR"

    return 0  # Non-blocking
}

# -----------------------------------------------------------------------------
# check_pending_migrations
# Description: Check for pending Django migrations
# NO SILENT FAILURES: Reports migration status
# IDEMPOTENT: Safe to run multiple times
# NON-BLOCKING: Always returns 0
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-blocking)
# -----------------------------------------------------------------------------
check_pending_migrations() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando migraciones pendientes"

    if ! iact_check_django_project_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_info "Django project no disponible, saltando verificación de migraciones"
        return 0
    fi

    # Check for pending migrations (non-blocking)
    if iact_check_django_migrations_needed 2>/dev/null; then
        iact_log_warning "Hay migraciones pendientes"
        iact_log_info "Ejecuta: python manage.py migrate"
        return 0  # Non-blocking
    else
        iact_log_success "No hay migraciones pendientes"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# display_environment_info
# Description: Display environment information
# NO SILENT FAILURES: Shows complete environment status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_environment_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información del entorno"

    echo ""
    echo "=================================================================="
    echo "Contexto: $(iact_get_context)"
    echo "Project Root: $IACT_PROJECT_ROOT"
    echo "Django Project: $DJANGO_PROJECT_DIR"
    echo "Python: $(iact_get_python_version 2>/dev/null || echo 'No disponible')"
    echo "Django: $(iact_get_django_version 2>/dev/null || echo 'No disponible')"
    echo ""
    echo "PostgreSQL: ${DJANGO_DB_HOST}:${DJANGO_DB_PORT} / ${DJANGO_DB_NAME}"
    echo "MariaDB: ${IVR_DB_HOST}:${IVR_DB_PORT} / ${IVR_DB_NAME}"
    echo ""
    echo "Logs: $(iact_get_log_file)"
    echo "=================================================================="
    echo ""

    return 0
}

# -----------------------------------------------------------------------------
# display_helpful_tips
# Description: Display helpful tips for development
# NO SILENT FAILURES: Shows useful commands
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_helpful_tips() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Tips de desarrollo"

    cat << 'EOF'

Comandos utiles:
   - Ejecutar servidor: python manage.py runserver
   - Ejecutar tests: pytest
   - Verificar sistema: infrastructure/devcontainer/scripts/verificar.sh
   - Ver logs: tail -f infrastructure/logs/*.log
   - Setup databases: infrastructure/scripts/setup-databases.sh

EOF

    return 0
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN (NON-BLOCKING)
# =============================================================================

main() {
    iact_log_header "DEVCONTAINER POST-START CHECK"
    iact_log_info "Verificando estado del DevContainer al iniciar"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        check_python_environment
        check_database_services
        check_django_configuration
        check_pending_migrations
        display_environment_info
        display_helpful_tips
    )

    # Auto-ejecutar con patrón (NON-BLOCKING MODE)
    local total=${#steps[@]}
    local current=0

    for step_func in "${steps[@]}"; do
        ((current++))

        # Continue on error (post-start should NEVER fail)
        $step_func "$current" "$total" || true
    done

    # Report completion
    echo ""
    iact_log_success "Post-start completado"
    iact_log_info "Total verificaciones: $total"

    # CRITICAL: Always return 0 (post-start must NEVER block container start)
    return 0
}

# Execute main
main "$@"