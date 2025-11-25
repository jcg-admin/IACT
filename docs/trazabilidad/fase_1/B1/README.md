# B1 — Publicación de TRZ-001 y política base de trazabilidad

## Objetivo
Establecer la guía normativa inicial (TRZ-001) para trazabilidad SDLC, dejando publicada la política que habilita el resto de tareas de la fase 1.

## Alcance
- Consolidar los lineamientos del plan oficial en un documento TRZ-001 dentro de `docs/trazabilidad/`.
- Alinear la política con la cadena obligatoria RN→RF→UC→UML definida en el plan y con los requisitos de completitud por fase.
- Referenciar las reglas de gobernanza vigentes y los controles CI/CD previstos (lint de trazabilidad y validaciones de RTM).

## Entradas
- Plan de remediación y PROC-IACT-TRZ v1.1.
- Reglas de gobernanza en `docs/gobernanza/` y lineamientos de trazabilidad.

## Salidas esperadas
- Documento TRZ-001 publicado y versionado en `docs/trazabilidad/`.
- Notas de enlace hacia RTM-IACT, plantillas v2 y backlog de la fase 1.

## Criterios de done
- TRZ-001 describe explícitamente la cadena RN→RF→UC→UML y los campos upward/downward obligatorios.
- La política menciona los controles CI/CD aplicables (p. ej., `lint-trazabilidad`, `rtm-drift-check`).
- Se registra la relación con el backlog B1–B4 y las dependencias con las siguientes subtareas.
