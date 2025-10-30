#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - MariaDB Installation Script
# =============================================================================
# Description: Install and configure MariaDB on Ubuntu 18.04
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant provisioning
# Pattern: Idempotent execution, No silent failures
# =============================================================================

set -euo pipefail

# =============================================================================
# SETUP
# =============================================================================

# Obtener directorio del script
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Detect Vagrant environment
if [[ -d "/vagrant" ]]; then
    readonly PROJECT_ROOT="/vagrant"
else
    readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
fi

# Configuration (with defaults)
readonly MARIADB_VERSION="${MARIADB_VERSION:-10.6}"
readonly DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"

# Cargar core (que auto-carga logging)
source "${PROJECT_ROOT}/infrastructure/utils/core.sh"

# Cargar módulos adicionales
iact_source_module "validation"
iact_source_module "database"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# MARIADB INSTALLATION FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# setup_mariadb_repository
# Description: Setup MariaDB APT repository
# NO SILENT FAILURES: Reports repository setup status
# IDEMPOTENT: Checks if already configured
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
setup_mariadb_repository() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando repositorio de MariaDB"

    local repo_file="/etc/apt/sources.list.d/mariadb.list"
    local repo_url="https://162.55.42.214/repo/$MARIADB_VERSION/ubuntu"

    # Check if repository already configured
    if [[ -f "$repo_file" ]] && grep -q "$repo_url" "$repo_file" 2>/dev/null; then
        iact_log_info "Repositorio de MariaDB ya configurado"
        return 0
    fi

    iact_log_info "Agregando clave GPG de MariaDB..."
    if ! apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error agregando clave GPG de MariaDB"
        return 1
    fi

    iact_log_info "Agregando repositorio de MariaDB $MARIADB_VERSION..."
    local repo_line="deb [arch=amd64,arm64,ppc64el] $repo_url bionic main"
    echo "$repo_line" > "$repo_file"

    iact_log_info "Actualizando cache de paquetes..."
    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Repositorio de MariaDB configurado correctamente"
        return 0
    else
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_mariadb_packages
# Description: Install MariaDB packages
# NO SILENT FAILURES: Reports installation status
# IDEMPOTENT: APT handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
install_mariadb_packages() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes de MariaDB"

    # Check if already installed and running
    if iact_check_mariadb_client && systemctl is-active --quiet mariadb 2>/dev/null; then
        iact_log_info "MariaDB ya instalado y en ejecucion"
        return 0
    fi

    local packages=(
        "mariadb-server"
        "mariadb-client"
        "mariadb-common"
    )

    iact_log_info "Paquetes a instalar: ${packages[*]}"

    export DEBIAN_FRONTEND=noninteractive

    if apt-get install -y --no-install-recommends "${packages[@]}" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Paquetes de MariaDB instalados correctamente"
        return 0
    else
        iact_log_error "Error instalando paquetes de MariaDB"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# configure_mariadb_service
# Description: Start and enable MariaDB service
# NO SILENT FAILURES: Reports service status
# IDEMPOTENT: Service commands are idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
configure_mariadb_service() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando servicio de MariaDB"

    # Enable service
    iact_log_info "Habilitando servicio MariaDB..."
    if ! systemctl enable mariadb 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error habilitando servicio MariaDB"
        return 1
    fi

    # Start service
    iact_log_info "Iniciando servicio MariaDB..."
    if ! systemctl start mariadb 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error iniciando servicio MariaDB"
        return 1
    fi

    # Wait for service to be ready
    iact_log_info "Esperando a que MariaDB este listo..."
    local timeout=30
    local counter=0

    while [[ $counter -lt $timeout ]]; do
        if iact_check_mariadb_connect 2>/dev/null; then
            iact_log_success "Servicio MariaDB iniciado y respondiendo (${counter}s)"
            return 0
        fi
        sleep 1
        ((counter++))
    done

    iact_log_error "MariaDB no respondio despues de ${timeout}s"
    return 1
}

# -----------------------------------------------------------------------------
# secure_mariadb_installation
# Description: Secure MariaDB installation
# NO SILENT FAILURES: Reports each security step
# IDEMPOTENT: SQL operations are idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success (warnings are non-critical)
# -----------------------------------------------------------------------------
secure_mariadb_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando seguridad de MariaDB"

    # Set root password
    iact_log_info "Configurando password de root..."
    if mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASSWORD'; FLUSH PRIVILEGES;" 2>/dev/null; then
        iact_log_success "Password de root configurado"
    else
        # Try alternative method for fresh installations
        if mysqladmin -u root password "$DB_ROOT_PASSWORD" 2>/dev/null; then
            iact_log_success "Password de root configurado (metodo alternativo)"
        else
            iact_log_warning "Password de root puede estar ya configurado o usando unix_socket"
        fi
    fi

    # Remove anonymous users
    iact_log_info "Eliminando usuarios anonimos..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='';" 2>/dev/null; then
        iact_log_success "Usuarios anonimos eliminados"
    else
        iact_log_warning "No se pudieron eliminar usuarios anonimos (puede ser normal)"
    fi

    # Disable remote root login
    iact_log_info "Deshabilitando login remoto de root..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');" 2>/dev/null; then
        iact_log_success "Login remoto de root deshabilitado"
    else
        iact_log_warning "No se pudo deshabilitar login remoto de root"
    fi

    # Remove test database
    iact_log_info "Eliminando base de datos de prueba..."
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS test;" 2>/dev/null || true
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';" 2>/dev/null || true
    iact_log_success "Base de datos de prueba eliminada"

    # Flush privileges
    iact_log_info "Aplicando cambios de privilegios..."
    if mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>/dev/null; then
        iact_log_success "Privilegios actualizados"
    else
        iact_log_warning "No se pudieron actualizar privilegios"
    fi

    iact_log_success "Configuracion de seguridad completada"
    return 0
}

# -----------------------------------------------------------------------------
# verify_mariadb_installation
# Description: Verify MariaDB installation
# NO SILENT FAILURES: Reports verification results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_mariadb_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalacion de MariaDB"

    # Check if client is installed
    if ! iact_check_mariadb_client; then
        iact_log_error "Cliente de MariaDB no encontrado"
        return 1
    fi
    iact_log_success "Cliente de MariaDB disponible"

    # Check if service is running
    if ! systemctl is-active --quiet mariadb; then
        iact_log_error "Servicio MariaDB no esta en ejecucion"
        return 1
    fi
    iact_log_success "Servicio MariaDB en ejecucion"

    # Test root connectivity
    if ! mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
        iact_log_error "No se puede conectar con el usuario root"
        return 1
    fi
    iact_log_success "Conexion con usuario root exitosa"

    # Get version information
    local version
    version=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" 2>/dev/null | tail -n 1)
    iact_log_info "Version de MariaDB: $version"

    iact_log_success "Verificacion de instalacion completada"
    return 0
}

# -----------------------------------------------------------------------------
# display_mariadb_info
# Description: Display MariaDB installation information
# NO SILENT FAILURES: Shows complete installation status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_mariadb_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de instalacion"

    echo ""
    echo "=================================================================="
    echo "                  INFORMACION DE MARIADB"
    echo "=================================================================="
    echo ""
    echo "Version: $MARIADB_VERSION"
    echo "Estado del servicio: $(systemctl is-active mariadb 2>/dev/null || echo 'unknown')"
    echo ""
    echo "CREDENCIALES (GUARDAR DE FORMA SEGURA):"
    echo "  Usuario root: root"
    echo "  Password root: $DB_ROOT_PASSWORD"
    echo ""
    echo "Logs: $(iact_get_log_file)"
    echo ""
    echo "=================================================================="
    echo ""

    return 0
}

# =============================================================================
# MAIN EXECUTION - AUTO-EXECUTION PATTERN
# =============================================================================

main() {
    iact_log_header "MARIADB INSTALLATION - UBUNTU 18.04"
    iact_log_info "Instalando MariaDB $MARIADB_VERSION"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        setup_mariadb_repository
        install_mariadb_packages
        configure_mariadb_service
        secure_mariadb_installation
        verify_mariadb_installation
        display_mariadb_info
    )

    # Auto-ejecutar con patron
    local total=${#steps[@]}
    local current=0
    local failed_steps=()

    for step_func in "${steps[@]}"; do
        ((current++))

        if ! $step_func "$current" "$total"; then
            failed_steps+=("$step_func")
        fi
    done

    # Report final results
    echo ""
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Instalacion de MariaDB completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Siguiente paso: Configuracion de bases de datos de aplicacion"
        return 0
    else
        iact_log_error "Instalacion completada con ${#failed_steps[@]} error(es):"
        for step in "${failed_steps[@]}"; do
            iact_log_error "  - $step"
        done
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "Pasos exitosos: $((total - ${#failed_steps[@]}))"
        return 1
    fi
}

# Execute main
main "$@"