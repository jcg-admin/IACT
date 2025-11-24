# Resumen de artefactos de reglas y restricciones

## Propósito

Este resumen consolida los artefactos donde se documentan, validan y auditan las restricciones del proyecto. Sirve como punto de entrada para localizar fuentes de verdad antes de aprobar nuevas reglas o revisar su cumplimiento.

## Rutas principales

- **Documentación base**: `docs/backend/requisitos/restricciones_y_lineamientos.md` y `docs/frontend/requisitos/reglas_negocio/restricciones.md` definen las restricciones maestras por dominio.
- **Checklists y plantillas**: `docs/gobernanza/qa/checklist_auditoria_restricciones.md` y `docs/gobernanza/templates/RN-restriccion-template.md` estandarizan cómo se evidencian las validaciones.
- **Guías de guiones**: `docs/gobernanza/guias/scripts/validate_critical_restrictions.md` describe el alcance del script crítico de validación.
- **Automatizaciones CI**: `scripts/ci/gate-restrictions.sh` bloquea merges si fallan validaciones de restricciones.
- **Validadores centrales**: `scripts/validate_critical_restrictions.sh` ejecuta chequeos sobre uso de email, Sentry, sesiones y otros riesgos críticos.
- **Agentes de código**: `scripts/coding/ai/agents/validation/restrictions_gate.py` replica las verificaciones para revisiones asistidas por IA.
- **QA de infraestructura**: `docs/infraestructura/qa/testing/comandos_validacion.md` registra cómo invocar los comandos de control en ambientes.

## Cómo usar este resumen

1. Revisar la documentación base antes de introducir nuevas restricciones o excepciones.
2. Ejecutar los scripts de validación (`scripts/validate_critical_restrictions.sh` y `scripts/ci/gate-restrictions.sh`) antes de abrir PRs.
3. Registrar la evidencia en las plantillas de QA y checklists de gobernanza.
4. Sincronizar cualquier cambio en restricciones críticas con los agentes/validadores en `scripts/coding/ai/`.
