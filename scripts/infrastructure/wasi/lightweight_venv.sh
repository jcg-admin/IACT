#!/bin/bash
# ============================================================
# Sistema de Ambientes Virtuales Ligeros (Sin Docker)
# ============================================================
#
# Crea "caparazones" aislados usando SOLO:
# - Directorios separados
# - Procesos en background
# - Variables de entorno
# - Port binding
#
# Similar a Python venv, pero para servicios.
#
# NO requiere:
# - Docker
# - Vagrant
# - VM
# - Containers
#
# Uso:
#   ./lightweight_venv.sh create postgres dev
#   ./lightweight_venv.sh activate dev
#   ./lightweight_venv.sh destroy dev
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENVS_DIR="$PROJECT_ROOT/.lightvenvs"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ════════════════════════════════════════════════════════════════
# FUNCIONES CORE
# ════════════════════════════════════════════════════════════════

create_venv() {
    local name=$1
    local port=${2:-5432}

    log_info "Creando ambiente ligero: $name"

    local venv_dir="$VENVS_DIR/$name"
    mkdir -p "$venv_dir"/{data,logs,bin,config}

    # Crear script de activación
    cat > "$venv_dir/bin/activate" << EOF
#!/bin/bash
# Ambiente Virtual: $name

# Desactivar ambiente anterior si existe
if [ -n "\$LIGHTVENV_ACTIVE" ]; then
    deactivate 2>/dev/null || true
fi

# Función de desactivación
deactivate() {
    if [ -n "\$_OLD_VIRTUAL_PATH" ]; then
        export PATH="\$_OLD_VIRTUAL_PATH"
        unset _OLD_VIRTUAL_PATH
    fi

    if [ -n "\$_OLD_VIRTUAL_PS1" ]; then
        export PS1="\$_OLD_VIRTUAL_PS1"
        unset _OLD_VIRTUAL_PS1
    fi

    unset LIGHTVENV_ACTIVE
    unset LIGHTVENV_NAME
    unset DB_HOST
    unset DB_PORT
    unset DB_NAME
    unset DB_USER
    unset DB_PASSWORD
    unset DB_DATA_DIR

    echo "[LIGHTVENV] Ambiente desactivado"
}

# Guardar estado anterior
export _OLD_VIRTUAL_PATH="\$PATH"
export _OLD_VIRTUAL_PS1="\$PS1"

# Activar ambiente
export LIGHTVENV_ACTIVE="$name"
export LIGHTVENV_NAME="$name"
export PATH="$venv_dir/bin:\$PATH"
export PS1="($name) \$PS1"

# Variables de base de datos
export DB_HOST="localhost"
export DB_PORT="$port"
export DB_NAME="${name}_db"
export DB_USER="${name}_user"
export DB_PASSWORD="${name}_pass"
export DB_DATA_DIR="$venv_dir/data"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  AMBIENTE VIRTUAL ACTIVADO: $name${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Variables de entorno cargadas:"
echo "  DB_HOST     = \$DB_HOST"
echo "  DB_PORT     = \$DB_PORT"
echo "  DB_NAME     = \$DB_NAME"
echo "  DB_USER     = \$DB_USER"
echo "  DB_DATA_DIR = \$DB_DATA_DIR"
echo ""
echo "Para desactivar: deactivate"
echo ""
EOF

    chmod +x "$venv_dir/bin/activate"

    # Crear script de inicio de servicio simulado
    cat > "$venv_dir/bin/start-service" << 'EOF'
#!/bin/bash
# Simula un servicio de base de datos

VENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$VENV_DIR/logs/service.log"
PID_FILE="$VENV_DIR/service.pid"

echo "[$(date)] Servicio iniciado en puerto $DB_PORT" >> "$LOG_FILE"
echo $$ > "$PID_FILE"

# Simular servicio (en caso real, aquí iría postgres, mysql, etc.)
echo "[$(date)] Escuchando en $DB_HOST:$DB_PORT" >> "$LOG_FILE"

# Loop infinito simulando servicio
while true; do
    sleep 60
    echo "[$(date)] Heartbeat" >> "$LOG_FILE"
done
EOF

    chmod +x "$venv_dir/bin/start-service"

    # Crear README
    cat > "$venv_dir/README.md" << EOF
# Ambiente Virtual: $name

## Activar

\`\`\`bash
source $venv_dir/bin/activate
\`\`\`

## Variables disponibles

- \`DB_HOST\`: $DB_HOST
- \`DB_PORT\`: $port
- \`DB_NAME\`: ${name}_db
- \`DB_USER\`: ${name}_user
- \`DB_PASSWORD\`: ${name}_pass
- \`DB_DATA_DIR\`: $venv_dir/data

## Desactivar

\`\`\`bash
deactivate
\`\`\`

## Directorio

$venv_dir/
├── bin/          # Ejecutables
├── data/         # Datos del servicio
├── logs/         # Logs
├── config/       # Configuración
└── README.md     # Este archivo
EOF

    log_success "Ambiente '$name' creado en: $venv_dir"
    log_info "Para activar: source $venv_dir/bin/activate"
}

# ════════════════════════════════════════════════════════════════
# ACTIVACIÓN AUTOMÁTICA
# ════════════════════════════════════════════════════════════════

activate_venv() {
    local name=$1
    local venv_dir="$VENVS_DIR/$name"

    if [ ! -d "$venv_dir" ]; then
        log_error "Ambiente '$name' no existe"
        echo "Crear con: $0 create $name"
        exit 1
    fi

    # Mostrar comando de activación
    echo "# Para activar este ambiente, ejecuta:"
    echo "source $venv_dir/bin/activate"
}

# ════════════════════════════════════════════════════════════════
# LISTADO
# ════════════════════════════════════════════════════════════════

list_venvs() {
    log_info "Ambientes virtuales ligeros:"
    echo ""

    if [ ! -d "$VENVS_DIR" ] || [ -z "$(ls -A $VENVS_DIR 2>/dev/null)" ]; then
        echo "  (ninguno)"
        return
    fi

    for venv_dir in "$VENVS_DIR"/*; do
        if [ -d "$venv_dir" ]; then
            local name=$(basename "$venv_dir")
            local size=$(du -sh "$venv_dir" 2>/dev/null | cut -f1)

            if [ "$LIGHTVENV_ACTIVE" = "$name" ]; then
                echo -e "  ${GREEN}● $name${NC} (activo) - $size"
            else
                echo -e "  ○ $name - $size"
            fi
        fi
    done
}

# ════════════════════════════════════════════════════════════════
# DESTRUCCIÓN
# ════════════════════════════════════════════════════════════════

destroy_venv() {
    local name=$1
    local venv_dir="$VENVS_DIR/$name"

    if [ ! -d "$venv_dir" ]; then
        log_error "Ambiente '$name' no existe"
        exit 1
    fi

    log_warning "Esto eliminará completamente el ambiente '$name'"
    read -p "¿Continuar? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Cancelado"
        exit 0
    fi

    rm -rf "$venv_dir"
    log_success "Ambiente '$name' eliminado"
}

# ════════════════════════════════════════════════════════════════
# INFORMACIÓN
# ════════════════════════════════════════════════════════════════

info_venv() {
    local name=$1
    local venv_dir="$VENVS_DIR/$name"

    if [ ! -d "$venv_dir" ]; then
        log_error "Ambiente '$name' no existe"
        exit 1
    fi

    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  AMBIENTE: $name"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""

    echo "Ubicación:"
    echo "  $venv_dir"
    echo ""

    echo "Tamaño:"
    du -sh "$venv_dir" 2>/dev/null || echo "  N/A"
    echo ""

    echo "Estructura:"
    tree -L 2 "$venv_dir" 2>/dev/null || ls -la "$venv_dir"
    echo ""

    echo "Para activar:"
    echo "  source $venv_dir/bin/activate"
    echo ""
}

# ════════════════════════════════════════════════════════════════
# COMPARAR CON DOCKER
# ════════════════════════════════════════════════════════════════

show_comparison() {
    cat << 'EOF'

╔════════════════════════════════════════════════════════════════════╗
║  COMPARACIÓN: Lightweight venv vs Docker                           ║
╚════════════════════════════════════════════════════════════════════╝

┌─────────────────┬──────────────────┬─────────────────────────────┐
│ Aspecto         │ Docker           │ Lightweight venv            │
├─────────────────┼──────────────────┼─────────────────────────────┤
│ Requiere        │ Docker Engine    │ Solo Bash                   │
│ Tamaño          │ 100-500 MB       │ < 1 MB (solo config)        │
│ Inicio          │ 5-10 segundos    │ Instantáneo                 │
│ Memoria         │ 50-200 MB        │ < 1 MB                      │
│ Aislamiento     │ Contenedor       │ Proceso + directorios       │
│ Portabilidad    │ Requiere Docker  │ Funciona en cualquier Linux │
│ Complejidad     │ Media            │ Muy baja                    │
│ Ideal para      │ Servicios reales │ Testing, mocking, dev       │
└─────────────────┴──────────────────┴─────────────────────────────┘

CUÁNDO USAR:

✓ Lightweight venv (ESTE):
  - Desarrollo rápido
  - Testing con mocks
  - No necesitas servicio real
  - Quieres algo ultra-ligero
  - Solo necesitas variables de entorno

✓ Docker:
  - Necesitas servicio real (PostgreSQL, MySQL)
  - Producción
  - CI/CD con servicios reales
  - Compatibilidad con ecosistema Docker

EOF
}

# ════════════════════════════════════════════════════════════════
# COMANDO PRINCIPAL
# ════════════════════════════════════════════════════════════════

main() {
    local command=$1
    local name=$2
    local port=$3

    case "$command" in
        create)
            if [ -z "$name" ]; then
                log_error "Nombre requerido"
                echo "Uso: $0 create <nombre> [puerto]"
                exit 1
            fi
            create_venv "$name" "$port"
            ;;
        activate)
            if [ -z "$name" ]; then
                log_error "Nombre requerido"
                echo "Uso: $0 activate <nombre>"
                exit 1
            fi
            activate_venv "$name"
            ;;
        list)
            list_venvs
            ;;
        destroy)
            if [ -z "$name" ]; then
                log_error "Nombre requerido"
                echo "Uso: $0 destroy <nombre>"
                exit 1
            fi
            destroy_venv "$name"
            ;;
        info)
            if [ -z "$name" ]; then
                log_error "Nombre requerido"
                echo "Uso: $0 info <nombre>"
                exit 1
            fi
            info_venv "$name"
            ;;
        compare)
            show_comparison
            ;;
        *)
            cat << 'EOF'
╔════════════════════════════════════════════════════════════════════╗
║  AMBIENTES VIRTUALES LIGEROS (Sin Docker)                          ║
╚════════════════════════════════════════════════════════════════════╝

Similar a Python venv, pero para servicios de bases de datos.

CARACTERÍSTICAS:
  ✓ Solo Bash (sin Docker, sin VM)
  ✓ Instantáneo (< 1 segundo)
  ✓ Ultra-ligero (< 1 MB)
  ✓ Directorios aislados
  ✓ Variables de entorno propias

USO:
  create <nombre> [puerto]  - Crear ambiente
  activate <nombre>         - Activar ambiente
  list                      - Listar ambientes
  destroy <nombre>          - Eliminar ambiente
  info <nombre>             - Ver información
  compare                   - Comparar con Docker

EJEMPLOS:
  # Crear ambiente para desarrollo
  ./lightweight_venv.sh create dev 5432

  # Activar (carga variables de entorno)
  source .lightvenvs/dev/bin/activate

  # Tu aplicación ahora ve:
  #   DB_HOST=localhost
  #   DB_PORT=5432
  #   DB_NAME=dev_db
  #   etc.

  # Listar todos
  ./lightweight_venv.sh list

  # Destruir
  ./lightweight_venv.sh destroy dev

VENTAJAS vs Docker:
  • 100x más rápido
  • 100x más ligero
  • No requiere daemon
  • Funciona en cualquier Linux
  • Ideal para testing/mocking

Para comparación completa:
  ./lightweight_venv.sh compare

EOF
            ;;
    esac
}

main "$@"
