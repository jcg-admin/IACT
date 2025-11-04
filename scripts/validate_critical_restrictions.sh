#!/bin/bash
# scripts/validate_critical_restrictions.sh
# Valida que se cumplan las restricciones críticas del proyecto IACT

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api"

echo "🔍 Validando restricciones críticas del proyecto IACT..."
echo "📁 Directorio del proyecto: $PROJECT_ROOT"
echo ""

FAILED=0

# ==============================================================================
# 1. VERIFICAR NO EMAIL
# ==============================================================================
echo "1️⃣  Verificando NO uso de email..."
if grep -r "send_mail\|EmailMessage\|smtp\.SMTP\|smtplib" "$API_DIR" \
    --include="*.py" \
    --exclude-dir=tests \
    --exclude-dir=.venv \
    --exclude-dir=__pycache__ 2>/dev/null; then
    echo "❌ FALLO: Se encontró uso de email en el código"
    echo "   Restricción: NO se permite envío de correos electrónicos"
    echo "   Usar: InternalMessage para notificaciones"
    FAILED=$((FAILED + 1))
else
    echo "✅ OK: Sin uso de email"
fi
echo ""

# ==============================================================================
# 2. VERIFICAR NO SENTRY
# ==============================================================================
echo "2️⃣  Verificando NO Sentry..."
if grep -ri "sentry" "$API_DIR/callcentersite/requirements/" 2>/dev/null || \
   grep -r "import sentry_sdk\|from sentry_sdk" "$API_DIR" \
    --include="*.py" \
    --exclude-dir=tests \
    --exclude-dir=.venv 2>/dev/null; then
    echo "❌ FALLO: Sentry encontrado en el proyecto"
    echo "   Restricción: NO se permite Sentry"
    echo "   Usar: Logging local y archivos rotativos"
    FAILED=$((FAILED + 1))
else
    echo "✅ OK: Sin Sentry"
fi
echo ""

# ==============================================================================
# 3. VERIFICAR NO REDIS/MEMCACHED PARA SESIONES
# ==============================================================================
echo "3️⃣  Verificando NO Redis/Memcached..."
if grep -ri "redis\|memcached" "$API_DIR/callcentersite/requirements/" 2>/dev/null; then
    echo "❌ FALLO: Redis/Memcached encontrado en requirements"
    echo "   Restricción: NO se permite Redis/Memcached para sesiones"
    echo "   Usar: Sesiones en base de datos"
    FAILED=$((FAILED + 1))
else
    echo "✅ OK: Sin Redis/Memcached"
fi
echo ""

# ==============================================================================
# 4. VERIFICAR NO CÓDIGO PELIGROSO (eval, exec, pickle)
# ==============================================================================
echo "4️⃣  Verificando NO código peligroso (eval/exec/pickle)..."
DANGEROUS_CODE=$(grep -rn "eval(\|exec(\|pickle\.load" "$API_DIR/callcentersite" \
    --include="*.py" \
    --exclude-dir=tests \
    --exclude-dir=.venv \
    --exclude-dir=__pycache__ \
    --exclude-dir=migrations 2>/dev/null || true)

if [ ! -z "$DANGEROUS_CODE" ]; then
    echo "❌ FALLO: Código peligroso encontrado:"
    echo "$DANGEROUS_CODE"
    echo "   Restricción: NO se permite eval(), exec(), pickle.load()"
    FAILED=$((FAILED + 1))
else
    echo "✅ OK: Sin código peligroso"
fi
echo ""

# ==============================================================================
# 5. VERIFICAR NO WEBSOCKETS/SSE
# ==============================================================================
echo "5️⃣  Verificando NO WebSockets/SSE (real-time updates)..."
if grep -r "websocket\|channels\|text/event-stream\|EventSource" "$API_DIR" \
    --include="*.py" \
    --exclude-dir=tests \
    --exclude-dir=.venv 2>/dev/null; then
    echo "❌ FALLO: WebSockets/SSE encontrado"
    echo "   Restricción: NO se permite actualizaciones en tiempo real"
    echo "   Usar: ETL programado cada 6-12 horas"
    FAILED=$((FAILED + 1))
else
    echo "✅ OK: Sin WebSockets/SSE"
fi
echo ""

# ==============================================================================
# 6. VERIFICAR DATABASE ROUTER EXISTE
# ==============================================================================
echo "6️⃣  Verificando Database Router..."
ROUTER_FILE="$API_DIR/callcentersite/callcentersite/database_router.py"
if [ ! -f "$ROUTER_FILE" ]; then
    echo "❌ FALLO: Database router no encontrado"
    echo "   Ubicación esperada: $ROUTER_FILE"
    FAILED=$((FAILED + 1))
else
    # Verificar que el router protege escritura a BD IVR
    if grep -q "raise ValueError" "$ROUTER_FILE" && \
       grep -q "READ-ONLY" "$ROUTER_FILE"; then
        echo "✅ OK: Database router existe y protege BD IVR"
    else
        echo "⚠️  WARNING: Database router existe pero no parece proteger escritura"
    fi
fi
echo ""

# ==============================================================================
# 7. VERIFICAR CONFIGURACIÓN DE SESSION_ENGINE
# ==============================================================================
echo "7️⃣  Verificando configuración de sesiones..."
SETTINGS_BASE="$API_DIR/callcentersite/callcentersite/settings/base.py"
if [ ! -f "$SETTINGS_BASE" ]; then
    echo "⚠️  WARNING: settings/base.py no encontrado"
else
    if grep -q "SESSION_ENGINE.*db" "$SETTINGS_BASE"; then
        echo "✅ OK: SESSION_ENGINE configurado para usar DB"
    else
        echo "⚠️  WARNING: SESSION_ENGINE no explícitamente configurado"
        echo "   Recomendación: Agregar SESSION_ENGINE = 'django.contrib.sessions.backends.db'"
    fi
fi
echo ""

# ==============================================================================
# 8. VERIFICAR MODELO InternalMessage EXISTE
# ==============================================================================
echo "8️⃣  Verificando modelo InternalMessage..."
NOTIF_MODELS="$API_DIR/callcentersite/callcentersite/apps/notifications/models.py"
if [ ! -f "$NOTIF_MODELS" ]; then
    echo "❌ FALLO: Modelo InternalMessage no encontrado"
    echo "   Ubicación esperada: $NOTIF_MODELS"
    FAILED=$((FAILED + 1))
else
    if grep -q "class InternalMessage" "$NOTIF_MODELS"; then
        echo "✅ OK: Modelo InternalMessage existe"
    else
        echo "❌ FALLO: InternalMessage no encontrado en models.py"
        FAILED=$((FAILED + 1))
    fi
fi
echo ""

# ==============================================================================
# RESUMEN
# ==============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo "✅ TODAS LAS RESTRICCIONES CRÍTICAS PASARON"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
else
    echo "❌ FALLOS ENCONTRADOS: $FAILED"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔧 ACCIONES REQUERIDAS:"
    echo "   1. Revisar los fallos reportados arriba"
    echo "   2. Corregir el código según las restricciones"
    echo "   3. Volver a ejecutar este script"
    echo "   4. Consultar: docs/requisitos/restricciones_completas.md"
    echo ""
    exit 1
fi
