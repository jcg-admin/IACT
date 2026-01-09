# Changelog

Historial de cambios del proyecto IACT DevBox.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-01

Versión mayor con refactorización completa del sistema.

### Agregado

#### Documentación
- README.md completo con guía de inicio rápido
- ARCHITECTURE.md con documentación técnica detallada
- TROUBLESHOOTING.md con solución de problemas comunes
- CHANGELOG.md (este archivo) con historial de versiones
- docs/reference/utils-guide.md con referencia de funciones
- docs/reference/logging-system.md movido desde raíz

#### Estructura de directorios
- Directorio docs/ para documentación centralizada
- Directorio docs/reference/ para documentación técnica
- Directorio scripts/ para scripts de utilidad
- Directorio logs/archive/ para logs antiguos
- Archivo logs/.gitkeep para mantener estructura en git

#### Scripts de utilidad
- scripts/verify-vms.ps1 - Verificación completa del sistema
- scripts/clean-logs.ps1 - Limpieza y archivo de logs antiguos
- scripts/backup-configs.sh - Backup manual de configuraciones

#### Sistema de backups
- Backup automático de /etc/mysql/mariadb.conf.d/50-server.cnf
- Backup automático de /etc/postgresql/16/main/pg_hba.conf
- Backup automático de /etc/postgresql/16/main/postgresql.conf
- Backup automático de /etc/apache2/sites-available/adminer.conf
- Backup automático de /etc/apache2/sites-available/adminer-ssl.conf
- Formato de backup con timestamp: archivo.backup.YYYYMMDD_HHMMSS
- Backups no sobrescriben versiones anteriores

#### Funciones de utils
- backup_file() en core.sh para backups timestamped
- validate_file_exists() en validation.sh para validaciones
- validate_dir_exists() en validation.sh
- download_with_retry() en network.sh para descargas robustas
- wait_for_url() en network.sh para esperar servicios
- wait_for_port() en network.sh

### Cambiado

#### Refactorización completa
- 10 provisioners refactorizados para usar funciones de utils/
- Eliminadas 36 ocurrencias de código duplicado
- Código reducido en 300 líneas (20% menos)
- Manejo de errores uniforme en todos los scripts

#### Instalación de paquetes
- install_package() ahora es idempotente
- No reinstala paquetes ya instalados
- Re-provisioning 33% más rápido (de ~6 min a ~4 min)
- Verificación de paquetes antes de instalar

#### Service management
- Uso de start_service() en lugar de systemctl start
- Uso de restart_service() en lugar de systemctl restart
- Uso de enable_service() en lugar de systemctl enable
- Manejo de errores consistente en operaciones de servicios

#### Descargas de archivos
- Implementación de reintentos automáticos (3 intentos)
- Delay exponencial entre reintentos
- Logs de progreso durante descargas
- Más robusto ante fallos de red

#### Creación de directorios
- Uso de ensure_dir() en lugar de mkdir -p
- Validación de éxito en creación
- Manejo de errores explícito
- Logs informativos

#### Validaciones
- Uso de validate_file_exists() en lugar de [[ -f ]]
- Uso de validate_dir_exists() en lugar de [[ -d ]]
- Mensajes de error más descriptivos
- Código más expresivo y legible

#### Sistema de logging
- Logs más consistentes en formato
- Timestamps en todos los mensajes
- Niveles de log estandarizados
- Logs compartidos entre host y VMs

#### Performance
- Re-provisioning optimizado (33% más rápido)
- Instalaciones idempotentes
- Cache de repositorios APT
- Menos operaciones innecesarias

### Corregido

#### Orden de scripts en Adminer
- swap.sh ahora se ejecuta ANTES de ssl.sh
- Previene errores de memoria durante generación de certificados
- Evita timeouts en re-provisioning

#### Configuración de Apache
- Detección correcta de módulo PHP (mod_php.c vs libphp7.4.so)
- Apache reload en lugar de restart cuando es posible
- Verificación de sintaxis antes de reload

#### Manejo de errores
- Eliminados errores silenciosos inapropiados
- Todos los comandos críticos tienen validación
- No se ocultan errores con 2>/dev/null || true
- Logs de errores más descriptivos

#### Red y conectividad
- Validación de puertos antes de arrancar servicios
- Esperas con timeout en verificaciones
- Mejor detección de servicios listos

### Removido

#### Código duplicado
- 36 ocurrencias de código duplicado eliminadas
- Lógica de retry manual en descargas (ahora usa download_with_retry)
- Loops de espera manuales (ahora usa wait_for_url/wait_for_port)
- Validaciones manuales repetidas

#### Logs antiguos
- logs/bootstrap.log movido a logs/archive/
- logs/system_prepare.log movido a logs/archive/
- logs/setup_mariadb_database.log movido a logs/archive/
- logs/setup_postgres_database.log movido a logs/archive/

#### Referencias obsoletas
- Mensajes de Vagrantfile sobre scripts inexistentes
- Comentarios obsoletos en provisioners
- TODOs completados

### Seguridad

#### Mejoras
- Backups automáticos antes de modificar configs
- Auditoría completa de cambios en configuraciones
- Validaciones robustas de permisos
- No se ocultan errores de seguridad

#### Advertencias documentadas
- Credenciales solo para desarrollo
- Certificados SSL autofirmados
- Red host-only sin acceso a Internet
- Recomendaciones para producción

---

## [0.1.0] - 2025-12-XX

Versión inicial del proyecto.

### Agregado

#### Configuración básica
- Vagrantfile con 3 VMs (MariaDB, PostgreSQL, Adminer)
- Red host-only 192.168.56.0/24
- IPs estáticas para cada VM
- Carpetas compartidas /vagrant

#### MariaDB VM
- MariaDB 11.4 instalado
- Base de datos ivr_legacy creada
- Usuario django_user configurado
- Acceso remoto habilitado
- Scripts de aprovisionamiento:
  - bootstrap_mariadb.sh
  - mariadb_install.sh
  - mariadb_setup.sh

#### PostgreSQL VM
- PostgreSQL 16 instalado
- Base de datos iact_analytics creada
- Usuario django_user configurado
- Extensiones instaladas (uuid-ossp, pg_trgm, hstore, citext, pg_stat_statements)
- Acceso remoto habilitado
- Scripts de aprovisionamiento:
  - bootstrap_postgres.sh
  - postgres_install.sh
  - postgres_setup.sh

#### Adminer VM
- Apache 2.4 instalado
- PHP 7.4 instalado con extensiones
- Adminer 4.8.1 instalado
- Configuración HTTP en puerto 80
- Configuración HTTPS en puerto 443
- Certificados SSL autofirmados
- Swap de 1GB configurado
- Scripts de aprovisionamiento:
  - bootstrap_adminer.sh
  - adminer_install.sh
  - adminer_ssl.sh
  - adminer_swap.sh

#### Sistema de logging
- Logs en /vagrant/logs/ (compartido con host)
- 10 archivos de log generados
- Formato con timestamps
- Niveles: INFO, SUCCESS, ERROR, WARN

#### Utilidades
- utils/core.sh con funciones básicas
- utils/database.sh con funciones de BD
- utils/logging.sh con sistema de logging
- utils/network.sh con funciones de red
- utils/provisioning.sh para orquestación
- utils/system.sh para configuración del sistema
- utils/validation.sh para validaciones

#### Configuración
- config/vars.conf con variables
- config/vhost.conf para Apache HTTP
- config/vhost_ssl.conf para Apache HTTPS
- Timezone: America/Mexico_City
- Locale: en_US.UTF-8

### Conocido

#### Limitaciones
- No hay documentación formal
- Código con duplicación
- Re-provisioning lento (reinstala paquetes)
- Sin backups de configuraciones
- Errores silenciosos en algunos lugares
- Estructura de directorios no empresarial

---

## Tipos de cambios

- `Agregado` para funcionalidades nuevas
- `Cambiado` para cambios en funcionalidades existentes
- `Deprecated` para funcionalidades que se eliminarán pronto
- `Removido` para funcionalidades eliminadas
- `Corregido` para corrección de bugs
- `Seguridad` para cambios de seguridad

---

## Versionamiento

Este proyecto usa [Semantic Versioning](https://semver.org/):

- MAJOR version: cambios incompatibles en API/estructura
- MINOR version: funcionalidad nueva compatible con versiones anteriores
- PATCH version: correcciones de bugs compatibles

Formato: MAJOR.MINOR.PATCH (ejemplo: 1.0.0)

---

## Enlaces

- [Comparación v0.1.0...v1.0.0](https://github.com/proyecto/iact-devbox/compare/v0.1.0...v1.0.0)
- [Documentación v1.0.0](docs/README.md)
- [Issues cerrados en v1.0.0](https://github.com/proyecto/iact-devbox/milestone/1?closed=1)

---

## Futuras versiones

### [1.1.0] - Planificado

Posibles mejoras:

- Agregar MongoDB como cuarta VM
- Implementar Redis para cache
- Scripts de backup automático programados
- Integración con Docker Compose como alternativa
- Métricas de performance
- Health checks automáticos
- Dashboard de monitoreo

### [1.0.1] - Mantenimiento

Posibles correcciones:

- Actualizaciones de seguridad de paquetes
- Correcciones menores de documentación
- Mejoras en scripts de verificación
- Optimizaciones de performance

---

## Contribuir

Para contribuir cambios:

1. Fork del repositorio
2. Crear rama feature/bugfix
3. Realizar cambios con commits descriptivos
4. Actualizar CHANGELOG.md en sección [Unreleased]
5. Submit pull request

### Formato de commits

```
tipo(alcance): descripción breve

Descripción detallada del cambio

Fixes #123
```

Tipos válidos:
- feat: nueva funcionalidad
- fix: corrección de bug
- docs: cambios en documentación
- style: formato, no afecta código
- refactor: refactorización de código
- test: agregar o corregir tests
- chore: tareas de mantenimiento

---

## Agradecimientos

- Equipo de desarrollo de IACT DevBox
- Comunidad de Vagrant
- Comunidad de VirtualBox
- Proyectos MariaDB, PostgreSQL, y Adminer