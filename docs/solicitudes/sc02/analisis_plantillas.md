---
id: DOC-SOL-SC02-ANALISIS-PLANTILLAS
estado: completado
propietario: equipo-backend
fecha: 2025-11-04
relacionados: ["DOC-SOL-SC02", "DOC-PLANTILLAS-INDEX"]
---
# SC02 - Análisis de plantillas para documentación de API

## Resumen ejecutivo

Análisis de las plantillas disponibles en `docs/plantillas/` para determinar cuáles son apropiadas para documentar la carpeta `api/` del proyecto IACT, y qué plantillas adicionales se requieren.

## Plantillas disponibles (29 plantillas)

### Categorización por tipo

#### Producto y alcance
- plantilla_project_charter.md
- plantilla_business_case.md
- plantilla_stakeholder_analysis.md

#### Requisitos y análisis
- plantilla_srs.md
- plantilla_regla_negocio.md
- plantilla_caso_de_uso.md
- plantilla_caso_prueba.md
- template_necesidad.md
- template_requisito_funcional.md
- template_requisito_negocio.md
- template_requisito_no_funcional.md
- template_requisito_stakeholder.md

#### Diseño y arquitectura
- ✅ **plantilla_sad.md** - Software Architecture Document
- ✅ **plantilla_tdd.md** - Technical Design Document
- ✅ **plantilla_database_design.md** - Diseño de base de datos
- ✅ **plantilla_api_reference.md** - Referencia de APIs

#### Infraestructura y despliegue
- plantilla_deployment_guide.md
- plantilla_setup_entorno.md

#### QA y soporte
- plantilla_plan_pruebas.md
- plantilla_setup_qa.md
- plantilla_runbook.md
- plantilla_troubleshooting.md

#### Gestión y planificación
- plantilla_project_management_plan.md
- plantilla_release_plan.md
- plantilla_registro_actividad.md

#### Documentación corporativa
- plantilla_espacio_documental.md
- plantilla_seccion_limitaciones.md
- plantilla_manual_usuario.md
- plantilla_ui_ux.md
- readme.md

## Plantillas que usaré para SC02

### 1. ✅ plantilla_tdd.md - Technical Design Document
**Uso**: Documentar cada aplicación Django en detalle

**Aplicación**:
- Un TDD por cada app Django (ETL, Analytics, Reports, etc.)
- Secciones útiles:
  - Propósito y alcance del módulo
  - Arquitectura detallada (diagramas UML)
  - Interfaces (servicios, APIs internas)
  - Modelado de datos (modelos Django)
  - Plan de pruebas técnicas

**Archivos a crear**:
- `docs/backend/diseno_detallado/tdd_etl.md`
- `docs/backend/diseno_detallado/tdd_analytics.md`
- `docs/backend/diseno_detallado/tdd_reports.md`
- etc.

**Estado**: ✅ Adecuada - Cubre la mayoría de necesidades

---

### 2. ✅ plantilla_database_design.md - Database Design
**Uso**: Documentar modelos de datos consolidados

**Aplicación**:
- Documento único con todos los modelos Django
- Diagramas ER por app y consolidado
- Documentar database router y multi-database
- Relaciones entre modelos

**Archivos a crear**:
- `docs/backend/diseno_detallado/database_design.md`

**Estado**: ✅ Adecuada - Perfecta para modelos Django

---

### 3. ⚠️ plantilla_api_reference.md - API Reference
**Uso**: Documentar endpoints REST (futuro)

**Aplicación**:
- Actualmente el proyecto NO tiene APIs REST expuestas
- Útil para cuando se implemente Django REST Framework
- Por ahora, documentar APIs internas entre servicios

**Archivos a crear** (futuro):
- `docs/backend/diseno_detallado/api_reference.md`

**Estado**: ⚠️ Básica - Requiere expansión para APIs internas

**Observación**: La plantilla actual es muy simple, solo tiene:
- Introducción
- Autenticación
- Endpoints (tabla)
- Ejemplos
- Errores
- Versionado

---

### 4. ✅ plantilla_sad.md - Software Architecture Document
**Uso**: Documentar arquitectura general de las apps

**Aplicación**:
- Vista general del monolito modular
- Diagramas de contexto
- Componentes y responsabilidades
- Vistas de despliegue

**Archivos a crear**:
- `docs/backend/arquitectura/arquitectura_apps.md`

**Estado**: ✅ Adecuada

---

### 5. ✅ plantilla_troubleshooting.md - Troubleshooting
**Uso**: Guías de resolución de problemas

**Aplicación**:
- Troubleshooting de ETL
- Problemas comunes en procesamiento
- Errores de integración con IVR

**Archivos a crear**:
- `docs/backend/arquitectura/troubleshooting_etl.md`

**Estado**: ✅ Adecuada

---

## Plantillas que ME FALTAN

### 1. ❌ plantilla_django_app.md - Django Application Documentation
**Necesidad**: Alta
**Razón**: Las apps Django tienen componentes específicos que no están bien cubiertos por TDD

**Secciones propuestas**:
```markdown
# Plantilla Django App Documentation

## 1. Información general
- Nombre de la app
- Propósito y responsabilidad
- Dependencias con otras apps

## 2. Modelos (models.py)
- Lista de modelos
- Campos y tipos
- Relaciones
- Managers personalizados
- Meta opciones

## 3. Servicios (services.py)
- Lista de servicios de negocio
- Métodos principales
- Contratos de entrada/salida
- Excepciones que puede lanzar

## 4. Vistas (views.py) - si aplica
- Lista de vistas/viewsets
- Endpoints
- Permisos requeridos

## 5. URLs (urls.py) - si aplica
- Patrones de URL
- Namespace

## 6. Comandos de management
- Lista de comandos
- Argumentos
- Ejemplos de uso

## 7. Signals y receivers
- Signals emitidos
- Signals escuchados

## 8. Tests
- Estrategia de testing
- Coverage actual
- Tests importantes

## 9. Configuración
- Variables de entorno requeridas
- Settings específicos

## 10. Diagramas
- Diagrama de componentes
- Diagrama de secuencia (flujos principales)
```

**Estado**: ❌ No existe - DEBE CREARSE

---

### 2. ❌ plantilla_service_layer.md - Service Layer Documentation
**Necesidad**: Media
**Razón**: Los servicios de negocio son componentes clave que merecen documentación específica

**Secciones propuestas**:
```markdown
# Plantilla Service Layer Documentation

## 1. Servicio
- Nombre del servicio
- Responsabilidad
- Ubicación (módulo/clase)

## 2. Métodos públicos
- Firma del método
- Descripción
- Parámetros
- Retorno
- Excepciones
- Ejemplo de uso

## 3. Dependencias
- Otros servicios utilizados
- Modelos accedidos
- APIs externas consumidas

## 4. Flujos de negocio
- Diagrama de secuencia
- Reglas de negocio aplicadas

## 5. Consideraciones
- Performance
- Transacciones
- Caché
```

**Estado**: ❌ No existe - RECOMENDABLE CREAR

---

### 3. ❌ plantilla_etl_job.md - ETL Job Documentation
**Necesidad**: Alta (específico para este proyecto)
**Razón**: El ETL es crítico para el negocio y tiene componentes únicos

**Secciones propuestas**:
```markdown
# Plantilla ETL Job Documentation

## 1. Información del Job
- Nombre del job
- Propósito
- Frecuencia de ejecución
- Duración estimada

## 2. Fuente de datos
- Base de datos origen
- Tablas/vistas consultadas
- Filtros aplicados
- Volumen de datos aproximado

## 3. Transformaciones
- Reglas de transformación
- Agregaciones
- Cálculos
- Validaciones

## 4. Destino
- Tablas de destino
- Estrategia de carga (insert, upsert, truncate+load)

## 5. Dependencias
- Jobs que deben ejecutarse antes
- Jobs que dependen de este

## 6. Monitoreo
- Métricas de éxito
- Alertas configuradas
- Logs importantes

## 7. Recuperación ante fallos
- Estrategia de retry
- Rollback
- Procedimiento de reproceso manual
```

**Estado**: ❌ No existe - MUY NECESARIA

---

### 4. ❌ plantilla_django_command.md - Django Management Command
**Necesidad**: Media
**Razón**: Los comandos de management son importantes para operaciones

**Secciones propuestas**:
```markdown
# Plantilla Django Management Command

## 1. Comando
- Nombre del comando
- Propósito
- App que lo contiene

## 2. Uso
```bash
python manage.py <comando> [opciones]
```

## 3. Argumentos
- Posicionales
- Opcionales (flags)
- Valores por defecto

## 4. Ejemplos
- Casos de uso comunes
- Combinaciones de argumentos

## 5. Comportamiento
- Qué hace el comando
- Efectos secundarios
- Validaciones

## 6. Consideraciones
- Seguridad (¿se puede ejecutar en producción?)
- Performance
- Idempotencia
```

**Estado**: ❌ No existe - ÚTIL

---

## Plantillas con limitaciones actuales

### plantilla_api_reference.md - Demasiado básica

**Estado actual**: Solo 6 secciones simples
**Limitaciones**:
- No cubre APIs internas (servicios Python)
- No documenta contratos de servicio
- No incluye ejemplos de código Python
- Enfocada solo en REST APIs HTTP

**Mejoras necesarias**:
```markdown
# Plantilla API Reference (Mejorada)

## 1. Introducción
- Descripción del servicio/módulo
- Contexto de uso
- Audiencia

## 2. Arquitectura
- Diagrama de componentes
- Capas de la API

## 3. Autenticación y autorización
- Métodos de autenticación
- Permisos requeridos
- Roles

## 4. Endpoints REST (si aplica)
| Método | Ruta | Descripción | Auth | Parámetros | Respuesta |

## 5. APIs internas / Servicios
- Clases de servicio
- Métodos públicos
- Contratos (tipo hints)
- Ejemplos de uso en Python

## 6. Modelos de datos
- DTOs
- Schemas
- Validaciones

## 7. Ejemplos completos
- Uso desde código Python
- Uso desde HTTP (curl/requests)
- Casos de uso end-to-end

## 8. Errores y excepciones
- Tabla de códigos HTTP
- Excepciones Python personalizadas
- Manejo de errores

## 9. Versionado
- Estrategia de versionado
- Cambios breaking vs non-breaking
- Deprecación

## 10. Performance
- Rate limiting
- Caché
- Optimizaciones

## 11. Testing
- Cómo probar la API
- Mocks disponibles
- Fixtures
```

---

## Análisis de gaps y recomendaciones

### Plantillas CRÍTICAS que faltan para SC02

| Plantilla | Prioridad | Razón | Acción |
|-----------|-----------|-------|---------|
| plantilla_django_app.md | 🔴 Alta | Estructura específica de Django no cubierta | Crear AHORA |
| plantilla_etl_job.md | 🔴 Alta | ETL es crítico para el negocio | Crear AHORA |
| Mejora a plantilla_api_reference.md | 🟡 Media | Actual muy básica | Mejorar después |
| plantilla_service_layer.md | 🟡 Media | Servicios son componentes clave | Crear si hay tiempo |
| plantilla_django_command.md | 🟢 Baja | Nice to have | Opcional |

### Plantillas existentes SUFICIENTES

| Plantilla | Evaluación | Uso en SC02 |
|-----------|------------|-------------|
| plantilla_tdd.md | ✅ Buena | Documentar diseño técnico por app |
| plantilla_database_design.md | ✅ Buena | Modelos Django consolidados |
| plantilla_sad.md | ✅ Buena | Arquitectura general |
| plantilla_troubleshooting.md | ✅ Buena | Guías de troubleshooting ETL |

## Propuesta de acción

### Opción 1: Crear plantillas nuevas ANTES de documentar
**Pros**: Documentación más estructurada y homogénea
**Contras**: Retrasa inicio de documentación de apps
**Tiempo**: +1-2 días

### Opción 2: Documentar usando plantillas existentes + adaptaciones
**Pros**: Comenzar documentación inmediatamente
**Contras**: Menos homogeneidad, puede requerir refactoring después
**Tiempo**: 0 días de overhead

### Opción 3: Crear solo las plantillas CRÍTICAS (Híbrido - RECOMENDADO)
**Pros**: Balance entre estructura y velocidad
**Contras**: Requiere 1 día de preparación
**Tiempo**: +1 día

**Plantillas a crear**:
1. plantilla_django_app.md (3-4 horas)
2. plantilla_etl_job.md (2-3 horas)

**Plantillas a mejorar**:
- Ninguna en esta fase (hacerlo después)

## Decisión recomendada

**OPCIÓN 3: Crear plantillas críticas primero**

### Justificación:
1. Django apps son el 100% de lo que vamos a documentar → necesitamos plantilla específica
2. ETL es componente crítico con estructura única → merece plantilla propia
3. Con estas 2 plantillas + las existentes (TDD, Database Design, SAD) cubrimos el 95% de necesidades
4. Inversión de 1 día ahorra semanas de refactoring después

### Plan de ejecución:
1. **Hoy**: Crear plantilla_django_app.md y plantilla_etl_job.md
2. **Mañana**: Comenzar documentación de apps Fase 1 (ETL, Analytics, Reports)
3. **Futuro**: Mejorar plantilla_api_reference.md cuando tengamos REST APIs

## Anexo: Estructura propuesta para nuevas plantillas

Ver propuestas detalladas en secciones "Plantillas que ME FALTAN" arriba.

---

**Conclusión**: Necesitamos crear 2 plantillas críticas antes de comenzar SC02 para asegurar documentación de calidad y evitar refactoring futuro.
