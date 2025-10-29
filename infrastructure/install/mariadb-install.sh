#!/bin/bash
set -euo pipefail

# =================================================================
# SCRIPT CONFIGURATION
# =================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Detect Vagrant environment
if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
fi

# Variables from bootstrap (with defaults)
MARIADB_VERSION="${MARIADB_VERSION:-10.6}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-rootpass123}"

# =================================================================
# LOAD DEPENDENCIES
# =================================================================

# Source required libraries
if [ -f "$PROJECT_ROOT/utils/logging.sh" ]; then
  source "$PROJECT_ROOT/utils/logging.sh"
else
  echo "ERROR: Cannot find logging.sh at $PROJECT_ROOT/utils/logging.sh"
  exit 1
fi

if [ -f "$PROJECT_ROOT/utils/common.sh" ]; then
  source "$PROJECT_ROOT/utils/common.sh"
else
  log_error "Cannot find common.sh at $PROJECT_ROOT/utils/common.sh"
  exit 1
fi

# =================================================================
# MARIADB INSTALLATION FUNCTIONS
# =================================================================
setup_mariadb_repository() {
  log_header "MariaDB Repository Setup"

  log_step "Adding MariaDB signing key"
  if ! sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8; then
      log_error "Failed to add MariaDB signing key"
      return 1
  fi

  log_step "Adding MariaDB repository for Ubuntu 18.04"
  local repo_line="deb [arch=amd64,arm64,ppc64el] https://162.55.42.214/repo/$MARIADB_VERSION/ubuntu bionic main"
  echo "$repo_line" > /etc/apt/sources.list.d/mariadb.list

  # Use centralized function instead of manual apt-get update
  if ! update_package_cache; then
      return 1
  fi

  log_success "MariaDB repository configured successfully"
  return 0
}

install_mariadb_packages() {
  log_header "MariaDB Installation"

  # Use centralized function instead of manual checks
  if check_mariadb_installed && check_mariadb_running; then
      log_success "MariaDB is already installed and running"
      return 0
  fi

  local packages=(
      "mariadb-server"
      "mariadb-client"
      "mariadb-common"
  )

  # Use centralized function instead of manual DEBIAN_FRONTEND
  if ! install_packages "${packages[@]}"; then
      log_error "Failed to install MariaDB packages"
      return 1
  fi

  return 0
}

configure_mariadb_service() {
  log_header "MariaDB Service Configuration"

  # Use centralized function instead of manual systemctl commands
  if ! start_and_enable_service "mariadb"; then
      return 1
  fi

  # Use centralized function instead of manual counter loop
  if ! wait_for_service "mariadb" 30; then
      return 1
  fi

  return 0
}

secure_mariadb_installation() {
  log_header "MariaDB Security Configuration"

  log_step "Setting root password"
  if ! mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASSWORD'; FLUSH PRIVILEGES;" 2>/dev/null; then
      # Try alternative method for fresh installations
      if ! mysqladmin -u root password "$DB_ROOT_PASSWORD" 2>/dev/null; then
          log_warning "Root password may already be set or using unix_socket"
      fi
  fi

  log_step "Removing anonymous users"
  mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='';" 2>/dev/null || true

  log_step "Disabling remote root login"
  mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');" 2>/dev/null || true

  log_step "Removing test database"
  mysql -u root -p"$DB_ROOT_PASSWORD" -e "DROP DATABASE IF EXISTS test;" 2>/dev/null || true
  mysql -u root -p"$DB_ROOT_PASSWORD" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';" 2>/dev/null || true

  log_step "Flushing privileges"
  mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>/dev/null || true

  log_success "MariaDB security configuration completed"
  return 0
}

verify_mariadb_installation() {
  log_header "MariaDB Installation Verification"

  # Use centralized validation instead of manual checks
  if ! validate_mariadb_installation; then
      return 1
  fi

  # Test root connectivity using centralized function
  if ! test_mysql_connection "root" "$DB_ROOT_PASSWORD"; then
      log_error "Cannot connect to database with root password"
      return 1
  fi

  # Show version information
  local version
  version=$(mysql -u root -p"$DB_ROOT_PASSWORD" -e "SELECT VERSION();" 2>/dev/null | tail -n 1)
  log_info "MariaDB version: $version"

  log_success "MariaDB installation verification completed"
  return 0
}

# =================================================================
# MAIN EXECUTION
# =================================================================

main() {
  log_header "MariaDB Installation - Ubuntu 18.04"
  log_info "MariaDB Version: $MARIADB_VERSION"

  # Use centralized function instead of manual EUID check
  if ! check_root_privileges; then
      log_error "root privileges setup failed"
      exit 1
  fi

  # Setup MariaDB repository
  if ! setup_mariadb_repository; then
      log_error "MariaDB repository setup failed"
      exit 1
  fi

  # Install MariaDB packages
  if ! install_mariadb_packages; then
      log_error "MariaDB package installation failed"
      exit 1
  fi

  # Configure MariaDB service
  if ! configure_mariadb_service; then
      log_error "MariaDB service configuration failed"
      exit 1
  fi

  # Secure MariaDB installation
  if ! secure_mariadb_installation; then
      log_error "MariaDB security configuration failed"
      exit 1
  fi

  # Verify installation
  if ! verify_mariadb_installation; then
      log_error "MariaDB installation verification failed"
      exit 1
  fi

  log_success "MariaDB installation completed successfully"
  log_info "Next step: Application database setup"

  return 0
}

# Execute main function
main "$@"