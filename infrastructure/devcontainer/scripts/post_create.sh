#!/usr/bin/env bash
#
# post_create.sh - DevContainer Post-Create Setup
#
# Ejecuta setup completo DESPUÉS de instalar dependencias.
# Este script corre DESPUÉS de update_content.sh
#
# Lifecycle: postCreateCommand (CONTAINER - después de dependencias)
# Frecuencia: UNA SOLA VEZ (creación del contenedor)
# Criterio: Setup completo - bases de datos, migraciones, superuser
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

# Superuser configuration
DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
DJANGO_SUPERUSER_EMAIL="${DJANGO_SUPERUSER_EMAIL:-admin@example.com}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-admin}"

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
if ! iact_init_logging "post-create"; then
    echo "Warning: No se pudo inicializar logging, continuando sin logs a archivo" >&2
fi

iact_log_header "DEVCONTAINER - POST-CREATE SETUP"

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
# STEP 1: VALIDAR PREREQUISITOS
# =============================================================================

validate_prerequisites() {
    iact_log_step 1 7 "Validating prerequisites"

    # Validar que Django está instalado
    if ! iact_validate_django_installed; then
        iact_log_error "Django no está instalado - ejecutar update-content.sh primero"
        increment_errors
        return 1
    fi

    local django_version
    django_version=$(iact_django_get_version)
    iact_log_success "Django installed: $django_version"

    # Validar proyecto Django
    if ! iact_validate_django_project "$DJANGO_DIR"; then
        iact_log_error "Proyecto Django no válido: $DJANGO_DIR"
        increment_errors
        return 1
    fi

    iact_log_success "Django project valid: $DJANGO_DIR"

    # Validar clientes de base de datos
    if ! iact_validate_postgres_client; then
        iact_log_warning "PostgreSQL client no disponible"
        increment_warnings
    else
        iact_log_success "PostgreSQL client available"
    fi

    if ! iact_validate_mariadb_client; then
        iact_log_warning "MariaDB client no disponible"
        increment_warnings
    else
        iact_log_success "MariaDB client available"
    fi

    iact_log_success "Prerequisites validated"
}

# =============================================================================
# STEP 2: ESPERAR POSTGRESQL
# =============================================================================

wait_for_postgresql() {
    iact_log_step 2 7 "Waiting for PostgreSQL"

    iact_log_info "PostgreSQL connection details:"
    iact_log_info "  Host: $POSTGRES_HOST"
    iact_log_info "  User: $POSTGRES_USER"
    iact_log_info "  Database: $POSTGRES_DB"

    # Esperar hasta 120 segundos
    if iact_db_postgres_wait "$POSTGRES_USER" "$POSTGRES_PASSWORD" 120 "$POSTGRES_HOST"; then
        iact_log_success "PostgreSQL is ready"
    else
        iact_log_error "PostgreSQL no respondió en 120s"
        increment_errors
        return 1
    fi

    # Test de conexión detallado
    if iact_db_postgres_test_connection "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$POSTGRES_DB" "$POSTGRES_HOST"; then
        iact_log_success "PostgreSQL connection test successful"
    else
        iact_log_error "PostgreSQL connection test failed"
        increment_errors
        return 1
    fi

    # Verificar que la base de datos existe
    if iact_db_postgres_database_exists "$POSTGRES_DB" "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$POSTGRES_HOST"; then
        iact_log_success "Database exists: $POSTGRES_DB"
    else
        iact_log_warning "Database does not exist: $POSTGRES_DB"
        iact_log_info "Database will be created by Django migrations"
        increment_warnings
    fi

    iact_log_success "PostgreSQL ready for Django"
}

# =============================================================================
# STEP 3: ESPERAR MARIADB
# =============================================================================

wait_for_mariadb() {
    iact_log_step 3 7 "Waiting for MariaDB"

    iact_log_info "MariaDB connection details:"
    iact_log_info "  Host: $MARIADB_HOST"
    iact_log_info "  User: $MARIADB_USER"
    iact_log_info "  Database: $MARIADB_DB"

    # Esperar hasta 120 segundos
    if iact_db_mariadb_wait "$MARIADB_USER" "$MARIADB_PASSWORD" 120 "$MARIADB_HOST"; then
        iact_log_success "MariaDB is ready"
    else
        iact_log_error "MariaDB no respondió en 120s"
        increment_errors
        return 1
    fi

    # Test de conexión detallado
    if iact_db_mariadb_test_connection "$MARIADB_USER" "$MARIADB_PASSWORD" "$MARIADB_DB" "$MARIADB_HOST"; then
        iact_log_success "MariaDB connection test successful"
    else
        iact_log_error "MariaDB connection test failed"
        increment_errors
        return 1
    fi

    # Verificar que la base de datos existe
    if iact_db_mariadb_database_exists "$MARIADB_DB" "$MARIADB_USER" "$MARIADB_PASSWORD" "$MARIADB_HOST"; then
        iact_log_success "Database exists: $MARIADB_DB"
    else
        iact_log_warning "Database does not exist: $MARIADB_DB"
        iact_log_info "Database may need to be created manually"
        increment_warnings
    fi

    iact_log_success "MariaDB ready for Django"
}

# =============================================================================
# STEP 4: DJANGO SYSTEM CHECK
# =============================================================================

django_system_check() {
    iact_log_step 4 7 "Running Django system check"

    # Esperar a que Django pueda conectarse a la base de datos
    iact_log_info "Waiting for Django to connect to database..."

    if iact_django_wait_for_db "$DJANGO_DIR" 120; then
        iact_log_success "Django can connect to database"
    else
        iact_log_error "Django cannot connect to database after 120s"
        increment_errors
        return 1
    fi

    # Ejecutar Django check
    iact_log_info "Running Django system check..."

    if iact_django_check "$DJANGO_DIR"; then
        iact_log_success "Django system check passed"
    else
        iact_log_warning "Django system check reported issues"
        increment_warnings
        # No retornar error - algunas warnings son normales
    fi

    iact_log_success "Django system check completed"
}

# =============================================================================
# STEP 5: EJECUTAR MIGRACIONES
# =============================================================================

run_migrations() {
    iact_log_step 5 7 "Running Django migrations"

    # Mostrar estado de migraciones para PostgreSQL (default)
    iact_log_info "Checking migration status for PostgreSQL (default)..."
    if iact_django_has_pending_migrations "$DJANGO_DIR" "default"; then
        iact_log_info "Pending migrations found for default database"
    else
        iact_log_info "No pending migrations for default database"
    fi

    # Ejecutar migraciones para PostgreSQL (default)
    iact_log_info "Running migrations for PostgreSQL (default database)..."
    if iact_django_migrate "$DJANGO_DIR" "default"; then
        iact_log_success "Migrations applied for default database"
    else
        iact_log_error "Failed to apply migrations for default database"
        increment_errors
        return 1
    fi

    # Mostrar estado de migraciones para MariaDB (legacy)
    iact_log_info "Checking migration status for MariaDB (legacy)..."
    if iact_django_has_pending_migrations "$DJANGO_DIR" "legacy"; then
        iact_log_info "Pending migrations found for legacy database"
    else
        iact_log_info "No pending migrations for legacy database"
    fi

    # Ejecutar migraciones para MariaDB (legacy)
    iact_log_info "Running migrations for MariaDB (legacy database)..."
    if iact_django_migrate "$DJANGO_DIR" "legacy"; then
        iact_log_success "Migrations applied for legacy database"
    else
        iact_log_error "Failed to apply migrations for legacy database"
        increment_errors
        return 1
    fi

    iact_log_success "All migrations completed"
}

# =============================================================================
# STEP 6: CREAR SUPERUSER
# =============================================================================

create_superuser() {
    iact_log_step 6 7 "Creating Django superuser"

    iact_log_info "Superuser configuration:"
    iact_log_info "  Username: $DJANGO_SUPERUSER_USERNAME"
    iact_log_info "  Email: $DJANGO_SUPERUSER_EMAIL"

    # Crear superuser (idempotente - skip si ya existe)
    if iact_django_createsuperuser_noninteractive \
        "$DJANGO_DIR" \
        "$DJANGO_SUPERUSER_USERNAME" \
        "$DJANGO_SUPERUSER_EMAIL" \
        "$DJANGO_SUPERUSER_PASSWORD"; then
        iact_log_success "Superuser operation completed"
    else
        iact_log_warning "Superuser operation had issues"
        increment_warnings
    fi

    iact_log_success "Superuser setup completed"
}

# =============================================================================
# STEP 7: MARCAR COMPLETADO
# =============================================================================

mark_completed() {
    iact_log_step 7 7 "Marking postCreate as completed"

    local state_file="${PROJECT_ROOT}/infrastructure/state/post-create.completed"
    local timestamp
    timestamp=$(date --iso-8601=seconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S%z")

    # Crear directorio si no existe
    iact_create_dir "$(dirname "$state_file")"

    # Crear marker file
    {
        echo "# DevContainer postCreate Completion"
        echo "completed_at: ${timestamp}"
        echo "context: $(iact_get_context)"
        echo "django_version: $(iact_django_get_version)"
        echo "python_version: $(iact_python_get_version)"
        echo "postgres_host: ${POSTGRES_HOST}"
        echo "mariadb_host: ${MARIADB_HOST}"
        echo "superuser: ${DJANGO_SUPERUSER_USERNAME}"
    } > "$state_file"

    iact_log_file_operation "created" "$state_file"
    iact_log_success "postCreate marked as completed"
}

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print_summary() {
    echo ""
    iact_log_separator

    iact_log_info "postCreate Summary:"
    iact_log_info "  Django Project: ${DJANGO_DIR}"
    iact_log_info "  Django Version: $(iact_django_get_version)"
    iact_log_info "  PostgreSQL: ${POSTGRES_HOST}:5432"
    iact_log_info "  MariaDB: ${MARIADB_HOST}:3306"
    iact_log_info "  Superuser: ${DJANGO_SUPERUSER_USERNAME}"

    echo ""

    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        iact_log_success "postCreate completed successfully"
        iact_log_info "Errors: 0, Warnings: 0"
        echo ""
        iact_log_success "🎉 DevContainer is ready to use!"
        iact_log_info "Run Django: cd api/callcentersite && python manage.py runserver"
    elif [[ $ERRORS -eq 0 ]]; then
        iact_log_success "postCreate completed with warnings"
        iact_log_info "Errors: 0, Warnings: ${WARNINGS}"
        echo ""
        iact_log_warning "Review warnings above before proceeding"
    else
        iact_log_error "postCreate completed with errors"
        iact_log_info "Errors: ${ERRORS}, Warnings: ${WARNINGS}"
        echo ""
        iact_log_error "Fix errors before using DevContainer"
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
    # Ejecutar todos los pasos
    validate_prerequisites || true
    echo ""

    wait_for_postgresql || true
    echo ""

    wait_for_mariadb || true
    echo ""

    django_system_check || true
    echo ""

    run_migrations || true
    echo ""

    create_superuser || true
    echo ""

    mark_completed || true
    echo ""

    # Resumen final
    print_summary

    # Exit con codigo apropiado
    if [[ $ERRORS -gt 0 ]]; then
        exit 1
    fi

    exit 0
}

# Ejecutar main
main "$@"