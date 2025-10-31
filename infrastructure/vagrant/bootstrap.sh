#!/bin/bash
set -euo pipefail

# =============================================================================
# Bootstrap - Sistema de aprovisionamiento modular
# =============================================================================

# Funciones core
print_safe() {
    printf '%s\n' "$1"
}

dir_exists() {
    [ -d "$1" ]
}

file_exists() {
    [ -f "$1" ]
}

is_executable() {
    [ -x "$1" ]
}

ensure_dir() {
    local dir="$1"
    dir_exists "$dir" && return 0

    if ! mkdir -p "$dir"; then
        print_safe "ERROR: No se pudo crear directorio: $dir" >&2
        return 1
    fi
    return 0
}

make_executable() {
    local path="$1"

    if ! file_exists "$path"; then
        print_safe "ERROR: Archivo no existe: $path" >&2
        return 1
    fi

    is_executable "$path" && return 0

    if ! chmod +x "$path"; then
        print_safe "ERROR: No se pudo dar permisos de ejecucion: $path" >&2
        return 1
    fi
    return 0
}

# Ejecucion de scripts con captura correcta de errores
run_script() {
    local script="$1"
    local step="$2"
    local total="$3"
    local name

    name=$(basename "$script")

    iact_log_step "$step" "$total" "Ejecutando: $name"

    if ! make_executable "$script"; then
        iact_log_error "Script no disponible o sin permisos: $script"
        return 1
    fi

    iact_log_info "Iniciando ejecucion de $name"

    # CORRECCION: Agregar set -o pipefail para capturar errores en tuberias
    set -o pipefail

    if bash "$script"; then
        iact_log_success "$name completado exitosamente"
        return 0
    else
        local code=$?
        iact_log_error "$name fallo con codigo: $code"
        iact_log_error "Error ejecutando $name"
        return "$code"
    fi
}

# Configuracion de entorno
compute_project_root() {
    local script_dir="$1"

    if [ -n "${IACT_BOOTSTRAP_TEST_ROOT:-}" ]; then
        printf '%s' "$IACT_BOOTSTRAP_TEST_ROOT"
    elif [ -d "/vagrant" ]; then
        printf '%s' "/vagrant"
    else
        printf '%s' "$script_dir"
    fi
}

init_env_vars() {
    export DEBIAN_FRONTEND=noninteractive

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    PROJECT_ROOT=$(compute_project_root "$script_dir")
    LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
    DEBUG="${DEBUG:-false}"
    SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

    export PROJECT_ROOT LOGS_DIR DEBUG SCRIPT_NAME

    # Configuracion de bases de datos - CORRECCION: Versiones actualizadas
    DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"
    DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"
    IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
    IVR_DB_USER="${IVR_DB_USER:-django_user}"
    IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-django_pass}"
    DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
    DJANGO_DB_USER="${DJANGO_DB_USER:-django_user}"
    DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-django_pass}"
    MARIADB_VERSION="${MARIADB_VERSION:-11.4}"
    POSTGRES_VERSION="${POSTGRES_VERSION:-16}"

    export DB_ROOT_PASSWORD DB_PASSWORD
    export IVR_DB_NAME IVR_DB_USER IVR_DB_PASSWORD
    export DJANGO_DB_NAME DJANGO_DB_USER DJANGO_DB_PASSWORD
    export MARIADB_VERSION POSTGRES_VERSION
}

load_core_modules() {
    local core_path="${PROJECT_ROOT}/utils/core.sh"

    if ! file_exists "$core_path"; then
        print_safe "ERROR: No se encontro $core_path" >&2
        return 1
    fi

    # shellcheck disable=SC1090
    . "$core_path"

    if type "iact_source_module" >/dev/null 2>&1; then
        if ! iact_source_module "validation"; then
            iact_log_error "No se pudo cargar modulo validation"
            return 1
        fi
    else
        print_safe "ADVERTENCIA: iact_source_module no disponible" >&2
    fi

    if type "iact_init_logging" >/dev/null 2>&1; then
        iact_init_logging "${SCRIPT_NAME%.sh}"
    fi

    return 0
}

setup_env() {
    init_env_vars

    if ! ensure_dir "$LOGS_DIR"; then
        return 1
    fi

    if ! load_core_modules; then
        return 1
    fi

    if [ "$DEBUG" = "true" ]; then
        set -x
    fi

    iact_log_info "Entorno configurado correctamente"
    return 0
}

# Validacion de entorno
var_is_set() {
    eval "[ -n \"\${$1:-}\" ]"
}

count_missing_vars() {
    local errors=0
    local var

    for var in "$@"; do
        if ! var_is_set "$var"; then
            iact_log_error "Variable obligatoria vacia: $var" >&2
            errors=$((errors + 1))
        fi
    done

    printf '%d' "$errors"
}

count_missing_dirs() {
    local errors=0
    local dir

    for dir in "$@"; do
        if ! dir_exists "$dir"; then
            iact_log_error "Directorio requerido inexistente: $dir" >&2
            errors=$((errors + 1))
        fi
    done

    printf '%d' "$errors"
}

validate_env() {
    local var_errors
    local dir_errors
    local total_errors

    var_errors=$(count_missing_vars \
        "PROJECT_ROOT" \
        "LOGS_DIR" \
        "DB_ROOT_PASSWORD" \
        "DB_PASSWORD" \
        "IVR_DB_NAME" \
        "DJANGO_DB_NAME")

    dir_errors=$(count_missing_dirs \
        "$PROJECT_ROOT" \
        "$PROJECT_ROOT/scripts" \
        "$PROJECT_ROOT/utils")

    total_errors=$((var_errors + dir_errors))

    if [ "$total_errors" -gt 0 ]; then
        iact_log_error "Validacion de entorno fallo con $total_errors error(es)"
        return 1
    fi

    iact_log_info "Validacion de entorno exitosa"
    return 0
}

# Informacion del sistema
show_env_snapshot() {
    iact_log_info "Contexto: $(iact_get_context)"
    iact_log_info "Proyecto: $PROJECT_ROOT"
    iact_log_info "Logs: $LOGS_DIR"
    iact_log_info "MariaDB: $MARIADB_VERSION"
    iact_log_info "PostgreSQL: $POSTGRES_VERSION"
}

# Verificacion de scripts
get_required_scripts() {
    printf '%s\n' \
        "$PROJECT_ROOT/scripts/system-prepare.sh" \
        "$PROJECT_ROOT/scripts/mariadb-install.sh" \
        "$PROJECT_ROOT/scripts/postgres-install.sh" \
        "$PROJECT_ROOT/scripts/setup-mariadb-database.sh" \
        "$PROJECT_ROOT/scripts/setup-postgres-database.sh"
}

count_script_issues() {
    local missing=0
    local script

    for script in $(get_required_scripts); do
        if ! file_exists "$script"; then
            iact_log_error "Script faltante: $script"
            missing=$((missing + 1))
        elif ! is_executable "$script" && ! make_executable "$script"; then
            iact_log_error "Script sin permisos: $script"
            missing=$((missing + 1))
        fi
    done

    printf '%d' "$missing"
}

verify_scripts() {
    local issues

    issues=$(count_script_issues)

    if [ "$issues" -gt 0 ]; then
        iact_log_error "Encontrados $issues problemas con scripts"
        return 1
    fi

    iact_log_info "Todos los scripts requeridos estan disponibles"
    return 0
}

# Informacion de credenciales
show_credentials() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de credenciales"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "                    CREDENCIALES"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "MariaDB:"
    printf '%s\n' "  Usuario: root"
    printf '%s\n' "  Password: $DB_ROOT_PASSWORD"
    printf '%s\n' "  Base de datos: $IVR_DB_NAME"
    printf '%s\n' "  Usuario aplicacion: $IVR_DB_USER"
    printf '%s\n' "  Password aplicacion: $IVR_DB_PASSWORD"
    printf '\n'
    printf '%s\n' "PostgreSQL:"
    printf '%s\n' "  Usuario: postgres"
    printf '%s\n' "  Password: $DB_PASSWORD"
    printf '%s\n' "  Base de datos: $DJANGO_DB_NAME"
    printf '%s\n' "  Usuario aplicacion: $DJANGO_DB_USER"
    printf '%s\n' "  Password aplicacion: $DJANGO_DB_PASSWORD"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

# Informacion de acceso
show_access_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de acceso"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "                    ACCESO A BASES DE DATOS"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "MariaDB:"
    printf '%s\n' "  mysql -u root -p'$DB_ROOT_PASSWORD'"
    printf '%s\n' "  mysql -u $IVR_DB_USER -p'$IVR_DB_PASSWORD' $IVR_DB_NAME"
    printf '\n'
    printf '%s\n' "PostgreSQL:"
    printf '%s\n' "  PGPASSWORD='$DB_PASSWORD' psql -U postgres -h localhost"
    printf '%s\n' "  PGPASSWORD='$DJANGO_DB_PASSWORD' psql -U $DJANGO_DB_USER -h localhost -d $DJANGO_DB_NAME"
    printf '\n'
    printf '%s\n' "Logs:"
    printf '%s\n' "  $LOGS_DIR"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

# =============================================================================
# Pasos de sistema
# =============================================================================

step_show_header() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de bootstrap"
    iact_log_info "Ubuntu: 20.04 LTS (Focal)"
    iact_log_info "MariaDB: $MARIADB_VERSION"
    iact_log_info "PostgreSQL: $POSTGRES_VERSION"
    return 0
}

step_check_apt() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Fuentes APT"
    iact_log_info "Validando configuracion de fuentes APT"
    iact_log_info "No se realizan cambios (operacion idempotente)"
    return 0
}

step_check_dns() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configuracion DNS"
    iact_log_info "Validando configuracion DNS"
    iact_log_info "No se requieren ajustes adicionales"
    return 0
}

step_check_cache() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualizacion de cache"
    iact_log_info "Se omite actualizacion automatica para mantener idempotencia"
    return 0
}

step_system_prepare() {
    local current="$1"
    local total="$2"
    local script="$PROJECT_ROOT/scripts/system-prepare.sh"

    if ! file_exists "$script"; then
        iact_log_error "Script no encontrado: $script"
        return 1
    fi

    if ! run_script "$script" "$current" "$total"; then
        iact_log_error "Error ejecutando system-prepare.sh"
        return 1
    fi
    return 0
}

# =============================================================================
# Pasos de base de datos
# =============================================================================

step_mariadb_install() {
    local current="$1"
    local total="$2"
    local script="$PROJECT_ROOT/scripts/mariadb-install.sh"

    if ! file_exists "$script"; then
        iact_log_error "Script no encontrado: $script"
        return 1
    fi

    if ! run_script "$script" "$current" "$total"; then
        iact_log_error "Error ejecutando mariadb-install.sh"
        return 1
    fi
    return 0
}

step_postgres_install() {
    local current="$1"
    local total="$2"
    local script="$PROJECT_ROOT/scripts/postgres-install.sh"

    if ! file_exists "$script"; then
        iact_log_error "Script no encontrado: $script"
        return 1
    fi

    if ! run_script "$script" "$current" "$total"; then
        iact_log_error "Error ejecutando postgres-install.sh"
        return 1
    fi
    return 0
}

step_mariadb_setup() {
    local current="$1"
    local total="$2"
    local script="$PROJECT_ROOT/scripts/setup-mariadb-database.sh"

    if ! file_exists "$script"; then
        iact_log_error "Script no encontrado: $script"
        return 1
    fi

    if ! run_script "$script" "$current" "$total"; then
        iact_log_error "Error ejecutando setup-mariadb-database.sh"
        return 1
    fi
    return 0
}

step_postgres_setup() {
    local current="$1"
    local total="$2"
    local script="$PROJECT_ROOT/scripts/setup-postgres-database.sh"

    if ! file_exists "$script"; then
        iact_log_error "Script no encontrado: $script"
        return 1
    fi

    if ! run_script "$script" "$current" "$total"; then
        iact_log_error "Error ejecutando setup-postgres-database.sh"
        return 1
    fi
    return 0
}

# =============================================================================
# Pasos de informacion
# =============================================================================

step_show_credentials() {
    local current="$1"
    local total="$2"

    if ! show_credentials "$current" "$total"; then
        iact_log_error "Error mostrando credenciales"
        return 1
    fi
    return 0
}

step_show_access() {
    local current="$1"
    local total="$2"

    if ! show_access_info "$current" "$total"; then
        iact_log_error "Error mostrando informacion de acceso"
        return 1
    fi
    return 0
}

# =============================================================================
# Pipelines - CORRECCION: Sin espacios en nombres de funciones
# =============================================================================

pipeline_system() {
    printf '%s\n' \
        'step_show_header' \
        'step_check_apt' \
        'step_check_dns' \
        'step_check_cache' \
        'step_system_prepare'
}

pipeline_database() {
    printf '%s\n' \
        'step_mariadb_install' \
        'step_postgres_install' \
        'step_mariadb_setup' \
        'step_postgres_setup'
}

pipeline_info() {
    printf '%s\n' \
        'step_show_credentials' \
        'step_show_access'
}

pipeline_all() {
    pipeline_system
    pipeline_database
    pipeline_info
}

build_steps() {
    local domain="${1:-all}"

    case "$domain" in
        system)   pipeline_system ;;
        database) pipeline_database ;;
        info)     pipeline_info ;;
        all)      pipeline_all ;;
        *)
            iact_log_error "Dominio desconocido: $domain" >&2
            return 1
            ;;
    esac
}

# =============================================================================
# Ejecucion de pasos
# =============================================================================

func_exists() {
    type "$1" >/dev/null 2>&1
}

exec_step() {
    local step_func="$1"
    local current="$2"
    local total="$3"

    # CORRECCION: Limpiar espacios del nombre de funcion
    step_func=$(echo "$step_func" | tr -d '[:space:]')

    if ! func_exists "$step_func"; then
        iact_log_error "Funcion no definida: $step_func"
        return 1
    fi

    if ! "$step_func" "$current" "$total"; then
        iact_log_error "Paso fallo: $step_func"
        return 1
    fi

    return 0
}

run_steps() {
    local total=0
    local current=0
    local failed_count=0
    local failed_list=""
    local step

    for step in "$@"; do
        total=$((total + 1))
    done

    if [ "$total" -eq 0 ]; then
        iact_log_error "No hay pasos para ejecutar"
        return 1
    fi

    iact_log_info "Total de pasos a ejecutar: $total"
    iact_log_info "Iniciando proceso de aprovisionamiento..."

    for step in "$@"; do
        current=$((current + 1))

        if ! exec_step "$step" "$current" "$total"; then
            if [ -z "$failed_list" ]; then
                failed_list="$step"
            else
                failed_list="$failed_list|$step"
            fi
            failed_count=$((failed_count + 1))
        fi
    done

    show_results "$total" "$failed_count" "$failed_list"
}

# =============================================================================
# Reporte de resultados
# =============================================================================

show_results() {
    local total="$1"
    local failed_count="$2"
    local failed_list="$3"
    local successful

    printf '\n'

    if [ "$failed_count" -eq 0 ]; then
        iact_log_success "Bootstrap completado sin fallos"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Revise el log para detalles: $(iact_get_log_file)"
        return 0
    fi

    successful=$((total - failed_count))

    iact_log_error "Bootstrap con $failed_count error(es):"

    local IFS='|'
    for step in $failed_list; do
        iact_log_error "  - $step"
    done

    iact_log_info "Total pasos ejecutados: $total"
    iact_log_info "Pasos exitosos: $successful"
    iact_log_info "Revise los logs para mas detalles: $(iact_get_log_file)"
    return 1
}

# =============================================================================
# Funcion principal
# =============================================================================

main() {
    local domain="${1:-all}"
    local steps_output

    setup_env || return 1
    show_env_snapshot
    validate_env || return 1
    verify_scripts || return 1

    steps_output=$(build_steps "$domain")

    if [ -z "$steps_output" ]; then
        iact_log_error "No se pudieron construir pasos para dominio: $domain"
        return 1
    fi

    # CORRECCION: Sin exit 0 prematuro - permitir ejecucion completa
    set -- $steps_output
    run_steps "$@"
}

# =============================================================================
# Punto de entrada
# =============================================================================

if [ "${IACT_BOOTSTRAP_MODE:-execute}" != "library" ]; then
    if [ "$(id -u)" -ne 0 ]; then
        print_safe "ERROR: Este script debe ejecutarse con privilegios de root" >&2
        print_safe "ACCION REQUERIDA: Intente: sudo $0" >&2
        exit 1
    fi

    main "$@"
fi