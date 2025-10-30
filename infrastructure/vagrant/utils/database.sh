#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Database Utilities
# =============================================================================
# Description: Database utilities for Vagrant environment
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant-specific database operations
# =============================================================================

# Prevenir ejecución directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    exit 1
fi

# =============================================================================
# POSTGRESQL UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_db_postgres_is_ready
# Description: Check if PostgreSQL is ready to accept connections
# Arguments: $1 - user, $2 - password, $3 - host (default: localhost)
# Returns: 0 if ready, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_db_postgres_is_ready() {
    local user="$1"
    local password="$2"
    local host="${3:-localhost}"

    PGPASSWORD="$password" psql -U "$user" -h "$host" -c "SELECT 1;" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# vagrant_db_postgres_wait
# Description: Wait for PostgreSQL to be ready
# Arguments: $1 - user, $2 - password, $3 - max wait (default: 60), $4 - host (default: localhost)
# Returns: 0 if ready, 1 on timeout
# -----------------------------------------------------------------------------
vagrant_db_postgres_wait() {
    local user="$1"
    local password="$2"
    local max_wait="${3:-60}"
    local host="${4:-localhost}"
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if vagrant_db_postgres_is_ready "$user" "$password" "$host"; then
            return 0
        fi

        sleep 1
        ((counter++))
    done

    echo "Error: PostgreSQL no respondio en ${max_wait}s" >&2
    return 1
}

# -----------------------------------------------------------------------------
# vagrant_db_postgres_database_exists
# Description: Check if PostgreSQL database exists
# Arguments: $1 - database name, $2 - user, $3 - password, $4 - host (default: localhost)
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_db_postgres_database_exists() {
    local database="$1"
    local user="$2"
    local password="$3"
    local host="${4:-localhost}"

    local count
    count=$(PGPASSWORD="$password" psql -U "$user" -h "$host" -tAc "SELECT COUNT(*) FROM pg_database WHERE datname='$database';" 2>/dev/null)

    [[ "$count" -eq 1 ]]
}

# -----------------------------------------------------------------------------
# vagrant_db_postgres_user_exists
# Description: Check if PostgreSQL user exists
# Arguments: $1 - username, $2 - admin user, $3 - admin password, $4 - host (default: localhost)
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_db_postgres_user_exists() {
    local username="$1"
    local admin_user="$2"
    local admin_password="$3"
    local host="${4:-localhost}"

    local count
    count=$(PGPASSWORD="$admin_password" psql -U "$admin_user" -h "$host" -tAc "SELECT COUNT(*) FROM pg_user WHERE usename='$username';" 2>/dev/null)

    [[ "$count" -eq 1 ]]
}

# =============================================================================
# MARIADB/MYSQL UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_db_mariadb_is_ready
# Description: Check if MariaDB is ready to accept connections
# Arguments: $1 - user, $2 - password
# Returns: 0 if ready, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_db_mariadb_is_ready() {
    local user="$1"
    local password="$2"

    mysql -u "$user" -p"$password" -e "SELECT 1;" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# vagrant_db_mariadb_wait
# Description: Wait for MariaDB to be ready
# Arguments: $1 - user, $2 - password, $3 - max wait (default: 60)
# Returns: 0 if ready, 1 on timeout
# -----------------------------------------------------------------------------
vagrant_db_mariadb_wait() {
    local user="$1"
    local password="$2"
    local max_wait="${3:-60}"
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if vagrant_db_mariadb_is_ready "$user" "$password"; then
            return 0
        fi

        sleep 1
        ((counter++))
    done

    echo "Error: MariaDB no respondio en ${max_wait}s" >&2
    return 1
}

# -----------------------------------------------------------------------------
# vagrant_db_mariadb_database_exists
# Description: Check if MariaDB database exists
# Arguments: $1 - database name, $2 - user, $3 - password
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_db_mariadb_database_exists() {
    local database="$1"
    local user="$2"
    local password="$3"

    local count
    count=$(mysql -u "$user" -p"$password" -e "SELECT COUNT(*) FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='$database';" 2>/dev/null | tail -n 1)

    [[ "$count" -eq 1 ]]
}

# -----------------------------------------------------------------------------
# vagrant_db_mariadb_user_exists
# Description: Check if MariaDB user exists
# Arguments: $1 - username, $2 - admin user, $3 - admin password
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_db_mariadb_user_exists() {
    local username="$1"
    local admin_user="$2"
    local admin_password="$3"

    local count
    count=$(mysql -u "$admin_user" -p"$admin_password" -e "SELECT COUNT(*) FROM mysql.user WHERE User='$username';" 2>/dev/null | tail -n 1)

    [[ "$count" -gt 0 ]]
}

# =============================================================================
# EXPORT
# =============================================================================

export -f vagrant_db_postgres_is_ready
export -f vagrant_db_postgres_wait
export -f vagrant_db_postgres_database_exists
export -f vagrant_db_postgres_user_exists
export -f vagrant_db_mariadb_is_ready
export -f vagrant_db_mariadb_wait
export -f vagrant_db_mariadb_database_exists
export -f vagrant_db_mariadb_user_exists