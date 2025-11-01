---
id: DOC-ROOT-001
estado: borrador
propietario: equipo-arquitectura
ultima_actualizacion: 2025-02-18
relacionados: ["ADR-2025-001", "DOC-INDEX-GENERAL"]
---
# Base documental del proyecto IACT

Toda la documentación funcional, técnica y operativa vive ahora en `docs/`. La estructura replica la jerarquía oficial de espacios corporativos y elimina la numeración heredada (`00_`, `01_`, ...), facilitando la navegación mediante MkDocs.

## Página padre
- _No aplica; este archivo representa la raíz documental del repositorio._

## Páginas hijas
- [`index.md`](index.md)

## Información clave
### Cómo navegar
- Consulta el índice maestro en [`index.md`](index.md) para ubicar rápidamente cada espacio temático.
- Cada sección cuenta con un archivo `readme.md` que actúa como portada y define responsables, artefactos y relaciones cruzadas.
- Los anexos, plantillas y checklists siguen disponibles en `anexos/`, `plantillas/` y `checklists/` respectivamente.

### Uso con MkDocs
La configuración `mkdocs.yml` permite visualizar la documentación con una experiencia homogénea.

```bash
pip install -r requirements/docs.txt
mkdocs serve
```

El comando `mkdocs serve` habilita un servidor local con recarga automática para revisar cambios en tiempo real.

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada raíz del repositorio documental | Sí | Este archivo concentra metadatos y enlaza al índice principal. |
| Índice maestro de espacios | Sí | Referenciado en [`index.md`](index.md). |
| Guía de navegación corporativa | Sí | Se detalla en la sección **Cómo navegar**. |
| Registro de métricas de documentación | No | Debe consolidarse en coordinación con QA y Gobernanza. |

## Acciones prioritarias
- [ ] Mantener la consistencia de enlaces relativos entre espacios (`../vision_y_alcance/`, `../gobernanza/`, etc.).
- [ ] Registrar nuevas decisiones estratégicas mediante ADR en `arquitectura/adr/`.
- [ ] Integrar métricas de cobertura y evidencias de pruebas en `qa/` siguiendo la metodología TDD establecida.
