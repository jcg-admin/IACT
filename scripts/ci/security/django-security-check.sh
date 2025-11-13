#!/bin/bash
# django-security-check.sh
#
# Django Security Check
# Replica: Security Scan / Django Security Check
#
# Exit codes:
#   0 - Security check passed
#   1 - Security issues found

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

log_info "Running Django security check..."

cd "$PROJECT_ROOT/api/callcentersite"

# Activar entorno virtual si existe
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

ISSUES_FOUND=0

# Check 1: Django check --deploy
log_info "Running: python manage.py check --deploy"
if python3 manage.py check --deploy 2>&1 | tee /tmp/django_check.log; then
    log_info "Django deployment checks passed"
else
    log_error "Django deployment checks failed"
    cat /tmp/django_check.log
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check 2: Settings security
log_info "Checking security settings..."
SETTINGS_FILE="callcentersite/settings.py"

# Check DEBUG setting
if grep -q "DEBUG = True" "$SETTINGS_FILE"; then
    log_error "DEBUG is True - should be False in production"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    log_info "DEBUG setting: OK"
fi

# Check SECRET_KEY not hardcoded
if grep -q 'SECRET_KEY = "[^"]*"' "$SETTINGS_FILE"; then
    log_warn "SECRET_KEY may be hardcoded - should use environment variable"
fi

# Check SECURE_SSL_REDIRECT
if grep -q "SECURE_SSL_REDIRECT = True" "$SETTINGS_FILE"; then
    log_info "SECURE_SSL_REDIRECT: Enabled"
else
    log_warn "SECURE_SSL_REDIRECT: Not enabled"
fi

# Check SESSION_COOKIE_SECURE
if grep -q "SESSION_COOKIE_SECURE = True" "$SETTINGS_FILE"; then
    log_info "SESSION_COOKIE_SECURE: Enabled"
else
    log_warn "SESSION_COOKIE_SECURE: Not enabled"
fi

# Check CSRF_COOKIE_SECURE
if grep -q "CSRF_COOKIE_SECURE = True" "$SETTINGS_FILE"; then
    log_info "CSRF_COOKIE_SECURE: Enabled"
else
    log_warn "CSRF_COOKIE_SECURE: Not enabled"
fi

# Check 3: SQL Injection patterns
log_info "Scanning for SQL injection patterns..."
if grep -r "\.raw(" --include="*.py" "$PROJECT_ROOT/api/callcentersite" | grep -v migrations | grep -v ".pyc"; then
    log_warn "Found .raw() SQL queries - review for SQL injection risk"
fi

# Summary
echo ""
if [ $ISSUES_FOUND -eq 0 ]; then
    log_info "Django security check passed"
    exit 0
else
    log_error "Found $ISSUES_FOUND security issues"
    exit 1
fi
