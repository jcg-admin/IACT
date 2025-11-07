#!/bin/bash
set -euo pipefail

# ============================================================================
# INSTALACIÓN Y CONFIGURACIÓN DE MARIADB (IDEMPOTENTE)
# ============================================================================
# Este script instala MariaDB solo si no está presente, aplica configuración
# segura si es necesario, y crea usuario/base de datos si no existen.
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UTILS_DIR="${SCRIPT_DIR}/../utils"
CONFIG_DIR="${SCRIPT_DIR}/../config/mariadb"

source "${UTILS_DIR}/logging.sh"
source "${UTILS_DIR}/validation.sh"
source "${UTILS_DIR}/common.sh"

log_header "Instalación y configuración de MariaDB"

# Paso 1: Verificar si MariaDB está instalado
if ! command -v mariadb &>/dev/null; then
    log_info "MariaDB no está instalado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y mariadb-server
    log_success "MariaDB instalado correctamente"
else
    log_info "MariaDB ya está instalado"
fi

# Paso 2: Aplicar configuración segura si es diferente
CONF_SRC="${CONFIG_DIR}/50-server.cnf"
CONF_DST="/etc/mysql/mariadb.conf.d/50-server.cnf"

if [ -f "$CONF_DST" ] && ! cmp -s "$CONF_SRC" "$CONF_DST"; then
    log_info "Configuración existente detectada. Respaldando..."
    sudo cp "$CONF_DST" "$CONF_DST.bak.$(date +%Y%m%d_%H%M%S)"
fi

if ! cmp -s "$CONF_SRC" "$CONF_DST"; then
    log_info "Aplicando configuración segura..."
    sudo cp "$CONF_SRC" "$CONF_DST"
    sudo systemctl restart mariadb
    log_success "Configuración aplicada y servicio reiniciado"
else
    log_info "La configuración ya está actualizada"
fi

# Paso 3: Crear usuario y base de datos si no existen
DB_NAME="ivr_legacy"
DB_USER="django_user"
DB_PASS="django_pass"

USER_EXISTS=$(sudo mariadb -Nse "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '$DB_USER' AND host = 'localhost');")
DB_EXISTS=$(sudo mariadb -Nse "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '$DB_NAME';")

if [ -z "$DB_EXISTS" ]; then
    log_info "Creando base de datos $DB_NAME..."
    sudo mariadb -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    log_success "Base de datos creada"
else
    log_info "La base de datos $DB_NAME ya existe"
fi

if [ "$USER_EXISTS" -eq 0 ]; then
    log_info "Creando usuario $DB_USER@localhost..."
    sudo mariadb -e "CREATE USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';"
    sudo mariadb -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
    sudo mariadb -e "FLUSH PRIVILEGES;"
    log_success "Usuario creado y permisos asignados"
else
    log_info "El usuario $DB_USER@localhost ya existe"
fi
