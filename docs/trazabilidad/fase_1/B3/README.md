# B3 — Publicación de la matriz RTM-IACT

## Objetivo
Crear y publicar la matriz oficial `RTM-IACT.md` con los campos completos que soportan trazabilidad bidireccional desde RN/RF/BR hacia UC/UML y descendiendo a Código/API/Tests/Evidencia.

## Alcance
- Definir la estructura base de la RTM conforme al plan y al PROC-IACT-TRZ v1.1.
- Incorporar campos para `trazabilidad_upward` y `trazabilidad_downward`, asegurando que no existan celdas vacías.
- Preparar la matriz para recibir los datos limpios de la ETL (subtarea B5) y marcar huecos con `PENDING` cuando corresponda.

## Entradas
- Indicaciones de la fase 10.2 y backlog (B3 y B5) para RTM-IACT.
- Resultados preliminares de inventario de matrices heredadas.

## Salidas esperadas
- Archivo `docs/trazabilidad/RTM.md` inicializado con los campos y cabeceras requeridos.
- Lineamientos de actualización para PRs y para los jobs de validación (`rtm-drift-check`, `coverage_rtm.py`).

## Criterios de done
- La RTM publicada no tiene campos vacíos estructurales y permite enlaces bidireccionales.
- Se documenta la relación con los controles CI/CD y el backlog de migración (B5).
- Se incluyen notas para mantener IDs consistentes y evitar artefactos huérfanos.
