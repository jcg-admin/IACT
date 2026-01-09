# Guía de Respaldo y Recuperación

Documentación completa de procedimientos de backup y restore para bases de datos y máquinas virtuales.

---

## Índice

1. [Estrategias de Respaldo](#estrategias-de-respaldo)
2. [Respaldo de MariaDB](#respaldo-de-mariadb)
3. [Restauración de MariaDB](#restauracion-de-mariadb)
4. [Respaldo de PostgreSQL](#respaldo-de-postgresql)
5. [Restauración de PostgreSQL](#restauracion-de-postgresql)
6. [Snapshots de Máquinas Virtuales](#snapshots-de-maquinas-virtuales)
7. [Respaldo Completo del Sistema](#respaldo-completo-del-sistema)
8. [Recuperación ante Desastres](#recuperacion-ante-desastres)
9. [Verificación de Respaldos](#verificacion-de-respaldos)
10. [Automatización](#automatizacion)

---

## Estrategias de Respaldo

### Tipos de Respaldo

**Respaldo Lógico:**
- Exporta datos como SQL
- Portable entre versiones
- Fácil de inspeccionar
- Más lento para restaurar

**Respaldo Físico:**
- Copia archivos de datos
- Más rápido
- Específico de versión
- Requiere detener servicio

**Snapshot de VM:**
- Captura estado completo
- Incluye sistema operativo
- Recuperación rápida
- Requiere más espacio

### Política de Respaldo Recomendada

**Respaldos diarios:**
- Tipo: Lógico (SQL dumps)
- Retención: 7 días
- Automatizado: Cron/Task Scheduler

**Respaldos semanales:**
- Tipo: Snapshot de VM
- Retención: 4 semanas
- Manual o automatizado

**Respaldos mensuales:**
- Tipo: Completo (SQL + Snapshot)
- Retención: 12 meses
- Almacenamiento externo

**Respaldos antes de cambios:**
- Tipo: Snapshot de VM
- Retención: Hasta validar cambio
- Manual

### Regla 3-2-1

Aplicar regla 3-2-1 para respaldos críticos:
- **3** copias de los datos (original + 2 respaldos)
- **2** tipos diferentes de medios (local + nube)
- **1** copia fuera del sitio (offsite)

---

## Respaldo de MariaDB

### Respaldo Lógico con mysqldump

Respaldo de una base de datos:
```bash
vagrant ssh mariadb
mysqldump -u root -p'rootpass123' ivr_legacy > /vagrant/backup_ivr_$(date +%Y%m%d).sql
exit
```

Archivo creado en: `./backup_ivr_YYYYMMDD.sql` (accesible desde host)

Respaldo de todas las bases de datos:
```bash
vagrant ssh mariadb
mysqldump -u root -p'rootpass123' --all-databases > /vagrant/backup_all_$(date +%Y%m%d).sql
exit
```

Respaldo con compresión:
```bash
vagrant ssh mariadb
mysqldump -u root -p'rootpass123' ivr_legacy | gzip > /vagrant/backup_ivr_$(date +%Y%m%d).sql.gz
exit
```

### Opciones Útiles de mysqldump

Respaldo completo con rutinas y triggers:
```bash
mysqldump -u root -p'rootpass123' \
  --routines \
  --triggers \
  --events \
  ivr_legacy > backup_completo.sql
```

Respaldo con transacción consistente:
```bash
mysqldump -u root -p'rootpass123' \
  --single-transaction \
  --quick \
  ivr_legacy > backup_consistente.sql
```

Respaldo excluyendo tablas:
```bash
mysqldump -u root -p'rootpass123' \
  --ignore-table=ivr_legacy.logs \
  --ignore-table=ivr_legacy.sessions \
  ivr_legacy > backup_sin_logs.sql
```

Solo estructura (sin datos):
```bash
mysqldump -u root -p'rootpass123' \
  --no-data \
  ivr_legacy > schema_only.sql
```

Solo datos (sin estructura):
```bash
mysqldump -u root -p'rootpass123' \
  --no-create-info \
  ivr_legacy > data_only.sql
```

### Respaldo desde el Host

Sin SSH a la VM:
```bash
mysqldump -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy > backup_ivr.sql
```

Con compresión:
```bash
mysqldump -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy | gzip > backup_ivr.sql.gz
```

### Respaldo Físico (Hot Backup)

ADVERTENCIA: Requiere detener el servicio o usar herramientas especializadas.

Método 1: Detener servicio (downtime)
```bash
vagrant ssh mariadb
sudo systemctl stop mariadb
sudo tar -czf /vagrant/mariadb_data_$(date +%Y%m%d).tar.gz /var/lib/mysql
sudo systemctl start mariadb
exit
```

Método 2: Usar mariabackup (sin downtime)
```bash
vagrant ssh mariadb
sudo mariabackup --backup --target-dir=/vagrant/backup_mariadb --user=root --password=rootpass123
exit
```

---

## Restauración de MariaDB

### Restaurar desde SQL Dump

Restaurar base de datos completa:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123' ivr_legacy < /vagrant/backup_ivr_20260102.sql
exit
```

Restaurar desde archivo comprimido:
```bash
vagrant ssh mariadb
gunzip < /vagrant/backup_ivr_20260102.sql.gz | mysql -u root -p'rootpass123' ivr_legacy
exit
```

Restaurar todas las bases de datos:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123' < /vagrant/backup_all_20260102.sql
exit
```

### Restaurar Recreando Base de Datos

Cuando necesitas empezar desde cero:
```bash
vagrant ssh mariadb

# Conectar a MySQL
mysql -u root -p'rootpass123'

# Eliminar base de datos existente
DROP DATABASE IF EXISTS ivr_legacy;

# Recrear base de datos
CREATE DATABASE ivr_legacy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Salir de MySQL
exit

# Restaurar datos
mysql -u root -p'rootpass123' ivr_legacy < /vagrant/backup_ivr_20260102.sql

exit
```

### Restaurar Tabla Específica

Extraer tabla de respaldo:
```bash
# En el host, extraer solo una tabla del dump
grep -A 1000 "CREATE TABLE \`mi_tabla\`" backup_ivr.sql > tabla_especifica.sql
```

Restaurar la tabla:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123' ivr_legacy -e "SET foreign_key_checks = 0;"
mysql -u root -p'rootpass123' ivr_legacy < /vagrant/tabla_especifica.sql
mysql -u root -p'rootpass123' ivr_legacy -e "SET foreign_key_checks = 1;"
exit
```

### Restaurar desde Host

```bash
mysql -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy < backup_ivr_20260102.sql
```

### Restaurar Respaldo Físico

Desde backup con mariabackup:
```bash
vagrant ssh mariadb

# Detener servicio
sudo systemctl stop mariadb

# Preparar respaldo
sudo mariabackup --prepare --target-dir=/vagrant/backup_mariadb

# Restaurar
sudo mariabackup --copy-back --target-dir=/vagrant/backup_mariadb

# Corregir permisos
sudo chown -R mysql:mysql /var/lib/mysql

# Iniciar servicio
sudo systemctl start mariadb

exit
```

---

## Respaldo de PostgreSQL

### Respaldo Lógico con pg_dump

Respaldo de una base de datos:
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_dump -U postgres iact_analytics > /vagrant/backup_analytics_$(date +%Y%m%d).sql
exit
```

Respaldo de todas las bases de datos:
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_dumpall -U postgres > /vagrant/backup_all_$(date +%Y%m%d).sql
exit
```

Respaldo con compresión:
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_dump -U postgres iact_analytics | gzip > /vagrant/backup_analytics_$(date +%Y%m%d).sql.gz
exit
```

Respaldo en formato custom (más rápido de restaurar):
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_dump -U postgres -Fc iact_analytics > /vagrant/backup_analytics_$(date +%Y%m%d).dump
exit
```

Respaldo en formato directory (paralelo):
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_dump -U postgres -Fd -j 4 iact_analytics -f /vagrant/backup_analytics_dir
exit
```

### Opciones Útiles de pg_dump

Solo esquema (sin datos):
```bash
PGPASSWORD='postgrespass123' pg_dump -U postgres -s iact_analytics > schema_only.sql
```

Solo datos (sin esquema):
```bash
PGPASSWORD='postgrespass123' pg_dump -U postgres -a iact_analytics > data_only.sql
```

Excluir tablas específicas:
```bash
PGPASSWORD='postgrespass123' pg_dump -U postgres \
  -T logs \
  -T sessions \
  iact_analytics > backup_sin_logs.sql
```

Incluir solo tablas específicas:
```bash
PGPASSWORD='postgrespass123' pg_dump -U postgres \
  -t users \
  -t products \
  iact_analytics > backup_tablas_especificas.sql
```

Con ownership y privileges:
```bash
PGPASSWORD='postgrespass123' pg_dump -U postgres -O iact_analytics > backup_sin_owners.sql
```

### Respaldo desde el Host

```bash
PGPASSWORD='postgrespass123' pg_dump -h 192.168.56.11 -U postgres iact_analytics > backup_analytics.sql
```

Con compresión:
```bash
PGPASSWORD='postgrespass123' pg_dump -h 192.168.56.11 -U postgres iact_analytics | gzip > backup_analytics.sql.gz
```

### Respaldo Físico

Método 1: Detener servicio (downtime)
```bash
vagrant ssh postgresql
sudo systemctl stop postgresql
sudo tar -czf /vagrant/postgres_data_$(date +%Y%m%d).tar.gz /var/lib/postgresql/16/main
sudo systemctl start postgresql
exit
```

Método 2: Usar pg_basebackup (sin downtime)
```bash
vagrant ssh postgresql
sudo -u postgres pg_basebackup -D /vagrant/backup_postgres -Ft -z -P
exit
```

---

## Restauración de PostgreSQL

### Restaurar desde SQL Dump

Restaurar base de datos:
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' psql -U postgres iact_analytics < /vagrant/backup_analytics_20260102.sql
exit
```

Restaurar desde archivo comprimido:
```bash
vagrant ssh postgresql
gunzip < /vagrant/backup_analytics_20260102.sql.gz | PGPASSWORD='postgrespass123' psql -U postgres iact_analytics
exit
```

Restaurar todas las bases de datos:
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' psql -U postgres < /vagrant/backup_all_20260102.sql
exit
```

### Restaurar desde Formato Custom

```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_restore -U postgres -d iact_analytics /vagrant/backup_analytics_20260102.dump
exit
```

Con opciones:
```bash
# Limpiar base de datos antes de restaurar
PGPASSWORD='postgrespass123' pg_restore -U postgres -d iact_analytics --clean /vagrant/backup.dump

# Crear base de datos si no existe
PGPASSWORD='postgrespass123' pg_restore -U postgres -d postgres --create /vagrant/backup.dump

# Restaurar solo datos (sin esquema)
PGPASSWORD='postgrespass123' pg_restore -U postgres -d iact_analytics --data-only /vagrant/backup.dump

# Restaurar en paralelo (más rápido)
PGPASSWORD='postgrespass123' pg_restore -U postgres -d iact_analytics -j 4 /vagrant/backup.dump
```

### Restaurar Recreando Base de Datos

```bash
vagrant ssh postgresql
sudo -u postgres psql

-- Terminar conexiones existentes
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'iact_analytics'
AND pid <> pg_backend_pid();

-- Eliminar base de datos
DROP DATABASE IF EXISTS iact_analytics;

-- Recrear base de datos
CREATE DATABASE iact_analytics OWNER django_user;

-- Salir
\q

# Restaurar datos
PGPASSWORD='postgrespass123' psql -U postgres iact_analytics < /vagrant/backup_analytics_20260102.sql

exit
```

### Restaurar Tabla Específica

Desde formato custom:
```bash
vagrant ssh postgresql
PGPASSWORD='postgrespass123' pg_restore -U postgres -d iact_analytics -t mi_tabla /vagrant/backup.dump
exit
```

Desde SQL:
```bash
# Extraer tabla específica del dump
pg_restore --table=mi_tabla backup.dump > tabla_especifica.sql

# O desde SQL dump
grep -A 1000 "CREATE TABLE mi_tabla" backup.sql > tabla_especifica.sql

# Restaurar
PGPASSWORD='postgrespass123' psql -U postgres iact_analytics < tabla_especifica.sql
```

### Restaurar desde Host

```bash
PGPASSWORD='postgrespass123' psql -h 192.168.56.11 -U postgres iact_analytics < backup_analytics.sql
```

---

## Snapshots de Máquinas Virtuales

### Crear Snapshot

Snapshot de VM específica:
```bash
vagrant snapshot save mariadb mariadb_baseline
vagrant snapshot save postgresql postgres_baseline
vagrant snapshot save adminer adminer_baseline
```

Snapshot con nombre descriptivo:
```bash
vagrant snapshot save mariadb mariadb_$(date +%Y%m%d)_antes_upgrade
vagrant snapshot save postgresql postgres_$(date +%Y%m%d)_produccion
```

Snapshot de todas las VMs:
```bash
for vm in mariadb postgresql adminer; do
  vagrant snapshot save $vm ${vm}_$(date +%Y%m%d)
done
```

### Listar Snapshots

```bash
vagrant snapshot list mariadb
vagrant snapshot list postgresql
vagrant snapshot list adminer
```

Salida ejemplo:
```
mariadb_baseline
mariadb_20260102_antes_upgrade
mariadb_20260105_test_data
```

### Restaurar Snapshot

Restaurar a snapshot específico:
```bash
vagrant snapshot restore mariadb mariadb_baseline
```

Restaurar y arrancar VM:
```bash
vagrant snapshot restore mariadb mariadb_baseline
vagrant up mariadb
```

NOTA: Restaurar snapshot revierte la VM al estado exacto cuando se creó el snapshot.

### Eliminar Snapshot

Eliminar snapshot específico:
```bash
vagrant snapshot delete mariadb mariadb_20260102_antes_upgrade
```

Eliminar todos los snapshots de una VM:
```bash
vagrant snapshot list mariadb | tail -n +2 | while read name; do
  vagrant snapshot delete mariadb "$name"
done
```

### Push/Pop Snapshots

Crear snapshot temporal (push):
```bash
vagrant snapshot push mariadb
```

Restaurar último snapshot temporal (pop):
```bash
vagrant snapshot pop mariadb
```

Restaurar sin eliminar snapshot (peek):
```bash
vagrant snapshot pop --no-delete mariadb
```

Uso típico:
```bash
# Antes de cambio riesgoso
vagrant snapshot push mariadb

# Hacer cambios...

# Si algo sale mal:
vagrant snapshot pop mariadb

# Si todo está bien:
vagrant snapshot delete mariadb --name (último push)
```

---

## Respaldo Completo del Sistema

### Script de Respaldo Completo

Crear archivo `backup_completo.sh`:
```bash
#!/bin/bash

BACKUP_DIR="./backups/completo_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=== Respaldo Completo IACT DevBox ==="
echo "Directorio: $BACKUP_DIR"

# 1. Respaldar MariaDB
echo "Respaldando MariaDB..."
vagrant ssh mariadb -c "mysqldump -u root -p'rootpass123' --all-databases" | gzip > "$BACKUP_DIR/mariadb_all.sql.gz"

# 2. Respaldar PostgreSQL
echo "Respaldando PostgreSQL..."
PGPASSWORD='postgrespass123' vagrant ssh postgresql -c "pg_dumpall -U postgres" | gzip > "$BACKUP_DIR/postgresql_all.sql.gz"

# 3. Crear snapshots de VMs
echo "Creando snapshots de VMs..."
for vm in mariadb postgresql adminer; do
  vagrant snapshot save $vm "backup_$(date +%Y%m%d)"
done

# 4. Copiar archivos de configuración
echo "Respaldando configuraciones..."
cp Vagrantfile "$BACKUP_DIR/"
cp -r provisioners "$BACKUP_DIR/"
cp -r utils "$BACKUP_DIR/"
cp -r config "$BACKUP_DIR/" 2>/dev/null || true

# 5. Crear archivo de información
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
Respaldo Completo IACT DevBox
Fecha: $(date)
Hostname: $(hostname)
Usuario: $(whoami)

Contenido:
- mariadb_all.sql.gz: Todas las bases de datos MariaDB
- postgresql_all.sql.gz: Todas las bases de datos PostgreSQL
- Snapshots de VMs: backup_$(date +%Y%m%d)
- Vagrantfile: Configuración de VMs
- provisioners/: Scripts de aprovisionamiento
- utils/: Utilidades compartidas
- config/: Archivos de configuración

Para restaurar:
1. vagrant snapshot restore <vm> backup_$(date +%Y%m%d)
2. O importar dumps SQL manualmente
EOF

echo "Respaldo completado en: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"
```

Hacer ejecutable:
```bash
chmod +x backup_completo.sh
```

Ejecutar:
```bash
./backup_completo.sh
```

### Estructura de Respaldo

```
backups/
└── completo_20260102_153000/
    ├── BACKUP_INFO.txt
    ├── mariadb_all.sql.gz
    ├── postgresql_all.sql.gz
    ├── Vagrantfile
    ├── provisioners/
    ├── utils/
    └── config/
```

---

## Recuperación ante Desastres

### Escenario 1: Corrupción de Base de Datos

Síntomas:
- Errores al consultar tablas
- Servicio de BD no arranca
- Datos inconsistentes

Recuperación:
```bash
# Opción A: Restaurar desde snapshot
vagrant snapshot restore mariadb mariadb_baseline
vagrant up mariadb

# Opción B: Restaurar desde respaldo SQL
vagrant ssh mariadb
mysql -u root -p'rootpass123'
DROP DATABASE ivr_legacy;
CREATE DATABASE ivr_legacy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit
mysql -u root -p'rootpass123' ivr_legacy < /vagrant/backup_ivr_latest.sql
```

### Escenario 2: VM Corrupta

Síntomas:
- VM no arranca
- Errores de VirtualBox
- Sistema de archivos corrupto

Recuperación:
```bash
# Opción A: Restaurar snapshot
vagrant snapshot restore postgresql postgres_baseline

# Opción B: Destruir y recrear
vagrant destroy -f postgresql
vagrant up postgresql

# Luego restaurar datos
PGPASSWORD='postgrespass123' psql -h 192.168.56.11 -U postgres iact_analytics < backup_analytics.sql
```

### Escenario 3: Pérdida Total del Host

Recuperación completa:

1. **Instalar prerequisitos:**
```bash
# Instalar VirtualBox y Vagrant
```

2. **Clonar/descargar proyecto:**
```bash
git clone <repositorio>
cd infrastructure
```

3. **Restaurar Vagrantfile:**
```bash
cp backups/completo_20260102/Vagrantfile .
```

4. **Levantar VMs:**
```bash
vagrant up
```

5. **Restaurar bases de datos:**
```bash
# MariaDB
gunzip < backups/completo_20260102/mariadb_all.sql.gz | \
  mysql -h 192.168.56.10 -u root -p'rootpass123'

# PostgreSQL
gunzip < backups/completo_20260102/postgresql_all.sql.gz | \
  PGPASSWORD='postgrespass123' psql -h 192.168.56.11 -U postgres
```

6. **Verificar:**
```bash
.\scripts\verify-vms.ps1
```

---

## Verificación de Respaldos

### Verificar Integridad de Archivos

Verificar que el archivo SQL es válido:
```bash
# Ver primeras líneas
head -n 20 backup_ivr_20260102.sql

# Para archivos comprimidos
gunzip -t backup_ivr_20260102.sql.gz
```

Verificar tamaño:
```bash
ls -lh backup_*.sql
```

### Probar Restauración

Crear base de datos temporal para probar:

MariaDB:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123' -e "CREATE DATABASE test_restore;"
mysql -u root -p'rootpass123' test_restore < /vagrant/backup_ivr_20260102.sql
mysql -u root -p'rootpass123' -e "SHOW TABLES FROM test_restore;"
mysql -u root -p'rootpass123' -e "SELECT COUNT(*) FROM test_restore.mi_tabla;"
mysql -u root -p'rootpass123' -e "DROP DATABASE test_restore;"
exit
```

PostgreSQL:
```bash
vagrant ssh postgresql
sudo -u postgres psql -c "CREATE DATABASE test_restore;"
sudo -u postgres psql test_restore < /vagrant/backup_analytics_20260102.sql
sudo -u postgres psql -c "\dt" test_restore
sudo -u postgres psql -c "SELECT COUNT(*) FROM mi_tabla;" test_restore
sudo -u postgres psql -c "DROP DATABASE test_restore;"
exit
```

### Verificar Snapshots

Listar snapshots disponibles:
```bash
vagrant snapshot list mariadb
vagrant snapshot list postgresql
vagrant snapshot list adminer
```

Probar restauración de snapshot:
```bash
# Crear snapshot de prueba
vagrant snapshot save mariadb test_snapshot

# Hacer cambios
vagrant ssh mariadb -c "mysql -u root -p'rootpass123' -e 'CREATE DATABASE test_db;'"

# Restaurar snapshot
vagrant snapshot restore mariadb test_snapshot

# Verificar que cambio se revirtió
vagrant ssh mariadb -c "mysql -u root -p'rootpass123' -e 'SHOW DATABASES;'"
# test_db no debe aparecer

# Limpiar
vagrant snapshot delete mariadb test_snapshot
```

### Checksum de Respaldos

Crear checksums:
```bash
# Crear checksum MD5
md5sum backup_ivr_20260102.sql > backup_ivr_20260102.sql.md5

# Crear checksum SHA256
sha256sum backup_ivr_20260102.sql > backup_ivr_20260102.sql.sha256
```

Verificar checksums:
```bash
# Verificar MD5
md5sum -c backup_ivr_20260102.sql.md5

# Verificar SHA256
sha256sum -c backup_ivr_20260102.sql.sha256
```

---

## Automatización

### Script de Respaldo Automático MariaDB

Crear `backup_mariadb_auto.sh`:
```bash
#!/bin/bash

BACKUP_DIR="./backups/mariadb"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Crear directorio
mkdir -p "$BACKUP_DIR"

# Ejecutar respaldo
echo "Respaldando MariaDB..."
vagrant ssh mariadb -c "mysqldump -u root -p'rootpass123' ivr_legacy" | \
  gzip > "$BACKUP_DIR/ivr_legacy_$DATE.sql.gz"

# Eliminar respaldos antiguos
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Respaldo completado: ivr_legacy_$DATE.sql.gz"
```

### Script de Respaldo Automático PostgreSQL

Crear `backup_postgresql_auto.sh`:
```bash
#!/bin/bash

BACKUP_DIR="./backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Crear directorio
mkdir -p "$BACKUP_DIR"

# Ejecutar respaldo
echo "Respaldando PostgreSQL..."
PGPASSWORD='postgrespass123' vagrant ssh postgresql -c \
  "pg_dump -U postgres iact_analytics" | \
  gzip > "$BACKUP_DIR/iact_analytics_$DATE.sql.gz"

# Eliminar respaldos antiguos
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Respaldo completado: iact_analytics_$DATE.sql.gz"
```

### Programar con Cron (Linux/macOS)

Editar crontab:
```bash
crontab -e
```

Agregar tareas:
```bash
# Respaldo diario a las 2 AM
0 2 * * * /ruta/a/infrastructure/backup_mariadb_auto.sh >> /ruta/a/logs/backup_mariadb.log 2>&1
0 3 * * * /ruta/a/infrastructure/backup_postgresql_auto.sh >> /ruta/a/logs/backup_postgres.log 2>&1

# Respaldo semanal (domingo a las 4 AM) con snapshots
0 4 * * 0 /ruta/a/infrastructure/backup_completo.sh >> /ruta/a/logs/backup_completo.log 2>&1
```

### Programar con Task Scheduler (Windows)

Crear tarea programada:
```powershell
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
  -Argument "-File C:\ruta\a\infrastructure\backup_mariadb_auto.ps1"

$Trigger = New-ScheduledTaskTrigger -Daily -At 2am

$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName "IACT DevBox - Backup MariaDB" `
  -Action $Action -Trigger $Trigger -Settings $Settings
```

### Rotación Automática de Respaldos

Script con rotación inteligente:
```bash
#!/bin/bash

BACKUP_DIR="./backups/mariadb"
DATE=$(date +%Y%m%d_%H%M%S)

# Retención
DAILY_RETENTION=7      # Mantener últimos 7 días
WEEKLY_RETENTION=28    # Mantener últimas 4 semanas
MONTHLY_RETENTION=365  # Mantener último año

# Crear respaldo
mkdir -p "$BACKUP_DIR"
vagrant ssh mariadb -c "mysqldump -u root -p'rootpass123' ivr_legacy" | \
  gzip > "$BACKUP_DIR/daily_$DATE.sql.gz"

# Cada domingo, crear respaldo semanal
if [ $(date +%u) -eq 7 ]; then
  cp "$BACKUP_DIR/daily_$DATE.sql.gz" "$BACKUP_DIR/weekly_$DATE.sql.gz"
fi

# Primer día del mes, crear respaldo mensual
if [ $(date +%d) -eq 01 ]; then
  cp "$BACKUP_DIR/daily_$DATE.sql.gz" "$BACKUP_DIR/monthly_$DATE.sql.gz"
fi

# Limpiar respaldos antiguos
find "$BACKUP_DIR" -name "daily_*.sql.gz" -mtime +$DAILY_RETENTION -delete
find "$BACKUP_DIR" -name "weekly_*.sql.gz" -mtime +$WEEKLY_RETENTION -delete
find "$BACKUP_DIR" -name "monthly_*.sql.gz" -mtime +$MONTHLY_RETENTION -delete
```

---

## Encriptación de Respaldos

### Encriptar con GPG

Crear respaldo encriptado:
```bash
mysqldump -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy | \
  gpg --symmetric --cipher-algo AES256 > backup_ivr.sql.gpg
```

Restaurar desde respaldo encriptado:
```bash
gpg --decrypt backup_ivr.sql.gpg | \
  mysql -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy
```

### Encriptar con OpenSSL

Crear respaldo encriptado:
```bash
mysqldump -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy | \
  openssl enc -aes-256-cbc -salt -pbkdf2 > backup_ivr.sql.enc
```

Restaurar desde respaldo encriptado:
```bash
openssl enc -aes-256-cbc -d -pbkdf2 -in backup_ivr.sql.enc | \
  mysql -h 192.168.56.10 -u root -p'rootpass123' ivr_legacy
```

---

## Almacenamiento Externo

### Copiar a Cloud Storage

AWS S3:
```bash
aws s3 cp backup_ivr_20260102.sql.gz s3://mi-bucket/backups/iact-devbox/
```

Google Cloud Storage:
```bash
gsutil cp backup_ivr_20260102.sql.gz gs://mi-bucket/backups/iact-devbox/
```

### Copiar a Servidor Remoto

SCP (SSH):
```bash
scp backup_ivr_20260102.sql.gz usuario@servidor:/backups/iact-devbox/
```

Rsync:
```bash
rsync -avz backups/ usuario@servidor:/backups/iact-devbox/
```

### Copiar a Unidad Externa

```bash
# Linux/macOS
cp backup_ivr_20260102.sql.gz /mnt/external/backups/

# Windows
Copy-Item backup_ivr_20260102.sql.gz E:\backups\
```

---

## Mejores Prácticas

1. **Probar restauraciones regularmente**: Mínimo una vez al mes

2. **Mantener múltiples copias**: Seguir regla 3-2-1

3. **Encriptar respaldos sensibles**: Especialmente si se almacenan externamente

4. **Documentar procedimientos**: Mantener runbook de recuperación actualizado

5. **Automatizar respaldos**: No confiar en respaldos manuales

6. **Verificar integridad**: Usar checksums y pruebas de restauración

7. **Monitorear espacio en disco**: Asegurar suficiente espacio para respaldos

8. **Retener snapshots temporalmente**: Eliminar después de validar cambios

9. **Etiquetar respaldos claramente**: Usar nombres descriptivos con fecha

10. **Mantener logs de respaldos**: Para auditoría y troubleshooting

---

## Solución de Problemas

### Respaldo falla con "Out of Space"

Verificar espacio:
```bash
df -h
```

Solución:
- Limpiar respaldos antiguos
- Usar compresión
- Aumentar espacio en disco

### Restauración falla con "Access Denied"

Verificar permisos:
```bash
# MariaDB
mysql -u root -p'rootpass123' -e "SHOW GRANTS FOR 'django_user'@'%';"

# PostgreSQL
sudo -u postgres psql -c "\du"
```

### Snapshot no restaura correctamente

Verificar que snapshot existe:
```bash
vagrant snapshot list mariadb
```

Intentar con snapshot diferente o recrear VM.

### Respaldo muy lento

Opciones:
- Usar formato custom en PostgreSQL (`-Fc`)
- Usar compresión en pipe
- Excluir tablas grandes innecesarias
- Ejecutar durante horas de baja actividad

---

## Referencias

- CONFIGURACION.md - Cambio de contraseñas
- USO_DIARIO.md - Snapshots de VMs
- SCRIPTS.md - backup-configs.sh
- ARCHITECTURE.md - Estructura del sistema
- TROUBLESHOOTING.md - Diagnóstico de problemas

---

Última actualización: 02 de enero de 2026
Versión del documento: 1.0.0