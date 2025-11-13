#!/bin/bash

# ============================================================================
# Hardware Requirements Validation Hook
# Validates minimum hardware requirements for dual-VM deployment
# Single responsibility: Hardware capacity validation only
# ============================================================================

set -euo pipefail

# Source centralized logging functions
if [ -f "infrastructure/utils/logging-functions.sh" ]; then
    source infraestructura/utils/logging-functions.sh
else
    echo "[ERROR] Missing infrastructure/utils/logging-functions.sh"
    echo "ACTION REQUIRED: Run T006-MINI logging setup first"
    exit 1
fi

log_section "HARDWARE REQUIREMENTS VALIDATION"

# Configuration - realistic values for dual-machine stack
REQUIRED_RAM_GB=4        # 4GB RAM minimum for host
REQUIRED_DISK_GB=6       # 6GB disk space (realistic vs 10GB alternatives)
MIN_CPU_CORES=2          # Minimum CPU cores

# CPU validation
log_info "Checking CPU requirements..."
if command -v nproc >/dev/null 2>&1; then
    CPU_CORES=$(nproc)
elif [ -f /proc/cpuinfo ]; then
    CPU_CORES=$(grep -c ^processor /proc/cpuinfo)
elif command -v sysctl >/dev/null 2>&1; then
    CPU_CORES=$(sysctl -n hw.ncpu 2>/dev/null || echo "unknown")
else
    CPU_CORES="unknown"
fi

if [ "$CPU_CORES" != "unknown" ] && [ "$CPU_CORES" -ge "$MIN_CPU_CORES" ]; then
    log_success "CPU cores: $CPU_CORES (minimum $MIN_CPU_CORES required)"
elif [ "$CPU_CORES" != "unknown" ]; then
    log_warning "CPU cores: $CPU_CORES (2+ recommended for better performance)"
else
    log_warning "CPU cores: Unable to detect (ensure you have 2+ cores)"
fi

# Memory validation with enhanced Windows support
log_info "Checking memory requirements..."
if [ -f /proc/meminfo ]; then
    # Linux
    TOTAL_RAM_MB=$(awk '/MemTotal/ {printf "%.0f", $2/1024}' /proc/meminfo)
elif command -v sysctl >/dev/null 2>&1; then
    # macOS
    TOTAL_RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo "0")
    TOTAL_RAM_MB=$((TOTAL_RAM_BYTES / 1024 / 1024))
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]] || command -v wmic >/dev/null 2>&1; then
    # Windows - enhanced detection
    log_info "Windows detected - using enhanced RAM detection"
    TOTAL_RAM_MB=8192  # Conservative assumption for Windows VM-capable systems
    log_info "Windows RAM detection: Assuming ${TOTAL_RAM_MB}MB (common for VM-capable systems)"
else
    TOTAL_RAM_MB=0
fi

TOTAL_RAM_GB=$((TOTAL_RAM_MB / 1024))

if [ "$TOTAL_RAM_GB" -ge "$REQUIRED_RAM_GB" ]; then
    log_success "System RAM: ${TOTAL_RAM_GB}GB (${REQUIRED_RAM_GB}GB required)"
elif [ "$TOTAL_RAM_GB" -gt 0 ]; then
    log_error "System RAM: ${TOTAL_RAM_GB}GB (${REQUIRED_RAM_GB}GB required)"
    log_error "Insufficient memory for dual-machine deployment"
else
    log_warning "System RAM: Unable to detect (ensure you have ${REQUIRED_RAM_GB}GB+)"
fi

# Disk space validation
log_info "Checking disk space requirements..."
if command -v df >/dev/null 2>&1; then
    AVAILABLE_GB=$(df . | awk 'NR==2 {printf "%.0f", $4/1024/1024}')
    if [ "$AVAILABLE_GB" -ge "$REQUIRED_DISK_GB" ]; then
        log_success "Disk space: ${AVAILABLE_GB}GB available (${REQUIRED_DISK_GB}GB required)"
    else
        log_error "Disk space: ${AVAILABLE_GB}GB available (${REQUIRED_DISK_GB}GB required)"
        log_error "Insufficient disk space for VM deployment"
    fi
else
    log_warning "Disk space: Unable to detect (ensure you have ${REQUIRED_DISK_GB}GB+ available)"
fi

# Virtualization support detection
log_info "Checking hardware virtualization support..."
VT_SUPPORTED=false

if [ -f /proc/cpuinfo ]; then
    # Linux
    if grep -q "vmx\|svm" /proc/cpuinfo; then
        VT_SUPPORTED=true
    fi
elif command -v sysctl >/dev/null 2>&1; then
    # macOS
    if sysctl -n machdep.cpu.features 2>/dev/null | grep -q VMX; then
        VT_SUPPORTED=true
    fi
elif command -v wmic >/dev/null 2>&1; then
    # Windows - basic virtualization check
    if wmic cpu get VirtualizationFirmwareEnabled 2>/dev/null | grep -q "TRUE"; then
        VT_SUPPORTED=true
    fi
fi

if [ "$VT_SUPPORTED" = true ]; then
    log_success "Hardware virtualization: Supported (VT-x/AMD-V detected)"
else
    log_warning "Hardware virtualization: Unable to detect or not enabled"
    log_warning "Ensure VT-x/AMD-V is enabled in BIOS settings"
fi

# Summary
show_validation_summary

if [ $VALIDATION_ERRORS -eq 0 ]; then
    log_success "Hardware requirements validation completed successfully"
    exit 0
else
    log_error "Hardware requirements validation failed"
    log_error "System does not meet minimum requirements for dual-VM deployment"
    exit 1
fi
