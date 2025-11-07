#!/bin/bash
set -euo pipefail

# ============================================================================
# INSTALACIÓN Y CONFIGURACIÓN DE POSTGRESQL (IDEMPOTENTE)
# ============================================================================
# Este script instala PostgreSQL solo si no está presente, aplica configuración
# segura si es necesario, y crea usuario/base de datos si no existen.
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/../utils"
CONFIG_DIR="${SCRIPT_DIR}/../config/postgresql"

source "${UTILS_DIR}/logging.sh"
source "${UTILS_DIR}/validation.sh"
source "${UTILS_DIR}/common.sh"

log_header "Instalación y configuración de PostgreSQL"

# Paso 1: Verificar si PostgreSQL está instalado
if ! command -v psql &>/dev/null; then
    log_info "PostgreSQL no está instalado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y postgresql
    log_success "PostgreSQL instalado correctamente"
else
    log_info "PostgreSQL ya está instalado"
fi

# Paso 2: Aplicar configuración segura si es diferente
CONF_SRC="${CONFIG_DIR}/postgresql.conf"
CONF_DST="/etc/postgresql/16/main/postgresql.conf"
HBA_SRC="${CONFIG_DIR}/pg_hba.conf"
HBA_DST="/etc/postgresql/16/main/pg_hba.conf"

RESTART=0

if [ -f "$CONF_DST" ] && ! cmp -s "$CONF_SRC" "$CONF_DST"; then
    log_info "Respaldando postgresql.conf..."
    sudo cp "$CONF_DST" "$CONF_DST.bak.$(date +%Y%m%d_%H%M%S)"
    sudo cp "$CONF_SRC" "$CONF_DST"
    RESTART=1
fi

if [ -f "$HBA_DST" ] && ! cmp -s "$HBA_SRC" "$HBA_DST"; then
    log_info "Respaldando pg_hba.conf..."
    sudo cp "$HBA_DST" "$HBA_DST.bak.$(date +%Y%m%d_%H%M%S)"
    sudo cp "$HBA_SRC" "$HBA_DST"
    RESTART=1
fi

if [ "$RESTART" -eq 1 ]; then
    sudo systemctl restart postgresql
    log_success "Configuración aplicada y servicio reiniciado"
else
    log_info "La configuración ya está actualizada"
fi

# Paso 3: Crear usuario y base de datos si no existen
DB_NAME="iact_analytics"
DB_USER="django_user"
DB_PASS="django_pass"

USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'")
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" != "1" ]; then
    log_info "Creando base de datos $DB_NAME..."
    sudo -u postgres createdb "$DB_NAME"
    log_success "Base de datos creada"
else
    log_info "La base de datos $DB_NAME ya existe"
fi

if [ "$USER_EXISTS" != "1" ]; then
    log_info "Creando usuario $DB_USER..."
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    log_success "Usuario creado y permisos asignados"
else
    log_info "El usuario $DB_USER ya existe"
fi
