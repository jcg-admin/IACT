#!/bin/bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"


# Detect if running in Vagrant environment
if [ -d "/vagrant" ]; then
    PROJECT_ROOT="/vagrant"
fi

# Configuration
LOGS_DIR="${LOGS_DIR:-$PROJECT_ROOT/logs}"
DEBUG="${DEBUG:-false}"

# Export variables for child scripts
export LOGS_DIR DEBUG

# =================================================================
# LOAD DEPENDENCIES
# =================================================================

load_utility() {
  local util_file="$1"
  local util_path="$PROJECT_ROOT/utils/$util_file"

  if [ -f "$util_path" ]; then
      source "$util_path"
  else
      echo "ERROR: Required utility not found: $util_path"
      exit 1
  fi
}

# Load required utilities
load_utility "logging.sh"
load_utility "common.sh"

apply_external_config() {
  local config_type="$1"
  local source_file="$PROJECT_ROOT/config/$config_type"
  local target_file="$2"
  local description="${3:-$config_type}"

  if [ ! -f "$source_file" ]; then
      log_error "$description configuration not found: $source_file"
      return 1
  fi

  log_step "Applying $description configuration"
  if cp "$source_file" "$target_file"; then
      log_success "$description configuration applied"
      return 0
  else
      log_error "Failed to apply $description configuration"
      return 1
  fi
}


configure_system_base() {
  log_header "System Base Configuration"

  # Apply APT sources configuration
  if ! apply_external_config "apt/sources.list" "/etc/apt/sources.list" "APT sources"; then
      return 1
  fi

  # Apply DNS configurations
  if ! apply_external_config "systemd/resolved.conf" "/etc/systemd/resolved.conf" "systemd-resolved"; then
      return 1
  fi

  if ! apply_external_config "network/resolv.conf" "/etc/resolv.conf" "resolv.conf backup"; then
      return 1
  fi

  # Restart DNS service using common.sh function
  if ! restart_service "systemd-resolved"; then
      log_warning "Failed to restart systemd-resolved service"
  fi

  # Update package system using common.sh function
  if ! update_package_cache; then
      log_error "Package cache update failed"
      return 1
  fi

  log_success "System base configuration completed successfully"
  return 0
}

# =================================================================
# BOOTSTRAP ORCHESTRATION FUNCTIONS
# =================================================================

show_bootstrap_header() {
  log_header "MariaDB + phpMyAdmin Bootstrap"
  log_info "Target System: Ubuntu 18.04 LTS (Bionic Beaver)"
  log_info "Project Root: $PROJECT_ROOT"
  log_info "Logs Directory: $LOGS_DIR"
  echo ""

}

show_credentials_info() {
    log_header "Database Credentials"
    log_warning "IMPORTANT: Save these credentials securely"
    log_info "These credentials are logged to: $(get_log_file)"
    echo ""
}


show_access_information() {
    log_header "Access Information"

    echo "System Information:"
    echo "  VM SSH: vagrant ssh (if using Vagrant)"
    echo "  Logs: $(get_log_file)"
    echo "  Project: $PROJECT_ROOT"
    echo ""
}

execute_installation_script() {
  local script_path="$1"
  local script_name
  script_name=$(basename "$script_path")

  log_header "Executing: $script_name"

  # Verify script exists
  if [ ! -f "$script_path" ]; then
      log_error "Script not found: $script_path"
      return 1
  fi

  # Make script executable
  if ! chmod +x "$script_path"; then
      log_error "Cannot set execute permissions: $script_path"
      return 1
  fi

  log_step "Starting execution of $script_name"

  # Execute script and capture result
  if bash "$script_path"; then
      log_success "$script_name completed successfully"
      return 0
  else
      local exit_code=$?
      log_error "$script_name failed with exit code: $exit_code"
      return $exit_code
  fi
}

prepare_installation() {
  local scripts_sequence=(
    "$PROJECT_ROOT/install/system-prepare.sh"
    "$PROJECT_ROOT/install/mariadb-install.sh"
  )

  echo "${scripts_sequence[@]}"
}

run_installation_sequence() {
  local scripts_sequence
  scripts_sequence=($(prepare_installation))

  log_info "Installation sequence prepared: ${#scripts_sequence[@]} scripts"

  # Execute each script in sequence
  for script in "${scripts_sequence[@]}"; do
      if ! execute_installation_script "$script"; then
          log_error "Installation sequence interrupted at $(basename "$script")"
          log_error "Check logs for details: $(get_log_file)"
          return 1
      fi
  done

  return 0
}

# =================================================================
# ERROR HANDLING
# =================================================================

cleanup_on_error() {
  log_error "Bootstrap interrupted by signal or error"
  log_info "Partial installation may be present"
  log_info "Check logs for details: $(get_log_file)"
  log_info "You can retry by running: $0"
  exit 1
}


# =================================================================
# MAIN EXECUTION
# =================================================================

main() {
# Setup signal handlers
trap cleanup_on_error SIGINT SIGTERM ERR

# Show bootstrap header
show_bootstrap_header

# Pre-installation validation using common.sh
log_step "Running pre-installation validation"
if ! validate_environment; then
    log_error "Pre-installation validation failed"
    log_info "Please fix the issues above and retry"
    exit 1
fi

# Configure system base using external configs
log_step "Configuring system base"
if ! configure_system_base; then
    log_error "System base configuration failed"
    exit 1
fi

# Show generated credentials
show_credentials_info

# Run the installation sequence
log_step "Starting installation sequence"
if ! run_installation_sequence; then
    log_error "Installation sequence failed"
    exit 1
fi

# Final validation using common.sh
log_step "Running final validation"
if ! validate_final_installation; then
    log_warning "Some validation checks failed"
    log_info "Installation may be partially complete"
fi

# Show access information
show_access_information

# Success message
log_header "Bootstrap Completed Successfully"
log_success "MariaDB + PostgreSQL installation completed"
log_info "All services should be running and accessible"
log_info "Credentials and access information logged to: $(get_log_file)"

return 0
}

# =================================================================
# SCRIPT EXECUTION
# =================================================================

# Ensure script is run with appropriate privileges
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run with root privileges"
    echo "Try: sudo $0"
    exit 1
fi

# Execute main function
main "$@"