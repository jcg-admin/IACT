# ADR-020: Organizacion de Documentacion por Dominio

**Estado:** Aceptado
**Fecha:** 2025-11-16
**Autores:** Equipo de Arquitectura
**Contexto:** Reorganizacion completa de docs/

---

## Contexto y Problema

La documentacion del proyecto IACT estaba organizada de forma funcional (qa/, testing/, deployment/, etc.) en lugar de por dominio. Esto causaba:

1. **Confusion sobre ubicacion**: No se sabia donde buscar documentacion especifica
2. **Duplicacion**: Contenido duplicado en multiples ubicaciones
3. **Acoplamiento**: Dominios tenian que buscar en directorios compartidos
4. **Falta de ownership**: No estaba claro quien era responsable de cada documento

**Pregunta clave:** ¿Como organizar la documentacion para maximizar claridad, minimizar duplicacion y respetar boundaries de dominio?

---

## Drivers de Decision

1. **Separacion de concerns**: Cada dominio debe ser autonomo
2. **Discoverabilidad**: Facil encontrar documentacion relevante
3. **Ownership claro**: Cada equipo es responsable de su documentacion
4. **Minimizar duplicacion**: Contenido transversal en un solo lugar
5. **Escalabilidad**: Estructura que soporte crecimiento
6. **Consistencia**: Patron repetible para todos los dominios

---

## Decision

**Adoptar organizacion de documentacion por DOMINIO** con las siguientes reglas:

### Regla 1: Cada dominio contiene su propia documentacion completa

```
docs/
├── backend/
│   ├── api/
│   ├── adr/           # ADRs especificos de backend
│   ├── arquitectura/
│   ├── diagramas/
│   ├── qa/            # Testing de backend
│   ├── requisitos/    # Requisitos de backend
│   └── ...
├── frontend/
│   ├── adr/           # ADRs especificos de frontend
│   ├── arquitectura/
│   ├── diagramas/
│   ├── qa/            # Testing de frontend
│   ├── requisitos/    # Requisitos de frontend
│   └── ...
├── devops/
│   ├── ci-cd/
│   ├── deployment/
│   ├── git/
│   └── qa/            # Testing de pipelines/automation
├── infraestructura/
│   ├── arquitectura/
│   ├── requisitos/    # Requisitos de infraestructura
│   └── ...
```

### Regla 2: Contenido transversal va en gobernanza/ o anexos/

**gobernanza/**: Estrategias, procedimientos, lineamientos generales
- gobernanza/qa/ - Estrategia QA general (no testing especifico)
- gobernanza/adr/ - ADRs transversales que afectan multiples dominios
- gobernanza/requisitos/ - Requisitos de negocio/stakeholders
- gobernanza/arquitectura/ - Decisiones arquitecturales generales

**anexos/**: Solo contenido verdaderamente transversal
- Glosario
- FAQ
- Diagramas de contexto del sistema completo
- Referencias externas

### Regla 3: Requisitos por dominio con matriz de trazabilidad

Cada dominio mantiene sus propios requisitos:
- backend/requisitos/ - Requisitos de APIs, servicios, modelos
- frontend/requisitos/ - Requisitos de UI/UX, componentes
- infraestructura/requisitos/ - Requisitos de hardware, redes, cloud
- gobernanza/requisitos/ - Requisitos de negocio, compliance, stakeholders

**Trazabilidad:** Matriz en gobernanza/requisitos/MATRIZ_TRAZABILIDAD.md relaciona requisitos entre dominios

```
REQ-GOB-001 (Autenticacion OAuth2)
  ├─→ REQ-BACK-015 (Implementar OAuth2 provider)
  ├─→ REQ-FRONT-023 (Login UI con OAuth2)
  └─→ REQ-INFRA-008 (Redis para OAuth2 tokens)
```

### Regla 4: QA por dominio

Cada dominio es responsable de su propio testing:
- backend/qa/ - Tests backend (pytest, unit, integration)
- frontend/qa/ - Tests frontend (jest, testing-library, e2e)
- devops/qa/ - Tests de CI/CD, validation de pipelines
- infraestructura/qa/ - Smoke tests, validaciones de infraestructura

**Estrategia general QA:** gobernanza/qa/estrategia_qa.md

### Regla 5: Diagramas por dominio

Diagramas especificos de cada dominio viven con ese dominio:
- backend/diagramas/ - Arquitectura backend, ER, secuencia de APIs
- frontend/diagramas/ - Casos de uso, wireframes, componentes

**Diagramas transversales:** anexos/diagramas/contexto/ (C4 Level 1)

---

## Alternativas Consideradas

### Alternativa 1: Organizacion funcional (rechazada)

```
docs/
├── qa/              # Todo el QA junto
├── arquitectura/    # Toda la arquitectura junta
├── requisitos/      # Todos los requisitos juntos
└── deployment/      # Todo deployment junto
```

**Rechazada porque:**
- Alto acoplamiento entre dominios
- No escala bien
- Dificil determinar ownership
- Duplicacion inevitable

### Alternativa 2: Hibrido (rechazada)

Algunos por dominio, algunos funcionales

**Rechazada porque:**
- Inconsistente
- Confuso (dos patrones diferentes)
- No resuelve el problema de duplicacion

### Alternativa 3: Monorepo estilo (considerada pero muy complejo)

Cada dominio completamente separado con su propio docs/

**Rechazada porque:**
- Demasiado aislamiento
- Dificil ver vision general
- Duplicacion masiva de contenido transversal

---

## Consecuencias

### Positivas

1. **Claridad**: Siempre se sabe donde buscar documentacion de un dominio
2. **Ownership**: Cada equipo es responsable de su documentacion
3. **Autonomia**: Dominios pueden evolucionar independientemente
4. **Reduccion duplicacion**: Contenido transversal en un solo lugar
5. **Escalabilidad**: Facil agregar nuevos dominios
6. **Mantenibilidad**: Cambios en un dominio no afectan otros

### Negativas

1. **Repeticion estructural**: Cada dominio tiene subdirectorios similares (qa/, arquitectura/, etc.)
2. **Navegacion**: Requiere conocer el dominio para encontrar documentacion
3. **Contenido transversal**: Requiere disciplina para no duplicar
4. **Migracion**: Requiere reorganizar documentacion existente

### Neutras

1. **Matriz de trazabilidad**: Necesaria pero agrega overhead de mantenimiento
2. **README.md en cada dominio**: Necesario para guiar navegacion
3. **Gobernanza como dominio especial**: Contiene reglas/estrategias generales

---

## Implementacion

### Fase 1: Reorganizar estructura (COMPLETADO 2025-11-16)

- [x] Mover devops/ a primer nivel
- [x] Distribuir QA por dominio
- [x] Organizar diagramas por dominio
- [x] Generar READMEs para directorios vacios

### Fase 2: Consolidar duplicados (EN PROGRESO)

- [ ] Consolidar gobernanza/ai/ -> docs/ai/
- [ ] Consolidar checklists
- [ ] Consolidar agentes
- [ ] Limpiar gobernanza/procesos/

### Fase 3: Crear matriz de trazabilidad

- [ ] Crear gobernanza/requisitos/MATRIZ_TRAZABILIDAD.md
- [ ] Relacionar requisitos entre dominios
- [ ] Documentar dependencias

### Fase 4: Documentacion de navegacion

- [ ] README.md en cada dominio principal
- [ ] Guia de organizacion para nuevos contribuidores
- [ ] Actualizar CONTRIBUTING.md

---

## Referencias

- ADR-014: Organizacion proyecto por dominio (codigo)
- ANALISIS_FALLAS_DOCS.md - Analisis de fallas que motivo esta decision
- Discusion: Issue #XXX (pendiente)

---

## Notas

Esta decision arquitectural se aplica SOLO a la organizacion de documentacion (docs/). La organizacion del codigo fuente sigue ADR-014.

**Principio fundamental:** "Cada dominio es responsable de documentar completamente su implementacion, arquitectura, testing y requisitos. Solo estrategias/procedimientos transversales van en gobernanza."

---

**Aprobado por:** Equipo de Arquitectura
**Fecha de aprobacion:** 2025-11-16
**Revision proxima:** 2026-02-16 (3 meses)
