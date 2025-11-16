# Diagramas de Contexto

**Tipo:** Diagramas de contexto (C4 Level 1)
**Notacion:** C4 Model Context Diagrams
**Herramientas:** PlantUML C4, Draw.io

---

## Proposito

Vistas de muy alto nivel mostrando el sistema en su contexto organizacional y tecnico.

**Muestra:**
- El sistema como caja negra
- Usuarios principales
- Sistemas externos
- Flujos de datos principales

**NO muestra:**
- Detalles internos del sistema
- Tecnologias especificas
- Componentes internos

---

## Diagrama Principal

**Archivo:** `contexto_sistema_iact_v1.puml`

**Actores:**
- Agentes de call center
- Supervisores
- Administradores
- Analistas

**Sistemas externos:**
- CRM corporativo
- Sistema de telefonia (PBX)
- Servicio de email
- Servicio de SMS
- Sistema de analíticos empresariales

**Flujos de datos:**
- Agente → IACT: Interacciones
- IACT → CRM: Sincronizacion de datos
- IACT → Telefonia: Metricas de llamadas
- IACT → Email/SMS: Notificaciones

---

## Template C4 Context

```plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

Person(agente, "Agente", "Usuario del call center")
Person(supervisor, "Supervisor", "Gestiona equipo")

System(iact, "Sistema IACT", "Sistema de gestion de call center")

System_Ext(crm, "CRM", "Sistema CRM corporativo")
System_Ext(pbx, "PBX", "Sistema de telefonia")

Rel(agente, iact, "Usa")
Rel(supervisor, iact, "Gestiona")
Rel(iact, crm, "Sincroniza datos")
Rel(iact, pbx, "Obtiene metricas")

@enduml
```

---

## Versiones

- v1.0: Contexto inicial (2025-11-16)
- v2.0: Incluir nuevos sistemas (planificado)

---

**Ultima actualizacion:** 2025-11-16
