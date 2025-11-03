---
id: DOC-IMPLEMENTACION-INDEX
estado: activo
propietario: equipo-arquitectura
fecha_creacion: 2025-11-03
estrategia: Opción B - Separación clara requisitos vs docs técnicas
relacionados: ["DOC-PROPUESTA-FINAL-REESTRUCTURACION"]
---

# 📋 Implementación - Source of Truth para Requisitos

Esta carpeta contiene **todos los requisitos del proyecto IACT**, organizados por dominio técnico y siguiendo estándares BABOK v3, PMBOK 7th Ed e ISO/IEC/IEEE 29148:2018.

---

## 🎯 Separación Clara de Responsabilidades

### ✅ `docs/implementacion/` = **REQUISITOS**
- Necesidades de negocio (N-XXX)
- Requisitos de negocio (RN-XXX)
- Requisitos de stakeholders (RS-XXX)
- Requisitos funcionales (RF-XXX)
- Requisitos no funcionales (RNF-XXX)
- Documentación de tests relacionados

### ✅ `docs/backend/`, `docs/frontend/`, `docs/infrastructure/` = **DOCUMENTACIÓN TÉCNICA**
- Arquitectura y ADRs
- Checklists operativos
- DevOps y runbooks
- Diseño detallado
- Gobernanza y políticas
- QA y estrategias de testing

**Regla de oro**: Si es un requisito (describe QUÉ debe hacer el sistema) → va en `implementacion/`. Si es documentación técnica (describe CÓMO funciona) → va en `backend/`, `frontend/`, `infrastructure/`.

---

## 📁 Estructura

```
docs/implementacion/
│
├── backend/                           ★ Owner: equipo-backend
│   ├── requisitos/
│   │   ├── necesidades/               ← N-001, N-002 (Business Needs)
│   │   ├── negocio/                   ← RN-001 (Business Requirements)
│   │   ├── stakeholders/              ← RS-001 (Stakeholder Requirements)
│   │   ├── funcionales/               ← RF-001, RF-002 (Functional)
│   │   └── no_funcionales/            ← RNF-001 (Non-Functional)
│   ├── diseño/                        ← Documentos de diseño detallado
│   └── tests/                         ← Documentación de estrategia de tests
│
├── frontend/                          ★ Owner: equipo-frontend
│   ├── requisitos/
│   │   ├── necesidades/               ← Enlaza a backend (no duplica)
│   │   ├── negocio/                   ← RN específicos frontend
│   │   ├── stakeholders/              ← RS específicos frontend
│   │   ├── funcionales/               ← RF específicos frontend
│   │   └── no_funcionales/            ← RNF específicos frontend
│   └── tests/                         ← Docs de tests frontend
│
└── infrastructure/                    ★ Owner: equipo-devops
    ├── requisitos/
    │   ├── necesidades/               ← Enlaza a backend (no duplica)
    │   ├── negocio/                   ← RN específicos infra
    │   ├── funcionales/               ← RF específicos infra
    │   └── no_funcionales/            ← RNF específicos infra
    └── tests/                         ← Docs de tests infra
```

---

## 📝 Convenciones de Nombrado

| Tipo | Prefijo | Ejemplo | Template |
|------|---------|---------|----------|
| Necesidad | N-XXX | `n001_reducir_roturas_stock.md` | [template_necesidad.md](../plantillas/template_necesidad.md) |
| Req. Negocio | RN-XXX | `rn001_sistema_alertas.md` | [template_requisito_negocio.md](../plantillas/template_requisito_negocio.md) |
| Req. Stakeholder | RS-XXX | `rs001_alertas_gerente.md` | [template_requisito_stakeholder.md](../plantillas/template_requisito_stakeholder.md) |
| Req. Funcional | RF-XXX | `rf001_api_calcular_stock.md` | [template_requisito_funcional.md](../plantillas/template_requisito_funcional.md) |
| Req. No Funcional | RNF-XXX | `rnf001_performance_200ms.md` | [template_requisito_no_funcional.md](../plantillas/template_requisito_no_funcional.md) |

---

## 🔗 Trazabilidad (Obligatoria)

Cada requisito **DEBE** incluir frontmatter YAML con trazabilidad:

```yaml
---
id: RF-001
tipo: funcional
titulo: API para cálculo de stock mínimo
dominio: backend

# Trazabilidad Upward (de dónde viene)
trazabilidad_upward:
  - N-001  # Necesidad que origina
  - RN-001 # Req. negocio relacionado
  - RS-001 # Req. stakeholder relacionado

# Trazabilidad Downward (qué genera)
trazabilidad_downward:
  - TEST-001  # Tests que verifican
  - TEST-002
  - TASK-123  # Tareas de implementación
---
```

---

## 🤖 Generación Automática de Índices ISO 29148

Los índices se generan **automáticamente** en `docs/requisitos/` mediante GitHub Actions:

- **BRS** (Business Requirements Specification) - ISO 29148 Clause 9.3
- **StRS** (Stakeholder Requirements Specification) - ISO 29148 Clause 9.4
- **SyRS** (System Requirements Specification) - ISO 29148 Clause 9.5
- **SRS** (Software Requirements Specification) - ISO 29148 Clause 9.6
- **RTM** (Requirements Traceability Matrix)

**⚠️ NO edite manualmente** los archivos en `docs/requisitos/` - son auto-generados.

### Generación Manual

```bash
# Desde raíz del proyecto
python .github/workflows/scripts/generate_requirements_index.py

# Resultado: docs/requisitos/ actualizado
```

---

## 📚 Recursos

### Plantillas
- [Template Necesidad](../plantillas/template_necesidad.md)
- [Template Req. Negocio](../plantillas/template_requisito_negocio.md)
- [Template Req. Stakeholder](../plantillas/template_requisito_stakeholder.md)
- [Template Req. Funcional](../plantillas/template_requisito_funcional.md)
- [Template Req. No Funcional](../plantillas/template_requisito_no_funcional.md)

### Guías
- [Glosario BABOK/PMBOK/ISO](../anexos/glosario_babok_pmbok_iso.md)
- [Propuesta de Reestructuración](../PROPUESTA_FINAL_REESTRUCTURACION.md)

---

## 🔄 Migración desde Estructura Legacy

Si tienes requisitos en `docs/backend/requisitos/` (estructura antigua), consulta la [Guía de Migración](MIGRATION_FROM_LEGACY.md).

**Estrategia**: Los requisitos legacy coexisten temporalmente. Nuevos requisitos van en `implementacion/`. Migración gradual.

---

## 🚀 Cómo Crear un Nuevo Requisito

### 1. Identificar el tipo de requisito
- ¿Es una necesidad de negocio? → `necesidades/`
- ¿Es un objetivo de negocio? → `negocio/`
- ¿Es necesidad de un stakeholder? → `stakeholders/`
- ¿Es funcionalidad del sistema? → `funcionales/`
- ¿Es característica de calidad? → `no_funcionales/`

### 2. Elegir el dominio
- ¿Backend, Frontend, Infrastructure?

### 3. Copiar template correspondiente

```bash
# Ejemplo: Crear requisito funcional backend
cd docs/implementacion/backend/requisitos/funcionales/
cp ../../../../../plantillas/template_requisito_funcional.md rf001_mi_requisito.md
```

### 4. Completar el frontmatter YAML
- ID único
- Trazabilidad upward/downward
- Owner, prioridad, estado

### 5. Commit y push
- El workflow regenerará índices automáticamente

---

## ✅ Checklist para Nuevos Requisitos

- [ ] ID único asignado (no duplicado)
- [ ] Frontmatter YAML completo
- [ ] Trazabilidad upward documentada
- [ ] Criterios de aceptación definidos (Gherkin)
- [ ] Método de verificación especificado
- [ ] Template correcto usado
- [ ] Archivo nombrado correctamente (`rfXXX_descripcion.md`)
- [ ] Stakeholders identificados
- [ ] Tests asociados referenciados

---

## 📊 Métricas

Para ver estadísticas de requisitos:

```bash
# Contar requisitos por tipo
find docs/implementacion -name "n0*.md" | wc -l  # Necesidades
find docs/implementacion -name "rn*.md" | wc -l  # Req. Negocio
find docs/implementacion -name "rf*.md" | wc -l  # Req. Funcionales
```

O consulta los índices auto-generados en `docs/requisitos/`.

---

**Última actualización**: 2025-11-03
**Owner**: equipo-arquitectura
**Estrategia**: Opción B - Separación clara requisitos vs documentación técnica
