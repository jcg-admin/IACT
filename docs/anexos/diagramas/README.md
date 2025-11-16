# Diagramas Transversales - Proyecto IACT

Fecha: 2025-11-16

---

## Organizacion de Diagramas

Los diagramas del proyecto IACT estan organizados por dominio:

**Backend:**
- Ubicacion: [docs/backend/diagramas/](../../backend/diagramas/)
- Contenido: Arquitectura backend, database, secuencia de APIs, actividad de workflows

**Frontend:**
- Ubicacion: [docs/frontend/diagramas/](../../frontend/diagramas/)
- Contenido: Casos de uso, interacciones UI, componentes

**Transversales:**
- Ubicacion: `docs/anexos/diagramas/` (este directorio)
- Contenido: Diagramas de contexto general del sistema completo

---

## Diagramas Transversales

Este directorio contiene solo diagramas que abarcan multiples dominios o muestran el sistema completo.

```
docs/anexos/diagramas/
└── contexto/    - Diagramas de contexto C4 Level 1 (sistema completo)
```

---

## Contexto

**Ubicacion:** [contexto/](./contexto/)

Diagramas de contexto del sistema completo (C4 Model Level 1):
- Sistema IACT como caja negra
- Actores principales (Agentes, Supervisores, Admins)
- Sistemas externos (CRM, PBX, Email, SMS)
- Flujos de datos de alto nivel

**Proposito:**
- Vision general para stakeholders
- Comprension del alcance del sistema
- Identificacion de integraciones

---

## Navegacion Rapida

**Diagramas Backend:**
- [Arquitectura backend](../../backend/diagramas/arquitectura/)
- [Database schemas](../../backend/diagramas/database/)
- [Secuencia de APIs](../../backend/diagramas/secuencia/)
- [Actividad workflows](../../backend/diagramas/actividad/)

**Diagramas Frontend:**
- [Casos de uso UI](../../frontend/diagramas/casos_de_uso/)

---

## Herramientas

**PlantUML:**
- Editor online: https://www.plantuml.com/plantuml/
- VSCode extension: PlantUML
- C4 Model: https://github.com/plantuml-stdlib/C4-PlantUML

---

Mantenido por: Equipo Arquitectura
Ultima actualizacion: 2025-11-16
