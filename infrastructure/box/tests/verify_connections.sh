#!/bin/bash
# Verificación de puertos, conexiones y diagnóstico de red
# Idempotente, sin fallas silenciosas, con detección dinámica de puertos

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

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar e instalar netstat si no está
if ! command_exists netstat; then
    echo "[INFO] netstat no encontrado. Instalando net-tools..."
    sudo apt update && sudo apt install -y net-tools
    if ! command_exists netstat; then
        echo "[ERROR] No se pudo instalar netstat (net-tools)."
    else
        echo "[OK] netstat instalado correctamente."
    fi
fi

# Detección dinámica de IP y gateway
VM_IP=$(hostname -I | awk '{print $1}')
GATEWAY=$(ip route | awk '/default/ {print $3}')

# Detección robusta de puertos
if command_exists netstat; then
    MARIADB_PORT=$(netstat -tlnp 2>/dev/null | grep 3306 | awk '{print $4}' | awk -F: '{print $NF}' | head -n 1)
    POSTGRES_PORT=$(netstat -tlnp 2>/dev/null | grep 5432 | awk '{print $4}' | awk -F: '{print $NF}' | head -n 1)
elif command_exists ss; then
    MARIADB_PORT=$(ss -tlnp | grep 3306 | grep -oE '[0-9]+(?=/)' | head -n 1)
    POSTGRES_PORT=$(ss -tlnp | grep 5432 | grep -oE '[0-9]+(?=/)' | head -n 1)
else
    MARIADB_PORT="?"
    POSTGRES_PORT="?"
fi

echo "=================================================================="
echo "1. INFORMACION DEL SISTEMA"
echo "=================================================================="
echo ""

echo "Hostname: $(hostname)"
echo "IP principal: $VM_IP"
echo "Kernel: $(uname -r)"
echo "Arquitectura: $(uname -m)"
[ -f /etc/os-release ] && source /etc/os-release && echo "Sistema: $PRETTY_NAME"

echo ""
echo "=================================================================="
echo "2. INTERFACES DE RED"
echo "=================================================================="
echo ""

if command_exists ip; then
    echo "Interfaces de red (ip addr):"
    ip addr show | grep -E "^[0-9]+:|inet " | sed 's/^/  /'
elif command_exists ifconfig; then
    echo "Interfaces de red (ifconfig):"
    ifconfig | grep -E "^[a-z]|inet " | sed 's/^/  /'
else
    echo "[ERROR] Comandos ip/ifconfig no disponibles"
fi

echo ""
echo "=================================================================="
echo "3. VERIFICACION DE SERVICIOS"
echo "=================================================================="
echo ""

echo -n "MariaDB: "
if systemctl is-active --quiet mariadb 2>/dev/null; then
    echo "[CORRIENDO]"
elif service mariadb status >/dev/null 2>&1; then
    echo "[CORRIENDO]"
else
    echo "[DETENIDO]"
fi

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

echo -n "MariaDB puerto $MARIADB_PORT: "
if command_exists netstat; then
    if netstat -tlnp 2>/dev/null | grep -q ":$MARIADB_PORT"; then
        echo "[ESCUCHANDO]"
        netstat -tlnp 2>/dev/null | grep ":$MARIADB_PORT" | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
elif command_exists ss; then
    if ss -tlnp 2>/dev/null | grep -q ":$MARIADB_PORT"; then
        echo "[ESCUCHANDO]"
        ss -tlnp 2>/dev/null | grep ":$MARIADB_PORT" | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
else
    echo "[ERROR] Comandos netstat/ss no disponibles"
fi

echo ""

echo -n "PostgreSQL puerto $POSTGRES_PORT: "
if command_exists netstat; then
    if netstat -tlnp 2>/dev/null | grep -q ":$POSTGRES_PORT"; then
        echo "[ESCUCHANDO]"
        netstat -tlnp 2>/dev/null | grep ":$POSTGRES_PORT" | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
elif command_exists ss; then
    if ss -tlnp 2>/dev/null | grep -q ":$POSTGRES_PORT"; then
        echo "[ESCUCHANDO]"
        ss -tlnp 2>/dev/null | grep ":$POSTGRES_PORT" | head -n 1 | sed 's/^/  /'
    else
        echo "[NO ESCUCHANDO]"
    fi
else
    echo "[ERROR] Comandos netstat/ss no disponibles"
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
    echo "[FALLO] No se pudo hacer ping a 127.0.0.1"
fi

# Ping a gateway si existe
echo -n "Gateway por defecto: "
if [ -n "$GATEWAY" ]; then
    echo -n "$GATEWAY "
    if ping -c 1 -W 2 "$GATEWAY" >/dev/null 2>&1; then
        echo "[OK]"
    else
        echo "[FALLO] No se pudo hacer ping al gateway"
    fi
else
    echo "[NO ENCONTRADO] No se detectó gateway por defecto"
fi

# Conectividad externa
echo -n "Internet (8.8.8.8): "
if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO] No se pudo hacer ping a 8.8.8.8"
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
    echo "[ERROR] /etc/resolv.conf no encontrado"
fi

# Verificar resolución DNS
echo ""
echo -n "Resolucion DNS (google.com): "
if command_exists getent; then
    if getent hosts google.com >/dev/null 2>&1; then
        echo "[OK]"
    else
        echo "[FALLO] getent no pudo resolver google.com"
    fi
elif command_exists host; then
    if host google.com >/dev/null 2>&1; then
        echo "[OK]"
    else
        echo "[FALLO] host no pudo resolver google.com"
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
    echo "[ERROR] Comandos ss/netstat no disponibles"
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
    echo "[FALLO] No se pudo conectar como root"
fi

# Test MariaDB usuario aplicacion
echo -n "MariaDB ($MARIADB_USER): "
if mysql -u "$MARIADB_USER" -p"$MARIADB_PASS" "$MARIADB_DB" -e "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO] No se pudo conectar como $MARIADB_USER a $MARIADB_DB"
fi

# Test PostgreSQL postgres
echo -n "PostgreSQL (postgres): "
if PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO] No se pudo conectar como postgres"
fi

# Test PostgreSQL usuario aplicacion
echo -n "PostgreSQL ($POSTGRES_USER): "
if PGPASSWORD="$POSTGRES_PASS_USER" psql -U "$POSTGRES_USER" -h localhost -d "$POSTGRES_DB" -c "SELECT 1;" >/dev/null 2>&1; then
    echo "[OK]"
else
    echo "[FALLO] No se pudo conectar como $POSTGRES_USER a $POSTGRES_DB"
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
    echo "[ERROR] No se pudo conectar a MariaDB o no se encontró la base $MARIADB_DB"
fi

echo ""
echo "Bases de datos PostgreSQL:"
echo "--------------------------"
if PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "\l" 2>/dev/null | grep -E "(Name|$POSTGRES_DB)"; then
    :
else
    echo "[ERROR] No se pudo conectar a PostgreSQL o no se encontró la base $POSTGRES_DB"
fi

echo ""
echo "=================================================================="
echo "10. USUARIOS DE BASES DE DATOS"
echo "=================================================================="
echo ""

echo "Usuarios MariaDB:"
echo "-----------------"
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT User, Host FROM mysql.user WHERE User IN ('root', '$MARIADB_USER');" 2>/dev/null || echo "[ERROR] No se pudo consultar usuarios MariaDB"

echo ""
echo "Usuarios PostgreSQL:"
echo "--------------------"
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -c "SELECT usename FROM pg_user WHERE usename IN ('postgres', '$POSTGRES_USER');" 2>/dev/null || echo "[ERROR] No se pudo consultar usuarios PostgreSQL"
echo ""
echo "=================================================================="
echo "11. VERSIONES DE SOFTWARE"
echo "=================================================================="
echo ""

# Version MariaDB
echo -n "MariaDB: "
mysql -u root -p"$MARIADB_ROOT_PASS" -e "SELECT VERSION();" 2>/dev/null | tail -n 1 || echo "[ERROR] No se pudo obtener la versión de MariaDB"

# Version PostgreSQL
echo -n "PostgreSQL: "
PGPASSWORD="$POSTGRES_PASS" psql -U postgres -h localhost -t -c "SELECT version();" 2>/dev/null | head -n 1 | xargs || echo "[ERROR] No se pudo obtener la versión de PostgreSQL"

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
    echo "[ERROR] Comandos ip/route no disponibles"
fi

echo ""
echo "=================================================================="
echo "13. PORT FORWARDING INFO"
echo "=================================================================="
echo ""

echo "Configuración de Vagrant (en tu Vagrantfile):"
echo ""
echo "  Host (Windows)  ->  Guest (VM)"
echo "  --------------     -----------"
echo "  Puerto 13306    ->  ${MARIADB_PORT:-?} (MariaDB)"
echo "  Puerto 15432    ->  ${POSTGRES_PORT:-?} (PostgreSQL)"

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
echo "Con Clientes Gráficos (DBeaver/HeidiSQL/pgAdmin):"
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
