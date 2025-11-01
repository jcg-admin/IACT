---
id: DOC-QA-001
estado: borrador
propietario: lider-qa
ultima_actualizacion: 2025-02-18
relacionados: ["TC-USR-010", "QA-LOG-20250216"]
---
# Estrategia de QA

Hoja de ruta para garantizar calidad del software mediante TDD, métricas de cobertura y coordinación transversal con equipos de producto, arquitectura y DevOps.

## Página padre
- [`readme.md`](readme.md)

## Línea base de QA
- Consolidar suite `pytest` con cobertura mínima de 80 %.
- Registrar TC-USR-010 y TC-ADM-005 en `tests/` por aplicación Django.
- Documentar criterios de salida para despliegues APScheduler y reportes.
- Mantener bitácora de ejecuciones en `registros/`.

## Métricas esperadas
| Métrica | Objetivo | Fuente |
| --- | --- | --- |
| Cobertura unitaria | ≥ 80 % | Reportes de `pytest --cov`.
| Tiempo medio para corregir fallos críticos | ≤ 2 días | Bitácora en `registros/`.
| Cumplimiento de checklists QA | 100 % por release | [`../checklists/checklist_testing.md`](../checklists/checklist_testing.md).

## Acciones prioritarias
- [ ] Generar reporte inicial de cobertura y publicarlo en `registros/`.
- [ ] Completar registro de criterios de salida y enlazarlo con Planificación y DevOps.
- [ ] Configurar automatización de tests en la canalización CI.
