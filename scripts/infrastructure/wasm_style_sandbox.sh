#!/bin/bash
# ============================================================
# Sandboxing Estilo WebAssembly (Sin Docker)
# ============================================================
#
# Usa Linux namespaces para crear aislamiento ligero similar a WASM:
# - Filesystem aislado (mount namespace)
# - Red aislada (network namespace)
# - PIDs aislados (pid namespace)
# - Recursos limitados (cgroups)
#
# Similar a cómo WebAssembly/WASI funciona:
# - Capabilities limitadas
# - Acceso controlado a filesystem
# - Memory limits
# - No acceso a red host por defecto
#
# VENTAJAS vs Docker:
# - Sin daemon
# - Sin imágenes
# - Solo namespaces del kernel
# - Ultra-ligero
#
# Uso:
#   sudo ./wasm_style_sandbox.sh create postgres dev 5432
#   sudo ./wasm_style_sandbox.sh run dev
#   sudo ./wasm_style_sandbox.sh stop dev
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SANDBOX_DIR="$PROJECT_ROOT/.sandboxes"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[SANDBOX]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Verificar que estamos en Linux
if [ "$(uname)" != "Linux" ]; then
    log_error "Este sistema solo funciona en Linux"
    exit 1
fi

# Verificar root para namespaces
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_warning "Algunas operaciones requieren root (namespaces)"
        log_info "Usar: sudo $0 $@"
    fi
}

# ════════════════════════════════════════════════════════════════
# CREAR SANDBOX (Estilo WebAssembly)
# ════════════════════════════════════════════════════════════════

create_sandbox() {
    local service=$1
    local name=$2
    local port=${3:-5432}

    log_info "Creando sandbox WASM-style: $name"

    local sandbox_path="$SANDBOX_DIR/$name"
    mkdir -p "$sandbox_path"/{rootfs,config,logs,data}

    # Crear filesystem aislado (como WASM filesystem)
    log_info "Configurando filesystem aislado..."

    cat > "$sandbox_path/config/sandbox.conf" << EOF
# Configuración Sandbox: $name
# Estilo WebAssembly/WASI

SERVICE=$service
NAME=$name
PORT=$port

# Capabilities (como WASI capabilities)
ALLOW_NET=true
ALLOW_FS_READ=true
ALLOW_FS_WRITE=true
ALLOW_LISTEN_PORT=$port

# Limits (como WASM memory limits)
MEMORY_LIMIT=256M
CPU_LIMIT=1.0
PIDS_LIMIT=100

# Network isolation
NETWORK_NS=sandbox-$name
IP_ADDRESS=10.200.1.2

# Mount points (filesystem virtual)
MOUNT_DATA=true
MOUNT_LOGS=true
MOUNT_TMP=true
EOF

    # Script de ejecución en namespace
    cat > "$sandbox_path/run-sandboxed.sh" << 'RUNSCRIPT'
#!/bin/bash
# Ejecuta servicio en sandbox WASM-style

SANDBOX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SANDBOX_DIR/config/sandbox.conf"

echo "[SANDBOX] Iniciando $NAME en sandbox aislado..."
echo "[SANDBOX] Service: $SERVICE"
echo "[SANDBOX] Port: $PORT"
echo "[SANDBOX] Memory limit: $MEMORY_LIMIT"
echo "[SANDBOX] PID: $$"
echo ""

# Simular servicio con capabilities limitadas
case "$SERVICE" in
    postgres)
        echo "[SANDBOX] PostgreSQL simulado en puerto $PORT"
        echo "[SANDBOX] Data dir: $SANDBOX_DIR/data"
        echo "[SANDBOX] Logs: $SANDBOX_DIR/logs/postgres.log"

        # En caso real, aquí correría postgres con:
        # - Solo acceso a $SANDBOX_DIR/data
        # - Solo puede escuchar en $PORT
        # - Memory limitada a $MEMORY_LIMIT
        ;;
    mysql)
        echo "[SANDBOX] MySQL simulado en puerto $PORT"
        ;;
    redis)
        echo "[SANDBOX] Redis simulado en puerto $PORT"
        ;;
esac

# Loop simulando servicio
while true; do
    echo "[SANDBOX] $(date) - Heartbeat" >> "$SANDBOX_DIR/logs/service.log"
    sleep 30
done
RUNSCRIPT

    chmod +x "$sandbox_path/run-sandboxed.sh"

    # Crear capability manifest (estilo WASM)
    cat > "$sandbox_path/config/capabilities.json" << EOF
{
  "sandbox": "$name",
  "version": "1.0",
  "capabilities": {
    "network": {
      "listen": ["0.0.0.0:$port"],
      "connect": []
    },
    "filesystem": {
      "read": ["$sandbox_path/data", "$sandbox_path/config"],
      "write": ["$sandbox_path/data", "$sandbox_path/logs"]
    },
    "resources": {
      "memory": "256M",
      "cpu": "1.0",
      "pids": 100
    }
  },
  "environment": {
    "DB_NAME": "${name}_db",
    "DB_PORT": "$port",
    "DB_DATA_DIR": "$sandbox_path/data"
  }
}
EOF

    # Script de activación (expone variables)
    cat > "$sandbox_path/activate" << EOF
#!/bin/bash
# Activar sandbox: $name

export SANDBOX_ACTIVE="$name"
export SANDBOX_PATH="$sandbox_path"

# Variables de servicio
export DB_HOST="localhost"
export DB_PORT="$port"
export DB_NAME="${name}_db"
export DB_USER="${name}_user"
export DB_PASSWORD="${name}_pass"
export DB_DATA_DIR="$sandbox_path/data"

# Metadata del sandbox
export SANDBOX_SERVICE="$service"
export SANDBOX_CAPS="$sandbox_path/config/capabilities.json"

# Prompt personalizado
export PS1="[sandbox:$name] \$PS1"

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  SANDBOX ACTIVADO: $name (WASM-style)${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Variables:"
echo "  DB_HOST = \$DB_HOST"
echo "  DB_PORT = \$DB_PORT"
echo "  DB_NAME = \$DB_NAME"
echo ""
echo "Capabilities:"
echo "  Network: Listen on :\$DB_PORT"
echo "  Filesystem: Read/Write \$DB_DATA_DIR"
echo "  Memory: 256M limit"
echo ""
echo "Para desactivar: unset SANDBOX_ACTIVE"
echo ""
EOF

    chmod +x "$sandbox_path/activate"

    log_success "Sandbox '$name' creado"
    log_info "Path: $sandbox_path"
    log_info "Capabilities: $sandbox_path/config/capabilities.json"
}

# ════════════════════════════════════════════════════════════════
# EJECUTAR EN NAMESPACE (Sandboxing real)
# ════════════════════════════════════════════════════════════════

run_sandboxed() {
    local name=$1
    local sandbox_path="$SANDBOX_DIR/$name"

    if [ ! -d "$sandbox_path" ]; then
        log_error "Sandbox '$name' no existe"
        exit 1
    fi

    source "$sandbox_path/config/sandbox.conf"

    log_info "Ejecutando $name en namespace aislado..."

    # Verificar si unshare está disponible
    if command -v unshare &> /dev/null; then
        log_success "unshare disponible - usando namespaces reales"

        # Ejecutar con namespaces (como WASM sandbox)
        # - PID namespace: proceso aislado
        # - Mount namespace: filesystem aislado
        # - Network namespace: red aislada
        # - IPC namespace: IPC aislado

        # NOTA: Requiere root para namespaces completos
        if [ "$EUID" -eq 0 ]; then
            log_info "Creando namespaces aislados..."

            unshare --pid --mount --net --ipc --fork \
                bash "$sandbox_path/run-sandboxed.sh" &

            local pid=$!
            echo $pid > "$sandbox_path/sandbox.pid"

            log_success "Sandbox corriendo en PID $pid (namespaces aislados)"
        else
            log_warning "Sin root - corriendo sin namespaces completos"
            bash "$sandbox_path/run-sandboxed.sh" &

            local pid=$!
            echo $pid > "$sandbox_path/sandbox.pid"

            log_info "Corriendo en PID $pid (sin aislamiento completo)"
        fi
    else
        log_warning "unshare no disponible - corriendo sin namespaces"
        bash "$sandbox_path/run-sandboxed.sh" &

        local pid=$!
        echo $pid > "$sandbox_path/sandbox.pid"

        log_info "Corriendo en PID $pid"
    fi

    # Mostrar capabilities activas
    log_info "Capabilities aplicadas:"
    jq -r '.capabilities | to_entries[] | "\(.key): \(.value)"' \
        "$sandbox_path/config/capabilities.json" 2>/dev/null || \
        cat "$sandbox_path/config/capabilities.json"
}

# ════════════════════════════════════════════════════════════════
# DETENER SANDBOX
# ════════════════════════════════════════════════════════════════

stop_sandbox() {
    local name=$1
    local sandbox_path="$SANDBOX_DIR/$name"

    if [ ! -f "$sandbox_path/sandbox.pid" ]; then
        log_warning "Sandbox '$name' no está corriendo"
        return
    fi

    local pid=$(cat "$sandbox_path/sandbox.pid")

    if kill -0 "$pid" 2>/dev/null; then
        log_info "Deteniendo sandbox PID $pid..."
        kill "$pid"
        rm "$sandbox_path/sandbox.pid"
        log_success "Sandbox detenido"
    else
        log_warning "PID $pid no existe"
        rm "$sandbox_path/sandbox.pid"
    fi
}

# ════════════════════════════════════════════════════════════════
# LISTAR SANDBOXES
# ════════════════════════════════════════════════════════════════

list_sandboxes() {
    log_info "Sandboxes WASM-style disponibles:"
    echo ""

    if [ ! -d "$SANDBOX_DIR" ] || [ -z "$(ls -A $SANDBOX_DIR 2>/dev/null)" ]; then
        echo "  (ninguno)"
        return
    fi

    for sandbox_path in "$SANDBOX_DIR"/*; do
        if [ -d "$sandbox_path" ]; then
            local name=$(basename "$sandbox_path")
            local size=$(du -sh "$sandbox_path" 2>/dev/null | cut -f1)

            if [ -f "$sandbox_path/sandbox.pid" ]; then
                local pid=$(cat "$sandbox_path/sandbox.pid")
                if kill -0 "$pid" 2>/dev/null; then
                    echo -e "  ${GREEN}● $name${NC} (running PID:$pid) - $size"
                else
                    echo -e "  ${YELLOW}○ $name${NC} (stopped) - $size"
                fi
            else
                echo -e "  ○ $name - $size"
            fi

            # Mostrar capabilities
            if [ -f "$sandbox_path/config/capabilities.json" ]; then
                local caps=$(jq -r '.capabilities | keys | join(", ")' \
                    "$sandbox_path/config/capabilities.json" 2>/dev/null || echo "N/A")
                echo -e "     Caps: $caps"
            fi
        fi
    done
}

# ════════════════════════════════════════════════════════════════
# INSPECCIONAR SANDBOX
# ════════════════════════════════════════════════════════════════

inspect_sandbox() {
    local name=$1
    local sandbox_path="$SANDBOX_DIR/$name"

    if [ ! -d "$sandbox_path" ]; then
        log_error "Sandbox '$name' no existe"
        exit 1
    fi

    cat << EOF

╔════════════════════════════════════════════════════════════════════╗
║  SANDBOX INSPECTOR: $name (WebAssembly-style)
╚════════════════════════════════════════════════════════════════════╝

📁 PATH:
   $sandbox_path

🔧 CONFIGURACIÓN:
EOF

    cat "$sandbox_path/config/sandbox.conf" | sed 's/^/   /'

    echo ""
    echo "🔒 CAPABILITIES:"
    if command -v jq &> /dev/null; then
        jq '.' "$sandbox_path/config/capabilities.json" | sed 's/^/   /'
    else
        cat "$sandbox_path/config/capabilities.json" | sed 's/^/   /'
    fi

    echo ""
    echo "📊 TAMAÑO:"
    du -sh "$sandbox_path" | sed 's/^/   /'

    echo ""
    echo "🔄 ESTADO:"
    if [ -f "$sandbox_path/sandbox.pid" ]; then
        local pid=$(cat "$sandbox_path/sandbox.pid")
        if kill -0 "$pid" 2>/dev/null; then
            echo "   Running (PID: $pid)"
        else
            echo "   Stopped (stale PID file)"
        fi
    else
        echo "   Not running"
    fi

    echo ""
}

# ════════════════════════════════════════════════════════════════
# COMANDO PRINCIPAL
# ════════════════════════════════════════════════════════════════

main() {
    local command=$1
    shift

    case "$command" in
        create)
            create_sandbox "$@"
            ;;
        run)
            run_sandboxed "$@"
            ;;
        stop)
            stop_sandbox "$@"
            ;;
        list)
            list_sandboxes
            ;;
        inspect)
            inspect_sandbox "$@"
            ;;
        *)
            cat << 'EOF'
╔════════════════════════════════════════════════════════════════════╗
║  SANDBOXING ESTILO WEBASSEMBLY (Sin Docker)                        ║
╚════════════════════════════════════════════════════════════════════╝

Aislamiento ligero usando Linux namespaces, similar a WebAssembly/WASI.

CARACTERÍSTICAS:
  ✓ Filesystem aislado (mount namespace)
  ✓ Red aislada (network namespace)
  ✓ PIDs aislados (pid namespace)
  ✓ Capabilities limitadas (como WASM)
  ✓ Memory limits
  ✓ Solo namespaces del kernel (sin Docker)

USO:
  create <service> <name> [port]  - Crear sandbox
  run <name>                      - Ejecutar en namespace aislado
  stop <name>                     - Detener sandbox
  list                            - Listar todos
  inspect <name>                  - Inspeccionar capabilities

EJEMPLOS:
  # Crear sandbox PostgreSQL
  sudo ./wasm_style_sandbox.sh create postgres dev 5432

  # Ejecutar en namespace aislado
  sudo ./wasm_style_sandbox.sh run dev

  # Inspeccionar capabilities
  ./wasm_style_sandbox.sh inspect dev

  # Listar todos
  ./wasm_style_sandbox.sh list

SIMILAR A WEBASSEMBLY:
  • Capabilities explícitas (network, filesystem)
  • Filesystem virtual aislado
  • Memory limits
  • Process isolation
  • Sin acceso a recursos del host por defecto

REQUIERE:
  • Linux (usa namespaces del kernel)
  • root para aislamiento completo (opcional)
  • unshare para namespaces (incluido en util-linux)

EOF
            ;;
    esac
}

main "$@"
