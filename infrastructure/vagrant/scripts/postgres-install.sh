#!/bin/bash
set -euo pipefail

# =============================================================================
# PostgreSQL Installation - Ubuntu 20.04
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
fi

# Configuracion
POSTGRES_VERSION="${POSTGRES_VERSION:-16}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgrespass123}"
LOG_FILE="/tmp/postgres-install.log"

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

# Verifica si PostgreSQL esta instalado
postgres_is_installed() {
    command -v psql >/dev/null 2>&1
}

# Verifica si servicio PostgreSQL esta corriendo
postgres_is_running() {
    systemctl is-active --quiet postgresql 2>/dev/null
}

# Verifica conexion a PostgreSQL
postgres_can_connect() {
    local user="$1"
    local password="$2"
    PGPASSWORD="$password" psql -U "$user" -h localhost -c "SELECT 1;" >/dev/null 2>&1
}

# =============================================================================
# Configuracion de repositorio
# =============================================================================

setup_postgresql_repository() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Configurando repositorio PostgreSQL $POSTGRES_VERSION"

    # Instalar dependencias si no existen
    if ! command -v wget >/dev/null 2>&1; then
        log_info "Instalando wget..."
        apt-get update >/dev/null 2>&1 || true
        apt-get install -y wget >/dev/null 2>&1 || true
    fi

    # Importar clave GPG
    log_info "Importando clave GPG de PostgreSQL..."

    local gpg_imported=false
    local max_attempts=3
    local attempt=1

    while [ $attempt -le $max_attempts ] && [ "$gpg_imported" = false ]; do
        log_info "Intento $attempt de $max_attempts..."

        # Metodo 1: Desde postgresql.org
        if wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc 2>/dev/null | apt-key add - >/dev/null 2>&1; then
            log_success "Clave GPG importada desde postgresql.org"
            gpg_imported=true
            break
        fi

        # Metodo 2: Desde keyserver
        if apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 7FCC7D46ACCC4CF8 >/dev/null 2>&1; then
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

    # Configurar repositorio oficial con fallback
    log_info "Configurando repositorio oficial de PostgreSQL..."

    local repo_file="/etc/apt/sources.list.d/pgdg.list"
    local distro="focal"

    # Lista de mirrors oficiales en orden de prioridad
    local mirrors=(
        "http://apt.postgresql.org/pub/repos/apt"
        "http://apt-archive.postgresql.org/pub/repos/apt"
        "http://ftp.postgresql.org/pub/repos/apt"
    )

    local working_mirror=""

    # Probar cada mirror
    for mirror in "${mirrors[@]}"; do
        log_info "Probando mirror: $mirror"

        local test_url="${mirror}/dists/${distro}-pgdg/InRelease"

        if timeout 10 wget --spider --quiet "$test_url" 2>/dev/null; then
            log_success "Mirror accesible: $mirror"
            working_mirror="$mirror"
            break
        else
            log_warning "Mirror no accesible: $mirror"
        fi
    done

    if [ -z "$working_mirror" ]; then
        log_warning "Ningun mirror oficial respondio, usando primer mirror sin verificacion"
        working_mirror="${mirrors[0]}"
    fi

    # Crear archivo de repositorio
    if [ "$gpg_imported" = true ]; then
        echo "deb [arch=amd64] $working_mirror ${distro}-pgdg main" > "$repo_file"
    else
        echo "deb [arch=amd64 trusted=yes] $working_mirror ${distro}-pgdg main" > "$repo_file"
    fi

    log_success "Repositorio configurado: $repo_file"
    log_info "Mirror: $working_mirror"

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

    log_success "Repositorio PostgreSQL configurado exitosamente"
    return 0
}

# =============================================================================
# Instalacion de PostgreSQL
# =============================================================================

install_postgresql_packages() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Instalando PostgreSQL $POSTGRES_VERSION"

    # Verificar si ya esta instalado
    if postgres_is_installed && postgres_is_running; then
        log_success "PostgreSQL ya esta instalado y corriendo"

        # Verificar version
        local installed_version
        installed_version=$(psql --version 2>/dev/null | grep -oP 'PostgreSQL \K[0-9.]+' || echo "desconocida")
        log_info "Version instalada: $installed_version"

        return 0
    fi

    # Instalar paquetes
    local packages=(
        "postgresql-$POSTGRES_VERSION"
        "postgresql-client-$POSTGRES_VERSION"
        "postgresql-contrib-$POSTGRES_VERSION"
    )

    log_info "Paquetes a instalar: ${packages[*]}"

    export DEBIAN_FRONTEND=noninteractive

    local max_attempts=2
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        log_info "Instalando (intento $attempt de $max_attempts)..."

        if apt-get install -y "${packages[@]}" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "PostgreSQL instalado correctamente"

            # Verificar instalacion
            if postgres_is_installed; then
                local version
                version=$(psql --version 2>/dev/null | grep -oP 'PostgreSQL \K[0-9.]+' || echo "desconocida")
                log_info "Version instalada: $version"
                return 0
            else
                log_error "Instalacion completada pero comando psql no disponible"
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

    log_error "No se pudo instalar PostgreSQL despues de $max_attempts intentos"
    return 1
}

# =============================================================================
# Configuracion del servicio
# =============================================================================

configure_postgresql_service() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Configurando servicio PostgreSQL"

    # Iniciar servicio
    log_info "Iniciando servicio PostgreSQL..."

    if systemctl start postgresql 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Servicio iniciado"
    else
        log_error "No se pudo iniciar servicio"
        return 1
    fi

    # Habilitar en boot
    systemctl enable postgresql >/dev/null 2>&1 || true

    # Esperar a que este listo
    log_info "Esperando a que PostgreSQL este listo..."

    local max_wait=30
    local counter=0

    while [ $counter -lt $max_wait ]; do
        if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "PostgreSQL esta respondiendo"
            return 0
        fi

        sleep 2
        counter=$((counter + 2))
    done

    log_error "PostgreSQL no respondio despues de ${max_wait}s"
    return 1
}

# =============================================================================
# Configuracion de autenticacion
# =============================================================================

configure_postgresql_authentication() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Configurando autenticacion PostgreSQL"

    # Establecer contraseña para usuario postgres
    log_info "Estableciendo contraseña para usuario postgres..."

    if sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '$POSTGRES_PASSWORD';" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Contraseña establecida"
    else
        log_error "No se pudo establecer contraseña"
        return 1
    fi

    # Configurar pg_hba.conf
    log_info "Configurando pg_hba.conf..."

    local pg_hba_conf
    pg_hba_conf=$(sudo -u postgres psql -t -P format=unaligned -c "SHOW hba_file;" 2>/dev/null | tr -d ' ')

    if [ -z "$pg_hba_conf" ] || [ ! -f "$pg_hba_conf" ]; then
        log_warning "No se pudo encontrar pg_hba.conf automaticamente"

        # Buscar en ubicaciones comunes
        local common_paths=(
            "/etc/postgresql/$POSTGRES_VERSION/main/pg_hba.conf"
            "/etc/postgresql/*/main/pg_hba.conf"
        )

        for path_pattern in "${common_paths[@]}"; do
            local found_file
            found_file=$(ls $path_pattern 2>/dev/null | head -n 1)
            if [ -n "$found_file" ]; then
                pg_hba_conf="$found_file"
                log_info "Encontrado pg_hba.conf en: $pg_hba_conf"
                break
            fi
        done
    fi

    if [ -z "$pg_hba_conf" ] || [ ! -f "$pg_hba_conf" ]; then
        log_warning "No se pudo configurar pg_hba.conf (archivo no encontrado)"
        return 0
    fi

    # Backup del archivo
    cp "$pg_hba_conf" "${pg_hba_conf}.backup.$(date +%Y%m%d_%H%M%S)"
    log_info "Backup creado: ${pg_hba_conf}.backup"

    # Agregar reglas de autenticacion si no existen
    if ! grep -q "# Configuracion para desarrollo local" "$pg_hba_conf" 2>/dev/null; then
        cat >> "$pg_hba_conf" << 'EOF'

# Configuracion para desarrollo local
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF
        log_success "Reglas de autenticacion agregadas"
    else
        log_info "Reglas de autenticacion ya configuradas"
    fi

    # Recargar configuracion
    log_info "Recargando configuracion..."

    if sudo -u postgres psql -c "SELECT pg_reload_conf();" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Configuracion recargada"
    else
        log_warning "No se pudo recargar configuracion (reinicie manualmente si es necesario)"
    fi

    log_success "Autenticacion configurada"
    return 0
}

# =============================================================================
# Verificacion
# =============================================================================

verify_postgresql_installation() {
    local current="$1"
    local total="$2"

    log_step "$current" "$total" "Verificando instalacion"

    # Verificar comando
    if ! postgres_is_installed; then
        log_error "Comando psql no encontrado"
        return 1
    fi
    log_success "Comando psql disponible"

    # Verificar servicio
    if ! postgres_is_running; then
        log_error "Servicio PostgreSQL no esta corriendo"
        return 1
    fi
    log_success "Servicio PostgreSQL activo"

    # Verificar conexion con contraseña
    if postgres_can_connect "postgres" "$POSTGRES_PASSWORD"; then
        log_success "Conexion con contraseña verificada"
    else
        log_warning "No se puede conectar con contraseña, verificando unix_socket..."

        if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "Conexion con unix_socket funcional"
        else
            log_error "No se puede conectar a PostgreSQL"
            return 1
        fi
    fi

    # Mostrar version
    local version
    version=$(sudo -u postgres psql -t -c "SELECT version();" 2>/dev/null | head -n 1 | xargs || echo "desconocida")
    log_info "Version: $version"

    log_success "Verificacion completada"
    return 0
}

# =============================================================================
# Main
# =============================================================================

main() {
    log_init

    log_header "INSTALACION POSTGRESQL $POSTGRES_VERSION - UBUNTU 20.04"
    log_info "Password postgres: $POSTGRES_PASSWORD"

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
    if ! setup_postgresql_repository "$current_step" "$total_steps"; then
        log_error "Fallo configuracion de repositorio"
        failed=true
    fi

    # Paso 2: Instalar paquetes
    if [ "$failed" = false ]; then
        current_step=2
        if ! install_postgresql_packages "$current_step" "$total_steps"; then
            log_error "Fallo instalacion de paquetes"
            failed=true
        fi
    fi

    # Paso 3: Configurar servicio
    if [ "$failed" = false ]; then
        current_step=3
        if ! configure_postgresql_service "$current_step" "$total_steps"; then
            log_error "Fallo configuracion de servicio"
            failed=true
        fi
    fi

    # Paso 4: Configurar autenticacion
    if [ "$failed" = false ]; then
        current_step=4
        if ! configure_postgresql_authentication "$current_step" "$total_steps"; then
            log_warning "Configuracion de autenticacion incompleta (no critico)"
        fi
    fi

    # Verificacion final
    if [ "$failed" = false ]; then
        if ! verify_postgresql_installation 5 5; then
            log_error "Verificacion fallo"
            failed=true
        fi
    fi

    # Resultado final
    echo ""
    if [ "$failed" = false ]; then
        log_header "POSTGRESQL INSTALADO EXITOSAMENTE"
        printf '%s\n' "Credenciales:"
        printf '%s\n' "  Usuario: postgres"
        printf '%s\n' "  Password: $POSTGRES_PASSWORD"
        printf '\n'
        printf '%s\n' "Conexion:"
        printf '%s\n' "  PGPASSWORD='$POSTGRES_PASSWORD' psql -U postgres -h localhost"
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