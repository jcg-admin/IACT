#!/usr/bin/env bash
set -euo pipefail

POSTGRES_HOST=${POSTGRES_HOST:-127.0.0.1}
POSTGRES_PORT=${POSTGRES_PORT:-15432}
POSTGRES_DB=${POSTGRES_DB:-callcenterdb}
POSTGRES_USER=${POSTGRES_USER:-django_user}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-django_pass}

MARIADB_HOST=${MARIADB_HOST:-127.0.0.1}
MARIADB_PORT=${MARIADB_PORT:-13306}
MARIADB_DB=${MARIADB_DB:-ivrdb}
MARIADB_USER=${MARIADB_USER:-django_user}
MARIADB_PASSWORD=${MARIADB_PASSWORD:-django_pass}

log() {
  local level="$1"; shift
  printf '[verificacion][%s] %s\n' "$level" "$*"
}

check_command() {
  local cmd="$1"
  local package="$2"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    log ERROR "No se encontró el comando '$cmd'. Instala el paquete '$package' en tu entorno anfitrión."
    return 1
  fi
  return 0
}

check_postgres() {
  log INFO "Verificando PostgreSQL en ${POSTGRES_HOST}:${POSTGRES_PORT}"
  if ! check_command psql postgresql-client; then
    return 1
  fi

  PGPASSWORD="$POSTGRES_PASSWORD" psql \
    --host "$POSTGRES_HOST" \
    --port "$POSTGRES_PORT" \
    --username "$POSTGRES_USER" \
    --dbname "$POSTGRES_DB" \
    --command "SELECT version();" \
    --set=ON_ERROR_STOP=1 >/dev/null

  log INFO "Conexión a PostgreSQL exitosa"
}

check_mariadb() {
  log INFO "Verificando MariaDB en ${MARIADB_HOST}:${MARIADB_PORT}"
  if ! check_command mysql mariadb-client; then
    return 1
  fi

  mysql \
    --host="$MARIADB_HOST" \
    --port="$MARIADB_PORT" \
    --user="$MARIADB_USER" \
    --password="$MARIADB_PASSWORD" \
    --database="$MARIADB_DB" \
    --execute="SELECT VERSION();" \
    --batch >/dev/null

  log INFO "Conexión a MariaDB exitosa"
}

main() {
  if [ -f .env ]; then
    # shellcheck source=/dev/null
    source .env
  fi

  local failures=0

  if ! check_postgres; then
    failures=$((failures + 1))
  fi

  if ! check_mariadb; then
    failures=$((failures + 1))
  fi

  if [ "$failures" -gt 0 ]; then
    log WARN "Verificación finalizada con ${failures} fallo(s). Revisa los mensajes anteriores."
    exit 1
  fi

  log INFO "Todos los servicios responden correctamente."
}

main "$@"
