# Diagramas de Arquitectura

**Tipo:** Diagramas de arquitectura de software
**Notacion:** C4 Model, UML Component Diagrams
**Herramientas:** PlantUML, Draw.io, Mermaid

---

## Proposito

Este directorio contiene diagramas que muestran la arquitectura del sistema IACT a diferentes niveles de abstraccion.

---

## Niveles de Abstraccion (C4 Model)

### Nivel 1: Contexto del Sistema

**Archivo:** `01_contexto_sistema.puml`

**Descripcion:** Vista de alto nivel mostrando el sistema y sus interacciones con usuarios y sistemas externos.

**Elementos:**
- Sistema IACT
- Usuarios (Agentes, Supervisores, Admins)
- Sistemas externos (CRM, telefonia, etc.)

---

### Nivel 2: Contenedores

**Archivo:** `02_contenedores.puml`

**Descripcion:** Principales contenedores tecnologicos del sistema.

**Contenedores:**
- Frontend (React)
- Backend API (Django)
- Base de datos (PostgreSQL/Cassandra)
- Redis (Cache)
- Nginx (Reverse proxy)

---

### Nivel 3: Componentes

**Archivo:** `03_componentes_{dominio}.puml`

**Descripcion:** Componentes internos de cada contenedor.

**Diagramas por dominio:**
- Backend componentes
- Frontend componentes
- Infraestructura componentes

---

### Nivel 4: Codigo

**Ubicacion:** Ver diagramas de clases en `../database/`

---

## Convenciones

**Nombres de archivos:**
```
{nivel}_{nombre}_{version}.{extension}
```

**Ejemplos:**
- `01_contexto_sistema_v1.puml`
- `02_contenedores_v2.drawio`
- `03_componentes_backend_v1.md` (Mermaid)

**Formato preferido:** PlantUML (.puml) para versionamiento en Git

---

## Como Crear un Diagrama

1. Seleccionar nivel C4 apropiado
2. Usar template correspondiente
3. Nombrar segun convencion
4. Generar imagen exportada (.png, .svg)
5. Referenciar desde documentacion

---

## Referencias

- [C4 Model](https://c4model.com/)
- [PlantUML C4](https://github.com/plantuml-stdlib/C4-PlantUML)
- [Arquitectura Backend](../../backend/arquitectura/)
- [Arquitectura Frontend](../../frontend/arquitectura/)

---

**Maintainer:** Architecture Team
**Ultima actualizacion:** 2025-11-16
