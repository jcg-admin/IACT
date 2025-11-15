---
name: SyncReporterAgent
description: Consolida la ejecución del pipeline de sincronización en un reporte Markdown con métricas y recomendaciones.
---

# Documentation Sync Reporter Agent

`SyncReporterAgent` (`scripts/coding/ai/documentation/sync_agent.py`) cierra el pipeline de sincronización generando un reporte ejecutivo con métricas, acciones realizadas e inconsistencias detectadas. Puede guardar el reporte automáticamente en `docs/anexos` o trabajar en modo in-memory.

## Capacidades

- Recibe resultados de Planner, Editor y Verifier y los integra en un resumen legible.
- Genera encabezado YAML con metadatos (`id`, `tipo`, `fecha`) para facilitar versionado.
- Incluye estadísticas clave: componentes analizados, documentación creada/actualizada, inconsistencias pendientes.
- Detalla acciones ejecutadas (creaciones, actualizaciones) y recomendaciones futuras.
- Permite habilitar/deshabilitar persistencia mediante `save_report`.

## Entradas y Salidas

- **Entradas**
  - Diccionario con resultados de agentes anteriores (`inspection_plan`, `stats`, `created_docs`, `updated_docs`, `verification_result`, etc.).
  - Configuración (`project_root`, `save_report`).
- **Salidas**
  - `report_markdown`: reporte en texto Markdown.
  - Opcional `report_path` cuando se guarda en disco.
  - Marca temporal (`timestamp`).

## Uso

```python
from scripts.coding.ai.documentation.sync_agent import SyncReporterAgent

reporter = SyncReporterAgent({"project_root": Path.cwd(), "save_report": True})
report = reporter.run({
    "inspection_plan": plan,
    "created_docs": created,
    "updated_docs": updated,
    "verification_passed": verifier_result["verification_passed"],
    "inconsistencies": verifier_result["inconsistencies"]
})
print(report["report_markdown"][:200])
```

## Validaciones Relacionadas

- Verificar permisos de escritura en `docs/anexos` cuando `save_report=True`.
- Versionar el reporte dentro de la documentación o adjuntarlo a PRs de sincronización para auditoría.
