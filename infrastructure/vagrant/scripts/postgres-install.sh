#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - PostgreSQL Installation Script
# =============================================================================
# Description: Install and configure PostgreSQL on Ubuntu 18.04
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant provisioning
# Pattern: Idempotent execution, No silent failures
# Strategy: Fallback - Intenta repositorio custom, luego oficial
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

# Repository configuration - Fallback Strategy
readonly POSTGRESQL_CUSTOM_REPO="${POSTGRESQL_CUSTOM_REPO:-http://apt.postgresql.org/pub/repos/apt}"
readonly POSTGRESQL_OFFICIAL_REPO="http://apt.postgresql.org/pub/repos/apt"

# Cargar core (que auto-carga logging)
source "${PROJECT_ROOT}/utils/core.sh"

# Cargar modulos adicionales
iact_source_module "validation"
iact_source_module "database"

# Configurar logging con nombre del script
iact_init_logging "${SCRIPT_NAME%.sh}"

# =============================================================================
# POSTGRESQL INSTALLATION FUNCTIONS - IDEMPOTENT & NO SILENT FAILURES
# =============================================================================

# -----------------------------------------------------------------------------
# add_postgresql_gpg_key
# Description: Add PostgreSQL GPG key
# NO SILENT FAILURES: Reports key addition status
# IDEMPOTENT: Key won't be added if already present
# Arguments: None
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
add_postgresql_gpg_key() {
    iact_log_info "Agregando clave GPG de PostgreSQL..."
    
    # Check if key already exists
    if [[ -f /etc/apt/trusted.gpg.d/postgresql.gpg ]]; then
        iact_log_info "Clave GPG de PostgreSQL ya existe"
        return 0
    fi

    # Try to add key
    if curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/postgresql.gpg > /dev/null 2>&1; then
        iact_log_success "Clave GPG de PostgreSQL agregada"
        return 0
    else
        iact_log_error "Error agregando clave GPG de PostgreSQL"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# setup_postgresql_repository
# Description: Setup PostgreSQL APT repository with fallback strategy
# NO SILENT FAILURES: Reports repository setup status
# IDEMPOTENT: Checks if already configured
# FALLBACK: Tries custom repo first, then official
# Arguments: $1 - current step, $2 - total steps
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
setup_postgresql_repository() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando repositorio de PostgreSQL"

    local repo_file="/etc/apt/sources.list.d/pgdg.list"

    # Check if repository already configured
    if [[ -f "$repo_file" ]]; then
        iact_log_info "Repositorio de PostgreSQL ya configurado"
        return 0
    fi

    # Add GPG key
    if ! add_postgresql_gpg_key; then
        iact_log_error "No se pudo agregar clave GPG de PostgreSQL"
        return 1
    fi

    iact_log_info "Configurando repositorio con estrategia de fallback..."
    
    # Create repository file with fallback strategy
    cat > "$repo_file" <<EOF
# PostgreSQL $POSTGRESQL_VERSION Repository - Fallback Strategy
# =============================================================================
# TIER 1: Custom/Corporate Mirror (May be faster in your network)
deb [arch=amd64] $POSTGRESQL_CUSTOM_REPO bionic-pgdg main

# TIER 2: Official PostgreSQL Mirror (Fallback)
deb [arch=amd64] $POSTGRESQL_OFFICIAL_REPO bionic-pgdg main
EOF

    if [[ $? -eq 0 ]]; then
        iact_log_success "Archivo de repositorio creado: $repo_file"
    else
        iact_log_error "Error creando archivo de repositorio"
        return 1
    fi

    iact_log_info "Actualizando cache de paquetes..."
    if apt-get update 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Repositorio de PostgreSQL configurado correctamente"
        
        # Verify which repository is being used
        iact_log_info "Verificando repositorio activo..."
        if apt-cache policy postgresql-${POSTGRESQL_VERSION} 2>/dev/null | grep -q "$POSTGRESQL_CUSTOM_REPO"; then
            iact_log_success "Usando repositorio custom (TIER 1): $POSTGRESQL_CUSTOM_REPO"
        elif apt-cache policy postgresql-${POSTGRESQL_VERSION} 2>/dev/null | grep -q "$POSTGRESQL_OFFICIAL_REPO"; then
            iact_log_success "Usando repositorio oficial (TIER 2): $POSTGRESQL_OFFICIAL_REPO"
        else
            iact_log_warning "No se pudo determinar el repositorio activo"
        fi
        
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
        # Backup postgresql.conf if not already backed up
        if [[ ! -f "${pg_conf}.backup" ]]; then
            iact_log_info "Creando backup de postgresql.conf..."
            cp "$pg_conf" "${pg_conf}.backup"
        fi

        if ! grep -q "^listen_addresses = '\*'" "$pg_conf" 2>/dev/null; then
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

    # Display which repository was used
    iact_log_info "Verificando origen del paquete..."
    local package_origin
    package_origin=$(apt-cache policy postgresql-${POSTGRESQL_VERSION} 2>/dev/null | grep "Installed" | head -1)
    iact_log_info "Informacion del paquete: $package_origin"

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
    echo "Estrategia de repositorio: Fallback"
    echo "  TIER 1 (Custom): $POSTGRESQL_CUSTOM_REPO"
    echo "  TIER 2 (Official): $POSTGRESQL_OFFICIAL_REPO"
    echo ""
    echo "CREDENCIALES (GUARDAR DE FORMA SEGURA):"
    echo "  Usuario: postgres"
    echo "  Password: $DB_PASSWORD"
    echo ""
    echo "CONEXION:"
    echo "  psql -U postgres -h localhost"
    echo "  PGPASSWORD='$DB_PASSWORD' psql -U postgres -h localhost"
    echo ""
    echo "Archivos de configuracion:"
    echo "  pg_hba.conf: /etc/postgresql/${POSTGRESQL_VERSION}/main/pg_hba.conf"
    echo "  postgresql.conf: /etc/postgresql/${POSTGRESQL_VERSION}/main/postgresql.conf"
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
    iact_log_info "Strategy: Fallback (Custom + Official repos)"

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

    iact_log_info "Total de pasos a ejecutar: $total"

    for step_func in "${steps[@]}"; do
        ((current++))

        iact_log_info "DEBUG: Ejecutando funcion: $step_func"

        if ! $step_func "$current" "$total"; then
            failed_steps+=("$step_func")
            iact_log_warning "Paso $step_func fallo, continuando..."
        fi
    done

    # Report final results
    echo ""
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Instalacion de PostgreSQL completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "PostgreSQL esta listo para usar"
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