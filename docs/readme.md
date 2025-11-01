---
id: DOC-ROOT-001
estado: borrador
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-18
relacionados: ["ADR-2025-001", "DOC-SPACES-INDEX"]
---
# Base documental del proyecto IACT

Toda la documentación funcional, técnica y operativa vive ahora en `docs/spaces/`. La estructura replica la jerarquía oficial de espacios corporativos y elimina la numeración heredada (`00_`, `01_`, ...), facilitando la navegación mediante MkDocs.

## Página padre
- _No aplica; este archivo representa la raíz documental del repositorio._

## Páginas hijas
- [`spaces/index.md`](spaces/index.md)

## Información clave
### Cómo navegar
- Consulta el índice maestro en [`spaces/index.md`](spaces/index.md) para ubicar rápidamente cada espacio temático.
- Cada sección cuenta con un archivo `readme.md` que actúa como portada y define responsables, artefactos y relaciones cruzadas.
- Los anexos, plantillas y checklists siguen disponibles en `spaces/anexos/`, `spaces/plantillas/` y `spaces/checklists/` respectivamente.

### Uso con MkDocs
La configuración `mkdocs.yml` permite visualizar la documentación con una experiencia homogénea.

```bash
pip install mkdocs
mkdocs serve
```

El comando `mkdocs serve` habilita un servidor local con recarga automática para revisar cambios en tiempo real.

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada raíz del repositorio documental | Sí | Este archivo concentra metadatos y enlaza al índice principal. |
| Índice maestro de espacios | Sí | Referenciado en [`spaces/index.md`](spaces/index.md). |
| Guía de navegación corporativa | Sí | Se detalla en la sección **Cómo navegar**. |
| Registro de métricas de documentación | No | Debe consolidarse en coordinación con QA y Gobernanza. |

## Acciones prioritarias
- [ ] Mantener la consistencia de enlaces relativos entre espacios (`../vision_y_alcance/`, `../gobernanza/`, etc.).
- [ ] Registrar nuevas decisiones estratégicas mediante ADR en `spaces/arquitectura/adr/`.
- [ ] Integrar métricas de cobertura y evidencias de pruebas en `spaces/qa/` siguiendo la metodología TDD establecida.
