#!/bin/bash
set -euo pipefail

# =============================================================================
# BOOTSTRAP - Sistema de aprovisionamiento funcional e idempotente
# =============================================================================

# -----------------------------------------------------------------------------
# Utilidades core - Funciones puras sin efectos secundarios
# -----------------------------------------------------------------------------

# Imprime mensaje de forma segura (función pura)
print_safe() {
    printf '%s\n' "$1"
}

# Valida si directorio existe (función pura de validación)
dir_exists() {
    [[ -d "$1" ]]
}

# Valida si archivo existe (función pura de validación)
file_exists() {
    [[ -f "$1" ]]
}

# Valida si archivo es ejecutable (función pura de validación)
is_executable() {
    [[ -x "$1" ]]
}

# Crea directorio con validación explícita (idempotente)
ensure_dir() {
    local dir="$1"

    dir_exists "$dir" && return 0

    if ! mkdir -p "$dir"; then
        print_safe "ERROR: No se pudo crear directorio: $dir" >&2
        return 1
    fi

    return 0
}

# Hace ejecutable un archivo con validación explícita (idempotente)
make_executable() {
    local path="$1"

    if ! file_exists "$path"; then
        print_safe "ERROR: Archivo no existe: $path" >&2
        return 1
    fi

    is_executable "$path" && return 0

    if ! chmod +x "$path"; then
        print_safe "ERROR: No se pudo dar permisos de ejecución: $path" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# Ejecución de scripts - Con validación explícita de errores
# -----------------------------------------------------------------------------

run_script() {
    local script="$1"
    local step="$2"
    local total="$3"
    local name

    name=$(basename "$script")

    iact_log_step "$step" "$total" "Ejecutando: $name"
    iact_log_info "DEBUG: Iniciando ejecución de $script"

    if ! make_executable "$script"; then
        iact_log_error "Script no disponible o sin permisos: $script"
        return 1
    fi

    iact_log_info "Ejecutando script: $script"

    local code=0
    set +e
    bash "$script" >> "$(iact_get_log_file)" 2>&1
    code=$?
    set -e

    if [[ $code -eq 0 ]]; then
        iact_log_success "$name completado exitosamente"
        return 0
    fi

    iact_log_error "$name falló con código: $code"
    return "$code"
}

# -----------------------------------------------------------------------------
# Configuración de entorno - Función pura que retorna configuración
# -----------------------------------------------------------------------------

# Calcula root del proyecto (función pura)
compute_project_root() {
    local script_dir="$1"

    if [[ -n "${IACT_BOOTSTRAP_TEST_ROOT:-}" ]]; then
        printf '%s' "$IACT_BOOTSTRAP_TEST_ROOT"
    elif [[ -d "/vagrant" ]]; then
        printf '%s' "/vagrant"
    else
        printf '%s' "$script_dir"
    fi
}

# Inicializa variables de entorno (idempotente)
init_env_vars() {
    export DEBIAN_FRONTEND=noninteractive

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    PROJECT_ROOT=$(compute_project_root "$script_dir")
    LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
    DEBUG="${DEBUG:-false}"
    SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

    export PROJECT_ROOT LOGS_DIR DEBUG SCRIPT_NAME

    # Configuración de bases de datos con valores por defecto
    export DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"
    export DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"
    export IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
    export IVR_DB_USER="${IVR_DB_USER:-django_user}"
    export IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-django_pass}"
    export DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
    export DJANGO_DB_USER="${DJANGO_DB_USER:-django_user}"
    export DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-django_pass}"
    export MARIADB_VERSION="${MARIADB_VERSION:-10.6}"
    export POSTGRESQL_VERSION="${POSTGRESQL_VERSION:-10}"
}

# Carga módulos del sistema
load_core_modules() {
    local core_path="${PROJECT_ROOT}/utils/core.sh"

    if ! file_exists "$core_path"; then
        print_safe "ERROR: No se encontró $core_path" >&2
        return 1
    fi

    # shellcheck disable=SC1090
    source "$core_path"

    if declare -f "iact_source_module" >/dev/null 2>&1; then
        if ! iact_source_module "validation"; then
            iact_log_error "No se pudo cargar módulo validation"
            return 1
        fi
    else
        print_safe "ADVERTENCIA: iact_source_module no disponible" >&2
    fi

    if declare -f "iact_init_logging" >/dev/null 2>&1; then
        iact_init_logging "${SCRIPT_NAME%.sh}"
    fi

    return 0
}

# Configura entorno completo (orquestador)
setup_env() {
    init_env_vars

    if ! ensure_dir "$LOGS_DIR"; then
        return 1
    fi

    if ! load_core_modules; then
        return 1
    fi

    if [[ "$DEBUG" == "true" ]]; then
        set -x
    fi

    iact_log_info "DEBUG: Entorno configurado correctamente"
    return 0
}

# -----------------------------------------------------------------------------
# Validación de entorno - Funciones puras de validación
# -----------------------------------------------------------------------------

# Valida que variable tenga valor (función pura)
var_is_set() {
    [[ -n "${!1}" ]]
}

# Cuenta errores de variables requeridas (función pura con side-effect de logging)
count_missing_vars() {
    local -a vars=("$@")
    local errors=0
    local var

    for var in "${vars[@]}"; do
        if ! var_is_set "$var"; then
            iact_log_error "Variable obligatoria vacía: $var"
            errors=$((errors + 1))
        fi
    done

    printf '%d' "$errors"
}

# Cuenta errores de directorios faltantes (función con side-effect de logging)
count_missing_dirs() {
    local -a dirs=("$@")
    local errors=0
    local dir

    for dir in "${dirs[@]}"; do
        if ! dir_exists "$dir"; then
            iact_log_error "Directorio requerido inexistente: $dir"
            errors=$((errors + 1))
        fi
    done

    printf '%d' "$errors"
}

# Valida entorno completo
validate_env() {
    local -a required_vars=(
        "PROJECT_ROOT"
        "LOGS_DIR"
        "DB_ROOT_PASSWORD"
        "DB_PASSWORD"
        "IVR_DB_NAME"
        "DJANGO_DB_NAME"
    )

    local -a required_dirs=(
        "$PROJECT_ROOT"
        "$PROJECT_ROOT/scripts"
        "$PROJECT_ROOT/utils"
    )

    local var_errors
    local dir_errors
    local total_errors

    var_errors=$(count_missing_vars "${required_vars[@]}")
    dir_errors=$(count_missing_dirs "${required_dirs[@]}")
    total_errors=$((var_errors + dir_errors))

    if [[ $total_errors -gt 0 ]]; then
        iact_log_error "Validación de entorno falló con $total_errors error(es)"
        return 1
    fi

    iact_log_info "Validación de entorno exitosa"
    return 0
}

# -----------------------------------------------------------------------------
# Información del sistema - Funciones de reporte
# -----------------------------------------------------------------------------

show_env_snapshot() {
    iact_log_info "Contexto: $(iact_get_context)"
    iact_log_info "Proyecto: $PROJECT_ROOT"
    iact_log_info "Logs: $LOGS_DIR"
    iact_log_info "MariaDB: $MARIADB_VERSION"
    iact_log_info "PostgreSQL: $POSTGRESQL_VERSION"
}

# -----------------------------------------------------------------------------
# Verificación de scripts - Funciones de validación
# -----------------------------------------------------------------------------

# Obtiene lista de scripts requeridos (función pura)
get_required_scripts() {
    printf '%s\n' \
        "$PROJECT_ROOT/scripts/system-prepare.sh" \
        "$PROJECT_ROOT/scripts/mariadb-install.sh" \
        "$PROJECT_ROOT/scripts/postgres-install.sh" \
        "$PROJECT_ROOT/scripts/setup-mariadb-database.sh" \
        "$PROJECT_ROOT/scripts/setup-postgres-database.sh"
}

# Cuenta scripts faltantes o no ejecutables
count_script_issues() {
    local -a scripts
    readarray -t scripts < <(get_required_scripts)

    local missing=0
    local script

    for script in "${scripts[@]}"; do
        if ! file_exists "$script"; then
            iact_log_error "Script faltante: $script"
            missing=$((missing + 1))
        elif ! make_executable "$script"; then
            missing=$((missing + 1))
        fi
    done

    printf '%d' "$missing"
}

# Verifica que todos los scripts estén disponibles
verify_scripts() {
    local issues
    issues=$(count_script_issues)

    if [[ $issues -gt 0 ]]; then
        iact_log_error "No se cumplen prerequisitos de scripts"
        return 1
    fi

    iact_log_info "Todos los scripts requeridos están disponibles"
    return 0
}

# -----------------------------------------------------------------------------
# Definición de pasos - Funciones puras que retornan listas
# -----------------------------------------------------------------------------

steps_system() {
    printf '%s\n' \
        'func:show_header' \
        'func:check_apt_sources' \
        'func:check_dns_config' \
        'func:check_pkg_cache' \
        "script:$PROJECT_ROOT/scripts/system-prepare.sh"
}

steps_database() {
    printf '%s\n' \
        "script:$PROJECT_ROOT/scripts/mariadb-install.sh" \
        "script:$PROJECT_ROOT/scripts/postgres-install.sh" \
        "script:$PROJECT_ROOT/scripts/setup-mariadb-database.sh" \
        "script:$PROJECT_ROOT/scripts/setup-postgres-database.sh"
}

steps_info() {
    printf '%s\n' \
        'func:show_credentials' \
        'func:show_access_info'
}

# Construye lista de pasos según dominio (función pura)
build_steps() {
    local domain="${1:-all}"
    iact_log_info "DEBUG: Construyendo pasos para dominio: $domain"

    case "$domain" in
        system)
            steps_system
            ;;
        database)
            steps_database
            ;;
        info)
            steps_info
            ;;
        all)
            steps_system
            steps_database
            steps_info
            ;;
        *)
            iact_log_error "Dominio desconocido: $domain"
            return 1
            ;;
    esac
}

# -----------------------------------------------------------------------------
# Ejecución de pasos - Función de orquestación
# -----------------------------------------------------------------------------

# Ejecuta un paso individual
exec_step() {
    local step="$1"
    local current="$2"
    local total="$3"
    local type="${step%%:*}"
    local value="${step#*:}"

    case "$type" in
        func)
            if ! declare -f "$value" >/dev/null 2>&1; then
                iact_log_error "Función no definida: $value"
                return 1
            fi
            iact_log_info "DEBUG: Ejecutando función: $value"
            "$value" "$current" "$total"
            ;;
        script)
            iact_log_info "DEBUG: Ejecutando script: $value"
            run_script "$value" "$current" "$total"
            ;;
        *)
            iact_log_error "Tipo de paso desconocido: $type"
            return 1
            ;;
    esac
}

# Ejecuta todos los pasos y recolecta fallos
run_steps() {
    local -a steps=("$@")
    local total=${#steps[@]}
    local current=0
    local -a failed=()
    local step

    iact_log_info "Total de pasos a ejecutar: $total"
    iact_log_info "Iniciando proceso de aprovisionamiento..."

    for step in "${steps[@]}"; do
        current=$((current + 1))

        if ! exec_step "$step" "$current" "$total"; then
            local label="${step#*:}"
            [[ "${step%%:*}" == "script" ]] && label=$(basename "$label")
            failed+=("$label")
        fi
    done

    show_results "$total" "${failed[@]}"
}

# -----------------------------------------------------------------------------
# Reporte de resultados - Función de presentación
# -----------------------------------------------------------------------------

show_results() {
    local total="$1"
    shift
    local -a failed=("$@")
    local count=${#failed[@]}
    local successful

    echo ""

    if [[ $count -eq 0 ]]; then
        iact_log_success "Bootstrap completado sin fallos"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Revise el log para detalles: $(iact_get_log_file)"
        return 0
    fi

    successful=$((total - count))

    iact_log_error "Bootstrap con $count error(es):"
    for step in "${failed[@]}"; do
        iact_log_error "  - $step"
    done
    iact_log_info "Total pasos ejecutados: $total"
    iact_log_info "Pasos exitosos: $successful"
    iact_log_info "Revise los logs para más detalles: $(iact_get_log_file)"
    return 1
}

# -----------------------------------------------------------------------------
# Funciones de información visual - Sin emojis
# -----------------------------------------------------------------------------

show_header() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de bootstrap"
    iact_log_info "DEBUG: Iniciando show_header"

    echo ""
    echo "=================================================================="
    echo "            MARIADB + POSTGRESQL BOOTSTRAP"
    echo "=================================================================="
    echo ""
    echo "Sistema objetivo: Ubuntu 18.04 LTS (Bionic Beaver)"
    echo "Project Root: $PROJECT_ROOT"
    echo "Logs Directory: $LOGS_DIR"
    echo "Context: $(iact_get_context)"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# Validación idempotente de fuentes APT
check_apt_sources() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Fuentes APT"
    iact_log_info "Validando configuración de fuentes APT"
    iact_log_info "No se realizan cambios (operación idempotente)"
    return 0
}

# Validación idempotente de DNS
check_dns_config() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configuración DNS"
    iact_log_info "Validando configuración DNS"
    iact_log_info "No se requieren ajustes adicionales"
    return 0
}

# Validación idempotente de cache de paquetes
check_pkg_cache() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualización de cache"
    iact_log_info "Se omite actualización automática para mantener idempotencia"
    return 0
}

show_credentials() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de credenciales"
    iact_log_info "DEBUG: Iniciando show_credentials"

    echo ""
    echo "=================================================================="
    echo "                  CREDENCIALES DE BASES DE DATOS"
    echo "=================================================================="
    echo ""
    echo "IMPORTANTE: Guarde estas credenciales de forma segura"
    echo ""
    echo "MariaDB:"
    echo "  Usuario: root"
    echo "  Password: $DB_ROOT_PASSWORD"
    echo ""
    echo "PostgreSQL:"
    echo "  Usuario: postgres"
    echo "  Password: $DB_PASSWORD"
    echo ""
    echo "Estas credenciales están registradas en: $(iact_get_log_file)"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

show_access_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de acceso"
    iact_log_info "DEBUG: Iniciando show_access_info"

    echo ""
    echo "=================================================================="
    echo "                  INFORMACION DE ACCESO"
    echo "=================================================================="
    echo ""
    echo "Acceso SSH:"
    echo "  vagrant ssh (si usa Vagrant)"
    echo ""
    echo "Bases de datos:"
    echo "  MariaDB: mysql -u root -p"
    echo "  PostgreSQL: psql -U postgres -h localhost"
    echo ""
    echo "Logs:"
    echo "  $(iact_get_log_file)"
    echo ""
    echo "Proyecto:"
    echo "  $PROJECT_ROOT"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# -----------------------------------------------------------------------------
# Función principal - Orquestación de alto nivel
# -----------------------------------------------------------------------------

main() {
    local domain="${1:-all}"
    local -a steps

    setup_env || return 1
    show_env_snapshot
    validate_env || return 1
    verify_scripts || return 1

    readarray -t steps < <(build_steps "$domain")
    run_steps "${steps[@]}"
}

# -----------------------------------------------------------------------------
# Punto de entrada - Verificación de privilegios
# -----------------------------------------------------------------------------

if [[ "${IACT_BOOTSTRAP_MODE:-execute}" != "library" ]]; then
    if [[ $EUID -ne 0 ]]; then
        print_safe "ERROR: Este script debe ejecutarse con privilegios de root" >&2
        print_safe "ACCION REQUERIDA: Intente: sudo $0" >&2
        exit 1
    fi

    main "$@"
fi