#!/bin/bash
set -euo pipefail

# System Preparation - Ubuntu 20.04

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Detectar PROJECT_ROOT
if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
else
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

# Cargar modulos
if [ ! -f "${PROJECT_ROOT}/utils/core.sh" ]; then
    printf 'ERROR: No se encontro %s/utils/core.sh\n' "$PROJECT_ROOT" >&2
    exit 1
fi

source "${PROJECT_ROOT}/utils/core.sh"

if type "iact_source_module" >/dev/null 2>&1; then
    iact_source_module "validation" || true
fi

if type "iact_init_logging" >/dev/null 2>&1; then
    iact_init_logging "${SCRIPT_NAME%.sh}"
fi


# Funciones de validacion

# Verifica version de Ubuntu
check_ubuntu_version() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando version de Ubuntu"

    if [ ! -f /etc/os-release ]; then
        iact_log_error "Archivo /etc/os-release no encontrado"
        return 1
    fi

    source /etc/os-release

    if [ "$ID" != "ubuntu" ]; then
        iact_log_error "Sistema operativo debe ser Ubuntu, detectado: $ID"
        return 1
    fi

    if [ "$VERSION_ID" != "20.04" ]; then
        iact_log_error "Version de Ubuntu debe ser 20.04, detectado: $VERSION_ID"
        return 1
    fi

    iact_log_success "Ubuntu 20.04 LTS detectado correctamente"
    return 0
}

# Verifica espacio en disco
check_disk_space() {
    local current="$1"
    local total="$2"
    local required_gb=10

    iact_log_step "$current" "$total" "Verificando espacio en disco"

    local available_kb
    available_kb=$(df / | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))

    if [ "$available_gb" -lt "$required_gb" ]; then
        iact_log_error "Espacio insuficiente: ${available_gb}GB disponibles, ${required_gb}GB requeridos"
        return 1
    fi

    iact_log_success "Espacio disponible: ${available_gb}GB"
    return 0
}

# Verifica conectividad a Internet
check_internet() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando conectividad"

    local hosts=("8.8.8.8" "1.1.1.1")

    for host in "${hosts[@]}"; do
        if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
            iact_log_success "Conectividad verificada"
            return 0
        fi
    done

    iact_log_error "Sin conectividad a Internet"
    return 1
}

# Actualiza cache de APT con auto-recuperacion
update_apt_cache() {
    local current="$1"
    local total="$2"
    local max_attempts=3
    local attempt=1

    iact_log_step "$current" "$total" "Actualizando cache de paquetes"

    export DEBIAN_FRONTEND=noninteractive

    while [ $attempt -le $max_attempts ]; do
        iact_log_info "Intento $attempt de $max_attempts..."

        if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_success "Cache actualizado correctamente"
            return 0
        fi

        iact_log_warning "Fallo en intento $attempt"

        if [ $attempt -lt $max_attempts ]; then
            iact_log_info "Intentando reparar repositorios..."

            # Limpiar listas parciales
            rm -rf /var/lib/apt/lists/partial/*

            # Esperar antes de reintentar
            sleep 2
        fi

        attempt=$((attempt + 1))
    done

    iact_log_error "No se pudo actualizar cache despues de $max_attempts intentos"
    return 1
}

# Instala paquetes con auto-recuperacion
install_essentials() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes esenciales"

    local packages="curl wget gnupg lsb-release software-properties-common apt-transport-https ca-certificates build-essential git"

    export DEBIAN_FRONTEND=noninteractive

    # Verificar si ya estan instalados
    local all_installed=true
    for pkg in $packages; do
        if ! dpkg -l "$pkg" 2>/dev/null | grep -q "^ii"; then
            all_installed=false
            break
        fi
    done

    if [ "$all_installed" = true ]; then
        iact_log_success "Todos los paquetes ya estan instalados"
        return 0
    fi

    # Intentar instalacion
    local max_attempts=2
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        iact_log_info "Instalando paquetes (intento $attempt de $max_attempts)..."

        if apt-get install -y --no-install-recommends $packages 2>&1 | tee -a "$(iact_get_log_file)"; then
            iact_log_success "Paquetes instalados correctamente"
            return 0
        fi

        iact_log_warning "Fallo en intento $attempt"

        if [ $attempt -lt $max_attempts ]; then
            iact_log_info "Intentando reparar dependencias..."

            # Intentar reparar paquetes rotos
            apt-get install -f -y 2>&1 | tee -a "$(iact_get_log_file)" || true
            dpkg --configure -a 2>&1 | tee -a "$(iact_get_log_file)" || true

            # Actualizar cache nuevamente
            apt-get update 2>&1 | tee -a "$(iact_get_log_file)" || true

            sleep 2
        fi

        attempt=$((attempt + 1))
    done

    iact_log_error "No se pudieron instalar paquetes despues de $max_attempts intentos"
    return 1
}

# Verifica comandos esenciales
check_essential_commands() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando comandos esenciales"

    local commands="curl wget gpg apt-get systemctl"
    local missing=""
    local missing_count=0

    for cmd in $commands; do
        if command -v "$cmd" >/dev/null 2>&1; then
            iact_log_info "Comando '$cmd' disponible"
        else
            iact_log_warning "Comando '$cmd' no encontrado"
            if [ -z "$missing" ]; then
                missing="$cmd"
            else
                missing="$missing $cmd"
            fi
            missing_count=$((missing_count + 1))
        fi
    done

    if [ "$missing_count" -eq 0 ]; then
        iact_log_success "Todos los comandos disponibles"
        return 0
    else
        iact_log_error "Comandos faltantes: $missing"
        return 1
    fi
}

# Muestra informacion del sistema
show_system_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion del sistema"

    iact_log_header "INFORMACION DEL SISTEMA"

    if [ -f /etc/os-release ]; then
        source /etc/os-release
        printf '  Sistema: %s %s (%s)\n' "$NAME" "$VERSION" "$VERSION_CODENAME"
    fi

    printf '  Kernel: %s\n' "$(uname -r)"
    printf '  Arquitectura: %s\n' "$(uname -m)"

    local available_kb
    available_kb=$(df / | awk 'NR==2 {print $4}')
    local total_kb
    total_kb=$(df / | awk 'NR==2 {print $2}')
    local available_gb=$((available_kb / 1024 / 1024))
    local total_gb=$((total_kb / 1024 / 1024))
    printf '  Disco: %sGB disponibles de %sGB\n' "$available_gb" "$total_gb"

    if [ -f /proc/meminfo ]; then
        local mem_total_kb
        mem_total_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        local mem_total_gb=$((mem_total_kb / 1024 / 1024))
        printf '  Memoria: %sGB\n' "$mem_total_gb"
    fi

    printf '  Hostname: %s\n' "$(hostname)"
    printf '\n'

    return 0
}

# =============================================================================
# Funciones de paso
# =============================================================================

step_check_ubuntu() {
    check_ubuntu_version "$1" "$2"
}

step_check_disk() {
    check_disk_space "$1" "$2"
}

step_check_internet() {
    check_internet "$1" "$2"
}

step_update_cache() {
    update_apt_cache "$1" "$2"
}

step_install_packages() {
    install_essentials "$1" "$2"
}

step_check_commands() {
    check_essential_commands "$1" "$2"
}

step_show_info() {
    show_system_info "$1" "$2"
}

# =============================================================================
# Reporte de resultados
# =============================================================================

show_results() {
    local total="$1"
    local failed_count="$2"
    local failed_list="$3"

    printf '\n'

    if [ "$failed_count" -eq 0 ]; then
        iact_log_success "Sistema preparado correctamente"
        iact_log_info "Total pasos: $total"

        printf '\n'
        iact_log_header "SISTEMA LISTO"
        printf '%s\n' "Siguiente paso: Instalar bases de datos"
        printf '%s\n' "  - MariaDB: sudo bash mariadb_install.sh"
        printf '%s\n' "  - PostgreSQL: sudo bash postgres_install.sh"
        printf '\n'
        return 0
    fi

    local successful=$((total - failed_count))

    iact_log_error "Completado con $failed_count error(es)"

    local IFS='|'
    for step in $failed_list; do
        iact_log_error "  - $step"
    done

    printf '\n'
    iact_log_info "Pasos exitosos: $successful de $total"

    printf '\n'
    iact_log_header "ACCION REQUERIDA"
    printf '%s\n' "Revise los errores anteriores"
    printf '%s\n' "Log: $(iact_get_log_file)"
    printf '\n'

    return 1
}

# =============================================================================
# Main
# =============================================================================

main() {
    iact_log_header "PREPARACION DEL SISTEMA - UBUNTU 20.04"
    iact_log_info "Context: $(iact_get_context)"

    local total_steps=7
    local current_step=0
    local failed_count=0
    local failed_list=""

    run_step() {
        local step_func="$1"
        current_step=$((current_step + 1))

        if ! "$step_func" "$current_step" "$total_steps"; then
            iact_log_warning "Paso $step_func fallo"

            if [ -z "$failed_list" ]; then
                failed_list="$step_func"
            else
                failed_list="$failed_list|$step_func"
            fi
            failed_count=$((failed_count + 1))
            return 1
        fi
        return 0
    }

    run_step step_check_ubuntu
    run_step step_check_disk
    run_step step_check_internet
    run_step step_update_cache
    run_step step_install_packages
    run_step step_check_commands
    run_step step_show_info

    show_results "$total_steps" "$failed_count" "$failed_list"
}

main "$@"


