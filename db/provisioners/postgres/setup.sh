#!/bin/bash
# setup.sh
# PostgreSQL database setup script
# Version: 1.0.0

set -euo pipefail

# Load utilities
source /vagrant/utils/core.sh
source /vagrant/utils/database.sh
source /vagrant/utils/logging.sh
source /vagrant/utils/validation.sh

# Main function
main() {
    log_header "PostgreSQL Database Setup"

    # Validate running as root
    if ! validate_root; then
        log_fatal "This script must be run as root"
    fi

    # Validate required variables
    require_vars DB_NAME DB_USER DB_PASSWORD

    # Ensure log directory
    if ! ensure_dir /vagrant/logs; then
        log_error "Failed to create log directory"
        return 1
    fi

    # Verify PostgreSQL is running
    if ! verify_postgresql_running; then
        log_error "PostgreSQL is not running"
        return 1
    fi

    # Create database user
    if ! create_database_user; then
        log_error "Failed to create database user"
        return 1
    fi

    # Create database
    if ! create_database; then
        log_error "Failed to create database"
        return 1
    fi

    # Grant privileges
    if ! grant_user_privileges; then
        log_error "Failed to grant privileges"
        return 1
    fi

    # Install extensions
    if ! install_extensions; then
        log_error "Failed to install extensions"
        return 1
    fi

    # Create schema version table
    if ! create_schema_version_table; then
        log_error "Failed to create schema version table"
        return 1
    fi

    log_success "PostgreSQL database setup completed"
    return 0
}

# Verify PostgreSQL is running
verify_postgresql_running() {
    log_info "Verifying PostgreSQL is running"

    if ! systemctl is-active --quiet postgresql; then
        log_error "PostgreSQL service is not active"
        return 1
    fi

    # Wait for PostgreSQL to be ready
    if ! postgres_wait_ready 30; then
        log_error "PostgreSQL is not ready to accept connections"
        return 1
    fi

    log_success "PostgreSQL is running and ready"
    return 0
}

# Create database user
create_database_user() {
    log_info "Creating database user: ${DB_USER}"

    # Check if user already exists
    local user_exists=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}';" 2>/dev/null || echo "")

    if [[ "$user_exists" == "1" ]]; then
        log_warn "User ${DB_USER} already exists, skipping creation"
        return 0
    fi

    # Create user
    if ! postgres_create_user "${DB_USER}" "${DB_PASSWORD}"; then
        log_error "Failed to create user"
        return 1
    fi

    log_success "User ${DB_USER} created successfully"
    return 0
}

# Create database
create_database() {
    log_info "Creating database: ${DB_NAME}"

    # Check if database already exists
    if postgres_database_exists "${DB_NAME}"; then
        log_warn "Database ${DB_NAME} already exists, skipping creation"
        return 0
    fi

    # Create database
    if ! postgres_create_database "${DB_NAME}"; then
        log_error "Failed to create database"
        return 1
    fi

    log_success "Database ${DB_NAME} created successfully"
    return 0
}

# Grant privileges to user
grant_user_privileges() {
    log_info "Granting privileges to user: ${DB_USER}"

    # Grant all privileges on the database
    if ! postgres_grant_privileges "${DB_NAME}" "${DB_USER}"; then
        log_error "Failed to grant privileges"
        return 1
    fi

    log_success "Privileges granted to ${DB_USER} on ${DB_NAME}"
    return 0
}

# Install PostgreSQL extensions
install_extensions() {
    log_info "Installing PostgreSQL extensions"

    local extensions=(
        "uuid-ossp"
        "pg_trgm"
        "hstore"
        "citext"
        "pg_stat_statements"
    )

    local installed_count=0
    local failed_count=0

    for extension in "${extensions[@]}"; do
        log_info "Installing extension: ${extension}"

        # Check if extension is already installed
        local ext_exists=$(sudo -u postgres psql -d "${DB_NAME}" -tAc "SELECT 1 FROM pg_extension WHERE extname='${extension}';" 2>/dev/null || echo "")

        if [[ "$ext_exists" == "1" ]]; then
            log_warn "Extension ${extension} already installed, skipping"
            installed_count=$((installed_count + 1))
            continue
        fi

        # Install extension
        if sudo -u postgres psql -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS \"${extension}\";" 2>/dev/null; then
            log_success "Extension ${extension} installed"
            installed_count=$((installed_count + 1))
        else
            log_warn "Failed to install extension ${extension}"
            failed_count=$((failed_count + 1))
        fi
    done

    log_info "Extensions installed: ${installed_count}, failed: ${failed_count}"

    return 0
}

# Create schema version table
create_schema_version_table() {
    log_info "Creating schema version table"

    # Create a table to track schema version
    local sql="
    CREATE TABLE IF NOT EXISTS schema_version (
        id SERIAL PRIMARY KEY,
        version VARCHAR(50) NOT NULL,
        description VARCHAR(255),
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_schema_version ON schema_version(version);
    "

    if ! sudo -u postgres psql -d "${DB_NAME}" -c "${sql}" 2>/dev/null; then
        log_error "Failed to create schema_version table"
        return 1
    fi

    # Insert initial version
    local insert_sql="
    INSERT INTO schema_version (version, description)
    VALUES ('1.0.0', 'Initial database schema')
    ON CONFLICT DO NOTHING;
    "

    if ! sudo -u postgres psql -d "${DB_NAME}" -c "${insert_sql}" 2>/dev/null; then
        log_warn "Failed to insert initial schema version (may already exist)"
    fi

    log_success "Schema version table created"
    return 0
}

# Note: main() is called by bootstrap.sh, not auto-executed