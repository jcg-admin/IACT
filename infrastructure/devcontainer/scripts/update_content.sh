#!/usr/bin/env bash
#
# update_content.sh - DevContainer Dependencies Update
#
# Instala y actualiza dependencias de Python desde requirements files.
# Este script es COMPLETAMENTE IDEMPOTENTE y puede ejecutarse N veces.
#
# Lifecycle: updateContentCommand (CONTAINER - múltiples veces)
# Frecuencia: MULTIPLE (rebuild, actualizar contenido)
# Criterio: Instalar dependencias - debe ser idempotente
#

set -euo pipefail

# =============================================================================
# CONFIGURACION
# =============================================================================

# Detectar directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/../utils"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
DJANGO_DIR="${PROJECT_ROOT}/api/callcentersite"
REQ_DIR="${DJANGO_DIR}/requirements"
STATE_DIR="${PROJECT_ROOT}/infrastructure/state"

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

if ! iact_source_module "python"; then
    echo "Error: No se pudo cargar python.sh" >&2
    exit 1
fi

# =============================================================================
# INICIALIZACION
# =============================================================================

# Inicializar logging
if ! iact_init_logging "update-content"; then
    echo "Warning: No se pudo inicializar logging" >&2
fi

iact_log_header "DEVCONTAINER - UPDATE CONTENT (Dependencies)"

# Variables de control
ERRORS=0
WARNINGS=0
PACKAGES_INSTALLED=0

# =============================================================================
# FUNCIONES
# =============================================================================

increment_errors() {
    ((ERRORS++))
}

increment_warnings() {
    ((WARNINGS++))
}

increment_packages() {
    ((PACKAGES_INSTALLED++))
}

# -----------------------------------------------------------------------------
# get_file_hash
# Description: Get hash of a file for change detection
# Arguments: $1 - file path
# Returns: Hash via stdout, or empty if file doesn't exist
# -----------------------------------------------------------------------------
get_file_hash() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo ""
        return 1
    fi

    # Usar md5sum o sha256sum según disponibilidad
    if command -v md5sum >/dev/null 2>&1; then
        md5sum "$file" | awk '{print $1}'
    elif command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$file" | awk '{print $1}'
    else
        # Fallback: usar wc para obtener algo único
        wc -c < "$file"
    fi
}

# -----------------------------------------------------------------------------
# requirements_changed
# Description: Check if requirements file changed since last install
# Arguments: $1 - requirements file path
# Returns: 0 if changed, 1 if not changed
# -----------------------------------------------------------------------------
requirements_changed() {
    local req_file="$1"
    local req_basename
    req_basename=$(basename "$req_file")
    local state_file="${STATE_DIR}/requirements_${req_basename}.hash"

    # Si no existe el archivo de estado, asumir que cambió
    if [[ ! -f "$state_file" ]]; then
        return 0
    fi

    # Obtener hash actual y guardado
    local current_hash
    current_hash=$(get_file_hash "$req_file")
    local saved_hash
    saved_hash=$(cat "$state_file" 2>/dev/null || echo "")

    # Comparar hashes
    if [[ "$current_hash" != "$saved_hash" ]]; then
        return 0  # Cambió
    else
        return 1  # No cambió
    fi
}

# -----------------------------------------------------------------------------
# save_requirements_hash
# Description: Save hash of requirements file for future comparison
# Arguments: $1 - requirements file path
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
save_requirements_hash() {
    local req_file="$1"
    local req_basename
    req_basename=$(basename "$req_file")
    local state_file="${STATE_DIR}/requirements_${req_basename}.hash"

    # Crear directorio de estado si no existe
    iact_create_dir "$STATE_DIR" || return 1

    # Guardar hash
    local current_hash
    current_hash=$(get_file_hash "$req_file")

    if [[ -n "$current_hash" ]]; then
        echo "$current_hash" > "$state_file"
        return 0
    else
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_requirements_file
# Description: Install packages from requirements file (idempotent)
# Arguments: $1 - requirements file path, $2 - description
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
install_requirements_file() {
    local req_file="$1"
    local description="$2"

    # Validar que el archivo existe y es válido
    if ! iact_validate_requirements_file "$req_file"; then
        iact_log_error "Requirements file invalid: $req_file"
        increment_errors
        return 1
    fi

    # Check si cambió desde última instalación
    if requirements_changed "$req_file"; then
        iact_log_info "Requirements changed, installing: $description"
    else
        iact_log_info "Requirements unchanged, checking installation: $description"

        # Verificar que los paquetes realmente están instalados
        # (por si el contenedor fue reconstruido)
        local first_package
        first_package=$(grep -v '^#' "$req_file" | grep -v '^$' | head -n 1 | cut -d'=' -f1 | cut -d'>' -f1 | cut -d'<' -f1 | tr -d ' ')

        if [[ -n "$first_package" ]]; then
            if iact_pip_package_installed "$first_package"; then
                iact_log_success "Requirements already installed and verified: $description"
                return 0
            else
                iact_log_warning "Requirements hash matches but packages missing, reinstalling: $description"
            fi
        fi
    fi

    # Instalar requirements
    iact_log_info "Installing packages from: $req_file"

    if iact_pip_install_requirements "$req_file"; then
        iact_log_success "Requirements installed successfully: $description"

        # Guardar hash para próxima vez
        if save_requirements_hash "$req_file"; then
            iact_log_info "Requirements hash saved"
        fi

        increment_packages
        return 0
    else
        iact_log_error "Failed to install requirements: $description"
        increment_errors
        return 1
    fi
}

# =============================================================================
# STEP 1: VALIDAR ENTORNO
# =============================================================================

validate_environment() {
    iact_log_step 1 6 "Validating environment"

    # Validar Python
    if ! iact_validate_python_installed; then
        iact_log_error "Python no está instalado"
        increment_errors
        return 1
    fi

    local python_version
    python_version=$(iact_python_get_version)
    iact_log_success "Python available: $python_version"

    # Validar pip
    if ! iact_validate_pip_installed; then
        iact_log_error "pip no está instalado"
        increment_errors
        return 1
    fi

    local pip_cmd
    pip_cmd=$(iact_pip_get_command)
    iact_log_success "pip available: $pip_cmd"

    # Validar directorio de requirements
    if ! iact_validate_dir_exists "$REQ_DIR"; then
        iact_log_error "Requirements directory not found: $REQ_DIR"
        increment_errors
        return 1
    fi

    iact_log_success "Requirements directory found: $REQ_DIR"

    iact_log_success "Environment validated"
}

# =============================================================================
# STEP 2: ACTUALIZAR PIP
# =============================================================================

update_pip() {
    iact_log_step 2 6 "Updating pip to latest version"

    local pip_cmd
    pip_cmd=$(iact_pip_get_command)

    iact_log_info "Updating pip..."

    if $pip_cmd install --upgrade pip 2>&1 | grep -v "Requirement already satisfied"; then
        iact_log_success "pip updated successfully"

        # Mostrar versión
        local pip_version
        pip_version=$($pip_cmd --version | awk '{print $2}')
        iact_log_info "pip version: $pip_version"
    else
        iact_log_warning "pip update completed with warnings"
        increment_warnings
    fi
}

# =============================================================================
# STEP 3: INSTALAR BASE REQUIREMENTS
# =============================================================================

install_base_requirements() {
    iact_log_step 3 6 "Installing base requirements"

    local base_req="${REQ_DIR}/base.txt"

    if ! install_requirements_file "$base_req" "Base requirements"; then
        iact_log_error "Failed to install base requirements"
        return 1
    fi

    iact_log_success "Base requirements completed"
}

# =============================================================================
# STEP 4: INSTALAR DEV REQUIREMENTS
# =============================================================================

install_dev_requirements() {
    iact_log_step 4 6 "Installing development requirements"

    local dev_req="${REQ_DIR}/dev.txt"

    if ! install_requirements_file "$dev_req" "Development requirements"; then
        iact_log_error "Failed to install development requirements"
        return 1
    fi

    iact_log_success "Development requirements completed"
}

# =============================================================================
# STEP 5: INSTALAR TEST REQUIREMENTS (OPCIONAL)
# =============================================================================

install_test_requirements() {
    iact_log_step 5 6 "Installing test requirements (optional)"

    local test_req="${REQ_DIR}/test.txt"

    # Test requirements es opcional
    if ! iact_validate_file_exists "$test_req"; then
        iact_log_info "Test requirements not found (optional), skipping"
        return 0
    fi

    if ! install_requirements_file "$test_req" "Test requirements"; then
        iact_log_warning "Failed to install test requirements (non-critical)"
        increment_warnings
        return 0
    fi

    iact_log_success "Test requirements completed"
}

# =============================================================================
# STEP 6: VALIDAR DJANGO INSTALADO
# =============================================================================

validate_django_installation() {
    iact_log_step 6 6 "Validating Django installation"

    # Validar que Django está instalado
    if ! iact_validate_django_installed; then
        iact_log_error "Django no está instalado después de instalar requirements"
        increment_errors
        return 1
    fi

    local django_version
    django_version=$(iact_django_get_version)
    iact_log_success "Django installed: $django_version"

    # Validar versión mínima
    if ! iact_validate_django_version "4.2"; then
        iact_log_error "Django version debe ser >= 4.2"
        increment_errors
        return 1
    fi

    iact_log_success "Django version meets requirements (>= 4.2)"

    # Validar paquetes críticos
    local critical_packages=("psycopg2")
    for package in "${critical_packages[@]}"; do
        if iact_pip_package_installed "$package"; then
            iact_log_success "Critical package installed: $package"
        else
            iact_log_warning "Critical package missing: $package"
            increment_warnings
        fi
    done

    iact_log_success "Django installation validated"
}

# =============================================================================
# MARCAR COMPLETADO
# =============================================================================

mark_completed() {
    iact_log_info "Marking updateContent as completed"

    local state_file="${STATE_DIR}/update-content.completed"
    local timestamp
    timestamp=$(date --iso-8601=seconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S%z")

    # Crear directorio si no existe
    iact_create_dir "$(dirname "$state_file")"

    # Crear marker file
    {
        echo "# DevContainer updateContent Completion"
        echo "completed_at: ${timestamp}"
        echo "python_version: $(iact_python_get_version)"
        echo "django_version: $(iact_django_get_version)"
        echo "packages_installed: ${PACKAGES_INSTALLED}"
    } > "$state_file"

    iact_log_file_operation "updated" "$state_file"
}

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print_summary() {
    echo ""
    iact_log_separator

    iact_log_info "updateContent Summary:"
    iact_log_info "  Python: $(iact_python_get_version)"
    iact_log_info "  Django: $(iact_django_get_version 2>/dev/null || echo 'not installed')"
    iact_log_info "  pip: $(iact_pip_get_command)"
    iact_log_info "  Requirements sets processed: ${PACKAGES_INSTALLED}"

    echo ""

    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        iact_log_success "updateContent completed successfully"
        iact_log_info "Errors: 0, Warnings: 0"
    elif [[ $ERRORS -eq 0 ]]; then
        iact_log_success "updateContent completed with warnings"
        iact_log_info "Errors: 0, Warnings: ${WARNINGS}"
    else
        iact_log_error "updateContent completed with errors"
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
    validate_environment || true
    echo ""

    update_pip || true
    echo ""

    install_base_requirements || true
    echo ""

    install_dev_requirements || true
    echo ""

    install_test_requirements || true
    echo ""

    validate_django_installation || true
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