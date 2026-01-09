# Scripts Utilitarios - IACT DevBox

## Descripción General

Este documento describe los tres scripts utilitarios disponibles en el proyecto para facilitar la gestión y mantenimiento del entorno de desarrollo.

**Ubicación:** `scripts/`

**Scripts disponibles:**
- `verify-vms.ps1` - Verificación de estado del sistema
- `clean-logs.ps1` - Limpieza y compresión de logs
- `backup-configs.sh` - Respaldo de configuraciones

---

## verify-vms.ps1

### Propósito

Script de PowerShell para verificar el estado completo del entorno de desarrollo, incluyendo prerequisitos, estado de VMs, conectividad de red y logs.

### Ubicación de Ejecución

**Host Windows** (PowerShell)

### Sintaxis

```powershell
.\scripts\verify-vms.ps1
```

### Funcionalidades

1. **Verificación de prerequisitos**
   - Vagrant instalado y versión
   - VirtualBox instalado y versión
   
2. **Estado de máquinas virtuales**
   - Estado actual de cada VM (running, stopped, not created)
   - Información de recursos asignados
   
3. **Conectividad de red**
   - Ping a cada VM
   - Verificación de puertos de servicios
   
4. **Análisis de logs**
   - Revisión de errores en logs de provisioning
   - Reporte de warnings y problemas

### Salida Esperada

```
========================================
 IACT DevBox - System Verification
 Version: 1.0.0
========================================

PREREQUISITOS
  [OK] Vagrant 2.4.0 instalado
  [OK] VirtualBox 7.0.12 instalado

ESTADO DE VMs
  [OK] VM mariadb: running (192.168.56.10)
  [OK] VM postgresql: running (192.168.56.11)
  [OK] VM adminer: running (192.168.56.12)

CONECTIVIDAD
  [OK] Conectividad: 192.168.56.10
  [OK] Conectividad: 192.168.56.11
  [OK] Conectividad: 192.168.56.12

LOGS
  [OK] No se encontraron errores criticos

========================================
 RESUMEN
========================================
  Estado general: SALUDABLE
  VMs en ejecucion: 3/3
  Servicios accesibles: 3/3
```

### Cuándo Usar

- Después de ejecutar `vagrant up`
- Antes de comenzar a trabajar (verificación diaria)
- Al diagnosticar problemas
- Después de cambios en la configuración
- Antes de hacer commits importantes

### Casos de Uso Comunes

**Verificación post-instalación:**
```powershell
vagrant up
.\scripts\verify-vms.ps1
```

**Diagnóstico de problemas:**
```powershell
# Si algo no funciona bien:
.\scripts\verify-vms.ps1
# Revisar la salida para identificar problemas
```

**Verificación matutina:**
```powershell
# Al inicio del día de trabajo:
vagrant up
.\scripts\verify-vms.ps1
```

---

## clean-logs.ps1

### Propósito

Script de PowerShell para gestionar logs de provisioning, incluyendo limpieza de logs antiguos y compresión de archivos archivados.

### Ubicación de Ejecución

**Host Windows** (PowerShell)

### Sintaxis

```powershell
.\scripts\clean-logs.ps1 [-DaysToKeep <dias>] [-Compress] [-WhatIf] [-Confirm] [-Help]
```

### Parámetros

- **-DaysToKeep** `<int>`: Número de días a mantener (default: 30)
- **-Compress**: Comprimir logs en archive/
- **-WhatIf**: Simular sin hacer cambios
- **-Confirm**: Pedir confirmación antes de ejecutar
- **-Help**: Mostrar ayuda completa

### Funcionalidades

1. **Limpieza de logs antiguos**
   - Mueve logs de más de X días a `logs/archive/`
   - Preserva logs recientes en `logs/`
   
2. **Compresión de logs**
   - Comprime logs archivados en archivo ZIP
   - Elimina archivos originales después de comprimir
   - Genera nombre único con timestamp
   
3. **Modo simulación**
   - Muestra qué acciones se realizarían
   - No hace cambios reales
   
4. **Confirmación interactiva**
   - Pide confirmación antes de ejecutar
   - Una sola confirmación por operación completa

### Ejemplos de Uso

**Limpieza estándar (30 días):**
```powershell
.\scripts\clean-logs.ps1
```

**Limpieza más agresiva (7 días):**
```powershell
.\scripts\clean-logs.ps1 -DaysToKeep 7
```

**Ver qué se haría sin ejecutar:**
```powershell
.\scripts\clean-logs.ps1 -DaysToKeep 15 -WhatIf
```

**Comprimir logs archivados:**
```powershell
.\scripts\clean-logs.ps1 -Compress
```

**Ver qué se comprimiría:**
```powershell
.\scripts\clean-logs.ps1 -Compress -WhatIf
```

**Limpieza y compresión en un comando:**
```powershell
.\scripts\clean-logs.ps1 -DaysToKeep 15 -Compress
```

**Con confirmación interactiva:**
```powershell
.\scripts\clean-logs.ps1 -Compress -Confirm
```

### Estructura de Logs

```
logs/
├── adminer_bootstrap.log       (logs recientes)
├── mariadb_install.log
├── postgres_setup.log
└── archive/                    (logs antiguos)
    ├── old_log1.log
    ├── old_log2.log
    └── logs_20260102_120000.zip (comprimidos)
```

### Cuándo Usar

**Limpieza semanal:**
```powershell
# Cada viernes o lunes:
.\scripts\clean-logs.ps1 -DaysToKeep 7
```

**Limpieza mensual:**
```powershell
# Primer día del mes:
.\scripts\clean-logs.ps1 -DaysToKeep 30 -Compress
```

**Antes de commit:**
```powershell
# Para no commitear logs antiguos:
.\scripts\clean-logs.ps1 -DaysToKeep 1 -Compress
```

**Ahorro de espacio:**
```powershell
# Cuando archive/ crece mucho:
.\scripts\clean-logs.ps1 -Compress
```

### Casos de Uso Comunes

**Mantenimiento semanal:**
```powershell
# 1. Limpiar logs antiguos
.\scripts\clean-logs.ps1 -DaysToKeep 7 -WhatIf

# 2. Verificar qué se haría
# (revisar salida)

# 3. Ejecutar limpieza
.\scripts\clean-logs.ps1 -DaysToKeep 7
```

**Preparación para backup:**
```powershell
# 1. Comprimir todos los logs archivados
.\scripts\clean-logs.ps1 -Compress

# 2. Copiar ZIPs a ubicación de backup
Copy-Item logs\archive\*.zip E:\backups\
```

**Limpieza completa:**
```powershell
# 1. Mover logs antiguos (>15 días)
.\scripts\clean-logs.ps1 -DaysToKeep 15

# 2. Comprimir lo archivado
.\scripts\clean-logs.ps1 -Compress

# 3. Resultado: logs/ limpio, archive/ comprimido
```

---

## backup-configs.sh

### Propósito

Script de Bash para crear respaldos manuales de archivos de configuración críticos dentro de las máquinas virtuales.

### Ubicación de Ejecución

**Dentro de las VMs** (vía vagrant ssh)

**NOTA:** Los provisioners ya crean backups automáticos durante la instalación. Este script es para backups manuales adicionales.

### Sintaxis

```bash
sudo bash /vagrant/scripts/backup-configs.sh <comando> [opciones]
```

### Comandos Disponibles

- **backup**: Crear nuevo backup
- **list**: Listar backups existentes
- **cleanup** `<dias>`: Eliminar backups antiguos
- **restore** `<timestamp>`: Restaurar backup específico
- **help**: Mostrar ayuda

### Funcionalidades

1. **Crear backups**
   - Organiza por VM y timestamp
   - Incluye README.txt con información
   - Genera SUMMARY.txt con listado

2. **Listar backups**
   - Muestra todos los backups disponibles
   - Ordenados por fecha
   - Con tamaño y ubicación

3. **Limpiar backups antiguos**
   - Elimina backups de más de X días
   - Preserva backups recientes

4. **Restaurar configuraciones**
   - Restaura desde backup específico
   - Reinicia servicios automáticamente

### Archivos Respaldados

**MariaDB:**
- `/etc/mysql/mariadb.conf.d/50-server.cnf`

**PostgreSQL:**
- `/etc/postgresql/16/main/postgresql.conf`
- `/etc/postgresql/16/main/pg_hba.conf`

**Adminer:**
- `/etc/apache2/sites-available/adminer.conf`
- `/etc/apache2/sites-available/adminer-ssl.conf`

### Ejemplos de Uso

**Crear backup en MariaDB:**
```bash
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
```

**Crear backup en PostgreSQL:**
```bash
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
```

**Crear backup en Adminer:**
```bash
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
```

**Listar backups disponibles:**
```bash
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh list"
```

**Eliminar backups antiguos (>90 días):**
```bash
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
```

**Restaurar backup específico:**
```bash
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh restore 20260102_120000"
```

### Estructura de Backups

```
/vagrant/backups/
└── 20260102_120000/              (timestamp del backup)
    ├── README.txt                (información del backup)
    ├── SUMMARY.txt               (resumen de archivos)
    ├── mariadb/
    │   └── 50-server.cnf
    ├── postgresql/
    │   ├── postgresql.conf
    │   └── pg_hba.conf
    └── adminer/
        ├── adminer.conf
        └── adminer-ssl.conf
```

### Cuándo Usar

**Antes de cambios importantes:**
```bash
# 1. Crear backup
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"

# 2. Hacer cambios en configuración
vagrant ssh mariadb
sudo nano /etc/mysql/mariadb.conf.d/50-server.cnf

# 3. Si algo sale mal, restaurar:
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh restore TIMESTAMP"
```

**Mantenimiento programado:**
```bash
# Cada mes:
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
```

**Limpieza de backups antiguos:**
```bash
# Cada 3 meses, eliminar backups >90 días:
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
```

### Backups Automáticos vs Manuales

**Backups Automáticos (Provisioners):**
- Se crean durante `vagrant up` / `vagrant provision`
- Formato: `filename.backup.YYYYMMDD_HHMMSS`
- Ubicación: Mismo directorio que el archivo original
- Ejemplo: `/etc/mysql/mariadb.conf.d/50-server.cnf.backup.20260102_120530`

**Backups Manuales (backup-configs.sh):**
- Se crean cuando el usuario lo solicita
- Formato: `/vagrant/backups/TIMESTAMP/vm/filename`
- Organizados por timestamp y VM
- Incluyen README y SUMMARY

**Recomendación:**
- Los backups automáticos son suficientes para la mayoría de casos
- Use backups manuales para puntos de control importantes antes de cambios mayores

---

## Workflows Recomendados

### Workflow Diario

```powershell
# 1. Levantar VMs (si no están activas)
vagrant up

# 2. Verificar estado
.\scripts\verify-vms.ps1

# 3. Trabajar normalmente...

# 4. Al final del día (opcional):
vagrant halt
```

### Workflow Semanal

```powershell
# Lunes - Inicio de semana:
vagrant up
.\scripts\verify-vms.ps1

# Viernes - Fin de semana:
.\scripts\clean-logs.ps1 -DaysToKeep 7
vagrant halt
```

### Workflow Mensual

```powershell
# Primer día del mes:

# 1. Verificar sistema
.\scripts\verify-vms.ps1

# 2. Limpiar logs antiguos
.\scripts\clean-logs.ps1 -DaysToKeep 30 -Compress

# 3. Backup manual de configuraciones (opcional)
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh backup"

# 4. Limpiar backups muy antiguos (>90 días)
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
```

### Workflow Antes de Cambios Importantes

```bash
# 1. Verificar estado actual
.\scripts\verify-vms.ps1

# 2. Crear backup manual
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"

# 3. Hacer cambios...

# 4. Verificar que todo funciona
.\scripts\verify-vms.ps1

# 5. Si algo falla, restaurar backup
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh restore TIMESTAMP"
```

### Workflow de Troubleshooting

```powershell
# 1. Verificar estado general
.\scripts\verify-vms.ps1

# 2. Revisar logs recientes
dir logs\*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 5

# 3. Si hay errores, revisar log específico
Get-Content logs\mariadb_install.log -Tail 50

# 4. Si es necesario, re-provisionar
vagrant provision mariadb

# 5. Verificar de nuevo
.\scripts\verify-vms.ps1
```

---

## Referencias Cruzadas

### verify-vms.ps1 + clean-logs.ps1

```powershell
# Workflow de mantenimiento completo:
.\scripts\verify-vms.ps1          # Verificar estado
.\scripts\clean-logs.ps1 -DaysToKeep 7  # Limpiar logs antiguos
.\scripts\verify-vms.ps1          # Verificar que limpieza no causó problemas
```

### clean-logs.ps1 + backup-configs.sh

```powershell
# Antes de limpiar logs, guardar configuraciones:
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
.\scripts\clean-logs.ps1 -DaysToKeep 15 -Compress
```

### Todos los scripts en secuencia

```powershell
# Mantenimiento completo:

# 1. Verificar estado inicial
.\scripts\verify-vms.ps1

# 2. Crear backups de configuraciones
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh backup"

# 3. Limpiar logs
.\scripts\clean-logs.ps1 -DaysToKeep 30 -Compress

# 4. Verificar estado final
.\scripts\verify-vms.ps1

# 5. Limpiar backups antiguos
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
vagrant ssh postgresql -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
vagrant ssh adminer -c "sudo bash /vagrant/scripts/backup-configs.sh cleanup 90"
```

---

## Solución de Problemas

### verify-vms.ps1 no se puede ejecutar

**Error:** "verify-vms.ps1 is not recognized"

**Solución:**
```powershell
# Verificar ubicación:
Get-Location  # Debe estar en infrastructure/

# Si no estás ahí:
cd E:\Proyectos\code-space\infrastructure\infrastructure

# Ejecutar:
.\scripts\verify-vms.ps1
```

### clean-logs.ps1 pide múltiples confirmaciones

**Problema:** Al usar -Confirm, pide confirmación para cada archivo

**Solución:** Asegúrate de tener la versión 1.0.6 o superior:
```powershell
.\scripts\clean-logs.ps1 -Help
# Debe decir "Version: 1.0.6" o superior
```

### backup-configs.sh no encuentra archivos

**Error:** "No se encontraron archivos para respaldar"

**Solución:**
```bash
# Verificar que estás en la VM correcta:
vagrant ssh mariadb  # Para backups de MariaDB
vagrant ssh postgresql  # Para backups de PostgreSQL
vagrant ssh adminer  # Para backups de Adminer

# Ejecutar el comando completo:
sudo bash /vagrant/scripts/backup-configs.sh backup
```

### Política de ejecución de PowerShell bloqueada

**Error:** "cannot be loaded because running scripts is disabled"

**Solución temporal:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Solución permanente (como administrador):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned
```

---

## Mejores Prácticas

1. **Siempre verificar después de vagrant up:**
   ```powershell
   vagrant up
   .\scripts\verify-vms.ps1
   ```

2. **Usar -WhatIf antes de operaciones destructivas:**
   ```powershell
   .\scripts\clean-logs.ps1 -DaysToKeep 1 -WhatIf
   ```

3. **Crear backups antes de cambios importantes:**
   ```bash
   vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"
   ```

4. **Mantener logs limpios semanalmente:**
   ```powershell
   .\scripts\clean-logs.ps1 -DaysToKeep 7
   ```

5. **Documentar backups importantes:**
   - Anotar el timestamp del backup
   - Describir qué cambios se hicieron
   - Guardar información de recuperación

---

## Resumen de Comandos Rápidos

```powershell
# Verificación
.\scripts\verify-vms.ps1

# Limpieza de logs (simulación)
.\scripts\clean-logs.ps1 -WhatIf

# Limpieza de logs (real)
.\scripts\clean-logs.ps1 -DaysToKeep 30

# Comprimir logs
.\scripts\clean-logs.ps1 -Compress

# Backup de configuración
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh backup"

# Listar backups
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh list"

# Ayuda de cualquier script
.\scripts\verify-vms.ps1 -Help
.\scripts\clean-logs.ps1 -Help
vagrant ssh mariadb -c "sudo bash /vagrant/scripts/backup-configs.sh help"
```

---

## Notas Adicionales

- Todos los scripts tienen ayuda integrada accesible con `-Help` o `help`
- Los scripts de PowerShell requieren PowerShell 5.1 o superior
- El script de Bash requiere ejecutarse con sudo dentro de las VMs
- Los logs se almacenan en `logs/` y son ignorados por Git (excepto .gitkeep)
- Los backups se almacenan en `/vagrant/backups/` y son accesibles desde el host

---

**Última actualización:** 02 de enero de 2026
**Versión del documento:** 1.0.0