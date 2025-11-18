#!/bin/bash
# scripts/validate_security_config.sh
# Valida la configuración de seguridad del proyecto IACT

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api/callcentersite"

echo "[INFO] Validando configuración de seguridad del proyecto IACT..."
echo "[INFO] Directorio API: $API_DIR"
echo ""

cd "$API_DIR"

FAILED=0
WARNINGS=0

# ==============================================================================
# 1. DJANGO CHECK --DEPLOY
# ==============================================================================
echo "[1] Ejecutando Django check --deploy..."
if python manage.py check --deploy --settings=callcentersite.settings.production 2>&1; then
    echo "[OK] Django check --deploy passed"
else
    echo "[FAIL] FALLO: Django check --deploy encontró problemas"
    FAILED=$((FAILED + 1))
fi
echo ""

# ==============================================================================
# 2. BANDIT (SAST)
# ==============================================================================
echo "[2] Ejecutando Bandit (SAST)..."
BANDIT_REPORT="$PROJECT_ROOT/reports/bandit-report.json"
mkdir -p "$PROJECT_ROOT/reports"

if command -v bandit &> /dev/null; then
    bandit -r callcentersite/ \
        -f json \
        -o "$BANDIT_REPORT" \
        --exclude "./callcentersite/tests,./callcentersite/**/migrations" \
        --skip B101 2>&1 || true

    # Analizar resultados
    if [ -f "$BANDIT_REPORT" ]; then
        HIGH_SEVERITY=$(cat "$BANDIT_REPORT" | grep -o '"issue_severity": "HIGH"' | wc -l || echo "0")
        MEDIUM_SEVERITY=$(cat "$BANDIT_REPORT" | grep -o '"issue_severity": "MEDIUM"' | wc -l || echo "0")

        if [ "$HIGH_SEVERITY" -gt 0 ]; then
            echo "[FAIL] FALLO: Bandit encontró $HIGH_SEVERITY problemas de severidad ALTA"
            echo "       Revisar: $BANDIT_REPORT"
            FAILED=$((FAILED + 1))
        elif [ "$MEDIUM_SEVERITY" -gt 0 ]; then
            echo "[WARN] WARNING: Bandit encontró $MEDIUM_SEVERITY problemas de severidad MEDIA"
            echo "       Revisar: $BANDIT_REPORT"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "[OK] Bandit no encontró problemas de seguridad"
        fi
    fi
else
    echo "[WARN] WARNING: Bandit no está instalado"
    echo "       Instalar: pip install bandit"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ==============================================================================
# 3. SAFETY CHECK
# ==============================================================================
echo "[3] Ejecutando Safety check (CVE scan)..."
SAFETY_REPORT="$PROJECT_ROOT/reports/safety-report.json"

if command -v safety &> /dev/null; then
    if safety check --json --output "$SAFETY_REPORT" 2>&1; then
        echo "[OK] Safety check - Sin vulnerabilidades conocidas"
    else
        echo "[FAIL] FALLO: Safety encontró vulnerabilidades"
        echo "       Revisar: $SAFETY_REPORT"
        FAILED=$((FAILED + 1))
    fi
else
    echo "[WARN] WARNING: Safety no está instalado"
    echo "       Instalar: pip install safety"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ==============================================================================
# 4. RUFF LINTING
# ==============================================================================
echo "[4] Ejecutando Ruff linting..."
if command -v ruff &> /dev/null; then
    if ruff check . --output-format=json > "$PROJECT_ROOT/reports/ruff-report.json" 2>&1; then
        echo "[OK] Ruff check passed"
    else
        # Contar errores
        RUFF_ERRORS=$(cat "$PROJECT_ROOT/reports/ruff-report.json" | grep -o '"code":' | wc -l || echo "0")
        if [ "$RUFF_ERRORS" -gt 0 ]; then
            echo "[WARN] WARNING: Ruff encontró $RUFF_ERRORS problemas"
            echo "       Revisar: $PROJECT_ROOT/reports/ruff-report.json"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "[OK] Ruff check passed"
        fi
    fi
else
    echo "[WARN] WARNING: Ruff no está instalado"
    echo "       Instalar: pip install ruff"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ==============================================================================
# 5. VERIFICAR CONFIGURACIÓN DE SEGURIDAD EN SETTINGS
# ==============================================================================
echo "[5] Verificando configuración de seguridad en settings..."
SETTINGS_PROD="callcentersite/settings/production.py"

SECURITY_CHECKS=(
    "DEBUG = False:DEBUG debe ser False en producción"
    "SECURE_HSTS_SECONDS:HSTS debe estar configurado"
    "SESSION_COOKIE_SECURE:Cookies de sesión deben ser seguras"
    "CSRF_COOKIE_SECURE:Cookies CSRF deben ser seguras"
)

SECURITY_FAILED=0
for check in "${SECURITY_CHECKS[@]}"; do
    IFS=':' read -r setting message <<< "$check"
    if grep -q "$setting" "$SETTINGS_PROD"; then
        echo "    [OK] $message"
    else
        echo "    [FAIL] $message - NO ENCONTRADO"
        SECURITY_FAILED=$((SECURITY_FAILED + 1))
    fi
done

if [ $SECURITY_FAILED -gt 0 ]; then
    echo "[FAIL] FALLO: $SECURITY_FAILED configuraciones de seguridad faltantes"
    FAILED=$((FAILED + 1))
else
    echo "[OK] Configuraciones de seguridad básicas presentes"
fi
echo ""

# ==============================================================================
# 6. VERIFICAR JWT CONFIGURACIÓN
# ==============================================================================
echo "[6] Verificando configuración JWT..."
SETTINGS_BASE="callcentersite/settings/base.py"

JWT_CHECKS=(
    "ACCESS_TOKEN_LIFETIME.*15:Access token debe ser 15 minutos"
    "REFRESH_TOKEN_LIFETIME.*7:Refresh token debe ser 7 días"
    "ROTATE_REFRESH_TOKENS.*True:Refresh tokens deben rotarse"
    "BLACKLIST_AFTER_ROTATION.*True:Tokens deben ir a blacklist después de rotación"
)

JWT_FAILED=0
for check in "${JWT_CHECKS[@]}"; do
    IFS=':' read -r pattern message <<< "$check"
    if grep -q "$pattern" "$SETTINGS_BASE"; then
        echo "    [OK] $message"
    else
        echo "    [FAIL] $message - NO ENCONTRADO"
        JWT_FAILED=$((JWT_FAILED + 1))
    fi
done

if [ $JWT_FAILED -gt 0 ]; then
    echo "[FAIL] FALLO: $JWT_FAILED configuraciones de JWT faltantes"
    FAILED=$((FAILED + 1))
else
    echo "[OK] Configuración JWT correcta"
fi
echo ""

# ==============================================================================
# 7. VERIFICAR THROTTLING
# ==============================================================================
echo "[7] Verificando throttling..."
if grep -q "DEFAULT_THROTTLE_CLASSES" "$SETTINGS_BASE"; then
    echo "[OK] Throttling configurado"
else
    echo "[WARN] WARNING: Throttling NO configurado"
    echo "       Recomendación: Agregar DEFAULT_THROTTLE_CLASSES en REST_FRAMEWORK"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ==============================================================================
# RESUMEN
# ==============================================================================
echo "========================================================================="
if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "[OK] VALIDACIÓN DE SEGURIDAD COMPLETADA - TODO OK"
    echo "========================================================================="
    exit 0
elif [ $FAILED -eq 0 ]; then
    echo "[WARN] VALIDACIÓN COMPLETADA CON $WARNINGS WARNINGS"
    echo "========================================================================="
    echo ""
    echo "Se recomienda revisar los warnings antes de producción"
    exit 0
else
    echo "[FAIL] VALIDACIÓN FALLÓ - $FAILED ERRORES, $WARNINGS WARNINGS"
    echo "========================================================================="
    echo ""
    echo "ACCIONES REQUERIDAS:"
    echo "   1. Corregir los errores reportados"
    echo "   2. Ejecutar: python manage.py check --deploy"
    echo "   3. Revisar reportes en: $PROJECT_ROOT/reports/"
    echo "   4. Consultar: docs/qa/checklist_auditoria_restricciones.md"
    echo ""
    exit 1
fi
