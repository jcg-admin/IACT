#!/usr/bin/env bash
#
# post-start.sh - DevContainer Post-Start Verification
#
# Ejecuta verificaciones rápidas CADA VEZ que el contenedor se inicia.
# Este script debe ser RÁPIDO (<30s) y solo VERIFICAR, no instalar.
#
# Lifecycle: postStartCommand (CONTAINER - cada inicio)
# Frecuencia: MÚLTIPLE (cada vez que se inicia el contenedor)
# Criterio: Verificación rápida - asegurar que todo funciona
#

set -euo pipefail

# =============================================================================
# CONFIGURACION
# =============================================================================

# Detectar directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/../utils"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# Django project directory
DJANGO_DIR="${PROJECT_ROOT}/api/callcentersite"

# Database configuration (from docker-compose.yml)
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_HOST="${POSTGRES_HOST:-db_postgres}"
POSTGRES_DB="${POSTGRES_DB:-callcenter_db}"

MARIADB_USER="${MARIADB_USER:-root}"
MARIADB_PASSWORD="${MARIADB_ROOT_PASSWORD:-root}"
MARIADB_HOST="${MARIADB_HOST:-db_mariadb}"
MARIADB_DB="${MARIADB_DATABASE:-callcenter_legacy}"

# =============================================================================
# CARGAR UTILIDADES
# =============================================================================

# Cargar core (requerido)
if [[ -f "${UTILS_DIR}/core.sh" ]]; then
    source "${UTILS_DIR}/core.sh"
else
    echo "Error: No se pudo cargar core.sh" >&2
    exit 1
fi

# Cargar otros módulos
if ! iact_source_module "logging"; then
    echo "Error: No se pudo cargar logging.sh" >&2
    exit 1
fi

if ! iact_source_module "validation"; then
    echo "Error: No se pudo cargar validation.sh" >&2
    exit 1
fi

if ! iact_source_module "database"; then
    echo "Error: No se pudo cargar database.sh" >&2
    exit 1
fi

if ! iact_source_module "python"; then
    echo "Error: No se pudo cargar python.sh" >&2
    exit 1
fi

# =============================================================================
# INICIALIZACION
# =============================================================================

# Inicializar logging
if ! iact_init_logging "post-start"; then
    echo "Warning: No se pudo inicializar logging, continuando sin logs a archivo" >&2
fi

iact_log_header "DEVCONTAINER - POST-START VERIFICATION"

# Variables de control
ERRORS=0
WARNINGS=0

# =============================================================================
# FUNCIONES
# =============================================================================

increment_errors() {
    ((ERRORS++))
}

increment_warnings() {
    ((WARNINGS++))
}

# =============================================================================
# STEP 1: VERIFICAR CONTEXTO
# =============================================================================

check_context() {
    iact_log_step 1 5 "Checking container context"

    # Detectar contexto
    local context
    context=$(iact_get_context)
    iact_log_info "Context: $context"

    # Información básica
    iact_log_info "Hostname: $(hostname)"
    iact_log_info "User: $(whoami)"
    iact_log_info "Working Directory: $(pwd)"

    # Verificar Python
    if iact_validate_python_installed; then
        local python_version
        python_version=$(iact_python_get_version)
        iact_log_info "Python: $python_version"
    else
        iact_log_warning "Python no disponible"
        increment_warnings
    fi

    # Verificar Django
    if iact_validate_django_installed; then
        local django_version
        django_version=$(iact_django_get_version)
        iact_log_info "Django: $django_version"
    else
        iact_log_warning "Django no disponible"
        increment_warnings
    fi

    iact_log_success "Context check completed"
}

# =============================================================================
# STEP 2: VERIFICAR BASES DE DATOS
# =============================================================================

check_databases() {
    iact_log_step 2 5 "Checking database connectivity"

    # Verificar PostgreSQL (timeout corto: 30s)
    iact_log_info "Checking PostgreSQL at $POSTGRES_HOST..."

    if iact_db_postgres_wait "$POSTGRES_USER" "$POSTGRES_PASSWORD" 30 "$POSTGRES_HOST"; then
        iact_log_success "PostgreSQL is available"

        # Verificar que la base de datos existe
        if iact_db_postgres_database_exists "$POSTGRES_DB" "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$POSTGRES_HOST"; then
            iact_log_success "Database exists: $POSTGRES_DB"
        else
            iact_log_warning "Database does not exist: $POSTGRES_DB"
            increment_warnings
        fi
    else
        iact_log_warning "PostgreSQL no disponible después de 30s"
        increment_warnings
    fi

    # Verificar MariaDB (timeout corto: 30s)
    iact_log_info "Checking MariaDB at $MARIADB_HOST..."

    if iact_db_mariadb_wait "$MARIADB_USER" "$MARIADB_PASSWORD" 30 "$MARIADB_HOST"; then
        iact_log_success "MariaDB is available"

        # Verificar que la base de datos existe
        if iact_db_mariadb_database_exists "$MARIADB_DB" "$MARIADB_USER" "$MARIADB_PASSWORD" "$MARIADB_HOST"; then
            iact_log_success "Database exists: $MARIADB_DB"
        else
            iact_log_warning "Database does not exist: $MARIADB_DB"
            increment_warnings
        fi
    else
        iact_log_warning "MariaDB no disponible después de 30s"
        increment_warnings
    fi

    iact_log_success "Database check completed"
}

# =============================================================================
# STEP 3: VERIFICAR DJANGO
# =============================================================================

check_django() {
    iact_log_step 3 5 "Checking Django application"

    # Verificar proyecto Django
    if ! iact_validate_django_project "$DJANGO_DIR"; then
        iact_log_error "Proyecto Django no válido"
        increment_errors
        return 1
    fi

    iact_log_success "Django project valid"

    # Verificar conexión a base de datos (timeout corto: 15s)
    iact_log_info "Checking Django database connection..."

    if iact_django_wait_for_db "$DJANGO_DIR" 15; then
        iact_log_success "Django can connect to database"
    else
        iact_log_warning "Django no puede conectar a base de datos"
        iact_log_info "Esto es normal si las bases de datos aún están iniciando"
        increment_warnings
    fi

    # Verificar estado de migraciones (solo para default database)
    iact_log_info "Checking migration status..."

    if iact_django_has_pending_migrations "$DJANGO_DIR" "default" 2>/dev/null; then
        iact_log_warning "Hay migraciones pendientes en default database"
        iact_log_info "Ejecutar: python manage.py migrate"
        increment_warnings
    else
        iact_log_success "No pending migrations on default database"
    fi

    iact_log_success "Django check completed"
}

# =============================================================================
# STEP 4: VERIFICAR ARCHIVOS CRÍTICOS
# =============================================================================

check_critical_files() {
    iact_log_step 4 5 "Checking critical files"

    local critical_files=(
        "${DJANGO_DIR}/manage.py"
        "${DJANGO_DIR}/callcentersite/settings/base.py"
        "${DJANGO_DIR}/callcentersite/urls.py"
    )

    for file in "${critical_files[@]}"; do
        if iact_validate_file_exists "$file"; then
            if iact_validate_file_not_empty "$file"; then
                local relative_path="${file#$PROJECT_ROOT/}"
                iact_log_success "File OK: $relative_path"
            else
                iact_log_error "File is empty: $file"
                increment_errors
            fi
        else
            iact_log_error "File missing: $file"
            increment_errors
        fi
    done

    # Verificar env file
    local env_file="${DJANGO_DIR}/env"
    if iact_validate_file_exists "$env_file"; then
        iact_log_success "Environment file exists: api/callcentersite/env"
    else
        iact_log_warning "Environment file missing: api/callcentersite/env"
        iact_log_info "Copy from env.example if needed"
        increment_warnings
    fi

    iact_log_success "Critical files check completed"
}

# =============================================================================
# STEP 5: MARCAR INICIO
# =============================================================================

mark_startup() {
    iact_log_step 5 5 "Marking container startup"

    local state_file="${PROJECT_ROOT}/infrastructure/state/last-start.log"
    local timestamp
    timestamp=$(date --iso-8601=seconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S%z")

    # Crear directorio si no existe
    iact_create_dir "$(dirname "$state_file")"

    # Append startup timestamp
    echo "$timestamp - Container started (context: $(iact_get_context))" >> "$state_file"

    iact_log_file_operation "updated" "$state_file"
    iact_log_success "Container startup marked"
}

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print_summary() {
    echo ""
    iact_log_separator

    iact_log_info "postStart Summary:"

    # Estado de bases de datos
    if iact_db_postgres_is_ready "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$POSTGRES_HOST" 2>/dev/null; then
        iact_log_info "  PostgreSQL: ✓ Available"
    else
        iact_log_info "  PostgreSQL: ✗ Not available"
    fi

    if iact_db_mariadb_is_ready "$MARIADB_USER" "$MARIADB_PASSWORD" "$MARIADB_HOST" 2>/dev/null; then
        iact_log_info "  MariaDB: ✓ Available"
    else
        iact_log_info "  MariaDB: ✗ Not available"
    fi

    # Estado de Django
    if iact_validate_django_installed 2>/dev/null; then
        iact_log_info "  Django: ✓ $(iact_django_get_version)"
    else
        iact_log_info "  Django: ✗ Not installed"
    fi

    echo ""

    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        iact_log_success "postStart completed successfully"
        iact_log_info "Errors: 0, Warnings: 0"
        echo ""
        iact_log_success "✓ Container is ready to use"
    elif [[ $ERRORS -eq 0 ]]; then
        iact_log_success "postStart completed with warnings"
        iact_log_info "Errors: 0, Warnings: ${WARNINGS}"
        echo ""
        iact_log_warning "Some services may not be ready yet"
        iact_log_info "This is normal during initial startup"
    else
        iact_log_error "postStart completed with errors"
        iact_log_info "Errors: ${ERRORS}, Warnings: ${WARNINGS}"
        echo ""
        iact_log_error "Some critical issues detected"
    fi

    iact_log_separator

    if [[ -n "$(iact_get_log_file)" ]]; then
        echo ""
        iact_log_info "Log file: $(iact_get_log_file)"
    fi
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    # Ejecutar todos los pasos (no fallar por warnings)
    check_context || true
    echo ""

    check_databases || true
    echo ""

    check_django || true
    echo ""

    check_critical_files || true
    echo ""

    mark_startup || true
    echo ""

    # Resumen final
    print_summary

    # Exit con codigo apropiado (solo errores críticos)
    if [[ $ERRORS -gt 0 ]]; then
        exit 1
    fi

    exit 0
}

# Ejecutar main
main "$@"