# TASK-063: Crear GUIA_NAVEGACION_BACKEND.md

## Metadatos
- **ID**: TASK-063
- **Fase**: FASE 4 - Validación y Limpieza
- **Prioridad**: MEDIA 🟢
- **Estimación**: 25 minutos
- **Estado**: PENDIENTE
- **Metodología**: Auto-CoT + Self-Consistency

## Descripción
Crear una guía completa de navegación del backend que explique la estructura de carpetas, convenciones, y cómo encontrar diferentes tipos de código y documentación.

## Auto-CoT: Razonamiento Paso a Paso

### Paso 1: Definir Propósito de la Guía
**Pensamiento**: ¿A quién ayuda esta guía y cómo?

**Problemas que Resuelve**:
1. **Orientación**: Desarrolladores nuevos no saben dónde está cada cosa
2. **Descubribilidad**: Difícil encontrar código específico
3. **Convenciones**: No está claro dónde agregar nuevo código
4. **Migración**: Desarrolladores existentes perdidos tras reorganización

**Audiencias**:
- **Desarrollador Nuevo**: Nunca vio el proyecto
- **Desarrollador Transferido**: Conoce un área, explora otra
- **Desarrollador Legacy**: Trabajó en estructura anterior
- **Arquitecto/Lead**: Necesita visión general

### Paso 2: Estructurar la Guía
**Pensamiento**: ¿Qué secciones debe tener?

**Estructura Propuesta**:
1. **Introducción**: Propósito y alcance
2. **Visión General**: Mapa mental de la estructura
3. **Por Carpeta**: Descripción detallada de cada carpeta
4. **Por Caso de Uso**: "Quiero hacer X, ¿dónde voy?"
5. **Por Tipo de Código**: "¿Dónde van los servicios? ¿Los utils?"
6. **Convenciones**: Reglas para agregar nuevo código
7. **Mapeo Legacy**: Dónde está ahora lo que estaba antes
8. **FAQ**: Preguntas frecuentes

### Paso 3: Recopilar Contenido
**Pensamiento**: ¿Qué información incluir?

**Información por Carpeta**:
- Nombre y propósito
- Qué contiene (tipos de archivos)
- Qué NO contiene (límites claros)
- Ejemplos de contenido
- Cuándo usar esta carpeta
- Enlaces a READMEs específicos

**Información de Navegación**:
- Estructura de árbol visual
- Índice de carpetas con enlaces
- Rutas comunes de acceso rápido
- Atajos y trucos

### Paso 4: Hacer la Guía Accionable
**Pensamiento**: ¿Cómo facilitar el uso?

**Elementos Interactivos**:
- Índice con enlaces ancla
- Secciones "Búsqueda Rápida"
- Tablas de decisión
- Ejemplos concretos
- Comandos útiles

## Self-Consistency: Validación Múltiple

### Enfoque 1: Guía Orientada por Estructura
```markdown
# Guía de Navegación - Backend

## Estructura de Carpetas

### core/
**Propósito**: Servicios fundamentales del sistema
**Contiene**: Auth, Database, Config, Logging, Cache
**Cuándo usar**: Funcionalidad core compartida por todo el sistema

### packages/
**Propósito**: Paquetes reutilizables
**Contiene**: Librerías, utilities, validators
**Cuándo usar**: Código compartido sin dependencias del sistema

[... continuar por cada carpeta ...]
```

### Enfoque 2: Guía Orientada por Tareas
```markdown
# Guía de Navegación - Backend

## Búsqueda por Tarea

### Quiero implementar autenticación
→ Ve a `core/auth/`
→ Lee `core/auth/README.md`
→ Sigue ejemplos en `core/auth/examples/`

### Quiero crear una API REST
→ Ve a `services/api/`
→ Revisa `services/api/TEMPLATE.md`
→ Sigue convenciones en `docs/API_CONVENTIONS.md`

### Quiero agregar una utilidad compartida
→ Si es genérica: `packages/utils/`
→ Si es específica del dominio: `utils/`
→ Sigue naming en `TASK-058-validar-nomenclatura/`

[... continuar por casos de uso ...]
```

### Enfoque 3: Guía de Mapeo Legacy
```markdown
# Guía de Navegación - Backend

## Mapeo de Estructura Anterior

| Ubicación Antigua | Ubicación Nueva | Notas |
|-------------------|-----------------|-------|
| `old-auth/` | `core/auth/` | Renombrado y reorganizado |
| `utils-shared/` | `packages/utils/` | Movido a packages |
| `api-v1/` | `services/api/v1/` | Bajo services |

Ver mapeo completo en TASK-053/054
```

### Convergencia de Resultados
- Combinar los 3 enfoques en una guía comprehensiva
- Estructura principal + Sección de búsqueda rápida + Mapeo legacy
- Validar que cubre todos los casos de uso comunes

## Criterios de Aceptación
- [ ] Guía creada en docs/backend/docs/GUIA_NAVEGACION_BACKEND.md
- [ ] Todas las carpetas principales documentadas
- [ ] Sección de búsqueda rápida por tarea
- [ ] Mapeo de legacy a nueva estructura
- [ ] Convenciones claramente explicadas
- [ ] Ejemplos concretos incluidos
- [ ] Comandos útiles documentados
- [ ] FAQ con preguntas comunes
- [ ] Índice navegable
- [ ] Validada por al menos 1 desarrollador

## Entregables
1. **docs/backend/docs/GUIA_NAVEGACION_BACKEND.md**
   - Guía completa de navegación
   - Múltiples formas de búsqueda
   - Ejemplos prácticos

2. **RESUMEN-ESTRUCTURA-BACKEND.md** (Opcional)
   - Versión condensada de 1 página
   - Quick reference
   - Para imprimir/compartir

## Template GUIA_NAVEGACION_BACKEND.md

```markdown
# Guía de Navegación - Backend del Sistema IACT

> Guía completa para navegar y entender la estructura del backend.
> Última actualización: 2025-11-18

## Tabla de Contenidos

- [Introducción](#introducción)
- [Visión General](#visión-general)
- [Búsqueda Rápida](#búsqueda-rápida)
- [Estructura Detallada](#estructura-detallada)
- [Convenciones](#convenciones)
- [Mapeo Legacy](#mapeo-legacy)
- [FAQ](#faq)
- [Recursos](#recursos)

---

## Introducción

### Propósito de Esta Guía

Esta guía te ayudará a:
- 🧭 **Orientarte** en la estructura del backend
- 🔍 **Encontrar** código y documentación específica
- ➕ **Agregar** nuevo código en el lugar correcto
- 🗺️ **Mapear** código legacy a nueva ubicación
- 📚 **Aprender** convenciones y mejores prácticas

### Audiencia

- **Nuevo en el proyecto**: Lee [Visión General](#visión-general) → [Búsqueda Rápida](#búsqueda-rápida)
- **Migrando desde legacy**: Ve directo a [Mapeo Legacy](#mapeo-legacy)
- **Agregando código nuevo**: Lee [Convenciones](#convenciones)
- **Explorando el sistema**: Usa [Estructura Detallada](#estructura-detallada)

---

## Visión General

### Mapa Mental de la Estructura

```
docs/backend/
│
├── 🏗️ core/              Servicios fundamentales del sistema
│   ├── auth/             Autenticación y autorización
│   ├── database/         Gestión de base de datos
│   ├── config/           Configuración del sistema
│   └── logging/          Logging centralizado
│
├── 📦 packages/          Paquetes reutilizables (sin deps del sistema)
│   ├── utils/            Utilidades generales
│   ├── validators/       Validadores compartidos
│   └── helpers/          Funciones helper
│
├── 🧩 components/        Componentes modulares del backend
│   ├── email/            Gestión de emails
│   ├── notifications/    Sistema de notificaciones
│   └── file-storage/     Almacenamiento de archivos
│
├── 🚀 services/          Microservicios y APIs
│   ├── api/              APIs REST
│   ├── graphql/          API GraphQL
│   └── jobs/             Background jobs
│
├── 🔧 utils/             Utilidades específicas del dominio
│   ├── scripts/          Scripts de automatización
│   └── helpers/          Helpers del sistema
│
├── ⚙️ config/            Configuraciones del proyecto
│   ├── environments/     Configs por ambiente
│   └── docker/           Docker configs
│
├── 📚 docs/              Documentación técnica
│   ├── arquitectura/     Docs de arquitectura
│   ├── guias/            Guías y tutoriales
│   └── api/              Documentación de APIs
│
├── 🧪 tests/             Tests de integración
│   ├── integration/      Tests de integración
│   └── e2e/              Tests end-to-end
│
├── 📋 gobernanza/        Políticas y procesos
│   ├── standards/        Estándares de código
│   └── processes/        Procesos de desarrollo
│
└── 🗂️ legacy/            Código legacy (temporal)
    └── [proyectos]       A migrar o deprecar
```

### Principios de Organización

1. **Modularidad**: Código organizado por función, no por tipo
2. **Separación de Concerns**: Cada carpeta tiene responsabilidad única
3. **Escalabilidad**: Estructura crece sin reorganización
4. **Descubribilidad**: Nombres claros y estructura lógica

---

## Búsqueda Rápida

### Por Tarea: "Quiero..."

#### ...implementar autenticación
```
📁 core/auth/
├── README.md          ← Empieza aquí
├── strategies/        ← Estrategias de auth (JWT, OAuth, etc.)
├── middleware/        ← Middlewares de autenticación
└── examples/          ← Ejemplos de uso
```

#### ...crear una nueva API
```
📁 services/api/
├── README.md          ← Guía de APIs
├── TEMPLATE.md        ← Template para nueva API
├── v1/                ← APIs versión 1
└── v2/                ← APIs versión 2
```

#### ...agregar una utilidad compartida
```
¿Es genérica (sin deps del sistema)?
  → packages/utils/

¿Es específica del dominio?
  → utils/

¿Es parte de un componente?
  → components/[nombre]/utils/
```

#### ...configurar un nuevo ambiente
```
📁 config/
├── environments/
│   ├── development.yml
│   ├── staging.yml
│   └── production.yml
└── README.md          ← Guía de configuración
```

#### ...escribir tests de integración
```
📁 tests/
├── integration/
│   └── [nombre-del-test]/
├── e2e/
│   └── [escenario]/
└── README.md          ← Guía de testing
```

#### ...trabajar con base de datos
```
📁 core/database/
├── README.md          ← Overview
├── schemas/           ← Definiciones de esquemas
├── migrations/        ← Migraciones
├── seeders/           ← Datos de prueba
└── queries/           ← Queries comunes
```

### Por Tipo de Archivo

| Busco... | Ubicación | Ejemplo |
|----------|-----------|---------|
| Servicio Core | `core/[nombre]/` | `core/auth/authService.js` |
| Paquete Reutilizable | `packages/[nombre]/` | `packages/utils/dateUtils.js` |
| Componente | `components/[nombre]/` | `components/email/emailService.js` |
| API Endpoint | `services/api/v[X]/` | `services/api/v1/users.js` |
| Config | `config/` | `config/database.yml` |
| Documentación | `docs/` | `docs/arquitectura/overview.md` |
| Tests | `tests/` | `tests/integration/auth-test.js` |
| Scripts | `utils/scripts/` | `utils/scripts/setup.sh` |

### Por Tecnología

| Tecnología | Ubicación Principal |
|------------|---------------------|
| Node.js/Express | `services/api/` |
| GraphQL | `services/graphql/` |
| Database (SQL) | `core/database/` |
| Redis/Cache | `core/cache/` |
| Docker | `config/docker/` |
| CI/CD | `.github/` o `config/ci/` |

---

## Estructura Detallada

### 🏗️ core/

**Propósito**: Servicios fundamentales que todo el sistema necesita.

**Características**:
- Funcionalidad crítica del sistema
- Alta cohesión, bajo acoplamiento
- Reutilizado por múltiples servicios
- Difícil de reemplazar sin impacto mayor

**Subcarpetas**:

#### core/auth/
- **Qué**: Autenticación y autorización
- **Contiene**: Strategies, middleware, tokens, permisos
- **Ejemplos**: JWT auth, OAuth, RBAC
- **Cuándo usar**: Implementar login, proteger rutas, verificar permisos

#### core/database/
- **Qué**: Gestión de conexiones y operaciones de BD
- **Contiene**: Conexiones, modelos, migraciones, queries
- **Ejemplos**: Connection pools, ORM config, migrations
- **Cuándo usar**: Configurar BD, crear modelos, ejecutar migraciones

#### core/config/
- **Qué**: Configuración centralizada del sistema
- **Contiene**: Parsers de config, validadores, defaults
- **Ejemplos**: Leer .env, validar configs, configuración por ambiente
- **Cuándo usar**: Gestionar configuración de la aplicación

#### core/logging/
- **Qué**: Sistema de logging centralizado
- **Contiene**: Loggers, formatters, transports
- **Ejemplos**: Winston config, log levels, log rotation
- **Cuándo usar**: Implementar logging en servicios

---

### 📦 packages/

**Propósito**: Código reutilizable sin dependencias del sistema.

**Características**:
- Sin dependencias de `core/` o `services/`
- Potencialmente extraíble a npm package
- Genérico y reutilizable
- Bien testeado y documentado

**Cuándo usar**:
- ✅ Funciones puras o utilidades genéricas
- ✅ Validadores sin lógica de negocio
- ✅ Helpers matemáticos o de string
- ❌ Código que depende de autenticación
- ❌ Código que usa modelos del sistema
- ❌ Lógica de negocio específica

**Subcarpetas**:
- `utils/` - Utilidades generales
- `validators/` - Validadores genéricos
- `helpers/` - Funciones helper
- `constants/` - Constantes compartidas

---

### 🧩 components/

**Propósito**: Componentes modulares con funcionalidad específica.

**Características**:
- Responsabilidad única y clara
- Puede depender de `core/` y `packages/`
- No depende de otros components
- Intercambiable y reemplazable

**Ejemplos de Componentes**:
- `email/` - Gestión de envío de emails
- `notifications/` - Sistema de notificaciones
- `file-storage/` - Almacenamiento de archivos
- `search/` - Funcionalidad de búsqueda
- `analytics/` - Tracking y analytics

**Estructura de un Componente**:
```
components/email/
├── README.md
├── emailService.js       # Servicio principal
├── templates/            # Templates de email
├── providers/            # Providers (SendGrid, SES, etc.)
├── utils/                # Utils específicos del componente
└── tests/                # Tests del componente
```

---

### 🚀 services/

**Propósito**: Microservicios y servicios independientes.

**Características**:
- Puede ser deployado independientemente
- Tiene su propia API
- Puede depender de core y components
- Escalable horizontalmente

**Subcarpetas**:

#### services/api/
- APIs REST organizadas por versión
- Endpoints, controllers, middleware
- Documentación de API (Swagger/OpenAPI)

#### services/graphql/
- API GraphQL
- Schemas, resolvers, directives

#### services/jobs/
- Background jobs y cron tasks
- Workers, schedulers, queues

---

### 🔧 utils/

**Propósito**: Utilidades específicas del sistema.

**Diferencia con packages/**:
- `packages/utils/`: Genérico, sin deps del sistema
- `utils/`: Específico del dominio, puede usar core/

**Contiene**:
- Scripts de automatización
- Helpers que usan lógica del sistema
- Tools y CLI internos

---

### ⚙️ config/

**Propósito**: Archivos de configuración del proyecto.

**Contiene**:
- `environments/` - Configs por ambiente (dev, staging, prod)
- `docker/` - Docker y docker-compose configs
- Archivos de configuración de herramientas

---

### 📚 docs/

**Propósito**: Documentación técnica y arquitectónica.

**Estructura**:
```
docs/
├── arquitectura/         # Docs de arquitectura
│   ├── OVERVIEW.md       # Visión general
│   ├── PATTERNS.md       # Patrones usados
│   └── adr/              # Architecture Decision Records
├── guias/                # Guías y tutoriales
│   ├── DESARROLLO.md     # Guía de desarrollo
│   ├── DEPLOYMENT.md     # Guía de deployment
│   └── TESTING.md        # Guía de testing
├── api/                  # Documentación de APIs
└── GUIA_NAVEGACION_BACKEND.md  # Esta guía
```

---

### 🧪 tests/

**Propósito**: Tests de integración y end-to-end.

**Nota**: Tests unitarios van junto al código que testean.

**Estructura**:
- `integration/` - Tests de integración entre componentes
- `e2e/` - Tests end-to-end de flujos completos
- `fixtures/` - Datos de prueba compartidos

---

### 📋 gobernanza/

**Propósito**: Políticas, procesos y estándares.

**Contiene**:
- Estándares de código
- Procesos de review
- Políticas de seguridad
- SLAs y métricas

---

### 🗂️ legacy/

**Propósito**: Código legacy temporal durante migración.

**Estado**: A deprecar gradualmente

**Contiene**: Proyectos antiguos no migrados aún

---

## Convenciones

### Nomenclatura

#### Carpetas
- **Formato**: `kebab-case`
- **Ejemplos**: `user-management`, `api-gateway`
- ❌ **Evitar**: `UserManagement`, `user_management`, `user management`

#### Archivos JavaScript/TypeScript
- **Formato**: `camelCase.js` o `PascalCase.js` (para clases)
- **Ejemplos**: `userService.js`, `AuthController.js`

#### Archivos Python
- **Formato**: `snake_case.py`
- **Ejemplos**: `user_service.py`, `auth_controller.py`

#### Documentación
- **README**: `README.md` (uppercase)
- **Guías**: `kebab-case.md` o `SCREAMING_CASE.md`
- **Ejemplos**: `guia-rapida.md`, `CHANGELOG.md`

### Dónde Agregar Código Nuevo

#### Diagrama de Decisión

```
¿Qué estoy creando?

├─ ¿Es funcionalidad CORE del sistema?
│  └─ SÍ → core/[nombre]/
│
├─ ¿Es código GENÉRICO reutilizable?
│  └─ SÍ → packages/[nombre]/
│
├─ ¿Es un COMPONENTE con responsabilidad única?
│  └─ SÍ → components/[nombre]/
│
├─ ¿Es un SERVICIO/API independiente?
│  └─ SÍ → services/[nombre]/
│
├─ ¿Es una UTILIDAD específica del dominio?
│  └─ SÍ → utils/[nombre]/
│
└─ ¿No estás seguro?
   └─ Pregunta al equipo de arquitectura
```

### Estructura de un Nuevo Módulo

```
[carpeta-nombre]/
├── README.md              # Documentación del módulo
├── index.js               # Entry point (exports principales)
├── [nombre]Service.js     # Servicio principal
├── [nombre]Controller.js  # Controller (si aplica)
├── [nombre]Model.js       # Modelo de datos (si aplica)
├── middleware/            # Middlewares del módulo
├── utils/                 # Utilidades específicas
├── tests/                 # Tests unitarios
│   ├── [nombre].test.js
│   └── fixtures/
└── docs/                  # Documentación adicional (opcional)
```

### Imports y Dependencias

```javascript
// ✅ CORRECTO: Orden de imports
// 1. Node.js built-ins
const fs = require('fs');
const path = require('path');

// 2. External dependencies
const express = require('express');
const _ = require('lodash');

// 3. Internal core
const { auth } = require('@core/auth');
const db = require('@core/database');

// 4. Internal packages
const { validateEmail } = require('@packages/validators');

// 5. Local modules
const userService = require('./userService');
const { helper } = require('./utils/helper');
```

---

## Mapeo Legacy

### Tabla de Mapeo: Dónde Está Ahora

| Ubicación Anterior | Ubicación Nueva | Tipo | Notas |
|--------------------|-----------------|------|-------|
| `old-auth-system/` | `core/auth/` | Core Service | Refactorizado |
| `shared-utils/` | `packages/utils/` | Package | Sin cambios mayores |
| `email-sender/` | `components/email/` | Component | Renombrado |
| `api-v1/` | `services/api/v1/` | Service | Movido bajo services |
| `database-layer/` | `core/database/` | Core Service | Reorganizado |
| `config-files/` | `config/` | Config | Consolidado |
| `docs-old/` | `docs/` | Documentation | Actualizado |
| `test-integration/` | `tests/integration/` | Tests | Reestructurado |

### Proyectos Legacy Específicos

**Ver mapeo detallado en**:
- [TASK-053: Migración Legacy Prioridad Alta](../qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/TASK-053-migracion-legacy-alta/)
- [TASK-054: Migración Legacy Prioridad Media](../qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/TASK-054-migracion-legacy-media/)

### ¿Mi código no está migrado?

1. **Busca en `legacy/`**: Puede estar ahí temporalmente
2. **Consulta el plan**: Ver `qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/PLAN-REORGANIZACION-ESTRUCTURA-BACKEND-2025-11-18.md`
3. **Pregunta al equipo**: Puede estar en progreso de migración

---

## FAQ

### ¿Dónde va mi código?

**P**: ¿Dónde pongo un nuevo endpoint de API?
**R**: `services/api/v[X]/[recurso].js`

**P**: ¿Dónde pongo una función helper genérica?
**R**: Si es genérica (sin deps): `packages/utils/`. Si usa lógica del sistema: `utils/`

**P**: ¿Dónde pongo un servicio de envío de SMS?
**R**: `components/sms/` (componente con responsabilidad única)

**P**: ¿Dónde pongo un background job?
**R**: `services/jobs/[nombre-job]/`

### ¿Cómo encuentro código?

**P**: No encuentro el código de autenticación legacy
**R**: Ahora está en `core/auth/`. Ver [Mapeo Legacy](#mapeo-legacy)

**P**: ¿Cómo busco todos los servicios?
**R**: `find docs/backend -name "*Service.js"` o busca en `services/` y `core/`

**P**: ¿Dónde está la documentación de arquitectura?
**R**: `docs/arquitectura/`

### ¿Convenciones?

**P**: ¿Uso camelCase o kebab-case para carpetas?
**R**: Siempre `kebab-case` para carpetas

**P**: ¿Cómo nombro un archivo de servicio?
**R**: `[nombre]Service.js` en camelCase

**P**: ¿Necesito README en cada carpeta?
**R**: Sí en carpetas principales (core, packages, components, services). Opcional en subcarpetas.

### ¿Proceso?

**P**: ¿Puedo crear una carpeta nueva en core/?
**R**: Discutir con equipo de arquitectura primero. Core es para funcionalidad fundamental.

**P**: ¿Debo migrar código legacy yo mismo?
**R**: Ver plan de migración. Si no está asignado, coordinar con el equipo.

**P**: ¿Los tests van junto al código?
**R**: Tests unitarios sí. Tests de integración en `tests/integration/`

---

## Recursos

### Documentación Relacionada
- [README Principal](../README.md)
- [INDEX de Documentación](../INDEX.md)
- [CHANGELOG](../CHANGELOG.md)
- [Plan de Reorganización](../qa/QA-ANALISIS-ESTRUCTURA-BACKEND-001/PLAN-REORGANIZACION-ESTRUCTURA-BACKEND-2025-11-18.md)

### Herramientas Útiles

#### Comandos de Navegación
```bash
# Ver estructura de árbol
tree docs/backend -L 3

# Buscar archivos por nombre
find docs/backend -name "*Service.js"

# Buscar en contenido
grep -r "auth" docs/backend --include="*.js"

# Contar archivos por tipo
find docs/backend -name "*.js" | wc -l
```

#### Scripts Disponibles
- `utils/scripts/validate-structure.sh` - Validar estructura
- `utils/scripts/find-legacy.sh` - Encontrar código legacy
- `utils/scripts/generate-tree.sh` - Generar árbol de estructura

### Contacto

¿Preguntas no respondidas?
- 💬 Canal de Slack: #backend-architecture
- 📧 Email: architecture@team.com
- 📝 Issue Tracker: [GitHub Issues](#)

---

**Última actualización**: 2025-11-18
**Versión**: 2.0.0
**Mantenida por**: Equipo de Arquitectura Backend
```

## Comandos Útiles

### Generar estructura de árbol
```bash
tree docs/backend -L 3 -d > estructura.txt
```

### Encontrar todos los READMEs
```bash
find docs/backend -name "README.md" | sort
```

### Contar archivos por carpeta
```bash
for dir in docs/backend/*/; do
  echo "$(basename $dir): $(find $dir -type f | wc -l) archivos"
done
```

## Checklist de Revisión

### Contenido
- [ ] Visión general clara
- [ ] Todas las carpetas principales documentadas
- [ ] Búsqueda rápida por tarea
- [ ] Búsqueda por tipo de archivo
- [ ] Convenciones de nomenclatura
- [ ] Guía "dónde agregar código"
- [ ] Mapeo legacy a nueva estructura
- [ ] FAQ con preguntas comunes

### Usabilidad
- [ ] Tabla de contenidos navegable
- [ ] Ejemplos concretos
- [ ] Comandos útiles incluidos
- [ ] Diagramas de decisión
- [ ] Enlaces a documentación relacionada

### Formato
- [ ] Markdown válido
- [ ] Encabezados bien jerarquizados
- [ ] Emojis para navegación visual
- [ ] Bloques de código con sintaxis
- [ ] Tablas correctamente formateadas

## Prioridades

### MUST HAVE
- Visión general de estructura
- Descripción de cada carpeta principal
- Convenciones de nomenclatura
- Guía "dónde agregar código"

### SHOULD HAVE
- Búsqueda rápida por tarea
- Mapeo legacy
- FAQ
- Ejemplos concretos

### NICE TO HAVE
- Diagramas visuales
- Scripts interactivos
- Videos/GIFs demostrativos

## Dependencias
- TASK-002: Estructura de carpetas creada
- TASK-053/054: Migraciones completadas (para mapeo)
- TASK-058: Convenciones de nomenclatura definidas

## Notas
- Esta guía es documento vivo, actualizar cuando estructura cambie
- Solicitar feedback de desarrolladores nuevos para mejorar
- Considerar versión interactiva (web) en el futuro
- Mantener sincronizada con README e INDEX

## Referencias
- [Docs as Code](https://www.writethedocs.org/guide/docs-as-code/)
- [Documentation Guide](https://www.divio.com/blog/documentation/)
- Auto-CoT: Wei et al. (2022)
- Self-Consistency: Wang et al. (2022)
