# Automatización SDLC (ubicación actualizada)

Esta carpeta conserva stubs de compatibilidad. Los scripts de automatización de gobernanza SDLC se movieron a `scripts/gobernanza_sdlc/automation/` para reflejar la nueva nomenclatura sin referencias a agentes.

Ejecute los scripts desde la nueva ruta, por ejemplo:

```
python scripts/gobernanza_sdlc/automation/schema_validator_agent.py --help
```

Los archivos aquí importan el código real desde la nueva ubicación para mantener compatibilidad temporal. Esta sustitución explica la reducción de líneas en los antiguos módulos: el código completo sigue vivo en `scripts/gobernanza_sdlc/automation/`.
