---
id: DOC-PLANTILLAS-README
titulo: Plantillas de Requisitos ISO 29148
version: 1.0.0
fecha_creacion: 2025-11-06
propietario: equipo-ba
estandares: ["BABOK v3", "PMBOK Guide 7th Ed", "ISO/IEC/IEEE 29148:2018"]
---

# Plantillas de Requisitos

Este directorio contiene las plantillas oficiales para documentar requisitos en el proyecto IACT, conforme a **BABOK v3**, **PMBOK 7th Ed** e **ISO/IEC/IEEE 29148:2018**.

---

## Plantillas Disponibles

### 1. Necesidades de Negocio (Business Needs)
**Archivo**: [`template_necesidad.md`](./template_necesidad.md)
**Uso**: Documentar problemas u oportunidades que deben abordarse
**Ubicación**: `implementacion/backend/requisitos/necesidades/`
**Prefijo ID**: `N-XXX`
**Estándar**: BABOK v3 + ISO 29148 Clause 6.2

```bash
# Crear nueva necesidad
cp docs/plantillas/template_necesidad.md \
   implementacion/backend/requisitos/necesidades/n001_reducir_roturas_stock.md
```

---

### 2. Requisitos de Negocio (Business Requirements)
**Archivo**: [`template_requisito_negocio.md`](./template_requisito_negocio.md)
**Uso**: Objetivos o metas de alto nivel que el negocio debe lograr
**Ubicación**: `implementacion/{dominio}/requisitos/negocio/`
**Prefijo ID**: `RN-XXX`
**Estándar**: ISO 29148 Clause 9.3 (BRS)

```bash
# Crear requisito de negocio
cp docs/plantillas/template_requisito_negocio.md \
   implementacion/backend/requisitos/negocio/rn001_sistema_alertas.md
```

---

### 3. Requisitos de Stakeholders
**Archivo**: [`template_requisito_stakeholder.md`](./template_requisito_stakeholder.md)
**Uso**: Necesidades específicas de usuarios y partes interesadas
**Ubicación**: `implementacion/{dominio}/requisitos/stakeholders/`
**Prefijo ID**: `RS-XXX`
**Estándar**: ISO 29148 Clause 9.4 (StRS)

```bash
# Crear requisito de stakeholder
cp docs/plantillas/template_requisito_stakeholder.md \
   implementacion/backend/requisitos/stakeholders/rs001_alertas_gerente.md
```

---

### 4. Requisitos Funcionales (Functional Requirements)
**Archivo**: [`template_requisito_funcional.md`](./template_requisito_funcional.md)
**Uso**: Comportamientos, acciones o capacidades que el sistema debe realizar
**Ubicación**: `implementacion/{dominio}/requisitos/funcionales/`
**Prefijo ID**: `RF-XXX`
**Estándar**: ISO 29148 Clause 9.6 (SRS)

```bash
# Crear requisito funcional
cp docs/plantillas/template_requisito_funcional.md \
   implementacion/backend/requisitos/funcionales/rf001_api_calcular_stock.md
```

---

### 5. Requisitos No Funcionales (Non-Functional Requirements)
**Archivo**: [`template_requisito_no_funcional.md`](./template_requisito_no_funcional.md)
**Uso**: Características de calidad que el sistema debe poseer
**Ubicación**: `implementacion/{dominio}/requisitos/no_funcionales/`
**Prefijo ID**: `RNF-XXX`
**Estándar**: ISO 29148 + ISO 25010

```bash
# Crear requisito no funcional
cp docs/plantillas/template_requisito_no_funcional.md \
   implementacion/backend/requisitos/no_funcionales/rnf001_tiempo_respuesta.md
```

---

## Jerarquía y Trazabilidad

```
N-001: Necesidad de Negocio
  ↓
RN-001: Requisito de Negocio (¿QUÉ debe lograr el negocio?)
  ↓
RS-001: Requisito de Stakeholder (¿QUÉ necesitan los usuarios?)
  ↓
  ├─ RF-001: Requisito Funcional (¿QUÉ debe hacer el sistema?)
  └─ RNF-001: Requisito No Funcional (¿CÓMO debe comportarse?)
       ↓
    TEST-001: Casos de Prueba
```

---

## Checklist de Uso de Plantillas

Cuando cree un nuevo requisito:

- [ ] **Copiar** la plantilla correspondiente al directorio correcto
- [ ] **Renombrar** el archivo: `{prefijo}{numero}_{descripcion_corta}.md`
- [ ] **Completar frontmatter YAML** (todos los campos obligatorios)
- [ ] **Asignar ID único** en el proyecto
- [ ] **Documentar trazabilidad upward** (de dónde viene)
- [ ] **Usar verbos modales** correctos (DEBERÁ/DEBERÍA/PUEDE)
- [ ] **Definir criterios de aceptación** verificables
- [ ] **Especificar método de verificación** (test/inspection/analysis/demonstration)
- [ ] **Obtener aprobaciones** requeridas
- [ ] **Actualizar trazabilidad downward** cuando se deriven requisitos/tests
- [ ] **Commit** con mensaje descriptivo

---

## Reglas de Frontmatter YAML

### Campos Obligatorios (TODAS las plantillas):
```yaml
---
id: [PREFIJO]-[XXX]           # Único en el proyecto
tipo: [necesidad|negocio|stakeholder|funcional|no_funcional]
titulo: [Título descriptivo]
dominio: [backend|frontend|infrastructure]
owner: [equipo-propietario]
prioridad: [critica|alta|media|baja]
estado: [propuesto|en_revision|aprobado|en_desarrollo|implementado]
fecha_creacion: [YYYY-MM-DD]
trazabilidad_upward: []       # IDs de requisitos padre
trazabilidad_downward: []     # IDs de requisitos hijo
stakeholders: []
iso29148_clause: "[X.X]"
---
```

### Campos Opcionales (según tipo):
- `verificacion_metodo`: test|inspection|analysis|demonstration
- `sprint_target`: SPRINT-XX
- `estimacion_esfuerzo`: story points
- `categoria`: ui|api|business-logic|integration|etc.
- `breaking_change`: si|no

---

## Automatización CI/CD

Los requisitos creados con estas plantillas alimentan:

1. **Workflow de Índices ISO** (`.github/workflows/requirements-index.yml`)
   - Genera automáticamente: BRS, StRS, SyRS, SRS, RTM
   - Ubicación: `docs/requisitos/`

2. **Workflow de Validación** (`.github/workflows/lint.yml`)
   - Valida frontmatter YAML
   - Detecta IDs duplicados
   - Verifica enlaces de trazabilidad

3. **Índices Generados** (READ-ONLY):
   - `docs/requisitos/brs_business_requirements.md`
   - `docs/requisitos/strs_stakeholder_requirements.md`
   - `docs/requisitos/syrs_system_requirements.md`
   - `docs/requisitos/srs_software_requirements.md`
   - `docs/requisitos/matriz_trazabilidad_rtm.md`

---

## Recursos Adicionales

- **Glosario**: [docs/anexos/glosario_babok_pmbok_iso.md](../anexos/glosario_babok_pmbok_iso.md)
- **Propuesta de Reestructuración**: [docs/anexos/analisis_nov_2025/PROPUESTA_FINAL_REESTRUCTURACION.md](../anexos/analisis_nov_2025/PROPUESTA_FINAL_REESTRUCTURACION.md)
- **Guía ISO 29148**: [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html)
- **BABOK v3**: [IIBA BABOK Guide](https://www.iiba.org/standards-and-resources/babok/)
- **PMBOK 7th Ed**: [PMI PMBOK Guide](https://www.pmi.org/pmbok-guide-standards)

---

## Soporte

Para dudas sobre el uso de plantillas:
- **BA Lead**: Responsable de requisitos y estándares
- **PMO**: Procesos y gobernanza
- **Tech Lead**: Aspectos técnicos de implementación

---

**Última actualización**: 2025-11-06
**Versión**: 1.0.0
**Conformance**: Full ISO/IEC/IEEE 29148:2018 (Clause 4.2)
