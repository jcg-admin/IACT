#!/bin/bash

# ============================================================================
# Network Configuration Validation Hook
# Validates network readiness for VM deployment
# Single responsibility: Network ports, connectivity, and IP validation only
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

log_section "NETWORK CONFIGURATION VALIDATION"

# Default network configuration
DEFAULT_NGINX_IP="192.168.56.11"
DEFAULT_TOMCAT_IP="192.168.56.10"
REQUIRED_PORTS=(8080 8081)

# Load network configuration from environment files
NGINX_IP="$DEFAULT_NGINX_IP"
TOMCAT_IP="$DEFAULT_TOMCAT_IP"

log_info "Loading network configuration..."

# Check for environment files and load IPs
if [ -f ".env" ]; then
    if grep -q "LOAD_BALANCER_IP" .env; then
        NGINX_IP=$(grep "LOAD_BALANCER_IP" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ' | cut -d'#' -f1)
    fi
    if grep -q "APPLICATION_SERVER_IP" .env; then
        TOMCAT_IP=$(grep "APPLICATION_SERVER_IP" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ' | cut -d'#' -f1)
    fi
    log_success "Network IPs loaded from .env: nginx=$NGINX_IP, tomcat=$TOMCAT_IP"
elif [ -f ".env.vagrant" ]; then
    if grep -q "VM_NGINX_IP" .env.vagrant; then
        NGINX_IP=$(grep "VM_NGINX_IP" .env.vagrant | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
    fi
    if grep -q "VM_TOMCAT_IP" .env.vagrant; then
        TOMCAT_IP=$(grep "VM_TOMCAT_IP" .env.vagrant | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
    fi
    log_success "Network IPs loaded from .env.vagrant: nginx=$NGINX_IP, tomcat=$TOMCAT_IP"
else
    log_info "Using default network IPs: nginx=$NGINX_IP, tomcat=$TOMCAT_IP"
fi

# Port availability validation
log_info "Checking for port conflicts..."
PORT_CONFLICTS=false

for port in "${REQUIRED_PORTS[@]}"; do
    if command -v netstat >/dev/null 2>&1; then
        if netstat -an 2>/dev/null | grep -q ":$port "; then
            log_warning "Port $port is already in use"
            PORT_CONFLICTS=true
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -an 2>/dev/null | grep -q ":$port "; then
            log_warning "Port $port is already in use"
            PORT_CONFLICTS=true
        fi
    elif command -v lsof >/dev/null 2>&1; then
        if lsof -i ":$port" >/dev/null 2>&1; then
            log_warning "Port $port is already in use"
            PORT_CONFLICTS=true
        fi
    fi
done

if [ "$PORT_CONFLICTS" = false ]; then
    log_success "Network ports: 8080, 8081 available"
else
    log_warning "Some ports are in use - may cause conflicts"
    log_warning "Stop conflicting services or change ports in environment configuration"
fi

# IP address validation
log_info "Validating configured IP addresses..."
if [[ "$NGINX_IP" =~ ^192\.168\.56\.[0-9]+$ ]]; then
    log_success "nginx IP address format valid: $NGINX_IP"
else
    log_error "nginx IP address invalid format: $NGINX_IP (should be 192.168.56.x)"
fi

if [[ "$TOMCAT_IP" =~ ^192\.168\.56\.[0-9]+$ ]]; then
    log_success "tomcat IP address format valid: $TOMCAT_IP"
else
    log_error "tomcat IP address invalid format: $TOMCAT_IP (should be 192.168.56.x)"
fi

# Check for IP conflicts
if [ "$NGINX_IP" = "$TOMCAT_IP" ]; then
    log_error "nginx and tomcat have conflicting IP addresses: $NGINX_IP"
    log_error "Configure different IP addresses in environment files"
fi

# Internet connectivity check
log_info "Checking internet connectivity..."
if command -v curl >/dev/null 2>&1; then
    if curl -s --connect-timeout 5 http://www.google.com >/dev/null 2>&1; then
        log_success "Internet connectivity: Available"
    else
        log_warning "Internet connectivity: Limited or not available"
        log_warning "Package downloads during provisioning may fail"
    fi
elif command -v wget >/dev/null 2>&1; then
    if wget -q --spider --timeout=5 http://www.google.com >/dev/null 2>&1; then
        log_success "Internet connectivity: Available"
    else
        log_warning "Internet connectivity: Limited or not available"
    fi
else
    log_warning "Internet connectivity: Unable to test (curl/wget not available)"
fi

# DNS resolution test
log_info "Testing basic DNS functionality..."
if command -v nslookup >/dev/null 2>&1; then
    if nslookup google.com >/dev/null 2>&1; then
        log_success "DNS resolution is functional"
    else
        log_warning "DNS resolution issues detected"
    fi
elif command -v dig >/dev/null 2>&1; then
    if dig google.com >/dev/null 2>&1; then
        log_success "DNS resolution is functional"
    else
        log_warning "DNS resolution issues detected"
    fi
else
    log_info "DNS resolution test skipped (no nslookup/dig available)"
fi

# Summary
show_validation_summary

if [ $VALIDATION_ERRORS -eq 0 ]; then
    log_success "Network configuration validation completed successfully"
    exit 0
else
    log_error "Network configuration validation failed"
    log_error "Network not ready for VM deployment"
    exit 1
fi
