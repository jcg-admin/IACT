# Reubicar fichas de agentes Copilot a .github/agents

Esta ExecPlan es un documento vivo. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse actualizadas conforme avancemos. Debe seguirse al pie de la letra lo descrito en `.agent/PLANS.md`.

## Purpose / Big Picture

Queremos que GitHub Copilot consuma las fichas de agentes directamente desde `.github/agents/`, usando un formato consistente `<nombre>-agent.agent.md`. Con esto, las definiciones que Copilot expone estarán alineadas con la documentación humana y será sencillo ubicar cada agente sin navegar directorios paralelos.

## Progress

- [x] (2025-02-15 00:00Z) Analizado el estado actual: fichas principales viven en `.agent/agents/*.md` y Copilot las referencia.
- [x] (2025-02-15 00:20Z) Generar nuevas fichas en `.github/agents/` con convención kebab-case y sufijo `.agent.md`.
- [x] (2025-02-15 00:25Z) Actualizar `.github/copilot/agents.json` para apuntar a las nuevas rutas.
- [x] (2025-02-15 00:30Z) Ajustar documentación principal para indicar la nueva ubicación canónica consumida por Copilot.
- [x] (2025-02-15 00:40Z) Validar que el JSON sea válido y que las rutas referenciadas existan.
- [x] (2025-02-15 00:45Z) Registrar retrospectiva final con los resultados obtenidos.

## Surprises & Discoveries

- Aún no se identifican sorpresas; actualizar si aparecen durante la implementación.

## Decision Log

- (2025-02-15) Mantener las fichas originales en `.agent/agents/` para no romper documentación ni automatizaciones previas, pero crear copias en `.github/agents/` para Copilot. Autor: gpt-5-codex.

## Outcomes & Retrospective

- (2025-02-15 00:45Z) Copilot ahora referencia 42 fichas en `.github/agents/` con formato unificado y las validaciones confirmaron que todas las rutas existen. La documentación raíz señala la nueva ubicación para evitar confusiones.

## Context and Orientation

- `.agent/agents/` contiene 42 fichas Markdown (excluyendo el README) usadas hasta hoy para instruir agentes.
- `.github/agents/` ya aloja algunas fichas (`*_agent.md`) y documentación complementaria.
- `.github/copilot/agents.json` expone los agentes disponibles en Copilot y ahora todas las entradas apuntan a `.github/agents/`.
- `AGENTS.md` en la raíz explica la existencia del catálogo histórico; ya incluye una nota sobre la nueva ubicación consumida por Copilot para evitar confusiones.

## Plan of Work

1. Enumerar todas las fichas dentro de `.agent/agents/` ignorando el README.
2. Para cada una, construir el nombre de destino aplicando:
   - Reemplazar `_` por `-`.
   - Conservar el sufijo original (si ya termina en `_agent` quedará `-agent` tras la conversión; si no, no añadimos sufijo extra).
   - Agregar extensión `.agent.md`.
3. Copiar el contenido original a `.github/agents/<nombre-kebab>.agent.md`. Si ya existía una ficha previa (`my_agent.md`), sobrescribirla para mantener un único formato.
4. Actualizar `.github/copilot/agents.json` cambiando cada campo `instructions` para que apunte a `.github/agents/<nombre-kebab>.agent.md`.
5. Editar `AGENTS.md` en la raíz para aclarar que Copilot lee ahora las fichas de `.github/agents/`, preservando la referencia histórica a `.agent/agents/` para documentación extendida.
6. Ejecutar validaciones:
   - Formatear el JSON con `python3 -m json.tool`.
   - Verificar que todas las rutas declaradas en `instructions` existan.
7. Actualizar esta ExecPlan (Progress, posibles sorpresas, decisiones adicionales, retrospectiva) y preparar el commit.

## Concrete Steps

1. Desde la raíz del repo, ejecutar un script Python que realice la copia con la convención nueva.
2. Editar el JSON con la misma sesión (puede usarse `jq` o edición manual seguida de formateo).
3. Modificar `AGENTS.md` con la nota aclaratoria.
4. Correr los comandos de validación.

## Validation and Acceptance

- `python3 -m json.tool .github/copilot/agents.json` debe devolver un JSON formateado sin errores.
- Un script que itere `jq -r '.agents[].instructions'` debe confirmar que cada ruta existe bajo `.github/agents/`.
- Las secciones `Progress` y `Outcomes & Retrospective` actualizadas evidenciarán la finalización.

## Idempotence and Recovery

- El script de copia puede ejecutarse múltiples veces; al sobrescribir asegura convergencia.
- Si una edición manual falla, se puede restablecer usando `git checkout -- <archivo>` y repetir el paso.

## Artifacts and Notes

- Registrar en esta sección cualquier listado de rutas generado o salidas relevantes si aportan contexto adicional.

## Interfaces and Dependencies

- Depende de `python3`, `jq` y utilidades básicas de shell disponibles en el contenedor.
- No introduce dependencias nuevas ni modifica código ejecutable, únicamente documentación y configuración Copilot.
