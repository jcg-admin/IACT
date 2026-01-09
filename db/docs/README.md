# IACT DevBox - Multi-Database Development Environment

Entorno de desarrollo Vagrant con 3 VMs aisladas para desarrollo local de aplicaciones con múltiples bases de datos.

---

## Descripción

IACT DevBox es un entorno de desarrollo completo que proporciona:

- MariaDB 11.4 para bases de datos MySQL/MariaDB legacy
- PostgreSQL 16 para aplicaciones modernas
- Adminer como interfaz web para gestión de bases de datos

Todas las VMs están conectadas en una red privada host-only, accesibles únicamente desde la máquina host.

---

## Requisitos del Sistema

### Software requerido

- VirtualBox 7.x o superior
- Vagrant 2.x o superior
- Sistema operativo: Windows 10/11, Linux, o macOS
- Espacio en disco: mínimo 10 GB libres
- RAM: mínimo 6 GB (para correr las 3 VMs simultáneamente)

### Opcional

- MySQL Client (para conectar desde host)
- PostgreSQL Client (para conectar desde host)
- Git (para control de versiones)

---

## Arquitectura

El sistema consta de 3 máquinas virtuales independientes:

### VM 1 - MariaDB
- Hostname: iact-mariadb
- IP: 192.168.56.10
- Puerto: 3306
- RAM: 2048 MB
- Base de datos: ivr_legacy

### VM 2 - PostgreSQL
- Hostname: iact-postgres
- IP: 192.168.56.11
- Puerto: 5432
- RAM: 2048 MB
- Base de datos: iact_analytics

### VM 3 - Adminer
- Hostname: iact-adminer
- IP: 192.168.56.12
- Puertos: 80 (HTTP), 443 (HTTPS)
- RAM: 1024 MB
- Interfaz web para gestión de bases de datos

Ver documentación completa de arquitectura en: docs/ARCHITECTURE.md

---

## Inicio Rápido

### Instalación

```bash
# Clonar o descargar el proyecto
cd infrastructure

# Levantar todas las VMs
vagrant up
```

El proceso de aprovisionamiento tarda aproximadamente 6 minutos.

### Verificación

```bash
# Verificar estado de las VMs
vagrant status

# Ejecutar script de verificación
.\scripts\verify-vms.ps1
```

### Acceso a servicios

Adminer Web Interface:
```
http://192.168.56.12
https://192.168.56.12 (con certificado autofirmado)
```

Conexión a MariaDB desde host:
```bash
mysql -h 192.168.56.10 -u django_user -p'django_pass' ivr_legacy
```

Conexión a PostgreSQL desde host:
```bash
PGPASSWORD='django_pass' psql -h 192.168.56.11 -U django_user -d iact_analytics
```

---

## Credenciales

### MariaDB
```
Host:     192.168.56.10
Port:     3306
Database: ivr_legacy
User:     django_user
Password: django_pass
Root:     rootpass123
```

### PostgreSQL
```
Host:     192.168.56.11
Port:     5432
Database: iact_analytics
User:     django_user
Password: django_pass
Postgres: postgrespass123
```

### Adminer
```
URL HTTP:  http://192.168.56.12
URL HTTPS: https://192.168.56.12
```

ADVERTENCIA: Estas credenciales son para DESARROLLO únicamente. 
NO usar en producción.

---

## Gestión de VMs

### Comandos básicos

```bash
# Levantar todas las VMs
vagrant up

# Levantar una VM específica
vagrant up mariadb
vagrant up postgresql
vagrant up adminer

# Ver estado
vagrant status

# Conectar por SSH
vagrant ssh mariadb
vagrant ssh postgresql
vagrant ssh adminer

# Detener VMs
vagrant halt

# Detener una VM específica
vagrant halt mariadb

# Reiniciar
vagrant reload

# Destruir VMs
vagrant destroy

# Destruir y recrear
vagrant destroy -f
vagrant up

# Re-provisionar (aplicar cambios en scripts)
vagrant provision
vagrant provision mariadb
```

---

## Logs de Aprovisionamiento

### Ubicación

Todos los logs se guardan en: `logs/`

Los logs son compartidos entre el host y las VMs (carpeta sincronizada).

### Archivos generados

Después de vagrant up, se generan 10 archivos de log:

```
logs/
├── mariadb_bootstrap.log
├── mariadb_install.log
├── mariadb_setup.log
├── postgres_bootstrap.log
├── postgres_install.log
├── postgres_setup.log
├── adminer_bootstrap.log
├── adminer_install.log
├── adminer_ssl.log
└── adminer_swap.log
```

### Consultar logs

```powershell
# Ver todos los logs
dir logs\*.log

# Buscar errores
Select-String -Path logs\*.log -Pattern "\[ERROR"

# Ver logs de una VM específica
Get-Content logs\mariadb_bootstrap.log

# Ver últimas 20 líneas
Get-Content logs\mariadb_bootstrap.log -Tail 20

# Verificar que completó exitosamente
Select-String -Path logs\*_bootstrap.log -Pattern "completed successfully"
```

---

## Integración con Django

### Configuración de settings.py

```python
DATABASES = {
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_legacy',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.10',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.11',
        'PORT': '5432',
    }
}
```

### Migraciones

```bash
# Aplicar migraciones a base de datos legacy
python manage.py migrate --database=legacy

# Aplicar migraciones a base de datos principal
python manage.py migrate --database=default
```

---

## Scripts de Utilidad

### verify-vms.ps1

Verifica el estado completo del sistema:

```powershell
.\scripts\verify-vms.ps1
```

Revisa:
- Estado de VMs
- Logs generados
- Conectividad de red
- Puertos de servicios
- Acceso HTTP

### clean-logs.ps1

Limpia logs antiguos moviéndolos a archive:

```powershell
.\scripts\clean-logs.ps1
```

---

## Mantenimiento

### Re-provisioning

Si actualizas los scripts de aprovisionamiento:

```bash
# Re-provisionar todas las VMs
vagrant provision

# Re-provisionar una VM específica
vagrant provision mariadb
```

Nota: Con la versión 1.0.0, el re-provisioning es idempotente y no reinstala paquetes innecesariamente.

### Actualizar configuraciones

Si modificas archivos en config/:

```bash
vagrant provision
```

### Limpiar y empezar de cero

```bash
vagrant destroy -f
vagrant up
```

---

## Estructura del Proyecto

```
infrastructure/
├── config/              Archivos de configuración
├── docs/                Documentación
├── logs/                Logs de aprovisionamiento
│   └── archive/         Logs antiguos
├── provisioners/        Scripts de aprovisionamiento
│   ├── adminer/
│   ├── mariadb/
│   └── postgres/
├── scripts/             Scripts de utilidad
├── utils/               Funciones compartidas
├── .gitignore
├── CHANGELOG.md         Historial de cambios
└── Vagrantfile          Configuración de Vagrant
```

---

## Documentación

### Documentos disponibles

- README.md (este archivo): Guía rápida
- docs/ARCHITECTURE.md: Arquitectura detallada
- docs/TROUBLESHOOTING.md: Solución de problemas
- docs/CHANGELOG.md: Historial de versiones
- docs/reference/utils-guide.md: Guía de funciones utils/
- docs/reference/logging-system.md: Sistema de logging

### Temas cubiertos

- Configuración de red
- Flujo de aprovisionamiento
- Sistema de logging
- Backups automáticos
- Seguridad
- Conexión desde aplicaciones

---

## Solución de Problemas

### Problemas comunes

Ver documentación completa en: docs/TROUBLESHOOTING.md

#### VMs no inician

```bash
# Verificar VirtualBox
VBoxManage --version

# Verificar red host-only
VBoxManage list hostonlyifs

# Reiniciar servicio VirtualBox (Windows)
Restart-Service -Name "VBoxSDS"
```

#### Errores de red

```
VERR_INTNET_FLT_IF_NOT_FOUND
```

Solución: Deshabilitar y habilitar adaptador de red en ncpa.cpl

#### Servicios no arrancan

```bash
# SSH a la VM
vagrant ssh mariadb

# Verificar servicio
sudo systemctl status mariadb

# Ver logs del sistema
sudo journalctl -u mariadb -n 50
```

#### No se generan logs

Causa: VMs ya provisionadas previamente

Solución:
```bash
vagrant destroy -f
vagrant up
```

---

## Seguridad

### Alcance

Este entorno está diseñado para DESARROLLO LOCAL únicamente.

### Características de seguridad

- Red privada host-only (no accesible desde Internet)
- Firewall configurado en cada VM
- Acceso limitado a red 192.168.56.0/24
- Certificados SSL autofirmados (para desarrollo)

### Advertencias

1. NO usar en producción
2. NO exponer al Internet
3. Cambiar TODAS las contraseñas para producción
4. Los certificados SSL son autofirmados
5. Las credenciales están en texto plano en configs

---

## Backups Automáticos

El sistema crea backups automáticos de archivos críticos de configuración:

### Archivos con backup

- /etc/mysql/mariadb.conf.d/50-server.cnf
- /etc/postgresql/16/main/pg_hba.conf
- /etc/postgresql/16/main/postgresql.conf
- /etc/apache2/sites-available/adminer.conf
- /etc/apache2/sites-available/adminer-ssl.conf

### Formato de backup

```
archivo.backup.YYYYMMDD_HHMMSS
```

Ejemplo:
```
50-server.cnf.backup.20260101_153045
```

Los backups NO se sobrescriben, permitiendo auditoría completa de cambios.

---

## Performance

### Tiempos de aprovisionamiento

Primera ejecución (vagrant up):
- MariaDB: ~2 min
- PostgreSQL: ~1.5 min
- Adminer: ~2.5 min
- Total: ~6 min

Re-provisioning (vagrant provision):
- MariaDB: ~30 seg
- PostgreSQL: ~30 seg
- Adminer: ~45 seg
- Total: ~2 min

Nota: Los tiempos de re-provisioning son significativamente menores gracias a instalación idempotente.

---

## Contribuir

### Reportar problemas

1. Verificar que no sea un problema conocido (docs/TROUBLESHOOTING.md)
2. Recolectar información:
   - Output de vagrant up
   - Contenido de logs/
   - Versión de VirtualBox y Vagrant
3. Crear issue con información completa

### Mejoras

1. Fork del repositorio
2. Crear rama para feature
3. Probar cambios completamente
4. Actualizar documentación si es necesario
5. Submit pull request

---

## Licencia

Especificar licencia según aplique al proyecto.

---

## Soporte

### Recursos

- Documentación: docs/
- Logs: logs/
- Scripts de diagnóstico: scripts/verify-vms.ps1

### Referencias externas

- VirtualBox: https://www.virtualbox.org/manual/
- Vagrant: https://www.vagrantup.com/docs
- MariaDB: https://mariadb.com/kb/
- PostgreSQL: https://www.postgresql.org/docs/
- Adminer: https://www.adminer.org/

---

## Changelog

Ver CHANGELOG.md para historial completo de versiones.

### Versión actual: 1.0.0

Cambios principales:
- Refactorización completa de provisioners
- Sistema de logging mejorado
- Backups automáticos de configuración
- Estructura de directorios empresarial
- Documentación completa
- Scripts de utilidad

---

## Créditos

IACT DevBox - Entorno de Desarrollo Multi-Base de Datos

Desarrollado para proyectos que requieren múltiples bases de datos en desarrollo local.