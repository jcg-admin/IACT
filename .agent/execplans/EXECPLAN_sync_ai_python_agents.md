# Documentar agentes Python en scripts/coding/ai

Esta ExecPlan es un documento vivo. Actualiza las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` a medida que avances. Debe cumplirse lo indicado en `.agent/PLANS.md`.

## Purpose / Big Picture

Exponer en GitHub Copilot todos los agentes implementados bajo `scripts/coding/ai/` creando fichas `.agent.md` consistentes en `.github/agents/` y registrándolos en `.github/copilot/agents.json`. Esto permitirá invocar desde Copilot los agentes Python reales (Business Analysis, Documentation Sync, Quality, Shared utilities, etc.) con instrucciones precisas.

## Progress

- [x] (2025-02-15 01:00Z) Auditar `scripts/coding/ai/` para listar clases que heredan de `Agent` o terminan en `Agent`.
- [x] (2025-02-15 02:05Z) Crear fichas en `.github/agents/` para los agentes que aún no tienen documentación Copilot.
- [x] (2025-02-15 02:20Z) Actualizar `.github/copilot/agents.json` agregando las nuevas entradas con su descripción corta.
- [x] (2025-02-15 02:25Z) Ejecutar validaciones (formato JSON + existencia de rutas) y documentar retrospectiva.

## Surprises & Discoveries

- La automatización detectó 23 agentes faltantes (techniques, documentation sync, generators, quality, shared, permissions y SDLC). No fue necesario modificar código Python, solo documentación y configuración.

## Decision Log

- (2025-02-15) Usar convención `<dominio>-<nombre>-agent.agent.md` para las nuevas fichas, tomando el dominio desde la ruta (`documentation`, `business-analysis`, `quality`, etc.). Autor: gpt-5-codex.
- (2025-02-15) Ordenar alfabéticamente `agents.json` después de insertar nuevas entradas para mantener consistencia con futuras automatizaciones. Autor: gpt-5-codex.

## Outcomes & Retrospective

- (2025-02-15 02:25Z) Se añadieron 23 fichas nuevas y Copilot expone ahora 65 agentes (42 existentes + 23 nuevos) cubriendo la implementación Python real. Las validaciones de JSON y paths pasaron sin errores.

## Context and Orientation

- `.github/agents/` ya contiene 42 fichas migradas desde `.agent/agents/`.
- `.github/copilot/agents.json` publica ahora 65 agentes incluyendo los componentes de `scripts/coding/ai/`.
- `scripts/coding/ai/shared/agent_base.py` define la clase `Agent` usada por los agentes especializados.
- `scripts/coding/ai/documentation/sync_agent.py`, `business_analysis/generator.py`, `quality/*.py` y `shared/*.py` contienen agentes no documentados en Copilot.

## Plan of Work

1. Generar listado definitivo de agentes a documentar (clases que heredan de `Agent` o terminan en `Agent`), excluyendo bases internas (`Agent`, `SDLCAgent`, etc.) si ya cuentan con ficha.
2. Para cada agente sin ficha existente:
   - Derivar nombre kebab-case `<dominio>-<nombre>-agent`.
   - Crear archivo `.github/agents/<dominio>-<nombre>-agent.agent.md` con secciones: descripción general, responsabilidades, entradas/salidas, modo de uso y validaciones relacionadas.
3. Actualizar `AGENTS_IMPLEMENTATION_MAP.md` si es necesario para reflejar nuevas fichas.
4. Añadir entradas en `.github/copilot/agents.json` con `name`, `description`, `instructions` (ruta al nuevo markdown) y `tags` acordes.
5. Ejecutar validaciones:
   - `python3 -m json.tool .github/copilot/agents.json`.
   - Script que verifique existencia de cada `instructions`.
6. Completar esta ExecPlan con progreso final y retrospectiva.

## Concrete Steps

1. Usar script Python para listar agentes faltantes y confirmar nombres.
2. Crear fichas Markdown manualmente asegurando consistencia con fichas existentes.
3. Editar `agents.json` añadiendo las entradas nuevas manteniendo orden alfabético por `name`.
4. Ejecutar validaciones y actualizar secciones de la ExecPlan.

## Validation and Acceptance

- JSON válido (`python3 -m json.tool`).
- Todas las rutas referenciadas en `instructions` existen.
- ExecPlan actualizado con progreso completado y retrospectiva.

## Idempotence and Recovery

- Las fichas pueden recrearse sobrescribiendo archivos si hay errores.
- Cambios en `agents.json` pueden revertirse con `git checkout --` y rehacerse.

## Artifacts and Notes

- Script de auditoría de agentes: `python - <<'PY' ...` (ver historial de shell) permitió identificar clases que heredan de `Agent`.

## Interfaces and Dependencies

- Herramientas disponibles: `python3`, `jq`, utilidades básicas de shell.
- No se añaden dependencias nuevas.
