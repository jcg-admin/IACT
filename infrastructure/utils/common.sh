#!/bin/bash

set -euo pipefail

# =================================================================
# SYSTEM VERIFICATION FUNCTIONS
# =================================================================

check_ubuntu_bionic() {
    if [ ! -f /etc/os-release ]; then
        log_error "Cannot detect OS version - /etc/os-release not found"
        return 1
    fi

    if ! grep -q "VERSION_ID=\"18.04\"" /etc/os-release; then
        log_error "This script requires Ubuntu 18.04 LTS (Bionic Beaver)"
        log_info "Current OS: $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
        return 1
    fi

    log_success "Ubuntu 18.04 LTS detected"
    return 0
}

check_root_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with root privileges"
        log_info "Try: sudo $0"
        return 1
    fi

    log_success "Root privileges confirmed"
    return 0
}

check_internet_connectivity() {
    local test_hosts=("8.8.8.8" "1.1.1.1")

    for host in "${test_hosts[@]}"; do
        if ping -c 1 -W 5 "$host" >/dev/null 2>&1; then
            log_success "Internet connectivity verified"
            return 0
        fi
    done

    log_error "No internet connectivity detected"
    log_info "Please check network configuration"
    return 1
}

check_disk_space() {
    local required_gb="${1:-2}"
    local available_kb
    available_kb=$(df / | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))

    if [ "$available_gb" -lt "$required_gb" ]; then
        log_error "Insufficient disk space"
        log_info "Required: ${required_gb}GB, Available: ${available_gb}GB"
        return 1
    fi

    log_success "Disk space check passed (${available_gb}GB available)"
    return 0
}

check_memory() {
    local required_mb="${1:-1024}"
    local available_mb
    available_mb=$(free -m | awk 'NR==2{print $2}')

    if [ "$available_mb" -lt "$required_mb" ]; then
        log_warning "Low memory detected"
        log_info "Required: ${required_mb}MB, Available: ${available_mb}MB"
        log_info "Installation may be slow or fail"
        return 1
    fi

    log_success "Memory check passed (${available_mb}MB available)"
    return 0
}

# =================================================================
# PACKAGE MANAGEMENT FUNCTIONS
# =================================================================

update_package_cache() {
    log_step "Updating package cache"

    # Clean APT cache first
    apt-get clean
    rm -rf /var/lib/apt/lists/*

    if apt-get update -qq; then
        log_success "Package cache updated successfully"
        return 0
    else
        log_error "Failed to update package cache"
        return 1
    fi
}

install_packages() {
    local packages=("$@")

    if [ ${#packages[@]} -eq 0 ]; then
        log_warning "No packages specified for installation"
        return 0
    fi

    log_step "Installing packages: ${packages[*]}"

    if DEBIAN_FRONTEND=noninteractive apt-get install -y "${packages[@]}"; then
        log_success "Packages installed successfully"
        return 0
    else
        log_error "Failed to install packages: ${packages[*]}"
        return 1
    fi
}

check_package_installed() {
    local package="$1"

    if dpkg -l | grep -q "^ii  $package "; then
        log_debug "Package $package is installed"
        return 0
    else
        log_debug "Package $package is not installed"
        return 1
    fi
}

install_package_if_missing() {
    local package="$1"

    if check_package_installed "$package"; then
        log_info "Package $package already installed"
        return 0
    else
        log_step "Installing missing package: $package"
        install_packages "$package"
    fi
}

add_repository() {
    local repo_line="$1"
    local keyserver="$2"
    local key_id="$3"

    log_step "Adding repository: $repo_line"

    # Add GPG key if provided
    if [ -n "$keyserver" ] && [ -n "$key_id" ]; then
        log_step "Adding GPG key from $keyserver"
        if ! apt-key adv --keyserver "$keyserver" --recv-keys "$key_id"; then
            log_error "Failed to add GPG key"
            return 1
        fi
    fi

    # Add repository
    if ! add-apt-repository -y "$repo_line"; then
        log_error "Failed to add repository"
        return 1
    fi

    log_success "Repository added successfully"
    return 0
}

# =================================================================
# SERVICE MANAGEMENT FUNCTIONS
# =================================================================

check_service_active() {
    local service="$1"

    if systemctl is-active --quiet "$service"; then
        log_debug "Service $service is active"
        return 0
    else
        log_debug "Service $service is not active"
        return 1
    fi
}

check_service_enabled() {
    local service="$1"

    if systemctl is-enabled --quiet "$service"; then
        log_debug "Service $service is enabled"
        return 0
    else
        log_debug "Service $service is not enabled"
        return 1
    fi
}

start_and_enable_service() {
    local service="$1"

    log_step "Starting and enabling service: $service"

    if ! systemctl enable "$service"; then
        log_error "Failed to enable service: $service"
        return 1
    fi

    if ! systemctl start "$service"; then
        log_error "Failed to start service: $service"
        return 1
    fi

    # Verify service is running
    sleep 2
    if check_service_active "$service"; then
        log_success "Service $service started and enabled successfully"
        return 0
    else
        log_error "Service $service failed to start properly"
        return 1
    fi
}

restart_service() {
    local service="$1"

    log_step "Restarting service: $service"

    if systemctl restart "$service"; then
        sleep 2
        if check_service_active "$service"; then
            log_success "Service $service restarted successfully"
            return 0
        else
            log_error "Service $service failed to restart properly"
            return 1
        fi
    else
        log_error "Failed to restart service: $service"
        return 1
    fi
}

# =================================================================
# CONFIGURATION MANAGEMENT FUNCTIONS
# =================================================================

apply_external_config() {
    local config_type="$1"
    local source_file="$2"
    local target_file="$3"
    local description="${4:-$config_type}"

    if [ ! -f "$source_file" ]; then
        log_error "$description configuration not found: $source_file"
        return 1
    fi

    log_step "Applying $description configuration"

    # Backup existing file if it exists
    if [ -f "$target_file" ]; then
        backup_file "$target_file"
    fi

    if cp "$source_file" "$target_file"; then
        log_success "$description configuration applied"
        return 0
    else
        log_error "Failed to apply $description configuration"
        return 1
    fi
}

load_external_config() {
    local config_type="$1"
    local target_file="$2"
    local substitutions="${3:-}"
    local project_root="${PROJECT_ROOT:-/vagrant}"

    local source_file="$project_root/config/$config_type"

    if [ ! -f "$source_file" ]; then
        log_error "Configuration file not found: $source_file"
        return 1
    fi

    log_step "Loading $config_type configuration"

    if [ -n "$substitutions" ]; then
        # Apply substitutions and copy
        cp "$source_file" "$target_file.tmp"

        # Process substitutions (format: "PATTERN:REPLACEMENT,PATTERN2:REPLACEMENT2")
        IFS=',' read -ra SUBS <<< "$substitutions"
        for sub in "${SUBS[@]}"; do
            if [[ "$sub" == *":"* ]]; then
                IFS=':' read -ra PAIR <<< "$sub"
                sed -i "s|${PAIR[0]}|${PAIR[1]}|g" "$target_file.tmp"
            fi
        done

        mv "$target_file.tmp" "$target_file"
    else
        # Direct copy
        cp "$source_file" "$target_file"
    fi

    log_success "Configuration loaded: $target_file"
    return 0
}

# =================================================================
# MARIADB SPECIFIC FUNCTIONS
# =================================================================

check_mariadb_installed() {
    if command -v mariadb >/dev/null 2>&1; then
        log_debug "MariaDB client found"
        return 0
    elif command -v mysql >/dev/null 2>&1; then
        log_debug "MySQL/MariaDB client found"
        return 0
    else
        log_debug "MariaDB/MySQL client not found"
        return 1
    fi
}

check_mariadb_running() {
    if check_service_active "mariadb" || check_service_active "mysql"; then
        log_debug "MariaDB/MySQL service is running"
        return 0
    else
        log_debug "MariaDB/MySQL service is not running"
        return 1
    fi
}

test_mysql_connection() {
    local user="$1"
    local password="$2"
    local database="${3:-}"

    local mysql_cmd="mysql -u $user"

    if [ -n "$password" ]; then
        mysql_cmd="$mysql_cmd -p$password"
    fi

    if [ -n "$database" ]; then
        mysql_cmd="$mysql_cmd -D $database"
    fi

    if $mysql_cmd -e "SELECT 1;" >/dev/null 2>&1; then
        log_debug "MySQL connection successful for user: $user"
        return 0
    else
        log_debug "MySQL connection failed for user: $user"
        return 1
    fi
}

check_database_exists() {
    local database="$1"
    local root_password="$2"

    if mysql -u root -p"$root_password" -e "SHOW DATABASES LIKE '$database';" 2>/dev/null | grep -q "$database"; then
        log_debug "Database $database exists"
        return 0
    else
        log_debug "Database $database does not exist"
        return 1
    fi
}

check_user_exists() {
    local username="$1"
    local root_password="$2"

    if mysql -u root -p"$root_password" -e "SELECT User FROM mysql.user WHERE User='$username';" 2>/dev/null | grep -q "$username"; then
        log_debug "User $username exists"
        return 0
    else
        log_debug "User $username does not exist"
        return 1
    fi
}

# =================================================================
# UTILITY FUNCTIONS
# =================================================================

generate_secure_password() {
    local length="${1:-32}"

    if command -v openssl >/dev/null 2>&1; then
        openssl rand -base64 "$length" | tr -d '\n'
    elif [ -f /dev/urandom ]; then
        tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "$length"
    else
        log_warning "Cannot generate secure password - using timestamp"
        echo "temp_$(date +%s)"
    fi
}

backup_file() {
    local file="$1"
    local backup_suffix="${2:-.backup.$(date +%Y%m%d_%H%M%S)}"

    if [ -f "$file" ]; then
        log_step "Backing up $file"
        if cp "$file" "${file}${backup_suffix}"; then
            log_success "Backup created: ${file}${backup_suffix}"
            return 0
        else
            log_error "Failed to backup $file"
            return 1
        fi
    else
        log_debug "File $file does not exist, no backup needed"
        return 0
    fi
}

wait_for_service() {
    local service="$1"
    local timeout="${2:-30}"
    local counter=0

    log_step "Waiting for service $service to be ready"

    while [ $counter -lt $timeout ]; do
        if check_service_active "$service"; then
            log_success "Service $service is ready"
            return 0
        fi

        sleep 1
        ((counter++))
    done

    log_error "Service $service did not become ready within $timeout seconds"
    return 1
}

# =================================================================
# VALIDATION FUNCTIONS
# =================================================================

validate_environment() {
    log_header "Environment Validation"

    local validation_errors=0

    # System checks
    if ! check_ubuntu_bionic; then
        ((validation_errors++))
    fi

    if ! check_root_privileges; then
        ((validation_errors++))
    fi

    if ! check_internet_connectivity; then
        ((validation_errors++))
    fi

    if ! check_disk_space 2; then
        ((validation_errors++))
    fi

    if ! check_memory 1024; then
        log_warning "Low memory detected, but continuing..."
    fi

    # Return validation result
    if [ $validation_errors -eq 0 ]; then
        log_success "Environment validation passed"
        return 0
    else
        log_error "Environment validation failed with $validation_errors errors"
        return 1
    fi
}

validate_mariadb_installation() {
    log_header "MariaDB Installation Validation"

    local validation_errors=0

    # Check if MariaDB is installed
    if ! check_mariadb_installed; then
        log_error "MariaDB client not installed"
        ((validation_errors++))
    fi

    # Check if service is running
    if ! check_mariadb_running; then
        log_error "MariaDB service not running"
        ((validation_errors++))
    fi

    # Check if listening on port 3306
    if ! netstat -tlnp 2>/dev/null | grep -q ":3306.*LISTEN"; then
        log_error "MariaDB not listening on port 3306"
        ((validation_errors++))
    fi

    if [ $validation_errors -eq 0 ]; then
        log_success "MariaDB validation passed"
        return 0
    else
        log_error "MariaDB validation failed with $validation_errors errors"
        return 1
    fi
}

validate_final_installation() {
    log_header "Final Installation Validation"

    local validation_errors=0

    # Validate MariaDB installation
    if ! validate_mariadb_installation; then
        ((validation_errors++))
    fi

    # Test root connectivity
    log_step "Testing root database connectivity"
    if test_mysql_connection "root" "${DB_ROOT_PASSWORD:-}" ""; then
        log_success "Root database connection: OK"
    else
        log_error "Root database connection: FAILED"
        ((validation_errors++))
    fi

    # Test application database and user
    log_step "Testing application database and user"
    if test_mysql_connection "${DB_USER:-}" "${DB_PASSWORD:-}" "${DB_NAME:-}"; then
        log_success "Application database connection: OK"
    else
        log_error "Application database connection: FAILED"
        ((validation_errors++))
    fi

    # Test phpMyAdmin if installed
    if [ "${INSTALL_PHPMYADMIN:-false}" = "true" ]; then
        log_step "Testing phpMyAdmin accessibility"
        if curl -s "http://localhost/phpmyadmin/" | grep -q "phpMyAdmin" 2>/dev/null; then
            log_success "phpMyAdmin web interface: ACCESSIBLE"
        else
            log_warning "phpMyAdmin web interface: NOT RESPONDING"
            log_info "This might be normal if Apache is still starting"
        fi
    fi

    # Report validation results
    if [ $validation_errors -eq 0 ]; then
        log_success "Final validation completed successfully"
        return 0
    else
        log_error "Final validation completed with $validation_errors errors"
        return 1
    fi
}

# =================================================================
# INITIALIZATION
# =================================================================

# Ensure logging is available
if ! command -v log_info >/dev/null 2>&1; then
    echo "ERROR: Logging functions not available. Please source logging.sh first."
    exit 1
fi

log_debug "Common functions library loaded successfully"