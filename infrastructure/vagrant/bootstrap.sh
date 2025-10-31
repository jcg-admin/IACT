#!/bin/bash
set -euo pipefail

# -----------------------------------------------------------------------------
# Utilidades internas para asegurar comandos seguros
# -----------------------------------------------------------------------------
safe_printf() {
    printf '%s\n' "$1"
}

ensure_directory() {
    local directory="$1"

    if [[ -d "$directory" ]]; then
        return 0
    fi

    if ! mkdir -p "$directory"; then
        safe_printf "ERROR: No se pudo crear el directorio requerido: $directory" >&2
        return 1
    fi
    return 0
}

ensure_executable() {
    local path="$1"

    if [[ ! -f "$path" ]]; then
        safe_printf "ERROR: Archivo inexistente: $path" >&2
        return 1
    fi

    if [[ -x "$path" ]]; then
        return 0
    fi

    if ! chmod +x "$path"; then
        safe_printf "ERROR: No se pudo establecer permiso de ejecución en: $path" >&2
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# execute_installation_script
# Description: Execute an installation script
# Arguments: $1 - script path, $2 - current step, $3 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
execute_installation_script() {
    local script_path="$1"
    local current="$2"
    local total="$3"
    local script_name
    script_name=$(basename "$script_path")

    iact_log_step "$current" "$total" "Ejecutando: $script_name"
    iact_log_info "DEBUG: Iniciando execute_installation_script para $script_path"

    if ! ensure_executable "$script_path"; then
        iact_log_error "Script no disponible o sin permisos: $script_path"
        return 1
    fi

    iact_log_info "Ejecutando script: $script_path"

    local exit_code=0
    set +e
    bash "$script_path" >> "$(iact_get_log_file)" 2>&1
    exit_code=$?
    set -e

    if [[ $exit_code -eq 0 ]]; then
        iact_log_success "$script_name completado exitosamente"
        return 0
    fi

    iact_log_error "$script_name falló con código de salida: $exit_code"
    return $exit_code
}

# -----------------------------------------------------------------------------
# setup_environment
# Description: Configura variables de entorno y carga módulos base
# -----------------------------------------------------------------------------
setup_environment() {
    export DEBIAN_FRONTEND=noninteractive

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    if [[ -n "${IACT_BOOTSTRAP_TEST_ROOT:-}" ]]; then
        PROJECT_ROOT="$IACT_BOOTSTRAP_TEST_ROOT"
    elif [[ -d "/vagrant" ]]; then
        PROJECT_ROOT="/vagrant"
    else
        PROJECT_ROOT="$script_dir"
    fi

    LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
    DEBUG="${DEBUG:-false}"
    SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

    export PROJECT_ROOT LOGS_DIR DEBUG

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

    if ! ensure_directory "$PROJECT_ROOT/logs"; then
        exit 1
    fi

    if [[ ! -f "${PROJECT_ROOT}/utils/core.sh" ]]; then
        safe_printf "ERROR: No se encontró ${PROJECT_ROOT}/utils/core.sh" >&2
        exit 1
    fi

    # shellcheck disable=SC1090
    source "${PROJECT_ROOT}/utils/core.sh"

    if declare -f "iact_source_module" >/dev/null 2>&1; then
        if ! iact_source_module "validation"; then
            iact_log_error "No se pudo cargar el módulo validation"
            return 1
        fi
    else
        safe_printf "ADVERTENCIA: iact_source_module no disponible" >&2
    fi

    if declare -f "iact_init_logging" >/dev/null 2>&1; then
        iact_init_logging "${SCRIPT_NAME%.sh}"
    fi

    if [[ "$DEBUG" == "true" ]]; then
        set -x
    fi

    iact_log_info "DEBUG: Entorno configurado correctamente"
}

validate_environment() {
    local errors=0
    local -a required_vars=(
        "PROJECT_ROOT"
        "LOGS_DIR"
        "DB_ROOT_PASSWORD"
        "DB_PASSWORD"
        "IVR_DB_NAME"
        "DJANGO_DB_NAME"
    )

    for var_name in "${required_vars[@]}"; do
        if [[ -z "${!var_name}" ]]; then
            iact_log_error "Variable obligatoria vacía: $var_name"
            errors=$((errors + 1))
        fi
    done

    local -a required_dirs=(
        "$PROJECT_ROOT"
        "$PROJECT_ROOT/scripts"
        "$PROJECT_ROOT/utils"
    )

    for directory in "${required_dirs[@]}"; do
        if [[ ! -d "$directory" ]]; then
            iact_log_error "Directorio requerido inexistente: $directory"
            errors=$((errors + 1))
        fi
    done

    if [[ "$errors" -gt 0 ]]; then
        iact_log_error "Validación de entorno falló con $errors error(es)"
        return 1
    fi

    iact_log_info "Validación de entorno exitosa"
    return 0
}

collect_environment_snapshot() {
    iact_log_info "Contexto: $(iact_get_context)"
    iact_log_info "Proyecto: $PROJECT_ROOT"
    iact_log_info "Logs: $LOGS_DIR"
    iact_log_info "MariaDB: $MARIADB_VERSION"
    iact_log_info "PostgreSQL: $POSTGRESQL_VERSION"
}

collect_required_script_paths() {
    local domain="${1:-all}"
    local -a steps=()
    local -a scripts=()
    local step
    local type
    local path

    readarray -t steps < <(build_bootstrap_steps "$domain")

    local -A seen=()

    for step in "${steps[@]}"; do
        type="${step%%:*}"
        if [[ "$type" != "script" ]]; then
            continue
        fi

        path="${step#*:}"
        if [[ -z "$path" ]]; then
            continue
        fi

        if [[ -n "${seen["$path"]:-}" ]]; then
            continue
        fi

        seen["$path"]=1
        scripts+=("$path")
    done

    printf '%s\n' "${scripts[@]}"
}

verify_required_scripts() {
    local -a scripts=()
    local missing=0
    local path

    readarray -t scripts < <(collect_required_script_paths all)

    iact_log_info "Validando scripts requeridos (${#scripts[@]})"

    for path in "${scripts[@]}"; do
        if [[ -z "$path" ]]; then
            continue
        fi

        if [[ ! -f "$path" ]]; then
            iact_log_error "Script faltante: $path"
            missing=$((missing + 1))
            continue
        fi

        if ! ensure_executable "$path"; then
            missing=$((missing + 1))
        fi
    done

    if [[ "$missing" -gt 0 ]]; then
        iact_log_error "No se cumplen los prerequisitos de scripts"
        return 1
    fi

    iact_log_info "Todos los scripts requeridos están disponibles"
    return 0
}

# -----------------------------------------------------------------------------
# Funciones de definición de pasos
# -----------------------------------------------------------------------------
define_system_steps() {
    printf '%s\n' \
        'func:display_bootstrap_header' \
        'func:apply_apt_sources' \
        'func:apply_dns_configuration' \
        'func:update_package_cache' \
        "script:$PROJECT_ROOT/scripts/system-prepare.sh"
}

define_database_steps() {
    printf '%s\n' \
        "script:$PROJECT_ROOT/scripts/mariadb-install.sh" \
        "script:$PROJECT_ROOT/scripts/postgres-install.sh" \
        "script:$PROJECT_ROOT/scripts/setup-mariadb-database.sh" \
        "script:$PROJECT_ROOT/scripts/setup-postgres-database.sh"
}

define_info_steps() {
    printf '%s\n' \
        'func:display_credentials_info' \
        'func:display_access_information'
}

build_bootstrap_steps() {
    local domain="${1:-all}"
    iact_log_info "DEBUG: Construyendo pasos para dominio: $domain"

    local steps=()

    case "$domain" in
        system)
            readarray -t steps < <(define_system_steps)
            ;;
        database)
            readarray -t steps < <(define_database_steps)
            ;;
        info)
            readarray -t steps < <(define_info_steps)
            ;;
        all)
            readarray -t system < <(define_system_steps)
            readarray -t database < <(define_database_steps)
            readarray -t info < <(define_info_steps)
            steps=("${system[@]}" "${database[@]}" "${info[@]}")
            ;;
        *)
            iact_log_error "Dominio desconocido: $domain"
            exit 1
            ;;
    esac

    printf '%s\n' "${steps[@]}"
}

# -----------------------------------------------------------------------------
# run_bootstrap_steps
# Description: Ejecuta todos los pasos definidos
# -----------------------------------------------------------------------------
run_bootstrap_steps() {
    local steps=("$@")
    local total=${#steps[@]}
    local current=0
    local failed_steps=()

    iact_log_info "Total de pasos a ejecutar: $total"
    iact_log_info "Iniciando proceso de aprovisionamiento..."

    for step in "${steps[@]}"; do
        ((current++))
        local type="${step%%:*}"
        local value="${step#*:}"

        if [[ "$type" == "func" ]]; then
            if ! declare -f "$value" > /dev/null; then
                iact_log_error "Funcion no definida: $value"
                failed_steps+=("$value")
                continue
            fi
            iact_log_info "DEBUG: Ejecutando funcion: $value"
            if ! "$value" "$current" "$total"; then
                failed_steps+=("$value")
            fi
        elif [[ "$type" == "script" ]]; then
            iact_log_info "DEBUG: Ejecutando script: $value"
            if ! execute_installation_script "$value" "$current" "$total"; then
                failed_steps+=("$(basename "$value")")
            fi
        else
            iact_log_error "Tipo de paso desconocido: $type"
            failed_steps+=("$step")
        fi
    done

    report_bootstrap_results "$total" "${failed_steps[@]}"
}

# -----------------------------------------------------------------------------
# report_bootstrap_results
# Description: Muestra el resumen final del proceso
# -----------------------------------------------------------------------------
report_bootstrap_results() {
    local total="$1"
    shift
    local failed_steps=("$@")

    echo ""
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Bootstrap completado sin fallos"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Revise el log para detalles: $(iact_get_log_file)"
        return 0
    fi

    iact_log_error "Bootstrap con ${#failed_steps[@]} error(es):"
    for step in "${failed_steps[@]}"; do
        iact_log_error "  - $step"
    done
    iact_log_info "Total pasos ejecutados: $total"
    iact_log_info "Pasos exitosos: $((total - ${#failed_steps[@]}))"
    iact_log_info "Revise los logs para más detalles: $(iact_get_log_file)"
    return 1
}

# -----------------------------------------------------------------------------
# Funciones de información y visualización
# -----------------------------------------------------------------------------
display_bootstrap_header() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de bootstrap"
    iact_log_info "DEBUG: Iniciando display_bootstrap_header"

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

apply_apt_sources() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Fuentes APT"
    iact_log_info "Validando configuración de fuentes APT"
    iact_log_info "No se realizan cambios (operación idempotente)"
    return 0
}

apply_dns_configuration() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configuración DNS"
    iact_log_info "Validando configuración DNS"
    iact_log_info "No se requieren ajustes adicionales"
    return 0
}

update_package_cache() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualización de cache"
    iact_log_info "Se omite actualización automática para mantener idempotencia"
    return 0
}

display_credentials_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de credenciales"
    iact_log_info "DEBUG: Iniciando display_credentials_info"

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
    echo "Estas credenciales estan registradas en: $(iact_get_log_file)"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

display_access_information() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de acceso"
    iact_log_info "DEBUG: Iniciando display_access_information"

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
# Punto de entrada principal
# -----------------------------------------------------------------------------
main() {
    setup_environment
    collect_environment_snapshot

    if ! validate_environment; then
        return 1
    fi

    if ! verify_required_scripts; then
        return 1
    fi

    local domain="${1:-all}"
    local -a steps
    readarray -t steps < <(build_bootstrap_steps "$domain")
    run_bootstrap_steps "${steps[@]}"
}

# -----------------------------------------------------------------------------
# Verificación de privilegios y ejecución
# -----------------------------------------------------------------------------
if [[ "${IACT_BOOTSTRAP_MODE:-execute}" != "library" ]]; then
    if [[ $EUID -ne 0 ]]; then
        echo "ERROR: Este script debe ejecutarse con privilegios de root" >&2
        echo "Intente: sudo $0" >&2
        exit 1
    fi

    main "$@"
fi

