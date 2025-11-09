#!/bin/bash
# utils/network.sh - Network operations for CPython Builder
# Reference: SPEC_INFRA_001
# Purpose: File download, connectivity checks, and network utilities

set -euo pipefail

# =============================================================================
# DEPENDENCIES
# =============================================================================

# Note: SCRIPT_DIR may be set by calling script, so don't mark as readonly
if [[ -z "${SCRIPT_DIR:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "$SCRIPT_DIR/logger.sh"
source "$SCRIPT_DIR/validator.sh"

# =============================================================================
# CONSTANTS
# =============================================================================

readonly DEFAULT_DOWNLOAD_TIMEOUT=300
readonly DEFAULT_DOWNLOAD_RETRIES=3
readonly DEFAULT_CONNECTIVITY_HOST="8.8.8.8"

# =============================================================================
# FILE DOWNLOAD
# =============================================================================

# Download file using wget or curl
# Args: $1 - URL, $2 - destination path
# Returns: 0 on success, 1 on failure
# Example: download_file "https://example.com/file.tgz" "/tmp/file.tgz"
download_file() {
    local url="$1"
    local dest="$2"

    log_info "Downloading: $url"
    log_debug "Destination: $dest"

    # Validate URL format
    if [[ ! "$url" =~ ^https?:// ]]; then
        log_error "Invalid URL format: $url"
        return 1
    fi

    # Ensure destination directory exists
    local dest_dir
    dest_dir=$(dirname "$dest")
    if [[ ! -d "$dest_dir" ]]; then
        if ! mkdir -p "$dest_dir" 2>/dev/null; then
            log_error "Cannot create destination directory: $dest_dir"
            return 1
        fi
    fi

    # Try wget first, then curl
    if command -v wget >/dev/null 2>&1; then
        if wget -q --show-progress --timeout="$DEFAULT_DOWNLOAD_TIMEOUT" -O "$dest" "$url" 2>&1; then
            log_info "Download completed successfully"
            return 0
        else
            local exit_code=$?
            log_error "wget failed with exit code: $exit_code"
            return 1
        fi
    elif command -v curl >/dev/null 2>&1; then
        if curl -fsSL --max-time "$DEFAULT_DOWNLOAD_TIMEOUT" -o "$dest" "$url" 2>&1; then
            log_info "Download completed successfully"
            return 0
        else
            local exit_code=$?
            log_error "curl failed with exit code: $exit_code"
            return 1
        fi
    else
        log_error "Neither wget nor curl available for download"
        return 1
    fi
}

# Download file with automatic retry
# Args: $1 - URL, $2 - destination path, $3 - optional max retries (default 3)
# Returns: 0 on success, 1 on failure after retries
# Example: download_file_with_retry "https://example.com/file.tgz" "/tmp/file.tgz" 5
download_file_with_retry() {
    local url="$1"
    local dest="$2"
    local max_retries="${3:-$DEFAULT_DOWNLOAD_RETRIES}"

    # Load retry handler if available
    if [[ -f "$SCRIPT_DIR/retry_handler.sh" ]]; then
        source "$SCRIPT_DIR/retry_handler.sh"
        execute_with_retry "$max_retries" "Download file" download_file "$url" "$dest"
        return $?
    fi

    # Fallback: simple retry logic
    local attempt=0
    while (( attempt < max_retries )); do
        attempt=$((attempt + 1))

        log_info "Download attempt $attempt/$max_retries"

        if download_file "$url" "$dest"; then
            return 0
        fi

        if (( attempt < max_retries )); then
            local delay=$((attempt * 5))
            log_warning "Download failed, retrying in ${delay}s..."
            sleep "$delay"
        fi
    done

    log_error "Download failed after $max_retries attempts"
    return 1
}

# Download file with checksum verification
# Args: $1 - URL, $2 - destination, $3 - checksum URL
# Returns: 0 on success, 1 on failure
# Example: download_file_with_checksum "https://example.com/file.tgz" "/tmp/file.tgz" "https://example.com/file.tgz.sha256"
download_file_with_checksum() {
    local file_url="$1"
    local dest="$2"
    local checksum_url="$3"

    local checksum_file="${dest}.sha256"

    # Download main file
    if ! download_file_with_retry "$file_url" "$dest"; then
        return 1
    fi

    # Download checksum
    if ! download_file "$checksum_url" "$checksum_file"; then
        log_error "Failed to download checksum"
        return 1
    fi

    # Verify checksum
    if ! validate_sha256_checksum "$dest" "$checksum_file"; then
        log_error "Checksum verification failed"
        rm -f "$dest" "$checksum_file"
        return 1
    fi

    log_info "File downloaded and verified successfully"
    rm -f "$checksum_file"
    return 0
}

# =============================================================================
# CONNECTIVITY CHECKS
# =============================================================================

# Check network connectivity
# Args: $1 - optional host to test (default 8.8.8.8)
# Returns: 0 if connected, 1 if not
# Example: check_network_connectivity "google.com"
check_network_connectivity() {
    local host="${1:-$DEFAULT_CONNECTIVITY_HOST}"

    log_debug "Checking network connectivity (host: $host)"

    if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
        log_debug "Network connectivity OK"
        return 0
    fi

    log_error "No network connectivity to $host"
    return 1
}

# Wait for network connectivity
# Args: $1 - optional max wait seconds (default 60), $2 - optional host
# Returns: 0 if connected within timeout, 1 if timeout
# Example: wait_for_network_connectivity 120 "google.com"
wait_for_network_connectivity() {
    local max_wait="${1:-60}"
    local host="${2:-$DEFAULT_CONNECTIVITY_HOST}"

    log_info "Waiting for network connectivity (max ${max_wait}s)..."

    local elapsed=0
    while (( elapsed < max_wait )); do
        if check_network_connectivity "$host"; then
            log_info "Network connectivity established after ${elapsed}s"
            return 0
        fi

        sleep 2
        elapsed=$((elapsed + 2))

        if (( elapsed % 10 == 0 )); then
            log_debug "Still waiting for connectivity... (${elapsed}s elapsed)"
        fi
    done

    log_error "Network connectivity timeout after ${max_wait}s"
    return 1
}

# Test URL reachability
# Args: $1 - URL to test
# Returns: 0 if reachable, 1 if not
# Example: test_url_reachable "https://www.python.org"
test_url_reachable() {
    local url="$1"

    log_debug "Testing URL reachability: $url"

    if command -v curl >/dev/null 2>&1; then
        if curl -fsSL --head --max-time 10 "$url" >/dev/null 2>&1; then
            log_debug "URL reachable: $url"
            return 0
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget --spider --timeout=10 -q "$url" 2>/dev/null; then
            log_debug "URL reachable: $url"
            return 0
        fi
    else
        log_warning "Cannot test URL (no curl or wget available)"
        return 1
    fi

    log_error "URL not reachable: $url"
    return 1
}

# =============================================================================
# NETWORK INFORMATION
# =============================================================================

# Get public IP address
# Returns: Public IP via stdout, empty on failure
# Example: public_ip=$(get_public_ip_address)
get_public_ip_address() {
    local ip=""

    # Try multiple services
    local services=(
        "https://api.ipify.org"
        "https://ifconfig.me/ip"
        "https://icanhazip.com"
    )

    for service in "${services[@]}"; do
        if command -v curl >/dev/null 2>&1; then
            ip=$(curl -fsSL --max-time 5 "$service" 2>/dev/null || echo "")
        elif command -v wget >/dev/null 2>&1; then
            ip=$(wget -qO- --timeout=5 "$service" 2>/dev/null || echo "")
        fi

        if [[ -n "$ip" ]]; then
            echo "$ip"
            return 0
        fi
    done

    log_debug "Could not determine public IP"
    echo ""
    return 1
}

# Get default network interface
# Returns: Interface name via stdout, empty on failure
# Example: interface=$(get_default_network_interface)
get_default_network_interface() {
    local interface
    interface=$(ip route | grep default | awk '{print $5}' | head -1 2>/dev/null || echo "")

    if [[ -n "$interface" ]]; then
        echo "$interface"
        return 0
    fi

    log_debug "Could not determine default network interface"
    echo ""
    return 1
}

# =============================================================================
# BANDWIDTH AND SPEED TESTING
# =============================================================================

# Estimate download speed
# Args: $1 - test URL (small file), $2 - optional timeout (default 10)
# Returns: Speed in KB/s via stdout, 0 on failure
# Example: speed=$(estimate_download_speed "https://example.com/1mb.bin")
estimate_download_speed() {
    local test_url="$1"
    local timeout="${2:-10}"

    local temp_file
    temp_file=$(mktemp)

    local start_time
    start_time=$(date +%s)

    if command -v curl >/dev/null 2>&1; then
        if ! curl -fsSL --max-time "$timeout" -o "$temp_file" "$test_url" 2>/dev/null; then
            rm -f "$temp_file"
            echo "0"
            return 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if ! wget -q --timeout="$timeout" -O "$temp_file" "$test_url" 2>/dev/null; then
            rm -f "$temp_file"
            echo "0"
            return 1
        fi
    else
        rm -f "$temp_file"
        echo "0"
        return 1
    fi

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    if (( elapsed == 0 )); then
        elapsed=1
    fi

    local file_size
    file_size=$(stat -c %s "$temp_file" 2>/dev/null || echo 0)
    rm -f "$temp_file"

    local speed_kbs=$((file_size / 1024 / elapsed))
    echo "$speed_kbs"
    return 0
}

# =============================================================================
# DNS UTILITIES
# =============================================================================

# Resolve hostname to IP
# Args: $1 - hostname
# Returns: IP address via stdout, empty on failure
# Example: ip=$(resolve_hostname_to_ip "www.python.org")
resolve_hostname_to_ip() {
    local hostname="$1"

    local ip
    ip=$(getent hosts "$hostname" 2>/dev/null | awk '{print $1}' | head -1 || echo "")

    if [[ -n "$ip" ]]; then
        echo "$ip"
        return 0
    fi

    log_debug "Could not resolve hostname: $hostname"
    echo ""
    return 1
}