# Convenciones y Lecciones Aprendidas - Agentes IACT

Esta guía restaura el nivel de detalle esperado para coordinar agentes y documentación. Se alinea con los principios obligatorios de TDD,
commits convencionales y trazabilidad total.

## Organización de Contenido
- Mantén los catálogos maestros (`README.md`, `AGENTS_IMPLEMENTATION_MAP.md`, `META_PROMPTS_LIBRARY.md`) en este directorio.
- Coloca fichas operativas en `.github/agents/<agent>.agent.md` y guías extendidas en `docs/<dominio>/` según corresponda.
- Documenta decisiones estratégicas con ADRs (`docs/adr/`), incluso cuando la lógica resida en scripts.

## Convenciones Específicas
1. **TDD primero**: cada agente o script nuevo debe acompañarse de tests que fallen antes del código. Usa `pytest`, `unittest` o `jest` según el lenguaje.
2. **Cobertura mínima**: apunta a ≥80% en suites relevantes; si la métrica no aplica (p.ej., documentación), justifica explícitamente en la ficha del agente.
3. **Commits**: usa `type(scope): description` (feat/fix/docs/style/refactor/test/chore/perf/ci/build/revert) para cualquier cambio en agentes.
4. **Sin rutas frágiles**: describe ubicaciones de alto nivel y procesos; evita paths absolutos que puedan cambiar.
5. **Principios R1-R5**: idempotencia, sin emojis, verificación, documentación y trazabilidad deben reflejarse en cada guía de agente.

## Lecciones Operativas
- **Cross-check constante**: antes de actualizar un agente, revisa `scripts/coding/ai/` para confirmar si existe implementación Python relacionada.
- **Meta-prompting obligatorio**: cuando definas instrucciones complejas, referencia bloques relevantes en `META_PROMPTS_LIBRARY.md` para reducir alucinaciones.
- **Errores frecuentes**:
  - Omisión de `pre-commit` → pipelines fallan (solución: ejecutar `pre-commit run --all-files`).
  - Migraciones en MariaDB → bloqueo (solución: limitar `python manage.py migrate` a PostgreSQL).
  - Tests sin datos semilla → falsos positivos (solución: usa fixtures y `pytest --reuse-db`).
- **Documenta mitigaciones**: cada vez que un agente requiera workaround (por ejemplo, ampliar memoria para `npm run build`), registra los pasos exactos y el contexto.

## Recomendaciones para Fichas de Agentes
- Mantén secciones de Propósito, Responsabilidades, Procedimiento y Validación; enlaza a metas globales (Goals/Limits/WhatToAdd/Steps) cuando aplique.
- Incluye criterios objetivos de éxito: métricas, checklists o resultados tangibles (logs, reportes, builds verdes).
- Describe dependencias externas (bases de datos, APIs, llaves LLM) en términos generales, indicando cómo preparar el entorno.
- Referencia las técnicas de meta-prompting adecuadas para minimizar alucinaciones.

## Ciclo de Actualización
1. Audita fichas al menos una vez por release o cuando cambien los pipelines.
2. Ejecuta `python3 -m json.tool .github/copilot/agents.json` para validar que las instrucciones referenciadas existan.
3. Sincroniza `AGENTS_IMPLEMENTATION_MAP.md` con nuevos estados de pruebas o cobertura.
4. Registra la fecha de actualización y responsable en los PRs asociados.

Seguir estas convenciones evita regresiones y mantiene alineados a todos los agentes Copilot y scripts auxiliares.
