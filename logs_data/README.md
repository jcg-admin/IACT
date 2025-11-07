# Logs Data (JSON temporal)

**Proposito**: Almacenar logs en formato JSON mientras Cassandra no esta disponible

## Estructura

- deployment_logs.json: Logs de deployments
- dora_metrics.json: Metricas DORA calculadas
- incident_logs.json: Logs de incidentes

## Migracion a Cassandra

Una vez Cassandra este montada, estos JSONs se migraran a la base de datos definitiva.

