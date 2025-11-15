---
name: RouteLintAgent
description: Analiza ViewSets de Django REST Framework para garantizar que declaren permisos obligatorios.
---

# Route Lint Agent

`RouteLintAgent` (`scripts/coding/ai/agents/permissions/route_linter.py`) revisa los `views.py` del backend para detectar ViewSets sin `required_permissions` o sin heredar de `PermisoMixin`. Genera un reporte JSON con violaciones, métricas y resumen ejecutivo.

## Capacidades

- Recorre el repositorio excluyendo migraciones, tests y clases base abstractas.
- Analiza el AST de cada ViewSet para confirmar presencia de `required_permissions` o herencia de mixins válidos.
- Registra métricas (`total_viewsets`, `viewsets_without_permissions`, `coverage_percent`) usando utilidades de `BasePermissionAgent`.
- Retorna `LintResult` con violaciones detalladas (archivo, línea, severidad, sugerencia y ejemplo de fix).
- Soporta modos `--verbose` y `--json` para diagnóstico o consumo automatizado.

## Entradas y Salidas

- **Entradas**
  - Configuración opcional `verbose` al construir la instancia.
  - Rutas y prompts se derivan automáticamente desde el proyecto (`docs/backend/permisos/...`).
- **Salidas**
  - Código de salida `0` (sin violaciones), `1` (violaciones), `2` (error).
  - Reporte JSON con resumen y lista de violaciones.

## Uso

```bash
python scripts/coding/ai/agents/permissions/route_linter.py --verbose
```

## Validaciones Relacionadas

- Ejecutar dentro de pipelines de seguridad o CI para impedir despliegues con endpoints sin permisos.
- Extender reglas personalizadas ajustando métodos de análisis en `RouteLintAgent`.
