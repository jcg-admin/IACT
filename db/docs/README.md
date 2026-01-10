# IACT DevBox

Entorno de desarrollo multi-VM para bases de datos con Vagrant y VirtualBox.

## ¿Qué es IACT DevBox?

IACT DevBox es un entorno de desarrollo completo que proporciona 3 máquinas virtuales pre-configuradas:

- **MariaDB 11.4** - Base de datos legacy (IVR)
- **PostgreSQL 16** - Base de datos principal (Analytics)
- **Adminer 4.8.1** - Interfaz web para administración

Todas las VMs están conectadas en una red Host-Only privada (192.168.56.0/24) y son accesibles desde tu máquina host.

## Quick Start

### Prerequisitos

- **VirtualBox** 7.0+ → [Descargar](https://www.virtualbox.org/)
- **Vagrant** 2.3+ → [Descargar](https://www.vagrantup.com/)
- **RAM**: 6 GB libres (recomendado)
- **Disco**: 20 GB libres

### Setup Inicial (Recomendado)

```powershell
# 1. Verificar requisitos
.\scripts\check-prerequisites.ps1

# 2. Setup automático guiado
.\scripts\setup-environment.ps1
```

El script `setup-environment.ps1` te guiará paso a paso y ejecutará todo automáticamente.

### Setup Manual

```powershell
# 1. Crear VMs
vagrant up

# 2. Verificar que funcionan
.\scripts\verify-vms.ps1

# 3. Probar conectividad
ping 192.168.56.10
ping 192.168.56.11
ping 192.168.56.12
```

## Acceso a Servicios

### MariaDB 11.4

```
IP:       192.168.56.10:3306
Users:    root / django_user
Password: rootpass123 / django_pass
Database: ivr_legacy
```

**Comando:**
```bash
mysql -h 192.168.56.10 -u root -p'rootpass123'
```

### PostgreSQL 16

```
IP:       192.168.56.11:5432
Users:    postgres / django_user
Password: postgrespass123 / django_pass
Database: iact_analytics
```

**Comando:**
```bash
psql -h 192.168.56.11 -U postgres
```

### Adminer (Web Interface)

```
HTTP:  http://192.168.56.12
HTTPS: https://192.168.56.12
```

**Acceso desde navegador:**
- Usuario: root / postgres / django_user
- Contraseñas: ver arriba

## Scripts de Utilidad

IACT DevBox incluye 7 scripts PowerShell para facilitar el manejo del entorno:

| Script | Cuándo Usar | Descripción |
|--------|-------------|-------------|
| `check-prerequisites.ps1` | **Antes** de `vagrant up` | Verifica requisitos del sistema |
| `setup-environment.ps1` | Primera vez | Asistente de setup completo |
| `diagnose-system.ps1` | Hay problemas | Diagnóstico profundo del sistema |
| `fix-network.ps1` | Ghost Network Adapters | Elimina adaptadores duplicados |
| `verify-vms.ps1` | **Después** de `vagrant up` | Verifica que VMs funcionan |
| `clean-logs.ps1` | Mantenimiento | Limpia y archiva logs antiguos |
| `generate-support-bundle.ps1` | Soporte técnico | Genera bundle de diagnóstico |

**Ejemplo de uso:**
```powershell
# Diagnóstico completo
.\scripts\diagnose-system.ps1

# Generar reporte para soporte
.\scripts\generate-support-bundle.ps1 -IncludeLogs
```

## Comandos Vagrant Esenciales

```powershell
vagrant status          # Ver estado de VMs
vagrant up              # Iniciar todas las VMs
vagrant halt            # Detener todas las VMs
vagrant reload          # Reiniciar VMs
vagrant destroy -f      # Eliminar VMs completamente
vagrant ssh mariadb     # SSH a VM específica
```

## Estructura del Proyecto

```
IACT/db/
├── Vagrantfile              # Configuración de VMs
├── scripts/                 # Scripts PowerShell
│   ├── diagnose-system.ps1
│   ├── fix-network.ps1
│   └── ...
├── provisioners/            # Scripts de provisioning (Bash)
│   ├── mariadb/
│   ├── postgres/
│   └── adminer/
├── utils/                   # Funciones compartidas (Bash)
│   ├── core.sh
│   ├── logging.sh
│   └── ...
├── logs/                    # Logs de provisioning
│   └── archive/             # Logs archivados
├── config/                  # Configuración de servicios
├── test/                    # Scripts de prueba
└── docs/                    # Documentación
```

## Documentación Completa

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Comandos rápidos
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Solución de problemas
- **[COMMANDS.md](docs/COMMANDS.md)** - Referencia de comandos
- **[PROVISIONERS.md](docs/PROVISIONERS.md)** - Cómo funcionan los provisioners
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Extender el sistema

## Troubleshooting Rápido

### Problema #1: Error 10060 (Timeout)

**Síntomas:**
- `ping 192.168.56.10` falla con 100% packet loss
- Error de conexión a bases de datos

**Solución:**
```powershell
# 1. Diagnosticar
.\scripts\diagnose-system.ps1

# 2. Si detecta Ghost Network Adapters
.\scripts\fix-network.ps1

# 3. Verificar
.\scripts\verify-vms.ps1
```

### Problema #2: VMs no arrancan

```powershell
# Ver logs de provisioning
Get-ChildItem logs\*.log | Select-String "ERROR"

# Reintentar provisioning
vagrant reload --provision
```

### Problema #3: No puedo conectarme a MariaDB/PostgreSQL

```bash
# MariaDB
vagrant ssh mariadb -c "sudo systemctl status mariadb"

# PostgreSQL
vagrant ssh postgresql -c "sudo systemctl status postgresql"

# Ver logs
vagrant ssh mariadb -c "sudo tail -50 /var/log/mysql/error.log"
vagrant ssh postgresql -c "sudo tail -50 /var/log/postgresql/postgresql-16-main.log"
```

### Problema #4: Adminer HTTPS no funciona

HTTPS está configurado con certificado autofirmado. El browser mostrará warning:

1. Ir a `https://192.168.56.12`
2. Click en "Avanzado" → "Continuar al sitio"
3. Adminer cargará con HTTPS

Ver [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) para todos los problemas.

## Logs y Mantenimiento

Los logs se generan automáticamente en `logs/`:

```
logs/
├── mariadb_bootstrap.log    # Provisioning de MariaDB
├── postgres_bootstrap.log   # Provisioning de PostgreSQL
├── adminer_bootstrap.log    # Provisioning de Adminer
└── diagnose-system_*.log    # Scripts de diagnóstico
```

**Limpiar logs antiguos:**
```powershell
# Mover logs de 30+ días a archive/
.\scripts\clean-logs.ps1

# Comprimir logs archivados
.\scripts\clean-logs.ps1 -Compress

# Limpiar todo (útil para desarrollo)
.\scripts\clean-logs.ps1 -DaysToKeep 0 -Compress -DeleteArchived
```

## Desarrollo

### Modificar Vagrantfile

El `Vagrantfile` define las 3 VMs. Para cambiar configuración:

```ruby
# Ejemplo: Cambiar RAM de MariaDB
config.vm.define "mariadb" do |mariadb|
  mariadb.vm.provider "virtualbox" do |vb|
    vb.memory = 3072  # Cambiar de 2048 a 3072
  end
end
```

### Agregar Scripts de Provisioning

Los provisioners están en `provisioners/<vm>/`:

```bash
# Ejemplo: Agregar paso a MariaDB
# Editar: provisioners/mariadb/bootstrap.sh

log_info "Nuevo paso de configuración"
# ... tu código aquí ...
```

Ver [DEVELOPMENT.md](docs/DEVELOPMENT.md) para detalles.

## Soporte

### Generar Reporte de Diagnóstico

```powershell
# Bundle completo
.\scripts\generate-support-bundle.ps1 -IncludeLogs -IncludeVagrantfile

# Resultado: support-bundle_TIMESTAMP.zip
```

Comparte el archivo `.zip` con el equipo de soporte.

### Recursos

- Logs en: `logs/`
- VirtualBox Logs: `~/.VirtualBox/`
- Vagrant Logs: Agregar `VAGRANT_LOG=debug` antes de comandos

## Licencia

Proyecto interno de IACT para desarrollo.

---

**Versión**: 1.0.0  
**Última actualización**: 2026-01-10
