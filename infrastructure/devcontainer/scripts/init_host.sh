#!/usr/bin/env bash
#
# init_host.sh - DevContainer Pre-Initialization
#
# Ejecuta validaciones universales en el HOST antes de construir el contenedor.
# Este script debe funcionar en:
#   - GitHub Codespaces
#   - VS Code Local + Docker Desktop
#   - VS Code Remote - SSH
#
# Lifecycle: initializeCommand (HOST)
# Frecuencia: MULTIPLE (creacion + reinicios)
# Criterio: CRITICO - Si falla, detener
#

set -euo pipefail

# =============================================================================
# CONFIGURACION
# =============================================================================

# Detectar el directorio del proyecto (desde donde se ejecuta el script)
PROJECT_ROOT="$(pwd)"

# Colores para output (solo si terminal soporta)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Contadores
ERRORS=0
WARNINGS=0

# =============================================================================
# FUNCIONES
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_ok() {
    echo -e "${GREEN}[OK]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    ERRORS=$((ERRORS + 1))
}

print_separator() {
    echo "==================================================="
}

# =============================================================================
# DETECCION DE CONTEXTO
# =============================================================================

detect_context() {
    log_info "Detecting execution context..."

    if [[ -n "${CODESPACES:-}" ]]; then
        CONTEXT="codespaces"
        log_ok "Running in GitHub Codespaces"
    elif [[ -n "${REMOTE_CONTAINERS:-}" ]]; then
        CONTEXT="vscode-remote"
        log_ok "Running in VS Code Remote"
    else
        CONTEXT="local"
        log_ok "Running locally"
    fi

    log_info "OS: $(uname -s)"
    log_info "Project root: ${PROJECT_ROOT}"
}

# =============================================================================
# VALIDACION DE ESTRUCTURA DE DIRECTORIOS
# =============================================================================

validate_directory_structure() {
    log_info "Validating directory structure..."

    local required_dirs=(
        "infrastructure/devcontainer"
        "infrastructure/devcontainer/scripts"
        "api/callcentersite"
    )

    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "${PROJECT_ROOT}/${dir}" ]]; then
            log_error "Required directory not found: ${dir}"
        else
            log_ok "Directory found: ${dir}"
        fi
    done
}

# =============================================================================
# VALIDACION DE SCRIPTS DE LIFECYCLE
# =============================================================================

validate_lifecycle_scripts() {
    log_info "Validating lifecycle scripts..."

    local required_scripts=(
        "infrastructure/devcontainer/scripts/on_create.sh"
        "infrastructure/devcontainer/scripts/update_content.sh"
        "infrastructure/devcontainer/scripts/post_create.sh"
        "infrastructure/devcontainer/scripts/post_start.sh"
    )

    for script in "${required_scripts[@]}"; do
        local script_path="${PROJECT_ROOT}/${script}"

        if [[ ! -f "$script_path" ]]; then
            log_error "Required script not found: ${script}"
        else
            # Verificar si es ejecutable
            if [[ ! -x "$script_path" ]]; then
                log_warn "Script not executable: ${script}"
                log_info "Making executable: ${script}"
                chmod +x "$script_path" || log_error "Failed to make executable: ${script}"
            fi
            log_ok "Script found and executable: ${script}"
        fi
    done
}

# =============================================================================
# VALIDACION DE ARCHIVOS CRITICOS
# =============================================================================

ensure_required_file() {
    local relative_path="$1"
    local expected_path="${PROJECT_ROOT}/${relative_path}"

    # Si el archivo existe con el nombre esperado, terminar rápido
    if [[ -f "$expected_path" ]]; then
        log_ok "File found: ${relative_path}"
        return 0
    fi

    # Buscar el archivo ignorando mayúsculas/minúsculas para tolerar variaciones
    local directory="${expected_path%/*}"
    local filename="${relative_path##*/}"

    if [[ ! -d "$directory" ]]; then
        log_error "Critical directory not found for: ${relative_path}"
        return 1
    fi

    local found_path
    found_path=$(find "$directory" -maxdepth 1 -type f -iname "$filename" -print -quit)

    if [[ -n "$found_path" ]]; then
        local relative_found="${found_path#${PROJECT_ROOT}/}"

        if [[ "$relative_found" != "$relative_path" ]]; then
            log_warn "Nombre detectado distinto para ${relative_path}: ${relative_found}"
        fi

        log_ok "File found: ${relative_found}"
        return 0
    fi

    log_error "Critical file not found: ${relative_path}"
    return 1
}

validate_critical_files() {
    log_info "Validating critical files..."

    local required_files=(
        "api/callcentersite/manage.py"
        ".devcontainer/docker_compose.yml"
        ".devcontainer/Dockerfile"
        ".devcontainer/devcontainer.json"
    )

    for file in "${required_files[@]}"; do
        ensure_required_file "$file"
    done
}

# =============================================================================
# VALIDACION DE REQUIREMENTS
# =============================================================================

validate_requirements() {
    log_info "Validating requirements files..."

    local req_dir="${PROJECT_ROOT}/api/callcentersite/requirements"

    if [[ ! -d "$req_dir" ]]; then
        log_error "Requirements directory not found: api/callcentersite/requirements"
        return
    fi

    # Validar base.txt (requerido)
    if [[ ! -f "${req_dir}/base.txt" ]]; then
        log_error "Base requirements not found: requirements/base.txt"
    else
        log_ok "Base requirements found: requirements/base.txt"
    fi

    # Validar dev.txt (requerido)
    if [[ ! -f "${req_dir}/dev.txt" ]]; then
        log_error "Development requirements not found: requirements/dev.txt"
    else
        log_ok "Development requirements found: requirements/dev.txt"
    fi

    # Validar test.txt (opcional)
    if [[ ! -f "${req_dir}/test.txt" ]]; then
        log_warn "Testing requirements not found: requirements/test.txt (non-critical)"
    else
        log_ok "Testing requirements found: requirements/test.txt"
    fi
}

# =============================================================================
# CREACION DE DIRECTORIOS NECESARIOS
# =============================================================================

create_required_directories() {
    log_info "Creating required directories..."

    local directories_to_create=(
        "infrastructure/devcontainer/logs"
        "infrastructure/state"
    )

    for dir in "${directories_to_create[@]}"; do
        local dir_path="${PROJECT_ROOT}/${dir}"
        if [[ ! -d "$dir_path" ]]; then
            mkdir -p "$dir_path"
            log_ok "Created directory: ${dir}"
        else
            log_ok "Directory already exists: ${dir}"
        fi
    done
}

# =============================================================================
# SETUP DE ENV FILE
# =============================================================================

setup_env_file() {
    log_info "Setting up environment file..."

    local env_example="${PROJECT_ROOT}/api/callcentersite/env.example"
    local env_file="${PROJECT_ROOT}/api/callcentersite/env"
    local devcontainer_env_example="${PROJECT_ROOT}/.devcontainer/.env.example"
    local devcontainer_env_file="${PROJECT_ROOT}/.devcontainer/.env"

    # Si ya existe env, no hacer nada
    if [[ -f "$env_file" ]]; then
        log_ok "Environment file already exists: api/callcentersite/env"
        return
    fi

    # Si existe env.example, copiarlo
    if [[ -f "$env_example" ]]; then
        cp "$env_example" "$env_file"
        log_ok "Created env from env.example"
    else
        log_warn "env.example not found, creating basic env file"

        # Crear env basico
        cat > "$env_file" << 'EOF'
# Django Environment Variables
# This file is for LOCAL developer configuration only
# Most variables come from docker_compose.yml

# Uncomment and customize as needed:
# DEBUG=True
# SECRET_KEY=your-local-secret-key

# Developer-specific settings:
# ENABLE_DEBUG_TOOLBAR=True
# ENABLE_SILK=True
EOF
        log_ok "Created basic env file"
    fi

    if [[ -f "$devcontainer_env_file" ]]; then
        log_ok "DevContainer env file already exists: .devcontainer/.env"
    elif [[ -f "$devcontainer_env_example" ]]; then
        cp "$devcontainer_env_example" "$devcontainer_env_file"
        log_ok "Created .devcontainer/.env from .env.example"
    else
        log_warn "DevContainer .env.example not found; skipping .devcontainer/.env creation"
    fi
}

# =============================================================================
# VALIDACION DE UTILS (OPCIONAL)
# =============================================================================

validate_utils() {
    log_info "Validating utils directory..."

    local utils_dir="${PROJECT_ROOT}/infrastructure/devcontainer/utils"

    if [[ ! -d "$utils_dir" ]]; then
        log_warn "Utils directory not found (scripts will use fallback)"
        return
    fi

    log_ok "Utils directory found"

    # Validar que core.sh existe y es valido
    local core_sh="${utils_dir}/core.sh"
    if [[ -f "$core_sh" ]]; then
        # Verificar que no esta corrupto (tiene contenido)
        if [[ -s "$core_sh" ]]; then
            log_ok "Utils core.sh is available"
        else
            log_warn "Utils core.sh is empty"
        fi
    else
        log_warn "Utils core.sh not found (non-critical)"
    fi
}

# =============================================================================
# CONTROL DE IDEMPOTENCIA
# =============================================================================

mark_initialization() {
    log_info "Marking initialization..."

    local state_file="${PROJECT_ROOT}/.devcontainer/.init_completed"
    local state_dir="${PROJECT_ROOT}/.devcontainer"

    # Crear directorio si no existe
    mkdir -p "$state_dir"

    # Timestamp actual
    local timestamp=$(date --iso-8601=seconds 2>/dev/null || date +"%Y-%m-%dT%H:%M:%S%z")

    if [[ ! -f "$state_file" ]]; then
        # Primera inicializacion
        {
            echo "# DevContainer Initialization State"
            echo "first_init: ${timestamp}"
            echo "context: ${CONTEXT}"
            echo "os: $(uname -s)"
        } > "$state_file"
        log_ok "First-time initialization completed at: ${timestamp}"
    else
        # Re-inicializacion
        echo "re_init: ${timestamp}" >> "$state_file"
        local first_init=$(grep "first_init:" "$state_file" | cut -d' ' -f2)
        log_ok "Re-initialization completed (first init: ${first_init})"
    fi
}

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print_summary() {
    echo ""
    print_separator

    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        log_ok "Pre-initialization completed successfully"
        log_info "Errors: 0, Warnings: 0"
    elif [[ $ERRORS -eq 0 ]]; then
        log_ok "Pre-initialization completed with warnings"
        log_info "Errors: 0, Warnings: ${WARNINGS}"
    else
        log_error "Pre-initialization completed with errors"
        log_info "Errors: ${ERRORS}, Warnings: ${WARNINGS}"
    fi

    print_separator
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    print_separator
    echo "DEVCONTAINER PRE-INITIALIZATION"
    print_separator
    echo ""

    # Ejecutar todas las validaciones
    detect_context
    echo ""

    echo "[STEP 1/8] Validating directory structure..."
    validate_directory_structure
    echo ""

    echo "[STEP 2/8] Validating lifecycle scripts..."
    validate_lifecycle_scripts
    echo ""

    echo "[STEP 3/8] Validating critical files..."
    validate_critical_files
    echo ""

    echo "[STEP 4/8] Validating requirements..."
    validate_requirements
    echo ""

    echo "[STEP 5/8] Creating required directories..."
    create_required_directories
    echo ""

    echo "[STEP 6/8] Setting up environment file..."
    setup_env_file
    echo ""

    echo "[STEP 7/8] Validating utils..."
    validate_utils
    echo ""

    echo "[STEP 8/8] Marking initialization..."
    mark_initialization
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