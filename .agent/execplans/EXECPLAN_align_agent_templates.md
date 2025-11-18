# Homologar fichas de agentes con etiquetas Goals/Limitations/WhatToAdd/Steps

Este ExecPlan es un documento vivo y sigue `/.agent/PLANS.md`. Su objetivo es normalizar todas las fichas `.github/agents/*.agent.md` con la envoltura etiquetada (`<Goals>`, `<Limitations>`, `<WhatToAdd>` con sub-secciones y `<StepsToFollow>`) para que coincidan con el formato requerido por los lineamientos recientes.

## Purpose / Big Picture

Los agentes Copilot sólo interpretan correctamente las instrucciones si comparten una estructura uniforme. Hoy cada ficha usa encabezados (`## Propósito`, `## Procedimiento`, etc.), lo que contradice el requerimiento explícito del catálogo (`AGENTS_IMPLEMENTATION_MAP.md`). Tras completar este plan, cualquier ficha tendrá las etiquetas HTML solicitadas y conservará su información original (propósito, responsabilidades, pasos y validaciones) redistribuida bajo las nuevas etiquetas. Esto elimina rechazos de PR por instrucciones incompletas.

## Progress

- [x] (2025-02-15 17:10Z) Inventariar `.github/agents/*.agent.md` y confirmar que todas comparten secciones `Propósito/Responsabilidades/Procedimiento/Validación` excepto `my-agent` (tiene front matter YAML).
- [x] (2025-02-15 17:20Z) Diseñar conversión automática: extraer cada sección, transformarla en listas y envolverla en las etiquetas nuevas; definir limitaciones estándar para todos los agentes para evitar rutas frágiles.
- [x] (2025-02-15 17:30Z) Ejecutar script Python (`Path.glob('*.agent.md')`) que reemplaza contenido respetando UTF-8 y normalizando finales CRLF→LF.
- [x] (2025-02-15 17:45Z) Revisar muestras (ApiAgent, AutomationCoherenceAnalyzer, ReleaseAgent) para verificar que conservan propósito, responsabilidades, pasos y validaciones dentro de las etiquetas.
- [x] (2025-02-15 17:55Z) Manejar `my-agent` manualmente: reinsertar front matter, redactar el contenido bajo las etiquetas y preservar capacidades/uso/validaciones.
- [x] (2025-02-15 18:00Z) Registrar este ExecPlan y preparar commit `docs(agents): add tagged structure to fiches`.

## Surprises & Discoveries

- Observación: el script inicial no extrajo secciones porque los archivos usaban finales `\r\n`. Evidencia: tras la primera ejecución las fichas quedaron con texto genérico.
  Evidencia: `sed` mostró sólo las líneas de fallback en ApiAgent.
- Observación: `my-agent` contiene front matter YAML, por lo que la heurística `splitlines()[0]` devolvió `---`. Se optó por excluirlo del script y reescribirlo manualmente.

## Decision Log

- Decisión: definir un bloque `<Limitations>` uniforme para todos los agentes que refuerce alcance, documentación sin rutas y cumplimiento TDD.
  Racional: evita duplicar lógica específica y cumple el requerimiento de no referenciar archivos.
  Fecha/Autor: 2025-02-15 / gpt-5-codex.
- Decisión: convertir `## Procedimiento Recomendado` tanto en `<BuildInstructions>` (pasos en bullets "Paso N") como en `<StepsToFollow>` (enumeración original) para que el agente lector tenga referencias en ambos apartados.
  Racional: mantiene fidelidad al contenido original y respeta la semántica de la plantilla.
  Fecha/Autor: 2025-02-15 / gpt-5-codex.

## Outcomes & Retrospective

Todas las fichas quedaron envueltas con etiquetas uniformes sin rutas específicas. El script reutilizable permite futuras migraciones, y `my-agent` conserva metadatos YAML. Pendiente: si se agregan nuevas fichas, deben utilizar el mismo template desde su creación para evitar migraciones posteriores.

## Context and Orientation

- Catálogo de fichas: `.github/agents/*.agent.md` (65 archivos). Cada ficha compartía secciones `## Propósito`, `## Responsabilidades Clave`, `## Procedimiento Recomendado`, `## Validación`.
- Requerimiento: `.github/agents/AGENTS_IMPLEMENTATION_MAP.md` establece que “estas fichas siguen la estructura Goals → Limitations → WhatToAdd → Steps”. El incumplimiento provocó el reclamo del usuario.
- Particularidad: `.github/agents/my-agent.agent.md` contiene front matter YAML y describe CodeTasker con secciones personalizadas (`## Capacidades`, `## Cómo usarlo`).

## Plan of Work

1. Normalizar finales de línea y parsear secciones mediante regex. El script debe:
   - Abrir cada fichero (`Path('.github/agents').glob('*.agent.md')`).
   - Reemplazar `\r\n` con `\n` para simplificar los patrones.
   - Extraer bloques `Propósito`, `Responsabilidades Clave`, `Procedimiento Recomendado`, `Validación` usando `re.search`.
   - Convertir cada bloque en listas (prefijo `-` o enumeraciones) conservando el texto.
2. Construir plantilla nueva:
   - `<Goals>` recibe el texto del propósito.
   - `<Limitations>` incluye tres bullets estándar (alcance, documentación sin rutas, cumplimiento de políticas).
   - `<WhatToAdd>/<HighLevelDetails>` recibe responsabilidades.
   - `<BuildInstructions>` recibe los pasos (prefijo “Paso N”).
   - `<ProjectLayout>` añade recordatorios genéricos (“Opera sobre artefactos del dominio”, “Coordina hallazgos…”).
   - `<StepsToFollow>` replica la lista numerada original.
   - `<Validation>` preserva la lista de validaciones y cualquier párrafo final.
3. Ejecutar script, revisar manualmente varias fichas y corregir `my-agent` (ya que su estructura difiere) introduciendo manualmente la plantilla tras el front matter.
4. Ejecutar `git status` para asegurar que no se incluyan otros archivos ajenos y preparar commit.

## Concrete Steps

- Ejecutar script desde la raíz:

        python scripts/tmp/convert_agents.py  # (el script se ejecutó inline con `python - <<'PY'` y realiza los pasos descritos)

- Verificar muestras:

        sed -n '1,200p' .github/agents/api-agent.agent.md
        sed -n '1,200p' .github/agents/automation-coherence-analyzer-agent.agent.md
        sed -n '1,200p' .github/agents/release-agent.agent.md

- Reescribir manualmente `my-agent` manteniendo front matter y añadiendo la plantilla.
- Validar estado:

        git status -sb

## Validation and Acceptance

- Revisar manualmente que cada ficha contenga las etiquetas `<Goals>`, `<Limitations>`, `<WhatToAdd>` (con sub-secciones), `<StepsToFollow>` y `<Validation>`.
- Confirmar que el contenido original (propósito, responsabilidades, pasos, validaciones) está presente bajo las etiquetas correctas en un subconjunto significativo (al menos uno por dominio: SDLC, automatización, calidad, documentación, proveedores LLM).
- Asegurarse de que `my-agent` conserva front matter y añade la nueva estructura sin rutas específicas.
- No se requieren pruebas automatizadas; el cambio es documental.

## Idempotence and Recovery

- El script puede volver a ejecutarse porque siempre recalcula el contenido desde las secciones originales. En caso de error, `git checkout HEAD -- .github/agents/*.agent.md` restaura el estado previo.
- Para fichas nuevas, basta copiar una existente como plantilla para evitar futuras migraciones.

## Artifacts and Notes

- Script inline ejecutado:

        python - <<'PY'
        import re
        from pathlib import Path
        # ... (ver historial del commit docs(agents): add tagged structure to fiches)
        PY

- Edición manual `my-agent`: archivo contiene front matter YAML seguido de la estructura etiquetada solicitada.

## Interfaces and Dependencies

- Sólo depende de la biblioteca estándar de Python 3.11 (`pathlib`, `re`).
- No interactúa con servicios externos.
- Los agentes Copilot leerán directamente estos archivos desde `.github/agents/` a través de `.github/copilot/agents.json`, por lo que mantener la plantilla uniforme es crítico.
