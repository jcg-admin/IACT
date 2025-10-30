#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Post-Start Hook
# =============================================================================
# Description: Executed every time the container starts
# Author: IACT Team
# Version: 2.0.0
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
# FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
# check_python_environment
# Description: Quick check of Python environment
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
check_python_environment() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando entorno Python"

    if iact_check_python_version "3.11"; then
        iact_log_success "Python $(python --version) disponible"
        return 0
    else
        iact_log_error "Python 3.11+ no encontrado"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# check_database_services
# Description: Quick check of database availability
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
check_database_services() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando servicios de base de datos"

    local all_ok=true

    # Check PostgreSQL
    if iact_check_postgres_connect; then
        iact_log_success "PostgreSQL conectado"
    else
        iact_log_warning "PostgreSQL no disponible"
        all_ok=false
    fi

    # Check MariaDB
    if iact_check_mariadb_connect; then
        iact_log_success "MariaDB conectado"
    else
        iact_log_warning "MariaDB no disponible"
        all_ok=false
    fi

    if $all_ok; then
        return 0
    else
        return 1
    fi
}

# -----------------------------------------------------------------------------
# display_environment_info
# Description: Display environment information
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
display_environment_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información del entorno"

    echo ""
    echo "📍 Contexto: $(iact_get_context)"
    echo "📁 Workspace: $WORKSPACE_ROOT"
    echo "🐍 Python: $(python --version 2>&1)"
    echo "🗄️  PostgreSQL: ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}"
    echo "🗄️  MariaDB: ${IVR_DB_HOST}:${IVR_DB_PORT}"
    echo ""

    return 0
}

# -----------------------------------------------------------------------------
# check_pending_migrations
# Description: Check for pending Django migrations
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
check_pending_migrations() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando migraciones pendientes"

    cd "$DJANGO_PROJECT_DIR" || return 1

    # Check for pending migrations (non-blocking)
    if python manage.py showmigrations --plan 2>&1 | grep -q '\[ \]'; then
        iact_log_warning "⚠️  Hay migraciones pendientes. Ejecuta: python manage.py migrate"
        return 0  # No crítico
    else
        iact_log_success "No hay migraciones pendientes"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# display_helpful_tips
# Description: Display helpful tips for development
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
display_helpful_tips() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Tips de desarrollo"

    cat << 'EOF'

💡 Comandos útiles:
   - Ejecutar servidor: python manage.py runserver
   - Ejecutar tests: pytest
   - Verificar sistema: infrastructure/devcontainer/verificar.sh
   - Ver logs: tail -f infrastructure/devcontainer/logs/*.log

EOF

    return 0
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    iact_log_header "Post-Start Check"
    iact_log_info "Verificando estado del DevContainer"

    # Define steps array (auto-calculated)
    local steps=(
        check_python_environment
        check_database_services
        display_environment_info
        check_pending_migrations
        display_helpful_tips
    )

    # Auto-calculate total and execute
    local total=${#steps[@]}
    local current=0

    for step_func in "${steps[@]}"; do
        ((current++))

        # Continue on error (post-start should not fail)
        $step_func "$current" "$total" || true
    done

    echo ""
    iact_log_success "✅ Post-start completado"

    # Always return 0 (post-start should not block container start)
    return 0
}

# Execute main
main "$@"