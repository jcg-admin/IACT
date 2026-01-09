# Guía de Configuración

Documentación completa de todas las opciones de configuración disponibles en el Vagrantfile y cómo personalizar el entorno IACT DevBox.

---

## Índice

1. [Archivo de Configuración](#archivo-de-configuracion)
2. [Recursos de Máquinas Virtuales](#recursos-de-maquinas-virtuales)
3. [Configuración de Red](#configuracion-de-red)
4. [Configuración de Bases de Datos](#configuracion-de-bases-de-datos)
5. [Versiones de Software](#versiones-de-software)
6. [Sistema Operativo](#sistema-operativo)
7. [Plugins de Vagrant](#plugins-de-vagrant)
8. [Configuración Avanzada](#configuracion-avanzada)
9. [Aplicar Cambios](#aplicar-cambios)
10. [Configuraciones de Ejemplo](#configuraciones-de-ejemplo)

---

## Archivo de Configuración

El archivo principal de configuración es `Vagrantfile`, ubicado en el directorio raíz del proyecto.

El Vagrantfile utiliza sintaxis Ruby pero la configuración es sencilla mediante asignación de variables.

---

## Recursos de Máquinas Virtuales

### VM MariaDB

```ruby
MARIADB_MEMORY = "2048"  # RAM en MB
MARIADB_CPUS = "1"       # Número de cores de CPU
```

Valores recomendados según uso:

| Uso | RAM | CPU | Descripción |
|-----|-----|-----|-------------|
| Ligero | 1024 MB | 1 | Desarrollo básico, pocas consultas |
| Normal | 2048 MB | 1 | Desarrollo estándar (predeterminado) |
| Pesado | 4096 MB | 2 | Múltiples consultas, grandes datasets |

### VM PostgreSQL

```ruby
POSTGRES_MEMORY = "2048"  # RAM en MB
POSTGRES_CPUS = "1"       # Número de cores de CPU
```

Valores recomendados según uso:

| Uso | RAM | CPU | Descripción |
|-----|-----|-----|-------------|
| Ligero | 1024 MB | 1 | Desarrollo básico |
| Normal | 2048 MB | 1 | Desarrollo estándar (predeterminado) |
| Pesado | 4096 MB | 2 | Analytics, queries complejos |

### VM Adminer

```ruby
ADMINER_MEMORY = "1024"  # RAM en MB
ADMINER_CPUS = "1"       # Número de cores de CPU
```

Valores recomendados según uso:

| Uso | RAM | CPU | Descripción |
|-----|-----|-----|-------------|
| Ligero | 512 MB | 1 | Uso ocasional |
| Normal | 1024 MB | 1 | Uso regular (predeterminado) |
| Pesado | 2048 MB | 1 | Múltiples usuarios simultáneos |

### Requisitos Totales del Sistema

Configuración predeterminada:
```
RAM total:  5 GB (2 + 2 + 1)
CPUs total: 3 (1 + 1 + 1)
Disco:      ~20 GB después de aprovisionamiento
```

Requisitos del host:
- RAM disponible: Al menos 6-8 GB (considerando SO del host)
- CPU: Procesador multi-core
- Disco: 25 GB disponibles recomendados

### Cómo Cambiar Recursos

Editar Vagrantfile:
```ruby
# Aumentar RAM de MariaDB a 4GB
MARIADB_MEMORY = "4096"

# Aumentar CPUs de PostgreSQL a 2
POSTGRES_CPUS = "2"

# Reducir RAM de Adminer a 512MB
ADMINER_MEMORY = "512"
```

Aplicar cambios:
```bash
vagrant reload mariadb
vagrant reload postgresql
vagrant reload adminer
```

O recargar todas:
```bash
vagrant reload
```

---

## Configuración de Red

### Direcciones IP Estáticas

```ruby
MARIADB_IP = "192.168.56.10"
POSTGRES_IP = "192.168.56.11"
ADMINER_IP = "192.168.56.12"
```

### Reglas para Cambiar IPs

1. Las IPs deben estar en la misma subred: `192.168.56.0/24`
2. Rango válido: `192.168.56.2` - `192.168.56.254`
3. Evitar `192.168.56.1` (gateway del host)
4. Evitar conflictos con otras VMs

### Ejemplo de Cambio de IPs

```ruby
# Usar un rango diferente dentro de la subred
MARIADB_IP = "192.168.56.20"
POSTGRES_IP = "192.168.56.21"
ADMINER_IP = "192.168.56.22"
```

Después de cambiar IPs:
1. Actualizar configuración en aplicaciones cliente
2. Recargar VMs: `vagrant reload`
3. Verificar conectividad: `ping 192.168.56.20`

### Tipo de Red

Predeterminado: Red host-only (privada)
```ruby
mariadb.vm.network "private_network", ip: MARIADB_IP
```

Características:
- Aislada de Internet
- Solo accesible desde host
- Comunicación entre VMs

### Configuraciones Alternativas de Red

Red pública (bridged):
```ruby
mariadb.vm.network "public_network", bridge: "eth0"
```

Port forwarding (acceso desde host):
```ruby
mariadb.vm.network "forwarded_port", guest: 3306, host: 3307
```

Ejemplo: Mapear puerto 3306 de MariaDB a puerto 3307 del host.

---

## Configuración de Bases de Datos

### MariaDB

```ruby
DB_NAME = "ivr_legacy"
DB_USER = "django_user"
DB_PASSWORD = "django_pass"
DB_ROOT_PASSWORD = "rootpass123"
```

### PostgreSQL

```ruby
POSTGRES_DB_NAME = "iact_analytics"
POSTGRES_DB_USER = "django_user"
POSTGRES_DB_PASSWORD = "django_pass"
POSTGRES_PASSWORD = "postgrespass123"
```

### Cambiar Contraseñas

ADVERTENCIA: Las contraseñas predeterminadas son INSEGURAS. Solo para desarrollo.

Para cambiar contraseñas:

1. Editar Vagrantfile:
```ruby
DB_PASSWORD = "mi_contraseña_segura_123!"
DB_ROOT_PASSWORD = "otra_contraseña_segura_456!"
POSTGRES_DB_PASSWORD = "contraseña_postgres_789!"
POSTGRES_PASSWORD = "superuser_password_012!"
```

2. Destruir y recrear VMs:
```bash
vagrant destroy -f
vagrant up
```

Nota: No es posible cambiar contraseñas con `vagrant provision`. Es necesario destruir y recrear.

### Requisitos de Contraseñas Seguras

Para producción o ambientes expuestos:
- Mínimo 16 caracteres
- Incluir mayúsculas, minúsculas, números y símbolos
- Evitar palabras comunes
- Usar contraseñas únicas por ambiente
- Nunca commitear contraseñas reales a git

Herramienta para generar contraseñas:
```bash
# Linux/macOS
openssl rand -base64 24

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 20 | % {[char]$_})
```

### Cambiar Nombres de Bases de Datos

Editar Vagrantfile:
```ruby
DB_NAME = "mi_base_legacy"
POSTGRES_DB_NAME = "mi_analytics_db"
```

Destruir y recrear:
```bash
vagrant destroy -f
vagrant up
```

### Agregar Bases de Datos Adicionales

Opción 1: Modificar scripts de setup

Editar `provisioners/mariadb/setup.sh`:
```bash
# Agregar después de la creación de ivr_legacy
execute_sql "CREATE DATABASE IF NOT EXISTS otra_base CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
execute_sql "GRANT ALL PRIVILEGES ON otra_base.* TO '${DB_USER}'@'%';"
```

Editar `provisioners/postgres/setup.sh`:
```bash
# Agregar después de la creación de iact_analytics
sudo -u postgres psql -c "CREATE DATABASE otra_base OWNER ${POSTGRES_DB_USER};"
```

Aplicar cambios:
```bash
vagrant provision mariadb
vagrant provision postgresql
```

Opción 2: Crear manualmente después

```bash
# MariaDB
vagrant ssh mariadb
mysql -u root -p'rootpass123'
CREATE DATABASE otra_base CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON otra_base.* TO 'django_user'@'%';
FLUSH PRIVILEGES;

# PostgreSQL
vagrant ssh postgresql
sudo -i -u postgres
createdb -O django_user otra_base
```

### Agregar Usuarios Adicionales

MariaDB:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123'

CREATE USER IF NOT EXISTS 'readonly'@'%' IDENTIFIED BY 'readonly_pass';
GRANT SELECT ON ivr_legacy.* TO 'readonly'@'%';
FLUSH PRIVILEGES;
```

PostgreSQL:
```bash
vagrant ssh postgresql
sudo -i -u postgres
psql

CREATE USER readonly WITH PASSWORD 'readonly_pass';
GRANT CONNECT ON DATABASE iact_analytics TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

---

## Versiones de Software

### MariaDB

```ruby
MARIADB_VERSION = "11.4"
```

Versiones disponibles:
- `11.4` - Última estable (predeterminado)
- `11.3` - Estable anterior
- `11.2` - Estable anterior
- `10.11` - LTS (Long Term Support)
- `10.6` - LTS anterior

Para cambiar versión:
1. Editar Vagrantfile
2. Destruir y recrear VM: `vagrant destroy -f mariadb && vagrant up mariadb`

### PostgreSQL

```ruby
POSTGRES_VERSION = "16"
```

Versiones disponibles:
- `16` - Última estable (predeterminado)
- `15` - Estable anterior
- `14` - Estable anterior
- `13` - Aún soportada

Para cambiar versión:
1. Editar Vagrantfile
2. Destruir y recrear VM: `vagrant destroy -f postgresql && vagrant up postgresql`

Nota: Al cambiar versión mayor, revisar compatibilidad de extensiones y sintaxis SQL.

### Adminer

```ruby
ADMINER_VERSION = "4.8.1"
```

Versiones disponibles:
- `4.8.1` - Última estable (predeterminado)
- `4.8.0` - Estable anterior
- `4.7.9` - Versión anterior

Verificar versiones disponibles: https://github.com/vrana/adminer/releases

Para cambiar versión:
1. Editar Vagrantfile
2. Re-provisionar: `vagrant provision adminer`

No es necesario destruir la VM para cambiar versión de Adminer.

---

## Sistema Operativo

### Base Box

```ruby
config.vm.box = "ubuntu/focal64"
```

Predeterminado: Ubuntu 20.04 LTS (Focal Fossa)

Otras opciones disponibles:
- `ubuntu/jammy64` - Ubuntu 22.04 LTS
- `ubuntu/noble64` - Ubuntu 24.04 LTS

### Cambiar Base Box

ADVERTENCIA: Los scripts de aprovisionamiento están optimizados para Ubuntu 20.04. Otras versiones pueden requerir modificaciones.

Para cambiar:
```ruby
config.vm.box = "ubuntu/jammy64"
```

Consideraciones:
- Versiones de PHP pueden diferir
- Paquetes pueden tener nombres diferentes
- Comandos de sistema pueden variar
- Probar exhaustivamente después del cambio

---

## Plugins de Vagrant

### vagrant-cachier (Recomendado)

Cachea paquetes de APT para acelerar re-provisioning.

Instalación:
```bash
vagrant plugin install vagrant-cachier
```

Verificar instalación:
```bash
vagrant plugin list
```

El Vagrantfile ya está configurado para usar este plugin:
```ruby
if Vagrant.has_plugin?("vagrant-cachier")
  config.cache.scope = :box
  config.cache.auto_detect = true
  config.cache.enable :apt
end
```

Beneficios:
- Re-provisioning 30-50% más rápido
- Ahorro de ancho de banda
- Cache compartido entre VMs

### vagrant-vbguest

Mantiene VirtualBox Guest Additions actualizado.

Instalación:
```bash
vagrant plugin install vagrant-vbguest
```

Beneficios:
- Mejor rendimiento de carpetas compartidas
- Mejor integración con VirtualBox
- Actualizaciones automáticas

---

## Configuración Avanzada

### Carpetas Compartidas

Predeterminado:
```ruby
config.vm.synced_folder ".", "/vagrant"
```

El directorio del proyecto se monta en `/vagrant` dentro de cada VM.

Deshabilitar carpeta compartida:
```ruby
config.vm.synced_folder ".", "/vagrant", disabled: true
```

Agregar carpetas adicionales:
```ruby
config.vm.synced_folder "./data", "/data"
config.vm.synced_folder "./backups", "/backups"
```

Opciones de rendimiento:
```ruby
config.vm.synced_folder ".", "/vagrant", type: "nfs"  # Linux/Mac
config.vm.synced_folder ".", "/vagrant", type: "smb"  # Windows
```

### Hostname de VMs

Predeterminado:
```ruby
mariadb.vm.hostname = "iact-mariadb"
postgresql.vm.hostname = "iact-postgres"
adminer.vm.hostname = "iact-adminer"
```

Cambiar hostnames:
```ruby
mariadb.vm.hostname = "dev-mariadb"
postgresql.vm.hostname = "dev-postgres"
adminer.vm.hostname = "dev-adminer"
```

Aplicar con:
```bash
vagrant reload
```

### Configuración de VirtualBox

Opciones adicionales de VirtualBox:
```ruby
mariadb.vm.provider "virtualbox" do |vb|
  vb.memory = MARIADB_MEMORY
  vb.cpus = MARIADB_CPUS
  
  # Opciones adicionales
  vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  vb.customize ["modifyvm", :id, "--ioapic", "on"]
  vb.customize ["modifyvm", :id, "--audio", "none"]
  vb.customize ["modifyvm", :id, "--usb", "off"]
end
```

Opciones útiles:
- `--natdnshostresolver1 on` - Mejora resolución DNS
- `--ioapic on` - Necesario para múltiples CPUs
- `--audio none` - Deshabilita audio (innecesario)
- `--usb off` - Deshabilita USB (innecesario)

### Provisioning Paralelo

Predeterminado: Deshabilitado (para logging correcto)

Habilitar provisioning paralelo:
```ruby
config.vm.provider "virtualbox" do |vb|
  # ... otras configuraciones
end

# Eliminar esta línea si existe:
# config.vm.define ... do |vm|
#   vm.vm.provision ...
# end
```

Nota: Provisioning paralelo es más rápido pero los logs se mezclan.

### Provisioners Personalizados

Agregar scripts de provisioning adicionales:

```ruby
config.vm.define "mariadb" do |mariadb|
  # Provisioners existentes...
  
  # Agregar provisioner personalizado
  mariadb.vm.provision "shell", 
    path: "provisioners/custom/mi_script.sh",
    env: { "CUSTOM_VAR" => "valor" }
end
```

### Limitar VMs a Crear

Comentar VMs que no se necesitan:

```ruby
Vagrant.configure("2") do |config|
  # ... configuración global
  
  # Solo crear PostgreSQL y Adminer, no MariaDB
  # config.vm.define "mariadb" do |mariadb|
  #   ... configuración de MariaDB
  # end
  
  config.vm.define "postgresql" do |postgresql|
    # ... configuración de PostgreSQL
  end
  
  config.vm.define "adminer" do |adminer|
    # ... configuración de Adminer
  end
end
```

Levantar VMs específicas:
```bash
vagrant up postgresql adminer
```

---

## Aplicar Cambios

### Cambios de Recursos (RAM, CPU)

Método: Reload
```bash
vagrant reload mariadb
vagrant reload postgresql
vagrant reload adminer
```

O todas:
```bash
vagrant reload
```

Tiempo: ~30 segundos por VM

### Cambios de Red (IPs)

Método: Reload
```bash
vagrant reload
```

Verificar después:
```bash
vagrant ssh mariadb -c "ip addr show"
ping 192.168.56.10
```

### Cambios de Configuración de Base de Datos

Método: Destruir y recrear
```bash
vagrant destroy -f
vagrant up
```

Esto es necesario para:
- Cambiar contraseñas
- Cambiar nombres de bases de datos
- Cambiar versiones de MariaDB/PostgreSQL

Tiempo: ~6 minutos (aprovisionamiento completo)

### Cambios en Scripts de Provisioning

Método: Provision
```bash
vagrant provision mariadb
vagrant provision postgresql
vagrant provision adminer
```

O todas:
```bash
vagrant provision
```

Tiempo: ~2 minutos con instalación idempotente

### Cambios en Archivos de Configuración (config/)

Método: Provision
```bash
vagrant provision
```

Los scripts copiarán las nuevas configuraciones.

---

## Configuraciones de Ejemplo

### Ambiente de Desarrollo Ligero

Mínimos recursos para desarrollo básico:

```ruby
# Recursos mínimos
MARIADB_MEMORY = "1024"
MARIADB_CPUS = "1"
POSTGRES_MEMORY = "1024"
POSTGRES_CPUS = "1"
ADMINER_MEMORY = "512"
ADMINER_CPUS = "1"

# Total: 2.5 GB RAM, 3 CPUs
```

Uso:
- Laptop con RAM limitada
- Desarrollo de aplicaciones simples
- Testing básico

### Ambiente de Desarrollo Normal

Configuración balanceada (predeterminado):

```ruby
# Recursos balanceados
MARIADB_MEMORY = "2048"
MARIADB_CPUS = "1"
POSTGRES_MEMORY = "2048"
POSTGRES_CPUS = "1"
ADMINER_MEMORY = "1024"
ADMINER_CPUS = "1"

# Total: 5 GB RAM, 3 CPUs
```

Uso:
- Desarrollo estándar
- Testing con datasets moderados
- Uso diario

### Ambiente de Desarrollo Pesado

Máximos recursos para desarrollo intensivo:

```ruby
# Recursos generosos
MARIADB_MEMORY = "4096"
MARIADB_CPUS = "2"
POSTGRES_MEMORY = "4096"
POSTGRES_CPUS = "2"
ADMINER_MEMORY = "2048"
ADMINER_CPUS = "1"

# Total: 10 GB RAM, 5 CPUs
```

Uso:
- Analytics con datasets grandes
- Testing de performance
- Desarrollo de queries complejos
- Múltiples usuarios simultáneos

### Ambiente Solo PostgreSQL

Solo bases de datos PostgreSQL:

```ruby
Vagrant.configure("2") do |config|
  # Configuración global...
  
  # MariaDB deshabilitado
  # config.vm.define "mariadb" do |mariadb|
  # ...
  # end
  
  # PostgreSQL habilitado
  config.vm.define "postgresql" do |postgresql|
    POSTGRES_MEMORY = "4096"  # Más RAM disponible
    POSTGRES_CPUS = "2"
    # ... resto de configuración
  end
  
  # Adminer habilitado
  config.vm.define "adminer" do |adminer|
    # ... configuración
  end
end
```

Levantar:
```bash
vagrant up postgresql adminer
```

### Ambiente Solo MariaDB

Solo bases de datos MariaDB:

```ruby
Vagrant.configure("2") do |config|
  # Configuración global...
  
  # MariaDB habilitado
  config.vm.define "mariadb" do |mariadb|
    MARIADB_MEMORY = "4096"  # Más RAM disponible
    MARIADB_CPUS = "2"
    # ... resto de configuración
  end
  
  # PostgreSQL deshabilitado
  # config.vm.define "postgresql" do |postgresql|
  # ...
  # end
  
  # Adminer habilitado
  config.vm.define "adminer" do |adminer|
    # ... configuración
  end
end
```

Levantar:
```bash
vagrant up mariadb adminer
```

### Ambiente con IPs Personalizadas

Usando diferente rango de IPs:

```ruby
# Rango personalizado (evitar conflictos)
MARIADB_IP = "192.168.56.100"
POSTGRES_IP = "192.168.56.101"
ADMINER_IP = "192.168.56.102"
```

Útil cuando:
- Ya hay VMs usando .10, .11, .12
- Se quiere organización por rangos
- Múltiples proyectos simultáneos

### Ambiente con Versiones Específicas

Versiones antiguas para compatibilidad:

```ruby
# Versiones LTS para compatibilidad
MARIADB_VERSION = "10.11"  # LTS
POSTGRES_VERSION = "14"     # Estable anterior
ADMINER_VERSION = "4.7.9"   # Versión anterior
```

Útil para:
- Compatibilidad con aplicación legacy
- Testing de migraciones
- Replicar ambiente de producción antiguo

---

## Validación de Configuración

### Verificar Sintaxis de Vagrantfile

```bash
vagrant validate
```

Salida esperada:
```
Vagrantfile validated successfully.
```

Si hay errores, corregir antes de ejecutar `vagrant up`.

### Verificar Recursos Asignados

Después de levantar VMs:

```bash
# Verificar RAM
vagrant ssh mariadb -c "free -h"
vagrant ssh postgresql -c "free -h"

# Verificar CPUs
vagrant ssh mariadb -c "nproc"
vagrant ssh postgresql -c "nproc"
```

### Verificar Configuración de Red

```bash
# Verificar IPs asignadas
vagrant ssh mariadb -c "ip addr show enp0s8"
vagrant ssh postgresql -c "ip addr show enp0s8"

# Verificar conectividad desde host
ping 192.168.56.10
ping 192.168.56.11
ping 192.168.56.12
```

### Verificar Versiones Instaladas

```bash
# MariaDB
vagrant ssh mariadb -c "mysql --version"

# PostgreSQL
vagrant ssh postgresql -c "psql --version"

# Adminer (verificar en navegador)
# http://192.168.56.12
```

---

## Variables de Ambiente

### Usar Variables de Ambiente

Crear archivo `.env` (no commitear a git):
```bash
export MARIADB_MEMORY="4096"
export DB_PASSWORD="mi_contraseña_segura"
export POSTGRES_MEMORY="4096"
```

Cargar antes de ejecutar Vagrant:
```bash
source .env
vagrant up
```

En Vagrantfile:
```ruby
MARIADB_MEMORY = ENV['MARIADB_MEMORY'] || "2048"
DB_PASSWORD = ENV['DB_PASSWORD'] || "django_pass"
```

### Archivo de Configuración Local

Crear `Vagrantfile.local` (no commitear):
```ruby
# Configuración local
MARIADB_MEMORY = "8192"
DB_PASSWORD = "mi_contraseña_local"
```

Cargar en Vagrantfile principal:
```ruby
# Al inicio del Vagrantfile
load 'Vagrantfile.local' if File.exist?('Vagrantfile.local')
```

Agregar a `.gitignore`:
```
Vagrantfile.local
.env
```

---

## Solución de Problemas

### Configuración no se aplica

Síntomas:
- Cambios en Vagrantfile no tienen efecto
- VMs usan valores antiguos

Soluciones:
```bash
# 1. Verificar sintaxis
vagrant validate

# 2. Recargar configuración
vagrant reload

# 3. Si persiste, destruir y recrear
vagrant destroy -f
vagrant up
```

### Errores de validación

Error:
```
Vagrantfile syntax error
```

Verificar:
- Sintaxis de Ruby correcta
- Comillas balanceadas
- Variables definidas antes de uso
- Bloques `do ... end` correctamente cerrados

### VMs sin suficiente RAM

Síntomas:
- VMs lentas
- Servicios no arrancan
- OOM (Out of Memory) errors

Solución:
```ruby
# Aumentar RAM
MARIADB_MEMORY = "4096"
POSTGRES_MEMORY = "4096"
```

Verificar RAM disponible en host:
```bash
# Linux/Mac
free -h

# Windows
systeminfo | findstr Memory
```

### Conflictos de IP

Síntomas:
- VMs no accesibles
- Errores de red

Verificar IPs en uso:
```bash
# Ver VMs de Vagrant
vagrant global-status

# Verificar IPs de VirtualBox
VBoxManage list hostonlyifs
```

Cambiar a IPs no usadas:
```ruby
MARIADB_IP = "192.168.56.20"
POSTGRES_IP = "192.168.56.21"
ADMINER_IP = "192.168.56.22"
```

---

## Mejores Prácticas

1. **Documentar cambios**: Anotar en CHANGELOG.md cambios importantes de configuración

2. **Usar control de versiones**: Commitear Vagrantfile pero no credenciales

3. **No commitear secretos**: Usar .env o Vagrantfile.local para credenciales

4. **Validar antes de aplicar**: Siempre ejecutar `vagrant validate`

5. **Probar en desarrollo**: Probar cambios en ambiente de desarrollo antes de producción

6. **Mantener backups**: Crear snapshots antes de cambios importantes
   ```bash
   vagrant snapshot save mariadb backup_antes_cambio
   ```

7. **Empezar pequeño**: Comenzar con recursos mínimos y aumentar según necesidad

8. **Monitorear recursos**: Verificar uso de RAM/CPU con `htop` dentro de VMs

---

## Referencias

- ARCHITECTURE.md - Arquitectura del sistema
- README.md - Documentación general
- ACCESO_BASES_DATOS.md - Conexión a bases de datos
- RESPALDO_RECUPERACION.md - Backups y snapshots
- SEGURIDAD.md - Cambio de contraseñas para producción

---

Última actualización: 02 de enero de 2026
Versión del documento: 1.0.0