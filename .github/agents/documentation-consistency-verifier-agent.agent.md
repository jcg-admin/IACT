---
name: ConsistencyVerifierAgent
description: Evalúa la consistencia entre componentes descubiertos y documentación creada o existente.
---

# Documentation Consistency Verifier Agent

`ConsistencyVerifierAgent` (`scripts/coding/ai/documentation/sync_agent.py`) actúa como fase Verifier del pipeline de sincronización. Analiza los componentes detectados por `CodeInspectorAgent`, los documentos creados por `DocumentationEditorAgent` y la documentación histórica para detectar brechas y emitir recomendaciones.

## Capacidades

- Valida la presencia de `discovered_components` antes de iniciar el análisis.
- Compara conteos de componentes por dominio con los documentos existentes y recién creados.
- Clasifica inconsistencias por severidad (`high`, `medium`, `low`) y genera mensajes detallados.
- Produce recomendaciones accionables para cerrar brechas de documentación.
- Resumen de métricas en `stats` (totales y severidades).

## Entradas y Salidas

- **Entradas**
  - `discovered_components`: estructura generada por `CodeInspectorAgent`.
  - `created_docs`: resultado de `DocumentationEditorAgent` (opcional).
  - `existing_docs`: snapshot de documentación previa.
- **Salidas**
  - `verification_passed`: bandera booleana.
  - `inconsistencies`: lista de hallazgos con dominio, mensaje y severidad.
  - `recommendations`: acciones sugeridas.
  - `stats`: métricas de severidad y conteos.

## Uso

```python
from scripts.coding.ai.documentation.sync_agent import ConsistencyVerifierAgent

verifier = ConsistencyVerifierAgent()
result = verifier.run({
    "discovered_components": discovered,
    "created_docs": created,
    "existing_docs": existing_docs
})
print(result["verification_passed"], result["recommendations"])
```

## Validaciones Relacionadas

- Consumir su salida antes de generar reportes finales con `SyncReporterAgent`.
- Incorporar reglas adicionales según necesidades del dominio extendiendo el método `run` o agregando análisis por dominio.
