---
id: RB-DEVOPS-003
estado: borrador
propietario: equipo-devops
ultima_actualizacion: 2025-02-14
relacionados: ["UC-REP-004", "RQ-ANL-003"]
---
# Runbook: Reprocesar ETL fallido

1. **Identificar el lote afectado**
   - Consulta `api/reports/logs/etl_failures.log` para obtener `job_id` y timestamp.
   - Verifica en PostgreSQL con `SELECT * FROM etl_jobs WHERE id = :job_id;`.
2. **Aislar el incidente**
   ```bash
   vagrant ssh -- "sudo systemctl stop apscheduler-etl.service"
   ```
   Evita que se inicien ejecuciones concurrentes.
3. **Reprocesar manualmente**
   ```bash
   vagrant ssh -- "cd /vagrant/api && python manage.py run_etl --job-id :job_id"
   ```
   Sustituye `:job_id` por el identificador obtenido en el paso 1.
4. **Validar resultados**
   ```bash
   vagrant ssh -- "cd /vagrant/api && python manage.py check_etl --job-id :job_id"
   ```
   Confirma que el registro cambie a estado `success` y que los datos estén disponibles en el data warehouse.
5. **Reactivar scheduler y documentar**
   ```bash
   vagrant ssh -- "sudo systemctl start apscheduler-etl.service"
   ```
   Registra el incidente en la bitácora y actualiza la matriz de trazabilidad si el UC-REP-004 tuvo impacto.
