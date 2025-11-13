#!/bin/bash
# Script: verificar servicios de bases de datos locales (PostgreSQL + MariaDB)
#
# Este script valida tres aspectos clave:
#   1. Disponibilidad de los clientes `psql` y `mysql`.
#   2. Conexión básica a ambas bases de datos utilizando credenciales del entorno.
#   3. Reporte compacto con códigos de salida diferenciados.
#
# Uso:
#   ./scripts/verificar_servicios.sh [opciones]
#
# Opciones principales:
#   --dry-run                Muestra los pasos sin ejecutar conexiones reales.
#   --postgres-host <host>   Host PostgreSQL (default: $DB_ANALYTICS_HOST o 127.0.0.1)
#   --postgres-port <port>   Puerto PostgreSQL (default: $DB_ANALYTICS_PORT o 15432)
#   --postgres-db <db>       Base PostgreSQL (default: $DB_ANALYTICS_NAME o iact_analytics)
#   --postgres-user <user>   Usuario PostgreSQL (default: $DB_ANALYTICS_USER o django_user)
#   --postgres-password <pw> Password PostgreSQL (default: $DB_ANALYTICS_PASSWORD o django_pass)
#   --mariadb-host <host>    Host MariaDB (default: $DB_IVR_HOST o 127.0.0.1)
#   --mariadb-port <port>    Puerto MariaDB (default: $DB_IVR_PORT o 13306)
#   --mariadb-db <db>        Base MariaDB (default: $DB_IVR_NAME o ivr_data)
#   --mariadb-user <user>    Usuario MariaDB (default: $DB_IVR_USER o django_user)
#   --mariadb-password <pw>  Password MariaDB (default: $DB_IVR_PASSWORD o django_pass)
#   --help                   Muestra esta ayuda.
#
# Códigos de salida:
#   0  -> Todo OK.
#   1  -> Clientes instalados pero alguna conexión falló.
#   2  -> Clientes requeridos no disponibles en PATH.
#
# El modo `--dry-run` permite validar configuraciones durante CI sin depender de
# bases de datos levantadas.

set -u

POSTGRES_HOST="${DB_ANALYTICS_HOST:-127.0.0.1}"
POSTGRES_PORT="${DB_ANALYTICS_PORT:-15432}"
POSTGRES_DB="${DB_ANALYTICS_NAME:-iact_analytics}"
POSTGRES_USER="${DB_ANALYTICS_USER:-django_user}"
POSTGRES_PASSWORD="${DB_ANALYTICS_PASSWORD:-django_pass}"

MARIADB_HOST="${DB_IVR_HOST:-127.0.0.1}"
MARIADB_PORT="${DB_IVR_PORT:-13306}"
MARIADB_DB="${DB_IVR_NAME:-ivr_data}"
MARIADB_USER="${DB_IVR_USER:-django_user}"
MARIADB_PASSWORD="${DB_IVR_PASSWORD:-django_pass}"

DRY_RUN=false

usage() {
    sed -n '1,40p' "$0" | sed 's/^# //'
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --postgres-host)
            POSTGRES_HOST="$2"; shift 2;;
        --postgres-port)
            POSTGRES_PORT="$2"; shift 2;;
        --postgres-db)
            POSTGRES_DB="$2"; shift 2;;
        --postgres-user)
            POSTGRES_USER="$2"; shift 2;;
        --postgres-password)
            POSTGRES_PASSWORD="$2"; shift 2;;
        --mariadb-host)
            MARIADB_HOST="$2"; shift 2;;
        --mariadb-port)
            MARIADB_PORT="$2"; shift 2;;
        --mariadb-db)
            MARIADB_DB="$2"; shift 2;;
        --mariadb-user)
            MARIADB_USER="$2"; shift 2;;
        --mariadb-password)
            MARIADB_PASSWORD="$2"; shift 2;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "[ERROR] Opción desconocida: $1" >&2
            usage
            exit 1
            ;;
    esac
done

echo "========================================================================"
echo "Script: verificar servicios de bases de datos"
echo "========================================================================"
echo "[INFO] PostgreSQL => ${POSTGRES_USER}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "[INFO] MariaDB    => ${MARIADB_USER}@${MARIADB_HOST}:${MARIADB_PORT}/${MARIADB_DB}"
echo ""

missing=0
for client in psql mysql; do
    if ! command -v "$client" >/dev/null 2>&1; then
        echo "[ERROR] Cliente $client no encontrado en PATH"
        missing=1
    else
        echo "[OK] Cliente $client disponible"
    fi
done

if [[ "$missing" -eq 1 && "$DRY_RUN" == true ]]; then
    echo ""
    echo "[ATENCION] Clientes faltantes detectados, pero continuamos por tratarse de un dry-run."
fi

if [[ "$missing" -eq 1 && "$DRY_RUN" != true ]]; then
    echo ""
    echo "[ATENCION] Ejecuta el runbook manual si necesitas más contexto: docs/operaciones/verificar_servicios.md"
    exit 2
fi

if [[ "$DRY_RUN" == true ]]; then
    echo "[DRY-RUN] Validación de conectividad omitida."
    echo "[DRY-RUN] Ejecutarías:"
    echo "  PGPASSWORD=**** psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c 'SELECT 1;'"
    echo "  mysql -h $MARIADB_HOST -P $MARIADB_PORT -u $MARIADB_USER -p**** -e 'SELECT 1;' $MARIADB_DB"
    exit 0
fi

EXIT_CODE=0

echo "[INFO] Verificando PostgreSQL..."
PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" >/dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "[OK] PostgreSQL respondió correctamente"
else
    echo "[FAIL] No fue posible conectar a PostgreSQL"
    EXIT_CODE=1
fi

echo "[INFO] Verificando MariaDB..."
mysql -h "$MARIADB_HOST" -P "$MARIADB_PORT" -u "$MARIADB_USER" -p"$MARIADB_PASSWORD" -e "SELECT 1;" "$MARIADB_DB" >/dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "[OK] MariaDB respondió correctamente"
else
    echo "[FAIL] No fue posible conectar a MariaDB"
    EXIT_CODE=1
fi

if [[ "$EXIT_CODE" -eq 0 ]]; then
    echo ""
    echo "[OK] Todos los servicios están operativos"
else
    echo ""
    echo "[ATENCION] Revisa el runbook docs/operaciones/verificar_servicios.md para pasos de troubleshooting"
fi

exit "$EXIT_CODE"
