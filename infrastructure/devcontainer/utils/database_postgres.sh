#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - PostgreSQL Database Utilities
# =============================================================================
# Description: PostgreSQL utilities for DevContainer environment
# Author: IACT Team
# Version: 1.0.0
# Context: DevContainer-specific PostgreSQL operations
# =============================================================================

# Prevenir ejecucion directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    exit 1
fi

# =============================================================================
# POSTGRESQL UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# iact_db_postgres_is_ready
# Description: Check if PostgreSQL is ready to accept connections
# Arguments: $1 - user, $2 - password, $3 - host (default: localhost)
# Returns: 0 if ready, 1 otherwise
# -----------------------------------------------------------------------------
iact_db_postgres_is_ready() {
    local user="$1"
    local password="$2"
    local host="${3:-localhost}"

    if [[ -z "$user" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_db_postgres_is_ready requiere user y password" >&2
        return 1
    fi

    PGPASSWORD="$password" psql -U "$user" -h "$host" -c "SELECT 1;" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# iact_db_postgres_wait
# Description: Wait for PostgreSQL to be ready
# Arguments: $1 - user, $2 - password, $3 - max wait (default: 60), $4 - host (default: localhost)
# Returns: 0 if ready, 1 on timeout
# -----------------------------------------------------------------------------
iact_db_postgres_wait() {
    local user="$1"
    local password="$2"
    local max_wait="${3:-60}"
    local host="${4:-localhost}"
    local counter=0

    if [[ -z "$user" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_db_postgres_wait requiere user y password" >&2
        return 1
    fi

    # Validar que max_wait es un número
    if ! [[ "$max_wait" =~ ^[0-9]+$ ]]; then
        echo "Error: max_wait debe ser un número: $max_wait" >&2
        return 1
    fi

    while [[ $counter -lt $max_wait ]]; do
        if iact_db_postgres_is_ready "$user" "$password" "$host"; then
            return 0
        fi

        sleep 1
        ((counter++))
    done

    echo "Error: PostgreSQL no respondio en ${max_wait}s (host: $host, user: $user)" >&2
    return 1
}

# -----------------------------------------------------------------------------
# iact_db_postgres_database_exists
# Description: Check if PostgreSQL database exists
# Arguments: $1 - database name, $2 - user, $3 - password, $4 - host (default: localhost)
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_db_postgres_database_exists() {
    local database="$1"
    local user="$2"
    local password="$3"
    local host="${4:-localhost}"

    if [[ -z "$database" ]] || [[ -z "$user" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_db_postgres_database_exists requiere database, user y password" >&2
        return 1
    fi

    local count
    count=$(PGPASSWORD="$password" psql -U "$user" -h "$host" -tAc "SELECT COUNT(*) FROM pg_database WHERE datname='$database';" 2>/dev/null)

    if [[ -z "$count" ]]; then
        echo "Error: No se pudo consultar base de datos PostgreSQL" >&2
        return 1
    fi

    [[ "$count" -eq 1 ]]
}

# -----------------------------------------------------------------------------
# iact_db_postgres_user_exists
# Description: Check if PostgreSQL user exists
# Arguments: $1 - username, $2 - admin user, $3 - admin password, $4 - host (default: localhost)
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_db_postgres_user_exists() {
    local username="$1"
    local admin_user="$2"
    local admin_password="$3"
    local host="${4:-localhost}"

    if [[ -z "$username" ]] || [[ -z "$admin_user" ]] || [[ -z "$admin_password" ]]; then
        echo "Error: iact_db_postgres_user_exists requiere username, admin_user y admin_password" >&2
        return 1
    fi

    local count
    count=$(PGPASSWORD="$admin_password" psql -U "$admin_user" -h "$host" -tAc "SELECT COUNT(*) FROM pg_user WHERE usename='$username';" 2>/dev/null)

    if [[ -z "$count" ]]; then
        echo "Error: No se pudo consultar usuarios PostgreSQL" >&2
        return 1
    fi

    [[ "$count" -eq 1 ]]
}

# -----------------------------------------------------------------------------
# iact_db_postgres_test_connection
# Description: Test PostgreSQL connection with detailed output
# Arguments: $1 - user, $2 - password, $3 - database (default: postgres), $4 - host (default: localhost)
# Returns: 0 if successful, 1 otherwise
# -----------------------------------------------------------------------------
iact_db_postgres_test_connection() {
    local user="$1"
    local password="$2"
    local database="${3:-postgres}"
    local host="${4:-localhost}"

    if [[ -z "$user" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_db_postgres_test_connection requiere user y password" >&2
        return 1
    fi

    local output
    output=$(PGPASSWORD="$password" psql -U "$user" -h "$host" -d "$database" -c "SELECT version();" 2>&1)
    local exit_code=$?

    if [[ $exit_code -eq 0 ]]; then
        return 0
    else
        echo "Error: Conexión a PostgreSQL falló: $output" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_db_postgres_create_database
# Description: Create PostgreSQL database (idempotent)
# Arguments: $1 - database name, $2 - user, $3 - password, $4 - host (default: localhost)
# Returns: 0 if created or already exists, 1 on failure
# -----------------------------------------------------------------------------
iact_db_postgres_create_database() {
    local database="$1"
    local user="$2"
    local password="$3"
    local host="${4:-localhost}"

    if [[ -z "$database" ]] || [[ -z "$user" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_db_postgres_create_database requiere database, user y password" >&2
        return 1
    fi

    # Check si ya existe (idempotencia)
    if iact_db_postgres_database_exists "$database" "$user" "$password" "$host"; then
        return 0
    fi

    # Crear base de datos
    if PGPASSWORD="$password" psql -U "$user" -h "$host" -c "CREATE DATABASE ${database};" >/dev/null 2>&1; then
        return 0
    else
        echo "Error: No se pudo crear base de datos: $database" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_db_postgres_get_version
# Description: Get PostgreSQL server version
# Arguments: $1 - user, $2 - password, $3 - host (default: localhost)
# Returns: Version string via stdout, or empty on failure
# -----------------------------------------------------------------------------
iact_db_postgres_get_version() {
    local user="$1"
    local password="$2"
    local host="${3:-localhost}"

    if [[ -z "$user" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_db_postgres_get_version requiere user y password" >&2
        return 1
    fi

    PGPASSWORD="$password" psql -U "$user" -h "$host" -tAc "SELECT version();" 2>/dev/null | head -n 1
}

# =============================================================================
# EXPORT
# =============================================================================

export -f iact_db_postgres_is_ready
export -f iact_db_postgres_wait
export -f iact_db_postgres_database_exists
export -f iact_db_postgres_user_exists
export -f iact_db_postgres_test_connection
export -f iact_db_postgres_create_database
export -f iact_db_postgres_get_version