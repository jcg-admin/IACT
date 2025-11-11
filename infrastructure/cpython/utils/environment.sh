#!/bin/bash
# utils/environment.sh - CPython Builder Environment System
# Purpose: Centralized loading of all utility modules and project environment setup
# Pattern: Inspired by generate's core.sh with Clean Code naming

set -euo pipefail

# =============================================================================
# GUARD AGAINST MULTIPLE SOURCING
# =============================================================================

if [[ -n "${_ENVIRONMENT_SH_LOADED:-}" ]]; then
    return 0
fi
readonly _ENVIRONMENT_SH_LOADED=1

# =============================================================================
# INITIALIZATION
# =============================================================================

ENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# =============================================================================
# INTERNAL MODULE LOADING
# =============================================================================

_load_module() {
    local module="$1"
    local module_path="$ENV_DIR/$module"

    if [[ ! -f "$module_path" ]]; then
        echo "CRITICAL: Module not found: $module_path" >&2
        return 1
    fi

    source "$module_path"
    return 0
}

# =============================================================================
# LOAD ALL MODULES IN DEPENDENCY ORDER
# =============================================================================

# Core module (no dependencies)
_load_module "logger.sh" || return 1

# Dependent modules (require logger)
_load_module "validator.sh" || return 1
_load_module "filesystem.sh" || return 1
_load_module "network.sh" || return 1
_load_module "name_parser.sh" || return 1
_load_module "retry_handler.sh" || return 1
_load_module "state_manager.sh" || return 1

# =============================================================================
# PROJECT ENVIRONMENT SETUP
# =============================================================================

load_project_environment() {
    # Setup project paths
    export PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"
    export BUILD_STATE_DIR="${BUILD_STATE_DIR:-$PROJECT_ROOT/.build_state}"

    # Setup logging configuration
    export LOG_FILE="${LOG_FILE:-}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"

    # Initialize state management if function is available
    if command -v initialize_state_directory >/dev/null 2>&1; then
        initialize_state_directory
    fi

    return 0
}

# Auto-initialize environment on source
load_project_environment

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

environment_version() {
    echo "CPython Builder Environment v2.0.0"
}

environment_info() {
    cat << EOF
CPython Builder Environment System

Loaded from: $ENV_DIR

Available modules:
  - logger          Logging with timestamps, no colors
  - validator       Validation functions (commands, files, dirs)
  - filesystem      File and directory operations
  - network         Download and connectivity checks
  - name_parser     Artifact naming and parsing
  - retry_handler   Retry logic with exponential backoff
  - state_manager   Build state tracking (idempotency)

Project configuration:
  PROJECT_ROOT:     $PROJECT_ROOT
  BUILD_STATE_DIR:  $BUILD_STATE_DIR
  LOG_LEVEL:        $LOG_LEVEL
  LOG_FILE:         ${LOG_FILE:-<none>}

Usage in scripts:
  source utils/environment.sh
  # All modules loaded automatically
  # Environment variables configured
  # Ready to use all functions

EOF
}

# =============================================================================
# COMPATIBILITY ALIASES
# =============================================================================

# Backward compatibility with loader.sh
load_utils() {
    load_project_environment "$@"
}

# Alternative name for consistency with generate pattern
load_core_system() {
    load_project_environment "$@"
}
