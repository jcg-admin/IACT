# Consideraciones de Seguridad

Advertencias y guías de seguridad para el uso del entorno IACT DevBox.

---

## ADVERTENCIA IMPORTANTE

**Este entorno está diseñado EXCLUSIVAMENTE para desarrollo local.**

El IACT DevBox utiliza configuraciones inseguras que son aceptables para entornos de desarrollo aislados, pero son **COMPLETAMENTE INADECUADAS para producción** o cualquier ambiente expuesto a redes no confiables.

**NO USAR EN PRODUCCIÓN SIN IMPLEMENTAR TODAS LAS MEDIDAS DE SEGURIDAD DESCRITAS EN ESTE DOCUMENTO.**

---

## Índice

1. [Problemas de Seguridad Conocidos](#problemas-de-seguridad-conocidos)
2. [Lista de Verificación para Producción](#lista-de-verificacion-para-produccion)
3. [Configuración de Red](#configuracion-de-red)
4. [Hardening de Bases de Datos](#hardening-de-bases-de-datos)
5. [Certificados SSL/TLS](#certificados-ssltls)
6. [Acceso SSH](#acceso-ssh)
7. [Firewall](#firewall)
8. [Respaldos](#respaldos)
9. [Monitoreo y Auditoría](#monitoreo-y-auditoria)
10. [Cumplimiento Normativo](#cumplimiento-normativo)

---

## Problemas de Seguridad Conocidos

### 1. Contraseñas por Defecto

**Problema:**

Todas las contraseñas están codificadas en texto plano en el Vagrantfile y son públicas:

```ruby
# MariaDB
DB_PASSWORD = "django_pass"
DB_ROOT_PASSWORD = "rootpass123"

# PostgreSQL
POSTGRES_DB_PASSWORD = "django_pass"
POSTGRES_PASSWORD = "postgrespass123"
```

**Riesgos:**
- Acceso no autorizado si la red está expuesta
- Compromiso de credenciales
- Escalación de privilegios

**Mitigación para Producción:**

1. Generar contraseñas seguras:
```bash
openssl rand -base64 32
```

2. Editar Vagrantfile:
```ruby
DB_PASSWORD = "Xk9$mP2#vL5@nQ8wYt4&hR7"
DB_ROOT_PASSWORD = "tR7&hY4!bN3$fG6zMw8#nK5"
POSTGRES_DB_PASSWORD = "pQ2$vL9xDf6&hR3@bY7!cT4"
POSTGRES_PASSWORD = "cT4zAq1$wS2!eD3#rF4@tG5"
```

3. Usar variables de entorno o vault:
```ruby
DB_PASSWORD = ENV['DB_PASSWORD'] || "default_insecure"
```

4. Nunca commitear contraseñas reales a control de versiones.

---

### 2. Acceso Root Remoto Habilitado

**Problema:**

MariaDB permite conexiones root desde cualquier host:
```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'rootpass123';
```

PostgreSQL permite acceso de superusuario desde red:
```
# pg_hba.conf
host all postgres 192.168.56.0/24 md5
```

**Riesgos:**
- Acceso administrativo completo desde red
- Sin restricción de IP
- Vulnerable a ataques de fuerza bruta

**Mitigación para Producción:**

MariaDB:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123'

-- Eliminar acceso root remoto
DELETE FROM mysql.user WHERE User='root' AND Host='%';

-- Crear usuario root solo para localhost
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 'nueva_contraseña_segura';
FLUSH PRIVILEGES;
```

PostgreSQL:
Editar `/etc/postgresql/16/main/pg_hba.conf`:
```
# Antes (inseguro):
host all postgres 192.168.56.0/24 md5

# Después (más seguro):
host all postgres 192.168.56.1/32 md5  # Solo desde IP específica
```

Reiniciar servicio:
```bash
sudo systemctl restart postgresql
```

---

### 3. Firewall Configurado pero Permisivo

**Problema:**

Las VMs tienen UFW (Uncomplicated Firewall) instalado pero configurado de manera permisiva para facilitar desarrollo.

MariaDB:
```bash
ufw allow from 192.168.56.0/24 to any port 3306
```

**Riesgos:**
- Acceso desde toda la subred
- Sin protección contra port scanning
- Sin rate limiting

**Mitigación para Producción:**

Configurar firewall restrictivo:

MariaDB:
```bash
vagrant ssh mariadb

# Deshabilitar firewall actual
sudo ufw disable

# Configurar política por defecto
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir solo desde IPs específicas
sudo ufw allow from 192.168.56.1 to any port 3306 proto tcp
sudo ufw allow from 192.168.56.12 to any port 3306 proto tcp

# Permitir SSH solo desde red local
sudo ufw allow from 192.168.56.0/24 to any port 22 proto tcp

# Habilitar firewall
sudo ufw enable
```

PostgreSQL:
```bash
vagrant ssh postgresql
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.56.1 to any port 5432 proto tcp
sudo ufw allow from 192.168.56.12 to any port 5432 proto tcp
sudo ufw allow from 192.168.56.0/24 to any port 22 proto tcp
sudo ufw enable
```

Adminer:
```bash
vagrant ssh adminer
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow from 192.168.56.0/24 to any port 22 proto tcp
sudo ufw enable
```

---

### 4. Certificados SSL Autofirmados

**Problema:**

Adminer usa certificados SSL autofirmados generados con:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/adminer.key \
  -out /etc/ssl/certs/adminer.crt
```

**Riesgos:**
- Navegadores muestran advertencia de seguridad
- Vulnerable a ataques man-in-the-middle
- No hay validación de identidad
- Certificado expira en 365 días

**Mitigación para Producción:**

Opción 1: Let's Encrypt (gratis):
```bash
vagrant ssh adminer

# Instalar certbot
sudo apt install certbot python3-certbot-apache

# Obtener certificado
sudo certbot --apache -d tudominio.com

# Auto-renovación
sudo certbot renew --dry-run
```

Opción 2: Certificado comercial:
1. Comprar certificado de CA confiable
2. Generar CSR con clave 4096-bit
3. Instalar certificado con cadena completa

Opción 3: Certificado corporativo interno:
```bash
# Usar certificado de CA interna de la empresa
sudo cp certificado_corporativo.crt /etc/ssl/certs/
sudo cp clave_corporativa.key /etc/ssl/private/
```

Actualizar configuración Apache:
```apache
SSLCertificateFile /etc/ssl/certs/certificado_valido.crt
SSLCertificateKeyFile /etc/ssl/private/clave_valida.key
SSLCertificateChainFile /etc/ssl/certs/cadena_ca.crt
```

---

### 5. Bases de Datos Escuchan en Todas las Interfaces

**Problema:**

MariaDB configurado para escuchar en todas las interfaces:
```ini
bind-address = 0.0.0.0
```

PostgreSQL configurado para escuchar en todas las interfaces:
```ini
listen_addresses = '*'
```

**Riesgos:**
- Servicio accesible desde cualquier interfaz de red
- Si VM tiene red pública, servicio queda expuesto
- Sin control granular de acceso

**Mitigación para Producción:**

MariaDB - Editar `/etc/mysql/mariadb.conf.d/50-server.cnf`:
```ini
# Antes
bind-address = 0.0.0.0

# Después
bind-address = 192.168.56.10
```

PostgreSQL - Editar `/etc/postgresql/16/main/postgresql.conf`:
```ini
# Antes
listen_addresses = '*'

# Después
listen_addresses = '192.168.56.11'
```

Reiniciar servicios:
```bash
vagrant ssh mariadb -c "sudo systemctl restart mariadb"
vagrant ssh postgresql -c "sudo systemctl restart postgresql"
```

---

### 6. Sin Autenticación SSH por Clave

**Problema:**

VMs usan la clave SSH insegura por defecto de Vagrant:
```
~/.vagrant.d/insecure_private_key
```

Esta clave es pública y conocida.

**Riesgos:**
- Cualquier persona con la clave puede acceder
- No hay protección si VMs quedan expuestas
- Sin autenticación de dos factores

**Mitigación para Producción:**

Generar nueva clave SSH:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/iact_devbox_key
```

Configurar en cada VM:
```bash
vagrant ssh mariadb

# Agregar clave pública
mkdir -p ~/.ssh
cat >> ~/.ssh/authorized_keys << 'EOF'
# Pegar tu clave pública aquí
EOF

# Configurar permisos
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# Deshabilitar autenticación por contraseña
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config

# Reiniciar SSH
sudo systemctl restart sshd

exit
```

---

### 7. Sin Protección contra Fuerza Bruta

**Problema:**

No hay fail2ban ni protección contra intentos de login fallidos.

**Riesgos:**
- Vulnerable a ataques de fuerza bruta
- Sin bloqueo automático de IPs maliciosas
- Sin logging de intentos fallidos

**Mitigación para Producción:**

Instalar fail2ban:
```bash
vagrant ssh mariadb
sudo apt install fail2ban

# Configurar fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

sudo nano /etc/fail2ban/jail.local
```

Configuración mínima en `jail.local`:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[mysqld-auth]
enabled = true
port = 3306
logpath = /var/log/mysql/error.log
```

Habilitar y arrancar:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
```

---

### 8. Sin Cifrado de Datos en Reposo

**Problema:**

Los archivos de base de datos se almacenan sin cifrar en disco.

**Riesgos:**
- Datos legibles si se accede al almacenamiento
- Sin protección si disco es robado
- Backups sin cifrar

**Mitigación para Producción:**

Opción 1: Cifrado a nivel de tabla (MariaDB):
```sql
-- Habilitar cifrado de tablas
ALTER TABLE mi_tabla ENCRYPTED=YES;
```

Opción 2: Cifrado de base de datos (PostgreSQL):
```sql
-- Usar extensión pgcrypto para cifrado de columnas
CREATE EXTENSION pgcrypto;

-- Cifrar datos sensibles
UPDATE usuarios SET password = crypt('contraseña', gen_salt('bf'));
```

Opción 3: Cifrado de disco completo:
- Usar LUKS en Linux
- BitLocker en Windows
- FileVault en macOS

---

### 9. Sin Logging de Auditoría

**Problema:**

No hay logging detallado de operaciones de base de datos.

**Riesgos:**
- Imposible rastrear accesos no autorizados
- Sin trail de auditoría
- No cumple con normativas de compliance

**Mitigación para Producción:**

MariaDB - Instalar plugin de auditoría:
```sql
INSTALL PLUGIN server_audit SONAME 'server_audit.so';

SET GLOBAL server_audit_logging = ON;
SET GLOBAL server_audit_file_path = '/var/log/mysql/audit.log';
SET GLOBAL server_audit_events = 'CONNECT,QUERY,TABLE';
```

PostgreSQL - Configurar logging:
Editar `/etc/postgresql/16/main/postgresql.conf`:
```ini
log_connections = on
log_disconnections = on
log_duration = on
log_statement = 'all'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

Reiniciar servicios:
```bash
sudo systemctl restart mariadb
sudo systemctl restart postgresql
```

---

### 10. Usuarios con Privilegios Excesivos

**Problema:**

Usuario de aplicación tiene privilegios completos:

MariaDB:
```sql
GRANT ALL PRIVILEGES ON ivr_legacy.* TO 'django_user'@'%';
```

PostgreSQL:
```sql
GRANT ALL PRIVILEGES ON DATABASE iact_analytics TO django_user;
```

**Riesgos:**
- Usuario puede eliminar tablas
- Usuario puede modificar permisos
- Usuario puede crear stored procedures
- Violación del principio de mínimo privilegio

**Mitigación para Producción:**

MariaDB:
```sql
-- Revocar todos los privilegios
REVOKE ALL PRIVILEGES ON ivr_legacy.* FROM 'django_user'@'%';

-- Otorgar solo lo necesario
GRANT SELECT, INSERT, UPDATE, DELETE ON ivr_legacy.* TO 'django_user'@'%';

-- Si necesita crear tablas temporales
GRANT CREATE TEMPORARY TABLES ON ivr_legacy.* TO 'django_user'@'%';

FLUSH PRIVILEGES;
```

PostgreSQL:
```sql
-- Revocar todos los privilegios
REVOKE ALL ON DATABASE iact_analytics FROM django_user;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM django_user;

-- Otorgar solo lo necesario
GRANT CONNECT ON DATABASE iact_analytics TO django_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO django_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO django_user;
```

---

## Lista de Verificación para Producción

### Crítico (Implementar antes de despliegue)

- [ ] Cambiar TODAS las contraseñas por defecto
- [ ] Deshabilitar acceso root/superuser remoto
- [ ] Configurar firewall restrictivo (solo IPs necesarias)
- [ ] Obtener e instalar certificados SSL válidos
- [ ] Configurar bases de datos para escuchar solo en IP específica
- [ ] Eliminar/deshabilitar clave SSH insegura de Vagrant
- [ ] Implementar autenticación SSH por clave solamente
- [ ] Deshabilitar autenticación SSH por contraseña

### Importante (Implementar primera semana)

- [ ] Instalar y configurar fail2ban
- [ ] Habilitar logging de auditoría en bases de datos
- [ ] Implementar principio de mínimo privilegio en usuarios
- [ ] Configurar actualizaciones automáticas de seguridad
- [ ] Configurar backups cifrados
- [ ] Implementar monitoreo de servicios
- [ ] Configurar alertas de seguridad
- [ ] Documentar procedimientos de seguridad

### Recomendado (Implementar primer mes)

- [ ] Habilitar cifrado de datos en reposo
- [ ] Implementar segmentación de red
- [ ] Configurar VPN para acceso remoto
- [ ] Instalar sistema de detección de intrusiones (IDS)
- [ ] Configurar rate limiting en servicios web
- [ ] Implementar rotación automática de credenciales
- [ ] Auditoría de seguridad externa
- [ ] Pruebas de penetración
- [ ] Implementar logging centralizado
- [ ] Configurar SIEM (Security Information and Event Management)

---

## Configuración de Red

### Red Actual (Host-Only)

Configuración actual:
```
Red: 192.168.56.0/24
Tipo: VirtualBox Host-Only Network
Acceso: Solo desde host
```

**Ventajas:**
- Aislada de Internet
- No accesible desde red externa
- Segura para desarrollo local

**Limitaciones:**
- No adecuada para acceso multi-usuario
- No adecuada para ambientes compartidos

### Para Acceso Multi-Usuario

**NO EXPONER directamente a Internet.**

Opciones seguras:

**Opción 1: VPN**
```
Internet → VPN Server → Red Privada → IACT DevBox
```

Implementar OpenVPN o WireGuard.

**Opción 2: Bastion Host**
```
Internet → Bastion (SSH Jump) → Red Privada → IACT DevBox
```

Todo acceso pasa por servidor fortificado.

**Opción 3: Reverse Proxy con Autenticación**
```
Internet → Nginx/Apache (auth) → IACT DevBox
```

Proxy maneja autenticación, SSL, rate limiting.

---

## Hardening de Bases de Datos

### MariaDB

Script de hardening:
```bash
vagrant ssh mariadb
mysql -u root -p'rootpass123'

-- 1. Eliminar usuarios anónimos
DELETE FROM mysql.user WHERE User='';

-- 2. Eliminar base de datos test
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

-- 3. Deshabilitar acceso root remoto
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- 4. Crear usuario con privilegios limitados
CREATE USER 'app_user'@'192.168.56.1' IDENTIFIED BY 'contraseña_segura';
GRANT SELECT, INSERT, UPDATE, DELETE ON ivr_legacy.* TO 'app_user'@'192.168.56.1';

-- 5. Configurar SSL (opcional)
-- ALTER USER 'app_user'@'192.168.56.1' REQUIRE SSL;

FLUSH PRIVILEGES;
```

Configuración adicional en `50-server.cnf`:
```ini
[mysqld]
# Seguridad
local-infile=0
symbolic-links=0
secure-file-priv=/var/lib/mysql-files/

# Performance y límites
max_connections=100
max_user_connections=50
```

### PostgreSQL

Script de hardening:
```bash
vagrant ssh postgresql
sudo -i -u postgres psql

-- 1. Cambiar contraseña de postgres
ALTER USER postgres WITH PASSWORD 'nueva_contraseña_muy_segura';

-- 2. Crear usuario con privilegios limitados
CREATE USER app_user WITH PASSWORD 'contraseña_segura';
GRANT CONNECT ON DATABASE iact_analytics TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- 3. Revocar privilegios públicos
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO app_user;

-- 4. Configurar límites
ALTER USER app_user CONNECTION LIMIT 20;
```

Configuración en `pg_hba.conf`:
```
# Solo desde IPs específicas con SSL
hostssl all all 192.168.56.1/32 md5
hostssl all all 192.168.56.12/32 md5

# Rechazar todo lo demás
host all all 0.0.0.0/0 reject
```

---

## Certificados SSL/TLS

### Estado Actual

Certificado autofirmado:
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048
```

**Problemas:**
- No confiable
- Advertencias en navegador
- Solo 2048-bit (mínimo aceptable)
- Expira en 1 año

### Mejorar Certificado Autofirmado

Para desarrollo extendido:
```bash
vagrant ssh adminer

# Generar clave 4096-bit
sudo openssl genrsa -out /etc/ssl/private/adminer.key 4096

# Generar certificado con validez de 10 años
sudo openssl req -new -x509 -key /etc/ssl/private/adminer.key \
  -out /etc/ssl/certs/adminer.crt -days 3650 \
  -subj "/C=MX/ST=Estado/L=Ciudad/O=Organizacion/CN=192.168.56.12"

# Reiniciar Apache
sudo systemctl restart apache2
```

### Para Producción

**Let's Encrypt (gratis, automatizado):**
```bash
vagrant ssh adminer

# Instalar certbot
sudo apt install certbot python3-certbot-apache

# Obtener certificado (requiere dominio válido)
sudo certbot --apache -d tudominio.com -d www.tudominio.com

# Verificar renovación automática
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

**Certificado comercial:**
1. Generar CSR con clave 4096-bit
2. Enviar CSR a CA (Digicert, GlobalSign, etc.)
3. Recibir certificado firmado
4. Instalar certificado con cadena completa
5. Configurar renovación manual

---

## Acceso SSH

### Configuración Actual

Autenticación por contraseña habilitada:
```
PasswordAuthentication yes
```

Clave insegura de Vagrant:
```
~/.vagrant.d/insecure_private_key
```

### Hardening SSH

Configurar en cada VM (`/etc/ssh/sshd_config`):
```bash
# Deshabilitar root login
PermitRootLogin no

# Solo autenticación por clave
PasswordAuthentication no
PubkeyAuthentication yes

# Deshabilitar métodos inseguros
ChallengeResponseAuthentication no
UsePAM no

# Configurar timeout
ClientAliveInterval 300
ClientAliveCountMax 2

# Limitar usuarios
AllowUsers vagrant app_user

# Configurar protocolo
Protocol 2

# Port no estándar (opcional)
Port 2222
```

Reiniciar SSH:
```bash
sudo systemctl restart sshd
```

### Autenticación de Dos Factores

Instalar Google Authenticator:
```bash
sudo apt install libpam-google-authenticator

# Configurar para usuario
google-authenticator
```

Configurar PAM (`/etc/pam.d/sshd`):
```
auth required pam_google_authenticator.so
```

Configurar SSH (`/etc/ssh/sshd_config`):
```
ChallengeResponseAuthentication yes
AuthenticationMethods publickey,keyboard-interactive
```

---

## Firewall

### Configuración Detallada por VM

Ver sección "Problema 3: Firewall" arriba para configuración completa.

### Monitoreo de Firewall

Verificar reglas:
```bash
vagrant ssh mariadb -c "sudo ufw status verbose"
```

Ver logs de firewall:
```bash
vagrant ssh mariadb -c "sudo tail -f /var/log/ufw.log"
```

### Rate Limiting

Configurar rate limiting en UFW:
```bash
# Limitar intentos de conexión SSH
sudo ufw limit ssh

# Limitar conexiones a MySQL
sudo ufw limit 3306/tcp
```

---

## Respaldos

### Seguridad de Respaldos

**Cifrado:**
- Siempre cifrar respaldos que contengan datos sensibles
- Usar GPG o OpenSSL para cifrado

**Almacenamiento:**
- No almacenar respaldos en mismo servidor
- Usar almacenamiento offsite (cloud, servidor remoto)
- Implementar regla 3-2-1

**Acceso:**
- Controlar quién puede acceder a respaldos
- Usar credenciales separadas para backups
- Auditar accesos a respaldos

Ver: RESPALDO_RECUPERACION.md para procedimientos completos.

---

## Monitoreo y Auditoría

### Logging Centralizado

Enviar logs a servidor central:
```bash
# Configurar rsyslog para enviar a servidor remoto
echo "*.* @log-server:514" | sudo tee -a /etc/rsyslog.conf
sudo systemctl restart rsyslog
```

### Monitoreo de Servicios

Herramientas recomendadas:
- Prometheus + Grafana
- Nagios
- Zabbix
- ELK Stack (Elasticsearch, Logstash, Kibana)

### Alertas de Seguridad

Configurar alertas para:
- Intentos de login fallidos
- Accesos root
- Cambios en configuración
- Uso anormal de recursos
- Modificaciones en bases de datos

---

## Cumplimiento Normativo

### GDPR (Protección de Datos Personales)

Si maneja datos personales de ciudadanos UE:
- Implementar cifrado de datos
- Mantener logs de acceso
- Implementar derecho al olvido
- Documentar procesamiento de datos
- Notificación de brechas en 72 horas

### PCI DSS (Datos de Tarjetas de Pago)

Si maneja datos de tarjetas:
- Cifrado de datos de tarjetas
- No almacenar CVV
- Implementar tokenización
- Auditorías trimestrales
- Segmentación de red

### HIPAA (Datos de Salud)

Si maneja datos médicos:
- Cifrado end-to-end
- Logs de auditoría completos
- Control de acceso estricto
- Backups seguros
- Business Associate Agreements

### SOX (Datos Financieros)

Si maneja datos financieros corporativos:
- Trail de auditoría completo
- Segregación de funciones
- Controles de acceso
- Retención de datos
- Auditorías externas

---

## Procedimiento de Respuesta a Incidentes

### Si Detectas Acceso No Autorizado

1. **Aislar inmediatamente:**
   ```bash
   vagrant halt  # Detener todas las VMs
   ```

2. **Preservar evidencia:**
   - No modificar logs
   - Crear snapshots de VMs
   - Documentar todo

3. **Investigar:**
   - Revisar logs de acceso
   - Identificar punto de entrada
   - Determinar alcance del compromiso

4. **Remediar:**
   - Cambiar todas las contraseñas
   - Parchear vulnerabilidades
   - Restaurar desde backup limpio si es necesario

5. **Notificar:**
   - Informar a stakeholders
   - Cumplir con obligaciones legales
   - Documentar lecciones aprendidas

6. **Prevenir recurrencia:**
   - Implementar controles adicionales
   - Actualizar procedimientos
   - Capacitar personal

---

## Recursos Adicionales

### Documentación Oficial

- MariaDB Security: https://mariadb.com/kb/en/securing-mariadb/
- PostgreSQL Security: https://www.postgresql.org/docs/current/security.html
- Apache Security Tips: https://httpd.apache.org/docs/2.4/misc/security_tips.html
- OWASP Database Security: https://owasp.org/www-project-database-security/

### Herramientas de Seguridad

- Lynis: Auditoría de seguridad del sistema
- OpenVAS: Escáner de vulnerabilidades
- SQLMap: Testing de SQL injection
- Nmap: Escaneo de red y puertos

### Auditoría de Seguridad

Ejecutar Lynis en cada VM:
```bash
vagrant ssh mariadb
sudo apt install lynis
sudo lynis audit system
exit
```

Revisar reporte y aplicar recomendaciones.

---

## Conclusión

Este entorno de desarrollo prioriza facilidad de uso sobre seguridad. Todas las configuraciones por defecto deben ser revisadas y endurecidas antes de cualquier uso en producción.

La seguridad no es una configuración única sino un proceso continuo que requiere:
- Auditorías regulares
- Actualizaciones de seguridad
- Monitoreo activo
- Respuesta rápida a incidentes
- Capacitación del equipo

Cuando tengas dudas sobre seguridad, consulta con profesionales especializados antes de exponer el sistema a redes no confiables.

---

## Referencias

- CONFIGURACION.md - Cambio de contraseñas
- RESPALDO_RECUPERACION.md - Backups seguros
- ARCHITECTURE.md - Configuración de red
- TROUBLESHOOTING.md - Diagnóstico de problemas

---

Última actualización: 02 de enero de 2026
Versión del documento: 1.0.0