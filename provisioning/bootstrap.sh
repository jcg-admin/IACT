#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

log() {
  local level="$1"; shift
  printf '[bootstrap][%s] %s\n' "$level" "$*"
}

install_packages() {
  log INFO "Actualizando índice de paquetes"
  apt-get update
  log INFO "Instalando PostgreSQL y MariaDB"
  apt-get install -y postgresql postgresql-contrib mariadb-server
}

configure_postgres() {
  log INFO "Configurando PostgreSQL"
  local pg_version
  pg_version="$(ls /etc/postgresql | head -n1)"
  local pg_conf="/etc/postgresql/${pg_version}/main/postgresql.conf"
  local pg_hba="/etc/postgresql/${pg_version}/main/pg_hba.conf"

  sed -i "s/^#\?listen_addresses.*/listen_addresses = '*'" "$pg_conf"

  cat <<CFG >"$pg_hba"
# Autenticación para Call Center Analytics
local   all             postgres                                peer
host    all             all             127.0.0.1/32            md5
host    all             all             0.0.0.0/0               md5
CFG

  systemctl restart postgresql

  sudo -u postgres psql <<SQL
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'django_user') THEN
    CREATE ROLE django_user LOGIN PASSWORD 'django_pass';
  END IF;
END
$$;
SQL

  if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = 'callcenterdb'" | grep -q 1; then
    sudo -u postgres createdb -O django_user callcenterdb
  fi

  sudo -u postgres psql -d callcenterdb <<SQL
CREATE SCHEMA IF NOT EXISTS analytics AUTHORIZATION django_user;
SQL
}

configure_mariadb() {
  log INFO "Configurando MariaDB"
  sed -i "s/^bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mariadb.conf.d/50-server.cnf
  systemctl restart mariadb

  mysql --protocol=socket -uroot <<SQL
CREATE DATABASE IF NOT EXISTS ivrdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'django_user'@'%' IDENTIFIED BY 'django_pass';
GRANT ALL PRIVILEGES ON ivrdb.* TO 'django_user'@'%';
FLUSH PRIVILEGES;
SQL
}

main() {
  install_packages
  configure_postgres
  configure_mariadb

  log INFO "Servicios preparados. Puertos expuestos: PostgreSQL 5432, MariaDB 3306"
}

main "$@"
