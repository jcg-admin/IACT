#!/bin/bash

# ============================================================================
# Environment Variables Validation Script
# Validates that required environment variables are properly set
# Enhanced for True Single Source of Truth architecture
# ============================================================================

set -euo pipefail

# Source centralized logging functions with robust path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOGGING_FUNCTIONS="$PROJECT_ROOT/infrastructure/utils/logging-functions.sh"

if [ -f "$LOGGING_FUNCTIONS" ]; then
    source "$LOGGING_FUNCTIONS"
elif [ -f "infrastructure/utils/logging-functions.sh" ]; then
    source infrastructure/utils/logging-functions.sh
else
    echo "[ERROR] Missing logging-functions.sh in expected locations"
    echo "ACTION REQUIRED: Run T006-MINI logging setup first"
    exit 1
fi

log_section "ENVIRONMENT VARIABLES VALIDATION"

# Check if .env file exists - REQUIRED in new architecture
if [ -f ".env" ]; then
    log_info "Loading environment from .env file..."
    source .env
elif [ -f ".env.development" ]; then
    log_info "Loading development environment..."
    source .env.development
else
    log_error "No environment configuration found!"
    log_error "REQUIRED: Copy .env.template to .env and configure"
    log_error "COMMAND: cp .env.template .env"
    exit 1
fi

# Required variables validation - STRICT enforcement
REQUIRED_VARS=(
    "NETWORK_SUBNET"
    "LOAD_BALANCER_IP"
    "APPLICATION_SERVER_IP"
    "HTTP_PORT"
    "HTTPS_PORT"
    "NGINX_MEMORY"
    "NGINX_CPUS"
    "TOMCAT_MEMORY"
    "TOMCAT_CPUS"
)

log_info "REQUIRED VARIABLES CHECK:"
MISSING_VARS=0

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        log_error "Required variable $var is not set"
        MISSING_VARS=$((MISSING_VARS + 1))
    else
        log_info "* $var: ${!var}"
    fi
done

if [ $MISSING_VARS -gt 0 ]; then
    log_error "$MISSING_VARS required variables are missing"
    log_error "Please copy .env.template to .env and configure required variables"
    exit 1
fi

# Network validation
log_info "NETWORK CONFIGURATION VALIDATION:"
if [[ ! "$NETWORK_SUBNET" =~ ^192\.168\.56\.0/24$ ]]; then
    log_warning "Network subnet should be 192.168.56.0/24 for compatibility"
fi

if [[ ! "$LOAD_BALANCER_IP" =~ ^192\.168\.56\. ]]; then
    log_error "Load balancer IP must be in 192.168.56.x range"
    exit 1
fi

if [[ ! "$APPLICATION_SERVER_IP" =~ ^192\.168\.56\. ]]; then
    log_error "Application server IP must be in 192.168.56.x range"
    exit 1
fi

# Resource validation
log_info "RESOURCE ALLOCATION VALIDATION:"
if [ "$NGINX_MEMORY" -lt 512 ]; then
    log_warning "nginx memory below 512MB may cause performance issues"
fi

if [ "$TOMCAT_MEMORY" -lt 1024 ]; then
    log_warning "Tomcat memory below 1GB may cause PlantUML failures"
fi

TOTAL_MEMORY=$((NGINX_MEMORY + TOMCAT_MEMORY))
log_info "* Total memory allocation: ${TOTAL_MEMORY}MB"

if [ "$TOTAL_MEMORY" -gt 4096 ]; then
    log_warning "Total memory allocation exceeds 4GB - ensure host has sufficient RAM"
fi

log_success "ENVIRONMENT VALIDATION: PASSED"
log_success "Configuration ready for True Single Source of Truth architecture"

# Display validation summary
show_validation_summary
