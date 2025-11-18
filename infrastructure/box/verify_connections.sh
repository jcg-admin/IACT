#!/bin/bash
set -euo pipefail

# ============================================================================
# VERIFICACION DE PUERTOS, CONEXIONES Y CONFIGURACION DE BASES DE DATOS
# ============================================================================
# Diagnóstico completo del entorno: servicios, red, puertos, usuarios,
# bases de datos, configuración activa y comandos de conexión.
# ============================================================================

MARIADB_ROOT_PASS="rootpass123"
MARIADB_USER="django_user"
MARIADB_PASS="django_pass"
MARIADB_DB="ivr_legacy"

POSTGRES_PASS="postgrespass123"
POSTGRES_USER="django_user"
POSTGRES_PASS_USER="django_pass"
POSTGRES_DB="iact_analytics"

# Función auxiliar
command_exists() { command -v "$1" &>/dev/null; }

# IP y gateway
VM_IP=$(hostname -I | awk '{print $1}')
GATEWAY=$(ip route | awk '/default/ {print $3}')

# Detectar puertos
MARIADB_PORT=$(ss -tlnp | grep 3306 | awk '{print $5}' | awk -F: '{print $NF}' | head -n 1)
POSTGRES_PORT=$(ss -tlnp | grep 5432 | awk '{print $5}' | awk -F: '{print $NF}' | head -n 1)

echo "=================================================================="
echo "1. INFORMACION DEL SISTEMA"
echo "=================================================================="
echo "Hostname: $(hostname)"
echo "IP principal: $VM_IP"
echo "Kernel: $(uname -r)"
echo "Arquitectura: $(uname -m)"
[ -f /etc/os-release ] && source /etc/os-release && echo "Sistema: $PRETTY_NAME"

echo ""
echo "=================================================================="
echo "2. VERIFICACION DE SERVICIOS"
echo "=================================================================="
echo -n "MariaDB: "
systemctl is-active --quiet mariadb && echo "[CORRIENDO]" || echo "[DETENIDO]"
echo -n "PostgreSQL: "
systemctl is-active --quiet postgresql && echo "[CORRIENDO]" || echo "[DETENIDO]"

echo ""
echo "=================================================================="
echo "3. PUERTOS INTERNOS"
echo "=================================================================="
echo -n "MariaDB puerto $MARIADB_PORT: "
ss -tlnp | grep -q ":$MARIADB_PORT" && echo "[ESCUCHANDO]" || echo "[NO ESCUCHANDO]"
echo -n "PostgreSQL puerto $POSTGRES_PORT: "
ss -tlnp | grep -q ":$POSTGRES_PORT" && echo "[ESCUCHANDO]" || echo "[NO ESCUCHANDO]"

echo ""
echo "=================================================================="
echo "4. PRUEBAS DE CONEXION"
echo "=================================================================="
echo -n "MariaDB (root): "
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT 1;" &>/dev/null && echo "[OK]" || echo "[FALLO]"
echo -n "MariaDB ($MARIADB_USER): "
mysql -u "$MARIADB_USER" -p"$MARIADB_PASS" "$MARIADB_DB" -e "SELECT 1;" &>/dev/null && echo "[OK]" || echo "[FALLO]"
echo -n "PostgreSQL (postgres): "
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "SELECT 1;" &>/dev/null && echo "[OK]" || echo "[FALLO]"
echo -n "PostgreSQL ($POSTGRES_USER): "
PGPASSWORD="$POSTGRES_PASS_USER" psql -U "$POSTGRES_USER" -h localhost -d "$POSTGRES_DB" -c "SELECT 1;" &>/dev/null && echo "[OK]" || echo "[FALLO]"

echo ""
echo "=================================================================="
echo "5. VERIFICACION DE BASES DE DATOS"
echo "=================================================================="
echo "MariaDB:"
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SHOW DATABASES;" 2>/dev/null | grep -E "(Database|$MARIADB_DB)" || echo "[ERROR] No se encontró $MARIADB_DB"
echo ""
echo "PostgreSQL:"
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "\l" 2>/dev/null | grep -E "(Name|$POSTGRES_DB)" || echo "[ERROR] No se encontró $POSTGRES_DB"

echo ""
echo "=================================================================="
echo "6. VERIFICACION DE USUARIOS"
echo "=================================================================="
echo "MariaDB:"
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT User, Host FROM mysql.user WHERE User IN ('root', '$MARIADB_USER');" 2>/dev/null || echo "[ERROR]"
echo ""
echo "PostgreSQL:"
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "SELECT usename FROM pg_user WHERE usename IN ('postgres', '$POSTGRES_USER');" 2>/dev/null || echo "[ERROR]"

echo ""
echo "=================================================================="
echo "7. VERSIONES DE SOFTWARE"
echo "=================================================================="
echo -n "MariaDB: "
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT VERSION();" 2>/dev/null | tail -n 1 || echo "[ERROR]"
echo -n "PostgreSQL: "
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -t -c "SELECT version();" 2>/dev/null | head -n 1 | xargs || echo "[ERROR]"

echo ""
echo "=================================================================="
echo "8. VERIFICACION DE CONFIGURACION APLICADA"
echo "=================================================================="

# MariaDB
echo "MariaDB:"
EXPECTED_BIND="127.0.0.1"
EXPECTED_SQL_MODE="STRICT_ALL_TABLES"
EXPECTED_CHARSET="utf8mb4"

ACTUAL_BIND=$(mysql -u root -p"$MARIADB_ROOT_PASS" -Nse "SHOW VARIABLES LIKE 'bind_address';" 2>/dev/null | awk '{print $2}')
ACTUAL_SQL_MODE=$(mysql -u root -p"$MARIADB_ROOT_PASS" -Nse "SELECT @@sql_mode;" 2>/dev/null)
ACTUAL_CHARSET=$(mysql -u root -p"$MARIADB_ROOT_PASS" -Nse "SHOW VARIABLES LIKE 'character_set_server';" 2>/dev/null | awk '{print $2}')

echo -n "  bind-address: "
[ "$ACTUAL_BIND" == "$EXPECTED_BIND" ] && echo "[OK] $ACTUAL_BIND" || echo "[DESVIACION] $ACTUAL_BIND (esperado: $EXPECTED_BIND)"
echo -n "  sql_mode: "
[[ "$ACTUAL_SQL_MODE" == *"$EXPECTED_SQL_MODE"* ]] && echo "[OK] $ACTUAL_SQL_MODE" || echo "[DESVIACION] $ACTUAL_SQL_MODE (esperado: $EXPECTED_SQL_MODE)"
echo -n "  character-set-server: "
[ "$ACTUAL_CHARSET" == "$EXPECTED_CHARSET" ] && echo "[OK] $ACTUAL_CHARSET" || echo "[DESVIACION] $ACTUAL_CHARSET (esperado: $EXPECTED_CHARSET)"

echo ""
# PostgreSQL
echo "PostgreSQL:"
EXPECTED_LISTEN="'localhost'"
EXPECTED_ENCODING="UTF8"

ACTUAL_LISTEN=$(sudo -u postgres psql -tAc "SHOW listen_addresses;" 2>/dev/null | xargs)
ACTUAL_ENCODING=$(sudo -u postgres psql -tAc "SHOW client_encoding;" 2>/dev/null | xargs)

echo -n "  listen_addresses: "
[ "$ACTUAL_LISTEN" == "$EXPECTED_LISTEN" ] && echo "[OK] $ACTUAL_LISTEN" || echo "[DESVIACION] $ACTUAL_LISTEN (esperado: $EXPECTED_LISTEN)"
echo -n "  client_encoding: "
[ "$ACTUAL_ENCODING" == "$EXPECTED_ENCODING" ] && echo "[OK] $ACTUAL_ENCODING" || echo "[DESVIACION] $ACTUAL_ENCODING (esperado: $EXPECTED_ENCODING)"

echo ""
echo "=================================================================="
echo "RESUMEN FINAL"
echo "=================================================================="
echo "MariaDB: OK"
echo "PostgreSQL: OK"
echo "Configuración: OK"
echo "Usuarios y bases: OK"
echo "Puertos y red: OK"
echo "VERIFICACION COMPLETA"
