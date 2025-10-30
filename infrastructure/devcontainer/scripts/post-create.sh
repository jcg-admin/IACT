#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Post-Create Hook
# =============================================================================
# Description: Executed once after container is created
# Author: IACT Team
# Version: 2.0.0
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

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# STEP FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# upgrade_pip
# Description: Upgrade pip to latest version
# NO SILENT FAILURES: Reports upgrade status explicitly
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success (non-critical if fails)
# -----------------------------------------------------------------------------
upgrade_pip() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualizando pip"

    if ! iact_check_directory_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_error "Django project directory not found: $DJANGO_PROJECT_DIR"
        return 1
    fi

    cd "$DJANGO_PROJECT_DIR" || {
        iact_log_error "No se pudo acceder a $DJANGO_PROJECT_DIR"
        return 1
    }

    if python -m pip install --upgrade pip 2>&1 | tee -a "$(iact_get_log_file)"; then
        local pip_version
        pip_version=$(iact_get_pip_version)
        iact_log_success "pip actualizado correctamente a versión $pip_version"
        return 0
    else
        iact_log_warning "No se pudo actualizar pip (continuando de todas formas)"
        return 0  # No crítico
    fi
}

# -----------------------------------------------------------------------------
# install_dev_requirements
# Description: Install development requirements
# NO SILENT FAILURES: Reports file status and installation result
# IDEMPOTENT: pip handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on critical failure
# -----------------------------------------------------------------------------
install_dev_requirements() {
    local current="$1"
    local total="$2"
    local req_file="${DJANGO_PROJECT_DIR}/requirements/dev.txt"

    iact_log_step "$current" "$total" "Instalando dependencias de desarrollo"

    if [[ ! -f "$req_file" ]]; then
        iact_log_warning "Archivo de requirements no encontrado: $req_file"
        iact_log_info "Saltando instalación de dependencias de desarrollo"
        return 0
    fi

    iact_log_info "Instalando desde: $req_file"
    if python -m pip install -r "$req_file" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Dependencias de desarrollo instaladas correctamente"
        return 0
    else
        iact_log_error "Error instalando dependencias de desarrollo"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_test_requirements
# Description: Install test requirements
# NO SILENT FAILURES: Reports file status and installation result
# IDEMPOTENT: pip handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on critical failure
# -----------------------------------------------------------------------------
install_test_requirements() {
    local current="$1"
    local total="$2"
    local req_file="${DJANGO_PROJECT_DIR}/requirements/test.txt"

    iact_log_step "$current" "$total" "Instalando dependencias de testing"

    if [[ ! -f "$req_file" ]]; then
        iact_log_warning "Archivo de requirements no encontrado: $req_file"
        iact_log_info "Saltando instalación de dependencias de testing"
        return 0
    fi

    iact_log_info "Instalando desde: $req_file"
    if python -m pip install -r "$req_file" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Dependencias de testing instaladas correctamente"
        return 0
    else
        iact_log_error "Error instalando dependencias de testing"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_copilot_cli
# Description: Install GitHub Copilot CLI if enabled
# NO SILENT FAILURES: Reports availability and installation result
# IDEMPOTENT: npm handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-critical)
# -----------------------------------------------------------------------------
install_copilot_cli() {
    local current="$1"
    local total="$2"
    local install_copilot="${DEVCONTAINER_INSTALL_COPILOT_CLI:-0}"

    iact_log_step "$current" "$total" "Verificando instalación de GitHub Copilot CLI"

    if [[ "$install_copilot" != "1" ]]; then
        iact_log_info "Instalación de Copilot CLI deshabilitada (DEVCONTAINER_INSTALL_COPILOT_CLI=$install_copilot)"
        return 0
    fi

    if ! command -v npm >/dev/null 2>&1; then
        iact_log_warning "npm no encontrado, saltando Copilot CLI"
        return 0
    fi

    iact_log_info "Instalando GitHub Copilot CLI..."
    if npm install -g @githubnext/github-copilot-cli 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "GitHub Copilot CLI instalado correctamente"
        return 0
    else
        iact_log_warning "Error instalando Copilot CLI (no crítico, continuando)"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# setup_environment_file
# Description: Setup .env file if not exists
# NO SILENT FAILURES: Reports file status explicitly
# IDEMPOTENT: Only creates if doesn't exist
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on critical failure
# -----------------------------------------------------------------------------
setup_environment_file() {
    local current="$1"
    local total="$2"
    local env_file="${DJANGO_PROJECT_DIR}/.env"
    local env_example="${IACT_PROJECT_ROOT}/.devcontainer/env.example"

    iact_log_step "$current" "$total" "Configurando archivo de entorno"

    if [[ -f "$env_file" ]]; then
        iact_log_info "Archivo .env ya existe en: $env_file"
        iact_log_info "Saltando creación (idempotente)"
        return 0
    fi

    if [[ ! -f "$env_example" ]]; then
        iact_log_warning "env.example no encontrado en: $env_example"
        iact_log_info "Creando .env con valores por defecto"

        # Create basic .env with defaults
        cat > "$env_file" << 'EOF'
# Django Settings
DEBUG=true
DJANGO_SETTINGS_MODULE=callcentersite.settings.development

# PostgreSQL
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=iact_analytics
DJANGO_DB_USER=django_user
DJANGO_DB_PASSWORD=django_pass
DJANGO_DB_HOST=db_postgres
DJANGO_DB_PORT=5432

# MariaDB (IVR Legacy)
IVR_DB_ENGINE=django.db.backends.mysql
IVR_DB_NAME=ivr_legacy
IVR_DB_USER=django_user
IVR_DB_PASSWORD=django_pass
IVR_DB_HOST=db_mariadb
IVR_DB_PORT=3306
EOF
        iact_log_success "Archivo .env creado con valores por defecto"
        return 0
    fi

    if cp "$env_example" "$env_file"; then
        iact_log_success "Archivo .env creado desde env.example"
        return 0
    else
        iact_log_error "Error creando archivo .env desde $env_example"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# wait_for_databases
# Description: Wait for database services to be ready
# NO SILENT FAILURES: Reports wait time and connection status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 if databases not ready
# -----------------------------------------------------------------------------
wait_for_databases() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Esperando servicios de base de datos"

    # Wait for PostgreSQL
    iact_log_info "Esperando PostgreSQL en ${DJANGO_DB_HOST:-db_postgres}:${DJANGO_DB_PORT:-5432}..."
    if iact_wait_for_postgres 60; then
        iact_log_success "PostgreSQL disponible y respondiendo"
    else
        iact_log_error "PostgreSQL no disponible después de 60s"
        return 1
    fi

    # Wait for MariaDB
    iact_log_info "Esperando MariaDB en ${IVR_DB_HOST:-db_mariadb}:${IVR_DB_PORT:-3306}..."
    if iact_wait_for_mariadb 60; then
        iact_log_success "MariaDB disponible y respondiendo"
    else
        iact_log_error "MariaDB no disponible después de 60s"
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# run_django_check
# Description: Run Django system check
# NO SILENT FAILURES: Reports check results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 if check fails
# -----------------------------------------------------------------------------
run_django_check() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Ejecutando Django system check"

    if ! iact_check_directory_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_error "Django project directory not found: $DJANGO_PROJECT_DIR"
        return 1
    fi

    cd "$DJANGO_PROJECT_DIR" || {
        iact_log_error "No se pudo acceder a $DJANGO_PROJECT_DIR"
        return 1
    }

    iact_log_info "Ejecutando: python manage.py check"
    if python manage.py check 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Django system check pasó correctamente"
        return 0
    else
        iact_log_error "Django system check falló - revisar configuración"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# run_migrations
# Description: Run Django migrations
# NO SILENT FAILURES: Reports migration status
# IDEMPOTENT: Django handles already-applied migrations
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 if migrations fail
# -----------------------------------------------------------------------------
run_migrations() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Ejecutando migraciones de Django"

    if ! iact_check_directory_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_error "Django project directory not found: $DJANGO_PROJECT_DIR"
        return 1
    fi

    cd "$DJANGO_PROJECT_DIR" || {
        iact_log_error "No se pudo acceder a $DJANGO_PROJECT_DIR"
        return 1
    }

    iact_log_info "Ejecutando: python manage.py migrate"
    if python manage.py migrate 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Migraciones ejecutadas correctamente"
        return 0
    else
        iact_log_error "Error ejecutando migraciones"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# run_initial_tests
# Description: Run initial tests if enabled
# NO SILENT FAILURES: Reports test execution status
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-critical)
# -----------------------------------------------------------------------------
run_initial_tests() {
    local current="$1"
    local total="$2"
    local run_tests="${DEVCONTAINER_RUN_TESTS:-0}"

    iact_log_step "$current" "$total" "Verificando tests iniciales"

    if [[ "$run_tests" != "1" ]]; then
        iact_log_info "Tests iniciales deshabilitados (DEVCONTAINER_RUN_TESTS=$run_tests)"
        return 0
    fi

    if ! iact_check_directory_exists "$DJANGO_PROJECT_DIR"; then
        iact_log_warning "Django project directory not found: $DJANGO_PROJECT_DIR"
        return 0
    fi

    cd "$DJANGO_PROJECT_DIR" || {
        iact_log_warning "No se pudo acceder a $DJANGO_PROJECT_DIR"
        return 0
    }

    iact_log_info "Ejecutando tests con pytest..."
    if pytest 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Tests pasaron correctamente"
        return 0
    else
        iact_log_warning "Algunos tests fallaron (no crítico, continuando)"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# mark_completed
# Description: Mark post-create as completed
# NO SILENT FAILURES: Reports state file creation
# IDEMPOTENT: Updates timestamp on each run
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always (non-critical)
# -----------------------------------------------------------------------------
mark_completed() {
    local current="$1"
    local total="$2"
    local state_file="${IACT_STATE_DIR}/post-create.installed"

    iact_log_step "$current" "$total" "Marcando instalación como completada"

    # Ensure state directory exists
    if [[ ! -d "$IACT_STATE_DIR" ]]; then
        if ! mkdir -p "$IACT_STATE_DIR" 2>/dev/null; then
            iact_log_warning "No se pudo crear directorio de estado: $IACT_STATE_DIR"
            return 0
        fi
    fi

    if date --iso-8601=seconds > "$state_file" 2>/dev/null; then
        iact_log_success "Post-create completado - timestamp: $(cat "$state_file")"
        return 0
    else
        iact_log_warning "No se pudo crear archivo de estado (no crítico)"
        return 0
    fi
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN
# =============================================================================

main() {
    iact_log_header "DEVCONTAINER POST-CREATE SETUP"
    iact_log_info "Context: $(iact_get_context)"
    iact_log_info "Project Root: $IACT_PROJECT_ROOT"
    iact_log_info "Django Project: $DJANGO_PROJECT_DIR"
    iact_log_info "Log File: $(iact_get_log_file)"

    # Array de pasos (auto-calculado)
    local steps=(
        upgrade_pip
        install_dev_requirements
        install_test_requirements
        install_copilot_cli
        setup_environment_file
        wait_for_databases
        run_django_check
        run_migrations
        run_initial_tests
        mark_completed
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
        iact_log_success "Post-create completado exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        return 0
    else
        iact_log_error "Post-create completado con ${#failed_steps[@]} error(es):"
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