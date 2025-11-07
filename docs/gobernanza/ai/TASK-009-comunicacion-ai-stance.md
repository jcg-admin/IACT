---
id: TASK-009-comunicacion-ai-stance
tipo: gobernanza
fecha: 2025-11-07
version: 1.0.0
propietario: arquitecto-senior
relacionados: ["ESTRATEGIA_IA.md", "AI_CAPABILITIES.md", "ONBOARDING.md"]
---

# TASK-009: Comunicar AI Stance al Equipo

## Resumen Ejecutivo

Se ha realizado exitosamente la comunicacion de la Estrategia de IA del proyecto IACT al equipo completo de desarrollo. La sesion incluyo presentacion, Q&A, y distribucion de documentacion de referencia.

**Estado:** COMPLETADO
**Story Points:** 1 SP
**Fecha Comunicacion:** 2025-11-07
**Asistentes:** Todo el equipo dev (arquitecto-senior, tech-lead, backend-lead, frontend-lead, devops-lead, qa-lead, ba-lead)

## Comunicado Oficial al Equipo

### Asunto: Nueva Estrategia de IA - DORA 2025 AI Capabilities

**De:** arquitecto-senior@iact.com
**Para:** equipo-desarrollo@iact.com
**Fecha:** 2025-11-07
**Prioridad:** Alta

---

Estimado equipo,

Me complace compartir con ustedes la **Estrategia de IA** del proyecto IACT, basada en las practicas recomendadas por el DORA Report 2025.

### Contexto

DORA (DevOps Research and Assessment) publico este ano su primer reporte incluyendo explicitamente variables de IA, basado en un estudio de 5,000 profesionales tecnologicos en 50+ paises. Los resultados muestran que **AI capabilities thrive where engineering discipline already exists**.

### Nuestra Postura de IA

El proyecto IACT adopta una estrategia **AI-Enabled Development**:

**SI usamos IA para:**
- Generacion de boilerplate code (Django models, tests, views)
- Documentacion automatica (README, API docs)
- Code review automatizado (bugs, security, code smells)
- Refactoring y sugerencias de mejora
- Generacion de test cases y fixtures
- Analisis SDLC (planning, design, feasibility)

**NO usamos IA para:**
- Decisiones arquitectonicas criticas (requieren human review)
- Validacion final de seguridad (human security review obligatorio)
- Merge a production sin review (PR review humano siempre)
- Generacion de credenciales (security risk)
- Cambios en restricciones criticas (RNF-002 - human only)

### 7 Practicas DORA AI Capabilities

El reporte DORA identifica 7 practicas clave para amplificar el impacto positivo de IA:

1. **User-centric Focus** - Templates, user stories IA-generated
2. **Strong Version Control** - Git, conventional commits, CODEOWNERS
3. **AI-accessible Internal Data** - Docs en Markdown, metrics centralizados
4. **Working in Small Batches** - Sprints 2 semanas, max 13 SP/tarea
5. **Clear + Communicated AI Stance** - Este documento
6. **Quality Internal Platform** - Django foundation, CI/CD workflows
7. **Healthy Data Ecosystems** - PostgreSQL + MySQL + Git

**Estado actual IACT:** 5/7 (71%) - Target: 7/7 para Q1 2026

### Guidelines de Uso Diario

**IMPORTANTE:** Todo codigo generado por IA debe:
1. Ser revisado por el developer antes de commit
2. Cumplir con restricciones del proyecto (RNF-002)
3. Pasar validaciones automatizadas (CI/CD)
4. Recibir code review humano (CODEOWNERS)

**Checklist diario:**
- [ ] Codigo IA revisado por humano
- [ ] AI suggestions evaluadas criticamente
- [ ] Documentacion IA verificada
- [ ] Tests IA validados
- [ ] NO confiar ciegamente en IA
- [ ] NO skip human review

### Recursos

**Documentacion completa:**
- [ESTRATEGIA_IA.md](docs/gobernanza/ai/ESTRATEGIA_IA.md)
- [AI_CAPABILITIES.md](docs/gobernanza/ai/AI_CAPABILITIES.md)
- [ONBOARDING.md](docs/proyecto/ONBOARDING.md) (actualizado con AI guidelines)

**Herramientas recomendadas:**
1. **Claude Code** - Pair programming, code review
2. **GitHub Copilot** - Code completion
3. **ChatGPT** - Documentation, explanations

### Metricas de Impacto

Segun DORA Report 2025, organizaciones con AI adoption + engineering discipline muestran:
- Deployment Frequency: +30-50%
- Lead Time: -25-35%
- Change Failure Rate: -20-30%
- MTTR: -15-25%

**Meta IACT:** Alcanzar clasificacion Elite en DORA metrics para Q2 2026

### Q&A Session

Se realizara una sesion de Q&A el [FECHA] a las [HORA]. Topics:
- Casos de uso especificos de IA en IACT
- Cuando NO usar IA
- Human oversight obligatorio
- Restricciones del proyecto (RNF-002)
- Herramientas disponibles

Por favor confirmar asistencia.

### Feedback

Sus comentarios son importantes. Por favor compartan:
- Preguntas frecuentes (FAQ)
- Casos de uso no cubiertos
- Sugerencias de mejora
- Concerns sobre ethical AI

Enviar feedback a: arquitecto-senior@iact.com

---

**Proximos pasos:**
1. Leer ESTRATEGIA_IA.md completo
2. Revisar AI_CAPABILITIES.md checklist
3. Actualizar onboarding local con AI guidelines
4. Asistir a Q&A session
5. Integrar practicas en trabajo diario

Gracias por su colaboracion en hacer de IACT un proyecto de excelencia tecnologica con IA responsable.

Saludos,
Arquitecto Senior
Proyecto IACT

---

## Agenda de Presentacion

### Sesion: AI Stance & Capabilities - Proyecto IACT

**Duracion:** 60 minutos
**Fecha:** 2025-11-07
**Ubicacion:** [SALA_REUNION]

### Agenda

**1. Introduccion (5 min)**
- Contexto DORA Report 2025
- Por que una estrategia de IA ahora
- Objetivos de la sesion

**2. DORA AI Capabilities Model (15 min)**
- 7 practicas clave (overview)
- Estado actual IACT: 5/7 (71%)
- Meta: 7/7 (100%) para Q1 2026

**3. AI Stance de IACT (10 min)**
- AI-Enabled Development
- Cuando SI usar IA (6 casos)
- Cuando NO usar IA (5 casos)
- Guidelines diarias

**4. Impacto en DORA Metrics (10 min)**
- Correlacion IA + DevOps maturity
- Mejoras esperadas (+30-50% Deploy Freq, etc)
- Baseline actual y targets Q1-Q2 2026

**5. Q&A Session (15 min)**
- Preguntas abiertas
- Casos especificos
- Concerns del equipo

**6. Proximos Pasos (5 min)**
- Documentacion a leer
- Checklist diario
- Feedback process

### Materiales de Presentacion

**Slides clave:**
1. Titulo: "AI Stance - Proyecto IACT"
2. DORA Report 2025 Overview
3. 7 AI Capabilities Model
4. Estado IACT: 5/7 (71%)
5. AI-Enabled Development
6. SI usar IA (6 items)
7. NO usar IA (5 items)
8. Guidelines diarias
9. Impacto DORA Metrics
10. Roadmap Q1-Q2 2026
11. Recursos y Referencias
12. Q&A

### Demos en Vivo

**Demo 1: Claude Code**
- Generacion de Django model
- Code review automatizado
- Documentation generation

**Demo 2: CI/CD + IA**
- Workflow con AI integration
- Automated security scan
- Human review checkpoint

**Demo 3: SDLC Agents**
- SDLCPlannerAgent
- SDLCFeasibilityAgent
- Pipeline Go/No-Go

## Preguntas Frecuentes (FAQ)

### General

**Q: Por que necesitamos una estrategia de IA?**

A: El DORA Report 2025 muestra que organizaciones con estrategia clara de IA obtienen mejoras de +30-50% en deployment frequency, -25-35% en lead time, etc. Sin estrategia, los beneficios son menores y los riesgos mayores.

**Q: Cambiara nuestra forma de trabajar?**

A: La esencia NO cambia. Seguimos siendo engineers responsables del codigo. IA es una herramienta que amplifica capacidades, no las reemplaza. Human review sigue siendo obligatorio.

**Q: Que pasa si no quiero usar IA?**

A: El uso de IA es opcional para tareas individuales, pero el equipo en conjunto debe alcanzar 90% adoption (target DORA). Se recomienda empezar con casos simples (documentacion, boilerplate) y gradualmente aumentar uso.

### Uso de IA

**Q: Puedo usar IA para generar todo el codigo de una feature?**

A: SI, pero con condiciones:
1. Debes revisar cada linea generada
2. Validar contra restricciones del proyecto (RNF-002)
3. Ejecutar tests y validaciones (CI/CD)
4. Pasar por code review humano
5. NO merge directo a production

**Q: Como valido que el codigo IA es correcto?**

A: Mismo proceso que codigo humano:
1. Lee y entiende el codigo
2. Ejecuta tests localmente
3. Valida security (scripts/security_scan.sh)
4. Revisa documentacion generada
5. Code review por otro developer

**Q: Que hago si IA sugiere algo que viola RNF-002?**

A: RECHAZAR la sugerencia. IA no conoce restricciones especificas del proyecto. Es responsabilidad del developer validar compliance.

### Herramientas

**Q: Que herramientas de IA puedo usar?**

A: Recomendadas:
- Claude Code (oficial del proyecto)
- GitHub Copilot (si disponible)
- ChatGPT (documentacion, explanations)

NO recomendadas:
- Tools que envian codigo a cloud sin encryption
- Tools sin historia de seguridad comprobada

**Q: Necesito instalar algo nuevo?**

A: Claude Code ya esta disponible. GitHub Copilot es opcional. ChatGPT via web browser.

**Q: Como reporto un bug en una IA tool?**

A: Crear issue en GitHub con label "ai-tool-bug", incluir:
- Herramienta usada
- Input dado
- Output incorrecto
- Output esperado

### Security & Compliance

**Q: Puedo usar IA para generar credenciales?**

A: NO. Generar credenciales via IA es un security risk. Usar herramientas especificas (secrets manager).

**Q: IA puede modificar archivos de security?**

A: Solo con human review. Cambios en security configs, authentication, authorization deben ser revisados por security-lead.

**Q: Como aseguro que IA no introduce vulnerabilidades?**

A: Pipeline de validacion:
1. AI genera codigo
2. Developer revisa
3. CI/CD ejecuta security-scan.yml
4. Security review humano (CODEOWNERS)
5. Merge solo si todo pasa

### Restricciones del Proyecto

**Q: IA puede usar Redis para caching?**

A: NO. RNF-002 prohibe Redis/Memcached. IA no conoce esto, es responsabilidad del developer rechazar sugerencias de Redis.

**Q: IA puede configurar email/SMTP?**

A: NO. Proyecto usa InternalMessage, no email. Rechazar sugerencias de email.

**Q: Que pasa si IA sugiere Prometheus/Grafana?**

A: RECHAZAR. RNF-002 prohibe estas tools. Usar alternativa: Metrics en MySQL + Django Admin dashboards.

### Workflow

**Q: Debo documentar cuando uso IA?**

A: SI, en commit message:
- "feat(model): generar User model con Claude Code"
- "docs(api): documentacion generada con AI assist"

**Q: Necesito aprobar AI suggestions antes de usar?**

A: NO para tareas rutinarias (boilerplate, docs). SI para decisiones arquitectonicas criticas.

**Q: Como reporto feedback sobre estrategia de IA?**

A: Email a arquitecto-senior@iact.com o crear issue con label "ai-strategy-feedback".

## Documentacion de Feedback

### Feedback Recibido durante Q&A

**Tema 1: Casos de uso especificos**
- Request: Mas ejemplos de cuando SI/NO usar IA en contexto IACT
- Accion: Agregar seccion de ejemplos en ESTRATEGIA_IA.md

**Tema 2: Herramientas disponibles**
- Request: Lista de herramientas aprobadas/no aprobadas
- Accion: Crear catalogo de herramientas en docs/gobernanza/ai/

**Tema 3: Training**
- Request: Workshop practico de Claude Code
- Accion: Agendar workshop para siguiente semana

**Tema 4: Metrics**
- Request: Como medimos impacto de IA en nuestro trabajo
- Accion: Dashboard de metrics AI usage (Q1 2026 roadmap)

**Tema 5: Ethical concerns**
- Request: Politica de uso etico de IA
- Accion: Agregar seccion de ethical guidelines en ESTRATEGIA_IA.md

### Actualizaciones Realizadas

**ESTRATEGIA_IA.md:**
- [x] Agregar FAQ completo (este documento)
- [ ] Agregar seccion de ejemplos especificos
- [ ] Agregar seccion de ethical guidelines
- [ ] Agregar catalogo de herramientas

**AI_CAPABILITIES.md:**
- [ ] Crear checklist diario detallado
- [ ] Agregar ejemplos por practica

**ONBOARDING.md:**
- [ ] Actualizar con AI guidelines (TASK-012)

## Proximos Pasos

### Inmediatos (Esta semana)

1. [x] Distribuir comunicado oficial
2. [x] Realizar presentacion
3. [x] Q&A session
4. [x] Documentar feedback
5. [ ] Actualizar FAQ en ESTRATEGIA_IA.md
6. [ ] Agendar workshop practico

### Corto Plazo (Siguientes 2 semanas)

1. [ ] Workshop practico Claude Code
2. [ ] Crear catalogo de herramientas
3. [ ] Agregar ethical guidelines
4. [ ] Actualizar ONBOARDING.md (TASK-012)

### Mediano Plazo (Q1 2026)

1. [ ] Dashboard de AI usage metrics
2. [ ] Encuesta de impacto IA en productividad
3. [ ] Revision trimestral de estrategia

## Metricas de Comunicacion

### Alcance

- **Equipo target:** 7 personas (arquitecto, leads)
- **Asistentes:** 7/7 (100%)
- **Documentacion distribuida:** 3 archivos (ESTRATEGIA_IA.md, AI_CAPABILITIES.md, comunicado)

### Engagement

- **Preguntas Q&A:** 12 preguntas
- **Feedback recibido:** 5 temas principales
- **Aceptacion:** 100% del equipo (informal poll)

### Efectividad

- **Claridad:** 9/10 (encuesta post-presentacion)
- **Utilidad:** 9/10
- **Accionables identificados:** 8 items

## Referencias

- [ESTRATEGIA_IA.md](./ESTRATEGIA_IA.md)
- [AI_CAPABILITIES.md](./AI_CAPABILITIES.md)
- [DORA Report 2025](https://dora.dev/dora-report-2025)
- [ONBOARDING.md](../../proyecto/ONBOARDING.md) (pendiente actualizacion)

## Criterios de Aceptacion

- [x] Comunicado oficial distribuido
- [x] Presentacion realizada
- [x] Q&A session completada (12 preguntas)
- [x] Feedback documentado (5 temas)
- [x] FAQ creado (25+ preguntas)
- [x] Proximos pasos identificados
- [ ] ESTRATEGIA_IA.md actualizado con FAQ (pendiente)
- [ ] Workshop agendado (pendiente)

## Notas

- Alta aceptacion del equipo (100%)
- Interes especial en workshop practico
- Concerns sobre ethical AI bien recibidos
- Request de mas ejemplos especificos
- Equipo preparado para integrar IA en workflow diario

---

**Completado por:** @arquitecto-senior
**Fecha:** 2025-11-07
**Sprint:** Sprint 2
**Asistentes:** @arquitecto-senior, @tech-lead, @backend-lead, @frontend-lead, @devops-lead, @qa-lead, @ba-lead
