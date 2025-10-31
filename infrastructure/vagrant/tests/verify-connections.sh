#!/bin/bash
# Verificacion de puertos, conexiones y diagnostico de red
# Sin emojis - Sin dependencias externas

echo "=================================================================="
echo "  VERIFICACION DE PUERTOS Y CONEXIONES"
echo "=================================================================="
echo ""

# Credenciales
MARIADB_ROOT_PASS="rootpass123"
MARIADB_USER="django_user"
MARIADB_PASS="django_pass"
MARIADB_DB="ivr_legacy"

POSTGRES_PASS="postgrespass123"
POSTGRES_USER="django_user"
POSTGRES_PASS_USER="django_pass"
POSTGRES_DB="iact_analytics"

# Funcion para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "=================================================================="
echo "1. INFORMACION DEL SISTEMA"
echo "=================================================================="
echo ""

echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "Arquitectura: $(uname -m)"

if [ -f /etc/os-release ]; then
    source /etc/os-release
    echo "Sistema: $PRETTY_NAME"
fi

echo ""
echo "=================================================================="
echo "2. INTERFACES DE RED"
echo "=================================================================="
echo ""

# Usar ip o ifconfig segun disponibilidad
if command_exists ip; then
    echo "Interfaces de red (ip addr):"
    ip addr show | grep -E "^[0-9]+:|inet " | sed 's/^/  /'
elif command_exists ifconfig; then
    echo "Interfaces de red (ifconfig):"
    ifconfig | grep -E "^[a-z]|inet " | sed 's/^/  /'
else
    echo "[WARNING] Comandos ip/ifconfig no disponibles"
fi

echo ""
echo "=================================================================="
echo "3. VERIFICACION DE SERVICIOS"
echo "=================================================================="
echo ""

# Verificar MariaDB
echo -n "MariaDB: "
if systemctl is-active --quiet mariadb 2>/dev/null; then
    echo "[CORRIENDO]"
elif service mariadb status >/dev/null 2>&1; then
    echo "[CORRIENDO]"
else
    echo "[DETENIDO]"
fi

# Verificar PostgreSQL
echo -n "PostgreSQL: "
if systemctl is-active --quiet postgresql 2>/dev/null; then
    echo "[CORRIENDO]"
elif service postgresql status >/dev/null 2>&1; then
    echo "[CORRIENDO]"
else
    echo "[DETENIDO]"
fi

echo ""
echo "=================================================================="
echo "4. PUERTOS INTERNOS (DENTRO DE VM)"
echo "=================================================================="
echo ""

# Verificar puerto MariaDB (3306)
echo -n "MariaDB puerto 3306: "
if command_exists ss; then
    if ss -tlnp 2>/dev/null | grep -q ':3306'; then
        echo "[ESCUCHANDO]"
        ss -tlnp 2>/dev/null | grep ':3306' | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
elif command_exists netstat; then
    if netstat -tlnp 2>/dev/null | grep -q ':3306'; then
        echo "[ESCUCHANDO]"
        netstat -tlnp 2>/dev/null | grep ':3306' | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
else
    echo "[WARNING] Comandos ss/netstat no disponibles"
fi

echo ""

# Verificar puerto PostgreSQL (5432)
echo -n "PostgreSQL puerto 5432: "
if command_exists ss; then
    if ss -tlnp 2>/dev/null | grep -q ':5432'; then
        echo "[ESCUCHANDO]"
        ss -tlnp 2>/dev/null | grep ':5432' | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
elif command_exists netstat; then
    if netstat -tlnp 2>/dev/null | grep -q ':5432'; then
        echo "[ESCUCHANDO]"
        netstat -tlnp 2>/dev/null | grep ':5432' | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
else
    echo "[WARNING] Comandos ss/netstat no disponibles"
fi

echo ""
echo "=================================================================="
echo "5. CONECTIVIDAD BASICA"
echo "=================================================================="
echo ""

# Ping a localhost
echo -n "Loopback (127.0.0.1): "
if ping -c 1 -W 2 127.0.0.1 >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO]"
fi

# Ping a gateway si existe
echo -n "Gateway por defecto: "
if command_exists ip; then
    GATEWAY=$(ip route | grep default | awk '{print $3}' | head -n 1)
    if [ -n "$GATEWAY" ]; then
        echo -n "$GATEWAY "
        if ping -c 1 -W 2 "$GATEWAY" >/dev/null 2>&1; then
            echo "[OK]"
        else
            echo "[FALLO]"
        fi
    else
        echo "[NO ENCONTRADO]"
    fi
else
    echo "[SKIP] comando ip no disponible"
fi

# Conectividad externa
echo -n "Internet (8.8.8.8): "
if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO]"
fi

echo ""
echo "=================================================================="
echo "6. CONFIGURACION DNS"
echo "=================================================================="
echo ""

if [ -f /etc/resolv.conf ]; then
    echo "Servidores DNS configurados:"
    grep nameserver /etc/resolv.conf | sed 's/^/  /'
else
    echo "[WARNING] /etc/resolv.conf no encontrado"
fi

# Verificar resolucion DNS
echo ""
echo -n "Resolucion DNS (google.com): "
if command_exists getent; then
    if getent hosts google.com >/dev/null 2>&1; then
        echo "[OK]"
    else
        echo "[FALLO]"
    fi
elif command_exists host; then
    if host google.com >/dev/null 2>&1; then
        echo "[OK]"
    else
        echo "[FALLO]"
    fi
else
    echo "[SKIP] comandos getent/host no disponibles"
fi

echo ""
echo "=================================================================="
echo "7. CONEXIONES ACTIVAS"
echo "=================================================================="
echo ""

if command_exists ss; then
    echo "Conexiones establecidas (ss):"
    ss -tnp 2>/dev/null | grep ESTAB | head -n 10 | sed 's/^/  /' || echo "  Ninguna"
elif command_exists netstat; then
    echo "Conexiones establecidas (netstat):"
    netstat -tnp 2>/dev/null | grep ESTABLISHED | head -n 10 | sed 's/^/  /' || echo "  Ninguna"
else
    echo "[WARNING] Comandos ss/netstat no disponibles"
fi

echo ""
echo "=================================================================="
echo "8. PRUEBAS DE CONEXION A BASES DE DATOS"
echo "=================================================================="
echo ""

# Test MariaDB root
echo -n "MariaDB (root): "
if mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO]"
fi

# Test MariaDB usuario aplicacion
echo -n "MariaDB (django_user): "
if mysql -u "$MARIADB_USER" -p"$MARIADB_PASS" "$MARIADB_DB" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO]"
fi

# Test PostgreSQL postgres
echo -n "PostgreSQL (postgres): "
if PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO]"
fi

# Test PostgreSQL usuario aplicacion
echo -n "PostgreSQL (django_user): "
if PGPASSWORD="$POSTGRES_PASS_USER" psql -U "$POSTGRES_USER" -h localhost -d "$POSTGRES_DB" -c "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO]"
fi

echo ""
echo "=================================================================="
echo "9. VERIFICACION DE BASES DE DATOS"
echo "=================================================================="
echo ""

echo "Bases de datos MariaDB:"
echo "-----------------------"
if mysql -u root -p"$MARIADB_ROOT_PASS" -e "SHOW DATABASES;" 2>/dev/null | grep -E "(Database|$MARIADB_DB)"; then
    :
else
    echo "[ERROR] No se pudo conectar a MariaDB"
fi

echo ""
echo "Bases de datos PostgreSQL:"
echo "--------------------------"
if PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "\l" 2>/dev/null | grep -E "(Name|$POSTGRES_DB)"; then
    :
else
    echo "[ERROR] No se pudo conectar a PostgreSQL"
fi

echo ""
echo "=================================================================="
echo "10. USUARIOS DE BASES DE DATOS"
echo "=================================================================="
echo ""

echo "Usuarios MariaDB:"
echo "-----------------"
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT User, Host FROM mysql.user WHERE User IN ('root', '$MARIADB_USER');" 2>/dev/null || echo "[ERROR] No se pudo consultar usuarios"

echo ""
echo "Usuarios PostgreSQL:"
echo "--------------------"
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "SELECT usename FROM pg_user WHERE usename IN ('postgres', '$POSTGRES_USER');" 2>/dev/null || echo "[ERROR] No se pudo consultar usuarios"

echo ""
echo "=================================================================="
echo "11. VERSIONES DE SOFTWARE"
echo "=================================================================="
echo ""

# Version MariaDB
echo -n "MariaDB: "
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT VERSION();" 2>/dev/null | tail -n 1 || echo "[ERROR]"

# Version PostgreSQL
echo -n "PostgreSQL: "
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -t -c "SELECT version();" 2>/dev/null | head -n 1 | xargs || echo "[ERROR]"

echo ""
echo "=================================================================="
echo "12. RUTAS DE RED"
echo "=================================================================="
echo ""

if command_exists ip; then
    echo "Tabla de rutas (ip route):"
    ip route | sed 's/^/  /'
elif command_exists route; then
    echo "Tabla de rutas (route):"
    route -n | sed 's/^/  /'
else
    echo "[WARNING] Comandos ip/route no disponibles"
fi

echo ""
echo "=================================================================="
echo "13. PORT FORWARDING INFO"
echo "=================================================================="
echo ""

echo "Configuracion de Vagrant (en tu Vagrantfile):"
echo ""
echo "  Host (Windows)  ->  Guest (VM)"
echo "  --------------     -----------"
echo "  Puerto 13306    ->  3306 (MariaDB)"
echo "  Puerto 15432    ->  5432 (PostgreSQL)"
echo ""

echo "=================================================================="
echo "14. COMANDOS DE CONEXION"
echo "=================================================================="
echo ""

echo "Desde DENTRO de la VM (vagrant ssh):"
echo "-------------------------------------"
echo "  MariaDB:    mysql -u root -p'$MARIADB_ROOT_PASS'"
echo "  PostgreSQL: PGPASSWORD='$POSTGRES_PASS' psql -U postgres -h localhost"
echo ""
echo "Desde tu HOST (Windows/Mac/Linux):"
echo "-----------------------------------"
echo "  MariaDB:    mysql -h 127.0.0.1 -P 13306 -u $MARIADB_USER -p'$MARIADB_PASS' $MARIADB_DB"
echo "  PostgreSQL: PGPASSWORD='$POSTGRES_PASS_USER' psql -h 127.0.0.1 -p 15432 -U $POSTGRES_USER -d $POSTGRES_DB"
echo ""
echo "Con Clientes Graficos (DBeaver/HeidiSQL/pgAdmin):"
echo "--------------------------------------------------"
echo "  MariaDB:"
echo "    Host: 127.0.0.1"
echo "    Puerto: 13306"
echo "    Usuario: $MARIADB_USER"
echo "    Password: $MARIADB_PASS"
echo "    Database: $MARIADB_DB"
echo ""
echo "  PostgreSQL:"
echo "    Host: 127.0.0.1"
echo "    Puerto: 15432"
echo "    Usuario: $POSTGRES_USER"
echo "    Password: $POSTGRES_PASS_USER"
echo "    Database: $POSTGRES_DB"
echo ""
echo "=================================================================="
echo "  VERIFICACION COMPLETA"
echo "=================================================================="
echo ""