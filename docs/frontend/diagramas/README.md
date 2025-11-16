# Diagramas Frontend - Proyecto IACT

Dominio: Frontend
Fecha: 2025-11-16

---

## Estructura de Diagramas

Este directorio contiene todos los diagramas relacionados con el frontend del proyecto IACT.

```
docs/frontend/diagramas/
└── casos_de_uso/    - Diagramas de casos de uso de interfaz de usuario
```

---

## Casos de Uso

**Ubicacion:** [casos_de_uso/](./casos_de_uso/)

Diagramas de casos de uso de:
- Interacciones de usuarios con la UI
- Flujos de navegacion
- Operaciones CRUD desde interfaz
- Permisos y accesos
- Workflows de usuario final

**Formato:** PlantUML (.puml)

**Contenido actual:**
- UC-001: Generar reporte de metricas
- UC-002: Registrar llamada entrante
- UC-003: Consultar estado de pedido
- UC-PERM-001 a UC-PERM-008: Sistema de permisos

---

## Diagramas Futuros

Proximos tipos de diagramas frontend a agregar:

**Arquitectura Frontend:**
- Estructura de componentes React
- Arbol de estado Redux
- Flujo de datos unidireccional
- Modulos y lazy loading

**Secuencia Frontend:**
- Flujos de autenticacion UI
- Interacciones componente-API
- Renderizado condicional
- Manejo de errores UI

**Navegacion:**
- Sitemap de la aplicacion
- Flujos de navegacion
- Breadcrumbs y rutas

---

## Herramientas

**PlantUML:**
- Editor online: https://www.plantuml.com/plantuml/
- VSCode extension: PlantUML
- CLI: `plantuml diagrama.puml`

**Renderizado:**
```bash
# Generar PNG
plantuml casos_de_uso/mi_diagrama.puml

# Generar SVG
plantuml -tsvg casos_de_uso/mi_diagrama.puml
```

---

## Convenciones

**Nomenclatura archivos:**
- `UC-{numero}_{descripcion}.puml` para casos de uso
- `{modulo}_{tipo}_{descripcion}.puml` para otros
- Ejemplos: `UC-001_generar_reporte_metricas.puml`

**Actores:**
- Agente: Usuario operador del call center
- Supervisor: Usuario supervisor
- Admin: Administrador del sistema
- Sistema: Aplicacion IACT

---

## Diagramas Transversales

Para diagramas de contexto general del sistema completo (frontend + backend + externos):
- Ver: [docs/anexos/diagramas/contexto/](../../anexos/diagramas/contexto/)

Para diagramas backend (APIs, database, procesamiento):
- Ver: [docs/backend/diagramas/](../../backend/diagramas/)

---

## Referencias

- [UML Use Case Diagrams](https://www.uml-diagrams.org/use-case-diagrams.html)
- [PlantUML Use Case Guide](https://plantuml.com/use-case-diagram)
- [User Story Mapping](https://www.jpattonassociates.com/user-story-mapping/)

---

Mantenido por: Equipo Frontend
Ultima actualizacion: 2025-11-16
