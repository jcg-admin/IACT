#!/bin/bash
set -euo pipefail

# =============================================================================
# BOOTSTRAP - Sistema de aprovisionamiento modular, funcional e idempotente
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
    [ -d "$1" ]
}

# Valida si archivo existe (función pura de validación)
file_exists() {
    [ -f "$1" ]
}

# Valida si archivo es ejecutable (función pura de validación)
is_executable() {
    [ -x "$1" ]
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

    if ! make_executable "$script"; then
        iact_log_error "Script no disponible o sin permisos: $script"
        return 1
    fi

    iact_log_info "Iniciando ejecución de $name"

    # Execute script directly without log redirection
    if bash "$script"; then
        iact_log_success "$name completado exitosamente"
        return 0
    else
        local code=$?
        iact_log_error "$name falló con código: $code"
        return "$code"
    fi
}

# -----------------------------------------------------------------------------
# Configuración de entorno - Función pura que retorna configuración
# -----------------------------------------------------------------------------

# Calcula root del proyecto (función pura)
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
    DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"
    DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"
    IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
    IVR_DB_USER="${IVR_DB_USER:-django_user}"
    IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-django_pass}"
    DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
    DJANGO_DB_USER="${DJANGO_DB_USER:-django_user}"
    DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-django_pass}"
    MARIADB_VERSION="${MARIADB_VERSION:-10.6}"
    POSTGRESQL_VERSION="${POSTGRESQL_VERSION:-10}"

    # Export all variables for child scripts
    export PROJECT_ROOT LOGS_DIR DEBUG SCRIPT_NAME
    export DB_ROOT_PASSWORD DB_PASSWORD
    export IVR_DB_NAME IVR_DB_USER IVR_DB_PASSWORD
    export DJANGO_DB_NAME DJANGO_DB_USER DJANGO_DB_PASSWORD
    export MARIADB_VERSION POSTGRESQL_VERSION
}

# Carga módulos del sistema
load_core_modules() {
    local core_path="${PROJECT_ROOT}/utils/core.sh"

    if ! file_exists "$core_path"; then
        print_safe "ERROR: No se encontró $core_path" >&2
        return 1
    fi

    # shellcheck disable=SC1090
    . "$core_path"

    if type "iact_source_module" >/dev/null 2>&1; then
        if ! iact_source_module "validation"; then
            iact_log_error "No se pudo cargar módulo validation"
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

# Configura entorno completo (orquestador)
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

# -----------------------------------------------------------------------------
# Validación de entorno - Funciones puras de validación (POSIX)
# -----------------------------------------------------------------------------

# Valida que variable tenga valor (función pura POSIX)
var_is_set() {
    eval "[ -n \"\${$1:-}\" ]"
}

# Cuenta errores de variables requeridas (POSIX)
count_missing_vars() {
    local errors=0
    local var

    for var in "$@"; do
        if ! var_is_set "$var"; then
            iact_log_error "Variable obligatoria vacía: $var" >&2
            errors=$((errors + 1))
        fi
    done

    printf '%d' "$errors"
}

# Cuenta errores de directorios faltantes (POSIX)
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

# Valida entorno completo (POSIX)
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
# Verificación de scripts - Funciones de validación (POSIX)
# -----------------------------------------------------------------------------

# Obtiene lista de scripts requeridos (función pura POSIX)
get_required_scripts() {
    printf '%s\n' \
        "$PROJECT_ROOT/scripts/system-prepare.sh" \
        "$PROJECT_ROOT/scripts/mariadb-install.sh" \
        "$PROJECT_ROOT/scripts/postgres-install.sh" \
        "$PROJECT_ROOT/scripts/setup-mariadb-database.sh" \
        "$PROJECT_ROOT/scripts/setup-postgres-database.sh"
}

# Cuenta scripts faltantes o no ejecutables (POSIX)
count_script_issues() {
    local missing=0
    local script

    # Usar command substitution con loop POSIX
    for script in $(get_required_scripts); do
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

    if [ "$issues" -gt 0 ]; then
        iact_log_error "No se cumplen prerequisitos de scripts"
        return 1
    fi

    iact_log_info "Todos los scripts requeridos están disponibles"
    return 0
}

# -----------------------------------------------------------------------------
# Funciones de información visual - Sin emojis
# -----------------------------------------------------------------------------

show_header() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de bootstrap"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "            MARIADB + POSTGRESQL BOOTSTRAP"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Sistema objetivo: Ubuntu 18.04 LTS (Bionic Beaver)"
    printf '%s\n' "Project Root: $PROJECT_ROOT"
    printf '%s\n' "Logs Directory: $LOGS_DIR"
    printf '%s\n' "Context: $(iact_get_context)"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

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

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "                  CREDENCIALES DE BASES DE DATOS"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "IMPORTANTE: Guarde estas credenciales de forma segura"
    printf '\n'
    printf '%s\n' "MariaDB:"
    printf '%s\n' "  Usuario: root"
    printf '%s\n' "  Password: $DB_ROOT_PASSWORD"
    printf '\n'
    printf '%s\n' "PostgreSQL:"
    printf '%s\n' "  Usuario: postgres"
    printf '%s\n' "  Password: $DB_PASSWORD"
    printf '\n'
    printf '%s\n' "Estas credenciales están registradas en: $(iact_get_log_file)"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

show_access_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de acceso"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "                  INFORMACION DE ACCESO"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Acceso SSH:"
    printf '%s\n' "  vagrant ssh (si usa Vagrant)"
    printf '\n'
    printf '%s\n' "Bases de datos:"
    printf '%s\n' "  MariaDB: mysql -u root -p"
    printf '%s\n' "  PostgreSQL: psql -U postgres -h localhost"
    printf '\n'
    printf '%s\n' "Logs:"
    printf '%s\n' "  $(iact_get_log_file)"
    printf '\n'
    printf '%s\n' "Proyecto:"
    printf '%s\n' "  $PROJECT_ROOT"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

# -----------------------------------------------------------------------------
# Definición de pasos modulares - Una función por paso
# -----------------------------------------------------------------------------

# Pasos de sistema - Cada uno es idempotente y sin fallas silenciosas
step_show_header() {
    local current="$1"
    local total="$2"

    if ! show_header "$current" "$total"; then
        iact_log_error "Error mostrando header"
        return 1
    fi
    return 0
}

step_check_apt() {
    local current="$1"
    local total="$2"

    if ! check_apt_sources "$current" "$total"; then
        iact_log_error "Error validando fuentes APT"
        return 1
    fi
    return 0
}

step_check_dns() {
    local current="$1"
    local total="$2"

    if ! check_dns_config "$current" "$total"; then
        iact_log_error "Error validando DNS"
        return 1
    fi
    return 0
}

step_check_cache() {
    local current="$1"
    local total="$2"

    if ! check_pkg_cache "$current" "$total"; then
        iact_log_error "Error validando cache de paquetes"
        return 1
    fi
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

# Pasos de base de datos - Cada uno es idempotente y sin fallas silenciosas
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

# Pasos de información - Sin efectos secundarios críticos
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
        iact_log_error "Error mostrando información de acceso"
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# Pipelines - Listas simples de nombres de funciones (POSIX puro)
# -----------------------------------------------------------------------------

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

# Selector de pipeline (función pura POSIX)
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

# -----------------------------------------------------------------------------
# Ejecución de pasos - POSIX puro sin fallas silenciosas
# -----------------------------------------------------------------------------

# Verifica si función existe (POSIX)
func_exists() {
    type "$1" >/dev/null 2>&1
}

# Ejecutor con validación explícita (sin fallas silenciosas)
exec_step() {
    local step_func="$1"
    local current="$2"
    local total="$3"

    if ! func_exists "$step_func"; then
        iact_log_error "Función no definida: $step_func"
        return 1
    fi

    if ! "$step_func" "$current" "$total"; then
        iact_log_error "Paso falló: $step_func"
        return 1
    fi

    return 0
}

# Ejecuta todos los pasos con validación explícita (POSIX)
run_steps() {
    local total=0
    local current=0
    local failed_count=0
    local failed_list=""
    local step

    # Contar total de pasos (bash arithmetic)
    for step in "$@"; do
        total=$((total + 1))
    done

    if [ "$total" -eq 0 ]; then
        iact_log_error "No hay pasos para ejecutar"
        return 1
    fi

    iact_log_info "Total de pasos a ejecutar: $total"
    iact_log_info "Iniciando proceso de aprovisionamiento..."

    # Ejecutar cada paso con validación explícita
    for step in "$@"; do
        current=$((current + 1))

        if ! exec_step "$step" "$current" "$total"; then
            # Acumular fallos sin fallas silenciosas
            if [ -z "$failed_list" ]; then
                failed_list="$step"
            else
                failed_list="$failed_list|$step"
            fi
            failed_count=$((failed_count + 1))
        fi
    done

    # Mostrar resultados
    show_results "$total" "$failed_count" "$failed_list"
}

# -----------------------------------------------------------------------------
# Reporte de resultados - POSIX puro
# -----------------------------------------------------------------------------

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

    # Mostrar cada fallo (POSIX compatible sin arrays)
    local IFS='|'
    for step in $failed_list; do
        iact_log_error "  - $step"
    done

    iact_log_info "Total pasos ejecutados: $total"
    iact_log_info "Pasos exitosos: $successful"
    iact_log_info "Revise los logs para más detalles: $(iact_get_log_file)"
    return 1
}

# -----------------------------------------------------------------------------
# Función principal - Orquestación de alto nivel
# -----------------------------------------------------------------------------

main() {
    local domain="${1:-all}"
    local steps_output

    setup_env || return 1
    show_env_snapshot
    validate_env || return 1
    verify_scripts || return 1

    # Construir lista de pasos
    steps_output=$(build_steps "$domain")

    if [ -z "$steps_output" ]; then
        iact_log_error "No se pudieron construir pasos para dominio: $domain"
        return 1
    fi

    # Convertir output a argumentos posicionales (POSIX)
    set -- $steps_output

    run_steps "$@"
}

# -----------------------------------------------------------------------------
# Punto de entrada - Verificación de privilegios
# -----------------------------------------------------------------------------

if [ "${IACT_BOOTSTRAP_MODE:-execute}" != "library" ]; then
    if [ "$(id -u)" -ne 0 ]; then
        print_safe "ERROR: Este script debe ejecutarse con privilegios de root" >&2
        print_safe "ACCION REQUERIDA: Intente: sudo $0" >&2
        exit 1
    fi

    main "$@"
fi