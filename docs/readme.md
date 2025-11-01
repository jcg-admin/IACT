---
id: DOC-ROOT-001
estado: borrador
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-18
relacionados: ["ADR-2025-001", "DOC-SPACES-INDEX"]
---
# Base documental del proyecto IACT

Toda la documentación funcional, técnica y operativa vive ahora en `docs/spaces/`. La estructura replica la jerarquía oficial de espacios corporativos y elimina la numeración heredada (`00_`, `01_`, ...), facilitando la navegación mediante MkDocs.

## Cómo navegar
- Consulta el índice maestro en [`spaces/index.md`](spaces/index.md) para ubicar rápidamente cada espacio temático.
- Cada sección cuenta con un archivo `readme.md` que actúa como portada y define responsables, artefactos y relaciones cruzadas.
- Los anexos, plantillas y checklists siguen disponibles en `spaces/anexos/`, `spaces/plantillas/` y `spaces/checklists/` respectivamente.

## MkDocs
El repositorio incluye una configuración de MkDocs para visualizar la documentación con una experiencia homogénea.

```bash
pip install mkdocs
mkdocs serve
```

El comando `mkdocs serve` habilita un servidor local con recarga automática para revisar cambios en tiempo real.

## Próximos pasos
1. Mantener la consistencia de enlaces relativos entre espacios (`../vision_y_alcance/`, `../gobernanza/`, etc.).
2. Registrar nuevas decisiones estratégicas mediante ADR en `spaces/arquitectura/adr/`.
3. Integrar métricas de cobertura y evidencias de pruebas en `spaces/qa/` siguiendo la metodología TDD establecida.
