# IACT DevBox

Entorno de desarrollo multi-base de datos para el proyecto IACT utilizando Vagrant y VirtualBox.

## Descripción

IACT DevBox es un entorno de desarrollo que proporciona tres máquinas virtuales aisladas con:
- MariaDB 11.4 para base de datos legacy (IVR)
- PostgreSQL 16 para analytics y datos modernos
- Adminer 4.8.1 como interfaz web unificada para administración

El entorno está diseñado para desarrollo local en Windows, con configuración automatizada y aprovisionamiento idempotente.

## Características Principales

- Arquitectura de 3 VMs independientes e interconectadas
- Networking privado (192.168.56.0/24)
- Dominio local: adminer.devbox (gestión automática de hosts)
- SSL/HTTPS con Certificate Authority propia
- Provisioning completamente automatizado
- Scripts de utilidades modulares y reutilizables
- Logging detallado de todas las operaciones
- Configuración documentada y reproducible

## Arquitectura del Sistema

```
Host Machine (Windows)
├── IP: 192.168.56.1 (VirtualBox Host-Only)
│
├── VM 1: MariaDB
│   ├── Hostname: iact-mariadb
│   ├── IP: 192.168.56.10
│   ├── Port: 3306
│   ├── Database: ivr_legacy
│   ├── User: django_user / django_pass
│   └── Root: root / rootpass123
│
├── VM 2: PostgreSQL
│   ├── Hostname: iact-postgres
│   ├── IP: 192.168.56.11
│   ├── Port: 5432
│   ├── Database: iact_analytics
│   ├── User: django_user / django_pass
│   └── Superuser: postgres / postgrespass123
│
└── VM 3: Adminer
    ├── Hostname: adminer.devbox
    ├── IP: 192.168.56.12
    ├── Ports: 80 (HTTP), 443 (HTTPS)
    ├── URLs: http://adminer.devbox, https://adminer.devbox
    └── Version: Adminer 4.8.1 (PHP 7.4, Apache 2.4)
```

## Requisitos del Sistema

### Software Requerido

- Windows 10/11 (64-bit)
- VirtualBox 7.0+ ([Descargar](https://www.virtualbox.org/wiki/Downloads))
- Vagrant 2.4+ ([Descargar](https://developer.hashicorp.com/vagrant/downloads))
- PowerShell 5.1+ (incluido en Windows)
- Git for Windows ([Descargar](https://git-scm.com/download/win))

### Hardware Recomendado

- CPU: 4+ cores (Intel/AMD)
- RAM: 8GB+ (sistema usa ~5GB con las 3 VMs)
- Disco: 20GB+ libres (VMs usan ~15GB)
- Red: Adaptador Ethernet o WiFi

### Permisos

- Privilegios de administrador (solo para instalación inicial)
- Capacidad de modificar archivo hosts de Windows
- Firewall: permitir VirtualBox Host-Only Network

## Instalación Rápida

### 1. Clonar o Descargar Proyecto

```powershell
cd D:\Estadia_IACT\proyecto\IACT
# El directorio 'db' debe contener el Vagrantfile
```

### 2. Configurar PowerShell

```powershell
# Verificar si perfil existe
Test-Path $PROFILE

# Si retorna False, crear perfil
New-Item -ItemType File -Path $PROFILE -Force

# Editar perfil
notepad $PROFILE

# Agregar estas líneas al inicio:
$env:PATH = "C:\Program Files\Git\usr\bin;$env:PATH"
$env:VAGRANT_LOG_LEVEL = "INFO"

# Guardar y recargar
. $PROFILE
```

### 3. Levantar VMs

```powershell
cd D:\Estadia_IACT\proyecto\IACT\db

# Primera ejecución (instala vagrant-goodhosts)
vagrant up

# Si pide ejecutar vagrant up de nuevo:
vagrant up
```

### 4. Verificar Instalación

```powershell
# Estado de VMs
vagrant status

# Ping a servicios
ping 192.168.56.10  # MariaDB
ping 192.168.56.11  # PostgreSQL
ping 192.168.56.12  # Adminer
ping adminer.devbox # Dominio

# Abrir Adminer
Start-Process http://adminer.devbox
```

### 5. Instalar Certificado SSL (Opcional pero Recomendado)

```powershell
# Como Administrador
cd D:\Estadia_IACT\proyecto\IACT\db\scripts
.\install-ca-certificate.ps1

# Reiniciar navegadores
# Acceder a: https://adminer.devbox (sin warnings)
```

### 6. Configurar Firewall (Opcional - Elimina UAC Prompts)

```powershell
# Como Administrador (UNA VEZ)
cd D:\Estadia_IACT\proyecto\IACT\db\scripts
.\configure-vagrant-firewall.ps1

# Después de esto, ya no necesitas ejecutar como admin
```

## Uso Básico

### Comandos de Vagrant

```powershell
# Iniciar todas las VMs
vagrant up

# Iniciar una VM específica
vagrant up mariadb
vagrant up postgresql
vagrant up adminer

# Ver estado
vagrant status

# SSH a una VM
vagrant ssh mariadb
vagrant ssh postgresql
vagrant ssh adminer

# Detener VMs
vagrant halt              # Detener todas
vagrant halt mariadb      # Detener una

# Reiniciar VMs
vagrant reload            # Reiniciar todas
vagrant reload adminer    # Reiniciar una

# Reprovisionar (ejecutar scripts de nuevo)
vagrant provision adminer

# Destruir VMs (eliminar completamente)
vagrant destroy           # Destruir todas
vagrant destroy -f mariadb  # Destruir una sin confirmación
```

### Conectar a Bases de Datos

#### MariaDB desde línea de comandos

```powershell
# Conectar como root
mysql -h 192.168.56.10 -u root -p'rootpass123'

# Conectar como usuario Django
mysql -h 192.168.56.10 -u django_user -p'django_pass' -D ivr_legacy

# Ejecutar query directa
mysql -h 192.168.56.10 -u root -p'rootpass123' -e "SHOW DATABASES;"
```

#### PostgreSQL desde línea de comandos

```powershell
# Conectar como superuser
$env:PGPASSWORD='postgrespass123'
psql -h 192.168.56.11 -U postgres

# Conectar como usuario Django
$env:PGPASSWORD='django_pass'
psql -h 192.168.56.11 -U django_user -d iact_analytics

# Ejecutar query directa
$env:PGPASSWORD='postgrespass123'
psql -h 192.168.56.11 -U postgres -c "SELECT version();"
```

#### Adminer (Interfaz Web)

```powershell
# Abrir en navegador
Start-Process http://adminer.devbox
# O: Start-Process https://adminer.devbox (con SSL)
```

Credenciales para login:

**MariaDB**:
- System: MySQL
- Server: 192.168.56.10
- Username: django_user
- Password: django_pass
- Database: ivr_legacy

**PostgreSQL**:
- System: PostgreSQL
- Server: 192.168.56.11
- Username: django_user
- Password: django_pass
- Database: iact_analytics

### Configuración de Django

```python
# settings.py

DATABASES = {
    # Base de datos legacy (IVR) en MariaDB
    'legacy': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ivr_legacy',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.10',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    
    # Base de datos principal (Analytics) en PostgreSQL
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'iact_analytics',
        'USER': 'django_user',
        'PASSWORD': 'django_pass',
        'HOST': '192.168.56.11',
        'PORT': '5432',
    },
}
```

## Estructura del Proyecto

```
db/
├── Vagrantfile                    # Configuración principal de Vagrant
├── README.md                      # Este archivo
│
├── config/                        # Archivos de configuración
│   ├── vhost.conf                 # VirtualHost HTTP de Adminer
│   ├── vhost_ssl.conf             # VirtualHost HTTPS de Adminer
│   ├── ssl.sh                     # Script de generación de certificados
│   └── certs/                     # Certificados SSL (generados)
│       ├── ca/
│       │   ├── ca.crt             # Certificate Authority
│       │   └── ca.key             # CA Private Key
│       ├── adminer.crt            # Certificado de Adminer
│       └── adminer.key            # Clave privada de Adminer
│
├── provisioners/                  # Scripts de provisioning por VM
│   ├── mariadb/
│   │   └── bootstrap.sh           # Provisioner de MariaDB
│   ├── postgresql/
│   │   └── bootstrap.sh           # Provisioner de PostgreSQL
│   └── adminer/
│       └── bootstrap.sh           # Provisioner de Adminer
│
├── scripts/                       # Scripts de utilidades para host
│   ├── install-ca-certificate.ps1           # Instalar CA en Windows
│   └── configure-vagrant-firewall.ps1       # Configurar firewall
│
├── utils/                         # Utilidades compartidas (en VMs)
│   ├── core.sh                    # Funciones core
│   ├── logging.sh                 # Sistema de logging
│   ├── network.sh                 # Utilidades de red
│   └── validation.sh              # Validaciones
│
├── logs/                          # Logs de provisioning (generados)
│   ├── mariadb/
│   ├── postgresql/
│   └── adminer/
│
└── docs/                          # Documentación técnica
    ├── INSTALAR_CA_WINDOWS.md
    ├── VAGRANT_2.4.7_WORKAROUND.md
    ├── VERIFICACION_COMPLETA.md
    ├── TROUBLESHOOTING_COMPLETO.md
    ├── PERFILES_POWERSHELL.md
    └── ANALISIS_PROBLEMA_SSH_VAGRANT.md
```

## Gestión de Datos

### Backups

Los datos de las bases de datos están dentro de las VMs. Para hacer backup:

```bash
# SSH a la VM correspondiente
vagrant ssh mariadb

# MariaDB - Dump de base de datos
sudo mysqldump -u root -p'rootpass123' ivr_legacy > /vagrant/backup_ivr_legacy.sql

# PostgreSQL - Dump de base de datos
vagrant ssh postgresql
sudo -u postgres pg_dump iact_analytics > /vagrant/backup_iact_analytics.sql
```

Los archivos quedarán en el directorio del proyecto (synced folder).

### Restaurar Datos

```bash
# MariaDB
vagrant ssh mariadb
sudo mysql -u root -p'rootpass123' ivr_legacy < /vagrant/backup_ivr_legacy.sql

# PostgreSQL
vagrant ssh postgresql
sudo -u postgres psql iact_analytics < /vagrant/backup_iact_analytics.sql
```

### Limpiar y Reinstalar

```powershell
# Eliminar todas las VMs y datos
vagrant destroy -f

# Levantar de nuevo (fresh install)
vagrant up
```

## Logs y Debugging

### Ver Logs de Provisioning

```powershell
# Logs locales en host
Get-Content logs\mariadb\mariadb_*.log
Get-Content logs\postgresql\postgresql_*.log
Get-Content logs\adminer\adminer_*.log
```

### Ver Logs del Sistema en VMs

```bash
# SSH a la VM
vagrant ssh adminer

# Ver logs de Apache
sudo tail -f /var/log/apache2/adminer-error.log
sudo tail -f /var/log/apache2/adminer-ssl-error.log

# Ver logs de sistema
sudo journalctl -u apache2 -f

# MariaDB logs
vagrant ssh mariadb
sudo tail -f /var/log/mysql/error.log

# PostgreSQL logs
vagrant ssh postgresql
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

### Verificación de Estado

```bash
# En cada VM, verificar servicio
vagrant ssh mariadb
sudo systemctl status mariadb

vagrant ssh postgresql
sudo systemctl status postgresql

vagrant ssh adminer
sudo systemctl status apache2
```

## Troubleshooting

### Problema: VMs no arrancan

```powershell
# Verificar VirtualBox
VBoxManage list vms

# Verificar red Host-Only
VBoxManage list hostonlyifs

# Reiniciar adaptador de red
# Win+R -> ncpa.cpl
# VirtualBox Host-Only Network -> Deshabilitar/Habilitar
```

### Problema: No se puede conectar a bases de datos

```powershell
# Verificar que VMs están corriendo
vagrant status

# Test de conectividad
Test-NetConnection -ComputerName 192.168.56.10 -Port 3306
Test-NetConnection -ComputerName 192.168.56.11 -Port 5432

# Ver logs
vagrant ssh mariadb
sudo systemctl status mariadb
```

### Problema: adminer.devbox no resuelve

```powershell
# Verificar plugin
vagrant plugin list | Select-String goodhosts

# Ver archivo hosts
Get-Content C:\Windows\System32\drivers\etc\hosts | Select-String adminer

# Reinstalar entradas
vagrant reload adminer
```

Para troubleshooting detallado, ver: **docs/TROUBLESHOOTING_COMPLETO.md**

## Seguridad

### Credenciales por Defecto

ADVERTENCIA: Las credenciales en este proyecto son para DESARROLLO LOCAL únicamente. NO usar en producción.

**MariaDB**:
- root: rootpass123
- django_user: django_pass

**PostgreSQL**:
- postgres: postgrespass123
- django_user: django_pass

### Acceso de Red

El entorno usa red privada 192.168.56.0/24:
- Solo accesible desde host machine
- NO accesible desde red externa
- NO accesible desde internet

### Certificados SSL

Los certificados son autofirmados y válidos solo para desarrollo local:
- CA: IACT DevBox Root CA (válido 10 años)
- Certificado Adminer: válido 365 días
- NO usar estos certificados en producción

## Actualizaciones y Mantenimiento

### Actualizar Vagrant

```powershell
# Verificar versión actual
vagrant --version

# Descargar nueva versión de:
# https://developer.hashicorp.com/vagrant/downloads

# Instalar (sobrescribe automáticamente)
```

### Actualizar VirtualBox

```powershell
# Verificar versión
VBoxManage --version

# Descargar nueva versión de:
# https://www.virtualbox.org/wiki/Downloads

# IMPORTANTE: Cerrar todas las VMs antes de actualizar
vagrant halt
```

### Actualizar Plugins de Vagrant

```powershell
# Listar plugins
vagrant plugin list

# Actualizar todos
vagrant plugin update

# Actualizar uno específico
vagrant plugin update vagrant-goodhosts
```

### Reprovisionar VMs

Si hay cambios en scripts de provisioning:

```powershell
# Reprovisionar una VM
vagrant provision adminer

# Reprovisionar todas
vagrant provision

# Forzar reprovisioning completo
vagrant destroy -f
vagrant up
```

## Recursos Adicionales

### Documentación Técnica

- **INSTALAR_CA_WINDOWS.md**: Instalación detallada de certificado CA
- **VAGRANT_2.4.7_WORKAROUND.md**: Solución a bug conocido de Vagrant
- **VERIFICACION_COMPLETA.md**: Checklist de verificación post-instalación
- **TROUBLESHOOTING_COMPLETO.md**: Guía completa de resolución de problemas
- **PERFILES_POWERSHELL.md**: Configuración detallada de PowerShell
- **ANALISIS_PROBLEMA_SSH_VAGRANT.md**: Análisis del problema SSH/PowerShell

### Enlaces Externos

- [Vagrant Documentation](https://developer.hashicorp.com/vagrant/docs)
- [VirtualBox Manual](https://www.virtualbox.org/manual/)
- [MariaDB Documentation](https://mariadb.com/kb/en/documentation/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Adminer Documentation](https://www.adminer.org/)

## Soporte

### Issues Comunes

Antes de reportar un problema, verificar:
1. Versiones de software (Vagrant, VirtualBox)
2. Logs de provisioning en `logs/`
3. Estado de VMs con `vagrant status`
4. Documentación en `docs/TROUBLESHOOTING_COMPLETO.md`

### Script de Diagnóstico

```powershell
# Ejecutar diagnóstico automático
cd D:\Estadia_IACT\proyecto\IACT\db

# Verificación rápida
vagrant status
Test-NetConnection adminer.devbox
```

## Licencia

Este proyecto es para uso interno de IACT. Todos los derechos reservados.

## Contribuciones

Para contribuir al proyecto:
1. Documentar cualquier cambio en la arquitectura
2. Actualizar este README si es necesario
3. Mantener scripts idempotentes
4. Agregar logging apropiado
5. Probar en fresh install antes de commitear

## Changelog

### v2.1.0 (2026-01-10)
- Implementación de dominio adminer.devbox con vagrant-goodhosts
- Certificate Authority para SSL
- Corrección de problema SSH en PowerShell
- Workaround para Vagrant 2.4.7 bug
- Script de configuración de firewall
- Documentación completa

### v2.0.0 (2026-01-10)
- SSL/HTTPS con CA propia
- Certificados firmados por CA
- VirtualHost SSL para Adminer

### v1.0.0 (2026-01-09)
- Arquitectura inicial de 3 VMs
- MariaDB 11.4 + PostgreSQL 16 + Adminer 4.8.1
- Networking host-only configurado
- Scripts de provisioning modulares

---

IACT DevBox v2.1.0
Última actualización: 2026-01-10
