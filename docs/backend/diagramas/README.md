# Diagramas Backend - Proyecto IACT

Dominio: Backend
Fecha: 2025-11-16

---

## Estructura de Diagramas

Este directorio contiene todos los diagramas relacionados con el backend del proyecto IACT.

```
docs/backend/diagramas/
├── arquitectura/    - Diagramas de arquitectura backend (C4 Model)
├── database/        - Diagramas ER y esquemas de base de datos
├── secuencia/       - Diagramas de secuencia de APIs y procesos backend
└── actividad/       - Diagramas de actividad de workflows de negocio
```

---

## Arquitectura

**Ubicacion:** [arquitectura/](./arquitectura/)

Diagramas de arquitectura del backend siguiendo C4 Model:
- Nivel 1: Contexto del sistema backend
- Nivel 2: Contenedores (Django, PostgreSQL, Redis, Cassandra)
- Nivel 3: Componentes (apps Django, APIs, servicios)
- Nivel 4: Codigo (clases, modulos)

**Formato:** PlantUML (.puml)

---

## Database

**Ubicacion:** [database/](./database/)

Diagramas de base de datos:
- Esquemas ER (Entity-Relationship)
- Modelos de datos
- Relaciones entre entidades
- Indices y constraints

**Formato:** PlantUML (.puml)

---

## Secuencia

**Ubicacion:** [secuencia/](./secuencia/)

Diagramas de secuencia de:
- Flujos de APIs REST
- Procesos de autenticacion/autorizacion
- Integraciones backend
- Operaciones CRUD
- Procesamiento de datos

**Formato:** PlantUML (.puml)

---

## Actividad

**Ubicacion:** [actividad/](./actividad/)

Diagramas de actividad de:
- Workflows de negocio
- Procesos ETL
- Flujos de aprobacion
- Procesamiento batch
- Validaciones de negocio

**Formato:** PlantUML (.puml)

---

## Herramientas

**PlantUML:**
- Editor online: https://www.plantuml.com/plantuml/
- VSCode extension: PlantUML
- CLI: `plantuml diagrama.puml`

**Renderizado:**
```bash
# Generar PNG
plantuml arquitectura/mi_diagrama.puml

# Generar SVG
plantuml -tsvg arquitectura/mi_diagrama.puml
```

---

## Convenciones

**Nomenclatura archivos:**
- `{modulo}_{tipo}_{descripcion}.puml`
- Ejemplos: `permisos_er.puml`, `dora_metrics_seq.puml`

**Versionamiento:**
- Incluir fecha en comentario inicial
- Documentar cambios significativos

---

## Diagramas Transversales

Para diagramas de contexto general del sistema completo (frontend + backend + externos):
- Ver: [docs/anexos/diagramas/contexto/](../../anexos/diagramas/contexto/)

---

## Referencias

- [C4 Model](https://c4model.com/)
- [PlantUML Guide](https://plantuml.com/guide)
- [UML Sequence Diagrams](https://www.uml-diagrams.org/sequence-diagrams.html)
- [ER Diagrams Best Practices](https://www.lucidchart.com/pages/er-diagrams)

---

Mantenido por: Equipo Backend
Ultima actualizacion: 2025-11-16
