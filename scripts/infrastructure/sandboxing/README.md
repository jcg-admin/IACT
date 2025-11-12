# Sistemas de Sandboxing y Virtualización

3 opciones para crear "caparazones" aislados, sin Vagrant:

## 1. `virtualize.sh` - Con Docker

**Usa**: Contenedores Docker

**Ventajas**:
- Servicios reales (PostgreSQL, MySQL, Redis)
- Producción-ready
- Portabilidad

**Desventajas**:
- Requiere Docker
- ~100-500 MB por ambiente
- Inicia en 5-10 segundos

**Uso**:
```bash
./virtualize.sh create postgres dev 5432
./virtualize.sh start postgres dev
./virtualize.sh list
```

## 2. `lightweight_venv.sh` - Solo Bash

**Usa**: Directorios + Variables de entorno

**Ventajas**:
- Ultra-ligero (< 1 MB)
- Instantáneo
- Solo requiere Bash
- Similar a Python venv

**Desventajas**:
- No corre servicio real
- Solo para mocking/testing

**Uso**:
```bash
./lightweight_venv.sh create dev 5432
source .lightvenvs/dev/bin/activate
# Variables DB_* ya cargadas
```

## 3. `wasm_style_sandbox.sh` - Estilo WebAssembly

**Usa**: Linux namespaces del kernel

**Ventajas**:
- Aislamiento REAL (como WASM)
- Sin Docker, sin VM
- Capabilities explícitas
- Filesystem/Network/PID aislados
- Ultra-ligero

**Desventajas**:
- Solo Linux
- Requiere root para aislamiento completo
- Más complejo

**Uso**:
```bash
sudo ./wasm_style_sandbox.sh create postgres dev 5432
sudo ./wasm_style_sandbox.sh run dev
./wasm_style_sandbox.sh inspect dev
```

## Comparación

| Característica | Docker | Lightweight | WASM-style |
|----------------|--------|-------------|------------|
| **Requiere** | Docker | Bash | Linux+unshare |
| **Tamaño** | 100-500 MB | < 1 MB | < 1 MB |
| **Inicio** | 5-10s | Instant | Instant |
| **Aislamiento** | Container | Directorios | Namespaces |
| **Servicio real** | Sí | No | No* |
| **Capabilities** | Implícitas | Ninguna | Explícitas |
| **Root** | No | No | Opcional |

*Puede ejecutar servicio real con namespaces

## Demo Interactivo

```bash
./demo.sh
```

Muestra cómo usar los 3 sistemas paso a paso.

## Cuándo Usar Cada Uno

### Usar Docker (`virtualize.sh`)
- Necesitas PostgreSQL/MySQL real
- Producción o staging
- Tienes Docker instalado
- CI/CD con servicios reales

### Usar Lightweight (`lightweight_venv.sh`)
- Desarrollo rápido
- Testing con mocks
- No necesitas servicio real
- Máquina sin Docker
- Quieres algo instantáneo

### Usar WASM-style (`wasm_style_sandbox.sh`)
- Necesitas aislamiento real
- Seguridad es crítica
- Quieres capabilities explícitas
- Testing de seguridad
- Entiendes namespaces de Linux

## Ejemplos

### Desarrollo local sin Docker

```bash
# Opción 1: Lightweight (más simple)
./lightweight_venv.sh create dev 5432
source .lightvenvs/dev/bin/activate
python3 app.py  # Ve DB_HOST, DB_PORT, etc.

# Opción 2: WASM-style (más seguro)
sudo ./wasm_style_sandbox.sh create postgres dev 5432
sudo ./wasm_style_sandbox.sh run dev
source .sandboxes/dev/activate
python3 app.py
```

### Testing con bases limpias

```bash
# Lightweight: destruir y recrear instantáneo
for test in test1 test2 test3; do
    ./lightweight_venv.sh create $test 5432
    source .lightvenvs/$test/bin/activate
    pytest
    ./lightweight_venv.sh destroy $test
done
```

### Múltiples ambientes simultáneos

```bash
# Docker: servicios reales
./virtualize.sh create postgres dev 5432
./virtualize.sh create mysql staging 3307
./virtualize.sh start postgres dev
./virtualize.sh start mysql staging

# O Lightweight: ultra-rápido
./lightweight_venv.sh create dev 5432
./lightweight_venv.sh create staging 5433
./lightweight_venv.sh create prod 5434
```

## Integración con environment_config.py

Todos los sistemas funcionan con `environment_config.py`:

```python
from scripts.ai.shared.environment_config import get_environment_config

config = get_environment_config()
db_config = config.get_database_config()

# Auto-detecta si hay sandbox activo
# Usa variables de entorno: DB_HOST, DB_PORT, etc.
```

## Documentación Completa

Ver: `docs/infrastructure/AMBIENTES_VIRTUALIZADOS.md`
