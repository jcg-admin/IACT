---
id: ADR-GOB-010
tipo: adr
titulo: Gobernanza Multi-nivel (Global y por Dominio)
estado: aprobado
fecha_creacion: 2025-01-17
autores: [Sistema]
revisores: []
relacionado_con: [ADR-GOB-001, ADR-GOB-002]
---

# ADR-GOB-010: Gobernanza Multi-nivel (Global y por Dominio)

## Contexto

El proyecto IACT tiene múltiples dominios técnicos (backend, frontend, infraestructura, etc.) que requieren tomar decisiones arquitectónicas y de diseño específicas a su contexto. Sin embargo, también existen decisiones que afectan a todo el proyecto y deben ser consistentes entre dominios.

### Problemas Identificados

1. **Duplicación de documentación**: Templates y guías se duplican entre dominios
2. **Inconsistencias**: Decisiones globales se implementan diferente en cada dominio
3. **Falta de claridad**: No está claro qué decisiones son globales vs específicas
4. **Acoplamiento innecesario**: Backend y frontend no pueden evolucionar independientemente

### Ejemplo del Problema

```
❌ ANTES (sin estructura clara):
docs/
├── adr/                    ← ¿Son globales o de backend?
├── templates/              ← ¿Para quién?
└── guias/                  ← ¿Aplican a frontend?

backend/
├── plantillas/             ← Duplicación
└── docs/                   ← Inconsistente

frontend/
├── templates/              ← Duplicación
└── README.md               ← Sin gobernanza clara
```

## Decisión

Adoptar una **arquitectura de gobernanza multi-nivel** con dos niveles claramente definidos:

### Nivel 1: Gobernanza Global (`/docs/gobernanza/`)

Decisiones que afectan a TODO el proyecto IACT.

**Ubicación**: `/docs/gobernanza/`

**Contenido**:
- ADRs globales (nomenclaturas, estándares, metodologías)
- Guías compartidas (requisitos, casos de uso, trazabilidad)
- Procedimientos globales (análisis de impacto, documentación)
- Templates compartidos (plantillas de requisitos, ADRs, etc.)

**Ejemplos de decisiones globales**:
- ADR-GOB-001: Nomenclatura de Archivos
- ADR-GOB-004: PlantUML para Diagramas
- ADR-GOB-005: Jerarquía de Requerimientos
- ADR-GOB-009: Sistema de Trazabilidad

### Nivel 2: Gobernanza por Dominio (`/docs/{dominio}/gobernanza/`)

Decisiones específicas a un dominio técnico que NO afectan a otros dominios.

**Ubicación**: `/docs/{dominio}/gobernanza/`

**Dominios identificados**:
- `/docs/backend/gobernanza/`
- `/docs/frontend/gobernanza/`
- (futuros: `/docs/infra/gobernanza/`, `/docs/mobile/gobernanza/`)

**Contenido por dominio**:
- ADRs específicos del dominio
- README.md con enlaces a gobernanza global
- Templates específicos del dominio (si necesarios)
- Guías técnicas específicas del stack

**Ejemplos de decisiones por dominio**:
- Backend: ADR sobre ORM (Django vs SQLAlchemy)
- Backend: ADR sobre estructura de APIs
- Frontend: ADR sobre framework (React vs Vue)
- Frontend: ADR sobre gestión de estado (Redux vs Context)

## Estructura Resultante

```
docs/
├── gobernanza/                          ← NIVEL 1: GLOBAL
│   ├── adr/                            ← ADRs que aplican a TODO el proyecto
│   │   ├── ADR-GOB-001-nomenclatura.md
│   │   ├── ADR-GOB-004-plantuml.md
│   │   └── ...
│   ├── guias/                          ← Guías compartidas
│   │   ├── GUIA-GOB-005-derivar-requisitos.md
│   │   └── ...
│   ├── procedimientos/                 ← Procedimientos globales
│   │   ├── PROCED-GOB-003-documentar-regla-negocio.md
│   │   └── ...
│   ├── templates/                      ← Templates compartidos
│   │   ├── RN-template.md
│   │   ├── UC-template-completo.md
│   │   └── ...
│   ├── diseno/                         ← Diseño global
│   │   ├── arquitectura/
│   │   └── diagramas/
│   └── requisitos/                     ← Requisitos del proyecto
│
├── backend/
│   ├── gobernanza/                     ← NIVEL 2: BACKEND
│   │   ├── README.md                   ← "Ver /docs/gobernanza/ para estándares globales"
│   │   ├── adr/                        ← ADRs específicos backend
│   │   │   ├── ADR-BACK-001-django-orm.md
│   │   │   └── ADR-BACK-002-api-versioning.md
│   │   └── templates/                  ← Solo si son ESPECÍFICOS backend
│   └── requisitos/                     ← Requisitos backend
│
└── frontend/
    ├── gobernanza/                     ← NIVEL 2: FRONTEND
    │   ├── README.md                   ← "Ver /docs/gobernanza/ para estándares globales"
    │   ├── adr/                        ← ADRs específicos frontend
    │   │   ├── ADR-FRONT-001-react-framework.md
    │   │   └── ADR-FRONT-002-state-management.md
    │   └── templates/                  ← Solo si son ESPECÍFICOS frontend
    └── requisitos/                     ← Requisitos frontend
```

## Principios de Separación

### ¿Cuándo es una decisión GLOBAL?

Una decisión es global si cumple **al menos uno** de estos criterios:

1. **Afecta a múltiples dominios**: Backend + Frontend deben seguirla
2. **Define estándares de proyecto**: Nomenclaturas, formatos, metodologías
3. **Garantiza interoperabilidad**: Contratos entre dominios
4. **Trazabilidad y gobernanza**: Requisitos, auditoría, compliance

**Ejemplos**:
- ✅ Nomenclatura de archivos (todos los dominios)
- ✅ Jerarquía de requisitos (afecta análisis de negocio)
- ✅ Sistema de trazabilidad (cross-cutting)
- ✅ PlantUML para diagramas (estándar de documentación)

### ¿Cuándo es una decisión POR DOMINIO?

Una decisión es específica del dominio si cumple **todos** estos criterios:

1. **Solo afecta a un dominio**: Implementación interna
2. **No rompe interoperabilidad**: Puede cambiar sin afectar otros
3. **Stack-specific**: Depende de tecnologías del dominio

**Ejemplos**:
- ✅ Backend: Elegir entre Django ORM vs SQLAlchemy
- ✅ Backend: Estructura de carpetas de apps Django
- ✅ Frontend: React vs Vue (no afecta backend)
- ✅ Frontend: Estructura de componentes

## Flujo de Trabajo

### 1. Crear una Decisión Global

```bash
# 1. Crear ADR en /docs/gobernanza/adr/
cd /docs/gobernanza/adr/
cp ADR-TEMPLATE.md ADR-GOB-011-nueva-decision.md

# 2. Documentar decisión siguiendo formato
vim ADR-GOB-011-nueva-decision.md

# 3. Commit y PR
git add docs/gobernanza/adr/ADR-GOB-011-nueva-decision.md
git commit -m "docs(gobernanza): ADR-GOB-011 sobre X"
```

### 2. Crear una Decisión por Dominio

```bash
# 1. Crear ADR en /docs/{dominio}/gobernanza/adr/
cd /docs/backend/gobernanza/adr/
cp ../../docs/gobernanza/templates/ADR-TEMPLATE.md ADR-BACK-005-nueva-decision.md

# 2. Documentar decisión
vim ADR-BACK-005-nueva-decision.md

# 3. Verificar que NO sea global
# - ¿Afecta a frontend? → Entonces es GLOBAL
# - ¿Define estándar de proyecto? → Entonces es GLOBAL
# - ¿Solo backend? → OK, es dominio

# 4. Commit y PR
git add docs/backend/gobernanza/adr/ADR-BACK-005-nueva-decision.md
git commit -m "docs(backend): ADR-BACK-005 sobre Y"
```

### 3. Consultar Gobernanza (Developer)

```bash
# Desde cualquier dominio:
cat docs/backend/gobernanza/README.md
# → "Para estándares globales, ver /docs/gobernanza/"
# → "ADRs específicos de backend: ver adr/"

# Ver todas las decisiones globales:
ls docs/gobernanza/adr/

# Ver decisiones de mi dominio:
ls docs/backend/gobernanza/adr/
```

## Consecuencias

### Ventajas

1. **Separación clara**: Se sabe inmediatamente si una decisión es global o específica
2. **DRY (Don't Repeat Yourself)**: Templates y guías no se duplican
3. **Autonomía de dominios**: Backend y frontend evolucionan independientemente
4. **Trazabilidad**: Referencias claras entre niveles
5. **Escalabilidad**: Fácil agregar nuevos dominios (mobile, infra, etc.)
6. **Onboarding**: Nuevos developers entienden rápidamente la estructura

### Desventajas

1. **Decisión inicial**: Requiere pensar si algo es global o específico
2. **Dos ubicaciones**: Developers deben consultar dos lugares
3. **Mantenimiento**: Gobernanza global requiere más consenso

### Mitigaciones

1. **README claro**: Cada dominio tiene README que linkea a global
2. **Guías de decisión**: Este ADR define criterios claros
3. **Scripts de validación**: `validar-trazabilidad.sh` verifica consistencia

## Implementación

### Fase 1: Estructura Base (Completado)

- [x] Crear `/docs/gobernanza/` con ADRs, guías, procedimientos, templates
- [x] Consolidar `/docs/gobernanza/diseno/` (arquitectura + diagramas)
- [x] Mover templates de root a `/docs/gobernanza/templates/`
- [x] Mover casos_de_uso a `/docs/gobernanza/requisitos/`

### Fase 2: Gobernanza por Dominio (Siguiente)

- [ ] Crear `/docs/backend/gobernanza/`
  - [ ] `README.md` con enlaces a global
  - [ ] `adr/` (inicialmente vacío)
  - [ ] Migrar ADRs existentes que sean específicos backend
- [ ] Crear `/docs/frontend/gobernanza/`
  - [ ] `README.md` con enlaces a global
  - [ ] `adr/` (inicialmente vacío)
- [ ] Actualizar scripts de validación

### Fase 3: Consolidación (Futuro)

- [ ] Auditar ADRs existentes: ¿son globales o de dominio?
- [ ] Mover ADRs mal ubicados
- [ ] Crear guía de migración para equipo

## Casos de Uso

### Caso 1: Backend necesita elegir ORM

**Pregunta**: ¿Django ORM o SQLAlchemy?

**Análisis**:
- ¿Afecta a frontend? NO (frontend consume APIs REST)
- ¿Define estándar de proyecto? NO (es implementación interna)
- ¿Stack-specific? SÍ (es decisión de Python/Django)

**Decisión**: ADR en `/docs/backend/gobernanza/adr/ADR-BACK-001-django-orm.md`

### Caso 2: Definir formato de respuestas API

**Pregunta**: ¿JSON:API, HAL, o custom?

**Análisis**:
- ¿Afecta a frontend? SÍ (frontend consume las APIs)
- ¿Define estándar de proyecto? SÍ (contrato entre dominios)
- ¿Garantiza interoperabilidad? SÍ

**Decisión**: ADR en `/docs/gobernanza/adr/ADR-GOB-011-formato-api.md`

### Caso 3: Frontend necesita gestor de estado

**Pregunta**: ¿Redux, Context API, o Zustand?

**Análisis**:
- ¿Afecta a backend? NO (es implementación interna del SPA)
- ¿Define estándar de proyecto? NO (solo para React)
- ¿Stack-specific? SÍ (es decisión de React)

**Decisión**: ADR en `/docs/frontend/gobernanza/adr/ADR-FRONT-002-state-management.md`

## Criterios de Éxito

### Métricas

1. **Claridad**: Developers encuentran decisiones en < 2 minutos
2. **Consistencia**: 0 decisiones globales en carpetas de dominio
3. **Autonomía**: Dominios pueden crear ADRs sin bloqueos
4. **DRY**: 0 templates duplicados entre dominios

### Validación

```bash
# Script de validación (futuro):
./scripts/validar-gobernanza.sh

# Verifica:
# - ADRs en ubicación correcta
# - READMEs en cada dominio
# - No duplicación de templates
# - Referencias válidas entre niveles
```

## Referencias

- ADR-GOB-001: Nomenclatura de Archivos (global)
- ADR-GOB-002: Organización de Documentación (global)
- [Thoughtworks: Architecture Decision Records](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
- [Spotify: Architectural Decision Records](https://engineering.atspotify.com/2020/04/when-should-i-write-an-architecture-decision-record/)

## Changelog

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2025-01-17 | Sistema | Creación inicial |

## Notas

### Casos Especiales

**¿Qué pasa si una decisión global necesita adaptación por dominio?**

La decisión **global** define el ESTÁNDAR, cada dominio puede tener un ADR **específico** que documente CÓMO lo implementa.

**Ejemplo**:
- Global: ADR-GOB-004 "Usar PlantUML para diagramas"
- Backend: ADR-BACK-010 "Generar diagramas PlantUML en CI/CD"
- Frontend: ADR-FRONT-008 "Embeber diagramas PlantUML en Storybook"

Ambos dominios SIGUEN el estándar global (PlantUML), pero documentan su implementación específica.

### Evolución

Esta estructura puede evolucionar agregando:
- `/docs/mobile/gobernanza/` (si se crea app móvil)
- `/docs/infra/gobernanza/` (decisiones de Kubernetes, CI/CD, etc.)
- `/docs/data/gobernanza/` (decisiones de pipelines, ETL, etc.)

El principio multi-nivel escala horizontalmente sin modificar la gobernanza global.
