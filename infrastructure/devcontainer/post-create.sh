#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Post-Create Hook
# =============================================================================
# Description: Executed once after container is created
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
# upgrade_pip
# Description: Upgrade pip to latest version
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
upgrade_pip() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualizando pip"

    cd "$DJANGO_PROJECT_DIR" || {
        iact_log_error "No se pudo acceder a $DJANGO_PROJECT_DIR"
        return 1
    }

    if python -m pip install --upgrade pip; then
        iact_log_success "pip actualizado correctamente"
        return 0
    else
        iact_log_warning "No se pudo actualizar pip (continuando)"
        return 0  # No crítico
    fi
}

# -----------------------------------------------------------------------------
# install_dev_requirements
# Description: Install development requirements
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
install_dev_requirements() {
    local current="$1"
    local total="$2"
    local req_file="requirements/dev.txt"

    iact_log_step "$current" "$total" "Instalando dependencias de desarrollo"

    if [[ ! -f "$req_file" ]]; then
        iact_log_warning "Archivo $req_file no encontrado"
        return 0
    fi

    if python -m pip install -r "$req_file"; then
        iact_log_success "Dependencias de desarrollo instaladas"
        return 0
    else
        iact_log_error "Error instalando dependencias de desarrollo"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_test_requirements
# Description: Install test requirements
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
install_test_requirements() {
    local current="$1"
    local total="$2"
    local req_file="requirements/test.txt"

    iact_log_step "$current" "$total" "Instalando dependencias de testing"

    if [[ ! -f "$req_file" ]]; then
        iact_log_warning "Archivo $req_file no encontrado"
        return 0
    fi

    if python -m pip install -r "$req_file"; then
        iact_log_success "Dependencias de testing instaladas"
        return 0
    else
        iact_log_error "Error instalando dependencias de testing"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_copilot_cli
# Description: Install GitHub Copilot CLI if enabled
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
install_copilot_cli() {
    local current="$1"
    local total="$2"
    local install_copilot="${DEVCONTAINER_INSTALL_COPILOT_CLI:-0}"

    iact_log_step "$current" "$total" "Verificando instalación de GitHub Copilot CLI"

    if [[ "$install_copilot" != "1" ]]; then
        iact_log_info "Instalación de Copilot CLI deshabilitada"
        return 0
    fi

    if ! command -v npm >/dev/null 2>&1; then
        iact_log_warning "npm no encontrado, saltando Copilot CLI"
        return 0
    fi

    iact_log_info "Instalando GitHub Copilot CLI..."
    if npm install -g @githubnext/github-copilot-cli; then
        iact_log_success "GitHub Copilot CLI instalado"
        return 0
    else
        iact_log_warning "Error instalando Copilot CLI (no crítico)"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# setup_environment_file
# Description: Setup .env file if not exists
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
setup_environment_file() {
    local current="$1"
    local total="$2"
    local env_file="${DJANGO_PROJECT_DIR}/.env"
    local env_example="${PROJECT_ROOT}/.devcontainer/env.example"

    iact_log_step "$current" "$total" "Configurando archivo de entorno"

    if [[ -f "$env_file" ]]; then
        iact_log_info "Archivo .env ya existe"
        return 0
    fi

    if [[ ! -f "$env_example" ]]; then
        iact_log_warning "env.example no encontrado"
        return 0
    fi

    if cp "$env_example" "$env_file"; then
        iact_log_success "Archivo .env creado desde env.example"
        return 0
    else
        iact_log_error "Error creando archivo .env"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# wait_for_databases
# Description: Wait for database services to be ready
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
wait_for_databases() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Esperando servicios de base de datos"

    # Wait for PostgreSQL
    iact_log_info "Esperando PostgreSQL..."
    if iact_wait_for_postgres 60; then
        iact_log_success "PostgreSQL disponible"
    else
        iact_log_error "PostgreSQL no disponible"
        return 1
    fi

    # Wait for MariaDB
    iact_log_info "Esperando MariaDB..."
    if iact_wait_for_mariadb 60; then
        iact_log_success "MariaDB disponible"
    else
        iact_log_error "MariaDB no disponible"
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# run_django_check
# Description: Run Django system check
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
run_django_check() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Ejecutando Django system check"

    cd "$DJANGO_PROJECT_DIR" || return 1

    if python manage.py check; then
        iact_log_success "Django system check pasó correctamente"
        return 0
    else
        iact_log_error "Django system check falló"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# run_migrations
# Description: Run Django migrations
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
run_migrations() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Ejecutando migraciones de Django"

    cd "$DJANGO_PROJECT_DIR" || return 1

    if python manage.py migrate; then
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
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
run_initial_tests() {
    local current="$1"
    local total="$2"
    local run_tests="${DEVCONTAINER_RUN_TESTS:-0}"

    iact_log_step "$current" "$total" "Verificando tests iniciales"

    if [[ "$run_tests" != "1" ]]; then
        iact_log_info "Tests iniciales deshabilitados"
        return 0
    fi

    cd "$DJANGO_PROJECT_DIR" || return 1

    iact_log_info "Ejecutando tests con pytest..."
    if pytest; then
        iact_log_success "Tests pasaron correctamente"
        return 0
    else
        iact_log_warning "Algunos tests fallaron (no crítico)"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# mark_completed
# Description: Mark post-create as completed
# Arguments: $1 - current step, $2 - total steps
# -----------------------------------------------------------------------------
mark_completed() {
    local current="$1"
    local total="$2"
    local state_file="${STATE_DIR}/post-create.installed"

    iact_log_step "$current" "$total" "Marcando instalación como completada"

    if date --iso-8601=seconds > "$state_file"; then
        iact_log_success "Post-create completado"
        return 0
    else
        iact_log_warning "No se pudo crear archivo de estado"
        return 0
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    iact_log_header "Post-Create Setup"
    iact_log_info "Iniciando configuración del DevContainer"

    # Define steps array (auto-calculated)
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
        iact_log_success "✅ Post-create completado exitosamente"
        return 0
    else
        iact_log_error "❌ Post-create completado con errores:"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        return 1
    fi
}

# Execute main
main "$@"