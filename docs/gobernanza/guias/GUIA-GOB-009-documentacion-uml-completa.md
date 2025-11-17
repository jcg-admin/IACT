---
id: GUIA-GOB-009
tipo: guia
titulo: Documentación UML Completa y Patrones de Diagramas
version: 1.0.0
fecha_creacion: 2025-01-17
autores: [Sistema]
estado: borrador
relacionado_con: [ADR-GOB-004, ADR-GOB-008, GUIA-GOB-008]
trazabilidad_upward: []
trazabilidad_downward: []
---

# GUIA-GOB-009: Documentación UML Completa y Patrones de Diagramas

## 1. Introducción

Esta guía proporciona patrones completos de documentación UML para todos los tipos de diagramas estándar de UML 2.5. Cada patrón incluye:

- **Propósito**: Cuándo usar el diagrama
- **Elementos principales**: Componentes del diagrama
- **Sintaxis PlantUML**: Código fuente comentado
- **Casos de uso**: Cuándo es más útil
- **Ejemplo del proyecto IACT**: Aplicación práctica
- **Anti-patrones**: Qué evitar

## 2. Fundamentos de PlantUML

### 2.1 Estructura Básica

Todos los diagramas PlantUML siguen esta estructura:

```plantuml
@startuml
' Metadata del diagrama
' Título, autor, versión, etc.

' Configuración (opcional)
' Estilos, dirección, escala

' Contenido del diagrama
' Elementos, relaciones, notas

@enduml
```

### 2.2 Nomenclatura de Archivos

Según [ADR-GOB-004](../adr/ADR-GOB-004-plantuml-para-diagramas.md):

```
TIPO-DOMINIO-###-descripcion.puml

Tipos:
- UC: Casos de Uso
- CLASS: Clases
- SEQ: Secuencia
- ACT: Actividad
- STATE: Estados
- COMP: Componentes
- DEPLOY: Despliegue
- OBJ: Objetos
- PKG: Paquetes
- TIMING: Timing
- COMM: Comunicación
```

### 2.3 Metadata Estándar

Todos los diagramas deben incluir:

```plantuml
@startuml
title Título del Diagrama
caption Versión 1.0.0 | Fecha: 2025-01-17
footer Proyecto IACT | Autor: [Nombre]

' Notas de documentación
note top
  **Propósito**: Describe qué hace el diagrama
  **Audiencia**: Quién debe leerlo
  **Referencias**: ADRs, RFs relacionados
end note

' Contenido aquí...

@enduml
```

## 3. Diagrama de Despliegue (Deployment Diagram)

### 3.1 Propósito

Documenta la **arquitectura física** del sistema:
- Nodos de hardware/software
- Artefactos desplegados
- Conexiones de red
- Protocolos de comunicación

### 3.2 Cuándo Usar

- ✅ Diseño de infraestructura cloud/on-premise
- ✅ Documentación de topología de red
- ✅ Planificación de deployment
- ✅ Comunicación con DevOps/Infra
- ❌ NO para lógica de negocio (usar Secuencia/Actividad)
- ❌ NO para estructura de clases (usar Clases)

### 3.3 Elementos Principales

| Elemento | Notación PlantUML | Descripción |
|----------|-------------------|-------------|
| **Nodo** | `node "Nombre"` | Hardware o entorno de ejecución |
| **Artefacto** | `artifact "Nombre"` | Software deployable (.jar, .war, .exe) |
| **Componente** | `component "Nombre"` | Módulo de software |
| **Conexión** | `-->` | Comunicación entre nodos |
| **Protocolo** | `: HTTP/HTTPS` | Protocolo de comunicación |
| **Estereotipo** | `<<database>>` | Tipo especial de nodo |

### 3.4 Sintaxis PlantUML Completa

```plantuml
@startuml DEPLOY-BACK-001-arquitectura-produccion
title Arquitectura de Despliegue - Producción IACT
caption Versión 1.0.0 | Fecha: 2025-01-17
footer Proyecto IACT | Backend Team

' Configuración
!define CLOUDOGU_BLUE #3b82f6
!define CLOUDOGU_GREEN #10b981
skinparam node {
  BackgroundColor CLOUDOGU_BLUE
  BorderColor #1e3a8a
}

' === CAPA DE PRESENTACIÓN ===
node "Load Balancer" <<nginx>> as lb {
  component "NGINX" as nginx
  note right
    - SSL Termination
    - Rate Limiting
    - Gzip Compression
  end note
}

' === CAPA DE APLICACIÓN ===
node "App Server 1" <<docker>> as app1 {
  artifact "django-app.tar" as django1
  component "Gunicorn" as gunicorn1
  component "Celery Worker" as celery1
}

node "App Server 2" <<docker>> as app2 {
  artifact "django-app.tar" as django2
  component "Gunicorn" as gunicorn2
  component "Celery Worker" as celery2
}

' === CAPA DE DATOS ===
node "Database Server" <<postgresql>> as db {
  database "PostgreSQL 15" as postgres {
    storage "iact_db" as dbschema
  }
  note bottom
    - Master-Slave Replication
    - Daily Backups
    - Connection Pooling
  end note
}

node "Cache Server" <<redis>> as cache {
  database "Redis 7" as redis
}

node "Message Broker" <<rabbitmq>> as broker {
  component "RabbitMQ" as rabbitmq
}

' === CAPA DE ALMACENAMIENTO ===
node "File Storage" <<s3>> as storage {
  storage "AWS S3" as s3
  note right
    - Media files
    - Static assets
    - Backups
  end note
}

' === CONEXIONES ===
' Internet -> Load Balancer
cloud "Internet" as internet
internet --> lb : HTTPS (443)

' Load Balancer -> App Servers
lb --> app1 : HTTP (8000)
lb --> app2 : HTTP (8000)

' App Servers -> Database
app1 --> db : PostgreSQL (5432)
app2 --> db : PostgreSQL (5432)

' App Servers -> Cache
app1 --> cache : Redis (6379)
app2 --> cache : Redis (6379)

' App Servers -> Message Broker
celery1 --> broker : AMQP (5672)
celery2 --> broker : AMQP (5672)

' App Servers -> Storage
app1 --> storage : HTTPS/S3 API
app2 --> storage : HTTPS/S3 API

' Broker -> Database (persistence)
broker ..> db : Persistence

' === NOTAS GENERALES ===
note top of internet
  **CDN**: CloudFlare
  - DDoS Protection
  - Edge Caching
end note

note bottom of app1
  **Escalabilidad Horizontal**
  Se pueden agregar más app servers
  según demanda (Auto-scaling)
end note

@enduml
```

### 3.5 Patrones Comunes

#### Patrón 1: 3-Tier Architecture

```plantuml
@startuml
title Arquitectura 3-Tier Estándar

' Tier 1: Presentación
node "Frontend Tier" {
  component "React SPA" as react
}

' Tier 2: Lógica de Negocio
node "Backend Tier" {
  component "Django API" as django
}

' Tier 3: Datos
node "Data Tier" {
  database "PostgreSQL" as db
}

react --> django : REST API (HTTPS)
django --> db : SQL (5432)

@enduml
```

#### Patrón 2: Microservicios

```plantuml
@startuml
title Arquitectura de Microservicios

node "API Gateway" as gateway {
  component "Kong" as kong
}

node "Auth Service" as auth {
  component "OAuth2 Server" as oauth
  database "Auth DB" as authdb
}

node "User Service" as user {
  component "User API" as userapi
  database "User DB" as userdb
}

node "Order Service" as order {
  component "Order API" as orderapi
  database "Order DB" as orderdb
}

node "Message Bus" as bus {
  component "RabbitMQ" as rabbit
}

gateway --> auth : Auth
gateway --> user : Users
gateway --> order : Orders

auth --> bus : Events
user --> bus : Events
order --> bus : Events

@enduml
```

#### Patrón 3: Serverless

```plantuml
@startuml
title Arquitectura Serverless (AWS)

cloud "AWS" {
  node "API Gateway" as apigw

  node "Lambda Functions" {
    component "auth_handler" as lambda1
    component "user_handler" as lambda2
    component "order_handler" as lambda3
  }

  database "DynamoDB" as dynamo
  storage "S3" as s3

  apigw --> lambda1
  apigw --> lambda2
  apigw --> lambda3

  lambda1 --> dynamo
  lambda2 --> dynamo
  lambda3 --> s3
}

@enduml
```

### 3.6 Estereotipos Útiles

```plantuml
@startuml
title Estereotipos Comunes en Diagramas de Despliegue

' Hardware
node "Physical Server" <<device>>
node "Virtual Machine" <<execution environment>>

' Contenedores
node "Docker Container" <<container>>
node "Kubernetes Pod" <<pod>>

' Bases de datos
database "Relational DB" <<database>>
database "NoSQL DB" <<document store>>
database "Cache" <<key-value store>>

' Servicios cloud
cloud "AWS" <<cloud provider>>
node "Lambda" <<function>>
node "S3" <<object storage>>

' Networking
node "Load Balancer" <<load balancer>>
node "Reverse Proxy" <<proxy>>
node "CDN" <<content delivery>>

@enduml
```

### 3.7 Ejemplo Completo: Sistema IACT

```plantuml
@startuml DEPLOY-IACT-001-arquitectura-completa
title Arquitectura de Despliegue Completa - Sistema IACT
caption Versión 1.0.0 | Fecha: 2025-01-17 | Trazabilidad: RNF-001, RNF-002
footer Proyecto IACT | Arquitectura

' === CONFIGURACIÓN ===
skinparam componentStyle rectangle
left to right direction

' === ZONA PÚBLICA (DMZ) ===
package "Zona Pública (DMZ)" {
  node "Reverse Proxy" <<nginx>> as proxy {
    component "NGINX" as nginx
    note right
      - SSL/TLS Termination
      - Rate Limiting (100 req/s)
      - Static File Serving
      - WebSocket Proxy
    end note
  }
}

' === ZONA DE APLICACIÓN ===
package "Zona de Aplicación (Privada)" {

  ' Frontend
  node "Frontend Server" <<docker>> as frontend {
    artifact "react-app.tar" as reactapp
    component "Nginx (SPA)" as frontnginx
  }

  ' Backend Cluster
  node "Backend Server 1" <<docker>> as backend1 {
    artifact "django-app.whl" as djangoapp1
    component "Gunicorn (4 workers)" as gunicorn1
    component "Celery Worker" as celery1
  }

  node "Backend Server 2" <<docker>> as backend2 {
    artifact "django-app.whl" as djangoapp2
    component "Gunicorn (4 workers)" as gunicorn2
    component "Celery Worker" as celery2
  }

  ' WebSocket Server
  node "WebSocket Server" <<docker>> as ws {
    component "Daphne (ASGI)" as daphne
    note bottom
      - Django Channels
      - Real-time notifications
      - Call center events
    end note
  }
}

' === ZONA DE DATOS ===
package "Zona de Datos (Aislada)" {

  ' Base de datos principal
  node "Database Primary" <<postgresql>> as dbprimary {
    database "PostgreSQL 15" as postgres {
      storage "iact_production" as proddb
    }
    note right
      - Master Node
      - Streaming Replication
      - Point-in-Time Recovery
    end note
  }

  node "Database Replica" <<postgresql>> as dbreplica {
    database "PostgreSQL 15 (Read)" as postgresreplica
  }

  ' Cache (según RNF-002: NO Redis en sesiones)
  node "Application Cache" <<redis>> as appcache {
    database "Redis 7" as redis
    note bottom
      - Solo para cache de datos
      - NO para sesiones (RNF-002)
      - TTL: 5-15 minutos
    end note
  }

  ' Message Broker
  node "Task Queue" <<rabbitmq>> as taskqueue {
    component "RabbitMQ 3.12" as rabbitmq
  }
}

' === ZONA DE SERVICIOS EXTERNOS ===
package "Servicios Externos" {
  cloud "AWS S3" as s3 {
    storage "Media Storage" as s3storage
  }

  cloud "Email Service" <<smtp>> as email

  cloud "Monitoring" as monitoring {
    component "Prometheus" as prometheus
    component "Grafana" as grafana
  }
}

' === CONEXIONES ===

' Internet -> Proxy
actor "Usuario" as user
user --> proxy : HTTPS (443)

' Proxy -> Frontend
proxy --> frontend : HTTP (3000)

' Proxy -> Backend
proxy --> backend1 : HTTP (8000)
proxy --> backend2 : HTTP (8000)

' Proxy -> WebSocket
proxy --> ws : WS/WSS (8001)

' Backend -> Database
backend1 --> dbprimary : PostgreSQL (5432)\nRead/Write
backend2 --> dbprimary : PostgreSQL (5432)\nRead/Write

backend1 ..> dbreplica : PostgreSQL (5432)\nRead Only
backend2 ..> dbreplica : PostgreSQL (5432)\nRead Only

' Database Replication
dbprimary --> dbreplica : Streaming\nReplication

' Backend -> Cache
backend1 --> appcache : Redis (6379)\nData Cache Only
backend2 --> appcache : Redis (6379)\nData Cache Only

' Celery -> RabbitMQ
celery1 --> taskqueue : AMQP (5672)
celery2 --> taskqueue : AMQP (5672)

' Backend -> S3
backend1 --> s3 : HTTPS\nMedia Upload
backend2 --> s3 : HTTPS\nMedia Upload

' Backend -> Email (según restricción: NO Email en dev)
backend1 ..> email : SMTP (587)\nSolo en producción
backend2 ..> email : SMTP (587)\nSolo en producción

' Monitoring
backend1 --> monitoring : Metrics (9090)
backend2 --> monitoring : Metrics (9090)
dbprimary --> monitoring : Metrics (9187)

' === LEYENDA ===
legend right
  **Restricciones IACT**
  - RNF-002: Sesiones en MySQL, NO Redis
  - RNF-004: NO emojis/iconos en código
  - RNF-006: Performance < 200ms (p95)

  **Capacidad**
  - Backend: 2 servers × 4 workers = 8 concurrent requests
  - Escalabilidad: Horizontal (agregar servers)

  **Alta Disponibilidad**
  - Load balancing en backend
  - Database replication (read replicas)
  - Failover automático
end legend

@enduml
```

### 3.8 Anti-patrones

❌ **Anti-patrón 1: Demasiado detalle**

```plantuml
' MAL: Muestra cada archivo y proceso
node "Server" {
  artifact "app.py"
  artifact "models.py"
  artifact "views.py"
  artifact "urls.py"
  ' ... 50 archivos más ...
}
```

✅ **Mejor: Agrupa por componente lógico**

```plantuml
node "Server" {
  component "Django App" {
    artifact "app.whl"
  }
}
```

❌ **Anti-patrón 2: Mezclar niveles de abstracción**

```plantuml
' MAL: Mezcla infraestructura con lógica
node "Server" {
  component "User Service"  ' <- lógica
  artifact "docker-compose.yml"  ' <- infra
}
```

✅ **Mejor: Consistencia en el nivel**

```plantuml
node "App Server" <<docker>> {
  component "User Service"
  component "Order Service"
}
```

## 4. Diagrama de Componentes (Component Diagram)

### 4.1 Propósito

Documenta la **arquitectura lógica** del software:
- Componentes principales
- Interfaces expuestas
- Dependencias entre componentes
- Puertos y conectores

### 4.2 Cuándo Usar

- ✅ Arquitectura de módulos/librerías
- ✅ Diseño de APIs
- ✅ Documentación de dependencias
- ✅ Refactoring de monolito a microservicios

### 4.3 Sintaxis PlantUML

```plantuml
@startuml COMP-BACK-001-arquitectura-modulos
title Arquitectura de Componentes - Backend IACT

package "Backend IACT" {

  ' Componentes
  component "API Gateway" as gateway
  component "Authentication" as auth
  component "User Management" as users
  component "Call Center" as calls
  component "Permissions" as perms

  ' Interfaces
  interface "REST API" as restapi
  interface "Auth Interface" as authif
  interface "Permission Check" as permif

  ' Relaciones
  gateway - restapi
  restapi -- auth
  restapi -- users
  restapi -- calls

  auth - authif
  perms - permif

  users --> authif : uses
  calls --> authif : uses
  calls --> permif : uses
  users --> permif : uses
}

database "PostgreSQL" as db

auth --> db
users --> db
calls --> db
perms --> db

note right of gateway
  **Responsabilidades**:
  - Routing
  - Rate limiting
  - CORS handling
end note

@enduml
```

### 4.4 Ejemplo: Módulo de Permisos IACT

```plantuml
@startuml COMP-BACK-005-modulo-permisos
title Componentes del Módulo de Permisos Granulares
caption Trazabilidad: UC-PERM-001 a UC-PERM-010
footer Proyecto IACT | Backend Team

package "Módulo de Permisos" <<subsystem>> {

  ' === CAPA DE API ===
  component "Permission API" as api {
    portin " REST Endpoints" as port_rest
    portin " GraphQL Endpoint" as port_graphql
  }

  ' === CAPA DE SERVICIO ===
  component "Permission Service" as service {
    port "IPermissionChecker" as port_checker
    port "IPermissionManager" as port_manager
  }

  ' === COMPONENTES FUNCIONALES ===
  component "Verification Engine" as verifier {
    note bottom
      **UC-PERM-007**: Verificar Permiso
      - Revocaciones excepcionales (prioridad 1)
      - Concesiones excepcionales (prioridad 2)
      - Grupos (prioridad 3)
    end note
  }

  component "Audit Logger" as auditor {
    note bottom
      **UC-PERM-009**: Auditar Acceso
      - Log de cada verificación
      - IP, User-Agent, Timestamp
    end note
  }

  component "Menu Generator" as menugenerator {
    note bottom
      **UC-PERM-008**: Generar Menú Dinámico
      - Estructura jerárquica
      - Basado en capacidades del usuario
    end note
  }

  component "Group Manager" as groupmanager
  component "Exception Manager" as exceptionmanager

  ' === CAPA DE DATOS ===
  component "Permission Repository" as repo {
    port "IRepository" as port_repo
  }

  ' === CAPA DE CACHE ===
  component "Permission Cache" as cache {
    note right
      - TTL: 5 minutos
      - Invalidación automática
      - Key: user_id:capability
    end note
  }

  ' === RELACIONES ===
  api --> service : uses

  service --> verifier : delegates
  service --> auditor : delegates
  service --> menugenerator : delegates
  service --> groupmanager : delegates
  service --> exceptionmanager : delegates

  verifier --> repo : reads
  verifier --> cache : checks first
  verifier --> auditor : logs result

  groupmanager --> repo : CRUD
  exceptionmanager --> repo : CRUD
  menugenerator --> verifier : uses

  cache --> repo : on miss
}

' === DEPENDENCIAS EXTERNAS ===
database "PostgreSQL" as db
component "Django ORM" as orm

repo --> orm : uses
orm --> db : SQL

' === CONSUMIDORES ===
component "User Management" as users
component "Call Center" as calls
component "Admin Panel" as admin

users --> api : HTTP/REST
calls --> api : HTTP/REST
admin --> api : HTTP/REST

@enduml
```

## 5. Diagrama de Secuencia (Sequence Diagram)

### 5.1 Propósito

Documenta **interacciones entre objetos a lo largo del tiempo**:
- Flujo de mensajes
- Orden temporal
- Loops y condicionales
- Asincronía

### 5.2 Sintaxis PlantUML

```plantuml
@startuml SEQ-PERM-007-verificar-permiso
title Secuencia: Verificar Permiso de Usuario
caption UC-PERM-007 | Performance Target: < 10ms

actor Usuario
participant "Frontend" as FE
participant "API Gateway" as GW
participant "Permission Service" as PS
participant "Cache" as Cache
participant "Database" as DB
participant "Audit Service" as Audit

Usuario -> FE : Intenta acceder a recurso
activate FE

FE -> GW : GET /api/permisos/verificar/\n{usuario_id}/tiene-permiso/\n?capacidad=sistema.vistas.dashboards.ver
activate GW

GW -> PS : verificarPermiso(usuario_id, capacidad)
activate PS

' Verificación en cache
PS -> Cache : get("user:123:sistema.vistas.dashboards.ver")
activate Cache
Cache --> PS : null (cache miss)
deactivate Cache

' Consulta a BD
PS -> DB : SELECT FROM vista_capacidades_usuario\nWHERE usuario_id = 123\nAND capacidad_codigo = 'sistema.vistas.dashboards.ver'
activate DB
DB --> PS : resultado (true)
deactivate DB

' Guardar en cache
PS -> Cache : set("user:123:...", true, TTL=300s)
activate Cache
deactivate Cache

' Auditoría asíncrona
PS ->> Audit : auditPermissionCheck(usuario_id, capacidad, resultado)
note right: Asíncrono (no bloquea)

PS --> GW : {tiene_permiso: true, origen: "grupo"}
deactivate PS

GW --> FE : HTTP 200\n{tiene_permiso: true}
deactivate GW

FE --> Usuario : Muestra dashboard
deactivate FE

@enduml
```

### 5.3 Elementos Avanzados

```plantuml
@startuml SEQ-EXAMPLE-elementos-avanzados
title Elementos Avanzados de Secuencia

actor Actor
participant "Sistema A" as A
participant "Sistema B" as B
database "Base de Datos" as DB

' Activación
Actor -> A : request()
activate A

' Condicional
alt successful case
  A -> B : call()
  B --> A : success
else failure
  A -> B : retry()
  B --> A : still failing
else fallback
  A -> A : useCachedData()
end

' Loop
loop every 5 seconds
  A -> B : healthCheck()
  B --> A : OK
end

' Opcional
opt if cache miss
  A -> DB : query()
  DB --> A : data
end

' Paralelo
par
  A -> B : async call 1
and
  A -> DB : async call 2
end

B --> A : response 1
DB --> A : response 2

' Referencia a otro diagrama
ref over A, B
  Ver SEQ-AUTH-001 para detalles de autenticación
end ref

deactivate A

@enduml
```

## 6. Diagrama de Actividad (Activity Diagram)

### 6.1 Propósito

Documenta **flujos de trabajo y procesos de negocio**:
- Decisiones (if/else)
- Paralelismo (fork/join)
- Loops
- Swimlanes (responsabilidades)

### 6.2 Sintaxis PlantUML

```plantuml
@startuml ACT-PERM-003-conceder-permiso-excepcional
title Actividad: Conceder Permiso Excepcional
caption UC-PERM-003 | Trazabilidad: RF-PERM-003

|Administrador|
start
:Selecciona usuario;
:Selecciona capacidad a conceder;
:Ingresa justificación;
:Define fecha de expiración (opcional);

|Sistema|
:Valida que capacidad exista;

if (¿Capacidad válida?) then (sí)
  :Verifica si ya existe concesión;

  if (¿Ya existe?) then (sí)
    |Administrador|
    :Muestra error:\n"Permiso ya concedido";
    stop
  else (no)
    |Sistema|
    :Crea registro en\ntabla permiso_excepcional_conceder;

    fork
      :Invalida cache del usuario;
    fork again
      :Registra en auditoría;
    fork again
      :Notifica al usuario\n(InternalMessage);
    end fork

    |Administrador|
    :Muestra confirmación;

    if (¿Tiene fecha de expiración?) then (sí)
      |Sistema|
      :Programa job de Celery\npara revocar automáticamente;
    endif
  endif
else (no)
  |Administrador|
  :Muestra error:\n"Capacidad no existe";
  stop
endif

stop

@enduml
```

### 6.3 Swimlanes para Responsabilidades

```plantuml
@startuml ACT-CALL-001-registrar-llamada
title Actividad: Registrar Llamada Entrante
caption UC-CALL-001 | Sistema de Call Center

|Sistema Telefónico|
start
:Llamada entrante detectada;
:Captura CallerID;

|Sistema IACT|
:Busca cliente por teléfono;

if (¿Cliente encontrado?) then (sí)
  :Muestra datos del cliente;
  :Crea registro de llamada\ncon cliente asociado;
else (no)
  :Muestra formulario\n"Cliente Nuevo";
endif

|Agente|
:Atiende la llamada;
:Selecciona motivo de llamada;
:Registra notas de la conversación;

|Sistema IACT|
:Valida campos obligatorios;

if (¿Datos completos?) then (sí)
  :Guarda llamada en BD;

  fork
    :Actualiza estadísticas\ndel agente;
  fork again
    :Genera evento para\nreportes en tiempo real;
  end fork

  :Marca llamada como "En Curso";

  |Agente|
  :Continúa conversación;

  :Finaliza llamada;

  |Sistema IACT|
  :Actualiza duración;
  :Marca como "Finalizada";
  :Calcula métricas\n(AHT, First Call Resolution);

else (no)
  |Agente|
  :Muestra errores de validación;
  stop
endif

stop

@enduml
```

## 7. Diagrama de Estados (State Diagram)

### 7.1 Propósito

Documenta el **ciclo de vida de un objeto**:
- Estados posibles
- Transiciones entre estados
- Eventos que causan transiciones
- Acciones en entrada/salida

### 7.2 Sintaxis PlantUML

```plantuml
@startuml STATE-CALL-001-ciclo-vida-llamada
title Estados: Ciclo de Vida de una Llamada
caption Trazabilidad: RF-CALL-001

[*] --> Entrante : Llamada detectada

Entrante : entry / Crear registro
Entrante : do / Ring
Entrante : exit / Detener ring

Entrante --> EnCurso : Agente atiende
Entrante --> Perdida : Timeout (30s)
Entrante --> Perdida : Agente rechaza

EnCurso : entry / Iniciar cronómetro
EnCurso : do / Grabar conversación
EnCurso : exit / Detener cronómetro

EnCurso --> EnEspera : Hold
EnCurso --> Transferida : Transferir
EnCurso --> Finalizada : Colgar

EnEspera : entry / Reproducir música
EnEspera --> EnCurso : Resume

Transferida : entry / Buscar agente destino
Transferida --> EnCurso : Aceptada
Transferida --> Finalizada : Rechazada

Finalizada : entry / Calcular duración
Finalizada : entry / Actualizar métricas
Finalizada --> RequiereNotas : Si faltan notas
Finalizada --> Completada : Si tiene notas

RequiereNotas --> Completada : Agente completa notas

Perdida : entry / Incrementar contador perdidas
Perdida --> [*]

Completada --> [*]

@enduml
```

### 7.3 Estados Compuestos

```plantuml
@startuml STATE-COMPLEX-ejemplo-compuesto
title Estados Compuestos: Sistema de Autenticación

[*] --> NoAutenticado

state NoAutenticado {
  [*] --> Inicial
  Inicial --> IngresandoCredenciales : Inicio de sesión
  IngresandoCredenciales --> ValidandoCredenciales : Submit
  ValidandoCredenciales --> IngresandoCredenciales : Error
}

NoAutenticado --> Autenticado : Credenciales válidas

state Autenticado {
  [*] --> Activo

  state Activo {
    [*] --> Normal
    Normal --> Inactivo : 15 min sin actividad
    Inactivo --> Normal : Actividad detectada
    Inactivo --> RequiereReautenticacion : 30 min sin actividad
  }

  RequiereReautenticacion --> Activo : Re-autenticación exitosa
}

Autenticado --> NoAutenticado : Logout
Autenticado --> NoAutenticado : Token expirado

@enduml
```

## 8. Diagrama de Paquetes (Package Diagram)

### 8.1 Propósito

Documenta la **organización de módulos/paquetes**:
- Estructura de directorios
- Dependencias entre paquetes
- Capas arquitectónicas
- Módulos públicos vs privados

### 8.2 Sintaxis PlantUML

```plantuml
@startuml PKG-BACK-001-estructura-backend
title Estructura de Paquetes - Backend IACT

package "apps" {
  package "authentication" {
    [models]
    [views]
    [serializers]
    [services]
  }

  package "users" {
    [models] as users_models
    [views] as users_views
    [serializers] as users_serializers
  }

  package "permissions" {
    [models] as perm_models
    [views] as perm_views
    [services] as perm_services
    [cache] as perm_cache
  }

  package "call_center" {
    [models] as call_models
    [views] as call_views
    [websockets] as call_ws
  }
}

package "core" {
  [settings]
  [urls]
  [middleware]
  [utils]
}

package "shared" {
  [exceptions]
  [validators]
  [decorators]
}

' Dependencias
users --> authentication : uses
call_center --> permissions : uses
call_center --> users : uses
permissions --> shared : uses

authentication ..> core : configured by

@enduml
```

## 9. Diagrama de Clases (Class Diagram)

### 9.1 Sintaxis PlantUML para Modelos Django

```plantuml
@startuml CLASS-BACK-010-modelo-permisos
title Modelo de Datos: Sistema de Permisos Granulares
caption Trazabilidad: RN-PERM-001 a RN-PERM-010

' === ENTIDADES PRINCIPALES ===

class Usuario {
  +id: Integer <<PK>>
  +username: String(150) <<unique>>
  +email: String(254) <<unique>>
  +first_name: String(150)
  +last_name: String(150)
  +is_active: Boolean
  +date_joined: DateTime
  --
  +get_capacidades(): List<String>
  +tiene_capacidad(codigo: String): Boolean
  +get_menu(): Dict
}

class Grupo {
  +id: Integer <<PK>>
  +nombre: String(100) <<unique>>
  +descripcion: Text
  +activo: Boolean
  +fecha_creacion: DateTime
  --
  +get_capacidades(): List<Capacidad>
  +agregar_capacidad(capacidad: Capacidad): void
  +remover_capacidad(capacidad: Capacidad): void
}

class Capacidad {
  +id: Integer <<PK>>
  +codigo: String(200) <<unique>>
  +nombre: String(200)
  +descripcion: Text
  +activo: Boolean
  +fecha_creacion: DateTime
  --
  <<constraint>> codigo formato "sistema.dominio.subdominio.funcion.accion"
  --
  +validar_formato(): Boolean
}

class UsuarioGrupo {
  +id: Integer <<PK>>
  +usuario: ForeignKey(Usuario)
  +grupo: ForeignKey(Grupo)
  +fecha_asignacion: DateTime
  +asignado_por: ForeignKey(Usuario)
  --
  <<unique_together>> (usuario, grupo)
}

class GrupoCapacidad {
  +id: Integer <<PK>>
  +grupo: ForeignKey(Grupo)
  +capacidad: ForeignKey(Capacidad)
  +fecha_asignacion: DateTime
  +asignado_por: ForeignKey(Usuario)
  --
  <<unique_together>> (grupo, capacidad)
}

class PermisoExcepcionalConceder {
  +id: Integer <<PK>>
  +usuario: ForeignKey(Usuario)
  +capacidad: ForeignKey(Capacidad)
  +justificacion: Text
  +fecha_concesion: DateTime
  +fecha_expiracion: DateTime <<nullable>>
  +concedido_por: ForeignKey(Usuario)
  +activo: Boolean
  --
  <<constraint>> fecha_expiracion > fecha_concesion
}

class PermisoExcepcionalRevocar {
  +id: Integer <<PK>>
  +usuario: ForeignKey(Usuario)
  +capacidad: ForeignKey(Capacidad)
  +justificacion: Text
  +fecha_revocacion: DateTime
  +fecha_expiracion: DateTime <<nullable>>
  +revocado_por: ForeignKey(Usuario)
  +activo: Boolean
}

class AuditoriaPermiso {
  +id: Integer <<PK>>
  +usuario: ForeignKey(Usuario)
  +capacidad_codigo: String(200)
  +resultado: Boolean
  +ip_address: String(45)
  +user_agent: Text
  +timestamp: DateTime
  +metadatos: JSONField
  --
  <<index>> (usuario, timestamp)
  <<index>> (capacidad_codigo, timestamp)
  <<index>> (resultado, timestamp)
}

' === RELACIONES ===

Usuario "1" -- "*" UsuarioGrupo : tiene >
Grupo "1" -- "*" UsuarioGrupo : contiene >
Grupo "1" -- "*" GrupoCapacidad : tiene >
Capacidad "1" -- "*" GrupoCapacidad : pertenece a >

Usuario "1" -- "*" PermisoExcepcionalConceder : recibe >
Capacidad "1" -- "*" PermisoExcepcionalConceder : otorga >

Usuario "1" -- "*" PermisoExcepcionalRevocar : pierde >
Capacidad "1" -- "*" PermisoExcepcionalRevocar : revoca >

Usuario "1" -- "*" AuditoriaPermiso : genera >

' === VISTA MATERIALIZADA ===

class VistaCapacidadesUsuario <<view>> {
  +usuario_id: Integer
  +capacidad_codigo: String(200)
  +origen: String(20)
  --
  <<materialized view>>
  <<refresh>> cada 5 minutos o por trigger
}

note right of VistaCapacidadesUsuario
  **Algoritmo de Verificación**:
  1. Revocaciones excepcionales activas → DENEGAR
  2. Concesiones excepcionales activas → CONCEDER
  3. Capacidad por grupos activos → CONCEDER
  4. Sino → DENEGAR
end note

Usuario "1" -- "*" VistaCapacidadesUsuario : tiene capacidades >

@enduml
```

## 10. Otros Diagramas UML

### 10.1 Diagrama de Objetos

```plantuml
@startuml OBJ-EXAMPLE-instancias
title Diagrama de Objetos: Ejemplo de Permisos

object "usuario:Usuario" as u1 {
  id = 123
  username = "carlos.ruiz"
  email = "carlos@iact.com"
}

object "grupo:Grupo" as g1 {
  id = 5
  nombre = "Agentes"
  activo = true
}

object "capacidad:Capacidad" as c1 {
  id = 42
  codigo = "sistema.vistas.dashboards.ver"
}

u1 -- g1 : miembro de
g1 -- c1 : tiene

@enduml
```

### 10.2 Diagrama de Tiempo (Timing)

```plantuml
@startuml TIMING-EXAMPLE-cache-invalidation
title Diagrama de Timing: Invalidación de Cache

robust "Cache Status" as cache
concise "Database" as db
concise "User Request" as req

@0
cache is Valid
db is Idle
req is Idle

@10
req is Request
: Usuario solicita permiso

@15
cache is Hit
: Cache HIT (válido)

@20
req is Response
: Respuesta rápida (< 5ms)

@100
db is Update
: Admin modifica grupos

@105
cache is Invalid
: Cache invalidado

@110
req is Request
: Nueva solicitud de usuario

@115
cache is Miss
: Cache MISS

@120
db is Query
: Consulta a base de datos

@150
cache is Valid
: Cache actualizado

@155
req is Response
: Respuesta (30ms)

@enduml
```

### 10.3 Diagrama de Comunicación

```plantuml
@startuml COMM-EXAMPLE-verificacion-permiso
title Diagrama de Comunicación: Verificar Permiso

object "frontend" as fe
object "api_gateway" as gw
object "permission_service" as ps
object "cache" as cache
object "database" as db

fe -> gw : 1: verificarPermiso(usuario, capacidad)
gw -> ps : 2: checkPermission(usuario, capacidad)
ps -> cache : 3: get(key)
cache --> ps : 4: null (miss)
ps -> db : 5: query(usuario, capacidad)
db --> ps : 6: resultado
ps -> cache : 7: set(key, resultado, TTL)
ps --> gw : 8: resultado
gw --> fe : 9: HTTP 200 {tiene_permiso: true}

@enduml
```

## 11. Mejores Prácticas

### 11.1 Nomenclatura de Archivos

```bash
# CORRECTO
TIPO-DOMINIO-###-descripcion.puml

Ejemplos:
- UC-BACK-001-login-usuario.puml
- SEQ-PERM-007-verificar-permiso.puml
- CLASS-BACK-010-modelo-permisos.puml
- DEPLOY-IACT-001-arquitectura-produccion.puml

# INCORRECTO
diagrama_de_clases.puml
sequence1.puml
deployment.puml
```

### 11.2 Metadata Obligatoria

Todos los diagramas deben incluir:

```plantuml
@startuml
title [Título Descriptivo]
caption Versión X.Y.Z | Fecha: YYYY-MM-DD | Trazabilidad: [IDs]
footer Proyecto IACT | [Equipo/Dominio]

' Contenido...

@enduml
```

### 11.3 Notas de Documentación

Usar notas para contexto:

```plantuml
@startuml
component "User Service" as users

note right of users
  **Responsabilidades**:
  - CRUD de usuarios
  - Validación de datos
  - Integración con LDAP

  **Performance**:
  - Target: < 100ms (p95)
  - Cache: 5 minutos

  **Trazabilidad**:
  - UC-USER-001 a UC-USER-010
end note

@enduml
```

### 11.4 Versionado

```bash
# Git workflow
git add docs/gobernanza/diseno/diagramas/DEPLOY-IACT-001-arquitectura.puml
git commit -m "docs(diseño): crear diagrama de despliegue v1.0.0"

# En el diagrama, actualizar metadata:
caption Versión 1.1.0 | Fecha: 2025-01-17 | Changelog: Agregado Redis
```

### 11.5 Generación de Imágenes

```bash
# Generar SVG (preferido, escalable)
plantuml -tsvg DEPLOY-IACT-001-arquitectura.puml

# Generar PNG (si se requiere)
plantuml -tpng -Sscale=2 DEPLOY-IACT-001-arquitectura.puml

# Batch: todos los .puml en directorio
plantuml -tsvg docs/gobernanza/diseno/diagramas/**/*.puml
```

## 12. Checklist de Calidad

Antes de hacer commit de un diagrama, verifica:

- [ ] **Nomenclatura correcta**: TIPO-DOMINIO-###-descripcion.puml
- [ ] **Metadata completa**: title, caption, footer
- [ ] **Trazabilidad**: Referencias a ADRs, UCs, RFs
- [ ] **Notas explicativas**: Contexto en notas cuando sea necesario
- [ ] **Convenciones PlantUML**: Sintaxis correcta, compila sin errores
- [ ] **Nivel de abstracción**: Consistente en todo el diagrama
- [ ] **Legibilidad**: No más de 20-30 elementos por diagrama
- [ ] **Dirección clara**: left to right o top to bottom según corresponda
- [ ] **Generación**: Imagen SVG generada y verificada
- [ ] **Commit**: Mensaje descriptivo siguiendo estándar

## 13. Herramientas

### 13.1 VSCode Extensions

```json
{
  "recommendations": [
    "jebbs.plantuml",
    "gruntfuggly.todo-tree"
  ]
}
```

### 13.2 Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validar que todos los .puml compilen
for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.puml$'); do
  plantuml -checkonly "$file"
  if [ $? -ne 0 ]; then
    echo "Error: $file no compila"
    exit 1
  fi
done
```

## 14. Referencias

- [PlantUML Official Documentation](https://plantuml.com/)
- [UML 2.5 Specification](https://www.omg.org/spec/UML/2.5/)
- [C4 Model](https://c4model.com/) - Para diagramas de arquitectura
- [ADR-GOB-004: PlantUML para Diagramas](../adr/ADR-GOB-004-plantuml-para-diagramas.md)
- [ADR-GOB-008: Diagramas UML de Casos de Uso](../adr/ADR-GOB-008-diagramas-uml-casos-uso.md)
- [GUIA-GOB-008: Crear Diagramas PlantUML](GUIA-GOB-008-crear-diagramas-plantuml.md)

## Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2025-01-17 | Sistema | Creación inicial con 10 tipos de diagramas UML |

---

**Nota**: Esta guía está en estado **borrador** y requiere ser completada con:

1. Más ejemplos del proyecto IACT para cada tipo de diagrama
2. Sección de troubleshooting común
3. Integración con CI/CD (validación automática)
4. Templates adicionales (profiles, skins personalizados)
5. Casos de estudio completos end-to-end

**Para continuar**: En otra sesión, expandir cada sección con ejemplos reales del código del proyecto IACT.
