#!/bin/bash
# ssl.sh
# SSL/HTTPS configuration script
# Version: 1.0.2 - Uses SSL variables from Vagrantfile

set -euo pipefail

# Load utilities
source /vagrant/utils/core.sh
source /vagrant/utils/logging.sh
source /vagrant/utils/network.sh
source /vagrant/utils/validation.sh

# Main function
main() {
    log_header "SSL/HTTPS Configuration"

    # Validate running as root
    if ! validate_root; then
        log_fatal "This script must be run as root"
    fi

    # Validate required variables
    require_vars ADMINER_IP SSL_DAYS SSL_COUNTRY SSL_STATE SSL_CITY SSL_ORG SSL_OU SSL_CN

    # Ensure log directory
    if ! ensure_dir /vagrant/logs; then
        log_error "Failed to create log directory"
        return 1
    fi

    # Generate SSL certificate
    if ! generate_ssl_certificate; then
        log_error "Failed to generate SSL certificate"
        return 1
    fi

    # Configure Apache SSL VirtualHost
    if ! configure_ssl_vhost; then
        log_error "Failed to configure SSL VirtualHost"
        return 1
    fi

    # Enable SSL site
    if ! enable_ssl_site; then
        log_error "Failed to enable SSL site"
        return 1
    fi

    log_success "SSL/HTTPS configuration completed"
    return 0
}

# Generate self-signed SSL certificate
generate_ssl_certificate() {
    log_info "Generating self-signed SSL certificate"

    local ssl_dir="/etc/ssl/private"
    local cert_file="${ssl_dir}/adminer.crt"
    local key_file="${ssl_dir}/adminer.key"

    # Ensure SSL directory exists
    if ! ensure_dir "$ssl_dir"; then
        log_error "Failed to create SSL directory"
        return 1
    fi

    # Check if certificate already exists
    if [[ -f "$cert_file" ]] && [[ -f "$key_file" ]]; then
        log_warn "SSL certificate already exists, skipping generation"
        return 0
    fi

    # Generate certificate
    log_info "Creating 2048-bit RSA certificate valid for ${SSL_DAYS} days"

    if ! openssl req -x509 -nodes -days "${SSL_DAYS}" -newkey rsa:2048 \
        -keyout "$key_file" \
        -out "$cert_file" \
        -subj "/C=${SSL_COUNTRY}/ST=${SSL_STATE}/L=${SSL_CITY}/O=${SSL_ORG}/OU=${SSL_OU}/CN=${SSL_CN}" \
        >/dev/null 2>&1; then
        log_error "Failed to generate SSL certificate"
        return 1
    fi

    # Set permissions
    log_info "Setting permissions on certificate files"
    chmod 600 "$key_file"
    chmod 644 "$cert_file"

    # Verify files exist
    if ! validate_file_exists "$cert_file"; then
        log_error "Certificate file not found after generation"
        return 1
    fi

    if ! validate_file_exists "$key_file"; then
        log_error "Key file not found after generation"
        return 1
    fi

    log_success "SSL certificate generated successfully"
    log_info "Certificate: $cert_file"
    log_info "Key: $key_file"

    return 0
}

# Configure Apache SSL VirtualHost
configure_ssl_vhost() {
    log_info "Configuring Apache SSL VirtualHost"

    local ssl_vhost_config="/etc/apache2/sites-available/adminer-ssl.conf"
    local ssl_template="/vagrant/config/vhost_ssl.conf"

    # Check if configuration template exists
    if [[ ! -f "$ssl_template" ]]; then
        log_error "SSL VirtualHost template not found: $ssl_template"
        return 1
    fi

    # Copy template to sites-available
    log_info "Creating SSL VirtualHost configuration"
    if ! cp "$ssl_template" "$ssl_vhost_config"; then
        log_error "Failed to copy SSL VirtualHost configuration"
        return 1
    fi

    # Verify the copied file exists and is readable
    if ! validate_file_exists "$ssl_vhost_config"; then
        log_error "SSL VirtualHost config not found after copy"
        return 1
    fi

    # Show the configuration for debugging
    log_info "SSL VirtualHost configuration:"
    log_info "---"
    cat "$ssl_vhost_config" | head -20
    log_info "---"

    # Test configuration syntax BEFORE enabling
    log_info "Testing Apache configuration syntax"
    if ! apachectl configtest 2>&1 | tee /tmp/apache_ssl_test.log; then
        log_error "Apache configuration syntax test failed"
        log_error "Configuration errors:"
        cat /tmp/apache_ssl_test.log
        log_error "SSL VirtualHost content:"
        cat "$ssl_vhost_config"
        return 1
    fi

    log_success "SSL VirtualHost configured and syntax validated"
    return 0
}

# Enable SSL site and restart Apache
enable_ssl_site() {
    log_info "Enabling SSL site"

    # Ensure SSL module is enabled
    log_info "Ensuring SSL module is enabled"
    if ! a2enmod ssl >/dev/null 2>&1; then
        log_warn "Failed to enable SSL module (may already be enabled)"
    else
        log_success "SSL module enabled"
    fi

    # Enable SSL site
    log_info "Enabling adminer-ssl.conf site"
    if ! a2ensite adminer-ssl.conf >/dev/null 2>&1; then
        log_error "Failed to enable SSL site"
        return 1
    fi

    # Test configuration again after enabling
    log_info "Testing Apache configuration after enabling SSL site"
    if ! apachectl configtest 2>&1 | tee /tmp/apache_ssl_final_test.log; then
        log_error "Apache configuration test failed after enabling SSL site"
        log_error "Configuration errors:"
        cat /tmp/apache_ssl_final_test.log
        log_error "Disabling SSL site to prevent Apache from failing"
        a2dissite adminer-ssl.conf >/dev/null 2>&1 || true
        return 1
    fi

    # Reload Apache to apply changes
    log_info "Reloading Apache to apply SSL configuration"
    if ! systemctl reload apache2 2>&1; then
        log_warn "Failed to reload Apache, attempting restart"

        if ! systemctl restart apache2 2>&1; then
            log_error "Failed to restart Apache"
            log_error "Apache status:"
            systemctl status apache2 --no-pager || true
            log_error "Apache error log (last 30 lines):"
            tail -30 /var/log/apache2/error.log 2>/dev/null || true
            log_error "Checking Apache configuration:"
            apachectl configtest 2>&1 || true
            return 1
        fi
    fi

    # Wait a moment for Apache to fully restart
    sleep 3

    # Verify Apache is running
    if ! systemctl is-active --quiet apache2; then
        log_error "Apache is not running after restart"
        log_error "Apache status:"
        systemctl status apache2 --no-pager || true
        return 1
    fi

    log_success "Apache is running"

    # Wait for HTTPS to be ready
    log_info "Waiting for HTTPS service to be ready"

    if ! wait_for_port "localhost" 443 30; then
        log_warn "HTTPS port did not open within 30 seconds"
        log_info "Checking listening ports:"
        netstat -tlnp | grep -E ":(80|443)" || true
    else
        log_success "HTTPS service is ready on port 443"
    fi

    # Verify HTTPS is accessible (may fail due to self-signed certificate)
    log_info "Testing HTTPS access"
    local http_code
    http_code=$(curl -k -s -o /dev/null -w "%{http_code}" https://localhost 2>/dev/null || echo "000")

    if [[ "$http_code" == "200" ]]; then
        log_success "HTTPS is accessible (HTTP 200)"
    elif [[ "$http_code" != "000" ]]; then
        log_warn "HTTPS responded with HTTP $http_code (may be acceptable)"
    else
        log_warn "HTTPS may not be fully accessible (self-signed certificate warnings expected)"
    fi

    log_success "SSL site enabled"
    return 0
}

# Note: main() is called by bootstrap.sh, not auto-executed