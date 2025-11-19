# Guía para configurar y operar un self-hosted runner

Esta guía resume **ventajas**, **requisitos** y un **procedimiento endurecido** para instalar un runner autoalojado de GitHub Actions en Linux (ARM64 o x86_64), partiendo de los pasos iniciales que compartiste y agregando controles de seguridad y operatividad.

## Ventajas clave
- **Aislamiento y control**: eliges el sistema operativo, endureces el host (AppArmor/SELinux, firewall) y mantienes los secretos fuera de la infraestructura de GitHub.
- **Dependencias precargadas**: instala toolchains pesados (Android SDK, Docker, CUDA, browsers) y evita reinstalarlos en cada job, reduciendo tiempos y variabilidad.
- **Reducción de costos**: aprovecha hardware propio o reservado, optimiza cachés (npm/pip/gradle), y minimiza minutos facturados en runners hospedados.
- **Conectividad interna**: habilita pruebas y despliegues contra recursos privados (bases de datos, brokers, servicios internos) sin exponerlos a internet.
- **Previsibilidad de performance**: hardware dedicado evita throttling; puedes fijar límites de CPU/RAM por job con cgroups.
- **Flexibilidad de etiquetado**: usa labels (`self-hosted`, `arm64`, `gpu`, `infra`) para enrutar jobs a capacidades específicas.

## Requisitos previos
- Usuario de sistema exclusivo para el runner (sin privilegios de login interactivo ni sudo innecesario).
- Acceso de red saliente a `github.com` y `objects.githubusercontent.com`; sin puertos entrantes abiertos.
- `curl`, `tar`, `shasum`, `systemd` (para servicio), y permisos para abrir puertos salientes 443.
- Token de registro efímero generado desde GitHub (**Settings → Actions → Runners → New self-hosted runner**) con caducidad corta.
- Espacio en disco para cachés (recomendado ≥ 20 GB) y, si usas Docker, cgroups v2 habilitado.

## Instalación paso a paso (Linux)
1. **Preparar usuario y carpeta**
   ```bash
   sudo useradd --create-home --shell /usr/sbin/nologin ghactions
   sudo mkdir -p /opt/actions-runner && sudo chown ghactions:ghactions /opt/actions-runner
   cd /opt/actions-runner
   ```
2. **Descargar binarios del runner** (ajusta la versión según [releases oficiales](https://github.com/actions/runner/releases)). Ejemplo ARM64:
   ```bash
   curl -o actions-runner-linux-arm64-2.329.0.tar.gz -L \
     https://github.com/actions/runner/releases/download/v2.329.0/actions-runner-linux-arm64-2.329.0.tar.gz
   echo "56768348b3d643a6a29d4ad71e9bdae0dc0ef1eb01afe0f7a8ee097b039bfaaf  actions-runner-linux-arm64-2.329.0.tar.gz" | \
     shasum -a 256 -c
   tar xzf actions-runner-linux-arm64-2.329.0.tar.gz
   ```
3. **Configurar el runner con token efímero** (reemplaza `<TOKEN>`):
   ```bash
   sudo -u ghactions ./config.sh \
     --url https://github.com/<ORG>/<REPO> \
     --token <TOKEN> \
     --name "iact-arm64-01" \
     --labels "self-hosted,arm64,ci" \
     --unattended
   ```
5. **Endurecimiento recomendado**
   - Limita permisos del usuario `ghactions` (sin sudo; agrega a `docker` solo si es necesario).
   - Habilita firewall saliente con allow-list a GitHub; bloquea puertos entrantes.
   - Activa actualizaciones automáticas del runner (`./svc.sh install` ya habilita `svc.sh self-update`).
   - Limpia artefactos y cachés periódicamente (`actions-runner/_work/_tool`, `actions-runner/_work/*`).
   - Si usas Docker, habilita `--mtu` correcto y `--log-driver json-file --log-opt max-size=100m` para evitar llenado de disco.

## Uso en workflows
Ejemplo de job apuntando al runner etiquetado:
```yaml
jobs:
  tests:
    runs-on: [self-hosted, arm64, ci]
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Run tests
        run: make test
```

## Operación y mantenimiento
- **Auto-update**: revisar `systemctl status ...` y logs en `/opt/actions-runner/_diag/`. Reinstala si la versión queda obsoleta.
- **Rotación de token**: si comprometes el host, revoca el runner en GitHub y regenera token.
- **Observabilidad**: expone métricas con `promtail`/`node_exporter` si el entorno lo permite; monitorea disco (`df -h`) y memoria.
- **Resiliencia**: usa al menos dos runners por etiqueta crítica para evitar cuellos de botella; considera `--ephemeral` si necesitas aislamiento fuerte por job.

## Limpieza/Desregistro
Para quitar el runner:
```bash
sudo systemctl stop actions.runner.2-Coatl-IACT.iact-arm64-01.service
sudo ./svc.sh uninstall
sudo -u ghactions ./config.sh remove --token <TOKEN>
```

> Mantén este archivo junto a los workflows para que cualquier operador pueda replicar la instalación siguiendo prácticas seguras y actualizadas.
