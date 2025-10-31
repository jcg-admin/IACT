# Plan general de documentación

## Inventario actual

| Ruta | Nombre usa guion bajo? | Observaciones |
| --- | --- | --- |
| docs/00-vision-y-alcance/glossary.md | No | Usa guiones medios en la carpeta y nombre simple en inglés. |
| docs/01-gobernanza/lineamientos-gobernanza.md | No | Guiones medios para separar palabras. |
| docs/02-requisitos/rq-plantilla.md | No | Archivo de plantilla con prefijo `rq-`. |
| docs/02-requisitos/trazabilidad.md | No | Nombre en una sola palabra. |
| docs/03-arquitectura/adr/adr-2025-001-vagrant-mod-wsgi.md | No | Convención ADR con guiones medios. |
| docs/03-arquitectura/adr/plantilla-adr.md | No | Plantilla ADR con guiones medios. |
| docs/06-qa/estrategia-qa.md | No | Nombre corto con guiones medios. |
| docs/06-qa/registros/2025-02-16-ejecucion-pytest.md | No | Registra fecha y tema separados por guiones. |
| docs/07-devops/contenedores-devcontainer.md | No | Guiones medios para unir palabras. |
| docs/07-devops/runbooks/github-copilot-codespaces.md | No | Guiones medios en todo el nombre. |
| docs/07-devops/runbooks/post-create.md | No | Nombre compuesto con guion medio. |
| docs/07-devops/runbooks/reprocesar-etl-fallido.md | No | Guiones medios entre términos. |
| docs/07-devops/runbooks/verificar-servicios.md | No | Guiones medios en el nombre. |
| docs/readme.md | No | Archivo principal sin guiones bajos. |

## Archivos que requieren normalización a guion bajo

Todos los archivos listados actualmente utilizan guiones medios. Será necesario definir una convención (por ejemplo, reemplazar `-` por `_`) y planificar los cambios en conjunto con el ajuste de enlaces internos.

## Propuesta de estructura objetivo (15 secciones + anexos)

```text
docs/
├── 00_vision_y_alcance/
├── 01_gobernanza/
├── 02_requisitos/
├── 03_arquitectura/
├── 04_diseno_detallado/
├── 05_planificacion_y_releases/
├── 06_gestion_de_calidad/
├── 07_devops/
├── 08_datos_y_integraciones/
├── 09_seguridad/
├── 10_operacion_y_monitorizacion/
├── 11_soporte_y_mantenimiento/
├── 12_experiencia_de_usuario/
├── 13_gestion_del_cambio/
├── 14_metrica_y_analytics/
├── 15_roadmap_y_vision_futura/
└── anexos/
    ├── plantillas/
    ├── registros/
    └── referencias/
```

## Próximos pasos sugeridos

1. Acordar la convención definitiva de nombres (guion bajo vs. guion medio) y calendarizar la normalización.
2. Reubicar los documentos existentes en la nueva estructura cuando se valide el mapa objetivo.
3. Actualizar enlaces internos y referencias externas tras los cambios de nombre y ubicación.
4. Crear plantillas y lineamientos para cada sección con el fin de facilitar su adopción.

## Detalle por sección (0-15)

Las siguientes plantillas y lineamientos permiten iniciar la transición hacia la estructura objetivo. Cada sección incluye subsecciones sugeridas, un fragmento reutilizable en formato Markdown, tablas de control, checklists con codificación `WKF-SDLC-XXX` y ejemplos completos. Todas las referencias cruzadas utilizan títulos y anclas compatibles con Markdown estándar.

### 00 - Visión y alcance

#### Estructura sugerida

- Contexto estratégico
- Declaración de visión
- Alcance funcional y tecnológico
- Exclusiones y supuestos
- Business case resumido (referencia cruzada a [Sección 05 - Planificación y releases](#05-planificacion-y-releases))

#### Plantilla base

```markdown
## Contexto estratégico
Describir drivers de negocio, actores clave y objetivos corporativos.

## Visión del producto
Declarar la visión en una frase medible, incluyendo indicadores clave (OKR/KPI).

## Alcance
- **Funcional:** ...
- **Tecnológico:** ...

## Exclusiones y supuestos
- Exclusión 1...
- Supuesto 1...

## Business case resumido
| Ítem | Descripción | Valor estimado |
| --- | --- | --- |
| Problema | ... | ... |
| Beneficios | ... | ... |
| Costos | ... | ... |
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-000 | Contexto estratégico documentado | Pendiente | Revisar resultados de discovery |
| WKF-SDLC-001 | Alcance alineado con stakeholders | En progreso | Vincular con [Sección 13 - Gestión del cambio](#13-gestion-del-cambio) |

#### Checklist WKF

- [ ] WKF-SDLC-002: Validar narrativa de visión con comité directivo.
- [ ] WKF-SDLC-003: Confirmar supuestos críticos con arquitectura empresarial.

#### Ejemplo

> Business case de referencia: Inversión inicial de USD 150k, ROI del 35% anual, payback de 18 meses. Se vincula al roadmap definido en [Sección 15 - Roadmap y visión futura](#15-roadmap-y-vision-futura).

### 01 - Gobernanza

#### Estructura sugerida

- Modelo de gobierno
- Roles y responsabilidades
- Comité de decisiones
- Rituales y cadencias
- Matriz RACI

#### Plantilla base

```markdown
## Modelo de gobierno
Definir órganos de decisión, frecuencia y criterios de escalamiento.

## Roles y responsabilidades
| Rol | Responsable | Suplente | Competencias clave |
| --- | --- | --- | --- |
| ... | ... | ... | ... |

## Cadencias
- Ritual 1: objetivo, asistentes, frecuencia.
- Ritual 2: objetivo, asistentes, frecuencia.

## Matriz RACI
| Actividad | R | A | C | I |
| --- | --- | --- | --- | --- |
| ... | ... | ... | ... | ... |
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-010 | Matriz RACI aprobada | Pendiente | Incorporar participación de Seguridad |
| WKF-SDLC-011 | Comité operativo definido | Completo | Minutas alojadas en [Sección 06 - Gestión de calidad](#06-gestion-de-calidad) |

#### Checklist WKF

- [ ] WKF-SDLC-012: Documentar criterios de escalamiento.
- [ ] WKF-SDLC-013: Publicar calendario de rituales trimestrales.

#### Ejemplo

> Comité de arquitectura se reúne cada miércoles a las 10:00 con representantes de tecnología, negocio y compliance. Las decisiones mayores se registran como ADR en [Sección 03 - Arquitectura](#03-arquitectura).

### 02 - Requisitos

#### Estructura sugerida

- Panorama de stakeholders
- Catálogo de requisitos funcionales
- Catálogo de requisitos no funcionales
- Casos de uso
- Trazabilidad con QA y releases

#### Plantilla base

```markdown
## Stakeholders clave
- Stakeholder 1: intereses, dolores, métricas.

## Requisitos funcionales
| ID | Descripción | Prioridad | Dependencias |
| --- | --- | --- | --- |

## Requisitos no funcionales
| ID | Categoría | Métrica | Umbral |
| --- | --- | --- | --- |

## Casos de uso
### UC-XXX - Título
1. Actor...
2. Flujo principal...
3. Flujo alternativo...

## Trazabilidad
| Requisito | Caso de uso | Prueba asociada | Release |
| --- | --- | --- | --- |
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-020 | Matriz de trazabilidad | En progreso | Cruce pendiente con [Sección 06 - Gestión de calidad](#06-gestion-de-calidad) |
| WKF-SDLC-021 | Inventario de requisitos no funcionales | Pendiente | Mapear dependencias de infraestructura |

#### Checklist WKF

- [ ] WKF-SDLC-022: Validar requisitos con negocio y seguridad.
- [ ] WKF-SDLC-023: Actualizar backlog TDD previo a sprints.

#### Ejemplo

| Caso de uso | UC-004 - Registrar solicitud de financiamiento |
| --- | --- |
| Actor principal | Gestor comercial |
| Precondiciones | Cliente validado en CRM |
| Flujo principal | 1. Captura datos → 2. Valida documentación → 3. Envía a evaluación |
| Flujo alternativo | A. Documentación incompleta → solicita adjuntos |
| Requisitos asociados | RQ-015, RQ-028 |
| Pruebas TDD | `tests/use_cases/test_uc_004.py` |

### 03 - Arquitectura

#### Estructura sugerida

- Principios y restricciones
- Diagrama de contexto
- Diagramas lógicos y físicos
- ADR vigentes
- Estrategia de integraciones

#### Plantilla base

```markdown
## Principios arquitectónicos
- Principio 1...

## Diagramas
![Diagrama de contexto](./img/diagrama-contexto.png)

## ADR relevantes
- ADR-2025-001: ...

## Integraciones
| Sistema origen | Sistema destino | Tipo | SLA |
| --- | --- | --- | --- |
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-030 | Diagrama de despliegue actualizado | Pendiente | Incorporar módulos devops |
| WKF-SDLC-031 | ADR críticos revisados | Completo | Referencia a [Sección 07 - DevOps](#07-devops) |

#### Checklist WKF

- [ ] WKF-SDLC-032: Validar decisiones con seguridad.
- [ ] WKF-SDLC-033: Confirmar compatibilidad con roadmap de datos.

#### Ejemplo

> Integración REST con el core bancario mediante API Gateway, autenticación OAuth2 y latencia objetivo < 300 ms. Documentado en `docs/03-arquitectura/integraciones.md`.

### 04 - Diseño detallado

#### Estructura sugerida

- Diseño lógico por módulo
- Modelos de datos
- Contratos de servicios
- Diagramas de secuencia
- Consideraciones de UX técnica

#### Plantilla base

```markdown
## Módulo: <Nombre>

### Responsabilidades
- ...

### Modelo de datos
| Entidad | Atributos clave | Notas |
| --- | --- | --- |

### Contratos de servicio
```json
{
  "endpoint": "/api/v1/...",
  "método": "POST",
  "request_schema": {},
  "response_schema": {}
}
```

### Diagramas de secuencia
Describir flujos primarios y alternos.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-040 | Diagramas validados | En progreso | Ajustar con [Sección 12 - Experiencia de usuario](#12-experiencia-de-usuario) |
| WKF-SDLC-041 | Contratos publicados | Pendiente | Registrar en catálogo de APIs |

#### Checklist WKF

- [ ] WKF-SDLC-042: Sincronizar modelos con arquitectura de datos.
- [ ] WKF-SDLC-043: Validar endpoints con equipo de QA.

#### Ejemplo

> Diseño del módulo de scoring crediticio con clases `ScoringService`, `RiskAdapter` y `CreditPolicy`. Ver pruebas asociadas en `tests/scoring/test_scoring_service.py`.

### 05 - Planificación y releases

#### Estructura sugerida

- Roadmap macro
- Plan de releases
- Gestión de dependencias
- Business case detallado (alineado con [Sección 00 - Visión y alcance](#00---vision-y-alcance))
- Mecanismo de aprobación

#### Plantilla base

```markdown
## Roadmap macro
| Trimestre | Objetivo | Métrica | Owner |
| --- | --- | --- | --- |

## Plan de releases
| Release | Fecha | Alcance | Indicadores |
| --- | --- | --- | --- |

## Dependencias
- Dependencia crítica...

## Business case detallado
Desglose de costos, beneficios y riesgos.

## Aprobaciones
- Comité: fecha, decisión, responsables.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-105 | Release calendarizado | En progreso | Integrar resultados de UC-004 |
| WKF-SDLC-106 | Dependencias críticas mitigadas | Pendiente | Coordinar con [Sección 08 - Datos e integraciones](#08-datos-e-integraciones) |

#### Checklist WKF

- [ ] WKF-SDLC-107: Validar business case con finanzas.
- [ ] WKF-SDLC-108: Confirmar cobertura mínima TDD del 80% por release.

#### Ejemplo

> Business case: Implementar onboarding digital reduce costo operativo en 25%. Release R1 incluye UC-004 y automatización de evaluación. `ROI` previsto del 40% en 12 meses.

### 06 - Gestión de calidad

#### Estructura sugerida

- Estrategia de QA
- Plan de pruebas
- Automatización
- Métricas y reporting
- Gestión de defectos

#### Plantilla base

```markdown
## Estrategia de QA
Definir niveles, tipos y entornos de prueba.

## Plan de pruebas
| Ciclo | Objetivo | Casos | Métrica |
| --- | --- | --- | --- |

## Automatización
- Frameworks y coverage esperado.

## Gestión de defectos
| ID | Severidad | Estado | Release |
| --- | --- | --- | --- |
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-060 | Coverage TDD ≥ 80% | En progreso | Sincronizar con pipeline de [Sección 07 - DevOps](#07-devops) |
| WKF-SDLC-061 | Reporte de métricas semanal | Pendiente | Automatizar dashboard |

#### Checklist WKF

- [ ] WKF-SDLC-062: Alinear criterios de aceptación con negocio.
- [ ] WKF-SDLC-063: Registrar ejecución en repositorio de evidencias.

#### Ejemplo

> Ejecución Pytest 2025-02-16 con resultados `92%` de cobertura, registrada en `docs/06-qa/registros/2025-02-16-ejecucion-pytest.md`.

### 07 - DevOps

#### Estructura sugerida

- Estrategia CI/CD
- Infraestructura como código
- Observabilidad técnica
- Gestión de entornos
- Runbooks

#### Plantilla base

```markdown
## Estrategia CI/CD
- Pipeline principal...

## Infraestructura como código
| Recurso | Repositorio | Estado | Owner |
| --- | --- | --- | --- |

## Observabilidad
- Métricas, logs y alertas.

## Runbooks
| Incidente | Runbook | Última revisión |
| --- | --- | --- |
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-070 | Pipeline automatizado | Completo | Referencia a `docs/07-devops/runbooks/` |
| WKF-SDLC-071 | Monitoreo base configurado | En progreso | Coordinar con [Sección 10 - Operación y monitorización](#10-operacion-y-monitorizacion) |

#### Checklist WKF

- [ ] WKF-SDLC-072: Validar estrategias de rollback.
- [ ] WKF-SDLC-073: Actualizar runbooks tras cada release.

#### Ejemplo

> Pipeline GitHub Actions con etapas `test → build → deploy`, ejecutando Pytest y verificación de cobertura antes de desplegar al entorno staging.

### 08 - Datos e integraciones

#### Estructura sugerida

- Modelo de datos corporativo
- Estrategia de calidad de datos
- Integraciones y APIs
- Gobierno de datos
- Cumplimiento normativo

#### Plantilla base

```markdown
## Modelo de datos
| Dominio | Fuente | Responsables |
| --- | --- | --- |

## Integraciones
| Sistema | Tipo | Frecuencia | SLA |
| --- | --- | --- | --- |

## Calidad de datos
- Métricas, reglas y reportes.

## Cumplimiento
Listado de normativas aplicables.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-080 | Inventario de integraciones | En progreso | Sincronizar con [Sección 03 - Arquitectura](#03-arquitectura) |
| WKF-SDLC-081 | Reglas de calidad definidas | Pendiente | Priorizar métricas críticas |

#### Checklist WKF

- [ ] WKF-SDLC-082: Validar acuerdos de nivel de servicio con partners.
- [ ] WKF-SDLC-083: Registrar diccionario de datos en repositorio central.

#### Ejemplo

> Integración batch diaria con el sistema de scoring externo `Risk360`, SLA de 2 horas, monitoreo a través de [Sección 10 - Operación y monitorización](#10-operacion-y-monitorizacion).

### 09 - Seguridad

#### Estructura sugerida

- Políticas y estándares
- Gestión de identidades
- Evaluación de riesgos
- Controles técnicos
- Plan de respuesta a incidentes

#### Plantilla base

```markdown
## Políticas aplicables
- Política 1...

## Matriz de riesgos
| Riesgo | Impacto | Probabilidad | Mitigación |
| --- | --- | --- | --- |

## Controles técnicos
- Control 1...

## Plan de respuesta
Pasos detallados, roles y tiempos.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-090 | Análisis de riesgos actualizado | En progreso | Integrar hallazgos de pentesting |
| WKF-SDLC-091 | Runbook de incidentes publicado | Pendiente | Referenciar [Sección 07 - DevOps](#07-devops) |

#### Checklist WKF

- [ ] WKF-SDLC-092: Validar segregación de funciones.
- [ ] WKF-SDLC-093: Ejecutar tabletop de incidentes anual.

#### Ejemplo

> Control MFA obligatorio para gestores comerciales, integrado con el proveedor corporativo de identidad y auditado cada trimestre.

### 10 - Operación y monitorización

#### Estructura sugerida

- Modelo operativo
- Monitoreo de servicios
- Gestión de capacidad
- Procedimientos de soporte N1/N2
- Indicadores operativos

#### Plantilla base

```markdown
## Modelo operativo
Definir horarios, equipos y herramientas.

## Monitoreo
| Servicio | Métrica | Umbral | Acción |
| --- | --- | --- | --- |

## Gestión de capacidad
- Métricas y triggers de escalado.

## Soporte N1/N2
Procedimientos, SLAs y runbooks asociados.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-100 | Panel de monitoreo activo | En progreso | Datos provenientes de [Sección 07 - DevOps](#07-devops) |
| WKF-SDLC-101 | Procedimientos N1 documentados | Pendiente | Entrenar al service desk |

#### Checklist WKF

- [ ] WKF-SDLC-102: Validar umbrales con operaciones.
- [ ] WKF-SDLC-103: Ejecutar simulacro de contingencia.

#### Ejemplo

> Dashboard en Grafana con métricas de disponibilidad (99.5%), tiempo de respuesta y tasa de errores, revisado semanalmente por el equipo operativo.

### 11 - Soporte y mantenimiento

#### Estructura sugerida

- Estrategia de soporte
- Backlog de mantenimiento
- Gestión de incidencias
- Plan de continuidad
- Gestión del conocimiento

#### Plantilla base

```markdown
## Estrategia de soporte
Definir niveles, horarios y acuerdos con proveedores.

## Backlog de mantenimiento
| Ítem | Tipo | Prioridad | Responsable |
| --- | --- | --- | --- |

## Plan de continuidad
Pasos para recuperación y procedimientos.

## Conocimiento
Listar manuales, FAQs y capacitaciones.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-110 | Backlog priorizado | En progreso | Coordinar con [Sección 05 - Planificación y releases](#05-planificacion-y-releases) |
| WKF-SDLC-111 | Plan de continuidad actualizado | Pendiente | Alinear con seguridad |

#### Checklist WKF

- [ ] WKF-SDLC-112: Revisar contratos de soporte externos.
- [ ] WKF-SDLC-113: Actualizar base de conocimiento trimestralmente.

#### Ejemplo

> Plan de mantenimiento correctivo para el módulo de scoring con ventanas los sábados de 02:00 a 04:00, comunicado mediante boletín operativo.

### 12 - Experiencia de usuario

#### Estructura sugerida

- Investigación y personas
- Journey maps
- Lineamientos de diseño
- Pruebas de usabilidad
- Accesibilidad

#### Plantilla base

```markdown
## Personas
| Persona | Objetivos | Dolor | Métrica |
| --- | --- | --- | --- |

## Journey map
- Fases, emociones, oportunidades.

## Lineamientos de diseño
- Componentes clave, bibliotecas.

## Pruebas de usabilidad
Resultados, hallazgos y acciones.

## Accesibilidad
Requisitos WCAG y validaciones.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-120 | Personas validadas | Completo | Alinear con UC-004 |
| WKF-SDLC-121 | Reporte de usabilidad | Pendiente | Programar sesión con usuarios piloto |

#### Checklist WKF

- [ ] WKF-SDLC-122: Incluir métricas de satisfacción.
- [ ] WKF-SDLC-123: Validar criterios de accesibilidad AA.

#### Ejemplo

> Prueba de usabilidad con 5 gestores comerciales mostró reducción del tiempo de captura en UC-004 de 12 a 7 minutos tras rediseñar formularios.

### 13 - Gestión del cambio

#### Estructura sugerida

- Evaluación de impacto
- Plan de comunicación
- Plan de formación
- Gestión de adopción
- Métricas de cambio

#### Plantilla base

```markdown
## Evaluación de impacto
| Área | Impacto | Riesgo | Mitigación |
| --- | --- | --- | --- |

## Plan de comunicación
- Mensaje, canal, audiencia, responsable.

## Plan de formación
Cursos, fechas y materiales.

## Métricas
Adopción, NPS, satisfacción.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-130 | Plan de formación definido | En progreso | Coordinar con [Sección 12 - Experiencia de usuario](#12-experiencia-de-usuario) |
| WKF-SDLC-131 | Métricas de adopción monitoreadas | Pendiente | Integrar con analítica |

#### Checklist WKF

- [ ] WKF-SDLC-132: Preparar kit de comunicación.
- [ ] WKF-SDLC-133: Definir indicadores de adopción trimestral.

#### Ejemplo

> Lanzamiento del módulo UC-004 incluye sesiones de formación en aula virtual, boletín semanal y seguimiento de adopción con encuesta post-uso.

### 14 - Métrica y analytics

#### Estructura sugerida

- Objetivos analíticos
- Métricas clave
- Arquitectura de analítica
- Gobierno de datos analíticos
- Reportes y dashboards

#### Plantilla base

```markdown
## Objetivos analíticos
Declarar hipótesis y decisiones habilitadas.

## Métricas
| Métrica | Descripción | Fuente | Frecuencia |
| --- | --- | --- | --- |

## Arquitectura
Diagramas, herramientas y flujos ETL.

## Reportes
Listar dashboards, responsables y audiencias.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-140 | Definición de métricas clave | En progreso | Incluir indicadores de UC-004 |
| WKF-SDLC-141 | Dashboard operativo publicado | Pendiente | Alinear con [Sección 10 - Operación y monitorización](#10-operacion-y-monitorizacion) |

#### Checklist WKF

- [ ] WKF-SDLC-142: Validar fuentes de datos certificadas.
- [ ] WKF-SDLC-143: Documentar catálogo de dashboards.

#### Ejemplo

> Dashboard mensual con métricas de tasa de aprobación, tiempo promedio de evaluación y conversión de UC-004.

### 15 - Roadmap y visión futura

#### Estructura sugerida

- Horizonte de innovación
- Evolución tecnológica
- Iniciativas estratégicas
- Gestión de riesgos futuros
- Dependencias externas

#### Plantilla base

```markdown
## Horizonte de innovación
| Año | Iniciativa | Valor esperado | Responsable |
| --- | --- | --- | --- |

## Evolución tecnológica
- Tecnologías a adoptar, retirar o evaluar.

## Riesgos futuros
| Riesgo | Impacto | Probabilidad | Acción preventiva |
| --- | --- | --- | --- |

## Dependencias externas
- Regulaciones, proveedores, tendencias.
```

#### Tabla de control

| Identificador | Elemento | Estado | Observaciones |
| --- | --- | --- | --- |
| WKF-SDLC-150 | Roadmap a 3 años | Pendiente | Alinear con visión de [Sección 00 - Visión y alcance](#00---vision-y-alcance) |
| WKF-SDLC-151 | Riesgos emergentes evaluados | En progreso | Coordinar con [Sección 09 - Seguridad](#09-seguridad) |

#### Checklist WKF

- [ ] WKF-SDLC-152: Revisar roadmap semestralmente.
- [ ] WKF-SDLC-153: Actualizar dependencias regulatorias.

#### Ejemplo

> Roadmap 2025-2027 incluye adopción de motor de IA para scoring (2026) y apertura de APIs a partners fintech (2027), sujeto a aprobación del comité de gobernanza.
