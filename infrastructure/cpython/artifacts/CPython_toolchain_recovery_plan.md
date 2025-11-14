# Artefacto: Plan de Recuperación Toolchain CPython

## Contexto acumulado

1. **Entorno Vagrant**
   - El `Vagrantfile` sincroniza `infrastructure/cpython` con `/vagrant` para compartir artefactos con `.devcontainer`.
   - Se habilitó la red interna con nombre explícito y el flujo de bootstrap en `bootstrap.sh` crea el entorno de build sobre Ubuntu 20.04.
2. **Pipeline de artefactos**
   - `.devcontainer/devcontainer.json` consume los artefactos generados por la VM (tarball y checksum) para mantener alineados local y release.
   - `ARTIFACTS.md` registra el inventario de builds publicados y sirve como fuente de verdad para la distribución.
3. **Mejoras recientes**
   - Se documentó el pipeline completo en `README.md` y `docs/infraestructura/CHANGELOG-cpython.md`.
   - `bootstrap.sh` ahora incluye `ensure_toolchain_ready` para reinstalar GCC/Make cuando el estado de la VM se recicla sin toolchain.

## Estado actual del problema

- Durante `vagrant up`, el resumen detecta que `gcc` no está disponible y dispara la autorreparación.
- La fase **Instalar dependencias de build** falla con código de salida 100 tres veces seguidas.
- El log sugiere revisar conectividad de red o configuración de repositorios APT.

## Hipótesis principales

- **Repositorios APT inaccesibles**: proxies corporativos, mirrors bloqueados o falta de DNS.
- **Cache corrompida**: `/var/cache/apt/archives` compartida entre host y VM con paquetes incompletos.
- **Bootstrap parcial previo**: el estado `bootstrap_complete` marcó éxito aunque la toolchain se eliminó luego.

## Plan de acción (tareas y subtareas)

### Tarea 1. Restaurar conectividad APT

1.1 Validar salida de `ping archive.ubuntu.com` dentro de la VM (`vagrant ssh`).

1.2 Ejecutar `sudo apt-get update` y capturar logs en `/vagrant/logs/apt-update.log`.

1.3 Si hay bloqueo por proxy, exportar `http_proxy/https_proxy` en `/etc/apt/apt.conf.d/99proxy` y repetir `apt-get update`.

### Tarea 2. Limpiar y reprovisionar dependencias

2.1 Eliminar cache compartida: `sudo rm -rf /var/cache/apt/archives/*` dentro de la VM.

2.2 Restablecer estados en frío:
```bash
cd /vagrant
source utils/state_manager.sh
reset_operation_state bootstrap_complete
reset_operation_state bootstrap_install_build_deps
reset_operation_state bootstrap_install_tools
```

2.3 Ejecutar manualmente `sudo ./bootstrap.sh --step install-build-deps` para validar instalación.

### Tarea 3. Validar toolchain y registrar artefacto

3.1 Confirmar versiones:
```bash
gcc --version
make --version
python3 --version
```

3.2 Si el bootstrap termina correctamente, generar el tarball con `make validate-cpython` y capturar checksum.

3.3 Actualizar `infrastructure/cpython/artifacts/ARTIFACTS.md` con la nueva entrada y adjuntar logs relevantes en `logs/`.

## Referencias

- `bootstrap.sh`: sección `ensure_toolchain_ready` (restablece estados y relanza steps).
- `utils/state_manager.sh`: utilería para manipular flags persistidos en `/vagrant/.state/`.
- `README.md`: flujo de validación y publicación de artefactos.

## Notas

- Mantener siempre habilitado el caché APT compartido requiere que el host no corrompa descargas; si hay sospecha, montar como `disabled: true` durante la reprovisión.
- Documentar cualquier proxy requerido en `infrastructure/cpython/README.md` bajo sección "Requisitos de Red".

