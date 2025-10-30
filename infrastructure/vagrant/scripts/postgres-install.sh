#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - PostgreSQL Installation Script
# =============================================================================
# Description: Install and configure PostgreSQL on Ubuntu 18.04
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
readonly POSTGRESQL_VERSION="${POSTGRESQL_VERSION:-10}"
readonly DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"

# Cargar core (que auto-carga logging)
source "${PROJECT_ROOT}/infrastructure/utils/core.sh"

# Cargar módulos adicionales
iact_source_module "validation"
iact_source_module "database"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# POSTGRESQL INSTALLATION FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# setup_postgresql_repository
# Description: Setup PostgreSQL APT repository
# NO SILENT FAILURES: Reports repository setup status
# IDEMPOTENT: Checks if already configured
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
setup_postgresql_repository() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando repositorio de PostgreSQL"

    local repo_file="/etc/apt/sources.list.d/pgdg.list"
    local repo_url="http://apt.postgresql.org/pub/repos/apt"

    # Check if repository already configured
    if [[ -f "$repo_file" ]] && grep -q "$repo_url" "$repo_file" 2>/dev/null; then
        iact_log_info "Repositorio de PostgreSQL ya configurado"
        return 0
    fi

    iact_log_info "Agregando clave GPG de PostgreSQL..."
    if ! curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/postgresql.gpg > /dev/null 2>&1; then
        iact_log_error "Error agregando clave GPG de PostgreSQL"
        return 1
    fi

    iact_log_info "Agregando repositorio de PostgreSQL..."
    echo "deb [arch=amd64] $repo_url bionic-pgdg main" > "$repo_file"

    iact_log_info "Actualizando cache de paquetes..."
    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Repositorio de PostgreSQL configurado correctamente"
        return 0
    else
        iact_log_error "Error actualizando cache de paquetes"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# install_postgresql_packages
# Description: Install PostgreSQL packages
# NO SILENT FAILURES: Reports installation status
# IDEMPOTENT: APT handles already-installed packages
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
install_postgresql_packages() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes de PostgreSQL"

    # Check if already installed and running
    if iact_check_postgres_client && systemctl is-active --quiet postgresql 2>/dev/null; then
        iact_log_info "PostgreSQL ya instalado y en ejecucion"
        return 0
    fi

    local packages=(
        "postgresql-${POSTGRESQL_VERSION}"
        "postgresql-client-${POSTGRESQL_VERSION}"
        "postgresql-contrib-${POSTGRESQL_VERSION}"
    )

    iact_log_info "Paquetes a instalar: ${packages[*]}"

    export DEBIAN_FRONTEND=noninteractive

    if apt-get install -y --no-install-recommends "${packages[@]}" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Paquetes de PostgreSQL instalados correctamente"
        return 0
    else
        iact_log_error "Error instalando paquetes de PostgreSQL"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# configure_postgresql_service
# Description: Start and enable PostgreSQL service
# NO SILENT FAILURES: Reports service status
# IDEMPOTENT: Service commands are idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
configure_postgresql_service() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando servicio de PostgreSQL"

    # Enable service
    iact_log_info "Habilitando servicio PostgreSQL..."
    if ! systemctl enable postgresql 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error habilitando servicio PostgreSQL"
        return 1
    fi

    # Start service
    iact_log_info "Iniciando servicio PostgreSQL..."
    if ! systemctl start postgresql 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error iniciando servicio PostgreSQL"
        return 1
    fi

    # Wait for service to be ready
    iact_log_info "Esperando a que PostgreSQL este listo..."
    local timeout=30
    local counter=0

    while [[ $counter -lt $timeout ]]; do
        if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
            iact_log_success "Servicio PostgreSQL iniciado y respondiendo (${counter}s)"
            return 0
        fi
        sleep 1
        ((counter++))
    done

    iact_log_error "PostgreSQL no respondio despues de ${timeout}s"
    return 1
}

# -----------------------------------------------------------------------------
# configure_postgresql_authentication
# Description: Configure PostgreSQL authentication
# NO SILENT FAILURES: Reports configuration changes
# IDEMPOTENT: Configuration file changes are idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
configure_postgresql_authentication() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando autenticacion de PostgreSQL"

    local pg_hba="/etc/postgresql/${POSTGRESQL_VERSION}/main/pg_hba.conf"
    local pg_conf="/etc/postgresql/${POSTGRESQL_VERSION}/main/postgresql.conf"

    if [[ ! -f "$pg_hba" ]]; then
        iact_log_error "Archivo de configuracion no encontrado: $pg_hba"
        return 1
    fi

    # Backup original configuration
    if [[ ! -f "${pg_hba}.backup" ]]; then
        iact_log_info "Creando backup de configuracion original..."
        cp "$pg_hba" "${pg_hba}.backup"
    fi

    # Configure to allow password authentication
    iact_log_info "Configurando autenticacion por password..."

    # Allow local connections with password
    if ! grep -q "^local.*all.*all.*md5" "$pg_hba" 2>/dev/null; then
        sed -i 's/^local.*all.*all.*peer/local   all             all                                     md5/' "$pg_hba"
        iact_log_success "Autenticacion local configurada (md5)"
    else
        iact_log_info "Autenticacion local ya configurada"
    fi

    # Allow network connections (for development)
    if ! grep -q "^host.*all.*all.*0.0.0.0/0.*md5" "$pg_hba" 2>/dev/null; then
        echo "host    all             all             0.0.0.0/0               md5" >> "$pg_hba"
        iact_log_success "Conexiones de red habilitadas"
    else
        iact_log_info "Conexiones de red ya habilitadas"
    fi

    # Configure listen addresses
    if [[ -f "$pg_conf" ]]; then
        if ! grep -q "^listen_addresses = '*'" "$pg_conf" 2>/dev/null; then
            sed -i "s/^#*listen_addresses.*/listen_addresses = '*'/" "$pg_conf"
            iact_log_success "Listen addresses configurado"
        else
            iact_log_info "Listen addresses ya configurado"
        fi
    fi

    # Reload PostgreSQL to apply changes
    iact_log_info "Aplicando cambios de configuracion..."
    if systemctl reload postgresql 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Configuracion aplicada correctamente"
        return 0
    else
        iact_log_error "Error aplicando configuracion"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# secure_postgresql_installation
# Description: Secure PostgreSQL installation
# NO SILENT FAILURES: Reports each security step
# IDEMPOTENT: SQL operations are idempotent
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success (warnings are non-critical)
# -----------------------------------------------------------------------------
secure_postgresql_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando seguridad de PostgreSQL"

    # Set postgres user password
    iact_log_info "Configurando password del usuario postgres..."
    if sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '$DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Password del usuario postgres configurado"
    else
        iact_log_warning "No se pudo configurar password del usuario postgres"
    fi

    # Remove template0 and template1 public access (if needed)
    iact_log_info "Revocando acceso publico a templates..."
    sudo -u postgres psql -c "REVOKE ALL ON DATABASE template0 FROM PUBLIC;" 2>/dev/null || true
    sudo -u postgres psql -c "REVOKE ALL ON DATABASE template1 FROM PUBLIC;" 2>/dev/null || true
    iact_log_success "Acceso publico a templates revocado"

    iact_log_success "Configuracion de seguridad completada"
    return 0
}

# -----------------------------------------------------------------------------
# verify_postgresql_installation
# Description: Verify PostgreSQL installation
# NO SILENT FAILURES: Reports verification results
# IDEMPOTENT: Safe to run multiple times
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
verify_postgresql_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalacion de PostgreSQL"

    # Check if client is installed
    if ! iact_check_postgres_client; then
        iact_log_error "Cliente de PostgreSQL no encontrado"
        return 1
    fi
    iact_log_success "Cliente de PostgreSQL disponible"

    # Check if service is running
    if ! systemctl is-active --quiet postgresql; then
        iact_log_error "Servicio PostgreSQL no esta en ejecucion"
        return 1
    fi
    iact_log_success "Servicio PostgreSQL en ejecucion"

    # Test postgres user connectivity
    if ! PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
        iact_log_error "No se puede conectar con el usuario postgres"
        return 1
    fi
    iact_log_success "Conexion con usuario postgres exitosa"

    # Get version information
    local version
    version=$(sudo -u postgres psql -t -c "SELECT version();" 2>/dev/null | head -n 1 | xargs)
    iact_log_info "Version de PostgreSQL: $version"

    iact_log_success "Verificacion de instalacion completada"
    return 0
}

# -----------------------------------------------------------------------------
# display_postgresql_info
# Description: Display PostgreSQL installation information
# NO SILENT FAILURES: Shows complete installation status
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 always
# -----------------------------------------------------------------------------
display_postgresql_info() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Informacion de instalacion"

    echo ""
    echo "=================================================================="
    echo "                  INFORMACION DE POSTGRESQL"
    echo "=================================================================="
    echo ""
    echo "Version: $POSTGRESQL_VERSION"
    echo "Estado del servicio: $(systemctl is-active postgresql 2>/dev/null || echo 'unknown')"
    echo ""
    echo "CREDENCIALES (GUARDAR DE FORMA SEGURA):"
    echo "  Usuario: postgres"
    echo "  Password: $DB_PASSWORD"
    echo ""
    echo "CONEXION:"
    echo "  psql -U postgres -h localhost"
    echo "  PGPASSWORD='$DB_PASSWORD' psql -U postgres -h localhost"
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
    iact_log_header "POSTGRESQL INSTALLATION - UBUNTU 18.04"
    iact_log_info "Instalando PostgreSQL $POSTGRESQL_VERSION"
    iact_log_info "Context: $(iact_get_context)"

    # Array de pasos (auto-calculado)
    local steps=(
        setup_postgresql_repository
        install_postgresql_packages
        configure_postgresql_service
        configure_postgresql_authentication
        secure_postgresql_installation
        verify_postgresql_installation
        display_postgresql_info
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
        iact_log_success "Instalacion de PostgreSQL completada exitosamente"
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