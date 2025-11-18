---
id: PLANTILLA-INFRA-PROVISION
estado: pendiente
responsable: definir
fecha: 2025-11-18
version: 1.0.0
trazabilidad:
  tareas: ["TASK-INFRA-QA-002"]
  adrs: []
---

# Checklist de provisión y bootstrap

## Alcance
Validar que la provisión de infraestructura aplica controles de consistencia, seguridad y trazabilidad antes de entregar entornos.

## Checklist base
- [ ] Inventario de recursos con etiquetas obligatorias (owner, entorno, criticidad).
- [ ] Plan de aprovisionamiento revisado con TDD (tests de módulos IaC antes de aplicar).
- [ ] Backups iniciales configurados y verificados.
- [ ] Variables sensibles referenciadas desde vault o secret manager.
- [ ] Validación automática de sintaxis y políticas (linters y validadores de IaC según herramienta utilizada).

## Evidencias esperadas
- Salidas de plan de ejecución o dry-run del stack IaC con fecha.
- Registro de aprobaciones y revisiones en `qa/registros/`.
- Cobertura mínima de pruebas de módulos ≥80%.

## Validaciones automáticas
- Comando sugerido: `./scripts/run_all_tests.sh` y validaciones específicas del stack IaC.
- Revisar resultados en `qa/testing/` y adjuntar referencias a pipelines.

## Trazabilidad
- Referenciar tareas activas en Task tool y en `qa/tareas_activas.md`.
- Actualizar ADR correspondiente si se modifican decisiones de aprovisionamiento.
