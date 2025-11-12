#!/bin/bash
# ============================================================
# Demo: Sistema de Ambientes Virtualizados
# ============================================================
#
# Este script demuestra cómo usar el sistema de virtualización
# para crear "caparazones" aislados para diferentes servicios.
#
# NOTA: Requiere Docker instalado y corriendo
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VIRT_SCRIPT="$SCRIPT_DIR/../scripts/infrastructure/virtualize.sh"

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

demo_step() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}PASO $1:${NC} $2"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

demo_command() {
    echo -e "${YELLOW}$ $1${NC}"
    echo ""
}

wait_continue() {
    echo ""
    read -p "Presiona ENTER para continuar..."
    echo ""
}

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  DEMO: SISTEMA DE AMBIENTES VIRTUALIZADOS"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Este demo muestra cómo crear 'caparazones' aislados para:"
echo "  • PostgreSQL (desarrollo)"
echo "  • MySQL (testing)"
echo "  • Redis (cache)"
echo ""
echo "Cada uno con su propio puerto, datos y configuración."
echo ""
wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 1: Crear Ambiente PostgreSQL para Desarrollo
# ════════════════════════════════════════════════════════════════

demo_step "1" "Crear ambiente PostgreSQL para desarrollo"

cat << 'EOF'
Vamos a crear un ambiente aislado de PostgreSQL:
  - Nombre: dev
  - Puerto: 5432
  - Database: iact_dev
  - User: dev_user
  - Password: dev_password

Este ambiente es completamente independiente de cualquier
PostgreSQL que tengas instalado en tu sistema.
EOF

echo ""
demo_command "./virtualize.sh create postgres dev 5432"

if command -v docker &> /dev/null; then
    bash "$VIRT_SCRIPT" create postgres dev 5432 || true
else
    echo "[INFO] Docker no disponible - mostrando simulación"
    echo ""
    echo "[OK] Ambiente PostgreSQL 'dev' creado en puerto 5432"
    echo "[INFO] Docker Compose: .venvs/postgres-dev/docker-compose.yml"
fi

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 2: Crear Ambiente MySQL para Testing
# ════════════════════════════════════════════════════════════════

demo_step "2" "Crear ambiente MySQL para testing"

cat << 'EOF'
Ahora creamos un ambiente MySQL en puerto diferente:
  - Nombre: test
  - Puerto: 3307 (no 3306, para no conflictuar)
  - Database: iact_test
  - User: test_user

Nota: Ambos ambientes pueden correr simultáneamente.
EOF

echo ""
demo_command "./virtualize.sh create mysql test 3307"

if command -v docker &> /dev/null; then
    bash "$VIRT_SCRIPT" create mysql test 3307 || true
else
    echo "[INFO] Docker no disponible - mostrando simulación"
    echo ""
    echo "[OK] Ambiente MySQL 'test' creado en puerto 3307"
    echo "[INFO] Docker Compose: .venvs/mysql-test/docker-compose.yml"
fi

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 3: Crear Ambiente Redis para Cache
# ════════════════════════════════════════════════════════════════

demo_step "3" "Crear ambiente Redis para cache"

cat << 'EOF'
Y un ambiente Redis para caching:
  - Nombre: cache
  - Puerto: 6379
  - Password: cache_password

Este es el tercer ambiente independiente.
EOF

echo ""
demo_command "./virtualize.sh create redis cache 6379"

if command -v docker &> /dev/null; then
    bash "$VIRT_SCRIPT" create redis cache 6379 || true
else
    echo "[INFO] Docker no disponible - mostrando simulación"
    echo ""
    echo "[OK] Ambiente Redis 'cache' creado en puerto 6379"
    echo "[INFO] Docker Compose: .venvs/redis-cache/docker-compose.yml"
fi

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 4: Listar Todos los Ambientes
# ════════════════════════════════════════════════════════════════

demo_step "4" "Listar todos los ambientes creados"

cat << 'EOF'
Veamos qué ambientes hemos creado:
EOF

echo ""
demo_command "./virtualize.sh list"

if command -v docker &> /dev/null; then
    bash "$VIRT_SCRIPT" list || true
else
    echo "[INFO] Docker no disponible - mostrando simulación"
    echo ""
    echo "Ambientes virtualizados disponibles:"
    echo "  ✗ postgres-dev (stopped)"
    echo "  ✗ mysql-test (stopped)"
    echo "  ✗ redis-cache (stopped)"
fi

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 5: Iniciar Ambiente PostgreSQL
# ════════════════════════════════════════════════════════════════

demo_step "5" "Iniciar ambiente PostgreSQL"

cat << 'EOF'
Vamos a iniciar el ambiente PostgreSQL.
Docker lo levantará y esperará a que esté saludable.
EOF

echo ""
demo_command "./virtualize.sh start postgres dev"

if command -v docker &> /dev/null; then
    bash "$VIRT_SCRIPT" start postgres dev || true
else
    echo "[INFO] Docker no disponible - mostrando simulación"
    echo ""
    echo "[INFO] Iniciando postgres-dev..."
    echo "[OK] postgres-dev esta corriendo y saludable"
    echo ""
    echo "Ambiente PostgreSQL: dev"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: iact_dev"
    echo "  User: dev_user"
    echo ""
    echo "Conectar:"
    echo "  psql -h localhost -p 5432 -U dev_user -d iact_dev"
fi

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 6: Activar Ambiente (Cargar Variables)
# ════════════════════════════════════════════════════════════════

demo_step "6" "Activar ambiente (cargar variables de entorno)"

cat << 'EOF'
Para usar el ambiente en tu código, actívalo:

  source <(./virtualize.sh activate postgres dev)

Esto carga variables de entorno:
  - DB_HOST=localhost
  - DB_PORT=5432
  - DB_NAME=iact_dev
  - DB_USER=dev_user
  - DB_PASSWORD=dev_password

Tu aplicación puede leerlas automáticamente.
EOF

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 7: Usar en Python
# ════════════════════════════════════════════════════════════════

demo_step "7" "Usar en tu aplicación Python"

cat << 'EOF'
Ejemplo de uso en Python:

    import os
    import psycopg2

    # Las variables ya están en el ambiente
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

    # O usar con environment_config.py (auto-detecta)
    from scripts.ai.shared.environment_config import get_environment_config

    config = get_environment_config()
    db_config = config.get_database_config()
    # Detecta automáticamente el ambiente virtualizado
EOF

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 8: Múltiples Ambientes Simultáneos
# ════════════════════════════════════════════════════════════════

demo_step "8" "Ejecutar múltiples ambientes simultáneos"

cat << 'EOF'
Puedes iniciar varios ambientes al mismo tiempo:

    ./virtualize.sh start postgres dev
    ./virtualize.sh start mysql test
    ./virtualize.sh start redis cache

Cada uno corre en su propio puerto sin conflictos:
  - PostgreSQL dev:  localhost:5432
  - MySQL test:      localhost:3307
  - Redis cache:     localhost:6379

Esto es imposible con instalaciones locales tradicionales.
EOF

wait_continue

# ════════════════════════════════════════════════════════════════
# PASO 9: Limpieza
# ════════════════════════════════════════════════════════════════

demo_step "9" "Limpiar ambientes"

cat << 'EOF'
Cuando termines, puedes:

1. Detener (mantiene datos):
   ./virtualize.sh stop postgres dev

2. Destruir (elimina TODO):
   ./virtualize.sh destroy postgres dev

Para testing, es común destruir y recrear para empezar limpio:

    # Test run 1
    ./virtualize.sh create postgres test 5433
    ./virtualize.sh start postgres test
    pytest tests/
    ./virtualize.sh destroy postgres test

    # Test run 2 - base de datos limpia
    ./virtualize.sh create postgres test 5433
    ./virtualize.sh start postgres test
    pytest tests/
    ./virtualize.sh destroy postgres test
EOF

wait_continue

# ════════════════════════════════════════════════════════════════
# RESUMEN
# ════════════════════════════════════════════════════════════════

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  RESUMEN"
echo "════════════════════════════════════════════════════════════════"
echo ""

cat << 'EOF'
Has aprendido a:

✓ Crear ambientes aislados (caparazones)
✓ Ejecutar múltiples servicios simultáneamente
✓ Activar ambientes para cargar variables
✓ Usar en tu código Python/Django
✓ Limpiar y recrear ambientes

VENTAJAS vs Vagrant:
  • 10x más rápido (segundos vs minutos)
  • 10x más ligero (100MB vs 1GB)
  • Múltiples ambientes fácilmente
  • Destruir/recrear instantáneo

VENTAJAS vs Instalación Local:
  • Sin conflictos de puertos
  • Múltiples versiones simultáneas
  • Testing con datos limpios
  • Portabilidad (solo requiere Docker)

COMANDOS PRINCIPALES:
  create   - Crear nuevo ambiente
  start    - Iniciar ambiente
  stop     - Detener (mantiene datos)
  destroy  - Eliminar completamente
  list     - Ver todos los ambientes
  activate - Cargar variables de entorno

PRÓXIMOS PASOS:
  1. Instala Docker si no lo tienes
  2. Crea tu primer ambiente:
     ./virtualize.sh create postgres dev 5432
  3. Inícialo:
     ./virtualize.sh start postgres dev
  4. Úsalo en tu código

¡Disfruta tu sistema de caparazones virtualizados!
EOF

echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
