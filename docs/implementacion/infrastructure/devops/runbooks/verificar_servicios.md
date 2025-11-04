---
id: RB-DEVOPS-002
estado: borrador
propietario: equipo-devops
ultima_actualizacion: 2025-02-14
relacionados: ["RB-DEVOPS-001", "RQ-ANL-002"]
---
# Runbook: Verificar servicios PostgreSQL y MariaDB

1. **Asegurar VM activa**
   ```bash
   vagrant status
   vagrant up
   ```
   Solo continúa cuando la VM aparezca como `running`.
2. **Probar conectividad desde el host**
   ```bash
   ./infrastructure/scripts/verificar_servicios.sh
   ```
   El script usa `psql` y `mysql` para validar los puertos `15432` y `13306`.
3. **Reiniciar servicios si hay fallos**
   ```bash
   vagrant ssh -- "sudo systemctl restart postgresql mariadb"
   sleep 10
   ./infrastructure/scripts/verificar_servicios.sh
   ```
4. **Actualizar credenciales locales**
   Confirma que `.env` contenga las variables `POSTGRES_HOST=127.0.0.1` y `MARIADB_HOST=127.0.0.1` con los puertos expuestos.
5. **Escalar incidentes**
   Si la verificación sigue fallando, crea ticket `INC-OPS-###` y adjunta los logs de `/var/log/postgresql/` y `/var/log/mysql/`.
