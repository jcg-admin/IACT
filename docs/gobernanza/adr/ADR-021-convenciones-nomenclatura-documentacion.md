# ADR-021: Convenciones de Nomenclatura para Documentación

**Estado:** Aceptado
**Fecha:** 2025-11-16
**Autores:** Equipo de Arquitectura
**Contexto:** Auditoría de nombres de archivos genéricos

---

## Contexto y Problema

La auditoría de nomenclatura de archivos (AUDITORIA_NOMBRES_ARCHIVOS.md) identificó **80-100 archivos** con nombres problemáticos en la documentación del proyecto IACT:

1. **Archivos con números secuenciales**: `testing_001.md`, `onboarding_002.md`, `deployment_003.md` no indican su contenido
2. **Uso inconsistente de MAYÚSCULAS**: Archivos normales como `AGENTES_SDLC.md`, `ESTRATEGIA_GIT_HOOKS.md` usan MAYÚSCULAS sin ser archivos especiales
3. **Nombres ambiguos/genéricos**: `index.md`, `TODO.md`, `TAREAS_ACTIVAS.md` tienen diferentes convenciones
4. **Prefijos inconsistentes**: `ADR-020-xxx.md` vs `ADR_2025_001_xxx.md`

**Problemas causados:**
- Difícil entender el contenido de un archivo sin abrirlo
- Inconsistencia en nomenclatura entre dominios
- Conflictos entre convenciones (MAYÚSCULAS vs snake_case)
- Búsqueda de documentación ineficiente

**Pregunta clave:** ¿Qué convenciones de nomenclatura deben aplicarse a toda la documentación del proyecto?

---

## Fundamento Teórico: Clean Code Naming Principles

Las convenciones de nomenclatura de este ADR están fundamentadas en los principios de **Clean Code** de Robert C. Martin (Uncle Bob), que aunque fueron escritos originalmente para código, son directamente aplicables a la documentación.

### Principios Aplicables a Nomenclatura de Archivos

#### 1. Usar Nombres que Revelen Intenciones

**Robert Martin**: _"En el software, los nombres son omnipresentes. Aparecen en variables, funciones, argumentos, clases y paquetes. Usamos nombres constantemente. Por ello, debemos hacerlo bien."_

**Aplicación a documentación**:
- ❌ `testing_001.md` - No revela intención
- ✅ `guia_ejecutar_pytest.md` - Revela exactamente qué contiene

**Martin's Definition**: _"El nombre debe indicar por qué existe, qué hace y cómo se usa. Si un nombre requiere un comentario, significa que no revela su cometido."_

#### 2. Evitar la Desinformación

**Martin's Principle**: _"No haga referencia a un grupo de cuentas como accountList a menos que realmente sea una lista. Evite usar nombres con variaciones mínimas."_

**Aplicación a documentación**:
- ❌ `index.md` cuando no es un índice real
- ❌ `TODO.md` y `TAREAS_ACTIVAS.md` para el mismo concepto
- ✅ Nombres precisos que no sugieren características inexistentes

#### 3. Realizar Distinciones con Sentido

**Martin's Warning**: _"No basta con añadir series de números o palabras adicionales. Info y Data son palabras adicionales, como a, an y the."_

**Aplicación a documentación**:
- ❌ `onboarding_001.md`, `onboarding_002.md` - Números sin significado
- ❌ `doc_info.md`, `archivo_data.md` - Palabras sin valor semántico
- ✅ `configurar_entorno_desarrollo.md` - Cada palabra añade valor

#### 4. Usar Nombres que se Puedan Pronunciar

**Martin's Insight**: _"Si no lo puede pronunciar, no podrá explicarlo sin parecer tonto. La programación es una actividad social."_

**Aplicación a documentación**:
- ❌ `AGTS_SDLC.md`, `cfg_env_dev.md` - Abreviaciones impronunciables
- ✅ `agentes_sdlc.md`, `configurar_entorno_desarrollo.md` - Pronunciables

**Beneficio**: Facilita comunicación en reuniones: "Revisa la guía ejecutar pytest" vs "Revisa el testing cero cero uno"

#### 5. Usar Nombres que se Puedan Buscar

**Martin's Rule**: _"Los nombres extensos superan a los breves y cualquier nombre que se pueda buscar supera a una constante. La longitud de un nombre debe corresponderse al tamaño de su ámbito."_

**Aplicación a documentación**:
- ❌ `test.md` - Imposible de buscar (demasiado genérico)
- ❌ `001.md` - No se puede buscar por concepto
- ✅ `guia_ejecutar_pytest.md` - Búsqueda efectiva por `pytest`, `guia`, `ejecutar`

**Equilibrio**: Nombres suficientemente largos para ser únicos, pero no verbosos.

#### 6. Evitar Codificaciones

**Martin's Warning**: _"No parece razonable que todos los nuevos empleados tengan que aprender otro lenguaje de codificación. Los nombres codificados resultan impronunciables."_

**Aplicación a documentación**:
- ❌ `ADR_2025_001_vagrant` - Codificación de año innecesaria
- ❌ `GUIA-ONB-001-CFG` - Requiere aprender sistema de abreviaciones
- ✅ `ADR-001-vagrant-mod-wsgi.md` - Lenguaje natural

#### 7. Evitar Asignaciones Mentales

**Martin's Principle**: _"Los lectores no tienen que traducir mentalmente sus nombres en otros que ya conocen. La claridad es lo que importa."_

**Aplicación a documentación**:
- ❌ `deployment_003.md` - Requiere recordar que "003" = permisos granulares
- ✅ `deployment_implementacion_permisos_granular.md` - Directo

#### 8. Una Palabra por Concepto

**Martin's Consistency Rule**: _"Elija una palabra por cada concepto abstracto y manténgala. Resulta confuso usar fetch, retrieve y get como métodos equivalentes."_

**Aplicación a documentación**:
- ❌ Mezclar `guia_`, `manual_`, `tutorial_` para el mismo tipo de documento
- ❌ `TODO.md` en un lugar, `TAREAS_ACTIVAS.md` en otro, `pendientes.md` en otro
- ✅ Usar consistentemente `guia_` para todas las guías paso a paso

### Principios Arquitecturales Aplicables

Los siguientes principios de Clean Architecture también informan la organización de documentación:

#### 9. Architecture Reveals Intent

**Uncle Bob**: _"Architecture is about intent. The architecture of the building tells you not what it's made of, not what its architectural frameworks were. It tells you its intent."_

**Aplicación**: La estructura de carpetas debe revelar el propósito del dominio, no la tecnología usada.
- ✅ `backend/qa/` - Revela dominio (backend) y propósito (QA)
- ❌ `pytest/` a nivel raíz - Revela herramienta, no propósito

#### 10-13. Dependencies, Use Cases, Testability

Estos principios soportan la decisión de **organizar documentación por dominio** (ADR-020):
- Cada dominio es autónomo en su documentación
- Los casos de uso (requisitos, QA) viven con el dominio que los implementa
- La documentación transversal (gobernanza/) es independiente de implementaciones específicas

---

## Drivers de Decisión

Basados en los principios de Clean Code anteriores:

1. **Descriptividad** (Principios 1, 3): Los nombres deben indicar claramente el contenido
2. **Consistencia** (Principio 8): Una sola convención para toda la documentación
3. **Estándar industria**: Seguir prácticas comunes (snake_case para archivos normales)
4. **Discoverabilidad** (Principio 5): Fácil encontrar archivos por nombre
5. **Pronunciabilidad** (Principio 4): Nombres que se puedan comunicar verbalmente
6. **Claridad sobre brevedad** (Principios 2, 6, 7): Evitar codificaciones y abreviaciones
7. **Prefijos semánticos** (Principio 3): Permitir prefijos descriptivos (`guia_`, `procedimiento_`, `estrategia_`)

---

## Decisión

**Adoptar convenciones de nomenclatura diferenciadas por tipo de archivo:**

### Regla 1: Archivos Especiales (MAYÚSCULAS permitidas)

Archivos reconocidos por herramientas y que tienen significado especial:

```yaml
Archivos Especiales (MAYÚSCULAS):
  - README.md           # Índice de directorio (único por directorio)
  - CHANGELOG.md        # Historial de cambios del proyecto
  - CONTRIBUTING.md     # Guía de contribución
  - LICENSE.md          # Licencia del proyecto
  - ADR-NNN-*.md        # Architecture Decision Records
  - TASK-NNN-*.md       # Issues/Tareas rastreables
  - SPEC-DOMINIO-NNN-*.md  # Especificaciones técnicas
```

**Formato de ADRs:**
```bash
ADR-{número}-{descripción-kebab-case}.md

# Ejemplos:
ADR-020-organizacion-documentacion-por-dominio.md
ADR-021-convenciones-nomenclatura-documentacion.md
```

**Formato de TASKs:**
```bash
TASK-{número}-{descripción-kebab-case}.md

# Ejemplos:
TASK-008-cron-job-dora-mensuales.md
TASK-015-actualizacion-documentacion.md
```

**Formato de SPECs:**
```bash
SPEC-{DOMINIO}-{número}-{descripción}.md

# Ejemplos:
SPEC-INFRA-001-cpython-precompilado.md
SPEC-BACKEND-002-api-autenticacion.md
```

### Regla 2: Archivos Normales (snake_case minúsculas)

Todos los archivos que NO son especiales usan **snake_case minúsculas**:

```bash
# Correcto
estrategia_qa.md
guia_pytest.md
procedimiento_deployment.md
configurar_entorno.md
analisis_congruencia_docs.md

# Incorrecto
ESTRATEGIA_QA.md           # No usar MAYÚSCULAS
estrategiaQA.md            # No usar camelCase
estrategia-qa.md           # No usar kebab-case (reservado para ADRs)
Estrategia_QA.md           # No capitalizar
```

### Regla 3: Prefijos Descriptivos (recomendados)

Usar prefijos para indicar tipo de contenido:

```yaml
Prefijos Recomendados:
  guia_*:           # Guías paso a paso para usuarios
    - guia_ejecutar_pytest.md
    - guia_configurar_entorno.md

  procedimiento_*:  # Procedimientos operativos/administrativos
    - procedimiento_deployment_produccion.md
    - procedimiento_backup_database.md

  estrategia_*:     # Documentos de estrategia/planificación
    - estrategia_qa_global.md
    - estrategia_migracion_cloud.md

  analisis_*:       # Análisis técnicos/investigaciones
    - analisis_performance_backend.md
    - analisis_congruencia_docs.md

  reporte_*:        # Reportes de sesiones/auditorías
    - reporte_ejecucion_task_001.md
    - reporte_auditoria_seguridad.md
```

### Regla 4: Prohibiciones

**NO usar:**

```bash
# ❌ Números secuenciales sin descripción
testing_001.md
onboarding_002.md
deployment_003.md

# ❌ Nombres genéricos
file.md
doc.md
test.md
documento.md

# ❌ MAYÚSCULAS para archivos normales
AGENTES_SDLC.md          → agentes_sdlc.md
ESTRATEGIA_GIT_HOOKS.md  → estrategia_git_hooks.md

# ❌ Mezcla de convenciones
Agentes_SDLC.md
estrategia-Git-Hooks.md
```

### Regla 5: Casos Especiales

**Archivos index.md:**
```bash
# Si es índice de directorio → Renombrar a README.md
infraestructura/index.md  →  infraestructura/README.md

# Si es índice temático específico → Nombre descriptivo
backend/api/index.md  →  backend/api/catalogo_apis.md
```

**Archivos TODO.md:**
```bash
# Estandarizar a TODO.md (reconocido por GitHub)
backend/TODO.md           # ✅ Correcto
TAREAS_ACTIVAS.md         # ❌ Renombrar a TODO.md
pendientes.md             # ❌ Renombrar a TODO.md
```

**Archivos históricos (sesiones/):**
```bash
# Pueden mantener formato original si son históricos
sesiones/2025-11/REPORTE_REORGANIZACION.md  # ✅ Aceptable (histórico)

# Pero preferiblemente usar snake_case para nuevos reportes
sesiones/2025-11/reporte_reorganizacion.md  # ✅ Preferido
```

---

## Alternativas Consideradas

### Alternativa 1: kebab-case para todo (rechazada)

```bash
estrategia-qa.md
guia-pytest.md
procedimiento-deployment.md
```

**Rechazada porque:**
- No es estándar en Python/Django ecosystems (usa snake_case)
- Confusión con ADRs que usan kebab-case
- Menos legible en file browsers que snake_case

### Alternativa 2: MAYÚSCULAS para todo (rechazada)

```bash
ESTRATEGIA_QA.md
GUIA_PYTEST.md
PROCEDIMIENTO_DEPLOYMENT.md
```

**Rechazada porque:**
- No es estándar industria (solo para archivos especiales)
- Dificulta lectura visual (todas MAYÚSCULAS parece "gritar")
- Usuario específicamente prefirió minúsculas: "creo que no debera llamarse solo testing_001"

### Alternativa 3: camelCase (rechazada)

```bash
estrategiaQa.md
guiaPytest.md
procedimientoDeployment.md
```

**Rechazada porque:**
- No es estándar para nombres de archivo
- Incompatible con sistemas case-insensitive
- Dificulta búsqueda por palabras

### Alternativa 4: Sin convención (rechazada)

Permitir cualquier formato según preferencia del autor.

**Rechazada porque:**
- Inconsistencia masiva (ya tenemos 80-100 archivos problemáticos)
- Dificulta mantenimiento y búsqueda
- No escala con múltiples contribuidores

---

## Consecuencias

### Positivas

1. **Descriptividad**: Nombres como `guia_ejecutar_pytest.md` son auto-explicativos
2. **Consistencia**: Una sola convención clara para toda la documentación
3. **Búsqueda eficiente**: Fácil encontrar archivos por prefijo (`guia_*`, `procedimiento_*`)
4. **Compatibilidad**: snake_case compatible con todos los sistemas operativos
5. **Escalabilidad**: Convención clara para nuevos contribuidores
6. **Alineación con código**: Consistente con convenciones Python/Django (snake_case)

### Negativas

1. **Renombrado masivo**: Requiere renombrar 80-100 archivos existentes
2. **Actualizar referencias**: Todos los enlaces internos deben actualizarse
3. **Git history**: Algunos archivos perderán continuidad de historial (mitigado con `git log --follow`)
4. **Esfuerzo de equipo**: Requiere capacitación en nuevas convenciones

### Neutras

1. **Prefijos opcionales**: Recomendados pero no obligatorios
2. **Archivos históricos**: Pueden mantener formato original si es necesario
3. **Transición gradual**: Puede implementarse por fases (críticos primero)

---

## Implementación

### Fase 1: Renombrar Archivos Críticos (Prioridad ALTA)

**Archivos con números secuenciales** - 20 archivos

```bash
# QA/Testing
mv backend/qa/testing_001.md backend/qa/guia_ejecutar_pytest.md
mv frontend/qa/testing_002.md frontend/qa/guia_ejecutar_jest_e2e.md
mv gobernanza/qa/testing_003.md gobernanza/qa/estrategia_test_pyramid.md

# Onboarding
mv gobernanza/onboarding/onboarding_001.md gobernanza/onboarding/configurar_entorno_desarrollo.md
mv gobernanza/onboarding/onboarding_002.md gobernanza/onboarding/ejecutar_proyecto_localmente.md
mv gobernanza/onboarding/onboarding_003.md gobernanza/onboarding/estructura_proyecto_iact.md
mv gobernanza/onboarding/onboarding_004.md gobernanza/onboarding/configurar_variables_entorno.md
mv gobernanza/onboarding/onboarding_005.md gobernanza/onboarding/usar_agentes_sdlc_planning.md
mv gobernanza/onboarding/onboarding_006.md gobernanza/onboarding/validar_documentacion.md
mv gobernanza/onboarding/onboarding_007.md gobernanza/onboarding/generar_indices_requisitos.md
mv gobernanza/onboarding/onboarding_008_agente_atencion_cliente.md gobernanza/onboarding/operaciones_agente_call_center.md

# Deployment (necesita revisión de contenido)
# Ver contenido primero para nombres apropiados
cat devops/deployment/deployment_001.md  # → nombre basado en contenido
cat devops/deployment/deployment_002.md  # → nombre basado en contenido

# Troubleshooting
cat operaciones/troubleshooting/troubleshooting_001.md  # → nombre basado en contenido
```

### Fase 2: Estandarizar MAYÚSCULAS (Prioridad MEDIA)

**Archivos normales en MAYÚSCULAS** - 50-60 archivos

```bash
# Infraestructura
mv infraestructura/ESTRATEGIA_GIT_HOOKS.md infraestructura/estrategia_git_hooks.md
mv infraestructura/WASI_ENVIRONMENT_INTEGRATION.md infraestructura/wasi_environment_integration.md
mv infraestructura/SHELL_SCRIPTS_CONSTITUTION.md infraestructura/shell_scripts_constitution.md
mv infraestructura/STORAGE_ARCHITECTURE.md infraestructura/storage_architecture.md
mv infraestructura/IMPLEMENTATION_REPORT.md infraestructura/implementation_report.md
mv infraestructura/ESTRATEGIA_MIGRACION_SHELL_SCRIPTS.md infraestructura/estrategia_migracion_shell_scripts.md
mv infraestructura/AMBIENTES_VIRTUALIZADOS.md infraestructura/ambientes_virtualizados.md

# Gobernanza/Procesos
mv gobernanza/procesos/AGENTES_SDLC.md gobernanza/procesos/agentes_sdlc.md
mv gobernanza/procesos/DEVOPS_AUTOMATION.md gobernanza/procesos/devops_automation.md
mv gobernanza/procesos/INDICE_WORKFLOWS.md gobernanza/procesos/indice_workflows.md
mv gobernanza/procesos/MAPEO_PROCESOS_TEMPLATES.md gobernanza/procesos/mapeo_procesos_templates.md
mv gobernanza/procesos/SDLC_PROCESS.md gobernanza/procesos/sdlc_process.md

# Backend (16 archivos)
mv backend/ARQUITECTURA-MODULOS-COMPLETA.md backend/arquitectura_modulos_completa.md
mv backend/ANALISIS_CONGRUENCIA_DOCS_CODIGO.md backend/analisis_congruencia_docs_codigo.md
mv backend/CASOS_DE_USO_SISTEMA_PERMISOS.md backend/casos_de_uso_sistema_permisos.md
# ... (resto de archivos backend)

# AI (19+ archivos)
mv ai/ADVANCED_PROMPTING_TECHNIQUES.md ai/advanced_prompting_techniques.md
mv ai/AGENTES_Y_TECNICAS_APLICADAS.md ai/agentes_y_tecnicas_aplicadas.md
mv ai/ANALISIS_POLITICA_NO_EMOJIS.md ai/analisis_politica_no_emojis.md
# ... (resto de archivos AI)
# Mantener: ai/CHANGELOG.md (archivo especial)
```

### Fase 3: Estandarizar ADRs (Prioridad MEDIA)

**ADRs con formato inconsistente** - 10-15 archivos

```bash
# Formato viejo: ADR_YYYY_NNN_xxx → ADR-NNN-xxx
mv infraestructura/ADR_2025_001_vagrant_mod_wsgi.md infraestructura/adr/ADR-001-vagrant-mod-wsgi.md
mv infraestructura/ADR_2025_002_suite_calidad_codigo.md infraestructura/adr/ADR-002-suite-calidad-codigo.md
mv ai/ADR_2025_003_dora_sdlc_integration.md ai/adr/ADR-003-dora-sdlc-integration.md
mv backend/ADR_2025_004_centralized_log_storage.md backend/adr/ADR-004-centralized-log-storage.md
mv backend/ADR_2025_005_grupos_funcionales_sin_jerarquia.md backend/adr/ADR-005-grupos-funcionales-sin-jerarquia.md

# Mover ADRs sueltos a subdirectorio adr/ de cada dominio
```

### Fase 4: Actualizar Referencias (Prioridad ALTA)

```bash
# Buscar todos los enlaces rotos después de renombrados
grep -r "testing_001.md" docs/
grep -r "onboarding_001.md" docs/
grep -r "AGENTES_SDLC.md" docs/

# Actualizar archivos que referencian los renombrados
# (puede automatizarse con script)
```

### Fase 5: Documentar y Comunicar

- [x] Crear ADR-021 (este documento)
- [ ] Actualizar CONTRIBUTING.md con convenciones
- [ ] Crear guía de nomenclatura para nuevos contribuidores
- [ ] Anunciar cambios al equipo
- [ ] Actualizar plantillas de documentación

---

## Validación

Para validar cumplimiento de convenciones:

```bash
# Script de validación (a crear)
python scripts/docs/validar_nomenclatura.py

# Debe reportar:
# - Archivos que no cumplen convenciones
# - Archivos con números secuenciales
# - Archivos normales en MAYÚSCULAS
# - ADRs con formato incorrecto
```

---

## Referencias

- **AUDITORIA_NOMBRES_ARCHIVOS.md** - Auditoría que motivó esta decisión
- **ADR-020** - Organización de documentación por dominio
- **Clean Code** (Robert C. Martin, 2008) - Capítulo 2: Meaningful Names
- **Clean Architecture** (Robert C. Martin, 2017) - Principios de organización por casos de uso
- Discusión: Usuario prefiere minúsculas ("creo que no debera llamarse solo testing_001")
- Estándar Python: PEP 8 recomienda snake_case para nombres de módulos
- Estándar GitHub: README.md, CHANGELOG.md, CONTRIBUTING.md en MAYÚSCULAS

---

## Notas

**Principio fundamental:**

> "Los nombres de archivos deben ser descriptivos, consistentes y seguir estándares de industria. Usar snake_case para archivos normales, MAYÚSCULAS solo para archivos especiales reconocidos por herramientas."

**Excepción histórica:**

Archivos en `sesiones/` pueden mantener formato original si son históricos y no se modifican frecuentemente. Sin embargo, nuevos reportes deben usar snake_case.

**Migración gradual:**

La implementación puede hacerse por fases, priorizando archivos críticos (números secuenciales) antes que estéticos (MAYÚSCULAS → minúsculas).

---

**Aprobado por:** Equipo de Arquitectura
**Fecha de aprobación:** 2025-11-16
**Revisión próxima:** 2026-02-16 (3 meses)
**Relacionado con:** ADR-020 (Organización por dominio)
