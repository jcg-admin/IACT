#!/bin/bash
set -euo pipefail

# =============================================================================
# SYSTEM PREPARATION - Preparación del sistema para bases de datos
# =============================================================================
# Descripción: Prepara Ubuntu 18.04 para instalación de bases de datos
# Patrón: Funcional, Idempotente, Sin fallas silenciosas, POSIX
# =============================================================================

# -----------------------------------------------------------------------------
# Setup - Configuración inicial
# -----------------------------------------------------------------------------

# Detectar directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Detectar PROJECT_ROOT
if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
else
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

# Cargar módulos core
if [ ! -f "${PROJECT_ROOT}/utils/core.sh" ]; then
    printf 'ERROR: No se encontró %s/utils/core.sh\n' "$PROJECT_ROOT" >&2
    exit 1
fi

# shellcheck disable=SC1090
. "${PROJECT_ROOT}/utils/core.sh"

# Cargar módulo de validación si está disponible
if type "iact_source_module" >/dev/null 2>&1; then
    iact_source_module "validation" || {
        printf 'ADVERTENCIA: No se pudo cargar módulo validation\n' >&2
    }
fi

# Inicializar logging
if type "iact_init_logging" >/dev/null 2>&1; then
    iact_init_logging "${SCRIPT_NAME%.sh}"
fi

# -----------------------------------------------------------------------------
# Funciones de validación - Idempotentes y sin fallas silenciosas
# -----------------------------------------------------------------------------

# Verifica versión de Ubuntu (idempotente)
check_ubuntu_version() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando versión de Ubuntu"

    if ! type "iact_validate_ubuntu_version" >/dev/null 2>&1; then
        iact_log_error "Función iact_validate_ubuntu_version no disponible"
        return 1
    fi

    if iact_validate_ubuntu_version; then
        iact_log_success "Versión de Ubuntu verificada: 18.04 LTS"
        return 0
    else
        iact_log_error "Versión de Ubuntu no soportada"
        return 1
    fi
}

# Verifica espacio en disco (idempotente)
check_disk_space() {
    local current="$1"
    local total="$2"
    local required_gb=10

    iact_log_step "$current" "$total" "Verificando espacio en disco"

    if ! type "iact_validate_disk_space" >/dev/null 2>&1; then
        iact_log_error "Función iact_validate_disk_space no disponible"
        return 1
    fi

    if iact_validate_disk_space "$required_gb"; then
        iact_log_success "Espacio en disco suficiente (mínimo: ${required_gb}GB)"
        return 0
    else
        iact_log_error "Espacio en disco insuficiente (mínimo requerido: ${required_gb}GB)"
        return 1
    fi
}

# Verifica conectividad a Internet (idempotente)
check_internet() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando conectividad a Internet"

    if ! type "iact_validate_internet" >/dev/null 2>&1; then
        iact_log_error "Función iact_validate_internet no disponible"
        return 1
    fi

    if iact_validate_internet; then
        iact_log_success "Conectividad a Internet verificada"
        return 0
    else
        iact_log_error "No hay conectividad a Internet"
        return 1
    fi
}

# Actualiza cache de paquetes APT (idempotente)
update_apt_cache() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Actualizando cache de paquetes APT"

    export DEBIAN_FRONTEND=noninteractive

    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Cache de paquetes actualizado"
        return 0
    else
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi
}

# Instala paquetes esenciales (idempotente - APT maneja paquetes ya instalados)
install_essentials() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes esenciales"

    # Lista de paquetes requeridos
    local packages="curl wget gnupg lsb-release software-properties-common apt-transport-https ca-certificates build-essential git"

    iact_log_info "Paquetes a instalar: $packages"

    export DEBIAN_FRONTEND=noninteractive

    # shellcheck disable=SC2086
    if apt-get install -y --no-install-recommends $packages 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Paquetes esenciales instalados correctamente"
        return 0
    else
        iact_log_error "Error instalando paquetes esenciales"
        return 1
    fi
}

# Verifica disponibilidad de comandos esenciales (idempotente)
check_essential_commands() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando comandos esenciales"

    local commands="curl wget gpg apt-get systemctl"
    local missing=""
    local missing_count=0

    if ! type "iact_command_exists" >/dev/null 2>&1; then
        iact_log_error "Función iact_command_exists no disponible"
        return 1
    fi

    # Verificar cada comando
    for cmd in $commands; do
        if iact_command_exists "$cmd"; then
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
        iact_log_success "Todos los comandos esenciales están disponibles"
        return 0
    else
        iact_log_error "Comandos faltantes: $missing"
        return 1
    fi
}

# Muestra información del sistema
show_system_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información del sistema"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "                  INFORMACION DEL SISTEMA"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Sistema Operativo:"
    lsb_release -a 2>/dev/null | grep -E "Description|Release|Codename" || true
    printf '\n'
    printf '%s\n' "Kernel:"
    uname -r
    printf '\n'
    printf '%s\n' "Espacio en disco:"
    df -h / | tail -1
    printf '\n'
    printf '%s\n' "Memoria:"
    free -h | grep "Mem:" || true
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

# -----------------------------------------------------------------------------
# Funciones de paso - Una por paso, con validación explícita
# -----------------------------------------------------------------------------

step_check_ubuntu() {
    local current="$1"
    local total="$2"

    if ! check_ubuntu_version "$current" "$total"; then
        iact_log_error "Error verificando versión de Ubuntu"
        return 1
    fi
    return 0
}

step_check_disk() {
    local current="$1"
    local total="$2"

    if ! check_disk_space "$current" "$total"; then
        iact_log_error "Error verificando espacio en disco"
        return 1
    fi
    return 0
}

step_check_internet() {
    local current="$1"
    local total="$2"

    if ! check_internet "$current" "$total"; then
        iact_log_error "Error verificando conectividad"
        return 1
    fi
    return 0
}

step_update_cache() {
    local current="$1"
    local total="$2"

    if ! update_apt_cache "$current" "$total"; then
        iact_log_error "Error actualizando cache"
        return 1
    fi
    return 0
}

step_install_packages() {
    local current="$1"
    local total="$2"

    if ! install_essentials "$current" "$total"; then
        iact_log_error "Error instalando paquetes"
        return 1
    fi
    return 0
}

step_check_commands() {
    local current="$1"
    local total="$2"

    if ! check_essential_commands "$current" "$total"; then
        iact_log_error "Error verificando comandos"
        return 1
    fi
    return 0
}

step_show_info() {
    local current="$1"
    local total="$2"

    if ! show_system_info "$current" "$total"; then
        iact_log_error "Error mostrando información"
        return 1
    fi
    return 0
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
        iact_log_success "Preparación del sistema completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Sistema listo para instalación de bases de datos"
        return 0
    fi

    successful=$((total - failed_count))

    iact_log_error "Preparación completada con $failed_count error(es):"

    # Mostrar cada fallo (POSIX compatible sin arrays)
    local IFS='|'
    for step in $failed_list; do
        iact_log_error "  - $step"
    done

    iact_log_info "Total pasos ejecutados: $total"
    iact_log_info "Pasos exitosos: $successful"
    return 1
}

# -----------------------------------------------------------------------------
# Main - Composición directa sin abstracciones innecesarias
# -----------------------------------------------------------------------------

main() {
    iact_log_header "SYSTEM PREPARATION - UBUNTU 18.04"
    iact_log_info "Preparando sistema para instalación de bases de datos"
    iact_log_info "Context: $(iact_get_context)"

    local total_steps=7
    local current_step=0
    local failed_count=0
    local failed_list=""

    # Helper para ejecutar paso y registrar fallo sin abortar
    run_step() {
        local step_func="$1"

        current_step=$((current_step + 1))

        if ! "$step_func" "$current_step" "$total_steps"; then
            iact_log_warning "Paso $step_func falló (continuando con siguientes pasos)"

            # Acumular fallos
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

    iact_log_info "Total de pasos a ejecutar: $total_steps"

    # Ejecutar todos los pasos - composición directa
    run_step step_check_ubuntu
    run_step step_check_disk
    run_step step_check_internet
    run_step step_update_cache
    run_step step_install_packages
    run_step step_check_commands
    run_step step_show_info

    # Mostrar resultados finales
    show_results "$total_steps" "$failed_count" "$failed_list"
}

# Ejecutar main
main "$@"