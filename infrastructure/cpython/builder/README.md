# CPython Builder - Vagrant VM

**Versión**: 1.0.0
**Referencia**: SPEC-INFRA-001
**Propósito**: Compilar CPython precompilado en entorno reproducible

---

## Descripción

Esta VM Vagrant proporciona un entorno controlado para compilar CPython desde código fuente con configuración reproducible. La VM usa Ubuntu 22.04 LTS, la misma versión que los Dev Containers objetivo.

---

## Prerequisitos

- Vagrant >= 2.3.0
- VirtualBox >= 7.0 (o provider compatible)
- Mínimo 6 GB RAM disponible (VM usa 4 GB)
- Mínimo 20 GB espacio en disco

### Instalación de prerequisitos

**macOS**:
```bash
brew install vagrant
brew install --cask virtualbox
```

**Ubuntu/Debian**:
```bash
# Vagrant
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vagrant

# VirtualBox
sudo apt install virtualbox
```

**Windows**:
- Descargar Vagrant: https://www.vagrantup.com/downloads
- Descargar VirtualBox: https://www.virtualbox.org/wiki/Downloads

---

## Inicio Rápido

### 1. Iniciar VM

Desde el directorio raíz del proyecto:

```bash
cd infrastructure/cpython/builder
vagrant up
```

Primera vez: ~10-15 minutos (descarga box + provisioning)

### 2. Compilar CPython

**Opción A: Desde fuera de VM (recomendado)**:
```bash
# Desde raíz del proyecto
./infrastructure/cpython/scripts/build-cpython.sh 3.12.6
```

**Opción B: Dentro de VM**:
```bash
vagrant ssh
cd /vagrant
./scripts/build-cpython.sh 3.12.6
```

Tiempo de compilación: ~10-15 minutos (con PGO)

### 3. Validar artefacto

**Opción A: Desde fuera de VM (recomendado)**:
```bash
./infrastructure/cpython/scripts/validate-cpython.sh cpython-3.12.6-ubuntu22.04-build1.tgz
```

**Opción B: Dentro de VM**:
```bash
vagrant ssh
cd /vagrant
./scripts/validate-build.sh cpython-3.12.6-ubuntu22.04-build1.tgz
```

### 4. Resultado

Artefactos generados en: `infrastructure/cpython/artifacts/`

```
infrastructure/cpython/artifacts/
  +-- cpython-3.12.6-ubuntu22.04-build1.tgz
  +-- cpython-3.12.6-ubuntu22.04-build1.tgz.sha256
```

---

## Uso Detallado

### Scripts Disponibles

#### build-cpython.sh

**Propósito**: Compilar CPython desde código fuente

**Sintaxis**:
```bash
./scripts/build-cpython.sh <version> [build-number]
```

**Argumentos**:
- `version`: Versión de Python (formato X.Y.Z, ejemplo: 3.12.6)
- `build-number`: Número de build (opcional, default: 1)

**Ejemplos**:
```bash
./scripts/build-cpython.sh 3.12.6        # Build 1 de Python 3.12.6
./scripts/build-cpython.sh 3.12.6 2      # Build 2 (rebuild)
./scripts/build-cpython.sh 3.11.9        # Python 3.11.9
```

**Flags de compilación**:
- `--enable-optimizations`: Profile-Guided Optimization (PGO)
- `--with-lto`: Link-Time Optimization
- `--enable-shared`: Librerías compartidas
- `--with-system-ffi`: Usar libffi del sistema

**Output**:
- Tarball: `cpython-<version>-ubuntu22.04-build<N>.tgz`
- Checksum: `cpython-<version>-ubuntu22.04-build<N>.tgz.sha256`
- Build info: Incluido en `.build-info` dentro del tarball

#### validate-build.sh

**Propósito**: Validar integridad y funcionalidad del artefacto

**Sintaxis**:
```bash
./scripts/validate-build.sh <artifact-name>
```

**Validaciones realizadas** (11 checks):
1. Existencia del artefacto
2. Existencia del checksum
3. Integridad SHA256
4. Tamaño razonable (30-150 MB)
5. Estructura de directorio correcta
6. Binarios presentes
7. Versión del binario
8. Módulos nativos (ssl, sqlite3, uuid, lzma, bz2, zlib, ctypes)
9. pip disponible
10. Build info presente
11. LICENSE presente

**Exit codes**:
- 0: Validación exitosa
- 1: Validación falló

---

## Gestión de VM

### Comandos básicos

```bash
# Iniciar VM
vagrant up

# Conectar a VM
vagrant ssh

# Detener VM (libera RAM)
vagrant halt

# Reiniciar VM
vagrant reload

# Destruir VM (limpieza completa)
vagrant destroy

# Ver estado
vagrant status

# Re-provisionar (actualizar dependencias)
vagrant provision
```

### Recursos de VM

**Configuración actual**:
- RAM: 4 GB
- CPUs: 4 cores
- Disco: ~10 GB (dinámico)

**Modificar recursos** (editar `Vagrantfile`):
```ruby
vb.memory = "8192"  # 8 GB RAM
vb.cpus = 8         # 8 cores
```

---

## Estructura de Directorios

```
infrastructure/cpython/builder/
|
+-- Vagrantfile             # Configuración de VM
+-- bootstrap.sh            # Script de aprovisionamiento
+-- scripts/
|   +-- build-cpython.sh    # Script de compilación
|   +-- validate-build.sh   # Script de validación
+-- utils/                  # Utilidades compartidas
+-- logs/                   # Logs de compilación
+-- config/                 # Configuraciones
+-- README.md               # Este archivo

Carpetas compartidas:
  /vagrant/artifacts/ <-> ../../../artifacts/
```

---

## Troubleshooting

### Error: "VM failed to start"

**Causa**: VirtualBox no instalado o configuración incorrecta

**Solución**:
```bash
# Verificar instalación
vagrant version
vboxmanage --version

# Reinstalar provider
vagrant plugin install vagrant-vbguest
```

### Error: "Compilation failed"

**Causa**: Dependencias faltantes o código fuente corrupto

**Solución**:
```bash
vagrant ssh
cd /vagrant

# Ver logs
tail -50 /tmp/cpython-build/Python-*/make.log

# Limpiar y reintentar
rm -rf /tmp/cpython-build
./scripts/build-cpython.sh 3.12.6
```

### Error: "Module X not found"

**Causa**: Librería dev faltante en provisioning

**Solución**:
```bash
vagrant ssh
sudo apt-get install lib<X>-dev  # Ejemplo: libssl-dev

# Re-compilar
cd /vagrant
./scripts/build-cpython.sh 3.12.6 2  # Nuevo build number
```

### VM muy lenta

**Causa**: Recursos insuficientes

**Solución**:
1. Cerrar aplicaciones que consuman RAM
2. Aumentar recursos en Vagrantfile
3. Considerar compilación nativa (sin VM) si OS es Ubuntu 22.04

### Artefacto muy grande (>150 MB)

**Causa**: Archivos de debug incluidos

**Solución**:
```bash
# Dentro de VM
vagrant ssh
cd /opt/python-X.Y.Z
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete

# Re-empaquetar
cd /opt
sudo tar czf /vagrant/infrastructure/cpython/artifacts/cpython-X.Y.Z-ubuntu22.04-build2.tgz python-X.Y.Z
```

---

## Mantenimiento

### Actualizar dependencias de sistema

```bash
vagrant ssh
sudo apt-get update
sudo apt-get upgrade

# Verificar nuevas versiones
dpkg -l | grep -E "libssl-dev|libsqlite3-dev"
```

### Limpiar builds antiguos

```bash
vagrant ssh

# Limpiar directorio temporal
rm -rf /tmp/cpython-build/*

# Limpiar instalaciones en /opt
sudo rm -rf /opt/python-*
```

### Rebuild semestral

Según SPEC-INFRA-001, se recomienda rebuild cada 6 meses:

```bash
# Destruir VM antigua
vagrant destroy -f

# Recrear con nuevas dependencias
vagrant up

# Compilar versiones activas
./scripts/build-cpython.sh 3.12.6 <nuevo-build-number>
```

---

## Siguiente Fase

Una vez generado y validado el artefacto:

1. Publicar en GitHub Releases:
   ```bash
   gh release create cpython-3.12.6-build1 \
     infrastructure/cpython/artifacts/cpython-3.12.6-ubuntu22.04-build1.tgz \
     infrastructure/cpython/artifacts/cpython-3.12.6-ubuntu22.04-build1.tgz.sha256 \
     --title "CPython 3.12.6 Build 1" \
     --notes "CPython 3.12.6 precompilado para Ubuntu 22.04"
   ```

2. Actualizar `infrastructure/artifacts/ARTIFACTS.md`

3. Proceder a Fase 2: Feature de Dev Container

---

## Referencias

- [SPEC-INFRA-001](../../../docs/specs/SPEC-INFRA-001-cpython-precompilado.md)
- [ADR-008: Features vs Imagen Base](../../../docs/adr/ADR-008-cpython-features-vs-imagen-base.md)
- [CPython Build Instructions](https://devguide.python.org/getting-started/setup-building/)
- [Vagrant Documentation](https://www.vagrantup.com/docs)

---

**Mantenido por**: Equipo Infraestructura IACT
**Última actualización**: 2025-11-06
