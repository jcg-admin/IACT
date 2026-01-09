
# Guia de Solucion de Problemas

Soluciones a problemas comunes en IACT DevBox.

---

## Indice

1. [Problemas de Instalacion](#problemas-de-instalacion)
2. [Problemas de Red](#problemas-de-red)
3. [Problemas de Servicios](#problemas-de-servicios)
4. [Problemas de Conectividad](#problemas-de-conectividad)
5. [Problemas de Logs](#problemas-de-logs)
6. [Problemas de Performance](#problemas-de-performance)
7. [Comandos de Diagnostico](#comandos-de-diagnostico)

---

## Problemas de Instalacion

### VMs no inician

Sintoma:
```
vagrant up
Error while creating VM
```

Posibles causas y soluciones:

#### Causa 1: VirtualBox no instalado o version incorrecta

Verificar:
```bash
VBoxManage --version
```

Debe mostrar version 7.x o superior.

Solucion:
```
1. Descargar VirtualBox desde https://www.virtualbox.org/
2. Instalar version 7.x o superior
3. Reiniciar sistema
4. Ejecutar: vagrant up
```

#### Causa 2: Vagrant no instalado o version incorrecta

Verificar:
```bash
vagrant --version
```

Debe mostrar version 2.x o superior.

Solucion:
```
1. Descargar Vagrant desde https://www.vagrantup.com/
2. Instalar version 2.x o superior
3. Reiniciar terminal
4. Ejecutar: vagrant up
```

#### Causa 3: Virtualizacion deshabilitada en BIOS

Sintoma:
```
VT-x is not available
AMD-V is not available
```

Solucion:
```
1. Reiniciar PC
2. Entrar a BIOS (usualmente F2, F10, o DEL)
3. Buscar opcion de virtualizacion:
   - Intel: VT-x, Intel Virtualization Technology
   - AMD: AMD-V, SVM Mode
4. Habilitar la opcion
5. Guardar y salir de BIOS
6. Ejecutar: vagrant up
```

#### Causa 4: Hyper-V habilitado (Windows)

VirtualBox no funciona si Hyper-V esta habilitado.

Verificar:
```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
```

Solucion:
```powershell
# Ejecutar como Administrador
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
Restart-Computer
```

---

## Problemas de Red

### Error: VERR_INTNET_FLT_IF_NOT_FOUND

Sintoma:
```
Failed to open/create the internal network
VERR_INTNET_FLT_IF_NOT_FOUND
```

Este es el error mas comun relacionado con red.

#### Solucion 1: Deshabilitar y habilitar adaptador manualmente

Windows:
```
1. Presionar Win+R
2. Escribir: ncpa.cpl
3. Buscar "VirtualBox Host-Only Network"
4. Click derecho -> Deshabilitar
5. Esperar 5 segundos
6. Click derecho -> Habilitar
7. Ejecutar: vagrant up
```

#### Solucion 2: Usar script automatico

```powershell
# Ejecutar como Administrador
.\scripts\fix_vbox_network_windows.ps1
```

#### Solucion 3: Recrear adaptador

```bash
# Eliminar adaptador existente
VBoxManage hostonlyif remove "VirtualBox Host-Only Ethernet Adapter"

# Crear nuevo adaptador
VBoxManage hostonlyif create

# Configurar IP
VBoxManage hostonlyif ipconfig "VirtualBox Host-Only Ethernet Adapter" --ip 192.168.56.1 --netmask 255.255.255.0

# Ejecutar: vagrant up
```

### No se puede hacer ping a las VMs

Sintoma:
```powershell
ping 192.168.56.10
Request timed out
```

#### Causa 1: VM no esta corriendo

Verificar:
```bash
vagrant status
```

Solucion:
```bash
vagrant up
```

#### Causa 2: Firewall de Windows bloqueando ICMP

Solucion:
```powershell
# Ejecutar como Administrador
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Enabled True -Direction Inbound
```

#### Causa 3: Red mal configurada

Verificar configuracion de red:
```bash
vagrant ssh mariadb
ip addr show
```

Debe mostrar:
```
enp0s8: 192.168.56.10
```

Si no aparece:
```bash
vagrant reload mariadb
```

### Adaptador de red no existe

Sintoma:
```
No host only network matching ... could be found
```

Solucion:
```bash
# Crear adaptador host-only
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig "VirtualBox Host-Only Ethernet Adapter" --ip 192.168.56.1

# Verificar
VBoxManage list hostonlyifs
```

---

## Problemas de Servicios

### MariaDB no inicia

#### Diagnostico

```bash
vagrant ssh mariadb

# Verificar status
sudo systemctl status mariadb

# Ver logs
sudo journalctl -u mariadb -n 50 --no-pager

# Ver log de MariaDB
sudo tail -50 /var/log/mysql/error.log
```

#### Causa 1: Puerto ya en uso

Sintoma en logs:
```
Can't start server: Bind on TCP/IP port: Address already in use
```

Verificar:
```bash
sudo netstat -tulpn | grep 3306
```

Solucion:
```bash
# Matar proceso que usa el puerto
sudo kill -9 <PID>

# O cambiar puerto en configuracion
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
# Cambiar: port = 3307

sudo systemctl restart mariadb
```

#### Causa 2: Archivos de datos corruptos

Sintoma en logs:
```
InnoDB: Corrupted page
```

Solucion:
```bash
# Backup de datos
sudo cp -r /var/lib/mysql /var/lib/mysql.backup

# Reparar tablas
sudo mysqlcheck -u root -p --all-databases --repair

# O recrear VM
exit
vagrant destroy -f mariadb
vagrant up mariadb
```

#### Causa 3: Sin espacio en disco

Verificar:
```bash
df -h
```

Solucion:
```bash
# Limpiar logs antiguos
sudo journalctl --vacuum-time=7d

# Limpiar cache de APT
sudo apt-get clean

# Aumentar disco en Vagrantfile si es necesario
```

### PostgreSQL no inicia

#### Diagnostico

```bash
vagrant ssh postgresql

# Verificar status
sudo systemctl status postgresql

# Ver logs
sudo journalctl -u postgresql -n 50 --no-pager

# Ver log de PostgreSQL
sudo tail -50 /var/log/postgresql/postgresql-16-main.log
```

#### Causa 1: Puerto ya en uso

Verificar:
```bash
sudo netstat -tulpn | grep 5432
```

Solucion similar a MariaDB.

#### Causa 2: Configuracion invalida

Sintoma en logs:
```
FATAL: configuration file contains errors
```

Verificar sintaxis:
```bash
sudo -u postgres /usr/lib/postgresql/16/bin/postgres -C config_file
```

Solucion:
```bash
# Restaurar desde backup
sudo cp /etc/postgresql/16/main/postgresql.conf.backup.* /etc/postgresql/16/main/postgresql.conf

sudo systemctl restart postgresql
```

#### Causa 3: Cluster corrupto

Sintoma en logs:
```
PANIC: could not locate a valid checkpoint record
```

Solucion:
```bash
# Recrear VM
exit
vagrant destroy -f postgresql
vagrant up postgresql
```

### Apache no inicia (Adminer)

#### Diagnostico

```bash
vagrant ssh adminer

# Verificar status
sudo systemctl status apache2

# Ver logs de error
sudo tail -50 /var/log/apache2/error.log

# Ver logs de acceso
sudo tail -50 /var/log/apache2/access.log

# Verificar sintaxis
sudo apachectl configtest
```

#### Causa 1: Error de sintaxis en configuracion

Sintoma:
```
Syntax error on line X of /etc/apache2/sites-enabled/...
```

Solucion:
```bash
# Ver error especifico
sudo apachectl configtest

# Restaurar configuracion
sudo cp /etc/apache2/sites-available/adminer.conf.backup.* /etc/apache2/sites-available/adminer.conf

sudo systemctl restart apache2
```

#### Causa 2: Puerto ya en uso

Verificar:
```bash
sudo netstat -tulpn | grep :80
```

Solucion:
```bash
# Matar proceso
sudo kill -9 <PID>

sudo systemctl restart apache2
```

#### Causa 3: Modulo PHP no cargado

Sintoma:
```
Unable to load module mod_php
```

Solucion:
```bash
# Re-habilitar modulo
sudo a2enmod php7.4

sudo systemctl restart apache2
```

---

## Problemas de Conectividad

### No puedo conectarme a MariaDB desde host

#### Diagnostico

```bash
# Desde host
mysql -h 192.168.56.10 -u django_user -p'django_pass' -e "SELECT 1;"
```

#### Causa 1: Servicio no corriendo

Verificar:
```bash
vagrant ssh mariadb -c "sudo systemctl status mariadb"
```

Solucion:
```bash
vagrant ssh mariadb -c "sudo systemctl start mariadb"
```

#### Causa 2: Firewall bloqueando

Verificar:
```bash
vagrant ssh mariadb -c "sudo ufw status"
```

Solucion:
```bash
vagrant ssh mariadb
sudo ufw allow from 192.168.56.0/24 to any port 3306
sudo ufw reload
```

#### Causa 3: bind-address incorrecto

Verificar:
```bash
vagrant ssh mariadb
grep bind-address /etc/mysql/mariadb.conf.d/50-server.cnf
```

Debe mostrar:
```
bind-address = 0.0.0.0
```

Si muestra 127.0.0.1:
```bash
sudo sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb
```

#### Causa 4: Usuario sin permisos remotos

Verificar:
```bash
vagrant ssh mariadb
sudo mysql -u root -p'rootpass123' -e "SELECT user, host FROM mysql.user WHERE user='django_user';"
```

Debe mostrar host '%' o '192.168.56.%'.

Si muestra 'localhost':
```bash
sudo mysql -u root -p'rootpass123' -e "GRANT ALL PRIVILEGES ON ivr_legacy.* TO 'django_user'@'%' IDENTIFIED BY 'django_pass';"
sudo mysql -u root -p'rootpass123' -e "FLUSH PRIVILEGES;"
```

### No puedo conectarme a PostgreSQL desde host

#### Diagnostico

```bash
# Desde host (Windows PowerShell)
$env:PGPASSWORD="django_pass"
psql -h 192.168.56.11 -U django_user -d iact_analytics -c "SELECT 1;"
```

#### Causa 1: pg_hba.conf no permite conexiones

Verificar:
```bash
vagrant ssh postgresql
sudo cat /etc/postgresql/16/main/pg_hba.conf | grep "192.168.56"
```

Debe contener:
```
host    all    all    192.168.56.0/24    md5
```

Si no existe:
```bash
sudo bash -c 'echo "host    all    all    192.168.56.0/24    md5" >> /etc/postgresql/16/main/pg_hba.conf'
sudo systemctl restart postgresql
```

#### Causa 2: listen_addresses incorrecto

Verificar:
```bash
vagrant ssh postgresql
sudo grep listen_addresses /etc/postgresql/16/main/postgresql.conf
```

Debe mostrar:
```
listen_addresses = '*'
```

Si no:
```bash
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf
sudo systemctl restart postgresql
```

### Adminer no carga en navegador

#### Sintoma

```
http://192.168.56.12
Unable to connect / Connection refused
```

#### Diagnostico

```bash
# Verificar VM corriendo
vagrant status adminer

# Verificar Apache corriendo
vagrant ssh adminer -c "sudo systemctl status apache2"

# Verificar puerto 80
vagrant ssh adminer -c "sudo netstat -tulpn | grep :80"
```

#### Causa 1: Apache no corriendo

Solucion:
```bash
vagrant ssh adminer -c "sudo systemctl start apache2"
```

#### Causa 2: Archivo index.php no existe

Verificar:
```bash
vagrant ssh adminer -c "ls -la /usr/share/adminer/index.php"
```

Si no existe:
```bash
vagrant provision adminer
```

#### Causa 3: Permisos incorrectos

Verificar:
```bash
vagrant ssh adminer -c "ls -la /usr/share/adminer/"
```

Corregir:
```bash
vagrant ssh adminer
sudo chown -R www-data:www-data /usr/share/adminer
sudo chmod 755 /usr/share/adminer
sudo chmod 644 /usr/share/adminer/index.php
```

---

## Problemas de Logs

### No se generan logs

#### Sintoma

Carpeta logs/ vacia despues de vagrant up.

#### Causa 1: VMs ya provisionadas

Vagrant no re-provisiona VMs que ya existen.

Solucion:
```bash
vagrant provision
```

O:
```bash
vagrant destroy -f
vagrant up
```

#### Causa 2: Directorio logs/ no existe

Crear:
```bash
mkdir logs
```

#### Causa 3: Permisos incorrectos

En Linux/Mac:
```bash
chmod 777 logs/
```

### Logs muestran errores

#### Buscar todos los errores

```powershell
Select-String -Path logs\*.log -Pattern "\[ERROR"
```

#### Ver contexto del error

```powershell
$file = "logs\mariadb_install.log"
$lineNum = (Select-String -Path $file -Pattern "\[ERROR" | Select-Object -First 1).LineNumber

Get-Content $file | Select-Object -Skip ($lineNum - 5) -First 15
```

#### Errores comunes

ERROR: "Failed to install package X"
```
Causa: Repositorio no disponible
Solucion: vagrant provision (reintenta con backoff)
```

ERROR: "Database already exists"
```
Causa: Normal en re-provisioning
Solucion: Ignorar (idempotente)
```

ERROR: "Service failed to start"
```
Causa: Ver seccion de servicios
Solucion: Diagnosticar servicio especifico
```

### Verificar que completo exitosamente

```powershell
Select-String -Path logs\*_bootstrap.log -Pattern "completed successfully"
```

Debe mostrar 3 lineas (una por VM).

Si falta alguna:
```bash
# Ver ultimo error en el log faltante
Select-String -Path logs\<vm>_bootstrap.log -Pattern "\[ERROR"
```

---

## Problemas de Performance

### Re-provisioning muy lento

#### Sintoma

vagrant provision tarda 5+ minutos.

#### Causa: Reinstalando paquetes innecesariamente

Verificar version:
```bash
git describe --tags
```

Si es v0.1.0 o anterior, actualizar a v1.0.0:
```bash
git checkout v1.0.0
vagrant provision
```

v1.0.0 implementa instalacion idempotente (33% mas rapido).

#### Causa: Conexion lenta a Internet

Verificar velocidad:
```bash
vagrant ssh mariadb
curl -o /dev/null http://speedtest.wdc01.softlayer.com/downloads/test10.zip
```

Solucion: Usar mirror local de repositorios.

### VMs consumen mucha RAM

#### Verificar consumo

```bash
VBoxManage list runningvms
VBoxManage showvminfo "iact-mariadb" | grep Memory
```

#### Reducir RAM asignada

Editar Vagrantfile:
```ruby
vb.memory = "1024"  # Reducir de 2048 a 1024
```

Reiniciar:
```bash
vagrant reload
```

Advertencia: MariaDB y PostgreSQL pueden requerir 2GB para performance optima.

### Disco lleno

#### Verificar espacio

```bash
vagrant ssh mariadb
df -h
```

#### Limpiar logs

```bash
sudo journalctl --vacuum-time=7d
sudo apt-get clean
```

#### Limpiar boxes de Vagrant

En host:
```bash
vagrant box prune
```

---

## Comandos de Diagnostico

### Estado general del sistema

```bash
# Estado de VMs
vagrant status
vagrant global-status

# Estado de servicios
vagrant ssh mariadb -c "sudo systemctl status mariadb"
vagrant ssh postgresql -c "sudo systemctl status postgresql"
vagrant ssh adminer -c "sudo systemctl status apache2"
```

### Red y conectividad

```bash
# Ping a VMs
ping 192.168.56.10
ping 192.168.56.11
ping 192.168.56.12

# Verificar puertos (PowerShell)
Test-NetConnection -ComputerName 192.168.56.10 -Port 3306
Test-NetConnection -ComputerName 192.168.56.11 -Port 5432
Test-NetConnection -ComputerName 192.168.56.12 -Port 80

# Ver adaptadores de red
VBoxManage list hostonlyifs
```

### Logs

```bash
# Ver todos los logs
dir logs\*.log

# Buscar errores
Select-String -Path logs\*.log -Pattern "\[ERROR"

# Buscar advertencias
Select-String -Path logs\*.log -Pattern "\[WARN"

# Ver ultimas lineas
Get-Content logs\mariadb_bootstrap.log -Tail 20
```

### Verificacion automatica

```powershell
.\scripts\verify-vms.ps1
```

Ejecuta verificaciones completas:
- Estado de VMs
- Logs generados
- Conectividad de red
- Puertos de servicios
- Acceso HTTP

### Informacion de versiones

```bash
# VirtualBox
VBoxManage --version

# Vagrant
vagrant --version

# Dentro de VMs
vagrant ssh mariadb -c "mysql --version"
vagrant ssh postgresql -c "psql --version"
vagrant ssh adminer -c "php --version"
```

### Logs detallados de Vagrant

```bash
# Verbose output
VAGRANT_LOG=info vagrant up

# Debug output
VAGRANT_LOG=debug vagrant up 2>&1 | tee vagrant-debug.log
```

---

## Reiniciar Todo

Si nada funciona, reiniciar completamente:

```bash
# 1. Detener VMs
vagrant halt

# 2. Destruir VMs
vagrant destroy -f

# 3. Limpiar logs
Remove-Item logs\*.log

# 4. Recrear todo
vagrant up

# 5. Verificar
.\scripts\verify-vms.ps1
```

---

## Obtener Soporte

### Antes de reportar problema

1. Verificar que no es un problema conocido (revisar este documento)
2. Ejecutar script de verificacion:
   ```
   .\scripts\verify-vms.ps1
   ```
3. Recolectar logs:
   ```
   Get-ChildItem logs\*.log | ForEach-Object { Get-Content $_.FullName }
   ```
4. Recolectar informacion del sistema:
   ```
   vagrant --version
   VBoxManage --version
   ```

### Informacion a incluir en reporte

1. Sistema operativo y version
2. Version de VirtualBox
3. Version de Vagrant
4. Output completo de vagrant up
5. Contenido de logs/
6. Output de verify-vms.ps1
7. Pasos para reproducir el problema

---

## Referencias

Documentacion oficial:
- VirtualBox: https://www.virtualbox.org/manual/
- Vagrant: https://www.vagrantup.com/docs
- MariaDB: https://mariadb.com/kb/
- PostgreSQL: https://www.postgresql.org/docs/
- Apache: https://httpd.apache.org/docs/

Foros y comunidad:
- Vagrant: https://discuss.hashicorp.com/c/vagrant/
- VirtualBox: https://forums.virtualbox.org/
- Stack Overflow: https://stackoverflow.com/questions/tagged/vagrant
EOFTRBL

cat /tmp/iact-refactoring/docs/TROUBLESHOOTING.md
Output

# Guia de Solucion de Problemas

Soluciones a problemas comunes en IACT DevBox.

---

## Indice

1. [Problemas de Instalacion](#problemas-de-instalacion)
2. [Problemas de Red](#problemas-de-red)
3. [Problemas de Servicios](#problemas-de-servicios)
4. [Problemas de Conectividad](#problemas-de-conectividad)
5. [Problemas de Logs](#problemas-de-logs)
6. [Problemas de Performance](#problemas-de-performance)
7. [Comandos de Diagnostico](#comandos-de-diagnostico)

---

## Problemas de Instalacion

### VMs no inician

Sintoma:
```
vagrant up
Error while creating VM
```

Posibles causas y soluciones:

#### Causa 1: VirtualBox no instalado o version incorrecta

Verificar:
```bash
VBoxManage --version
```

Debe mostrar version 7.x o superior.

Solucion:
```
1. Descargar VirtualBox desde https://www.virtualbox.org/
2. Instalar version 7.x o superior
3. Reiniciar sistema
4. Ejecutar: vagrant up
```

#### Causa 2: Vagrant no instalado o version incorrecta

Verificar:
```bash
vagrant --version
```

Debe mostrar version 2.x o superior.

Solucion:
```
1. Descargar Vagrant desde https://www.vagrantup.com/
2. Instalar version 2.x o superior
3. Reiniciar terminal
4. Ejecutar: vagrant up
```

#### Causa 3: Virtualizacion deshabilitada en BIOS

Sintoma:
```
VT-x is not available
AMD-V is not available
```

Solucion:
```
1. Reiniciar PC
2. Entrar a BIOS (usualmente F2, F10, o DEL)
3. Buscar opcion de virtualizacion:
   - Intel: VT-x, Intel Virtualization Technology
   - AMD: AMD-V, SVM Mode
4. Habilitar la opcion
5. Guardar y salir de BIOS
6. Ejecutar: vagrant up
```

#### Causa 4: Hyper-V habilitado (Windows)

VirtualBox no funciona si Hyper-V esta habilitado.

Verificar:
```powershell
Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
```

Solucion:
```powershell
# Ejecutar como Administrador
Disable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V-All
Restart-Computer
```

---

## Problemas de Red

### Error: VERR_INTNET_FLT_IF_NOT_FOUND

Sintoma:
```
Failed to open/create the internal network
VERR_INTNET_FLT_IF_NOT_FOUND
```

Este es el error mas comun relacionado con red.

#### Solucion 1: Deshabilitar y habilitar adaptador manualmente

Windows:
```
1. Presionar Win+R
2. Escribir: ncpa.cpl
3. Buscar "VirtualBox Host-Only Network"
4. Click derecho -> Deshabilitar
5. Esperar 5 segundos
6. Click derecho -> Habilitar
7. Ejecutar: vagrant up
```

#### Solucion 2: Usar script automatico

```powershell
# Ejecutar como Administrador
.\scripts\fix_vbox_network_windows.ps1
```

#### Solucion 3: Recrear adaptador

```bash
# Eliminar adaptador existente
VBoxManage hostonlyif remove "VirtualBox Host-Only Ethernet Adapter"

# Crear nuevo adaptador
VBoxManage hostonlyif create

# Configurar IP
VBoxManage hostonlyif ipconfig "VirtualBox Host-Only Ethernet Adapter" --ip 192.168.56.1 --netmask 255.255.255.0

# Ejecutar: vagrant up
```

### No se puede hacer ping a las VMs

Sintoma:
```powershell
ping 192.168.56.10
Request timed out
```

#### Causa 1: VM no esta corriendo

Verificar:
```bash
vagrant status
```

Solucion:
```bash
vagrant up
```

#### Causa 2: Firewall de Windows bloqueando ICMP

Solucion:
```powershell
# Ejecutar como Administrador
New-NetFirewallRule -DisplayName "Allow ICMPv4-In" -Protocol ICMPv4 -IcmpType 8 -Enabled True -Direction Inbound
```

#### Causa 3: Red mal configurada

Verificar configuracion de red:
```bash
vagrant ssh mariadb
ip addr show
```

Debe mostrar:
```
enp0s8: 192.168.56.10
```

Si no aparece:
```bash
vagrant reload mariadb
```

### Adaptador de red no existe

Sintoma:
```
No host only network matching ... could be found
```

Solucion:
```bash
# Crear adaptador host-only
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig "VirtualBox Host-Only Ethernet Adapter" --ip 192.168.56.1

# Verificar
VBoxManage list hostonlyifs
```

---

## Problemas de Servicios

### MariaDB no inicia

#### Diagnostico

```bash
vagrant ssh mariadb

# Verificar status
sudo systemctl status mariadb

# Ver logs
sudo journalctl -u mariadb -n 50 --no-pager

# Ver log de MariaDB
sudo tail -50 /var/log/mysql/error.log
```

#### Causa 1: Puerto ya en uso

Sintoma en logs:
```
Can't start server: Bind on TCP/IP port: Address already in use
```

Verificar:
```bash
sudo netstat -tulpn | grep 3306
```

Solucion:
```bash
# Matar proceso que usa el puerto
sudo kill -9 <PID>

# O cambiar puerto en configuracion
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf
# Cambiar: port = 3307

sudo systemctl restart mariadb
```

#### Causa 2: Archivos de datos corruptos

Sintoma en logs:
```
InnoDB: Corrupted page
```

Solucion:
```bash
# Backup de datos
sudo cp -r /var/lib/mysql /var/lib/mysql.backup

# Reparar tablas
sudo mysqlcheck -u root -p --all-databases --repair

# O recrear VM
exit
vagrant destroy -f mariadb
vagrant up mariadb
```

#### Causa 3: Sin espacio en disco

Verificar:
```bash
df -h
```

Solucion:
```bash
# Limpiar logs antiguos
sudo journalctl --vacuum-time=7d

# Limpiar cache de APT
sudo apt-get clean

# Aumentar disco en Vagrantfile si es necesario
```

### PostgreSQL no inicia

#### Diagnostico

```bash
vagrant ssh postgresql

# Verificar status
sudo systemctl status postgresql

# Ver logs
sudo journalctl -u postgresql -n 50 --no-pager

# Ver log de PostgreSQL
sudo tail -50 /var/log/postgresql/postgresql-16-main.log
```

#### Causa 1: Puerto ya en uso

Verificar:
```bash
sudo netstat -tulpn | grep 5432
```

Solucion similar a MariaDB.

#### Causa 2: Configuracion invalida

Sintoma en logs:
```
FATAL: configuration file contains errors
```

Verificar sintaxis:
```bash
sudo -u postgres /usr/lib/postgresql/16/bin/postgres -C config_file
```

Solucion:
```bash
# Restaurar desde backup
sudo cp /etc/postgresql/16/main/postgresql.conf.backup.* /etc/postgresql/16/main/postgresql.conf

sudo systemctl restart postgresql
```

#### Causa 3: Cluster corrupto

Sintoma en logs:
```
PANIC: could not locate a valid checkpoint record
```

Solucion:
```bash
# Recrear VM
exit
vagrant destroy -f postgresql
vagrant up postgresql
```

### Apache no inicia (Adminer)

#### Diagnostico

```bash
vagrant ssh adminer

# Verificar status
sudo systemctl status apache2

# Ver logs de error
sudo tail -50 /var/log/apache2/error.log

# Ver logs de acceso
sudo tail -50 /var/log/apache2/access.log

# Verificar sintaxis
sudo apachectl configtest
```

#### Causa 1: Error de sintaxis en configuracion

Sintoma:
```
Syntax error on line X of /etc/apache2/sites-enabled/...
```

Solucion:
```bash
# Ver error especifico
sudo apachectl configtest

# Restaurar configuracion
sudo cp /etc/apache2/sites-available/adminer.conf.backup.* /etc/apache2/sites-available/adminer.conf

sudo systemctl restart apache2
```

#### Causa 2: Puerto ya en uso

Verificar:
```bash
sudo netstat -tulpn | grep :80
```

Solucion:
```bash
# Matar proceso
sudo kill -9 <PID>

sudo systemctl restart apache2
```

#### Causa 3: Modulo PHP no cargado

Sintoma:
```
Unable to load module mod_php
```

Solucion:
```bash
# Re-habilitar modulo
sudo a2enmod php7.4

sudo systemctl restart apache2
```

---

## Problemas de Conectividad

### No puedo conectarme a MariaDB desde host

#### Diagnostico

```bash
# Desde host
mysql -h 192.168.56.10 -u django_user -p'django_pass' -e "SELECT 1;"
```

#### Causa 1: Servicio no corriendo

Verificar:
```bash
vagrant ssh mariadb -c "sudo systemctl status mariadb"
```

Solucion:
```bash
vagrant ssh mariadb -c "sudo systemctl start mariadb"
```

#### Causa 2: Firewall bloqueando

Verificar:
```bash
vagrant ssh mariadb -c "sudo ufw status"
```

Solucion:
```bash
vagrant ssh mariadb
sudo ufw allow from 192.168.56.0/24 to any port 3306
sudo ufw reload
```

#### Causa 3: bind-address incorrecto

Verificar:
```bash
vagrant ssh mariadb
grep bind-address /etc/mysql/mariadb.conf.d/50-server.cnf
```

Debe mostrar:
```
bind-address = 0.0.0.0
```

Si muestra 127.0.0.1:
```bash
sudo sed -i 's/bind-address.*/bind-address = 0.0.0.0/' /etc/mysql/mariadb.conf.d/50-server.cnf
sudo systemctl restart mariadb
```

#### Causa 4: Usuario sin permisos remotos

Verificar:
```bash
vagrant ssh mariadb
sudo mysql -u root -p'rootpass123' -e "SELECT user, host FROM mysql.user WHERE user='django_user';"
```

Debe mostrar host '%' o '192.168.56.%'.

Si muestra 'localhost':
```bash
sudo mysql -u root -p'rootpass123' -e "GRANT ALL PRIVILEGES ON ivr_legacy.* TO 'django_user'@'%' IDENTIFIED BY 'django_pass';"
sudo mysql -u root -p'rootpass123' -e "FLUSH PRIVILEGES;"
```

### No puedo conectarme a PostgreSQL desde host

#### Diagnostico

```bash
# Desde host (Windows PowerShell)
$env:PGPASSWORD="django_pass"
psql -h 192.168.56.11 -U django_user -d iact_analytics -c "SELECT 1;"
```

#### Causa 1: pg_hba.conf no permite conexiones

Verificar:
```bash
vagrant ssh postgresql
sudo cat /etc/postgresql/16/main/pg_hba.conf | grep "192.168.56"
```

Debe contener:
```
host    all    all    192.168.56.0/24    md5
```

Si no existe:
```bash
sudo bash -c 'echo "host    all    all    192.168.56.0/24    md5" >> /etc/postgresql/16/main/pg_hba.conf'
sudo systemctl restart postgresql
```

#### Causa 2: listen_addresses incorrecto

Verificar:
```bash
vagrant ssh postgresql
sudo grep listen_addresses /etc/postgresql/16/main/postgresql.conf
```

Debe mostrar:
```
listen_addresses = '*'
```

Si no:
```bash
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf
sudo systemctl restart postgresql
```

### Adminer no carga en navegador

#### Sintoma

```
http://192.168.56.12
Unable to connect / Connection refused
```

#### Diagnostico

```bash
# Verificar VM corriendo
vagrant status adminer

# Verificar Apache corriendo
vagrant ssh adminer -c "sudo systemctl status apache2"

# Verificar puerto 80
vagrant ssh adminer -c "sudo netstat -tulpn | grep :80"
```

#### Causa 1: Apache no corriendo

Solucion:
```bash
vagrant ssh adminer -c "sudo systemctl start apache2"
```

#### Causa 2: Archivo index.php no existe

Verificar:
```bash
vagrant ssh adminer -c "ls -la /usr/share/adminer/index.php"
```

Si no existe:
```bash
vagrant provision adminer
```

#### Causa 3: Permisos incorrectos

Verificar:
```bash
vagrant ssh adminer -c "ls -la /usr/share/adminer/"
```

Corregir:
```bash
vagrant ssh adminer
sudo chown -R www-data:www-data /usr/share/adminer
sudo chmod 755 /usr/share/adminer
sudo chmod 644 /usr/share/adminer/index.php
```

---

## Problemas de Logs

### No se generan logs

#### Sintoma

Carpeta logs/ vacia despues de vagrant up.

#### Causa 1: VMs ya provisionadas

Vagrant no re-provisiona VMs que ya existen.

Solucion:
```bash
vagrant provision
```

O:
```bash
vagrant destroy -f
vagrant up
```

#### Causa 2: Directorio logs/ no existe

Crear:
```bash
mkdir logs
```

#### Causa 3: Permisos incorrectos

En Linux/Mac:
```bash
chmod 777 logs/
```

### Logs muestran errores

#### Buscar todos los errores

```powershell
Select-String -Path logs\*.log -Pattern "\[ERROR"
```

#### Ver contexto del error

```powershell
$file = "logs\mariadb_install.log"
$lineNum = (Select-String -Path $file -Pattern "\[ERROR" | Select-Object -First 1).LineNumber

Get-Content $file | Select-Object -Skip ($lineNum - 5) -First 15
```

#### Errores comunes

ERROR: "Failed to install package X"
```
Causa: Repositorio no disponible
Solucion: vagrant provision (reintenta con backoff)
```

ERROR: "Database already exists"
```
Causa: Normal en re-provisioning
Solucion: Ignorar (idempotente)
```

ERROR: "Service failed to start"
```
Causa: Ver seccion de servicios
Solucion: Diagnosticar servicio especifico
```

### Verificar que completo exitosamente

```powershell
Select-String -Path logs\*_bootstrap.log -Pattern "completed successfully"
```

Debe mostrar 3 lineas (una por VM).

Si falta alguna:
```bash
# Ver ultimo error en el log faltante
Select-String -Path logs\<vm>_bootstrap.log -Pattern "\[ERROR"
```

---

## Problemas de Performance

### Re-provisioning muy lento

#### Sintoma

vagrant provision tarda 5+ minutos.

#### Causa: Reinstalando paquetes innecesariamente

Verificar version:
```bash
git describe --tags
```

Si es v0.1.0 o anterior, actualizar a v1.0.0:
```bash
git checkout v1.0.0
vagrant provision
```

v1.0.0 implementa instalacion idempotente (33% mas rapido).

#### Causa: Conexion lenta a Internet

Verificar velocidad:
```bash
vagrant ssh mariadb
curl -o /dev/null http://speedtest.wdc01.softlayer.com/downloads/test10.zip
```

Solucion: Usar mirror local de repositorios.

### VMs consumen mucha RAM

#### Verificar consumo

```bash
VBoxManage list runningvms
VBoxManage showvminfo "iact-mariadb" | grep Memory
```

#### Reducir RAM asignada

Editar Vagrantfile:
```ruby
vb.memory = "1024"  # Reducir de 2048 a 1024
```

Reiniciar:
```bash
vagrant reload
```

Advertencia: MariaDB y PostgreSQL pueden requerir 2GB para performance optima.

### Disco lleno

#### Verificar espacio

```bash
vagrant ssh mariadb
df -h
```

#### Limpiar logs

```bash
sudo journalctl --vacuum-time=7d
sudo apt-get clean
```

#### Limpiar boxes de Vagrant

En host:
```bash
vagrant box prune
```

---

## Comandos de Diagnostico

### Estado general del sistema

```bash
# Estado de VMs
vagrant status
vagrant global-status

# Estado de servicios
vagrant ssh mariadb -c "sudo systemctl status mariadb"
vagrant ssh postgresql -c "sudo systemctl status postgresql"
vagrant ssh adminer -c "sudo systemctl status apache2"
```

### Red y conectividad

```bash
# Ping a VMs
ping 192.168.56.10
ping 192.168.56.11
ping 192.168.56.12

# Verificar puertos (PowerShell)
Test-NetConnection -ComputerName 192.168.56.10 -Port 3306
Test-NetConnection -ComputerName 192.168.56.11 -Port 5432
Test-NetConnection -ComputerName 192.168.56.12 -Port 80

# Ver adaptadores de red
VBoxManage list hostonlyifs
```

### Logs

```bash
# Ver todos los logs
dir logs\*.log

# Buscar errores
Select-String -Path logs\*.log -Pattern "\[ERROR"

# Buscar advertencias
Select-String -Path logs\*.log -Pattern "\[WARN"

# Ver ultimas lineas
Get-Content logs\mariadb_bootstrap.log -Tail 20
```

### Verificacion automatica

```powershell
.\scripts\verify-vms.ps1
```

Ejecuta verificaciones completas:
- Estado de VMs
- Logs generados
- Conectividad de red
- Puertos de servicios
- Acceso HTTP

### Informacion de versiones

```bash
# VirtualBox
VBoxManage --version

# Vagrant
vagrant --version

# Dentro de VMs
vagrant ssh mariadb -c "mysql --version"
vagrant ssh postgresql -c "psql --version"
vagrant ssh adminer -c "php --version"
```

### Logs detallados de Vagrant

```bash
# Verbose output
VAGRANT_LOG=info vagrant up

# Debug output
VAGRANT_LOG=debug vagrant up 2>&1 | tee vagrant-debug.log
```

---

## Reiniciar Todo

Si nada funciona, reiniciar completamente:

```bash
# 1. Detener VMs
vagrant halt

# 2. Destruir VMs
vagrant destroy -f

# 3. Limpiar logs
Remove-Item logs\*.log

# 4. Recrear todo
vagrant up

# 5. Verificar
.\scripts\verify-vms.ps1
```

---

## Obtener Soporte

### Antes de reportar problema

1. Verificar que no es un problema conocido (revisar este documento)
2. Ejecutar script de verificacion:
   ```
   .\scripts\verify-vms.ps1
   ```
3. Recolectar logs:
   ```
   Get-ChildItem logs\*.log | ForEach-Object { Get-Content $_.FullName }
   ```
4. Recolectar informacion del sistema:
   ```
   vagrant --version
   VBoxManage --version
   ```

### Informacion a incluir en reporte

1. Sistema operativo y version
2. Version de VirtualBox
3. Version de Vagrant
4. Output completo de vagrant up
5. Contenido de logs/
6. Output de verify-vms.ps1
7. Pasos para reproducir el problema

---

## Referencias

Documentacion oficial:
- VirtualBox: https://www.virtualbox.org/manual/
- Vagrant: https://www.vagrantup.com/docs
- MariaDB: https://mariadb.com/kb/
- PostgreSQL: https://www.postgresql.org/docs/
- Apache: https://httpd.apache.org/docs/

Foros y comunidad:
- Vagrant: https://discuss.hashicorp.com/c/vagrant/
- VirtualBox: https://forums.virtualbox.org/
- Stack Overflow: https://stackoverflow.com/questions/tagged/vagrant