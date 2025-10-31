#!/bin/bash
set -euo pipefail

# =============================================================================
# MARIADB INSTALLATION - Instalación y configuración de MariaDB
# =============================================================================
# Descripción: Instala MariaDB en Ubuntu 18.04 con estrategia de fallback
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

# Configuración con valores por defecto
MARIADB_VERSION="${MARIADB_VERSION:-10.6}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"

# Configuración de repositorios - Estrategia de Fallback
MARIADB_CUSTOM_REPO="${MARIADB_CUSTOM_REPO:-https://162.55.42.214/repo}"
MARIADB_OFFICIAL_REPO="https://mirrors.xtom.de/mariadb/repo"

# Cargar módulos core
if [ ! -f "${PROJECT_ROOT}/utils/core.sh" ]; then
    printf 'ERROR: No se encontró %s/utils/core.sh\n' "$PROJECT_ROOT" >&2
    exit 1
fi

# shellcheck disable=SC1090
. "${PROJECT_ROOT}/utils/core.sh"

# Cargar módulos adicionales
if type "iact_source_module" >/dev/null 2>&1; then
    iact_source_module "validation" || {
        printf 'ADVERTENCIA: No se pudo cargar módulo validation\n' >&2
    }
    iact_source_module "database" || {
        printf 'ADVERTENCIA: No se pudo cargar módulo database\n' >&2
    }
fi

# Inicializar logging
if type "iact_init_logging" >/dev/null 2>&1; then
    iact_init_logging "${SCRIPT_NAME%.sh}"
fi

# -----------------------------------------------------------------------------
# Funciones auxiliares - Idempotentes
# -----------------------------------------------------------------------------

# Agrega clave GPG de MariaDB (idempotente)
add_gpg_key() {
    iact_log_info "Agregando clave GPG de MariaDB..."

    # Verificar si la clave ya existe
    if apt-key list 2>/dev/null | grep -q "MariaDB"; then
        iact_log_info "Clave GPG de MariaDB ya existe"
        return 0
    fi

    # Intentar agregar la clave
    if apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Clave GPG de MariaDB agregada"
        return 0
    else
        iact_log_error "Error agregando clave GPG de MariaDB"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Funciones de instalación - Idempotentes y sin fallas silenciosas
# -----------------------------------------------------------------------------

# Configura repositorio de MariaDB con estrategia de fallback (idempotente)
setup_repository() {
    local current="$1"
    local total="$2"
    local repo_file="/etc/apt/sources.list.d/mariadb.list"

    iact_log_step "$current" "$total" "Configurando repositorio de MariaDB"

    # Verificar si ya está configurado
    if [ -f "$repo_file" ]; then
        iact_log_info "Repositorio de MariaDB ya configurado"
        return 0
    fi

    # Agregar clave GPG
    if ! add_gpg_key; then
        iact_log_error "No se pudo agregar clave GPG de MariaDB"
        return 1
    fi

    iact_log_info "Configurando repositorio con estrategia de fallback..."

    # Crear archivo de repositorio con estrategia de fallback
    cat > "$repo_file" <<EOF
# MariaDB $MARIADB_VERSION Repository - Fallback Strategy
# =============================================================================
# TIER 1: Custom/Corporate Mirror (May be faster in your network)
deb [arch=amd64,arm64,ppc64el] $MARIADB_CUSTOM_REPO/$MARIADB_VERSION/ubuntu bionic main

# TIER 2: Official MariaDB Mirror (Fallback)
deb [arch=amd64,arm64,ppc64el] $MARIADB_OFFICIAL_REPO/$MARIADB_VERSION/ubuntu bionic main
EOF

    if [ $? -ne 0 ]; then
        iact_log_error "Error creando archivo de repositorio"
        return 1
    fi

    iact_log_success "Archivo de repositorio creado: $repo_file"

    # Actualizar cache de paquetes
    iact_log_info "Actualizando cache de paquetes..."
    if ! apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi

    iact_log_success "Repositorio de MariaDB configurado correctamente"

    # Verificar qué repositorio está activo
    iact_log_info "Verificando repositorio activo..."
    if apt-cache policy mariadb-server 2>/dev/null | grep -q "$MARIADB_CUSTOM_REPO"; then
        iact_log_success "Usando repositorio custom (TIER 1): $MARIADB_CUSTOM_REPO"
    elif apt-cache policy mariadb-server 2>/dev/null | grep -q "$MARIADB_OFFICIAL_REPO"; then
        iact_log_success "Usando repositorio oficial (TIER 2): $MARIADB_OFFICIAL_REPO"
    else
        iact_log_warning "No se pudo determinar el repositorio activo"
    fi

    return 0
}

# Instala paquetes de MariaDB (idempotente - APT maneja paquetes instalados)
install_packages() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes de MariaDB"

    # Verificar si ya está instalado y ejecutándose
    if type "iact_check_mariadb_client" >/dev/null 2>&1; then
        if iact_check_mariadb_client && systemctl is-active --quiet mariadb 2>/dev/null; then
            iact_log_info "MariaDB ya instalado y en ejecución"
            return 0
        fi
    fi

    local packages="mariadb-server mariadb-client mariadb-common"

    iact_log_info "Paquetes a instalar: $packages"

    export DEBIAN_FRONTEND=noninteractive

    # shellcheck disable=SC2086
    if apt-get install -y --no-install-recommends $packages 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Paquetes de MariaDB instalados correctamente"
        return 0
    else
        iact_log_error "Error instalando paquetes de MariaDB"
        return 1
    fi
}

# Configura servicio de MariaDB (idempotente)
configure_service() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando servicio de MariaDB"

    # Habilitar servicio
    iact_log_info "Habilitando servicio MariaDB..."
    if ! systemctl enable mariadb 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error habilitando servicio MariaDB"
        return 1
    fi

    # Iniciar servicio
    iact_log_info "Iniciando servicio MariaDB..."
    if ! systemctl start mariadb 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error iniciando servicio MariaDB"
        return 1
    fi

    # Esperar a que el servicio esté listo
    iact_log_info "Esperando a que MariaDB esté listo..."
    local timeout=30
    local counter=0

    while [ "$counter" -lt "$timeout" ]; do
        if mysqladmin ping >/dev/null 2>&1; then
            iact_log_success "Servicio MariaDB iniciado y respondiendo (${counter}s)"
            return 0
        fi
        sleep 1
        counter=$((counter + 1))
    done

    iact_log_error "MariaDB no respondió después de ${timeout}s"
    return 1
}

# Asegura instalación de MariaDB (idempotente)
secure_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando seguridad de MariaDB"

    # Configurar password de root
    iact_log_info "Configurando password de root..."
    if mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASSWORD'; FLUSH PRIVILEGES;" 2>/dev/null; then
        iact_log_success "Password de root configurado"
    else
        # Intentar método alternativo para instalaciones frescas
        if mysqladmin -u root password "$DB_ROOT_PASSWORD" 2>/dev/null; then
            iact_log_success "Password de root configurado (método alternativo)"
        else
            iact_log_warning "Password de root puede estar ya configurado o usando unix_socket"
        fi
    fi

    # Eliminar usuarios anónimos
    iact_log_info "Eliminando usuarios anónimos..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='';" 2>/dev/null; then
        iact_log_success "Usuarios anónimos eliminados"
    else
        iact_log_warning "No se pudieron eliminar usuarios anónimos (puede ser normal)"
    fi

    # Deshabilitar login remoto de root
    iact_log_info "Deshabilitando login remoto de root..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');" 2>/dev/null; then
        iact_log_success "Login remoto de root deshabilitado"
    else
        iact_log_warning "No se pudo deshabilitar login remoto de root"
    fi

    # Eliminar base de datos de prueba
    iact_log_info "Eliminando base de datos de prueba..."
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS test;" 2>/dev/null || true
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';" 2>/dev/null || true
    iact_log_success "Base de datos de prueba eliminada"

    # Aplicar cambios
    iact_log_info "Aplicando cambios de privilegios..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>/dev/null; then
        iact_log_success "Privilegios actualizados"
    else
        iact_log_warning "No se pudieron actualizar privilegios"
    fi

    iact_log_success "Configuración de seguridad completada"
    return 0
}

# Verifica instalación de MariaDB (idempotente)
verify_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalación de MariaDB"

    # Verificar cliente
    if type "iact_check_mariadb_client" >/dev/null 2>&1; then
        if ! iact_check_mariadb_client; then
            iact_log_error "Cliente de MariaDB no encontrado"
            return 1
        fi
        iact_log_success "Cliente de MariaDB disponible"
    fi

    # Verificar servicio
    if ! systemctl is-active --quiet mariadb; then
        iact_log_error "Servicio MariaDB no está en ejecución"
        return 1
    fi
    iact_log_success "Servicio MariaDB en ejecución"

    # Probar conectividad con root
    if ! mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
        iact_log_error "No se puede conectar con el usuario root"
        return 1
    fi
    iact_log_success "Conexión con usuario root exitosa"

    # Obtener versión
    local version
    version=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" 2>/dev/null | tail -n 1)
    iact_log_info "Versión de MariaDB: $version"

    # Mostrar origen del paquete
    iact_log_info "Verificando origen del paquete..."
    local package_origin
    package_origin=$(apt-cache policy mariadb-server 2>/dev/null | grep "Installed" | head -1)
    iact_log_info "Información del paquete: $package_origin"

    iact_log_success "Verificación de instalación completada"
    return 0
}

# Muestra información de instalación
show_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Información de instalación"

    printf '\n'
    printf '%s\n' "=================================================================="
    printf '%s\n' "                  INFORMACION DE MARIADB"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Versión: $MARIADB_VERSION"
    printf '%s\n' "Estado del servicio: $(systemctl is-active mariadb 2>/dev/null || echo 'unknown')"
    printf '\n'
    printf '%s\n' "Estrategia de repositorio: Fallback"
    printf '%s\n' "  TIER 1 (Custom): $MARIADB_CUSTOM_REPO"
    printf '%s\n' "  TIER 2 (Official): $MARIADB_OFFICIAL_REPO"
    printf '\n'
    printf '%s\n' "CREDENCIALES (GUARDAR DE FORMA SEGURA):"
    printf '%s\n' "  Usuario root: root"
    printf '%s\n' "  Password root: $DB_ROOT_PASSWORD"
    printf '\n'
    printf '%s\n' "Comando de conexión:"
    printf '%s\n' "  mysql -u root -p'$DB_ROOT_PASSWORD'"
    printf '\n'
    printf '%s\n' "Logs: $(iact_get_log_file)"
    printf '\n'
    printf '%s\n' "=================================================================="
    printf '\n'

    return 0
}

# -----------------------------------------------------------------------------
# Funciones de paso - Una por paso, con validación explícita
# -----------------------------------------------------------------------------

step_setup_repo() {
    local current="$1"
    local total="$2"

    if ! setup_repository "$current" "$total"; then
        iact_log_error "Error configurando repositorio"
        return 1
    fi
    return 0
}

step_install() {
    local current="$1"
    local total="$2"

    if ! install_packages "$current" "$total"; then
        iact_log_error "Error instalando paquetes"
        return 1
    fi
    return 0
}

step_configure_service() {
    local current="$1"
    local total="$2"

    if ! configure_service "$current" "$total"; then
        iact_log_error "Error configurando servicio"
        return 1
    fi
    return 0
}

step_secure() {
    local current="$1"
    local total="$2"

    if ! secure_installation "$current" "$total"; then
        iact_log_error "Error asegurando instalación"
        return 1
    fi
    return 0
}

step_verify() {
    local current="$1"
    local total="$2"

    if ! verify_installation "$current" "$total"; then
        iact_log_error "Error verificando instalación"
        return 1
    fi
    return 0
}

step_show_info() {
    local current="$1"
    local total="$2"

    if ! show_info "$current" "$total"; then
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
        iact_log_success "Instalación de MariaDB completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "MariaDB está listo para usar"
        return 0
    fi

    successful=$((total - failed_count))

    iact_log_error "Instalación completada con $failed_count error(es):"

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
    iact_log_header "MARIADB INSTALLATION - UBUNTU 18.04"
    iact_log_info "Instalando MariaDB $MARIADB_VERSION"
    iact_log_info "Context: $(iact_get_context)"
    iact_log_info "Strategy: Fallback (Custom + Official repos)"

    local total_steps=6
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
    run_step step_setup_repo
    run_step step_install
    run_step step_configure_service
    run_step step_secure
    run_step step_verify
    run_step step_show_info

    # Mostrar resultados finales
    show_results "$total_steps" "$failed_count" "$failed_list"
}

# Ejecutar main
main "$@"