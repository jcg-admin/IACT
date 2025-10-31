#!/usr/bin/env bash
#
# on_create.sh - DevContainer Initial Setup
#
# Ejecuta setup básico DENTRO del contenedor por primera vez.
# Este script corre DESPUÉS de init_host.sh pero ANTES de update_content.sh
#
# Lifecycle: onCreateCommand (CONTAINER - primera vez)
# Frecuencia: UNA SOLA VEZ (creación del contenedor)
# Criterio: Setup básico - preparar el ambiente
#

set -euo pipefail

# =============================================================================
# CONFIGURACION
# =============================================================================

# Detectar directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/../utils"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

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

# Cargar logging (requerido)
if ! iact_source_module "logging"; then
    echo "Error: No se pudo cargar logging.sh" >&2
    exit 1
fi

# Cargar validation (requerido)
if ! iact_source_module "validation"; then
    echo "Error: No se pudo cargar validation.sh" >&2
    exit 1
fi

# Cargar python (requerido)
if ! iact_source_module "python"; then
    echo "Error: No se pudo cargar python.sh" >&2
    exit 1
fi

# =============================================================================
# INICIALIZACION
# =============================================================================

# Inicializar logging
if ! iact_init_logging "on-create"; then
    echo "Warning: No se pudo inicializar logging, continuando sin logs a archivo" >&2
fi

iact_log_header "DEVCONTAINER - INITIAL SETUP (onCreate)"

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
# STEP 1: VALIDAR CONTEXTO Y SISTEMA
# =============================================================================

validate_context() {
    iact_log_step 1 7 "Validating context and system"

    # Detectar contexto
    local context
    context=$(iact_get_context)
    iact_log_info "Execution context: $context"

    # Información del sistema
    local os_info
    os_info=$(iact_get_os_info)
    iact_log_info "OS: $os_info"

    # Memoria
    local memory
    memory=$(iact_get_memory_info)
    iact_log_info "Memory: $memory"

    # Espacio en disco
    local disk
    disk=$(iact_get_disk_info)
    iact_log_info "Disk: $disk"

    # Validar espacio en disco (mínimo 5GB)
    if ! iact_validate_disk_space 5; then
        iact_log_error "Espacio en disco insuficiente"
        increment_errors
        return 1
    fi

    iact_log_success "Context and system validated"
}

# =============================================================================
# STEP 2: VALIDAR PYTHON Y PIP
# =============================================================================

validate_python_environment() {
    iact_log_step 2 7 "Validating Python environment"

    # Validar Python instalado
    if ! iact_validate_python_installed; then
        iact_log_error "Python no está instalado"
        increment_errors
        return 1
    fi

    local python_version
    python_version=$(iact_python_get_version)
    iact_log_success "Python installed: $python_version"

    # Validar versión mínima Python 3.11
    if ! iact_validate_python_version "3.11"; then
        iact_log_error "Python 3.11+ requerido"
        increment_errors
        return 1
    fi

    iact_log_success "Python version meets requirements (>= 3.11)"

    # Validar pip instalado
    if ! iact_validate_pip_installed; then
        iact_log_error "pip no está instalado"
        increment_errors
        return 1
    fi

    local pip_cmd
    pip_cmd=$(iact_pip_get_command)
    iact_log_success "pip installed: $pip_cmd"

    # Validar comandos adicionales
    local required_commands=("git" "curl")
    if iact_validate_commands_exist "${required_commands[@]}"; then
        iact_log_success "Required commands available: ${required_commands[*]}"
    else
        iact_log_warning "Some required commands are missing"
        increment_warnings
    fi

    iact_log_success "Python environment validated"
}

# =============================================================================
# STEP 3: VALIDAR ESTRUCTURA DEL PROYECTO
# =============================================================================

validate_project_structure() {
    iact_log_step 3 7 "Validating project structure"

    # Validar directorio del proyecto Django
    local django_dir="${PROJECT_ROOT}/api/callcentersite"

    if ! iact_validate_django_project "$django_dir"; then
        iact_log_error "Proyecto Django no válido: $django_dir"
        increment_errors
        return 1
    fi

    iact_log_success "Django project found: $django_dir"

    # Validar requirements directory
    local req_dir="${django_dir}/requirements"
    if ! iact_validate_dir_exists "$req_dir"; then
        iact_log_error "Directorio requirements no existe: $req_dir"
        increment_errors
        return 1
    fi

    iact_log_success "Requirements directory found: $req_dir"

    # Validar archivos de requirements
    local req_files=("base.txt" "dev.txt")
    for req_file in "${req_files[@]}"; do
        local req_path="${req_dir}/${req_file}"
        if iact_validate_requirements_file "$req_path"; then
            iact_log_success "Requirements file valid: requirements/${req_file}"
        else
            iact_log_error "Requirements file invalid: requirements/${req_file}"
            increment_errors
        fi
    done

    # Validar test.txt (opcional)
    if iact_validate_file_exists "${req_dir}/test.txt"; then
        if iact_validate_requirements_file "${req_dir}/test.txt"; then
            iact_log_success "Test requirements found: requirements/test.txt"
        else
            iact_log_warning "Test requirements file invalid"
            increment_warnings
        fi
    else
        iact_log_warning "Test requirements not found (optional)"
        increment_warnings
    fi

    iact_log_success "Project structure validated"
}

# =============================================================================
# STEP 4: CREAR DIRECTORIOS NECESARIOS
# =============================================================================

create_required_directories() {
    iact_log_step 4 7 "Creating required directories"

    local directories=(
        "${PROJECT_ROOT}/infrastructure/devcontainer/logs"
        "${PROJECT_ROOT}/infrastructure/state"
        "${PROJECT_ROOT}/.devcontainer"
    )

    for dir in "${directories[@]}"; do
        if iact_create_dir "$dir"; then
            if [[ -d "$dir" ]]; then
                iact_log_success "Directory ready: ${dir#$PROJECT_ROOT/}"
            fi
        else
            iact_log_error "No se pudo crear directorio: $dir"
            increment_errors
        fi
    done

    iact_log_success "Required directories created"
}

# =============================================================================
# STEP 5: SETUP GIT CONFIGURATION
# =============================================================================

setup_git_config() {
    iact_log_step 5 7 "Setting up Git configuration"

    # Verificar que git existe
    if ! iact_command_exists "git"; then
        iact_log_warning "Git no está instalado, skip configuración"
        increment_warnings
        return 0
    fi

    # Configuración básica de git (idempotente)
    if ! git config --global user.name >/dev/null 2>&1; then
        git config --global user.name "DevContainer User"
        iact_log_info "Git user.name set to: DevContainer User"
    else
        local git_user
        git_user=$(git config --global user.name)
        iact_log_info "Git user.name already set: $git_user"
    fi

    if ! git config --global user.email >/dev/null 2>&1; then
        git config --global user.email "devcontainer@localhost"
        iact_log_info "Git user.email set to: devcontainer@localhost"
    else
        local git_email
        git_email=$(git config --global user.email)
        iact_log_info "Git user.email already set: $git_email"
    fi

    # Configuración de safe.directory (para workspaces)
    git config --global --add safe.directory "$PROJECT_ROOT" 2>/dev/null || true
    iact_log_info "Git safe.directory configured"

    iact_log_success "Git configuration completed"
}

# =============================================================================
# STEP 6: VALIDAR CLIENTES DE BASE DE DATOS
# =============================================================================

validate_database_clients() {
    iact_log_step 6 7 "Validating database clients"

    # Validar PostgreSQL client
    if iact_validate_postgres_client; then
        iact_log_success "PostgreSQL client (psql) installed"
    else
        iact_log_warning "PostgreSQL client not installed"
        increment_warnings
    fi

    # Validar MariaDB client
    if iact_validate_mariadb_client; then
        iact_log_success "MariaDB client (mysql) installed"
    else
        iact_log_warning "MariaDB client not installed"
        increment_warnings
    fi

    iact_log_success "Database clients validated"
}

# =============================================================================
# STEP 7: MARCAR COMPLETADO
# =============================================================================

mark_completed() {
    iact_log_step 7 7 "Marking onCreate as completed"

    local state_file="${PROJECT_ROOT}/infrastructure/state/on-create.completed"
    local timestamp
    timestamp=$(date --iso-8601=seconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S%z")

    # Crear directorio si no existe
    iact_create_dir "$(dirname "$state_file")"

    # Crear marker file
    {
        echo "# DevContainer onCreate Completion"
        echo "completed_at: ${timestamp}"
        echo "context: $(iact_get_context)"
        echo "python_version: $(iact_python_get_version)"
        echo "project_root: ${PROJECT_ROOT}"
    } > "$state_file"

    iact_log_file_operation "created" "$state_file"
    iact_log_success "onCreate marked as completed"
}

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print_summary() {
    echo ""
    iact_log_separator

    iact_log_info "onCreate Summary:"
    iact_log_info "  Project Root: ${PROJECT_ROOT}"
    iact_log_info "  Context: $(iact_get_context)"
    iact_log_info "  Python: $(iact_python_get_version)"

    if iact_command_exists "git"; then
        iact_log_info "  Git User: $(git config --global user.name 2>/dev/null || echo 'not set')"
    fi

    echo ""

    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        iact_log_success "onCreate completed successfully"
        iact_log_info "Errors: 0, Warnings: 0"
    elif [[ $ERRORS -eq 0 ]]; then
        iact_log_success "onCreate completed with warnings"
        iact_log_info "Errors: 0, Warnings: ${WARNINGS}"
    else
        iact_log_error "onCreate completed with errors"
        iact_log_info "Errors: ${ERRORS}, Warnings: ${WARNINGS}"
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
    validate_context || true
    echo ""

    validate_python_environment || true
    echo ""

    validate_project_structure || true
    echo ""

    create_required_directories || true
    echo ""

    setup_git_config || true
    echo ""

    validate_database_clients || true
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