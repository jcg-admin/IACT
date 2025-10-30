#!/bin/bash

# Detect Vagrant environment
if [[ -d "/vagrant" ]]; then
    PROJECT_ROOT="/vagrant"
else
    # Obtener directorio del script sin readonly
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Nombre del script sin readonly
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Imprimir información del sistema
echo "=== INFORMACIÓN DEL SISTEMA ==="
uname -a
pwd
whoami

# Verificar variables de entorno
echo "=== VARIABLES DE ENTORNO ==="
env | grep -E "PROJECT_ROOT|VAGRANT|HOME"

# Listar contenido de directorios críticos
echo "=== CONTENIDO DE DIRECTORIOS ==="
ls -la /vagrant
ls -la "$PROJECT_ROOT/scripts"

# Verificar permisos
echo "=== PERMISOS ==="
stat /vagrant
stat "$PROJECT_ROOT/scripts"

# Configuration
LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
DEBUG="${DEBUG:-false}"

# Database configuration with defaults
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

# Verificaciones adicionales de seguridad
echo "=== VERIFICACIONES ADICIONALES ==="

# Verificar existencia de scripts críticos
REQUIRED_SCRIPTS=(
    "system-prepare.sh"
    "mariadb-install.sh"
    "postgres-install.sh"
    "setup-mariadb-database.sh"
    "setup-postgres-database.sh"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [[ ! -f "$PROJECT_ROOT/scripts/$script" ]]; then
        echo "ERROR: Script crítico no encontrado: $script"
        exit 1
    else
        echo "Script encontrado: $script ✓"
        # Verificar permisos de ejecución
        if [[ ! -x "$PROJECT_ROOT/scripts/$script" ]]; then
            echo "Estableciendo permisos de ejecución para $script"
            chmod +x "$PROJECT_ROOT/scripts/$script"
        fi
    fi
done

# Verificar directorios esenciales
REQUIRED_DIRS=(
    "$PROJECT_ROOT/utils"
    "$PROJECT_ROOT/config"
    "$PROJECT_ROOT/logs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        echo "ERROR: Directorio requerido no encontrado: $dir"
        exit 1
    else
        echo "Directorio encontrado: $dir ✓"
    fi
done

# Verificar archivo de utilidades core
if [[ ! -f "$PROJECT_ROOT/utils/core.sh" ]]; then
    echo "ERROR: Archivo core.sh no encontrado"
    exit 1
fi

# Debugging adicional
echo "=== DEBUGGING ADICIONAL ==="
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "SCRIPT_NAME: $SCRIPT_NAME"
echo "LOGS_DIR: $LOGS_DIR"

# Intentar cargar módulos con manejo de errores
set -e

# Cargar core con verificación
if [[ -f "${PROJECT_ROOT}/utils/core.sh" ]]; then
    echo "Cargando módulo core.sh"
    source "${PROJECT_ROOT}/utils/core.sh"
else
    echo "ERROR: No se encontró core.sh"
    exit 1
fi

# Intentar cargar módulos adicionales
try_load_module() {
    local module_name="$1"
    if declare -f "iact_source_module" > /dev/null; then
        echo "Cargando módulo: $module_name"
        if ! iact_source_module "$module_name"; then
            echo "ADVERTENCIA: No se pudo cargar el módulo $module_name"
        fi
    else
        echo "ADVERTENCIA: Función iact_source_module no definida"
    fi
}

# Cargar módulos críticos
try_load_module "validation"

# Configurar logging
if declare -f "iact_init_logging" > /dev/null; then
    iact_init_logging "${SCRIPT_NAME%.sh}"
else
    echo "ADVERTENCIA: Función iact_init_logging no definida"
fi

# Función de validación de configuración
validate_environment() {
    local errors=0

    # Validar variables críticas
    local critical_vars=(
        "PROJECT_ROOT"
        "DB_ROOT_PASSWORD"
        "DB_PASSWORD"
        "IVR_DB_NAME"
        "DJANGO_DB_NAME"
    )

    for var in "${critical_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo "ERROR: Variable crítica $var no está definida"
            ((errors++))
        fi
    done

    # Validar versiones de software
    if [[ -z "$MARIADB_VERSION" ]] || [[ -z "$POSTGRESQL_VERSION" ]]; then
        echo "ERROR: Versiones de MariaDB o PostgreSQL no definidas"
        ((errors++))
    fi

    # Validar directorios
    local required_dirs=(
        "$PROJECT_ROOT"
        "$PROJECT_ROOT/scripts"
        "$PROJECT_ROOT/utils"
        "$PROJECT_ROOT/config"
        "$LOGS_DIR"
    )

    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            echo "ERROR: Directorio requerido no existe: $dir"
            ((errors++))
        fi
    done

    # Resumen de validación
    if [[ $errors -gt 0 ]]; then
        echo "VALIDACIÓN FALLIDA: $errors errores encontrados"
        return 1
    else
        echo "VALIDACIÓN EXITOSA: Todos los requisitos cumplidos"
        return 0
    fi
}

# Ejecutar validación
if ! validate_environment; then
    echo "ERROR CRÍTICO: Configuración del entorno inválida"
    exit 1
fi

# Información final de diagnóstico
echo "=== RESUMEN FINAL ==="
echo "Entorno de proyecto configurado correctamente"
echo "Directorio raíz: $PROJECT_ROOT"
echo "Versiones configuradas:"
echo "  - MariaDB: $MARIADB_VERSION"
echo "  - PostgreSQL: $POSTGRESQL_VERSION"

# Preparar para siguiente etapa
export PROJECT_ROOT
export LOGS_DIR
export DEBUG

# Fin del script de diagnóstico
exit 0


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

    if [[ ! -f "$script_path" ]]; then
        iact_log_error "Script no encontrado: $script_path"
        iact_log_info "DEBUG: Script inexistente, abortando paso"
        return 1
    fi

    if ! chmod +x "$script_path"; then
        iact_log_error "No se pueden establecer permisos de ejecucion: $script_path"
        iact_log_info "DEBUG: chmod falló para $script_path"
        return 1
    fi

    iact_log_info "Ejecutando script: $script_path"
    if bash "$script_path" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "$script_name completado exitosamente"
        return 0
    else
        local exit_code=$?
        iact_log_error "$script_name fallo con codigo de salida: $exit_code"
        iact_log_info "DEBUG: Script $script_name terminó con error"
        return $exit_code
    fi
}

# -----------------------------------------------------------------------------
# setup_environment
# Description: Configura variables de entorno y carga módulos base
# -----------------------------------------------------------------------------
setup_environment() {
    set -euo pipefail
    export DEBIAN_FRONTEND=noninteractive

    readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

    if [[ -d "/vagrant" ]]; then
        readonly PROJECT_ROOT="/vagrant"
    else
        readonly PROJECT_ROOT="$SCRIPT_DIR"
    fi

    readonly LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
    readonly DEBUG="${DEBUG:-false}"

    # Configuración de credenciales con valores por defecto
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

    export LOGS_DIR DEBUG PROJECT_ROOT

    # Cargar módulos y utilidades
    source "${PROJECT_ROOT}/utils/core.sh"
    iact_source_module "validation"
    iact_init_logging "${SCRIPT_NAME%.sh}"

    [[ "$DEBUG" == "true" ]] && set -x
    iact_log_info "DEBUG: Entorno configurado correctamente"
}

# -----------------------------------------------------------------------------
# Funciones de definición de pasos
# -----------------------------------------------------------------------------
define_system_steps() {
    echo "
        func:display_bootstrap_header
        func:apply_apt_sources
        func:apply_dns_configuration
        func:update_package_cache
        script:$PROJECT_ROOT/scripts/system-prepare.sh
    "
}

define_database_steps() {
    echo "
        script:$PROJECT_ROOT/scripts/mariadb-install.sh
        script:$PROJECT_ROOT/scripts/postgres-install.sh
        script:$PROJECT_ROOT/scripts/setup-mariadb-database.sh
        script:$PROJECT_ROOT/scripts/setup-postgres-database.sh
    "
}

define_info_steps() {
    echo "
        func:display_credentials_info
        func:display_access_information
    "
}

build_bootstrap_steps() {
    local domain="${1:-all}"
    iact_log_info "DEBUG: Construyendo pasos para dominio: $domain"

    local steps=()

    case "$domain" in
        system)
            mapfile -t steps < <(define_system_steps)
            ;;
        database)
            mapfile -t steps < <(define_database_steps)
            ;;
        info)
            mapfile -t steps < <(define_info_steps)
            ;;
        all)
            mapfile -t system < <(define_system_steps)
            mapfile -t database < <(define_database_steps)
            mapfile -t info < <(define_info_steps)
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
        iact_log_success "Bootstrap completado exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "MariaDB y PostgreSQL instalados y configurados"
        iact_log_info "Todos los servicios     están en ejecución"
        return 0
    else
        iact_log_error "Bootstrap completado con ${#failed_steps[@]} error(es):"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Pasos exitosos: $((total - ${#failed_steps[@]}))"
        iact_log_info "Revise los logs para más detalles: $(iact_get_log_file)"
        return 1
    fi
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
    local domain="${1:-all}"
    local steps=($(build_bootstrap_steps "$domain"))
    run_bootstrap_steps "${steps[@]}"
}

# -----------------------------------------------------------------------------
# Verificación de privilegios y ejecución
# -----------------------------------------------------------------------------
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: Este script debe ejecutarse con privilegios de root"
    echo "Intente: sudo $0"
    exit 1
fi

# Ejecutar flujo principal
main "$@"

