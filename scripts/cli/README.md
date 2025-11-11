# CLI Scripts

Command-Line Interface scripts de alto nivel para operaciones del proyecto.

## Scripts

- `sdlc_agent.py` - CLI principal para agentes SDLC
- `dora_metrics.py` - Generación de métricas DORA
- `sync_documentation.py` - Sincronización de documentación

## Uso

```bash
# SDLC Agent
python scripts/cli/sdlc_agent.py --phase planning --input "Feature request..."

# DORA Metrics
python scripts/cli/dora_metrics.py --calculate

# Sync Documentation
python scripts/cli/sync_documentation.py
```
