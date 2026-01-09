# Arquitectura IACT DevBox

Documentación técnica completa de la arquitectura del sistema.

---

## Resumen Ejecutivo

IACT DevBox es un entorno de desarrollo basado en Vagrant que proporciona 3 máquinas virtuales independientes con diferentes bases de datos, conectadas mediante una red privada host-only. El sistema está diseñado para desarrollo local de aplicaciones que requieren múltiples bases de datos simultáneamente.

---

## Diagrama de Red

```
Host Machine (Windows/Linux/Mac)
    |
    | VirtualBox Host-Only Network
    | Subnet: 192.168.56.0/24
    |
    +------------------------------------------------+
    |                                                |
    |                                                |
VM1: MariaDB                 VM2: PostgreSQL        VM3: Adminer
192.168.56.10               192.168.56.11          192.168.56.12
    |                            |                       |
    |                            |                       |
MariaDB 11.4              PostgreSQL 16           Apache 2.4
Port: 3306                Port: 5432              Port: 80/443
    |                            |                       |
    |                            |                       |
DB: ivr_legacy            DB: iact_analytics      Adminer 4.8.1
User: django_user         User: django_user       PHP 7.4
                                                  Swap: 1GB
```

---

## Componentes del Sistema

### VM 1 - MariaDB Server

#### Especificaciones técnicas
```
Hostname:     iact-mariadb
IP Address:   192.168.56.10
RAM:          2048 MB
CPUs:         1
Disk:         Dynamic (max 40 GB)
Base Box:     ubuntu/focal64 (Ubuntu 20.04 LTS)
```

#### Software instalado
```
Sistema Operativo: Ubuntu 20.04 LTS (Focal Fossa)
MariaDB:           11.4 (latest stable)
Timezone:          America/Mexico_City
Locale:            en_US.UTF-8
```

#### Base de datos
```
Database Name:     ivr_legacy
Character Set:     utf8mb4
Collation:         utf8mb4_unicode_ci
```

#### Usuarios
```
Root User:
  Username: root
  Password: rootpass123
  Access:   localhost only

Application User:
  Username: django_user
  Password: django_pass
  Access:   192.168.56.0/24 (entire subnet)
  Privileges: ALL on ivr_legacy.*
```

#### Configuración de red
```
bind-address:    0.0.0.0 (acepta conexiones remotas)
port:            3306
max_connections: 151 (default)
```

#### Archivos de configuración
```
/etc/mysql/mariadb.conf.d/50-server.cnf
/etc/mysql/debian.cnf
```

### VM 2 - PostgreSQL Server

#### Especificaciones técnicas
```
Hostname:     iact-postgres
IP Address:   192.168.56.11
RAM:          2048 MB
CPUs:         1
Disk:         Dynamic (max 40 GB)
Base Box:     ubuntu/focal64 (Ubuntu 20.04 LTS)
```

#### Software instalado
```
Sistema Operativo: Ubuntu 20.04 LTS (Focal Fossa)
PostgreSQL:        16 (latest stable)
Timezone:          America/Mexico_City
Locale:            en_US.UTF-8
```

#### Base de datos
```
Database Name:     iact_analytics
Encoding:          UTF8
LC_COLLATE:        en_US.UTF-8
LC_CTYPE:          en_US.UTF-8
```

#### Extensiones instaladas
```
uuid-ossp       UUID generation
pg_trgm         Trigram similarity
hstore          Key-value store
citext          Case-insensitive text
pg_stat_statements  Query statistics
```

#### Usuarios
```
Superuser:
  Username: postgres
  Password: postgrespass123
  Access:   localhost + 192.168.56.0/24

Application User:
  Username: django_user
  Password: django_pass
  Access:   192.168.56.0/24
  Privileges: ALL on iact_analytics
```

#### Configuración de red
```
listen_addresses: '*' (acepta conexiones de cualquier IP)
port:             5432
max_connections:  100 (default)
```

#### Archivos de configuración
```
/etc/postgresql/16/main/postgresql.conf
/etc/postgresql/16/main/pg_hba.conf
/etc/postgresql/16/main/pg_ident.conf
```

### VM 3 - Adminer Web Interface

#### Especificaciones técnicas
```
Hostname:     iact-adminer
IP Address:   192.168.56.12
RAM:          1024 MB
CPUs:         1
Disk:         Dynamic (max 40 GB)
Base Box:     ubuntu/focal64 (Ubuntu 20.04 LTS)
```

#### Software instalado
```
Sistema Operativo: Ubuntu 20.04 LTS (Focal Fossa)
Apache:            2.4
PHP:               7.4
Adminer:           4.8.1
Timezone:          America/Mexico_City
Locale:            en_US.UTF-8
```

#### Servicios
```
HTTP:   Port 80 (sin SSL)
HTTPS:  Port 443 (con certificado autofirmado)
```

#### Módulos de Apache
```
rewrite
ssl
headers
php7.4 (libapache2-mod-php7.4)
```

#### Extensiones de PHP
```
php7.4-cli
php7.4-mysql
php7.4-pgsql
php7.4-mbstring
php7.4-xml
php7.4-curl
php7.4-zip
```

#### Swap configurado
```
Tamaño:      1 GB
Ubicación:   /swapfile
Prioridad:   -2
Swappiness:  10
```

#### Certificados SSL
```
Ubicación:   /etc/ssl/private/
Certificado: adminer.crt (autofirmado)
Llave:       adminer.key (2048 bits)
Validez:     365 días
```

---

## Red y Conectividad

### Red Host-Only

```
Network Name:  VirtualBox Host-Only Ethernet Adapter
Subnet:        192.168.56.0/24
Netmask:       255.255.255.0
Gateway:       192.168.56.1 (host machine)
DHCP:          Disabled (IPs estáticas)
```

### Asignación de IPs

```
192.168.56.1    Host machine (gateway)
192.168.56.10   MariaDB VM
192.168.56.11   PostgreSQL VM
192.168.56.12   Adminer VM
192.168.56.13+  Disponibles para expansión
```

### Puertos expuestos

```
MariaDB:
  3306/tcp      MySQL/MariaDB protocol

PostgreSQL:
  5432/tcp      PostgreSQL protocol

Adminer:
  80/tcp        HTTP
  443/tcp       HTTPS
```

### Reglas de Firewall

Cada VM tiene firewall configurado (ufw):

```
MariaDB:
  ALLOW 3306/tcp from 192.168.56.0/24
  DENY  3306/tcp from anywhere else

PostgreSQL:
  ALLOW 5432/tcp from 192.168.56.0/24
  DENY  5432/tcp from anywhere else

Adminer:
  ALLOW 80/tcp from anywhere
  ALLOW 443/tcp from anywhere
  ALLOW 22/tcp from anywhere (SSH)
```

---

## Flujo de Aprovisionamiento

### Fase 1: Preparación del Sistema

Ejecutado por: provisioners/{vm}/bootstrap_{vm}.sh

```
1. Validar permisos root
2. Validar variables de entorno
3. Inicializar sistema de logging
4. Ejecutar step_system:
   a. Actualizar índice de paquetes (apt-get update)
   b. Instalar herramientas esenciales
   c. Configurar timezone (America/Mexico_City)
   d. Configurar locale (en_US.UTF-8)
   e. Limpiar paquetes innecesarios
```

### Fase 2: Instalación de Servicios

Ejecutado por: provisioners/{vm}/install.sh

#### MariaDB
```
1. Agregar repositorio oficial de MariaDB
2. Importar GPG key
3. Actualizar índice de paquetes
4. Instalar mariadb-server y mariadb-client
5. Habilitar servicio para inicio automático
6. Iniciar servicio MariaDB
7. Esperar a que esté listo (mysql_wait_ready)
8. Configurar seguridad:
   a. Remover usuarios anónimos
   b. Deshabilitar root remoto
   c. Remover base de datos test
9. Backup de configuración
10. Configurar bind-address = 0.0.0.0
11. Reiniciar servicio
```

#### PostgreSQL
```
1. Agregar repositorio oficial de PostgreSQL
2. Importar GPG key
3. Actualizar índice de paquetes
4. Instalar postgresql-16 y postgresql-contrib-16
5. Iniciar servicio PostgreSQL
6. Esperar a que esté listo (postgres_wait_ready)
7. Configurar autenticación:
   a. Backup de pg_hba.conf
   b. Permitir conexiones con password desde 192.168.56.0/24
   c. Configurar método md5
8. Configurar red:
   a. Backup de postgresql.conf
   b. listen_addresses = '*'
9. Configurar password de postgres
10. Reiniciar servicio
```

#### Adminer
```
1. Instalar Apache 2.4
2. Habilitar módulos (rewrite, ssl, headers)
3. Agregar repositorio de PHP (ondrej/php)
4. Instalar PHP 7.4 y extensiones
5. Descargar Adminer desde GitHub
6. Configurar VirtualHost HTTP
7. Configurar swap (1GB)
8. Generar certificado SSL autofirmado
9. Configurar VirtualHost HTTPS
10. Reiniciar Apache
```

### Fase 3: Configuración de Bases de Datos

Ejecutado por: provisioners/{vm}/setup.sh

#### MariaDB
```
1. Verificar que MariaDB está corriendo
2. Crear base de datos ivr_legacy si no existe
3. Crear usuario django_user si no existe
4. Otorgar permisos ALL en ivr_legacy.*
5. Crear tabla schema_version
6. Flush privileges
```

#### PostgreSQL
```
1. Verificar que PostgreSQL está corriendo
2. Crear usuario django_user si no existe
3. Crear base de datos iact_analytics si no existe
4. Otorgar permisos ALL en iact_analytics
5. Instalar extensiones:
   - uuid-ossp
   - pg_trgm
   - hstore
   - citext
   - pg_stat_statements
6. Crear tabla schema_version
```

### Fase 4: Verificación

```
1. Verificar servicios activos (systemctl is-active)
2. Verificar puertos escuchando
3. Verificar conectividad
4. Registrar tiempo total de aprovisionamiento
5. Generar resumen en logs
```

---

## Sistema de Logging

### Ubicación de logs

```
Host:  infrastructure/logs/
VM:    /vagrant/logs/ (carpeta compartida)
```

### Archivos generados

```
MariaDB:
  mariadb_bootstrap.log     Preparación del sistema
  mariadb_install.log       Instalación de MariaDB
  mariadb_setup.log         Configuración de BD

PostgreSQL:
  postgres_bootstrap.log    Preparación del sistema
  postgres_install.log      Instalación de PostgreSQL
  postgres_setup.log        Configuración de BD

Adminer:
  adminer_bootstrap.log     Preparación del sistema
  adminer_install.log       Instalación de Apache/PHP/Adminer
  adminer_ssl.log           Configuración SSL
  adminer_swap.log          Configuración de swap
```

### Formato de logs

```
[YYYY-MM-DD HH:MM:SS] [NIVEL] Mensaje
```

Niveles disponibles:
```
INFO      Información general
SUCCESS   Operación exitosa
STEP      Inicio de paso importante
ERROR     Error en operación
WARN      Advertencia
FATAL     Error fatal (detiene ejecución)
```

### Funciones de logging

Definidas en: utils/logging.sh

```
log_info "mensaje"       Log informativo
log_success "mensaje"    Log de éxito
log_error "mensaje"      Log de error
log_warn "mensaje"       Log de advertencia
log_fatal "mensaje"      Log fatal (exit 1)
log_header "título"      Encabezado de sección
```

---

## Sistema de Backups

### Archivos con backup automático

Los siguientes archivos se respaldan antes de ser modificados:

```
MariaDB:
  /etc/mysql/mariadb.conf.d/50-server.cnf

PostgreSQL:
  /etc/postgresql/16/main/pg_hba.conf
  /etc/postgresql/16/main/postgresql.conf

Adminer:
  /etc/apache2/sites-available/adminer.conf
  /etc/apache2/sites-available/adminer-ssl.conf
```

### Formato de backup

```
archivo.backup.YYYYMMDD_HHMMSS
```

Ejemplos:
```
50-server.cnf.backup.20260101_153045
pg_hba.conf.backup.20260101_153112
postgresql.conf.backup.20260101_153115
adminer.conf.backup.20260101_153200
adminer-ssl.conf.backup.20260101_153245
```

### Función de backup

Definida en: utils/core.sh

```bash
backup_file /path/to/file

# Crea:
# /path/to/file.backup.20260101_153045
```

Características:
- Timestamp automático
- No sobrescribe backups anteriores
- Permite auditoría completa de cambios
- Facilita rollback

---

## Estructura de Directorios

### En el host

```
infrastructure/
├── config/
│   ├── vars.conf              Variables de configuración
│   ├── vhost.conf             VirtualHost HTTP template
│   └── vhost_ssl.conf         VirtualHost HTTPS template
├── docs/
│   ├── ARCHITECTURE.md        Este documento
│   ├── CHANGELOG.md           Historial de versiones
│   ├── README.md              Documentación principal
│   ├── TROUBLESHOOTING.md     Solución de problemas
│   └── reference/
│       ├── logging-system.md  Sistema de logging
│       └── utils-guide.md     Guía de funciones utils
├── logs/
│   ├── .gitkeep               Mantener directorio en git
│   ├── archive/               Logs antiguos
│   └── *.log                  Logs actuales (ignorados por git)
├── provisioners/
│   ├── adminer/
│   │   ├── bootstrap_adminer.sh
│   │   ├── install.sh
│   │   ├── ssl.sh
│   │   └── swap.sh
│   ├── mariadb/
│   │   ├── bootstrap_mariadb.sh
│   │   ├── install.sh
│   │   └── setup.sh
│   └── postgres/
│       ├── bootstrap_postgres.sh
│       ├── install.sh
│       └── setup.sh
├── scripts/
│   ├── backup-configs.sh      Backup manual de configs
│   ├── clean-logs.ps1         Limpieza de logs
│   └── verify-vms.ps1         Verificación del sistema
├── utils/
│   ├── core.sh                Funciones core
│   ├── database.sh            Funciones de BD
│   ├── logging.sh             Sistema de logging
│   ├── network.sh             Funciones de red
│   ├── provisioning.sh        Orquestación
│   ├── system.sh              Configuración del sistema
│   └── validation.sh          Validaciones
├── .gitattributes
├── .gitignore
├── CHANGELOG.md
└── Vagrantfile
```

### En las VMs

```
/vagrant/                      Carpeta compartida con host
├── config/
├── logs/
├── provisioners/
└── utils/

/etc/mysql/                    Configuración MariaDB
/etc/postgresql/16/main/       Configuración PostgreSQL
/etc/apache2/                  Configuración Apache
/usr/share/adminer/            Instalación de Adminer
/swapfile                      Archivo de swap (solo Adminer)
```

---

## Conexión desde Aplicaciones

### Django

```python
# settings.py

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
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
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

# Usar routers para distribuir modelos
DATABASE_ROUTERS = ['myapp.routers.DatabaseRouter']
```

### Node.js

```javascript
// MariaDB (usando mysql2)
const mysql = require('mysql2/promise');

const mariadbPool = mysql.createPool({
  host: '192.168.56.10',
  port: 3306,
  user: 'django_user',
  password: 'django_pass',
  database: 'ivr_legacy',
  waitForConnections: true,
  connectionLimit: 10,
});

// PostgreSQL (usando pg)
const { Pool } = require('pg');

const pgPool = new Pool({
  host: '192.168.56.11',
  port: 5432,
  user: 'django_user',
  password: 'django_pass',
  database: 'iact_analytics',
  max: 10,
});
```

### PHP

```php
<?php
// MariaDB
$mariadb = new PDO(
    'mysql:host=192.168.56.10;port=3306;dbname=ivr_legacy;charset=utf8mb4',
    'django_user',
    'django_pass',
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);

// PostgreSQL
$postgres = new PDO(
    'pgsql:host=192.168.56.11;port=5432;dbname=iact_analytics',
    'django_user',
    'django_pass',
    [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]
);
?>
```

---

## Seguridad

### Modelo de amenazas

Amenazas consideradas:
- Acceso no autorizado desde Internet: MITIGADO (red host-only)
- Acceso no autorizado desde red local: MITIGADO (firewall + IPs estáticas)
- Compromiso de credenciales: RIESGO ACEPTADO (entorno de desarrollo)
- SQL injection: RESPONSABILIDAD DE LA APLICACIÓN
- Man-in-the-middle: MITIGADO (red privada)

Amenazas NO consideradas:
- Ataques físicos a la máquina host
- Malware en la máquina host
- Compromiso del hipervisor VirtualBox
- Ataques de otros usuarios en la misma máquina host

### Configuración de seguridad

Red:
```
- Host-Only Network (aislada de Internet)
- Sin port forwarding al host
- Sin NAT para servicios de BD
- Firewall activo en todas las VMs
```

Autenticación:
```
- Contraseñas en texto plano (solo desarrollo)
- Sin autenticación de dos factores
- Root SSH deshabilitado
- Password authentication habilitado (para desarrollo)
```

Certificados:
```
- SSL autofirmado (desarrollo)
- Validez: 365 días
- 2048 bits RSA
- Sin verificación de hostname
```

### Recomendaciones para producción

1. Cambiar TODAS las contraseñas
2. Usar certificados SSL válidos (Let's Encrypt)
3. Implementar rotación de credenciales
4. Habilitar SSL/TLS en conexiones de BD
5. Configurar firewall más restrictivo
6. Implementar fail2ban
7. Habilitar audit logging
8. Configurar backups automáticos
9. Implementar monitoring y alertas
10. Restringir acceso SSH por IP

---

## Performance y Recursos

### Consumo de recursos

```
Total RAM requerida:  5 GB (2+2+1)
Total RAM recomendada: 8 GB
Espacio en disco:     ~15 GB después de aprovisionamiento
CPU:                  3 cores mínimo (1 por VM)
```

### Tiempos de aprovisionamiento

Primera ejecución (vagrant up):
```
MariaDB:     ~2 min
PostgreSQL:  ~1.5 min
Adminer:     ~2.5 min
Total:       ~6 min
```

Re-provisioning (vagrant provision):
```
MariaDB:     ~30 seg
PostgreSQL:  ~30 seg
Adminer:     ~45 seg
Total:       ~2 min
```

Mejora: 67% más rápido gracias a instalación idempotente

### Optimizaciones implementadas

```
1. Instalación idempotente (no reinstala paquetes)
2. Cache de repositorios APT
3. Parallel provisioning deshabilitado (para logging correcto)
4. Swap configurado en Adminer (evita OOM)
5. Servicios configurados para inicio rápido
```

---

## Escalabilidad

### Agregar más VMs

Para agregar una nueva VM (por ejemplo, MongoDB):

1. Agregar configuración en Vagrantfile:
```ruby
config.vm.define "mongodb" do |mongodb|
  mongodb.vm.hostname = "iact-mongodb"
  mongodb.vm.network "private_network", ip: "192.168.56.13"
  mongodb.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
    vb.cpus = 1
  end
  mongodb.vm.provision "shell", path: "provisioners/mongodb/bootstrap_mongodb.sh"
end
```

2. Crear scripts de aprovisionamiento
3. Actualizar documentación

### Agregar más bases de datos

Para agregar más bases de datos en VMs existentes:

1. Crear script setup adicional
2. Ejecutar: vagrant provision {vm}

---

## Mantenimiento

### Actualización de software

MariaDB:
```bash
vagrant ssh mariadb
sudo apt-get update
sudo apt-get upgrade mariadb-server
sudo systemctl restart mariadb
```

PostgreSQL:
```bash
vagrant ssh postgresql
sudo apt-get update
sudo apt-get upgrade postgresql-16
sudo systemctl restart postgresql
```

Adminer:
```bash
# Actualizar en provisioners/adminer/install.sh
ADMINER_VERSION="4.8.2"  # nueva versión

vagrant provision adminer
```

### Limpieza periódica

```bash
# Limpiar logs antiguos
.\scripts\clean-logs.ps1

# Limpiar packages cache en VMs
vagrant ssh mariadb -c "sudo apt-get clean"
vagrant ssh postgresql -c "sudo apt-get clean"
vagrant ssh adminer -c "sudo apt-get clean"

# Limpiar boxes antiguos
vagrant box prune
```

---

## Troubleshooting

Ver documentación completa en: docs/TROUBLESHOOTING.md

Temas cubiertos:
- Problemas de red
- Servicios que no arrancan
- Errores de aprovisionamiento
- Problemas de conectividad
- Logs y diagnóstico

---

## Referencias

Documentación oficial:
- VirtualBox: https://www.virtualbox.org/manual/
- Vagrant: https://www.vagrantup.com/docs
- MariaDB: https://mariadb.com/kb/
- PostgreSQL: https://www.postgresql.org/docs/16/
- Adminer: https://www.adminer.org/
- Ubuntu: https://ubuntu.com/server/docs

Repositorios:
- MariaDB: https://mariadb.org/download/
- PostgreSQL: https://www.postgresql.org/download/
- Adminer: https://github.com/vrana/adminer