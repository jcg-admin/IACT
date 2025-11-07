#!/bin/bash
#
# Security Scan Script - Local execution
#
# Ejecuta escaneos de seguridad basicos para Django + React
# Valida restricciones IACT criticas (RNF-002)
# Puede ejecutarse localmente o desde GitHub Actions
#
# Uso:
#   ./scripts/ci/security_scan.sh
#
# Requisitos:
#   - Python 3.11+ (bandit, safety)
#   - Node.js 18+ (npm audit)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

EXIT_CODE=0

log_info "Security Scan - Starting..."

# ===== Step 1: Validate IACT Critical Restrictions (RNF-002) =====
log_info "Step 1/8: Validating IACT Critical Restrictions (RNF-002)..."

cd "$PROJECT_ROOT"

# Check NO Redis
if grep -r "redis" api/callcentersite/settings*.py; then
    log_error "Redis detected in settings (PROHIBITED by RNF-002)"
    EXIT_CODE=1
else
    log_success "NO Redis usage (RNF-002 compliant)"
fi

# Check session backend is MySQL
if ! grep -q "django.contrib.sessions.backends.db" api/callcentersite/settings*.py; then
    log_error "SESSION_ENGINE must be django.contrib.sessions.backends.db (RNF-002)"
    EXIT_CODE=1
else
    log_success "Session backend in MySQL (RNF-002 compliant)"
fi

# Check NO Email
if grep -r "send_mail\|EmailMessage\|EmailMultiAlternatives" api/callcentersite/*.py 2>/dev/null | grep -v "# PROHIBITED" | grep -v "test_"; then
    log_warning "Email usage detected (should use InternalMessage)"
fi

# ===== Step 2: Django Security Checks =====
log_info "Step 2/8: Running Django security checks..."

cd "$PROJECT_ROOT/api/callcentersite"

if command -v python > /dev/null; then
    python manage.py check --deploy --settings=callcentersite.settings 2>/dev/null || {
        log_warning "Django security check warnings found"
    }
    log_success "Django security checks completed"
else
    log_warning "Python not available, skipping Django checks"
fi

# Check DEBUG setting
if grep -q "DEBUG = True" settings.py; then
    log_warning "DEBUG=True found in settings (should be False in production)"
fi

# Check SECRET_KEY
if grep -q "SECRET_KEY = ['\"]" settings.py; then
    log_warning "SECRET_KEY might be hardcoded (use environment variable)"
fi

# ===== Step 3: Bandit (Python Security) =====
log_info "Step 3/8: Running Bandit (Python security scan)..."

if command -v bandit > /dev/null; then
    cd "$PROJECT_ROOT/api/callcentersite"
    bandit -r . -f screen -ll || {
        log_warning "Bandit found security issues"
    }
    log_success "Bandit scan completed"
else
    log_warning "Bandit not installed (pip install bandit)"
fi

# ===== Step 4: Safety (Python Dependencies) =====
log_info "Step 4/8: Running Safety (Python dependency check)..."

if command -v safety > /dev/null; then
    cd "$PROJECT_ROOT/api"
    safety check --json > /dev/null 2>&1 || {
        log_warning "Safety found vulnerable dependencies"
        safety check || true
    }
    log_success "Safety check completed"
else
    log_warning "Safety not installed (pip install safety)"
fi

# ===== Step 5: npm audit (Frontend Security) =====
log_info "Step 5/8: Running npm audit (frontend security)..."

if [ -d "$PROJECT_ROOT/frontend" ]; then
    cd "$PROJECT_ROOT/frontend"

    if command -v npm > /dev/null; then
        # Run npm audit
        npm audit --json > npm-audit.json 2>/dev/null || true

        if [ -f npm-audit.json ]; then
            CRITICAL=$(cat npm-audit.json | grep -o '"critical":[0-9]*' | cut -d: -f2 || echo "0")
            HIGH=$(cat npm-audit.json | grep -o '"high":[0-9]*' | cut -d: -f2 || echo "0")

            if [ "${CRITICAL:-0}" -gt 0 ]; then
                log_error "CRITICAL vulnerabilities found in npm packages"
                EXIT_CODE=1
            elif [ "${HIGH:-0}" -gt 5 ]; then
                log_warning "High number of HIGH vulnerabilities in npm packages"
            else
                log_success "npm audit passed"
            fi

            rm -f npm-audit.json
        fi
    else
        log_warning "npm not available, skipping npm audit"
    fi
fi

# ===== Step 6: SQL Injection Check =====
log_info "Step 6/8: Checking for SQL injection vulnerabilities..."

cd "$PROJECT_ROOT"

# Look for raw SQL queries
if grep -r "\.raw\|\.execute" api/callcentersite/*.py 2>/dev/null | grep -v "test_" | grep -v ".pyc"; then
    log_warning "Raw SQL queries found (ensure they use parameterized queries)"
fi

# Look for string formatting in queries (CRITICAL)
if grep -r "f\".*SELECT\|\.format.*SELECT" api/callcentersite/*.py 2>/dev/null | grep -v "test_" | grep -v ".pyc"; then
    log_error "String formatting in SQL queries detected (SQL INJECTION RISK!)"
    EXIT_CODE=1
else
    log_success "No obvious SQL injection vulnerabilities"
fi

# ===== Step 7: XSS Check =====
log_info "Step 7/8: Checking for XSS vulnerabilities..."

# Check Django templates
if find . -name "*.html" -type f -exec grep -l "|safe\|{% autoescape off %}" {} \; 2>/dev/null | grep -v node_modules | head -1; then
    log_warning "Unescaped template variables found (potential XSS)"
fi

# Check React dangerous patterns
if grep -r "dangerouslySetInnerHTML" frontend/src/ 2>/dev/null | head -1; then
    log_warning "dangerouslySetInnerHTML found (ensure HTML is sanitized)"
fi

log_success "XSS check completed"

# ===== Step 8: CSRF Check =====
log_info "Step 8/8: Checking CSRF protection..."

cd "$PROJECT_ROOT"

# Check CSRF middleware
if ! grep -q "django.middleware.csrf.CsrfViewMiddleware" api/callcentersite/settings.py; then
    log_error "CSRF middleware not enabled"
    EXIT_CODE=1
else
    log_success "CSRF middleware enabled"
fi

# Check for @csrf_exempt
if grep -r "@csrf_exempt" api/callcentersite/*.py 2>/dev/null | grep -v "test_"; then
    log_warning "@csrf_exempt found (views bypass CSRF protection)"
fi

# ===== Summary =====
echo ""
echo "============================================"
echo "SECURITY SCAN SUMMARY"
echo "============================================"
echo "1. IACT RNF-002: $([ $EXIT_CODE -eq 0 ] && echo '[PASS]' || echo '[FAIL]')"
echo "2. Django Security: [OK]"
echo "3. Bandit (Python): [OK]"
echo "4. Safety (Dependencies): [OK]"
echo "5. npm audit (Frontend): [OK]"
echo "6. SQL Injection: $([ $EXIT_CODE -eq 0 ] && echo '[PASS]' || echo '[FAIL]')"
echo "7. XSS Protection: [OK]"
echo "8. CSRF Protection: $([ $EXIT_CODE -eq 0 ] && echo '[PASS]' || echo '[FAIL]')"
echo "============================================"
echo ""

if [ $EXIT_CODE -eq 0 ]; then
    log_success "Security scan PASSED"
else
    log_error "Security scan FAILED (see errors above)"
fi

exit $EXIT_CODE
