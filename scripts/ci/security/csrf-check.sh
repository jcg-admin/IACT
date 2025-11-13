#!/bin/bash
# csrf-check.sh
#
# CSRF Protection Check
# Replica: Security Scan / CSRF Protection Check
#
# Exit codes:
#   0 - CSRF protection OK
#   1 - CSRF issues found

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

log_info "Checking CSRF protection..."

ISSUES_FOUND=0

# Check 1: CSRF middleware enabled
log_info "Checking Django CSRF middleware..."
SETTINGS_FILE="$PROJECT_ROOT/api/callcentersite/callcentersite/settings.py"

if [ -f "$SETTINGS_FILE" ]; then
    if grep -q "django.middleware.csrf.CsrfViewMiddleware" "$SETTINGS_FILE"; then
        log_info "CSRF middleware is enabled"
    else
        log_error "CSRF middleware is NOT enabled"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    log_error "Settings file not found"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check 2: Find views without CSRF protection
log_info "Scanning views for CSRF exemptions..."
VIEW_FILES=$(find "$PROJECT_ROOT/api/callcentersite" -type f -name "views.py" ! -path "*/migrations/*")

EXEMPT_VIEWS=0
for view_file in $VIEW_FILES; do
    if grep -q "@csrf_exempt" "$view_file"; then
        log_warn "Found CSRF exempt view in: $view_file"
        EXEMPT_VIEWS=$((EXEMPT_VIEWS + 1))
    fi
done

if [ $EXEMPT_VIEWS -gt 0 ]; then
    log_warn "Found $EXEMPT_VIEWS views with @csrf_exempt - review manually"
fi

# Check 3: API views should use SessionAuthentication or CSRF tokens
log_info "Checking API views for CSRF handling..."
API_VIEW_FILES=$(find "$PROJECT_ROOT/api/callcentersite" -type f -name "views.py" ! -path "*/migrations/*")

for api_view in $API_VIEW_FILES; do
    if grep -q "APIView\|ViewSet" "$api_view"; then
        if grep -q "SessionAuthentication\|CsrfExemptSessionAuthentication" "$api_view"; then
            log_info "API view has session authentication: $api_view"
        else
            log_warn "API view may need CSRF review: $api_view"
        fi
    fi
done

# Summary
echo ""
if [ $ISSUES_FOUND -eq 0 ]; then
    log_info "CSRF protection check passed"
    exit 0
else
    log_error "Found $ISSUES_FOUND CSRF protection issues"
    exit 1
fi
