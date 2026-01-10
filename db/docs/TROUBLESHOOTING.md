# IACT DevBox - Troubleshooting

Soluciones a problemas comunes con IACT DevBox. Todos los problemas listados aquí han sido verificados en el sistema.

## Diagnóstico General

Antes de cualquier troubleshooting específico, ejecuta el diagnóstico completo:

```powershell
.\scripts\diagnose-system.ps1
```

Este script detecta automáticamente los problemas más comunes y sugiere soluciones.

## Problema #1: Ghost Network Adapters

### Síntomas

- Error al hacer `ping 192.168.56.10/11/12`:
  ```
  Request timed out.
  Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
  ```

- Error de conexión a bases de datos:
  ```
  ERROR 2003 (HY000): Can't connect to MySQL server on '192.168.56.10' (10060)
  ```

- `diagnose-system.ps1` reporta:
  ```
  [FAIL] PROBLEMA: Multiples adaptadores Host-Only detectados (5)
  [WARN] Esto causa el problema de Ghost Network Adapters
  ```

### Causa

VirtualBox crea múltiples adaptadores Host-Only numerados (#2, #3, #4, #5) que causan conflictos de enrutamiento de red.

### Solución Verificada

```powershell
# 1. Detener VMs
vagrant halt

# 2. Ejecutar fix-network.ps1
.\scripts\fix-network.ps1

# Esto eliminará los adaptadores numerados y dejará solo uno
# El script pide confirmación antes de eliminar

# 3. Reiniciar VMs
vagrant up

# 4. Verificar
.\scripts\verify-vms.ps1
ping 192.168.56.10
```

**Resultado esperado:**
```
[OK] EXITO: Configuracion ideal alcanzada
[OK] 1 adaptador con IP correcta (192.168.56.1)
```

### Prevención

Ejecutar `check-prerequisites.ps1` ANTES de `vagrant up` para detectar el problema temprano.

## Problema #2: VMs No Arrancan

### Síntomas

- `vagrant up` falla con error de VirtualBox
- VMs quedan en estado "aborted" o "poweroff"
- Error: `VBoxManage: error: Failed to open/create the internal network`

### Causa Común

RAM insuficiente o conflicto de puertos.

### Solución

**Paso 1: Verificar RAM**

```powershell
.\scripts\check-prerequisites.ps1
```

Si reporta:
```
[WARN] RAM Disponible: BAJA (1.18 GB)
```

Cierra aplicaciones para liberar RAM. Las VMs necesitan:
- MariaDB: 2 GB
- PostgreSQL: 2 GB
- Adminer: 1 GB

**Paso 2: Verificar puertos**

```powershell
# Ver qué está usando los puertos
Get-NetTCPConnection -LocalPort 3306,5432,80,443 -ErrorAction SilentlyContinue | 
  ForEach-Object {
    $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
    "Puerto $($_.LocalPort): $($proc.ProcessName)"
  }
```

Si hay conflictos, detén los procesos o cambia la configuración de puertos en el `Vagrantfile`.

**Paso 3: Reset completo**

```powershell
vagrant destroy -f
vagrant up
```

## Problema #3: Perfil de Red en PUBLIC

### Síntomas

- `diagnose-system.ps1` reporta:
  ```
  [WARN] Adaptador VirtualBox en perfil PUBLIC
  [INFO] El firewall de Windows puede bloquear puertos
  ```

- Puertos 3306, 5432, 80, 443 no son accesibles

### Solución

Cambiar el perfil de red a PRIVATE:

```powershell
# Ver adaptadores
Get-NetConnectionProfile | Where-Object { $_.InterfaceAlias -like "*VirtualBox*" }

# Cambiar a PRIVATE
Set-NetConnectionProfile -InterfaceAlias "VirtualBox Host-Only Network" -NetworkCategory Private
```

## Problema #4: Provisioning Incompleto

### Síntomas

- `vagrant up` termina pero las bases de datos no están disponibles
- `verify-vms.ps1` reporta:
  ```
  [WARN] mariadb provision incompleto o con errores
  ```

### Diagnóstico

```powershell
# Ver logs de provisioning
Get-Content logs\mariadb_bootstrap.log | Select-String "ERROR"
Get-Content logs\postgres_bootstrap.log | Select-String "ERROR"
Get-Content logs\adminer_bootstrap.log | Select-String "ERROR"
```

### Solución

```powershell
# Re-ejecutar provisioning
vagrant reload --provision
```

Si persiste el error, revisar los logs detallados en `logs/` para identificar el problema específico.

## Problema #5: Adminer Web Interface No Accesible

### Síntomas

- `http://192.168.56.12` no carga
- Browser muestra "This site can't be reached"

### Diagnóstico

```powershell
# Verificar que VM está corriendo
vagrant status adminer

# Verificar puerto 80
Test-NetConnection -ComputerName 192.168.56.12 -Port 80

# Ver logs de Apache
vagrant ssh adminer -c "sudo tail -50 /var/log/apache2/error.log"
```

### Soluciones

**Solución 1: Reiniciar Apache**

```powershell
vagrant ssh adminer -c "sudo systemctl restart apache2"
```

**Solución 2: Verificar firewall**

```powershell
vagrant ssh adminer -c "sudo ufw status"
# Debería mostrar: Status: inactive
```

**Solución 3: Reload VM**

```powershell
vagrant reload adminer
```

## Problema #6: Error de SSH

### Síntomas

- `vagrant ssh mariadb` falla
- Error: `Connection timeout`

### Solución

```powershell
# Ver estado detallado
vagrant status

# Si VM está running pero SSH no funciona
vagrant reload mariadb
```

## Generar Reporte para Soporte

Si ninguna solución funciona, genera un bundle de diagnóstico completo:

```powershell
.\scripts\generate-support-bundle.ps1 -IncludeLogs -IncludeVagrantfile
```

Esto creará un archivo `support-bundle_TIMESTAMP.zip` con toda la información del sistema.

## Comandos de Diagnóstico Útiles

```powershell
# Ver todos los adaptadores VirtualBox
VBoxManage list hostonlyifs

# Ver VMs de VirtualBox
VBoxManage list vms
VBoxManage list runningvms

# Logs detallados de Vagrant
$env:VAGRANT_LOG="debug"
vagrant up

# Ver procesos de VirtualBox
Get-Process | Where-Object { $_.Name -like "*VBox*" }

# Reiniciar servicios de VirtualBox (como admin)
net stop vboxdrv
net start vboxdrv
```

## Problemas Conocidos No Resueltos

Ninguno hasta la fecha.

Si encuentras un problema no listado aquí, genera un support bundle y repórtalo al equipo.

---

**Última actualización**: 2026-01-10
