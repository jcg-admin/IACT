# B5 — Migración de datos heredados a RTM-IACT

## Objetivo
Ejecutar la migración de matrices heredadas hacia `docs/trazabilidad/RTM.md`, limpiando datos y marcando matrices corruptas para completar la fase documental.

## Alcance
- Inventariar matrices de trazabilidad existentes y clasificarlas por criticidad (CRIT/MAJ/MIN).
- Ejecutar la ETL con `scripts/trazabilidad/etl_rtm.py` para normalizar IDs, detectar duplicados/huérfanos y marcar huecos con `PENDING`.
- Importar el resultado limpio en `RTM.md` y validar con `validar_rtm.py`, generando reportes de seguimiento.

## Entradas
- RTM estructurada publicada en la subtarea B3.
- Scripts de ETL y validación mencionados en el plan (`etl_rtm.py`, `validar_rtm.py`).
- Matrices heredadas ubicadas en `docs/gobernanza/trazabilidad/`.

## Salidas esperadas
- RTM-IACT poblada con datos normalizados y sin referencias huérfanas.
- Reportes de ETL/validación almacenados en `docs/trazabilidad/registros/`.
- Trazas de dependencias hacia backlog B3 y controles de cobertura (`coverage_rtm.py`).

## Criterios de done
- Importación completada con cero duplicados y huecos marcados explícitamente.
- `validar_rtm.py` y muestreo manual validan al menos 10% de entradas críticas.
- Se archivan las matrices antiguas como deprecated tras la carga.
