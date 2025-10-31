#!/bin/bash
set -euo pipefail

# =============================================================================
# MariaDB Installation - Ubuntu 20.04
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
fi

# Configuracion
MARIADB_VERSION="${MARIADB_VERSION:-11.4}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"
LOG_FILE="/tmp/mariadb-install.log"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# =============================================================================
# Funciones de logging
# =============================================================================

log_init() {
    : > "$LOG_FILE"
    {
        echo "=================================================================="
        echo "Log iniciado: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Script: $SCRIPT_NAME"
        echo "Host: $(hostname)"
        echo "User: $(whoami)"
        echo "=================================================================="
        echo ""
    } >> "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
    echo "[INFO] $*" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $*"
    echo "[OK] $*" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
    echo "[WARNING] $*" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
    echo "[ERROR] $*" >> "$LOG_FILE"
}

log_step() {
    local current="$1"
    local total="$2"
    shift 2
    echo ""
    echo -e "${BLUE}[PASO $current/$total]${NC} $*"
    echo "----------------------------------------------------------------------"
    echo "[STEP $current/$total] $*" >> "$LOG_FILE"
}

log_header() {
    echo ""
    echo "=================================================================="
    echo "$*"
    echo "=================================================================="
    echo ""
    echo "[HEADER] $*" >> "$LOG_FILE"
}

# =============================================================================
# Funciones auxiliares
# =============================================================================

# Verifica si MariaDB esta instalado
mariadb_is_installed() {
    command -v mysql >/dev/null 2>&1
}

# Verifica si servicio MariaDB esta corriendo
mariadb_is_running() {
    systemctl is-active --quiet mariadb 2>/dev/null || systemctl is-active --quiet mysql 2>/dev/null
}

# Verifica conexion a MariaDB
mariadb_can_connect() {
    local user="$1"
    local password="$2"
    mysql -u "$user" -p"$password" -e "SELECT 1;" >/dev/null 2>&1
}

# =============================================================================
# Configuracion de repositorio
# =============================================================================

setup_mariadb_repository() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Configurando repositorio MariaDB $MARIADB_VERSION"

    # Importar clave GPG
    log_info "Importando clave GPG de MariaDB..."

    local gpg_imported=false
    local max_attempts=3
    local attempt=1

    while [ $attempt -le $max_attempts ] && [ "$gpg_imported" = false ]; do
        log_info "Intento $attempt de $max_attempts..."

        # Metodo 1: Desde servidor de claves
        if curl -fsSL https://mariadb.org/mariadb_release_signing_key.asc 2>/dev/null | apt-key add - >/dev/null 2>&1; then
            log_success "Clave GPG importada desde mariadb.org"
            gpg_imported=true
            break
        fi

        # Metodo 2: Desde keyserver
        if apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 >/dev/null 2>&1; then
            log_success "Clave GPG importada desde keyserver"
            gpg_imported=true
            break
        fi

        if [ $attempt -lt $max_attempts ]; then
            log_warning "Fallo en intento $attempt, reintentando..."
            sleep 2
        fi

        attempt=$((attempt + 1))
    done

    if [ "$gpg_imported" = false ]; then
        log_warning "No se pudo importar clave GPG, usando [trusted=yes]"
    fi

    # Configurar repositorio oficial
    log_info "Configurando repositorio oficial de MariaDB..."

    local repo_url="http://mirror.mariadb.org/repo/$MARIADB_VERSION/ubuntu"
    local repo_file="/etc/apt/sources.list.d/mariadb.list"

    if [ "$gpg_imported" = true ]; then
        echo "deb [arch=amd64,arm64,ppc64el] $repo_url focal main" > "$repo_file"
    else
        echo "deb [arch=amd64,arm64,ppc64el trusted=yes] $repo_url focal main" > "$repo_file"
    fi

    log_success "Repositorio configurado: $repo_file"
    log_info "URL: $repo_url"

    # Actualizar cache con reintentos
    log_info "Actualizando cache de paquetes..."

    local cache_updated=false
    max_attempts=3
    attempt=1

    while [ $attempt -le $max_attempts ] && [ "$cache_updated" = false ]; do
        log_info "Intento $attempt de $max_attempts..."

        if apt-get update 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Cache actualizado correctamente"
            cache_updated=true
            break
        fi

        if [ $attempt -lt $max_attempts ]; then
            log_warning "Fallo en intento $attempt"

            # Limpiar listas parciales
            rm -rf /var/lib/apt/lists/partial/* 2>/dev/null || true

            sleep 2
        fi

        attempt=$((attempt + 1))
    done

    if [ "$cache_updated" = false ]; then
        log_error "No se pudo actualizar cache despues de $max_attempts intentos"
        return 1
    fi

    log_success "Repositorio MariaDB configurado exitosamente"
    return 0
}

# =============================================================================
# Instalacion de MariaDB
# =============================================================================

install_mariadb_packages() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Instalando MariaDB $MARIADB_VERSION"

    # Verificar si ya esta instalado
    if mariadb_is_installed && mariadb_is_running; then
        log_success "MariaDB ya esta instalado y corriendo"

        # Verificar version
        local installed_version
        installed_version=$(mysql --version 2>/dev/null | grep -oP 'Distrib \K[0-9.]+' || echo "desconocida")
        log_info "Version instalada: $installed_version"

        return 0
    fi

    # Instalar paquetes
    local packages=(
        "mariadb-server"
        "mariadb-client"
        "mariadb-common"
    )

    log_info "Paquetes a instalar: ${packages[*]}"

    export DEBIAN_FRONTEND=noninteractive

    local max_attempts=2
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Instalando (intento $attempt de $max_attempts)..."

        if apt-get install -y "${packages[@]}" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "MariaDB instalado correctamente"

            # Verificar instalacion
            if mariadb_is_installed; then
                local version
                version=$(mysql --version 2>/dev/null | grep -oP 'Distrib \K[0-9.]+' || echo "desconocida")
                log_info "Version instalada: $version"
                return 0
            else
                log_error "Instalacion completada pero comando mysql no disponible"
                return 1
            fi
        fi

        log_warning "Fallo en intento $attempt"

        if [ $attempt -lt $max_attempts ]; then
            log_info "Reparando dependencias..."

            apt-get install -f -y 2>&1 | tee -a "$LOG_FILE" || true
            dpkg --configure -a 2>&1 | tee -a "$LOG_FILE" || true

            sleep 2
        fi

        attempt=$((attempt + 1))
    done

    log_error "No se pudo instalar MariaDB despues de $max_attempts intentos"
    return 1
}

# =============================================================================
# Configuracion del servicio
# =============================================================================

configure_mariadb_service() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Configurando servicio MariaDB"

    # Iniciar servicio
    log_info "Iniciando servicio MariaDB..."

    if systemctl start mariadb 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Servicio iniciado"
    elif systemctl start mysql 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Servicio iniciado (como mysql)"
    else
        log_error "No se pudo iniciar servicio"
        return 1
    fi

    # Habilitar en boot
    systemctl enable mariadb >/dev/null 2>&1 || systemctl enable mysql >/dev/null 2>&1 || true

    # Esperar a que este listo
    log_info "Esperando a que MariaDB este listo..."

    local max_wait=30
    local counter=0

    while [ $counter -lt $max_wait ]; do
        if mysql -e "SELECT 1;" >/dev/null 2>&1; then
            log_success "MariaDB esta respondiendo"
            return 0
        fi

        sleep 2
        counter=$((counter + 2))
    done

    log_error "MariaDB no respondio despues de ${max_wait}s"
    return 1
}

# =============================================================================
# Configuracion de seguridad
# =============================================================================

secure_mariadb_installation() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Configurando seguridad de MariaDB"

    # Establecer contraseña root
    log_info "Estableciendo contraseña root..."

    if mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASSWORD'; FLUSH PRIVILEGES;" 2>/dev/null; then
        log_success "Contraseña root establecida"
    elif mysqladmin -u root password "$DB_ROOT_PASSWORD" 2>/dev/null; then
        log_success "Contraseña root establecida (metodo alternativo)"
    else
        log_warning "No se pudo establecer contraseña (puede ya estar configurada)"
    fi

    # Verificar conexion con contraseña
    if mariadb_can_connect "root" "$DB_ROOT_PASSWORD"; then
        log_success "Conexion con contraseña verificada"
    else
        log_warning "No se puede conectar con contraseña, puede usar unix_socket"
    fi

    # Remover usuarios anonimos
    log_info "Removiendo usuarios anonimos..."
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='';" 2>/dev/null || true

    # Deshabilitar login root remoto
    log_info "Deshabilitando login root remoto..."
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');" 2>/dev/null || true

    # Remover base de datos test
    log_info "Removiendo base de datos test..."
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS test;" 2>/dev/null || true
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';" 2>/dev/null || true

    # Aplicar privilegios
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>/dev/null || true

    log_success "Configuracion de seguridad completada"
    return 0
}

# =============================================================================
# Verificacion
# =============================================================================

verify_mariadb_installation() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Verificando instalacion"

    # Verificar comando
    if ! mariadb_is_installed; then
        log_error "Comando mysql no encontrado"
        return 1
    fi
    log_success "Comando mysql disponible"

    # Verificar servicio
    if ! mariadb_is_running; then
        log_error "Servicio MariaDB no esta corriendo"
        return 1
    fi
    log_success "Servicio MariaDB activo"

    # Verificar conexion
    if mariadb_can_connect "root" "$DB_ROOT_PASSWORD"; then
        log_success "Conexion con contraseña root verificada"
    else
        log_warning "No se puede conectar con contraseña, verificando unix_socket..."

        if mysql -u root -e "SELECT 1;" >/dev/null 2>&1; then
            log_success "Conexion con unix_socket funcional"
        else
            log_error "No se puede conectar a MariaDB"
            return 1
        fi
    fi

    # Mostrar version
    local version
    version=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" 2>/dev/null | tail -n 1 || echo "desconocida")
    log_info "Version: $version"

    log_success "Verificacion completada"
    return 0
}

# =============================================================================
# Main
# =============================================================================

main() {
    log_init

    log_header "INSTALACION MARIADB $MARIADB_VERSION - UBUNTU 20.04"
    log_info "Password root: $DB_ROOT_PASSWORD"

    # Verificar permisos root
    if [ "$EUID" -ne 0 ]; then
        log_error "Este script debe ejecutarse como root (usa sudo)"
        exit 1
    fi

    local total_steps=4
    local current_step=0
    local failed=false

    # Paso 1: Configurar repositorio
    current_step=1
    if ! setup_mariadb_repository "$current_step" "$total_steps"; then
        log_error "Fallo configuracion de repositorio"
        failed=true
    fi

    # Paso 2: Instalar paquetes
    if [ "$failed" = false ]; then
        current_step=2
        if ! install_mariadb_packages "$current_step" "$total_steps"; then
            log_error "Fallo instalacion de paquetes"
            failed=true
        fi
    fi

    # Paso 3: Configurar servicio
    if [ "$failed" = false ]; then
        current_step=3
        if ! configure_mariadb_service "$current_step" "$total_steps"; then
            log_error "Fallo configuracion de servicio"
            failed=true
        fi
    fi

    # Paso 4: Configurar seguridad
    if [ "$failed" = false ]; then
        current_step=4
        if ! secure_mariadb_installation "$current_step" "$total_steps"; then
            log_warning "Configuracion de seguridad incompleta (no critico)"
        fi
    fi

    # Verificacion final
    if [ "$failed" = false ]; then
        if ! verify_mariadb_installation 5 5; then
            log_error "Verificacion fallo"
            failed=true
        fi
    fi

    # Resultado final
    echo ""
    if [ "$failed" = false ]; then
        log_header "MARIADB INSTALADO EXITOSAMENTE"
        printf '%s\n' "Credenciales:"
        printf '%s\n' "  Usuario: root"
        printf '%s\n' "  Password: $DB_ROOT_PASSWORD"
        printf '\n'
        printf '%s\n' "Conexion:"
        printf '%s\n' "  mysql -u root -p'$DB_ROOT_PASSWORD'"
        printf '\n'
        printf '%s\n' "Log: $LOG_FILE"
        printf '\n'
        exit 0
    else
        log_header "INSTALACION FALLIDA"
        printf '%s\n' "Revise los errores en: $LOG_FILE"
        printf '\n'
        exit 1
    fi
}

main "$@"