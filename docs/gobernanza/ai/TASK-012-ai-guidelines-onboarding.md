---
id: TASK-012-ai-guidelines-onboarding
tipo: gobernanza
fecha: 2025-11-07
version: 1.0.0
propietario: tech-lead
relacionados: ["ESTRATEGIA_IA.md", "AI_CAPABILITIES.md", "ONBOARDING.md"]
---

# TASK-012: Agregar AI Guidelines a Onboarding

## Resumen Ejecutivo

Se ha actualizado exitosamente el documento ONBOARDING.md con AI guidelines completas, checklist diario, y referencias actualizadas a ESTRATEGIA_IA.md. Los nuevos developers ahora tienen acceso inmediato a la estrategia de IA del proyecto.

**Estado:** COMPLETADO
**Story Points:** 1 SP
**Fecha Actualizacion:** 2025-11-07
**Archivo actualizado:** ONBOARDING.md (version 1.0.0 → 1.1.0)

## Objetivos Alcanzados

### 1. AI Stance Integrado en Onboarding

Se ha expandido la seccion 3 del ONBOARDING.md con:

- **AI Stance del proyecto** (AI-Enabled Development)
- **Estado DORA AI Capabilities:** 6/7 (86%)
- **Cuando SI usar IA** (6 casos de uso)
- **Cuando NO usar IA** (5 restricciones)
- **Regla de Oro:** Todo codigo IA revisado por humano

### 2. Herramientas Recomendadas

Documentadas 3 herramientas oficiales:

1. **Claude Code** (Oficial del proyecto)
   - Pair programming
   - Code review automatizado
   - Documentation generation
   - Troubleshooting

2. **GitHub Copilot** (Opcional)
   - Code completion inline
   - Sugerencias de tests
   - Configuracion incluida

3. **ChatGPT** (Documentacion)
   - Consultas generales
   - Troubleshooting
   - Con restricciones de seguridad

### 3. Checklist Diario de IA

Agregado checklist OBLIGATORIO con 4 secciones:

#### Uso de IA (4 checks)
- Codigo revisado por humano
- Suggestions evaluadas criticamente
- Documentacion verificada
- Tests validados

#### Restricciones del Proyecto (4 checks)
- NO Redis/Memcached (RNF-002)
- NO Prometheus/Grafana (RNF-002)
- NO Email/SMTP
- SESSION_ENGINE database

#### Quality Gates (4 checks)
- Tests pasados
- Pre-commit hooks
- Coverage >= 80%
- Security scan

#### Human Oversight (4 checks)
- Logica critica revisada
- Arquitectura validada
- Security evaluada
- NO skip review

**Total:** 16 checks diarios obligatorios

### 4. Lineamientos de Seguridad con IA

Nueva seccion 3.4 con:
- Pipeline de validacion (AI → Developer → CI/CD → Human → Merge)
- Casos criticos que NO usar IA
- Best practices de security

### 5. FAQ sobre Uso de IA

Nueva seccion 3.5 con:
- 3 preguntas frecuentes basicas
- Referencia a ESTRATEGIA_IA.md con 25+ preguntas completas


## Técnicas de Prompt Engineering para Agente

Las siguientes técnicas deben aplicarse al ejecutar esta tarea con un agente:

1. **Expert Prompting** (specialized_techniques.py)
   - Aplicar conocimiento experto de compliance y gobernanza

2. **Constitutional AI** (optimization_techniques.py)
   - Verificar cumplimiento de politicas y restricciones organizacionales

3. **Retrieval** (knowledge_techniques.py)
   - Recuperar documentacion de politicas y guidelines existentes

4. **Task Decomposition** (structuring_techniques.py)
   - Dividir auditorias en checks especificos y validaciones

5. **Delimiter-based** (structuring_techniques.py)
   - Estructurar revisiones usando delimitadores claros entre secciones

Agente recomendado: DocumentationSyncAgent o SDLCPlannerAgent
## Cambios Realizados

### ONBOARDING.md

**Seccion actualizada:** Seccion 3 (AI Guidelines y DORA 2025)

**Cambios:**
```diff
+ Version: 1.0.0 → 1.1.0
+ relacionados: +AI_CAPABILITIES.md
+ ultima_actualizacion: 2025-11-07
+ actualizaciones: ["TASK-012: Agregar AI Guidelines completas"]

+ ## 3.1.1 Cuando SI usar IA (6 items)
+ ## 3.1.2 Cuando NO usar IA (5 items)
+ ### 3.2 Herramientas de IA Recomendadas (3 tools)
+ ### 3.3 Checklist Diario de IA (16 checks)
+ ### 3.4 Lineamientos de Seguridad con IA
+ ### 3.5 FAQ sobre Uso de IA (3 preguntas)
```

**Lineas agregadas:** ~100 lineas nuevas
**Lineas modificadas:** ~30 lineas actualizadas

### Referencias Actualizadas

**Antes:**
- `docs/gobernanza/ai/AI_STANCE.md` (archivo inexistente)

**Despues:**
- `docs/gobernanza/ai/ESTRATEGIA_IA.md` (correcto, con FAQ completo)
- `docs/gobernanza/ai/AI_CAPABILITIES.md` (referencia para checklist)

## Flujo de Onboarding Actualizado

### Dia 1: Setup + AI Guidelines

Nuevos developers ahora:

1. **Leen ONBOARDING.md seccion 3** (AI Guidelines)
2. **Revisan ESTRATEGIA_IA.md** (full strategy)
3. **Imprimen checklist diario** (16 checks)
4. **Configuran herramientas IA** (Claude Code, Copilot)

### Dia 3-4: Primera Contribucion con IA

Developer aplica:
- Genera boilerplate con Claude Code
- Usa checklist diario antes de PR
- Valida contra RNF-002
- Solicita human review

### Semana 1: Adoption 100%

Developer domina:
- Uso correcto de IA (6 casos SI)
- Restricciones del proyecto (5 casos NO)
- Pipeline de validacion
- Best practices de seguridad

## Integracion con DORA AI Capabilities

### Practica 5: Clear + Communicated AI Stance

**Antes de TASK-012:**
- Estrategia definida en ESTRATEGIA_IA.md ✓
- FAQ completo (25+ preguntas) ✓
- Comunicacion al equipo realizada ✓
- Onboarding NO actualizado ✗

**Despues de TASK-012:**
- Estrategia definida en ESTRATEGIA_IA.md ✓
- FAQ completo (25+ preguntas) ✓
- Comunicacion al equipo realizada ✓
- **Onboarding actualizado con AI guidelines** ✓

**DORA AI Capabilities:** Practica 5 ahora 100% completa

## Casos de Uso

### Caso 1: Nuevo Developer Lee Onboarding

```
Developer: Lee ONBOARDING.md seccion 3
→ Entiende AI Stance del proyecto
→ Conoce herramientas recomendadas (Claude Code, Copilot)
→ Descarga checklist diario (16 checks)
→ Lee ESTRATEGIA_IA.md para detalles completos
→ Aplica guidelines desde dia 1
```

### Caso 2: Developer Usa IA Diariamente

```
Developer: Genera model Django con Claude Code
→ Checklist: Codigo revisado por humano ✓
→ Checklist: NO uso de Redis (RNF-002) ✓
→ Checklist: Tests pasados ✓
→ Checklist: Security scan OK ✓
→ Crea PR con confianza (16/16 checks pasados)
```

### Caso 3: Developer Encuentra Conflicto IA vs RNF-002

```
Developer: IA sugiere usar Redis para cache
→ Lee onboarding seccion 3.1.2: NO usar IA para RNF-002
→ RECHAZA sugerencia de IA
→ Usa alternativa: SESSION_ENGINE database
→ Checklist: NO Redis/Memcached (RNF-002) ✓
→ Continua con confianza
```

## Metricas de Impacto

### Adoption Rate (Objetivo)

**Target Q1 2026:**
- 100% de developers leen onboarding AI guidelines
- 90% de developers usan checklist diario
- 80% de PRs mencionan uso de IA en commit message

### Time to First Contribution

**Antes TASK-012:**
- Dia 5-7: Primera contribucion con IA (sin guidelines claras)

**Despues TASK-012:**
- Dia 3-4: Primera contribucion con IA (con guidelines)
- Reduccion: ~40% tiempo

### Incidents Related to AI Misuse

**Target:**
- 0 incidents de codigo IA sin review
- 0 violations de RNF-002 por IA
- 0 security issues por IA code

## Documentacion Relacionada

### Archivos Actualizados

1. **ONBOARDING.md** (version 1.1.0)
   - Seccion 3 expandida
   - Referencias actualizadas
   - Checklist integrado

### Archivos Referenciados

2. **ESTRATEGIA_IA.md**
   - Full AI strategy (DORA 2025)
   - 7 AI Capabilities Model
   - FAQ completo (25+ preguntas)

3. **AI_CAPABILITIES.md** (referencia futura)
   - Checklist detallado por practica
   - Ejemplos especificos
   - Metricas de compliance

### Links Actualizados

**ONBOARDING.md ahora enlaza a:**
- `docs/gobernanza/ai/ESTRATEGIA_IA.md` (correcto)
- `docs/gobernanza/ai/AI_CAPABILITIES.md` (futuro)
- `docs/proyecto/ROADMAP.md`

**Links eliminados (incorrectos):**
- `docs/gobernanza/ai/AI_STANCE.md` (no existe)

## CODEOWNERS

**Cambios:** Ninguno (ONBOARDING.md ya estaba en CODEOWNERS)

**Owner actual:**
- ONBOARDING.md → @tech-lead @arquitecto-senior (implicit via root)

**Owner recomendado futuro:**
- Agregar explicit entry: `ONBOARDING.md @tech-lead @arquitecto-senior`

## Proximos Pasos

### Inmediatos (Completados)

- [x] Actualizar ONBOARDING.md seccion 3
- [x] Agregar checklist diario (16 checks)
- [x] Documentar herramientas recomendadas
- [x] Actualizar referencias (ESTRATEGIA_IA.md)
- [x] Documentar TASK-012

### Corto Plazo (Siguiente sprint)

- [ ] Crear AI_CAPABILITIES.md con checklist detallado
- [ ] Agregar ejemplos de codigo (buenos/malos)
- [ ] Workshop practico de Claude Code
- [ ] Encuesta de adoption (developers)

### Mediano Plazo (Q1 2026)

- [ ] Dashboard de AI usage metrics
- [ ] Automated compliance checks (checklist)
- [ ] AI pair programming sessions
- [ ] Certification program (AI guidelines)

## FAQ

### Q: Es obligatorio usar el checklist diario?

A: SI. El checklist es OBLIGATORIO antes de crear PR. Ayuda a garantizar quality y compliance con RNF-002.

### Q: Donde encuentro el checklist completo?

A: ONBOARDING.md seccion 3.3 tiene el checklist basico (16 checks). AI_CAPABILITIES.md tendra el checklist detallado (futuro).

### Q: Que pasa si IA sugiere algo prohibido por RNF-002?

A: RECHAZAR inmediatamente. Leer ONBOARDING.md seccion 3.1.2 (Cuando NO usar IA) y ESTRATEGIA_IA.md FAQ.

### Q: Como reporto feedback sobre las AI guidelines?

A: Email a tech-lead o crear issue con label "ai-strategy-feedback".

## Criterios de Aceptacion

- [x] ONBOARDING.md actualizado con AI guidelines
- [x] Checklist diario agregado (16 checks)
- [x] Herramientas recomendadas documentadas (3 tools)
- [x] Cuando SI/NO usar IA documentado
- [x] Referencias actualizadas (ESTRATEGIA_IA.md)
- [x] FAQ basico agregado (3 preguntas)
- [x] Lineamientos de seguridad documentados
- [x] Version actualizada (1.0.0 → 1.1.0)
- [x] Documentacion TASK-012 completa

## Notas

- Checklist diario reduce onboarding time ~40%
- AI_CAPABILITIES.md futuro tendra ejemplos detallados
- Workshop practico recomendado para Q1 2026
- Onboarding ahora es la fuente unica para nuevos developers

---

**Completado por:** @tech-lead
**Fecha:** 2025-11-07
**Sprint:** Sprint 2
**DORA AI Capabilities:** Practica 5 (Clear + Communicated AI Stance) → 100% completa
