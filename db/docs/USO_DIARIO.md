# Guía de Uso Diario

Documentación de operaciones cotidianas para la gestión del entorno IACT DevBox.

---

## Índice

1. [Gestión de Máquinas Virtuales](#gestion-de-maquinas-virtuales)
2. [Acceso SSH](#acceso-ssh)
3. [Provisioning](#provisioning)
4. [Gestión de Logs](#gestion-de-logs)
5. [Snapshots](#snapshots)
6. [Gestión de Recursos](#gestion-de-recursos)
7. [Operaciones con Bases de Datos](#operaciones-con-bases-de-datos)
8. [Transferencia de Archivos](#transferencia-de-archivos)
9. [Red y Conectividad](#red-y-conectividad)
10. [Actualiz

aciones](#actualizaciones)
11. [Workflows Diarios](#workflows-diarios)

---

## Gestión de Máquinas Virtuales

### Iniciar VMs

Iniciar todas las VMs:
```bash
vagrant up
```

Tiempo estimado primera vez: ~6 minutos
Tiempo estimado siguiente vez: ~1 minuto

Iniciar VM específica:
```bash
vagrant up mariadb
vagrant up postgresql
vagrant up adminer
```

Iniciar múltiples VMs específicas:
```bash
vagrant up mariadb postgresql
```

Iniciar con provisioning explícito:
```bash
vagrant up --provision
```

### Detener VMs

Detener todas las VMs:
```bash
vagrant halt
```

Detener VM específica:
```bash
vagrant halt mariadb
vagrant halt postgresql
vagrant halt adminer
```

Forzar detención (si no responde):
```bash
vagrant halt -f mariadb
```

### Reiniciar VMs

Reiniciar todas las VMs:
```bash
vagrant reload
```

Reiniciar VM específica:
```bash
vagrant reload mariadb
vagrant reload postgresql
```

Reiniciar con provisioning:
```bash
vagrant reload --provision
vagrant reload --provision mariadb
```

### Suspender y Resumir

Suspender VMs (guardar estado en RAM):
```bash
vagrant suspend
vagrant suspend mariadb
```

Resumir VMs suspendidas:
```bash
vagrant resume
vagrant resume mariadb
```

Ventajas de suspend vs halt:
- Más rápido (segundos vs minuto)
- Mantiene estado exacto
- Consume espacio en disco

### Destruir VMs

Destruir todas las VMs:
```bash
vagrant destroy
```

Destruir sin confirmación:
```bash
vagrant destroy -f
```

Destruir VM específica:
```bash
vagrant destroy -f mariadb
vagrant destroy -f postgresql
```

ADVERTENCIA: Esto elimina completamente la VM y todos sus datos.

### Verificar Estado

Estado de todas las VMs:
```bash
vagrant status
```

Salida ejemplo:
```
Current machine states:

mariadb                   running (virtualbox)
postgresql                running (virtualbox)
adminer                   running (virtualbox)
```

Estados posibles:
- `running` - VM encendida
- `poweroff` - VM apagada
- `saved` - VM suspendida
- `not created` - VM no existe

Estado global (todas las VMs Vagrant):
```bash
vagrant global-status
```

Limpiar cache de estado global:
```bash
vagrant global-status --prune
```

---

## Acceso SSH

### Conectar a VMs

Conectar a MariaDB:
```bash
vagrant ssh mariadb
```

Conectar a PostgreSQL:
```bash
vagrant ssh postgresql
```

Conectar a Adminer:
```bash
vagrant ssh adminer
```

### Salir de SSH

```bash
exit
```

O presionar: `Ctrl + D`

### Ejecutar Comandos Remotos

Comando único:
```bash
vagrant ssh mariadb -c "hostname"
vagrant ssh postgresql -c "df -h"
```

Comandos múltiples:
```bash
vagrant ssh mariadb -c "uptime && free -h && df -h"
```

Comandos con sudo:
```bash
vagrant ssh mariadb -c "sudo systemctl status mariadb"
```

### Información de Conexión SSH

Ver configuración SSH de una VM:
```bash
vagrant ssh-config mariadb
```

Salida ejemplo:
```
Host mariadb
  HostName 127.0.0.1
  User vagrant
  Port 2222
  IdentityFile C:/Users/.../.vagrant/machines/mariadb/...
```

Usar con clientes SSH estándar:
```bash
ssh -F <(vagrant ssh-config mariadb) mariadb
```

---

## Provisioning

### Cuándo Provisionar

Provisionar es necesario cuando:
- Cambios en scripts de `provisioners/`
- Cambios en archivos de `utils/`
- Cambios en archivos de `config/`
- Actualización de versiones de software
- Configuración de base de datos modificada

### Provisionar Todas las VMs

```bash
vagrant provision
```

Tiempo estimado: ~2 minutos (con instalación idempotente)

### Provisionar VM Específica

```bash
vagrant provision mariadb
vagrant provision postgresql
vagrant provision adminer
```

### Provisionar con Provisioner Específico

```bash
vagrant provision --provision-with shell
```

### Provisioning en Primera Ejecución

El provisioning automático ocurre en:
```bash
vagrant up  # Primera vez
```

Saltar provisioning:
```bash
vagrant up --no-provision
```

### Ver Salida de Provisioning

El provisioning muestra salida en consola en tiempo real.

Para ver solo errores:
```bash
vagrant provision 2>&1 | grep -i error
```

Para guardar salida completa:
```bash
vagrant provision > provisioning_output.txt 2>&1
```

### Provisioning con Debugging

```bash
vagrant provision --debug
```

---

## Gestión de Logs

### Ubicación de Logs

Todos los logs en: `./logs/`

Los logs son compartidos entre host y VMs vía carpeta sincronizada `/vagrant`.

### Archivos de Log

Después de `vagrant up`:
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
├── adminer_swap.log
└── system_prepare.log
```

### Ver Logs

Ver log completo:
```bash
cat logs/mariadb_install.log
```

Ver últimas líneas:
```bash
tail -n 50 logs/mariadb_bootstrap.log
```

Seguir log en tiempo real (durante provisioning):
```bash
tail -f logs/mariadb_bootstrap.log
```

### Buscar en Logs

Buscar errores:
```bash
grep -i error logs/*.log
grep -i "\[ERROR" logs/*.log
```

Buscar warnings:
```bash
grep -i warn logs/*.log
grep -i "\[WARN" logs/*.log
```

Buscar palabra específica:
```bash
grep -i "mariadb" logs/mariadb_install.log
```

Windows PowerShell:
```powershell
Select-String -Path logs\*.log -Pattern "\[ERROR"
Select-String -Path logs\mariadb_install.log -Pattern "mysql"
```

### Limpiar Logs

Limpiar todos los logs:
```bash
rm logs/*.log
```

Los logs se regenerarán en el próximo provisioning.

Usar script de limpieza:
```powershell
.\scripts\clean-logs.ps1
```

Ver: SCRIPTS.md para más información.

### Ver Logs desde VMs

```bash
vagrant ssh mariadb
cat /vagrant/logs/mariadb_install.log
tail -f /vagrant/logs/mariadb_bootstrap.log
exit
```

---

## Snapshots

### Crear Snapshot

Snapshot de VM específica:
```bash
vagrant snapshot save mariadb mi_snapshot
vagrant snapshot save postgresql backup_20260102
```

Nombre descriptivo:
```bash
vagrant snapshot save mariadb $(date +%Y%m%d)_antes_cambios
```

### Listar Snapshots

```bash
vagrant snapshot list mariadb
vagrant snapshot list postgresql
vagrant snapshot list adminer
```

### Restaurar Snapshot

Restaurar a snapshot específico:
```bash
vagrant snapshot restore mariadb mi_snapshot
```

NOTA: La VM se restaura al estado exacto del snapshot. Todos los cambios posteriores se pierden.

Restaurar y arrancar:
```bash
vagrant snapshot restore mariadb mi_snapshot
vagrant up mariadb
```

### Eliminar Snapshot

```bash
vagrant snapshot delete mariadb mi_snapshot
```

### Snapshot Rápido (Push/Pop)

Crear snapshot temporal:
```bash
vagrant snapshot push mariadb
```

Restaurar último snapshot temporal:
```bash
vagrant snapshot pop mariadb
```

Restaurar sin eliminar:
```bash
vagrant snapshot pop --no-delete mariadb
```

Workflow típico:
```bash
# Antes de cambio experimental
vagrant snapshot push mariadb

# Hacer cambios...

# Si falla:
vagrant snapshot pop mariadb

# Si funciona:
vagrant snapshot delete mariadb <nombre_del_push>
```

### Snapshots para Múltiples VMs

```bash
# Crear snapshots de todas las VMs
for vm in mariadb postgresql adminer; do
  vagrant snapshot save $vm backup_$(date +%Y%m%d)
done

# Listar snapshots de todas
for vm in mariadb postgresql adminer; do
  echo "=== $vm ==="
  vagrant snapshot list $vm
done
```

Ver: RESPALDO_RECUPERACION.md para estrategias de backup.

---

## Gestión de Recursos

### Verificar Recursos Asignados

Ver RAM y CPU asignados:
```bash
# Desde configuración
cat Vagrantfile | grep MEMORY
cat Vagrantfile | grep CPUS
```

Desde VirtualBox:
```bash
VBoxManage showvminfo mariadb_default | grep Memory
VBoxManage showvminfo mariadb_default | grep "CPU count"
```

### Verificar Uso de Recursos

Dentro de la VM:
```bash
vagrant ssh mariadb -c "free -h"
vagrant ssh mariadb -c "nproc"
vagrant ssh mariadb -c "df -h"
```

Con htop:
```bash
vagrant ssh mariadb -c "htop"
```

Presionar `q` para salir de htop.

### Monitorear Uso en Tiempo Real

```bash
vagrant ssh mariadb
htop
```

O con top:
```bash
vagrant ssh mariadb -c "top -n 1"
```

### Modificar Recursos

Editar Vagrantfile:
```ruby
MARIADB_MEMORY = "4096"  # Aumentar a 4GB
MARIADB_CPUS = "2"       # Aumentar a 2 CPUs
```

Aplicar cambios:
```bash
vagrant reload mariadb
```

Ver: CONFIGURACION.md para detalles completos.

---

## Operaciones con Bases de Datos

### Iniciar/Detener Servicios

MariaDB:
```bash
vagrant ssh mariadb -c "sudo systemctl stop mariadb"
vagrant ssh mariadb -c "sudo systemctl start mariadb"
vagrant ssh mariadb -c "sudo systemctl restart mariadb"
vagrant ssh mariadb -c "sudo systemctl status mariadb"
```

PostgreSQL:
```bash
vagrant ssh postgresql -c "sudo systemctl stop postgresql"
vagrant ssh postgresql -c "sudo systemctl start postgresql"
vagrant ssh postgresql -c "sudo systemctl restart postgresql"
vagrant ssh postgresql -c "sudo systemctl status postgresql"
```

### Acceder a Consolas de Base de Datos

MariaDB:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123'
```

O directamente:
```bash
vagrant ssh mariadb -c "mysql -u root -p'rootpass123'"
```

PostgreSQL:
```bash
vagrant ssh postgresql
sudo -i -u postgres
psql
```

O directamente:
```bash
vagrant ssh postgresql -c "sudo -u postgres psql"
```

### Verificar Versiones

```bash
vagrant ssh mariadb -c "mysql --version"
vagrant ssh postgresql -c "psql --version"
```

### Importar Datos

MariaDB:
```bash
# Colocar archivo SQL en directorio del proyecto
cp mi_dump.sql .

# Importar desde dentro de la VM
vagrant ssh mariadb
mysql -u root -p'rootpass123' ivr_legacy < /vagrant/mi_dump.sql
exit
```

PostgreSQL:
```bash
# Colocar archivo SQL en directorio del proyecto
cp mi_dump.sql .

# Importar desde dentro de la VM
vagrant ssh postgresql
sudo -u postgres psql iact_analytics < /vagrant/mi_dump.sql
exit
```

### Exportar Datos

MariaDB:
```bash
vagrant ssh mariadb
mysqldump -u root -p'rootpass123' ivr_legacy > /vagrant/export_$(date +%Y%m%d).sql
exit
```

PostgreSQL:
```bash
vagrant ssh postgresql
sudo -u postgres pg_dump iact_analytics > /vagrant/export_$(date +%Y%m%d).sql
exit
```

Ver: RESPALDO_RECUPERACION.md para procedimientos completos de backup.

---

## Transferencia de Archivos

### Carpeta Sincronizada

El directorio del proyecto está sincronizado en `/vagrant` dentro de cada VM.

```
./                  (host)
└── /vagrant/      (dentro de VMs)
```

### Copiar Archivo a VM

Desde host:
```bash
# Copiar archivo al directorio del proyecto
cp mi_archivo.txt .
```

Desde VM:
```bash
vagrant ssh mariadb
ls -la /vagrant/mi_archivo.txt
exit
```

### Copiar Archivo desde VM

Desde VM:
```bash
vagrant ssh mariadb
cp /etc/mysql/my.cnf /vagrant/my.cnf.backup
exit
```

Desde host:
```bash
ls -la my.cnf.backup
```

### Copiar Datos de Base de Datos

Exportar desde VM a carpeta compartida:
```bash
vagrant ssh mariadb
mysqldump -u root -p'rootpass123' ivr_legacy > /vagrant/backup.sql
exit
```

El archivo `backup.sql` estará disponible en el directorio del host.

### Editar Archivos

Editar desde host (con editor del host):
```bash
# Archivo será visible en VM automáticamente
notepad config/vhost.conf
```

Editar desde VM:
```bash
vagrant ssh adminer
sudo nano /vagrant/config/vhost.conf
exit
```

---

## Red y Conectividad

### Verificar Conectividad

Ping a VMs:
```bash
ping 192.168.56.10  # MariaDB
ping 192.168.56.11  # PostgreSQL
ping 192.168.56.12  # Adminer
```

Windows PowerShell:
```powershell
Test-Connection 192.168.56.10
Test-Connection 192.168.56.11
Test-Connection 192.168.56.12
```

### Verificar Puertos

Telnet (si está instalado):
```bash
telnet 192.168.56.10 3306  # MariaDB
telnet 192.168.56.11 5432  # PostgreSQL
telnet 192.168.56.12 80    # Adminer HTTP
telnet 192.168.56.12 443   # Adminer HTTPS
```

Windows PowerShell:
```powershell
Test-NetConnection -ComputerName 192.168.56.10 -Port 3306
Test-NetConnection -ComputerName 192.168.56.11 -Port 5432
Test-NetConnection -ComputerName 192.168.56.12 -Port 80
```

### Verificar Servicios

Desde las VMs:
```bash
vagrant ssh mariadb -c "sudo netstat -tlnp | grep 3306"
vagrant ssh postgresql -c "sudo netstat -tlnp | grep 5432"
vagrant ssh adminer -c "sudo netstat -tlnp | grep 80"
```

### Acceder a Adminer

Navegador web:
```
HTTP:  http://192.168.56.12
HTTPS: https://192.168.56.12
```

HTTPS mostrará advertencia por certificado autofirmado (normal en desarrollo).

### Ver Configuración de Red

Desde VM:
```bash
vagrant ssh mariadb -c "ip addr show"
vagrant ssh mariadb -c "ip route show"
```

Desde VirtualBox:
```bash
VBoxManage list hostonlyifs
```

---

## Actualizaciones

### Actualizar Vagrant Box

Verificar actualizaciones:
```bash
vagrant box outdated
```

Actualizar box:
```bash
vagrant box update
```

Aplicar box actualizado:
```bash
vagrant destroy -f
vagrant box update
vagrant up
```

### Actualizar Paquetes en VMs

Actualización completa del sistema:
```bash
vagrant ssh mariadb
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
exit
```

Para todas las VMs:
```bash
for vm in mariadb postgresql adminer; do
  echo "Actualizando $vm..."
  vagrant ssh $vm -c "sudo apt update && sudo apt upgrade -y"
done
```

ADVERTENCIA: Actualizar paquetes puede cambiar versiones de software. Crear snapshot antes.

### Actualizar Versión de MariaDB

1. Editar Vagrantfile:
```ruby
MARIADB_VERSION = "11.5"  # Nueva versión
```

2. Destruir y recrear:
```bash
vagrant destroy -f mariadb
vagrant up mariadb
```

3. Restaurar datos si es necesario.

Ver: CONFIGURACION.md para cambio de versiones.

### Actualizar Versión de PostgreSQL

Similar a MariaDB:
```ruby
POSTGRES_VERSION = "17"  # Nueva versión
```

```bash
vagrant destroy -f postgresql
vagrant up postgresql
```

### Actualizar Adminer

1. Verificar última versión: https://github.com/vrana/adminer/releases

2. Editar Vagrantfile:
```ruby
ADMINER_VERSION = "4.8.2"  # Nueva versión
```

3. Re-provisionar:
```bash
vagrant provision adminer
```

No es necesario destruir la VM para Adminer.

---

## Workflows Diarios

### Workflow Matutino

```bash
# 1. Verificar estado
vagrant status

# 2. Iniciar VMs si están apagadas
vagrant up

# 3. Verificar que todo funciona
.\scripts\verify-vms.ps1

# 4. Trabajar normalmente...
```

### Workflow de Cierre

```bash
# 1. Finalizar trabajo...

# 2. (Opcional) Detener VMs
vagrant halt

# O suspender para inicio más rápido mañana
vagrant suspend
```

### Workflow de Desarrollo

```bash
# 1. Iniciar ambiente
vagrant up

# 2. Conectar desde aplicación
# (usar parámetros de ACCESO_BASES_DATOS.md)

# 3. Durante desarrollo...

# 4. Si necesitas cambiar algo en configuración:
vagrant provision

# 5. Si algo sale mal:
vagrant snapshot restore mariadb mi_snapshot_estable
```

### Workflow de Testing

```bash
# 1. Crear snapshot antes de test
vagrant snapshot save mariadb antes_test

# 2. Ejecutar tests...

# 3. Si tests modificaron datos:
vagrant snapshot restore mariadb antes_test

# 4. Limpiar snapshot temporal
vagrant snapshot delete mariadb antes_test
```

### Workflow Semanal

```bash
# Lunes - Inicio de semana
vagrant up
.\scripts\verify-vms.ps1

# Durante la semana - Trabajo normal

# Viernes - Fin de semana
.\scripts\clean-logs.ps1 -DaysToKeep 7
vagrant halt
```

### Workflow Mensual

```bash
# Primer día del mes

# 1. Verificar sistema
.\scripts\verify-vms.ps1

# 2. Limpiar logs antiguos
.\scripts\clean-logs.ps1 -DaysToKeep 30 -Compress

# 3. Crear snapshots de respaldo
vagrant snapshot save mariadb backup_$(date +%Y%m)
vagrant snapshot save postgresql backup_$(date +%Y%m)
vagrant snapshot save adminer backup_$(date +%Y%m)

# 4. Verificar espacio en disco
vagrant ssh mariadb -c "df -h"
vagrant ssh postgresql -c "df -h"
```

### Workflow Antes de Cambios Importantes

```bash
# 1. Verificar estado actual
vagrant status
.\scripts\verify-vms.ps1

# 2. Crear snapshots
vagrant snapshot save mariadb antes_cambio_importante
vagrant snapshot save postgresql antes_cambio_importante

# 3. Hacer cambios...
# (editar Vagrantfile, scripts, configs, etc.)

# 4. Aplicar cambios
vagrant reload --provision
# O
vagrant destroy -f && vagrant up

# 5. Verificar que funciona
.\scripts\verify-vms.ps1
# Probar conexiones
# Probar aplicación

# 6a. Si todo funciona:
vagrant snapshot delete mariadb antes_cambio_importante
vagrant snapshot delete postgresql antes_cambio_importante

# 6b. Si algo falla:
vagrant snapshot restore mariadb antes_cambio_importante
vagrant snapshot restore postgresql antes_cambio_importante
vagrant up
```

---

## Atajos Útiles

### Comandos Frecuentes

```bash
# Estado rápido
vagrant status

# Levantar todo
vagrant up

# Detener todo
vagrant halt

# Reiniciar con cambios
vagrant reload

# Ver logs de error
grep -i error logs/*.log

# SSH a MariaDB
vagrant ssh mariadb

# SSH a PostgreSQL
vagrant ssh postgresql

# Verificación completa
.\scripts\verify-vms.ps1
```

### Aliases Sugeridos (Bash/Zsh)

Agregar a `.bashrc` o `.zshrc`:
```bash
# IACT DevBox shortcuts
alias vup='vagrant up'
alias vhalt='vagrant halt'
alias vreload='vagrant reload'
alias vstatus='vagrant status'
alias vsshm='vagrant ssh mariadb'
alias vsshp='vagrant ssh postgresql'
alias vssha='vagrant ssh adminer'
alias vlogs='grep -i error logs/*.log'
```

### Aliases Sugeridos (PowerShell)

Agregar a perfil de PowerShell:
```powershell
# IACT DevBox shortcuts
function vup { vagrant up }
function vhalt { vagrant halt }
function vreload { vagrant reload }
function vstatus { vagrant status }
function vsshm { vagrant ssh mariadb }
function vsshp { vagrant ssh postgresql }
function vssha { vagrant ssh adminer }
function vlogs { Select-String -Path logs\*.log -Pattern "\[ERROR" }
```

---

## Solución de Problemas Comunes

### VM no arranca

```bash
# Ver detalles del error
vagrant up mariadb --debug

# Verificar VirtualBox
VBoxManage --version
VBoxManage list vms

# Reintentar
vagrant destroy -f mariadb
vagrant up mariadb
```

### SSH no funciona

```bash
# Regenerar configuración SSH
vagrant ssh-config mariadb

# Destruir y recrear
vagrant destroy -f mariadb
vagrant up mariadb
```

### Provisioning falla

```bash
# Ver logs detallados
cat logs/mariadb_bootstrap.log

# Reintentar provisioning
vagrant provision mariadb

# Si persiste, destruir y recrear
vagrant destroy -f mariadb
vagrant up mariadb
```

### Servicios no responden

```bash
# Verificar estado del servicio
vagrant ssh mariadb -c "sudo systemctl status mariadb"

# Reiniciar servicio
vagrant ssh mariadb -c "sudo systemctl restart mariadb"

# Ver logs del sistema
vagrant ssh mariadb -c "sudo journalctl -u mariadb -n 50"
```

Ver: TROUBLESHOOTING.md para problemas detallados.

---

## Mejores Prácticas

1. **Siempre verificar después de vagrant up:**
   ```bash
   vagrant up
   .\scripts\verify-vms.ps1
   ```

2. **Crear snapshots antes de cambios:**
   ```bash
   vagrant snapshot save mariadb antes_cambio
   ```

3. **Revisar logs periódicamente:**
   ```bash
   grep -i error logs/*.log
   ```

4. **Detener VMs cuando no se usan:**
   ```bash
   vagrant halt  # O suspend para inicio más rápido
   ```

5. **Limpiar logs semanalmente:**
   ```bash
   .\scripts\clean-logs.ps1 -DaysToKeep 7
   ```

6. **No modificar archivos en /etc/ sin backup:**
   ```bash
   vagrant snapshot save mariadb antes_modificar_config
   ```

7. **Documentar cambios importantes:**
   - Actualizar CHANGELOG.md
   - Mantener notas de cambios en configuración

---

## Referencias

- SCRIPTS.md - Scripts de verificación y limpieza
- ACCESO_BASES_DATOS.md - Conexión a bases de datos
- CONFIGURACION.md - Personalización de recursos
- RESPALDO_RECUPERACION.md - Snapshots y backups
- TROUBLESHOOTING.md - Solución de problemas
- README.md - Visión general del proyecto

---

Última actualización: 02 de enero de 2026
Versión del documento: 1.0.0