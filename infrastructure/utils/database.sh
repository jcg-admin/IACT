#!/usr/bin/env bash
# utils/database.sh - Database verification functions for IACT DevContainer
# Provides functions to verify PostgreSQL and MariaDB connectivity and status
# Supports both DevContainer and traditional environments

set -euo pipefail

# =============================================================================
# POSTGRESQL VERIFICATION FUNCTIONS
# =============================================================================

# Check if PostgreSQL client is available
# Usage: iact_check_postgres_client
#
# Returns:
#   0 - PostgreSQL client (psql) is available
#   1 - PostgreSQL client not found
iact_check_postgres_client() {
    if iact_check_command_exists "psql"; then
        iact_log_debug "PostgreSQL client (psql) is available"
        return 0
    else
        iact_log_debug "PostgreSQL client (psql) not found"
        return 1
    fi
}

# Test PostgreSQL connection
# Usage: iact_test_postgres_connection
# Usage: iact_test_postgres_connection "custom_host" "5433" "custom_db" "custom_user" "custom_pass"
#
# Args:
#   $1 - Host (optional, default: from DJANGO_DB_HOST)
#   $2 - Port (optional, default: from DJANGO_DB_PORT)
#   $3 - Database (optional, default: from DJANGO_DB_NAME)
#   $4 - User (optional, default: from DJANGO_DB_USER)
#   $5 - Password (optional, default: from DJANGO_DB_PASSWORD)
#
# Returns:
#   0 - Connection successful
#   1 - Connection failed
iact_test_postgres_connection() {
    local host="${1:-${DJANGO_DB_HOST:-localhost}}"
    local port="${2:-${DJANGO_DB_PORT:-5432}}"
    local database="${3:-${DJANGO_DB_NAME:-postgres}}"
    local user="${4:-${DJANGO_DB_USER:-postgres}}"
    local password="${5:-${DJANGO_DB_PASSWORD:-}}"

    if ! iact_check_postgres_client; then
        iact_log_error "PostgreSQL client not available"
        return 1
    fi

    iact_log_debug "Testing PostgreSQL connection to $host:$port/$database as $user"

    # Set password environment variable if provided
    local pg_env=""
    if [[ -n "$password" ]]; then
        pg_env="PGPASSWORD=$password"
    fi

    # Try to connect and run a simple query
    if env $pg_env psql -h "$host" -p "$port" -U "$user" -d "$database" -c "SELECT 1;" >/dev/null 2>&1; then
        iact_log_debug "PostgreSQL connection successful"
        return 0
    else
        iact_log_debug "PostgreSQL connection failed"
        return 1
    fi
}

# Check if PostgreSQL is accessible (simplified version)
# Uses environment variables from Django settings
# Usage: iact_check_postgres_connect
#
# Returns:
#   0 - PostgreSQL is accessible
#   1 - PostgreSQL is not accessible
iact_check_postgres_connect() {
    local host="${DJANGO_DB_HOST:-db_postgres}"
    local port="${DJANGO_DB_PORT:-5432}"
    local database="${DJANGO_DB_NAME:-iact_analytics}"
    local user="${DJANGO_DB_USER:-iact_user}"
    local password="${DJANGO_DB_PASSWORD:-}"

    iact_log_debug "Checking PostgreSQL connectivity: $host:$port/$database"

    if iact_test_postgres_connection "$host" "$port" "$database" "$user" "$password"; then
        iact_log_debug "PostgreSQL is accessible"
        return 0
    else
        iact_log_debug "PostgreSQL is not accessible"
        return 1
    fi
}

# Check if PostgreSQL database exists
# Usage: iact_check_postgres_database_exists "iact_analytics"
#
# Args:
#   $1 - Database name
#   $2 - Host (optional)
#   $3 - Port (optional)
#   $4 - User (optional)
#   $5 - Password (optional)
#
# Returns:
#   0 - Database exists
#   1 - Database does not exist or connection failed
iact_check_postgres_database_exists() {
    local database="$1"
    local host="${2:-${DJANGO_DB_HOST:-localhost}}"
    local port="${3:-${DJANGO_DB_PORT:-5432}}"
    local user="${4:-${DJANGO_DB_USER:-postgres}}"
    local password="${5:-${DJANGO_DB_PASSWORD:-}}"

    if ! iact_check_postgres_client; then
        iact_log_error "PostgreSQL client not available"
        return 1
    fi

    iact_log_debug "Checking if PostgreSQL database exists: $database"

    local pg_env=""
    if [[ -n "$password" ]]; then
        pg_env="PGPASSWORD=$password"
    fi

    # List databases and check if our database exists
    local db_list
    db_list=$(env $pg_env psql -h "$host" -p "$port" -U "$user" -d postgres -t -c "SELECT datname FROM pg_database WHERE datname='$database';" 2>/dev/null | xargs)

    if [[ "$db_list" == "$database" ]]; then
        iact_log_debug "PostgreSQL database exists: $database"
        return 0
    else
        iact_log_debug "PostgreSQL database does not exist: $database"
        return 1
    fi
}

# Get count of tables in PostgreSQL database
# Usage: table_count=$(iact_check_postgres_tables_count "iact_analytics")
#
# Args:
#   $1 - Database name (optional, default: from DJANGO_DB_NAME)
#
# Returns:
#   Prints number of tables to stdout
iact_check_postgres_tables_count() {
    local database="${1:-${DJANGO_DB_NAME:-iact_analytics}}"
    local host="${DJANGO_DB_HOST:-localhost}"
    local port="${DJANGO_DB_PORT:-5432}"
    local user="${DJANGO_DB_USER:-postgres}"
    local password="${DJANGO_DB_PASSWORD:-}"

    if ! iact_check_postgres_client; then
        echo "0"
        return 1
    fi

    local pg_env=""
    if [[ -n "$password" ]]; then
        pg_env="PGPASSWORD=$password"
    fi

    # Count tables in public schema
    local count
    count=$(env $pg_env psql -h "$host" -p "$port" -U "$user" -d "$database" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';" 2>/dev/null | xargs)

    echo "${count:-0}"
}

# Wait for PostgreSQL to be ready
# Usage: iact_wait_for_postgres
# Usage: iact_wait_for_postgres "60"
#
# Args:
#   $1 - Timeout in seconds (optional, default: 30)
#
# Returns:
#   0 - PostgreSQL is ready
#   1 - Timeout reached
iact_wait_for_postgres() {
    local timeout="${1:-30}"
    local host="${DJANGO_DB_HOST:-db_postgres}"
    local port="${DJANGO_DB_PORT:-5432}"

    iact_log_info "Waiting for PostgreSQL to be ready on $host:$port (timeout: ${timeout}s)"

    local counter=0
    while [[ $counter -lt $timeout ]]; do
        if iact_check_postgres_connect; then
            iact_log_success "PostgreSQL is ready"
            return 0
        fi

        sleep 1
        ((counter++))
    done

    iact_log_error "PostgreSQL not ready after ${timeout}s"
    return 1
}

# =============================================================================
# MARIADB/MYSQL VERIFICATION FUNCTIONS
# =============================================================================

# Check if MariaDB/MySQL client is available
# Usage: iact_check_mariadb_client
#
# Returns:
#   0 - MariaDB/MySQL client is available
#   1 - MariaDB/MySQL client not found
iact_check_mariadb_client() {
    if iact_check_command_exists "mysql"; then
        iact_log_debug "MariaDB/MySQL client (mysql) is available"
        return 0
    elif iact_check_command_exists "mariadb"; then
        iact_log_debug "MariaDB client (mariadb) is available"
        return 0
    else
        iact_log_debug "MariaDB/MySQL client not found"
        return 1
    fi
}

# Test MariaDB connection
# Usage: iact_test_mariadb_connection
# Usage: iact_test_mariadb_connection "custom_host" "3307" "custom_db" "custom_user" "custom_pass"
#
# Args:
#   $1 - Host (optional, default: from IVR_DB_HOST)
#   $2 - Port (optional, default: from IVR_DB_PORT)
#   $3 - Database (optional, default: from IVR_DB_NAME)
#   $4 - User (optional, default: from IVR_DB_USER)
#   $5 - Password (optional, default: from IVR_DB_PASSWORD)
#
# Returns:
#   0 - Connection successful
#   1 - Connection failed
iact_test_mariadb_connection() {
    local host="${1:-${IVR_DB_HOST:-localhost}}"
    local port="${2:-${IVR_DB_PORT:-3306}}"
    local database="${3:-${IVR_DB_NAME:-mysql}}"
    local user="${4:-${IVR_DB_USER:-root}}"
    local password="${5:-${IVR_DB_PASSWORD:-}}"

    if ! iact_check_mariadb_client; then
        iact_log_error "MariaDB/MySQL client not available"
        return 1
    fi

    iact_log_debug "Testing MariaDB connection to $host:$port/$database as $user"

    # Build mysql command with password if provided
    local mysql_cmd="mysql -h $host -P $port -u $user"
    if [[ -n "$password" ]]; then
        mysql_cmd="$mysql_cmd -p$password"
    fi

    # Try to connect and run a simple query
    if $mysql_cmd -e "SELECT 1;" >/dev/null 2>&1; then
        iact_log_debug "MariaDB connection successful"
        return 0
    else
        iact_log_debug "MariaDB connection failed"
        return 1
    fi
}

# Check if MariaDB is accessible (simplified version)
# Uses environment variables from Django settings (IVR database)
# Usage: iact_check_mariadb_connect
#
# Returns:
#   0 - MariaDB is accessible
#   1 - MariaDB is not accessible
iact_check_mariadb_connect() {
    local host="${IVR_DB_HOST:-db_mariadb}"
    local port="${IVR_DB_PORT:-3306}"
    local database="${IVR_DB_NAME:-ivr_legacy}"
    local user="${IVR_DB_USER:-ivr_readonly}"
    local password="${IVR_DB_PASSWORD:-}"

    iact_log_debug "Checking MariaDB connectivity: $host:$port/$database"

    if iact_test_mariadb_connection "$host" "$port" "$database" "$user" "$password"; then
        iact_log_debug "MariaDB is accessible"
        return 0
    else
        iact_log_debug "MariaDB is not accessible"
        return 1
    fi
}

# Check if MariaDB database exists
# Usage: iact_check_mariadb_database_exists "ivr_legacy"
#
# Args:
#   $1 - Database name
#   $2 - Host (optional)
#   $3 - Port (optional)
#   $4 - User (optional)
#   $5 - Password (optional)
#
# Returns:
#   0 - Database exists
#   1 - Database does not exist or connection failed
iact_check_mariadb_database_exists() {
    local database="$1"
    local host="${2:-${IVR_DB_HOST:-localhost}}"
    local port="${3:-${IVR_DB_PORT:-3306}}"
    local user="${4:-${IVR_DB_USER:-root}}"
    local password="${5:-${IVR_DB_PASSWORD:-}}"

    if ! iact_check_mariadb_client; then
        iact_log_error "MariaDB/MySQL client not available"
        return 1
    fi

    iact_log_debug "Checking if MariaDB database exists: $database"

    local mysql_cmd="mysql -h $host -P $port -u $user"
    if [[ -n "$password" ]]; then
        mysql_cmd="$mysql_cmd -p$password"
    fi

    # Check if database exists
    if $mysql_cmd -e "SHOW DATABASES LIKE '$database';" 2>/dev/null | grep -q "$database"; then
        iact_log_debug "MariaDB database exists: $database"
        return 0
    else
        iact_log_debug "MariaDB database does not exist: $database"
        return 1
    fi
}

# Get count of tables in MariaDB database
# Usage: table_count=$(iact_check_mariadb_tables_count "ivr_legacy")
#
# Args:
#   $1 - Database name (optional, default: from IVR_DB_NAME)
#
# Returns:
#   Prints number of tables to stdout
iact_check_mariadb_tables_count() {
    local database="${1:-${IVR_DB_NAME:-ivr_legacy}}"
    local host="${IVR_DB_HOST:-localhost}"
    local port="${IVR_DB_PORT:-3306}"
    local user="${IVR_DB_USER:-root}"
    local password="${IVR_DB_PASSWORD:-}"

    if ! iact_check_mariadb_client; then
        echo "0"
        return 1
    fi

    local mysql_cmd="mysql -h $host -P $port -u $user"
    if [[ -n "$password" ]]; then
        mysql_cmd="$mysql_cmd -p$password"
    fi

    # Count tables
    local count
    count=$($mysql_cmd -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='$database';" 2>/dev/null)

    echo "${count:-0}"
}

# Wait for MariaDB to be ready
# Usage: iact_wait_for_mariadb
# Usage: iact_wait_for_mariadb "60"
#
# Args:
#   $1 - Timeout in seconds (optional, default: 30)
#
# Returns:
#   0 - MariaDB is ready
#   1 - Timeout reached
iact_wait_for_mariadb() {
    local timeout="${1:-30}"
    local host="${IVR_DB_HOST:-db_mariadb}"
    local port="${IVR_DB_PORT:-3306}"

    iact_log_info "Waiting for MariaDB to be ready on $host:$port (timeout: ${timeout}s)"

    local counter=0
    while [[ $counter -lt $timeout ]]; do
        if iact_check_mariadb_connect; then
            iact_log_success "MariaDB is ready"
            return 0
        fi

        sleep 1
        ((counter++))
    done

    iact_log_error "MariaDB not ready after ${timeout}s"
    return 1
}

# =============================================================================
# DATABASE VALIDATION FUNCTIONS
# =============================================================================

# Validate all database connections
# Checks both PostgreSQL and MariaDB connectivity
# Usage: iact_validate_database_connections
#
# Returns:
#   0 - All database connections successful
#   1 - One or more database connections failed
iact_validate_database_connections() {
    iact_log_header "Database Connections Validation"

    local validation_errors=0

    # Check PostgreSQL
    iact_log_info "Checking PostgreSQL connection..."
    if iact_check_postgres_connect; then
        iact_log_success "PostgreSQL connection: OK"

        # Check if database exists
        local pg_db="${DJANGO_DB_NAME:-iact_analytics}"
        if iact_check_postgres_database_exists "$pg_db"; then
            iact_log_success "PostgreSQL database exists: $pg_db"

            # Check table count
            local pg_tables
            pg_tables=$(iact_check_postgres_tables_count "$pg_db")
            iact_log_info "PostgreSQL tables in $pg_db: $pg_tables"
        else
            iact_log_warning "PostgreSQL database does not exist: $pg_db"
        fi
    else
        iact_log_error "PostgreSQL connection: FAILED"
        ((validation_errors++))
    fi

    # Check MariaDB
    iact_log_info "Checking MariaDB connection..."
    if iact_check_mariadb_connect; then
        iact_log_success "MariaDB connection: OK"

        # Check if database exists
        local maria_db="${IVR_DB_NAME:-ivr_legacy}"
        if iact_check_mariadb_database_exists "$maria_db"; then
            iact_log_success "MariaDB database exists: $maria_db"

            # Check table count
            local maria_tables
            maria_tables=$(iact_check_mariadb_tables_count "$maria_db")
            iact_log_info "MariaDB tables in $maria_db: $maria_tables"
        else
            iact_log_warning "MariaDB database does not exist: $maria_db"
        fi
    else
        iact_log_error "MariaDB connection: FAILED"
        ((validation_errors++))
    fi

    # Report results
    if [[ $validation_errors -eq 0 ]]; then
        iact_log_success "Database validation passed"
        return 0
    else
        iact_log_error "Database validation failed with $validation_errors errors"
        return 1
    fi
}

# =============================================================================
# COMPATIBILITY ALIASES
# =============================================================================

check_postgres_client() { iact_check_postgres_client "$@"; }
test_postgres_connection() { iact_test_postgres_connection "$@"; }
check_postgres_connect() { iact_check_postgres_connect "$@"; }
check_postgres_database_exists() { iact_check_postgres_database_exists "$@"; }
check_postgres_tables_count() { iact_check_postgres_tables_count "$@"; }
wait_for_postgres() { iact_wait_for_postgres "$@"; }

check_mariadb_client() { iact_check_mariadb_client "$@"; }
test_mariadb_connection() { iact_test_mariadb_connection "$@"; }
check_mariadb_connect() { iact_check_mariadb_connect "$@"; }
check_mariadb_database_exists() { iact_check_mariadb_database_exists "$@"; }
check_mariadb_tables_count() { iact_check_mariadb_tables_count "$@"; }
wait_for_mariadb() { iact_wait_for_mariadb "$@"; }

validate_database_connections() { iact_validate_database_connections "$@"; }

# =============================================================================
# INITIALIZATION
# =============================================================================

iact_log_debug "Database module loaded successfully"