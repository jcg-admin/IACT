#!/bin/bash
# ============================================================
# Sistema de Ambientes Virtualizados
# ============================================================
#
# Crea "caparazones" aislados para diferentes servicios:
# - MySQL
# - PostgreSQL
# - Redis
# - MongoDB
#
# Cada servicio corre en su propio contenedor aislado
# sin interferir con otros servicios.
#
# Uso:
#   ./virtualize.sh create postgres dev
#   ./virtualize.sh start postgres dev
#   ./virtualize.sh stop postgres dev
#   ./virtualize.sh destroy postgres dev
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$PROJECT_ROOT/.venvs"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker no esta instalado"
        echo "Instalar Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker ps &> /dev/null; then
        log_error "Docker daemon no esta corriendo"
        echo "Iniciar Docker y volver a intentar"
        exit 1
    fi

    log_success "Docker disponible"
}

# Crear ambiente PostgreSQL
create_postgres() {
    local name=$1
    local port=${2:-5432}

    log_info "Creando ambiente PostgreSQL: $name"

    mkdir -p "$VENV_DIR/postgres-$name"

    cat > "$VENV_DIR/postgres-$name/docker-compose.yml" << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: postgres-$name
    environment:
      POSTGRES_DB: iact_$name
      POSTGRES_USER: ${name}_user
      POSTGRES_PASSWORD: ${name}_password
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "$port:5432"
    volumes:
      - postgres-${name}-data:/var/lib/postgresql/data
    networks:
      - ${name}-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${name}_user -d iact_$name"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres-${name}-data:
    driver: local

networks:
  ${name}-network:
    driver: bridge
EOF

    # Crear archivo de conexión
    cat > "$VENV_DIR/postgres-$name/connection.sh" << EOF
#!/bin/bash
# Conexion a PostgreSQL $name

export DB_HOST=localhost
export DB_PORT=$port
export DB_NAME=iact_$name
export DB_USER=${name}_user
export DB_PASSWORD=${name}_password

echo "Ambiente PostgreSQL: $name"
echo "  Host: \$DB_HOST"
echo "  Port: \$DB_PORT"
echo "  Database: \$DB_NAME"
echo "  User: \$DB_USER"
echo ""
echo "Conectar:"
echo "  psql -h \$DB_HOST -p \$DB_PORT -U \$DB_USER -d \$DB_NAME"
EOF

    chmod +x "$VENV_DIR/postgres-$name/connection.sh"

    log_success "Ambiente PostgreSQL '$name' creado en puerto $port"
    log_info "Docker Compose: $VENV_DIR/postgres-$name/docker-compose.yml"
}

# Crear ambiente MySQL
create_mysql() {
    local name=$1
    local port=${2:-3306}

    log_info "Creando ambiente MySQL: $name"

    mkdir -p "$VENV_DIR/mysql-$name"

    cat > "$VENV_DIR/mysql-$name/docker-compose.yml" << EOF
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql-$name
    environment:
      MYSQL_DATABASE: iact_$name
      MYSQL_USER: ${name}_user
      MYSQL_PASSWORD: ${name}_password
      MYSQL_ROOT_PASSWORD: ${name}_root_password
    ports:
      - "$port:3306"
    volumes:
      - mysql-${name}-data:/var/lib/mysql
    networks:
      - ${name}-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${name}_root_password"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  mysql-${name}-data:
    driver: local

networks:
  ${name}-network:
    driver: bridge
EOF

    # Crear archivo de conexión
    cat > "$VENV_DIR/mysql-$name/connection.sh" << EOF
#!/bin/bash
# Conexion a MySQL $name

export DB_HOST=localhost
export DB_PORT=$port
export DB_NAME=iact_$name
export DB_USER=${name}_user
export DB_PASSWORD=${name}_password

echo "Ambiente MySQL: $name"
echo "  Host: \$DB_HOST"
echo "  Port: \$DB_PORT"
echo "  Database: \$DB_NAME"
echo "  User: \$DB_USER"
echo ""
echo "Conectar:"
echo "  mysql -h \$DB_HOST -P \$DB_PORT -u \$DB_USER -p\$DB_PASSWORD \$DB_NAME"
EOF

    chmod +x "$VENV_DIR/mysql-$name/connection.sh"

    log_success "Ambiente MySQL '$name' creado en puerto $port"
    log_info "Docker Compose: $VENV_DIR/mysql-$name/docker-compose.yml"
}

# Crear ambiente Redis
create_redis() {
    local name=$1
    local port=${2:-6379}

    log_info "Creando ambiente Redis: $name"

    mkdir -p "$VENV_DIR/redis-$name"

    cat > "$VENV_DIR/redis-$name/docker-compose.yml" << EOF
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: redis-$name
    command: redis-server --requirepass ${name}_password
    ports:
      - "$port:6379"
    volumes:
      - redis-${name}-data:/data
    networks:
      - ${name}-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis-${name}-data:
    driver: local

networks:
  ${name}-network:
    driver: bridge
EOF

    # Crear archivo de conexión
    cat > "$VENV_DIR/redis-$name/connection.sh" << EOF
#!/bin/bash
# Conexion a Redis $name

export REDIS_HOST=localhost
export REDIS_PORT=$port
export REDIS_PASSWORD=${name}_password

echo "Ambiente Redis: $name"
echo "  Host: \$REDIS_HOST"
echo "  Port: \$REDIS_PORT"
echo ""
echo "Conectar:"
echo "  redis-cli -h \$REDIS_HOST -p \$REDIS_PORT -a \$REDIS_PASSWORD"
EOF

    chmod +x "$VENV_DIR/redis-$name/connection.sh"

    log_success "Ambiente Redis '$name' creado en puerto $port"
    log_info "Docker Compose: $VENV_DIR/redis-$name/docker-compose.yml"
}

# Iniciar ambiente
start_environment() {
    local service=$1
    local name=$2

    local env_dir="$VENV_DIR/${service}-${name}"

    if [ ! -d "$env_dir" ]; then
        log_error "Ambiente ${service}-${name} no existe"
        echo "Crear con: ./virtualize.sh create $service $name"
        exit 1
    fi

    log_info "Iniciando ${service}-${name}..."

    cd "$env_dir"
    docker-compose up -d

    # Esperar a que este healthy
    local container="${service}-${name}"
    log_info "Esperando a que $container este listo..."

    for i in {1..30}; do
        if docker ps --filter "name=$container" --filter "health=healthy" | grep -q "$container"; then
            log_success "$container esta corriendo y saludable"

            # Mostrar informacion de conexion
            echo ""
            bash "$env_dir/connection.sh"
            return 0
        fi
        sleep 1
    done

    log_warning "$container inicio pero puede no estar completamente listo"
}

# Detener ambiente
stop_environment() {
    local service=$1
    local name=$2

    local env_dir="$VENV_DIR/${service}-${name}"

    if [ ! -d "$env_dir" ]; then
        log_error "Ambiente ${service}-${name} no existe"
        exit 1
    fi

    log_info "Deteniendo ${service}-${name}..."

    cd "$env_dir"
    docker-compose stop

    log_success "${service}-${name} detenido"
}

# Destruir ambiente
destroy_environment() {
    local service=$1
    local name=$2

    local env_dir="$VENV_DIR/${service}-${name}"

    if [ ! -d "$env_dir" ]; then
        log_error "Ambiente ${service}-${name} no existe"
        exit 1
    fi

    log_warning "Esto eliminara TODOS los datos de ${service}-${name}"
    read -p "Continuar? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Cancelado"
        exit 0
    fi

    log_info "Destruyendo ${service}-${name}..."

    cd "$env_dir"
    docker-compose down -v
    rm -rf "$env_dir"

    log_success "${service}-${name} eliminado completamente"
}

# Listar ambientes
list_environments() {
    log_info "Ambientes virtualizados disponibles:"
    echo ""

    if [ ! -d "$VENV_DIR" ]; then
        echo "  (ninguno)"
        return
    fi

    for env_dir in "$VENV_DIR"/*; do
        if [ -d "$env_dir" ]; then
            local env_name=$(basename "$env_dir")
            local container_name=$(echo "$env_name" | tr '-' '-')

            if docker ps --filter "name=$container_name" --format '{{.Names}}' | grep -q "$container_name"; then
                echo "  ✓ $env_name (running)"
            else
                echo "  ✗ $env_name (stopped)"
            fi
        fi
    done
}

# Activar ambiente (cargar variables)
activate_environment() {
    local service=$1
    local name=$2

    local env_dir="$VENV_DIR/${service}-${name}"

    if [ ! -d "$env_dir" ]; then
        log_error "Ambiente ${service}-${name} no existe"
        exit 1
    fi

    log_success "Ambiente ${service}-${name} activado"
    echo ""
    bash "$env_dir/connection.sh"
    echo ""
    echo "Variables de entorno cargadas en esta sesión"
    echo "Para usar en tu aplicación, ejecuta:"
    echo "  source $env_dir/connection.sh"
}

# Comando principal
main() {
    local command=$1
    local service=$2
    local name=$3
    local port=$4

    case "$command" in
        create)
            check_docker
            case "$service" in
                postgres|postgresql)
                    create_postgres "$name" "$port"
                    ;;
                mysql)
                    create_mysql "$name" "$port"
                    ;;
                redis)
                    create_redis "$name" "$port"
                    ;;
                *)
                    log_error "Servicio no soportado: $service"
                    echo "Servicios: postgres, mysql, redis"
                    exit 1
                    ;;
            esac
            ;;
        start)
            check_docker
            start_environment "$service" "$name"
            ;;
        stop)
            check_docker
            stop_environment "$service" "$name"
            ;;
        destroy)
            check_docker
            destroy_environment "$service" "$name"
            ;;
        list)
            list_environments
            ;;
        activate)
            activate_environment "$service" "$name"
            ;;
        *)
            echo "Sistema de Ambientes Virtualizados"
            echo ""
            echo "Uso:"
            echo "  ./virtualize.sh create <service> <name> [port]"
            echo "  ./virtualize.sh start <service> <name>"
            echo "  ./virtualize.sh stop <service> <name>"
            echo "  ./virtualize.sh destroy <service> <name>"
            echo "  ./virtualize.sh list"
            echo "  ./virtualize.sh activate <service> <name>"
            echo ""
            echo "Servicios:"
            echo "  postgres  - PostgreSQL"
            echo "  mysql     - MySQL"
            echo "  redis     - Redis"
            echo ""
            echo "Ejemplos:"
            echo "  # Crear PostgreSQL para desarrollo"
            echo "  ./virtualize.sh create postgres dev 5432"
            echo ""
            echo "  # Crear MySQL para testing"
            echo "  ./virtualize.sh create mysql test 3307"
            echo ""
            echo "  # Iniciar ambiente"
            echo "  ./virtualize.sh start postgres dev"
            echo ""
            echo "  # Listar ambientes"
            echo "  ./virtualize.sh list"
            echo ""
            echo "  # Activar (cargar variables)"
            echo "  source <(./virtualize.sh activate postgres dev)"
            exit 1
            ;;
    esac
}

# Ejecutar
main "$@"
