---
id: HAMILTON-FRAMEWORK-INTEGRACION-SDLC
tipo: guia
categoria: ai
version: 1.0.0
fecha_creacion: 2025-11-18
fecha_actualizacion: 2025-11-18
propietario: docs-agent
relacionados: ["FASES_IMPLEMENTACION_IA.md", "SDLC_AGENTS_GUIDE.md", "AI_CAPABILITIES.md", "TASK-024-ai-telemetry-system.md"]
---

# HAMILTON FRAMEWORK + 6 FASES SDLC IA

Guía técnica para incorporar Hamilton en el flujo SDLC asistido por IA del proyecto IACT, alineando la presentación "Hamilton Framework - Presentación Completa" con la metodología de seis fases descrita en `FASES_IMPLEMENTACION_IA.md`.

---

## 0. Executive Summary

- **Propósito**: consolidar cómo Hamilton (micro-orquestación declarativa) refuerza cada fase del SDLC IA, habilitando trazabilidad, modularidad y pruebas automatizadas.
- **Resultado esperado**: disponer de un plan accionable para que los agentes SDLC (ver `SDLC_AGENTS_GUIDE.md`) evalúen, diseñen, implementen y midan integraciones Hamilton.
- **Pruebas obligatorias**: `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` protege la publicación y referenciación de esta guía.

---

## 1. Hamilton en contexto IACT

| Aspecto | Contenido de la presentación | Adaptación IACT |
|---------|------------------------------|-----------------|
| Paradigma | Micro-orquestación declarativa mediante funciones con salidas = nombre de función e inputs = argumentos. | Mapear dataflows de agentes SDLC y pipelines IA, manteniendo la lógica dentro de módulos versionados en Git. |
| Beneficios clave | Testing, modularidad, reutilización, documentación automática y visualización de DAGs. | Cumple restricciones de gobierno IA: trazabilidad (`FASES_IMPLEMENTACION_IA.md` Fase 2) y small batches (`FASES_IMPLEMENTACION_IA.md` Fase 4). |
| Integraciones | Compatible con Ray, Dask, Spark, FastAPI, Flask, Jupyter. | Permite ejecutar en infraestructura existente (scripts/ci, pipelines manuales) sin introducir servicios prohibidos. |
| Casos GenAI/LLM | Control de prompts, RAG, evaluación con LLMs. | Conecta con agentes SDLC especializados (Design, Testing, Deployment) y guías de prompting (`ai_capabilities/prompting/`). |

---

## 2. Mapeo de las 6 fases SDLC IA

Cada subsección resume objetivos, acciones Hamilton y validaciones alineadas con `FASES_IMPLEMENTACION_IA.md`.

### Fase 1 — Evaluación Inicial y Diagnóstico Técnico

- **Objetivo**: medir madurez técnica antes de introducir Hamilton.
- **Acciones Hamilton**:
  - Inventariar dataflows candidatos: prompts, pipelines ETL, validadores (`scripts/validation/`).
  - Identificar servicios aptos para micro-orquestación (por ejemplo, generación de prompts en `docs/ai_capabilities/prompting/`).
  - Usar `tryhamilton.dev` para prototipos rápidos, documentando hallazgos en un archivo temporal dentro de `docs/analisis/rev/` antes de consolidar.
- **Artefactos**: checklist de dataflows + mapa de dependencias LLM/Hamilton enlazado al ExecPlan activo.
- **Métricas**: cobertura de pipelines auditados ≥ 80 %, compatibilidad con políticas `AI_CAPABILITIES.md`.

### Fase 2 — Estrategia y Gobierno Técnico de IA

- **Objetivo**: asegurar gobernanza antes del despliegue.
- **Acciones Hamilton**:
  - Definir políticas para funciones declarativas: naming estándar, anotaciones de tipo, uso de `@tag`, `@check_output` y `@config.when`.
  - Registrar decisiones en ADR cuando se introduzcan pipelines críticos (ver `docs/adr/`).
  - Sincronizar ExecPlans con agentes SDLC (`SDLC_AGENTS_GUIDE.md`) para documentar qué modelo LLM respalda cada dataflow Hamilton.
- **Artefactos**: sección adicional en `ESTRATEGIA_IA.md` (cuando aplique) apuntando a este documento.
- **Métricas**: 100 % de funciones Hamilton con docstring y tipo; 100 % de pipelines con versionado Git.

### Fase 3 — Fundamentos Técnicos y de Plataforma

- **Objetivo**: preparar infraestructura reproducible.
- **Acciones Hamilton**:
  - Crear módulos Python bajo `scripts/coding/ai/` o `api/` siguiendo TDD; usar `pip install sf-hamilton` en entornos aislados.
  - Implementar adaptadores Hamilton (`driver.Driver`) que permitan ejecutar pipelines en scripts CLI existentes.
  - Integrar validaciones con `@check_output` y `pandera` (cuando esté habilitado) para cumplir requisitos de calidad de datos.
- **Artefactos**: scripts de bootstrap (`scripts/ci/` o `scripts/validation/`) que llamen a pipelines Hamilton.
- **Métricas**: suites `pytest` con coverage ≥ 80 % y pipelines reproducibles en ambientes locales (sin dependencia de servicios prohibidos).

### Fase 4 — Despliegue Progresivo y Trabajo en Pequeños Lotes

- **Objetivo**: liberar incrementos controlados.
- **Acciones Hamilton**:
  - Usar micro-orquestación para aislar funciones; habilitar `@parameterize` para iterar prompts.
  - Ejecutar despliegues piloto en entornos controlados (ej. `scripts/run_all_tests.sh` + pipelines manuales) antes de ampliar cobertura.
  - Documentar warm starts y reemplazos en ExecPlans y en la sección `[PLANIFICADO]` del índice.
- **Artefactos**: registro de despliegues en `docs/qa/registros/` cuando se active Hamilton en producción.
- **Métricas**: lead time <= baseline + 10 %, zero change failure rate atribuible a Hamilton.

### Fase 5 — Medición, Validación y Mejora Continua

- **Objetivo**: medir impacto y calidad.
- **Acciones Hamilton**:
  - Incluir pruebas unitarias e integración (LLM evals) que se puedan ejecutar en CI.
  - Visualizar DAGs con `dr.visualize_execution(...)` y anexar capturas a documentación técnica.
  - Integrar métricas de costo LLM y tiempos de ejecución en `logs_data/` para seguimiento de DORA metrics.
- **Artefactos**: reportes periódicos en `logs_data/analysis/` o `docs/analisis/` con hallazgos.
- **Métricas**: cobertura de pruebas Hamilton ≥ 80 %, reducción de tiempo de depuración (MTTR) medido vía `logs_data`.

### Fase 6 — Escalamiento Técnico y Consolidación

- **Objetivo**: institucionalizar Hamilton como parte del stack.
- **Acciones Hamilton**:
  - Migrar flujos manuales a pipelines Hamilton versionados; compartir componentes reutilizables en `hub.dagworks.io` cuando sean open-source friendly.
  - Entrenar equipo usando esta guía + presentación original; registrar sesiones de conocimiento en `docs/ai/tareas/`.
  - Evaluar integración con `DAGWorks` para observabilidad avanzada y versionamiento.
- **Artefactos**: backlog de mejoras en `proyecto/TAREAS_ACTIVAS.md` y roadmap asociado.
- **Métricas**: adopción Hamilton en ≥ 3 dominios (api, scripts, docs) y monitoreo en `AI_CAPABILITIES.md` actualizado.

---

## 3. Flujo operativo recomendado

1. **Planificación**: crear o actualizar un ExecPlan (por ejemplo `docs/EXECPLAN_hamilton_framework_sdlc_integration.md`).
2. **Diseño de dataflow**: definir funciones Hamilton con dependencias claras.
3. **Implementación TDD**: escribir pruebas primero (`pytest`), luego código Hamilton.
4. **Validación**: ejecutar `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` y pruebas específicas del dominio.
5. **Documentación**: actualizar `docs/index.md`, guías de agentes SDLC y registros de QA.
6. **Revisión**: registrar métricas y decisiones en ExecPlans/ADRs.

---

## 4. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Falta de gobernanza sobre funciones generadas por IA | Requerir `@tag(owner=...)` y docstrings; auditar commits con metadata IA (Fase 2). |
| Costos de LLM altos por evaluaciones | Segmentar pruebas (desarrollo vs pre-release) como sugiere la presentación, documentando costos en `AI_CAPABILITIES.md`. |
| Integraciones mal instrumentadas | Mantener `scripts/run_all_tests.sh` actualizado y anexar nuevos comandos Hamilton. |
| Debt técnico en prompts | Usar Hamilton para versionar prompts como funciones; cubrir con pruebas y registros en `docs/ai_capabilities/prompting/`. |

---

## 5. Validación y pruebas

- **Obligatorio**: `python3 -m pytest docs/qa/testing/test_documentation_alignment.py` (garantiza existencia de esta guía y referenciación en el índice).
- **Recomendado**: pruebas específicas por dominio (ej. `pytest scripts/coding/tests/` para pipelines en scripts) y visualización de DAGs.
- **Documentación cruzada**: verificar que `docs/ai/SDLC_AGENTS_GUIDE.md` y `docs/index.md` enlacen a esta guía tras cada modificación.

---

## 6. Próximos pasos

1. Incorporar ejemplos de código Hamilton en `scripts/coding/ai/` siguiendo TDD.
2. Evaluar integración con `TASK-024-ai-telemetry-system.md` para recolectar métricas de ejecución.
3. Registrar aprendizajes en `docs/qa/registros/` una vez ejecutados pilotos.

---

**Última actualización**: 2025-11-18  
**Contacto**: Equipo de documentación SDLC (docs-agent)
