---
id: RF-CONSOLIDADO-PLACEMENT
tipo: funcional_consolidado
titulo: Requisitos Funcionales del Sistema de Placement
dominio: ai
owner: equipo-ai
fecha_creacion: 2025-11-16
estado: aprobado
trazabilidad_upward:
  - N-001
  - UC-001
  - UC-002
  - RN-001
  - RN-002
  - RN-003
  - RN-004
---

# Requisitos Funcionales: Sistema de Gestion de Ubicacion de Artefactos

Este documento consolida todos los requisitos funcionales derivados de N-001.

## RF-001: Detectar Tipo de Artefacto

### Descripcion
El sistema DEBERA detectar automaticamente el tipo de artefacto (task, adr, analisis, guia, etc.) mediante analisis del nombre del archivo y patron de contenido.

### Criterios de Aceptacion

```gherkin
Scenario: Detectar tipo desde nombre de archivo
Given un archivo con nombre "TASK-001-implementar_feature.md"
When el sistema analiza el nombre
Then el tipo detectado es "task"
  And la confianza es >= 0.95

Scenario: Detectar tipo desde contenido
Given un archivo con nombre "documento.md"
  And el contenido incluye "## Decision" y "## Status"
When el sistema analiza el contenido
Then el tipo detectado es "adr"
  And la confianza es >= 0.80

Scenario: Tipo no detectado (fallback)
Given un archivo con nombre "archivo_generico.md"
  And contenido sin patrones reconocibles
When el sistema analiza el archivo
Then el tipo detectado es "documento_general"
  And la confianza es < 0.50
  And requiere_clarificacion es true
```

### Implementacion
- `detector.py::detectar_tipo(nombre, contenido) -> str`
- Patrones de nombre: TASK-, ADR-, REQ-, ANALISIS_, etc.
- Patrones de contenido: headers Markdown especificos

## RF-002: Determinar Ownership

### Descripcion
El sistema DEBERA determinar el ownership del artefacto (transversal, dominio-especifico, agente, devops) analizando tipo, contexto y contenido.

### Criterios de Aceptacion

```gherkin
Scenario: Ownership transversal por tipo
Given un artefacto de tipo "adr"
When el sistema determina ownership
Then el ownership es "transversal"

Scenario: Ownership de dominio por contexto
Given un artefacto de tipo "task"
  And el contexto incluye dominio: "backend"
When el sistema determina ownership
Then el ownership es "dominio:backend"

Scenario: Ownership detectado por contenido
Given un artefacto de tipo "guia"
  And el contenido menciona solo "Django REST API"
When el sistema analiza dominios mencionados
Then el ownership es "dominio:backend"

Scenario: Ownership ambiguo requiere clarificacion
Given un artefacto de tipo "task"
  And sin contexto de dominio
  And contenido menciona "React" y "Django"
When el sistema determina ownership
Then el ownership es "REQUIERE_CLARIFICACION"
```

### Implementacion
- `ownership.py::determinar_ownership(tipo, contexto, contenido) -> str`
- `detector.py::detectar_dominios_en_contenido(contenido) -> List[str]`

## RF-003: Construir Ubicacion Canonica

### Descripcion
El sistema DEBERA construir la ubicacion canonica del artefacto basandose en su tipo, ownership y temporalidad, siguiendo ADR-010.

### Criterios de Aceptacion

```gherkin
Scenario: Ubicacion de ADR (transversal)
Given tipo: "adr", ownership: "transversal"
When el sistema construye ubicacion
Then la ubicacion es "docs/gobernanza/adr/"

Scenario: Ubicacion de TASK (dominio backend)
Given tipo: "task", ownership: "dominio:backend"
When el sistema construye ubicacion
Then la ubicacion es "docs/backend/tareas/"

Scenario: Ubicacion de analisis historico
Given tipo: "analisis"
  And temporalidad: "historico"
When el sistema construye ubicacion
Then la ubicacion coincide con "docs/gobernanza/sesiones/analisis_YYYY_MM/"

Scenario: Ubicacion de script temporal
Given tipo: "script"
  And temporalidad: "temporal"
When el sistema construye ubicacion
Then la ubicacion es "/tmp/"

Scenario: Ubicacion de documentacion de agente
Given tipo: "documentacion_agente"
When el sistema construye ubicacion
Then la ubicacion es "scripts/coding/ai/agents/"
```

### Implementacion
- `ubicacion.py::construir_ubicacion(tipo, ownership, temporalidad, contexto) -> str`
- Mapeo completo en dict UBICACIONES

## RF-004: Generar Nombre Estandarizado

### Descripcion
El sistema DEBERA generar nombres de archivos siguiendo convenciones Clean Code Naming (sin emojis, snake_case, prefijos por tipo).

### Criterios de Aceptacion

```gherkin
Scenario: Generar nombre de TASK
Given tipo: "task"
  And contexto: {id: "001", descripcion: "Implementar Feature"}
When el sistema genera nombre
Then el nombre es "TASK-001-implementar_feature.md"

Scenario: Generar nombre de analisis
Given tipo: "analisis"
  And contexto: {tema: "DOCS_ESTRUCTURA"}
  And fecha actual: 2025-11-16
When el sistema genera nombre
Then el nombre es "ANALISIS_DOCS_ESTRUCTURA_20251116.md"

Scenario: Normalizar descripcion con emojis
Given descripcion: "Fix Bug 🐛 en Login"
When el sistema normaliza descripcion
Then el resultado es "fix_bug_en_login"

Scenario: Normalizar nombre con caracteres especiales
Given descripcion: "Análisis de Docs 📊!!!"
When el sistema normaliza descripcion
Then el resultado es "analisis_de_docs"
```

### Implementacion
- `naming.py::construir_nombre(tipo, nombre_original, contexto) -> str`
- `naming.py::normalizar_descripcion(desc) -> str`
- Regex para eliminar emojis, normalizar a snake_case

## RF-005: Generar Frontmatter YAML

### Descripcion
El sistema DEBERA generar frontmatter YAML apropiado segun el tipo de artefacto, incluyendo fecha, tipo y campos especificos por tipo.

### Criterios de Aceptacion

```gherkin
Scenario: Frontmatter de TASK
Given tipo: "task"
  And contexto: {id: "001", categoria: "desarrollo", dominio: "backend"}
When el sistema genera frontmatter
Then el frontmatter incluye:
  | campo       | valor        |
  | id          | TASK-001     |
  | fecha       | 2025-11-16   |
  | tipo        | task         |
  | categoria   | desarrollo   |
  | dominio     | backend      |
  | estado      | pendiente    |

Scenario: Frontmatter de ADR
Given tipo: "adr"
  And contexto: {id: "010"}
When el sistema genera frontmatter
Then el frontmatter incluye:
  | campo       | valor        |
  | id          | ADR-010      |
  | tipo        | adr          |
  | categoria   | arquitectura |
  | estado      | propuesto    |
  | supersede   | []           |

Scenario: Validacion de frontmatter YAML
Given frontmatter generado
When se parsea con PyYAML
Then no lanza excepcion
  And todos los campos obligatorios estan presentes
```

### Implementacion
- `frontmatter.py::generar_frontmatter(tipo, contexto) -> Dict`
- Dict BASE con fecha y tipo
- Dict especifico por tipo (FRONTMATTER_POR_TIPO)

## RF-006: Calcular Confianza de Clasificacion

### Descripcion
El sistema DEBERA calcular un score de confianza (0.0-1.0) de la clasificacion basandose en coincidencias de patrones.

### Criterios de Aceptacion

```gherkin
Scenario: Alta confianza (tipo declarado + patron de nombre)
Given tipo_declarado: "task"
  And nombre contiene patron "TASK-"
When el sistema calcula confianza
Then la confianza es >= 0.95

Scenario: Confianza media (solo patron de contenido)
Given tipo_declarado: null
  And contenido contiene patron de ADR
When el sistema calcula confianza
Then la confianza esta entre 0.70 y 0.90

Scenario: Baja confianza (sin patrones claros)
Given tipo_declarado: null
  And nombre generico: "documento.md"
  And contenido sin patrones
When el sistema calcula confianza
Then la confianza es < 0.50
  And requiere_clarificacion es true
```

### Implementacion
- `validacion.py::calcular_confianza(tipo_declarado, tipo_detectado, matches) -> float`
- Pesos: tipo_declarado = 0.4, patron_nombre = 0.35, patron_contenido = 0.25

## RF-007: Aplicar Guardrails

### Descripcion
El sistema DEBERA aplicar guardrails de validacion para prevenir clasificaciones incorrectas o peligrosas.

### Criterios de Aceptacion

```gherkin
Scenario: Guardrail de confianza minima
Given clasificacion con confianza 0.45
  And confianza minima configurada 0.60
When el sistema aplica guardrails
Then el guardrail falla con error "Confianza muy baja: 45% < 60%"

Scenario: Guardrail de ubicacion prohibida
Given ubicacion calculada "/home/user/docs/"
When el sistema aplica guardrails
Then el guardrail falla con error "Ubicacion prohibida: /home/"

Scenario: Guardrail de tipo valido
Given tipo detectado "tipo_inexistente"
When el sistema aplica guardrails
Then el guardrail falla con error "Tipo no valido: tipo_inexistente"

Scenario: Todos los guardrails pasan
Given clasificacion con confianza 0.95
  And ubicacion "docs/gobernanza/adr/"
  And tipo "adr"
When el sistema aplica guardrails
Then no hay errores
  And guardrails_passed es true
```

### Implementacion
- `PlacementAgent::apply_guardrails(resultado) -> List[str]`
- Guardrails:
  1. Confianza >= min_confidence (default 0.6)
  2. Ubicacion no en UBICACIONES_PROHIBIDAS
  3. Tipo en TIPOS_VALIDOS

## Trazabilidad

### Upward (Origen)
- N-001: Sistema de Gestion Automatica de Ubicacion de Artefactos
- UC-001: Clasificar Artefacto via CLI
- UC-002: Clasificar Artefacto desde Agente SDLC
- RN-001, RN-002, RN-003, RN-004

### Downward (Derivados)
- TEST-RF-001-xxx: Tests unitarios de deteccion de tipo
- TEST-RF-002-xxx: Tests unitarios de ownership
- TEST-RF-003-xxx: Tests unitarios de ubicacion
- TEST-RF-004-xxx: Tests unitarios de naming
- TEST-RF-005-xxx: Tests unitarios de frontmatter
- TEST-RF-006-xxx: Tests unitarios de confianza
- TEST-RF-007-xxx: Tests unitarios de guardrails
- TASK-IMPL-001: Implementar modulo placement/
- TASK-IMPL-002: Implementar PlacementAgent

## Definition of Done

- [x] Todos los RF documentados con criterios de aceptacion Gherkin
- [ ] Tests escritos para cada RF (TDD RED phase)
- [ ] Implementacion completa (TDD GREEN phase)
- [ ] Coverage >= 90% en modulo placement/
- [ ] Guardrails implementados y testeados
- [ ] Integracion con al menos 1 agente SDLC verificada
- [ ] Documentacion tecnica completa
