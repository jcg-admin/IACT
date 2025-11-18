---
id: ADR-AI-018-ai-agents-standalone-architecture
estado: aceptada
propietario: equipo-arquitectura
ultima_actualizacion: 2025-11-16
relacionados: ["ADR-048", "ADR-053", "ADR-054", "ADR-055", "ADR-056"]
date: 2025-11-16
---
# ADR-058: AI Agents Framework como Proyecto Standalone

**Estado:** aceptada

**Fecha:** 2025-11-16

**Decisores:** Equipo de arquitectura, Claude Code Agent

**Contexto tecnico:** Full-stack / AI Infrastructure

## Contexto y Problema

El AI Agents Framework (implementado en `scripts/coding/ai/agents/`) y el sistema DORA de metricas necesitan una decision arquitectonica clara sobre su relacion con el proyecto principal Django (callcentersite).

**Preguntas clave:**
- ¿Debe el AI Agents Framework integrarse directamente con Django callcentersite?
- ¿Deben las dependencias del framework agregarse a callcentersite/requirements?
- ¿Como separar las responsabilidades entre el entregable principal y los sistemas de agentes?
- ¿Que impacto tiene esta decision en el deployment y mantenimiento?

**Restricciones actuales:**
- callcentersite es el entregable principal del proyecto
- El framework de agentes tiene propositos de automatizacion y analisis
- DORA metrics requiere independencia del sistema principal
- Los agentes deben poder evolucionar sin afectar callcentersite

## Factores de Decision

- **Separation of Concerns**: Mantener responsabilidades claras entre sistemas
- **Deployment Independence**: Capacidad de desplegar y actualizar independientemente
- **Dependency Management**: Evitar conflictos de dependencias entre proyectos
- **Maintainability**: Facilitar el mantenimiento a largo plazo
- **Scalability**: Permitir escalado independiente de cada sistema
- **Development Velocity**: No bloquear desarrollo del entregable principal
- **Testing**: Tests aislados y no interferentes
- **Production Stability**: No comprometer la estabilidad del sistema principal

## Opciones Consideradas

### Opcion 1: Integracion Completa con Django

**Descripcion:**
Integrar el AI Agents Framework directamente en callcentersite como una Django app, agregando todas las dependencias a requirements/base.txt y exponiendo endpoints via Django REST Framework.

**Pros:**
- OK Acceso directo a modelos Django y ORM
- OK Autenticacion y autorizacion unificadas
- OK Deployment simplificado (un solo sistema)
- OK Compartir configuracion y settings

**Contras:**
- NO Acoplamiento fuerte entre sistemas con propositos diferentes
- NO Conflictos potenciales de dependencias (Pydantic 2.x vs otras deps)
- NO Riesgo de inestabilidad en produccion del sistema principal
- NO Tests mezclados y mayor complejidad de test suite
- NO Imposibilidad de escalar independientemente
- NO Deployment conjunto obliga a coordinar releases
- NO Mayor superficie de ataque de seguridad

### Opcion 2: Proyecto Standalone con API REST Separada

**Descripcion:**
Mantener AI Agents Framework y DORA como proyecto Python standalone completamente separado, con su propia API REST (FastAPI), deployment independiente y base de datos propia si necesario.

**Pros:**
- OK Separation of Concerns completa
- OK Deployment y escalado independiente
- OK Gestion de dependencias aislada
- OK Tests completamente separados
- OK Menor riesgo para sistema principal
- OK Flexibilidad en eleccion de tecnologias
- OK Evolucion independiente de cada sistema
- OK Facilita integracion futura via APIs

**Contras:**
- NO Requiere infraestructura adicional para deployment
- NO Duplicacion potencial de autenticacion
- NO Comunicacion via HTTP/REST (latencia adicional)
- NO Mayor complejidad operacional inicial

### Opcion 3: Hybrid - Standalone Package con Opcional Django Integration

**Descripcion:**
Framework standalone como paquete Python independiente, con modulo opcional de integracion Django que puede instalarse si se necesita.

**Pros:**
- OK Flexibilidad maxima
- OK Uso como biblioteca standalone
- OK Integracion opcional cuando sea necesario

**Contras:**
- NO Mayor complejidad arquitectonica
- NO Dos modos de operacion a mantener
- NO Testing de integracion mas complejo
- NO Documentacion y onboarding mas complejos

## Decision

**Opcion elegida:** "Opcion 2: Proyecto Standalone con API REST Separada"

**Justificacion:**

La decision de mantener AI Agents Framework y DORA como proyecto standalone se basa en:

1. **Claridad de Proposito**: callcentersite es el sistema principal de negocio (call center management), mientras que agentes IA y DORA son sistemas auxiliares de automatizacion y metricas. Sus ciclos de vida y requisitos son fundamentalmente diferentes.

2. **Estabilidad del Entregable Principal**: No arriesgar la estabilidad de callcentersite con dependencias y codigo experimental de agentes IA. El sistema principal debe permanecer estable y predecible.

3. **Independencia Tecnologica**: El framework de agentes puede evolucionar libremente, adoptar nuevas tecnologias (ej: Pydantic 2.x, diferentes LLM providers) sin afectar al sistema principal.

4. **Testing y CI/CD Separados**: Tests del framework (140 tests) no interfieren con tests de callcentersite. Pipelines CI/CD independientes permiten releases desacoplados.

5. **Escalabilidad Futura**: Los agentes IA pueden requerir recursos computacionales significativos. Tener deployment separado permite escalar horizontalmente solo el componente de agentes.

**Trade-offs aceptados:**
- Aceptamos la complejidad adicional de mantener dos proyectos separados
- Aceptamos la necesidad de infraestructura adicional para deployment
- Aceptamos latencia de comunicacion HTTP/REST entre sistemas (si fuera necesario)

## Consecuencias

### Positivas

- OK callcentersite permanece limpio, enfocado y estable
- OK Framework de agentes puede evolucionar rapidamente sin restricciones
- OK Tests completamente aislados (140 tests agentes + tests callcentersite)
- OK Deployment independiente permite releases frecuentes del framework
- OK Menor superficie de ataque: agentes y sistema principal separados
- OK Facilita contribuciones: equipos pueden trabajar independientemente
- OK Documentacion clara: docs/agents/ vs documentacion callcentersite
- OK Reutilizacion: framework puede usarse en otros proyectos Python

### Negativas

- WARNING Requiere infraestructura adicional para deployment del framework
- WARNING Comunicacion entre sistemas via HTTP/REST si fuera necesario
- WARNING Dos codebases a mantener con sus respectivos CI/CD
- WARNING Autenticacion y autorizacion deben manejarse separadamente

### Neutrales

- INFO Framework ubicado en scripts/coding/ai/agents/ (separado de callcentersite/)
- INFO Tests ubicados en scripts/coding/tests/test_agents/ (separados)
- INFO Documentacion en docs/agents/ (espejo en scripts/coding/ai/agents/)
- INFO Requirements propios del framework (no en callcentersite/requirements/)

## Plan de Implementacion

**Estado Actual: COMPLETADO** (v1.0.0 - 2025-11-16)

### Fase 1: Estructura Base (COMPLETADO)
- [x] Crear estructura de directorios en scripts/coding/ai/agents/
- [x] Definir modelos Pydantic para planning, protocols, ux, security
- [x] Separar completamente de callcentersite/
- [x] Timeframe: Completado

### Fase 2: Implementacion Core (COMPLETADO)
- [x] Implementar 4 modulos principales (Planning, Protocols, UX, Security)
- [x] Crear 140 tests con 92% coverage
- [x] Establecer estructura de tests en scripts/coding/tests/test_agents/
- [x] Timeframe: Completado

### Fase 3: Documentacion y CI/CD (COMPLETADO)
- [x] Crear documentacion completa en docs/agents/
- [x] Configurar GitHub Actions workflow (agents-ci.yml)
- [x] Pre-commit hooks configurados
- [x] Timeframe: Completado

### Fase 4: Integracion (FUTURO - v1.1.0+)
- [ ] Definir API REST si se necesita comunicacion con callcentersite
- [ ] Implementar autenticacion/autorizacion independiente
- [ ] Configurar deployment separado
- [ ] Timeframe: Pendiente segun necesidades

## Validacion y Metricas

**Criterios de Exito:**
- Metrica 1: 0 dependencias del framework en callcentersite/requirements - CUMPLIDO
- Metrica 2: 140 tests del framework pasan independientemente - CUMPLIDO (0.55s)
- Metrica 3: Coverage >90% del framework - CUMPLIDO (92%)
- Metrica 4: CI/CD separado configurado - CUMPLIDO (agents-ci.yml)
- Metrica 5: Documentacion completa standalone - CUMPLIDO (13 archivos, 12,100 lineas)

**Como medir:**
- pytest scripts/coding/tests/test_agents/ para verificar independencia de tests
- grep -r "from.*callcentersite" scripts/coding/ai/agents/ debe retornar vacio
- GitHub Actions workflow separado debe ejecutarse sin dependencias de Django

**Revision:**
- Fecha de revision programada: 2026-01-16 (2 meses post-v1.0.0)
- Responsable de seguimiento: Equipo de arquitectura

## Estructura de Directorios

```
IACT---project/
├── api/callcentersite/              # Sistema principal Django (ENTREGABLE)
│   ├── requirements/
│   │   ├── base.txt                 # NO incluye deps del framework
│   │   ├── dev.txt
│   │   └── test.txt
│   └── ...
│
├── scripts/coding/ai/agents/        # AI Agents Framework (STANDALONE)
│   ├── planning/                    # Modulo de planificacion
│   ├── protocols/                   # MCP, A2A, NLWeb
│   ├── ux/                         # Transparency, Control, Consistency
│   ├── security/                   # Threat detection, HITL, Audit
│   ├── README.md                   # Documentacion principal
│   ├── INTEGRATION.md              # Patrones de integracion
│   ├── API_REFERENCE.md            # API completa
│   └── .pre-commit-config.yaml     # Hooks propios
│
├── scripts/coding/tests/test_agents/ # Tests del framework (SEPARADOS)
│   ├── test_planning/              # 40 tests
│   ├── test_protocols/             # 60 tests
│   ├── test_ux/                    # 20 tests
│   └── test_security/              # 20 tests
│
├── docs/agents/                     # Documentacion del framework
│   ├── README.md
│   ├── INTEGRATION.md
│   ├── API_REFERENCE.md
│   ├── EXAMPLES.md
│   ├── ARCHITECTURE.md
│   ├── CONTRIBUTING.md
│   ├── CHANGELOG.md
│   └── DOCUMENTATION_INDEX.md
│
└── .github/workflows/
    ├── backend-ci.yml              # CI/CD callcentersite
    └── agents-ci.yml               # CI/CD framework (SEPARADO)
```

## Dependencias Independientes

**Framework de Agentes (NO en callcentersite):**
```txt
# Dependencias propias del framework
pydantic>=2.5.0          # Modelos de datos
pytest>=7.4.0            # Testing
pytest-cov>=4.1.0        # Coverage
# Futuras: openai, anthropic, etc.
```

**callcentersite (SIN dependencias del framework):**
```txt
# Mantiene sus propias dependencias Django
Django>=4.2
djangorestframework
psycopg2-binary
# etc.
```

## Comunicacion Entre Sistemas

**Principio:** Loose Coupling via APIs (si es necesario)

Opciones para comunicacion futura:
1. **HTTP REST**: callcentersite consulta API del framework via HTTP
2. **Message Queue**: Comunicacion asincrona via RabbitMQ/Redis
3. **Shared Database**: Schema separado, queries read-only desde callcentersite
4. **File-based**: Framework genera reportes que callcentersite consume

**Recomendacion actual:** Evitar comunicacion directa. Framework opera independientemente. Si se necesita integracion, usar HTTP REST con autenticacion JWT.

## Referencias

- [ADR-048: AI Agent Memory Architecture](ADR-048-ai-agent-memory-architecture.md)
- [ADR-053: Multi-Agent Design Patterns](ADR-053-multi-agent-design-patterns.md)
- [ADR-054: Planning Architecture](ADR-054-planning-architecture.md)
- [ADR-055: Agent Protocols Architecture](ADR-055-agent-protocols-architecture.md)
- [AI Agents Framework README](../../agents/README.md)
- [AI Agents Framework Architecture](../../agents/ARCHITECTURE.md)
- [GitHub Actions Workflow](../../../.github/workflows/agents-ci.yml)
- [Branch: claude/safe-integration-01PNuXsNnT4QMuKC6AXWJLFC](https://github.com/2-Coatl/IACT---project)

## Notas Adicionales

**Fecha de implementacion completa:** 2025-11-16
**Version del framework:** v1.0.0
**Coverage de tests:** 92% (140/140 tests passing)
**Tiempo de ejecucion tests:** 0.55s
**Documentacion:** 13 archivos, ~12,100 lineas

**Decisiones tecnicas relacionadas:**
- Python 3.11+ como version minima del framework
- Pydantic 2.x para validacion de datos (incompatible con algunas deps Django)
- pytest como framework de testing (no Django TestCase)
- Ruff como linter y formatter
- MyPy para type checking
- Bandit para security scanning

**Commits relevantes:**
- `fe7f7dc3`: feat(agents): COMPLETE 140/140 tests implementation
- `cdc15ffc`: docs(agents): add comprehensive documentation and CI/CD workflow
- `e50e4724`: docs(agents): add project governance and development tools
- `e2a4e35b`: docs(agents): add documentation hub and index

---

**DECISION FINAL:**

`iact_agents/` = Proyecto Python STANDALONE (separado de callcentersite)
DORA + Agentes = Proyecto aparte del entregable principal
NO integrar con Django REST Framework
NO agregar dependencias a callcentersite/requirements/base.txt

Esta decision permite que ambos proyectos evolucionen independientemente, manteniendo la estabilidad del entregable principal mientras se experimenta e innova con el framework de agentes IA.
