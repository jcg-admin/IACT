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
CHECKS_SKIPPED=0

# Check 1: Django check --deploy
log_info "Running: python manage.py check --deploy"
MANAGE_READY=true
if ! python3 -c "import django" >/dev/null 2>&1; then
    MANAGE_READY=false
    log_warn "Skipping manage.py checks: Django is not installed"
    CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
elif [ ! -f "manage.py" ]; then
    MANAGE_READY=false
    log_warn "Skipping manage.py checks: manage.py not found"
    CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
fi

if [ "$MANAGE_READY" = true ]; then
    if python3 manage.py check --deploy 2>&1 | tee /tmp/django_check.log; then
        log_info "Django deployment checks passed"
    else
        log_error "Django deployment checks failed"
        cat /tmp/django_check.log
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    log_warn "manage.py checks skipped due to missing prerequisites"
fi

# Check 2: Settings security
log_info "Checking security settings..."
SETTINGS_FILE="callcentersite/settings.py"
SETTINGS_DIR="callcentersite/settings"

if [ -f "$SETTINGS_FILE" ]; then
    TARGET_SETTINGS="$SETTINGS_FILE"
elif [ -f "$SETTINGS_DIR/base.py" ]; then
    TARGET_SETTINGS="$SETTINGS_DIR/base.py"
else
    TARGET_SETTINGS=""
fi

if [ -n "$TARGET_SETTINGS" ]; then
    if grep -q "DEBUG = True" "$TARGET_SETTINGS"; then
        log_error "DEBUG is True - should be False in production"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        log_info "DEBUG setting: OK"
    fi

    if grep -q 'SECRET_KEY = "[^"]*"' "$TARGET_SETTINGS"; then
        log_warn "SECRET_KEY may be hardcoded - should use environment variable"
    fi

    if grep -q "SECURE_SSL_REDIRECT = True" "$TARGET_SETTINGS"; then
        log_info "SECURE_SSL_REDIRECT: Enabled"
    else
        log_warn "SECURE_SSL_REDIRECT: Not enabled"
    fi

    if grep -q "SESSION_COOKIE_SECURE = True" "$TARGET_SETTINGS"; then
        log_info "SESSION_COOKIE_SECURE: Enabled"
    else
        log_warn "SESSION_COOKIE_SECURE: Not enabled"
    fi

    if grep -q "CSRF_COOKIE_SECURE = True" "$TARGET_SETTINGS"; then
        log_info "CSRF_COOKIE_SECURE: Enabled"
    else
        log_warn "CSRF_COOKIE_SECURE: Not enabled"
    fi
else
    log_warn "Skipping settings inspection: settings module not found"
    CHECKS_SKIPPED=$((CHECKS_SKIPPED + 1))
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
    if [ $CHECKS_SKIPPED -gt 0 ]; then
        exit 2
    fi
    exit 0
else
    log_error "Found $ISSUES_FOUND security issues"
    exit 1
fi
