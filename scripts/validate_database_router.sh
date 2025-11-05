#!/bin/bash
# scripts/validate_database_router.sh
# Valida que el Database Router proteja correctamente la BD IVR

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
API_DIR="$PROJECT_ROOT/api/callcentersite"

echo "[INFO] Validando protección de Base de Datos IVR..."
echo "[INFO] Directorio API: $API_DIR"
echo ""

cd "$API_DIR"

# ==============================================================================
# 1. VERIFICAR QUE ROUTER EXISTE
# ==============================================================================
echo "[1] Verificando que IVRReadOnlyRouter existe..."
ROUTER_FILE="callcentersite/database_router.py"

if [ ! -f "$ROUTER_FILE" ]; then
    echo "[FAIL] FALLO: Database router no encontrado en $ROUTER_FILE"
    exit 1
fi

if grep -q "class IVRReadOnlyRouter" "$ROUTER_FILE"; then
    echo "[OK] Clase IVRReadOnlyRouter encontrada"
else
    echo "[FAIL] FALLO: Clase IVRReadOnlyRouter no encontrada"
    exit 1
fi
echo ""

# ==============================================================================
# 2. VERIFICAR CONFIGURACIÓN EN SETTINGS
# ==============================================================================
echo "[2] Verificando configuración en settings..."
SETTINGS_BASE="callcentersite/settings/base.py"

if grep -q "DATABASE_ROUTERS.*IVRReadOnlyRouter" "$SETTINGS_BASE"; then
    echo "[OK] Router configurado en DATABASE_ROUTERS"
else
    echo "[FAIL] FALLO: Router NO configurado en settings"
    exit 1
fi
echo ""

# ==============================================================================
# 3. TEST UNITARIO - INTENTO DE ESCRITURA
# ==============================================================================
echo "[3] Ejecutando test de protección contra escritura..."

python -c "
import os
import sys
import django

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'callcentersite.settings.development'
sys.path.insert(0, '.')
django.setup()

from callcentersite.database_router import IVRReadOnlyRouter

# Mock de modelo IVR
class MockMeta:
    app_label = 'ivr_legacy'
    label = 'ivr_legacy.TestModel'

class MockModel:
    _meta = MockMeta()

router = IVRReadOnlyRouter()

# Test 1: Verificar db_for_read
print('    [TEST] Test 1: Verificando lectura...')
db_read = router.db_for_read(MockModel())
if db_read == 'ivr_readonly':
    print('    [OK] Lectura enrutada a ivr_readonly')
else:
    print(f'    [FAIL] FALLO: Lectura enrutada a {db_read}, esperado: ivr_readonly')
    sys.exit(1)

# Test 2: Verificar db_for_write (debe lanzar excepción)
print('    [TEST] Test 2: Verificando protección contra escritura...')
try:
    db_write = router.db_for_write(MockModel())
    print(f'    [FAIL] FALLO: Router permitió escritura (retornó: {db_write})')
    sys.exit(1)
except ValueError as e:
    if 'READ-ONLY' in str(e) and 'CRITICAL RESTRICTION' in str(e):
        print('    [OK] Router bloquea escritura con ValueError apropiado')
    else:
        print(f'    [WARN] WARNING: Excepción lanzada pero mensaje inesperado: {e}')
        sys.exit(1)

# Test 3: Verificar allow_migrate
print('    [TEST] Test 3: Verificando protección contra migraciones...')
if not router.allow_migrate('ivr_readonly', 'ivr_legacy', 'SomeModel'):
    print('    [OK] Migraciones bloqueadas en BD IVR')
else:
    print('    [FAIL] FALLO: Migraciones permitidas en BD IVR')
    sys.exit(1)

# Test 4: Verificar que modelos normales van a default
print('    [TEST] Test 4: Verificando enrutamiento a default...')
class NormalMeta:
    app_label = 'users'
    label = 'users.User'

class NormalModel:
    _meta = NormalMeta()

db_normal_read = router.db_for_read(NormalModel())
db_normal_write = router.db_for_write(NormalModel())

if db_normal_read == 'default' and db_normal_write == 'default':
    print('    [OK] Modelos normales enrutados a default')
else:
    print(f'    [FAIL] FALLO: Modelos normales mal enrutados (read: {db_normal_read}, write: {db_normal_write})')
    sys.exit(1)

print()
print('[OK] TODOS LOS TESTS DE DATABASE ROUTER PASARON')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================================="
    echo "[OK] DATABASE ROUTER CORRECTAMENTE CONFIGURADO"
    echo "========================================================================="
    echo ""
    echo "Protecciones activas:"
    echo "   - Lectura de IVR enrutada a ivr_readonly [OK]"
    echo "   - Escritura a IVR BLOQUEADA [OK]"
    echo "   - Migraciones en IVR BLOQUEADAS [OK]"
    echo "   - Modelos normales enrutados a default [OK]"
    echo ""
    echo "[INFO] RECORDATORIO:"
    echo "   El usuario de BD 'ivr_readonly' DEBE tener SOLO permisos SELECT"
    echo "   Validar con DBA antes de producción"
    exit 0
else
    echo ""
    echo "[FAIL] DATABASE ROUTER FALLÓ LA VALIDACIÓN"
    exit 1
fi
