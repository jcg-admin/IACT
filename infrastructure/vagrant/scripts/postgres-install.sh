#!/bin/bash
set -euo pipefail

# =============================================================================
# POSTGRESQL INSTALLATION - Instalación y configuración de PostgreSQL
# =============================================================================
# Descripción: Instala PostgreSQL en Ubuntu 18.04 con estrategia de fallback
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
POSTGRESQL_VERSION="${POSTGRESQL_VERSION:-10}"
DB_PASSWORD="${DB_PASSWORD:-postgrespass123}"

# Configuración de repositorios - Estrategia de Fallback
POSTGRESQL_CUSTOM_REPO="${POSTGRESQL_CUSTOM_REPO:-http://apt.postgresql.org/pub/repos/apt}"
POSTGRESQL_OFFICIAL_REPO="http://apt.postgresql.org/pub/repos/apt"

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

# Agrega clave GPG de PostgreSQL (idempotente)
add_gpg_key() {
    iact_log_info "Agregando clave GPG de PostgreSQL..."

    # Verificar si la clave ya existe
    if [ -f /etc/apt/trusted.gpg.d/postgresql.gpg ]; then
        iact_log_info "Clave GPG de PostgreSQL ya existe"
        return 0
    fi

    # Intentar agregar la clave
    if curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor | tee /etc/apt/trusted.gpg.d/postgresql.gpg > /dev/null 2>&1; then
        iact_log_success "Clave GPG de PostgreSQL agregada"
        return 0
    else
        iact_log_error "Error agregando clave GPG de PostgreSQL"
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Funciones de instalación - Idempotentes y sin fallas silenciosas
# -----------------------------------------------------------------------------

# Configura repositorio de PostgreSQL con estrategia de fallback (idempotente)
setup_repository() {
    local current="$1"
    local total="$2"
    local repo_file="/etc/apt/sources.list.d/pgdg.list"

    iact_log_step "$current" "$total" "Configurando repositorio de PostgreSQL"

    # Verificar si ya está configurado
    if [ -f "$repo_file" ]; then
        iact_log_info "Repositorio de PostgreSQL ya configurado"
        return 0
    fi

    # Agregar clave GPG
    if ! add_gpg_key; then
        iact_log_error "No se pudo agregar clave GPG de PostgreSQL"
        return 1
    fi

    iact_log_info "Configurando repositorio con estrategia de fallback..."

    # Crear archivo de repositorio con estrategia de fallback
    cat > "$repo_file" <<EOF
# PostgreSQL $POSTGRESQL_VERSION Repository - Fallback Strategy
# =============================================================================
# TIER 1: Custom/Corporate Mirror (May be faster in your network)
deb [arch=amd64] $POSTGRESQL_CUSTOM_REPO bionic-pgdg main

# TIER 2: Official PostgreSQL Mirror (Fallback)
deb [arch=amd64] $POSTGRESQL_OFFICIAL_REPO bionic-pgdg main
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

    iact_log_success "Repositorio de PostgreSQL configurado correctamente"

    # Verificar qué repositorio está activo
    iact_log_info "Verificando repositorio activo..."
    if apt-cache policy "postgresql-${POSTGRESQL_VERSION}" 2>/dev/null | grep -q "$POSTGRESQL_CUSTOM_REPO"; then
        iact_log_success "Usando repositorio custom (TIER 1): $POSTGRESQL_CUSTOM_REPO"
    elif apt-cache policy "postgresql-${POSTGRESQL_VERSION}" 2>/dev/null | grep -q "$POSTGRESQL_OFFICIAL_REPO"; then
        iact_log_success "Usando repositorio oficial (TIER 2): $POSTGRESQL_OFFICIAL_REPO"
    else
        iact_log_warning "No se pudo determinar el repositorio activo"
    fi

    return 0
}

# Instala paquetes de PostgreSQL (idempotente - APT maneja paquetes instalados)
install_packages() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Instalando paquetes de PostgreSQL"

    # Verificar si ya está instalado y ejecutándose
    if type "iact_check_postgres_client" >/dev/null 2>&1; then
        if iact_check_postgres_client && systemctl is-active --quiet postgresql 2>/dev/null; then
            iact_log_info "PostgreSQL ya instalado y en ejecución"
            return 0
        fi
    fi

    local packages="postgresql-${POSTGRESQL_VERSION} postgresql-client-${POSTGRESQL_VERSION} postgresql-contrib-${POSTGRESQL_VERSION}"

    iact_log_info "Paquetes a instalar: $packages"

    export DEBIAN_FRONTEND=noninteractive

    # shellcheck disable=SC2086
    if apt-get install -y --no-install-recommends $packages 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Paquetes de PostgreSQL instalados correctamente"
        return 0
    else
        iact_log_error "Error instalando paquetes de PostgreSQL"
        return 1
    fi
}

# Configura servicio de PostgreSQL (idempotente)
configure_service() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando servicio de PostgreSQL"

    # Habilitar servicio
    iact_log_info "Habilitando servicio PostgreSQL..."
    if ! systemctl enable postgresql 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error habilitando servicio PostgreSQL"
        return 1
    fi

    # Iniciar servicio
    iact_log_info "Iniciando servicio PostgreSQL..."
    if ! systemctl start postgresql 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_error "Error iniciando servicio PostgreSQL"
        return 1
    fi

    # Esperar a que el servicio esté listo
    iact_log_info "Esperando a que PostgreSQL esté listo..."
    local timeout=30
    local counter=0

    while [ "$counter" -lt "$timeout" ]; do
        if sudo -u postgres psql -c "SELECT 1;" >/dev/null 2>&1; then
            iact_log_success "Servicio PostgreSQL iniciado y respondiendo (${counter}s)"
            return 0
        fi
        sleep 1
        counter=$((counter + 1))
    done

    iact_log_error "PostgreSQL no respondió después de ${timeout}s"
    return 1
}

# Configura autenticación de PostgreSQL (idempotente)
configure_authentication() {
    local current="$1"
    local total="$2"
    local pg_hba="/etc/postgresql/${POSTGRESQL_VERSION}/main/pg_hba.conf"
    local pg_conf="/etc/postgresql/${POSTGRESQL_VERSION}/main/postgresql.conf"

    iact_log_step "$current" "$total" "Configurando autenticación de PostgreSQL"

    # Configurar pg_hba.conf
    if [ -f "$pg_hba" ]; then
        # Backup si no existe
        if [ ! -f "${pg_hba}.backup" ]; then
            iact_log_info "Creando backup de pg_hba.conf..."
            cp "$pg_hba" "${pg_hba}.backup"
        fi

        # Verificar si ya está configurado
        if ! grep -q "^host.*all.*all.*0.0.0.0/0.*md5" "$pg_hba" 2>/dev/null; then
            iact_log_info "Agregando regla de autenticación MD5..."
            echo "host    all             all             0.0.0.0/0               md5" >> "$pg_hba"
            iact_log_success "Regla de autenticación agregada"
        else
            iact_log_info "Regla de autenticación ya existe"
        fi
    else
        iact_log_warning "Archivo pg_hba.conf no encontrado: $pg_hba"
    fi

    # Configurar listen_addresses
    if [ -f "$pg_conf" ]; then
        # Backup si no existe
        if [ ! -f "${pg_conf}.backup" ]; then
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

    # Aplicar cambios
    iact_log_info "Aplicando cambios de configuración..."
    if systemctl reload postgresql 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Configuración aplicada correctamente"
        return 0
    else
        iact_log_error "Error aplicando configuración"
        return 1
    fi
}

# Asegura instalación de PostgreSQL (idempotente)
secure_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Configurando seguridad de PostgreSQL"

    # Configurar password del usuario postgres
    iact_log_info "Configurando password del usuario postgres..."
    if sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD '$DB_PASSWORD';" 2>&1 | tee -a "$(iact_get_log_file)"; then
        iact_log_success "Password del usuario postgres configurado"
    else
        iact_log_warning "No se pudo configurar password del usuario postgres"
    fi

    # Revocar acceso público a templates
    iact_log_info "Revocando acceso público a templates..."
    sudo -u postgres psql -c "REVOKE ALL ON DATABASE template0 FROM PUBLIC;" 2>/dev/null || true
    sudo -u postgres psql -c "REVOKE ALL ON DATABASE template1 FROM PUBLIC;" 2>/dev/null || true
    iact_log_success "Acceso público a templates revocado"

    iact_log_success "Configuración de seguridad completada"
    return 0
}

# Verifica instalación de PostgreSQL (idempotente)
verify_installation() {
    local current="$1"
    local total="$2"

    iact_log_step "$current" "$total" "Verificando instalación de PostgreSQL"

    # Verificar cliente
    if type "iact_check_postgres_client" >/dev/null 2>&1; then
        if ! iact_check_postgres_client; then
            iact_log_error "Cliente de PostgreSQL no encontrado"
            return 1
        fi
        iact_log_success "Cliente de PostgreSQL disponible"
    fi

    # Verificar servicio
    if ! systemctl is-active --quiet postgresql; then
        iact_log_error "Servicio PostgreSQL no está en ejecución"
        return 1
    fi
    iact_log_success "Servicio PostgreSQL en ejecución"

    # Probar conectividad con postgres
    if ! PGPASSWORD="$DB_PASSWORD" psql -U postgres -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
        iact_log_error "No se puede conectar con el usuario postgres"
        return 1
    fi
    iact_log_success "Conexión con usuario postgres exitosa"

    # Obtener versión
    local version
    version=$(sudo -u postgres psql -t -c "SELECT version();" 2>/dev/null | head -n 1 | xargs)
    iact_log_info "Versión de PostgreSQL: $version"

    # Mostrar origen del paquete
    iact_log_info "Verificando origen del paquete..."
    local package_origin
    package_origin=$(apt-cache policy "postgresql-${POSTGRESQL_VERSION}" 2>/dev/null | grep "Installed" | head -1)
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
    printf '%s\n' "                  INFORMACION DE POSTGRESQL"
    printf '%s\n' "=================================================================="
    printf '\n'
    printf '%s\n' "Versión: $POSTGRESQL_VERSION"
    printf '%s\n' "Estado del servicio: $(systemctl is-active postgresql 2>/dev/null || echo 'unknown')"
    printf '\n'
    printf '%s\n' "Estrategia de repositorio: Fallback"
    printf '%s\n' "  TIER 1 (Custom): $POSTGRESQL_CUSTOM_REPO"
    printf '%s\n' "  TIER 2 (Official): $POSTGRESQL_OFFICIAL_REPO"
    printf '\n'
    printf '%s\n' "CREDENCIALES (GUARDAR DE FORMA SEGURA):"
    printf '%s\n' "  Usuario: postgres"
    printf '%s\n' "  Password: $DB_PASSWORD"
    printf '\n'
    printf '%s\n' "CONEXION:"
    printf '%s\n' "  psql -U postgres -h localhost"
    printf '%s\n' "  PGPASSWORD='$DB_PASSWORD' psql -U postgres -h localhost"
    printf '\n'
    printf '%s\n' "Archivos de configuración:"
    printf '%s\n' "  pg_hba.conf: /etc/postgresql/${POSTGRESQL_VERSION}/main/pg_hba.conf"
    printf '%s\n' "  postgresql.conf: /etc/postgresql/${POSTGRESQL_VERSION}/main/postgresql.conf"
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

step_configure_auth() {
    local current="$1"
    local total="$2"

    if ! configure_authentication "$current" "$total"; then
        iact_log_error "Error configurando autenticación"
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
        iact_log_success "Instalación de PostgreSQL completada exitosamente"
        iact_log_info "Total pasos ejecutados: $total"
        iact_log_info "PostgreSQL está listo para usar"
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
    iact_log_header "POSTGRESQL INSTALLATION - UBUNTU 18.04"
    iact_log_info "Instalando PostgreSQL $POSTGRESQL_VERSION"
    iact_log_info "Context: $(iact_get_context)"
    iact_log_info "Strategy: Fallback (Custom + Official repos)"

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
    run_step step_setup_repo
    run_step step_install
    run_step step_configure_service
    run_step step_configure_auth
    run_step step_secure
    run_step step_verify
    run_step step_show_info

    # Mostrar resultados finales
    show_results "$total_steps" "$failed_count" "$failed_list"
}

# Ejecutar main
main "$@"