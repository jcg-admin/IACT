---
id: ADR-2025-001
estado: aceptado
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-14
relacionados: ["RQ-ANL-001", "RN-015"]
---
# ADR-2025-001: Consolidar entorno Vagrant + Apache con mod_wsgi

## Contexto
Las evaluaciones de devcontainer y Docker mostraron incompatibilidades con las restricciones del proyecto (solo Vagrant, Apache y APScheduler). Los equipos de analytics requieren reproducibilidad sin depender de Docker Desktop ni Codespaces.

## Decisión
Mantener Vagrant como capa de virtualización oficial, sirviendo la aplicación Django bajo Apache 2.4 en modo daemon con mod_wsgi. La VM publica PostgreSQL y MariaDB mediante el `Vagrantfile` actual y expone scripts de verificación en `infrastructure/scripts`.

## Consecuencias
- **Positivas:** Configuración alineada con producción, soporte de Apache para TLS y logging unificado, menor fricción legal (sin Docker Desktop).
- **Negativas:** Provisiones iniciales más lentas y necesidad de VirtualBox; se requiere documentar runbooks para incidentes.

## Seguimiento
- Revisar `infrastructure/provisioning/bootstrap.sh` trimestralmente.
- Documentar métricas de disponibilidad en SLA-RN-015.
- Monitorear necesidades de escalado horizontal antes de considerar contenedores.
