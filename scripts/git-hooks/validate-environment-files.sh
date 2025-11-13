#!/bin/bash

# ============================================================================
# Environment Files Validation Hook
# Validates project environment setup for deployment
# Single responsibility: Environment files, Vagrantfile, and project structure only
# ============================================================================

set -euo pipefail

# Source centralized logging functions
if [ -f "infrastructure/utils/logging-functions.sh" ]; then
    source infrastructure/utils/logging-functions.sh
else
    echo "[ERROR] Missing infrastructure/utils/logging-functions.sh"
    echo "ACTION REQUIRED: Run T006-MINI logging setup first"
    exit 1
fi

log_section "ENVIRONMENT CONFIGURATION VALIDATION"

# Vagrantfile validation
log_info "Validating Vagrantfile..."
if [ -f "Vagrantfile" ]; then
    log_success "Vagrantfile exists"
    
    # Basic syntax validation
    if vagrant validate >/dev/null 2>&1; then
        log_success "Vagrantfile syntax is valid"
    else
        log_error "Vagrantfile has syntax errors detected"
        log_error "Run 'vagrant validate' for details"
    fi
    
    # Check for dual-machine configuration
    if grep -q "nginx01" Vagrantfile && grep -q "tomcat01" Vagrantfile; then
        log_success "Dual-machine VM configuration detected"
    else
        log_error "Missing nginx01 or tomcat01 VM configuration"
        log_error "Ensure both VMs are defined in Vagrantfile"
    fi
    
    # Check for port forwarding
    if grep -q "forwarded_port.*8080\|host.*8080" Vagrantfile; then
        log_success "Port forwarding configuration detected"
    else
        log_warning "Port forwarding configuration not found"
    fi
else
    log_error "Vagrantfile not found"
    log_error "Run T002 to create basic Vagrantfile"
fi

# Environment configuration validation
ENV_FILE_FOUND=false

# Check for .env file (complete configuration)
if [ -f ".env" ]; then
    log_success "Environment file .env found (complete configuration)"
    ENV_FILE_FOUND=true
    
    if [ -r ".env" ]; then
        log_success ".env is readable"
    else
        log_error ".env is not readable - check file permissions"
    fi
    
    # Validate key variables from .env
    KEY_VARS=("LOAD_BALANCER_IP" "APPLICATION_SERVER_IP" "NGINX_MEMORY" "TOMCAT_MEMORY")
    for var in "${KEY_VARS[@]}"; do
        if grep -q "^$var=" .env; then
            VALUE=$(grep "^$var=" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ' | cut -d'#' -f1)
            if [ -n "$VALUE" ]; then
                log_success "Variable $var defined: $VALUE"
            else
                log_error "Variable $var is empty in .env"
            fi
        else
            log_warning "Variable $var not found in .env"
        fi
    done
    
    # Validate resource allocation
    if grep -q "NGINX_MEMORY" .env && grep -q "TOMCAT_MEMORY" .env; then
        NGINX_MEM=$(grep "NGINX_MEMORY" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ' | cut -d'#' -f1 || echo "1024")
        TOMCAT_MEM=$(grep "TOMCAT_MEMORY" .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ' | cut -d'#' -f1 || echo "2048")
        TOTAL_MEMORY=$((NGINX_MEM + TOMCAT_MEM))
        if [ "$TOTAL_MEMORY" -le 4096 ]; then
            log_success "VM memory allocation: ${TOTAL_MEMORY}MB total"
        else
            log_warning "VM memory allocation: ${TOTAL_MEMORY}MB (high usage)"
        fi
    fi

# Check for .env.vagrant file (basic configuration)
elif [ -f ".env.vagrant" ]; then
    log_success "Environment file .env.vagrant found (basic configuration)"
    ENV_FILE_FOUND=true
    
    if [ -r ".env.vagrant" ]; then
        log_success ".env.vagrant is readable"
    else
        log_error ".env.vagrant is not readable - check file permissions"
    fi
    
    # Validate required vagrant variables
    VAGRANT_VARS=("VM_NGINX_IP" "VM_TOMCAT_IP" "VM_NGINX_MEMORY" "VM_TOMCAT_MEMORY")
    for var in "${VAGRANT_VARS[@]}"; do
        if grep -q "^$var=" .env.vagrant; then
            VALUE=$(grep "^$var=" .env.vagrant | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr -d ' ')
            if [ -n "$VALUE" ]; then
                log_success "Variable $var defined: $VALUE"
            else
                log_error "Variable $var is empty in .env.vagrant"
            fi
        else
            log_error "Variable $var missing from .env.vagrant"
        fi
    done
fi

if [ "$ENV_FILE_FOUND" = false ]; then
    log_error "No environment configuration file found"
    log_error "Required: .env or .env.vagrant with configuration variables"
fi

# Project structure validation
log_info "Validating project directory structure..."
REQUIRED_DIRS=("infrastructure" "infrastructure/hooks" "test" "docs")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        log_success "Required directory exists: $dir"
    else
        log_error "Missing required directory: $dir"
        log_error "Run T001 to create project structure"
    fi
done

# Git repository validation
log_info "Validating Git repository status..."
if [ -d ".git" ]; then
    log_success "Git repository detected"
    
    if git rev-parse --git-dir >/dev/null 2>&1; then
        log_success "Git repository is functional"
        
        if [ -f ".gitignore" ]; then
            log_success ".gitignore exists"
            
            # Check for essential patterns
            if grep -q "\.vagrant" .gitignore && grep -q "\.env" .gitignore; then
                log_success ".gitignore contains essential patterns"
            else
                log_warning ".gitignore may be missing essential patterns"
            fi
        else
            log_warning ".gitignore not found - run T003 for Git configuration"
        fi
        
        # Check git user configuration
        if git config --get user.name >/dev/null 2>&1 && git config --get user.email >/dev/null 2>&1; then
            log_success "Git user configuration is set"
        else
            log_warning "Git user configuration not set"
        fi
    else
        log_error "Git repository is corrupted"
    fi
else
    log_warning "Not a Git repository - run T001 for repository setup"
fi

# Summary
show_validation_summary

if [ $VALIDATION_ERRORS -eq 0 ]; then
    log_success "Environment configuration validation completed successfully"
    exit 0
else
    log_error "Environment configuration validation failed"
    log_error "Project environment not ready for deployment"
    exit 1
fi
