#!/bin/bash
#
# cleanup.sh - Clean CPython build environment
#
# Reference: SPEC_INFRA_001
# Purpose: Enable clean builds and manage state (idempotence)
#
# Usage:
#   ./cleanup.sh [--all|--state|--help]
#

set -euo pipefail

# =============================================================================
# LOAD UTILITIES
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"

# Load environment system
load_environment() {
    local env_path="$SCRIPT_DIR/../utils/environment.sh"

    if [[ ! -f "$env_path" ]]; then
        env_path="$PROJECT_ROOT/utils/environment.sh"
    fi

    if [[ ! -f "$env_path" ]]; then
        echo "ERROR: Environment system not found" >&2
        return 1
    fi

    source "$env_path"
    return 0
}

if ! load_environment; then
    echo "ERROR: Failed to load environment system" >&2
    exit 1
fi

# =============================================================================
# CONFIGURATION
# =============================================================================

BUILD_DIR="/tmp/cpython-build"
INSTALL_PREFIX_BASE="/opt"
ARTIFACT_DIR="/vagrant/artifacts/cpython"
STATE_DIR="${BUILD_STATE_DIR:-$PROJECT_ROOT/.build_state}"

# =============================================================================
# FUNCTIONS
# =============================================================================

show_usage() {
    cat <<EOF
Usage: $0 [options]

Options:
  --all        Clean everything (builds, installations)
  --state      Clear build state (operation tracking)
  --help, -h   Show this help message

Without arguments: shows current status

Examples:
  $0                  # Show status
  $0 --all            # Clean build directories
  $0 --state          # Clear state tracking
  $0 --all --state    # Clean everything including state
EOF
    exit 0
}

show_status() {
    log_header "Build Environment Status" 73
    echo ""

    # Build directory
    if [[ -d "$BUILD_DIR" ]]; then
        local build_size
        build_size=$(get_directory_size_kb "$BUILD_DIR")
        local build_size_mb=$((build_size / 1024))
        log_info "Build directory: $BUILD_DIR (${build_size_mb} MB)"
        find "$BUILD_DIR" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | sed 's/^/  /' || true
    else
        log_info "Build directory: does not exist"
    fi
    echo ""

    # Installations
    local installs
    installs=$(find "$INSTALL_PREFIX_BASE" -maxdepth 1 -type d -name "python-*" 2>/dev/null | wc -l)
    if (( installs > 0 )); then
        log_info "Installations in $INSTALL_PREFIX_BASE: $installs"
        find "$INSTALL_PREFIX_BASE" -maxdepth 1 -type d -name "python-*" 2>/dev/null | while read -r dir; do
            local size_kb
            size_kb=$(get_directory_size_kb "$dir")
            local size_mb=$((size_kb / 1024))
            echo "  $dir (${size_mb} MB)"
        done
    else
        log_info "Installations: none"
    fi
    echo ""

    # Artifacts
    if [[ -d "$ARTIFACT_DIR" ]]; then
        local artifact_count
        artifact_count=$(find "$ARTIFACT_DIR" -name "*.tgz" 2>/dev/null | wc -l)
        if (( artifact_count > 0 )); then
            log_info "Generated artifacts: $artifact_count"
            find "$ARTIFACT_DIR" -name "*.tgz" -exec ls -lh {} \; 2>/dev/null | \
                awk '{print "  " $9 " (" $5 ")"}' || true
        else
            log_info "Artifacts: none"
        fi
    else
        log_info "Artifacts directory: does not exist"
    fi
    echo ""

    # Build state
    if state_directory_exists; then
        local completed_count
        completed_count=$(count_completed_operations)
        log_info "Build state: $completed_count completed operations"

        if (( completed_count > 0 )); then
            log_info "Recent operations:"
            list_completed_operations | tail -5 | sed 's/^/  /'
        fi
    else
        log_info "Build state: not initialized"
    fi
    echo ""

    log_separator 73
    log_info "Usage: $0 --all to clean build directories"
    log_info "       $0 --state to clear build state"
    log_info "       $0 --all --state to clean everything"
    log_separator 73
}

cleanup_build() {
    log_info "Cleaning build directories..."
    echo ""

    # Clean build directory
    if [[ -d "$BUILD_DIR" ]]; then
        local build_size_kb
        build_size_kb=$(get_directory_size_kb "$BUILD_DIR")
        local build_size_mb=$((build_size_kb / 1024))

        log_info "Removing $BUILD_DIR (${build_size_mb} MB)..."
        if remove_path_safely "$BUILD_DIR"; then
            log_info "Build directory removed"
        else
            log_error "Failed to remove build directory"
            return 1
        fi
    else
        log_info "Build directory does not exist (already clean)"
    fi
    echo ""

    # Clean installations
    log_info "Cleaning Python installations..."

    local installs
    installs=$(find "$INSTALL_PREFIX_BASE" -maxdepth 1 -type d -name "python-*" 2>/dev/null || true)

    if [[ -z "$installs" ]]; then
        log_info "No installations to clean"
    else
        local install_count
        install_count=$(echo "$installs" | wc -l)
        log_info "Found $install_count installation(s)"

        while IFS= read -r install_dir; do
            [[ -z "$install_dir" ]] && continue

            local install_size_kb
            install_size_kb=$(get_directory_size_kb "$install_dir")
            local install_size_mb=$((install_size_kb / 1024))

            log_info "Removing $install_dir (${install_size_mb} MB)..."

            if ! sudo rm -rf "$install_dir"; then
                log_error "Failed to remove $install_dir (sudo required)"
                return 1
            fi
        done <<< "$installs"

        log_info "Installations removed"
    fi
    echo ""

    log_info "Build environment cleaned successfully"
}

cleanup_state() {
    log_info "Cleaning build state..."
    echo ""

    if ! state_directory_exists; then
        log_info "State directory does not exist (already clean)"
        return 0
    fi

    local completed_count
    completed_count=$(count_completed_operations)

    if (( completed_count == 0 )); then
        log_info "No state to clean"
        return 0
    fi

    log_info "Operations tracked: $completed_count"
    log_info "State directory: $STATE_DIR"
    echo ""

    log_warning "This will clear all build state tracking"
    log_warning "You will need to rebuild from scratch"
    echo ""

    read -p "Clear build state? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cancelled by user"
        return 0
    fi

    if clear_all_state; then
        log_info "Build state cleared"
    else
        log_error "Failed to clear state"
        return 1
    fi
}

cleanup_all() {
    log_header "Complete Environment Cleanup" 73
    echo ""

    cleanup_build || return 1

    echo ""
    log_separator 73
    log_info "Cleanup completed successfully"
    log_info "Environment is ready for a clean build"
    log_separator 73
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    # No arguments: show status
    if (( $# == 0 )); then
        show_status
        exit 0
    fi

    # Parse arguments
    local do_cleanup_all=0
    local do_cleanup_state=0

    for arg in "$@"; do
        case "$arg" in
            --help|-h)
                show_usage
                ;;
            --all)
                do_cleanup_all=1
                ;;
            --state)
                do_cleanup_state=1
                ;;
            *)
                log_error "Invalid option: $arg"
                echo ""
                show_usage
                ;;
        esac
    done

    # Execute cleanup operations
    if (( do_cleanup_all == 1 )); then
        cleanup_all || exit 1
    fi

    if (( do_cleanup_state == 1 )); then
        echo ""
        cleanup_state || exit 1
    fi

    # Show final status
    if (( do_cleanup_all == 1 || do_cleanup_state == 1 )); then
        echo ""
        log_info "Updated status:"
        echo ""
        show_status
    fi
}

main "$@"