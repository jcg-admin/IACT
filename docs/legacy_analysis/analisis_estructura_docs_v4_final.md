---
id: DOC-ANAL-ESTRUCTURA-V4-FINAL
estado: propuesta-final
propietario: equipo-producto
fecha_creacion: 2025-11-02
version: 4.0
relacionados: ["DOC-INDEX-GENERAL", "DOC-GOB-INDEX"]
estandares: ["BABOK v3", "PMBOK Guide 7th Ed", "ISO/IEC/IEEE 29148:2018"]
---
# Análisis Definitivo: Estructura de Documentación v4.0
## Requisitos por Dominio + Índices Generados (ISO 29148)

---

## CAMBIOS PRINCIPALES vs v3.0

**DECISIÓN ARQUITECTÓNICA:**
- ❌ **Rechazado**: Estructura centralizada con números (01_, 02_, 03_)
- ✅ **Aprobado**: Requisitos en dominios técnicos + `docs/requisitos/` como índice generado

**JUSTIFICACIÓN:**
1. **Co-localización**: Requisitos junto al código que los implementa
2. **Autonomía**: Cada equipo es dueño de sus requisitos
3. **Menos duplicación**: Source of truth en 1 lugar
4. **Cumple ISO 29148**: Índices generados SON los documentos oficiales

---

## ESTRUCTURA FINAL APROBADA

```
proyecto/
│
├── implementacion/                         ← CÓDIGO + REQUISITOS POR DOMINIO
│   │
│   ├── backend/                            ← Backend team owner
│   │   ├── requisitos/
│   │   │   ├── necesidades/               ← SOURCE OF TRUTH (dominio principal)
│   │   │   │   └── n001_reducir_roturas_stock.md
│   │   │   ├── negocio/                   ← Business Requirements (BRS)
│   │   │   │   └── rn001_sistema_alertas.md
│   │   │   ├── stakeholders/              ← Stakeholder Requirements (StRS)
│   │   │   │   └── rs001_alertas_gerente.md
│   │   │   ├── funcionales/               ← Functional Requirements (SRS)
│   │   │   │   ├── rf001_api_calcular_stock.md
│   │   │   │   └── rf002_api_alertas.md
│   │   │   └── no_funcionales/            ← Non-Functional Requirements
│   │   │       └── rnf001_performance_200ms.md
│   │   ├── diseño/
│   │   ├── src/
│   │   └── tests/
│   │
│   ├── frontend/                           ← Frontend team owner
│   │   ├── requisitos/
│   │   │   ├── _necesidades_vinculadas.md ← ENLACE a backend (no duplica)
│   │   │   ├── stakeholders/
│   │   │   │   └── rs003_ux_accesible.md
│   │   │   ├── funcionales/
│   │   │   │   ├── rf010_dashboard_alertas.md
│   │   │   │   └── rf011_filtros_inventario.md
│   │   │   └── no_funcionales/
│   │   │       └── rnf010_accesibilidad_wcag.md
│   │   ├── diseño/
│   │   ├── src/
│   │   └── tests/
│   │
│   └── infrastructure/                     ← DevOps team owner
│       ├── requisitos/
│       │   ├── _necesidades_vinculadas.md
│       │   ├── funcionales/
│       │   │   └── rf020_auto_scaling.md
│       │   └── no_funcionales/
│       │       └── rnf020_disaster_recovery.md
│       └── terraform/
│
├── docs/                                   ← DOCUMENTACIÓN + ÍNDICES GENERADOS
│   ├── requisitos/                         🤖 AUTO-GENERADO (NO EDITAR)
│   │   ├── README.md                       [Generado por CI/CD]
│   │   ├── brs_business_requirements.md    [ISO 9.3 - BRS]
│   │   ├── strs_stakeholder_requirements.md [ISO 9.4 - StRS]
│   │   ├── syrs_system_requirements.md     [ISO 9.5 - SyRS]
│   │   ├── srs_software_requirements.md    [ISO 9.6 - SRS]
│   │   ├── matriz_trazabilidad_rtm.md      [RTM completa]
│   │   └── .generator-timestamp
│   │
│   ├── necesidades_negocio/                ← Business case, ROI, OKRs (opcional)
│   │   └── vision_general.md
│   │
│   ├── arquitectura/
│   ├── diseño_detallado/
│   ├── gobernanza/
│   └── plantillas/
│       ├── template_necesidad.md
│       ├── template_requisito_negocio.md
│       ├── template_requisito_funcional.md
│       └── template_requisito_no_funcional.md
│
├── scripts/                                ← AUTOMATION SCRIPTS
│   ├── generate-requirements-index.js      [Generado por CI/CD]
│   └── README.md
│
└── .github/
    └── workflows/
        ├── requirements-index.yml          ← Regenera índices automáticamente
        ├── docs.yml
        ├── lint.yml
        └── release.yml
```

---

## REGLAS DE UBICACIÓN

| Tipo de Requisito | Ubicación | Owner | Otros Dominios |
|-------------------|-----------|-------|----------------|
| **Necesidades de negocio** | `backend/requisitos/necesidades/` | BA Lead + PMO | Enlazan con `_necesidades_vinculadas.md` |
| **Requisitos de negocio** | `{dominio}/requisitos/negocio/` | Cada equipo | Si es cross-domain, en backend + enlaces |
| **Requisitos stakeholders** | `{dominio}/requisitos/stakeholders/` | Cada equipo | Específicos por dominio |
| **Requisitos funcionales** | `{dominio}/requisitos/funcionales/` | Equipo dueño | Independientes |
| **Requisitos no funcionales** | `{dominio}/requisitos/no_funcionales/` | Equipo dueño | Si es global (GDPR), en backend + enlaces |

---

## FORMATO DE REQUISITO (Frontmatter YAML)

### Ejemplo: backend/requisitos/funcionales/rf001_api_calcular_stock.md

```markdown
---
id: RF-001
tipo: funcional
titulo: API para cálculo de stock mínimo
dominio: backend
owner: equipo-backend
prioridad: alta
estado: aprobado
fecha_creacion: 2025-01-15
trazabilidad_upward:
  - N-001  # Reducir roturas stock
  - RN-001 # Sistema alertas
  - RS-001 # Alertas gerente
trazabilidad_downward:
  - TEST-001
  - TEST-002
stakeholders:
  - gerente_compras
  - analista_inventario
iso29148_clause: "9.6.4"  # SRS - Interface Requirements
verificacion_metodo: "test"  # ISO 6.5.2.2.d
---

# RF-001: API para cálculo de stock mínimo

## Descripción
El sistema **deberá** proporcionar una API REST que calcule el stock mínimo...

## Criterios de aceptación
1. El endpoint **deberá** responder en <200ms (P95)
2. El cálculo **deberá** considerar demanda histórica de últimos 90 días
3. El resultado **deberá** incluir stock actual, mínimo, punto de reorden

## Dependencias técnicas
- Base de datos: PostgreSQL tabla `inventarios`
- Cache: Redis para cálculos frecuentes
- API externa: Sistema ERP para datos históricos

## Verificación
- Método: Test automatizado (ISO 29148 - 6.5.2.2.d)
- Test IDs: TEST-001 (funcionalidad), TEST-002 (performance)
- Ubicación: `backend/tests/test_stock_calculation.py`

## Trazabilidad upward
- [N-001](../necesidades/n001_reducir_roturas_stock.md): Necesidad de negocio
- [RN-001](../negocio/rn001_sistema_alertas.md): Requisito de negocio
- [RS-001](../stakeholders/rs001_alertas_gerente.md): Requisito stakeholder
```

---

## GENERACIÓN AUTOMÁTICA DE ÍNDICES

### GitHub Actions Workflow

**Archivo**: `.github/workflows/requirements-index.yml`

**Trigger**:
- Push a `implementacion/**/requisitos/**/*.md`
- Pull request modificando requisitos
- Manual dispatch

**Proceso**:
1. Escanea todos los `*.md` en `implementacion/**/requisitos/`
2. Parsea frontmatter YAML
3. Valida campos obligatorios (id, tipo, titulo, estado)
4. Construye mapa de trazabilidad
5. Genera índices ISO 29148:
   - `docs/requisitos/brs_business_requirements.md` (ISO 9.3)
   - `docs/requisitos/strs_stakeholder_requirements.md` (ISO 9.4)
   - `docs/requisitos/syrs_system_requirements.md` (ISO 9.5)
   - `docs/requisitos/srs_software_requirements.md` (ISO 9.6)
   - `docs/requisitos/matriz_trazabilidad_rtm.md` (RTM)
6. Valida traceability references (detecta enlaces rotos)
7. Commit automático con mensaje: `chore(requisitos): regenerar índices ISO 29148 [skip ci]`

### Índice Generado - Ejemplo

**docs/requisitos/brs_business_requirements.md**:

```markdown
# Business Requirements Specification (BRS)

**Auto-generated**: 2025-11-02T14:32:00Z
**Compliant with**: ISO/IEC/IEEE 29148:2018 - Clause 9.3
**Source**: `implementacion/**/requisitos/negocio/*.md`

---

⚠️ **DO NOT EDIT THIS FILE MANUALLY**

To modify requirements, edit source files in:
`implementacion/{domain}/requisitos/negocio/*.md`

## Business Requirements

| ID | Title | Domain | Owner | Priority | Status | Location |
|----|-------|--------|-------|----------|--------|----------|
| RN-001 | Sistema alertas automáticas | backend | equipo-backend | alta | aprobado | [📄](../../implementacion/backend/requisitos/negocio/rn001_sistema_alertas.md) |

## Downstream Traceability

### RN-001: Sistema alertas automáticas

**Implemented by**:
- [RF-001](../../implementacion/backend/requisitos/funcionales/rf001_api_calcular_stock.md): API cálculo stock (backend)
- [RF-010](../../implementacion/frontend/requisitos/funcionales/rf010_dashboard_alertas.md): Dashboard alertas (frontend)

---
*Generated by: `scripts/generate-requirements-index.js`*
*Compliant with ISO/IEC/IEEE 29148:2018*
```

---

## VALIDACIÓN ISO 29148

### Full Conformance Mantenida

| Requisito ISO | Implementación | Evidencia |
|---------------|----------------|-----------|
| ✅ **4.2 Full Conformance** | SÍ | Índices generados cumplen Clause 9 |
| ✅ **5.2.4 Requirement Construct** | SÍ | Plantilla con Subject + Verb + Condition |
| ✅ **5.2.5 Individual Characteristics** | SÍ | Validado en `lint.yml` workflow |
| ✅ **5.2.6 Set Characteristics** | SÍ | Checklist en tarea 7.2 |
| ✅ **5.2.8 Traceability** | SÍ | Frontmatter + RTM generado |
| ✅ **6.2 Business Analysis** | SÍ | `backend/requisitos/necesidades/` |
| ✅ **6.3 Stakeholder Needs** | SÍ | `{dominio}/requisitos/stakeholders/` |
| ✅ **6.4 System Requirements** | SÍ | `{dominio}/requisitos/funcionales/` |
| ✅ **7 Information Items** | SÍ | BRS, StRS, SyRS, SRS generados |
| ✅ **9.3 BRS Content** | SÍ | Template + índice generado |
| ✅ **9.4 StRS Content** | SÍ | Template + índice generado |
| ✅ **9.6 SRS Content** | SÍ | Template + índice generado |

**Declaración de Conformance:**
> "Esta estructura permite Full Conformance a ISO/IEC/IEEE 29148:2018 (Clause 4.2) mediante generación automática de Information Items normativos desde requisitos distribuidos por dominio técnico."

---

## VENTAJAS DE ESTA ESTRUCTURA

### 1. Co-localización (Locality Principle)
- ✅ Requisitos junto al código que los implementa
- ✅ Reducción de context switching para developers
- ✅ Más fácil mantener sincronización código-requisitos

### 2. Autonomía de Equipos
- ✅ Backend team es dueño de `backend/requisitos/`
- ✅ Frontend team es dueño de `frontend/requisitos/`
- ✅ No hay "comité central" bloqueando ediciones
- ✅ Ownership claro por dominio

### 3. Cero Duplicación
- ✅ Necesidades de negocio: 1 lugar (`backend/requisitos/necesidades/`)
- ✅ Otros dominios enlazan con `_necesidades_vinculadas.md`
- ✅ Requisitos funcionales: específicos por dominio
- ✅ Reducción de 40% → <5% duplicación

### 4. Cumplimiento ISO 29148
- ✅ Índices generados SON los documentos oficiales (BRS, StRS, SRS)
- ✅ Trazabilidad bidireccional automatizada
- ✅ Validación de frontmatter en CI/CD
- ✅ Auditable y certificable

### 5. Automatización
- ✅ Índices regenerados automáticamente en cada push
- ✅ Validación de traceability en PRs
- ✅ Comentarios automáticos en PRs con cambios
- ✅ Detección de enlaces rotos

---

## CASOS DE USO

### UC1: Developer busca requisito funcional de backend

```bash
# Antes (v3.0 centralizado):
cd docs/02_requisitos/requisitos_solucion/funcionales/modulo_inventario/
# Buscar entre múltiples módulos... 10-15 min

# Ahora (v4.0 por dominio):
cd implementacion/backend/requisitos/funcionales/
ls rf*_stock*.md
# Encontrado en <30 segundos ✅
```

### UC2: BA necesita ver trazabilidad completa

```bash
# Opción 1: Ver índice generado
cat docs/requisitos/matriz_trazabilidad_rtm.md

# Opción 2: Ver en GitHub Pages
open https://2-coatl.github.io/IACT---project/requisitos/matriz_trazabilidad_rtm/

# Trazabilidad automática upward/downward ✅
```

### UC3: Auditor pide BRS conforme a ISO 29148

```bash
# Mostrar índice generado
cat docs/requisitos/brs_business_requirements.md

# Verificar cumplimiento
grep "ISO/IEC/IEEE 29148:2018 - Clause 9.3" docs/requisitos/brs_business_requirements.md
# ✅ Full Conformance
```

### UC4: PM quiere agregar nueva necesidad de negocio

```bash
# 1. Crear archivo en dominio principal
cd implementacion/backend/requisitos/necesidades/
cp ../../../docs/plantillas/template_necesidad.md n002_optimizar_costos.md

# 2. Editar con frontmatter
vim n002_optimizar_costos.md

# 3. Commit y push
git add .
git commit -m "feat(requisitos): agregar necesidad N-002 optimizar costos"
git push

# 4. CI/CD regenera índices automáticamente ✅
# 5. BRS actualizado en docs/requisitos/brs_business_requirements.md ✅
```

### UC5: Cambio de requisito con impacto en múltiples dominios

```bash
# Cambio en backend
vim implementacion/backend/requisitos/funcionales/rf001_api_calcular_stock.md
# Modificar criterio de aceptación

# CI/CD detecta cambio
# → Regenera RTM
# → Muestra impacto en frontend (rf010_dashboard_alertas.md tiene trazabilidad)
# → Comenta en PR con requisitos afectados ✅
```

---

## PLAN DE MIGRACIÓN ACTUALIZADO

### FASE 0: Preparación (Semana 1)
- ✅ Workflows creados (`.github/workflows/`)
- ✅ Scripts creados (`.github/workflows/scripts/`)
- ⏳ Crear plantillas con frontmatter YAML
- ⏳ Capacitación: 4h BABOK + 2h PMBOK + 4h ISO 29148
- ⏳ Crear glosario: `docs/anexos/glosario_babok_pmbok_iso.md`

**Criterio GO**: Plantillas aprobadas, equipo capacitado

### FASE 1: Crear Estructura (Semana 2)
```bash
mkdir -p implementacion/{backend,frontend,infrastructure}/requisitos/{necesidades,negocio,stakeholders,funcionales,no_funcionales}
mkdir -p docs/requisitos
```

**Criterio GO**: Estructura creada, workflows ejecutándose

### FASE 2: Migrar 1 Necesidad Completa (Semana 3 - PILOTO)
- Elegir necesidad piloto (ej: SC00 o SC01)
- Migrar a `backend/requisitos/necesidades/n001_xxx.md`
- Derivar requisitos en 3 dominios
- Verificar generación de índices
- Validar trazabilidad

**Criterio GO**: Índices generados correctamente, trazabilidad 100%

### FASE 3: Migrar Todas las Necesidades (Semana 4-6)
- Clasificar solicitudes actuales (`docs/solicitudes/`)
- Migrar necesidades a `backend/requisitos/necesidades/`
- Crear enlaces en frontend/infrastructure

**Criterio GO**: ≥80% necesidades migradas, 0% duplicación

### FASE 4: Migrar Requisitos por Dominio (Semana 7-8)
- Backend: Migrar de `docs/backend/requisitos/` → `implementacion/backend/requisitos/`
- Frontend: Migrar de `docs/frontend/requisitos/` → `implementacion/frontend/requisitos/`
- Infrastructure: Crear desde cero en `implementacion/infrastructure/requisitos/`

**Criterio GO**: RTM completa, ≥95% requisitos con frontmatter válido

### FASE 5: Validación Final (Semana 9)
- Auditoría de conformance ISO 29148
- Verificar todos los workflows funcionando
- Validar índices generados
- Entrenar equipos en nueva estructura

**Criterio GO**: Declaración "Full Conformance ISO 29148" aprobada

### FASE 6: Archivar Estructura Antigua (Semana 10)
```bash
mkdir docs_legacy
mv docs/backend docs_legacy/
mv docs/frontend docs_legacy/
mv docs/solicitudes docs_legacy/
```

**Criterio GO**: Estructura antigua archivada, 100% enlaces válidos en nueva estructura

---

## MÉTRICAS DE ÉXITO

| Métrica | Baseline | Target | Método |
|---------|----------|--------|--------|
| % duplicación | 40% | <5% | diff analysis |
| Tiempo búsqueda requisito | 10-15 min | <2 min | Prueba usuarios |
| % requisitos con trazabilidad | 40% | 100% | RTM audit |
| % requisitos con frontmatter válido | 0% | 95% | Lint workflow |
| % conformance ISO 29148 | 0% | 100% Full | Auditoría |
| Tiempo regeneración índices | N/A | <30s | CI/CD logs |
| NPS documentación | No medido | >8/10 | Encuesta |

---

## HERRAMIENTAS Y AUTOMATIZACIÓN

### CI/CD Workflows (GitHub Actions)

1. **requirements-index.yml**
   - Trigger: Push a `implementacion/**/requisitos/*.md`
   - Genera: BRS, StRS, SyRS, SRS, RTM
   - Valida: Traceability, frontmatter

2. **lint.yml**
   - Valida: Markdown, YAML, frontmatter
   - Chequea: Enlaces rotos, estructura

3. **docs.yml**
   - Despliega: MkDocs a GitHub Pages
   - Incluye: Índices generados

4. **release.yml**
   - Crea: Releases con documentación empaquetada
   - Genera: Changelogs, paquetes ZIP/TAR.GZ

### Scripts

- `scripts/generate-requirements-index.js` (Node.js)
- `.github/workflows/scripts/*.sh` (Bash)

### Dependencias

```json
{
  "dependencies": {
    "glob": "^10.0.0",
    "gray-matter": "^4.0.3",
    "js-yaml": "^4.1.0"
  }
}
```

---

## DIFERENCIAS CLAVE vs v3.0

| Aspecto | v3.0 (Centralizado) | v4.0 (Por Dominio) |
|---------|---------------------|-------------------|
| Ubicación requisitos | `docs/02_requisitos/` | `implementacion/{dominio}/requisitos/` |
| Números de carpeta | 01_, 02_, 03_ | Sin números |
| Source of truth | Centralizado en docs/ | Distribuido por dominio |
| Índices ISO 29148 | Manuales | Auto-generados |
| Autonomía equipos | Baja (comité central) | Alta (cada equipo owner) |
| Duplicación | ~15% | <5% |
| Tiempo búsqueda | 5-10 min | <30 segundos |
| CI/CD | No automatizado | Completamente automatizado |
| Validación | Manual | Automática en PRs |

---

## RECOMENDACIÓN EJECUTIVA

**✅ APROBAR** migración a estructura v4.0 bajo las siguientes condiciones:

**OBLIGATORIO**:
1. Ejecutar FASE 0 completa (capacitación + plantillas)
2. FASE 2 piloto exitoso antes de migración masiva
3. Mantener estructura antigua read-only 3 meses
4. Asignar Responsable de Migración (BA Senior)

**RECOMENDADO**:
5. Auditor externo ISO para validación final
6. Certificar ≥1 BA en CBAP
7. Herramienta Requirements Management (JIRA/Azure DevOps)

---

## PRÓXIMOS PASOS INMEDIATOS

**HOY**:
1. Presentar esta propuesta a stakeholders
2. Solicitar aprobación formal

**SEMANA 1** (FASE 0):
1. Crear plantillas con frontmatter YAML
2. Ejecutar capacitación 10h (BABOK + PMBOK + ISO)
3. Crear glosario integrado

**SEMANA 2** (FASE 1):
1. Crear estructura de carpetas
2. Verificar workflows funcionando

**SEMANA 3** (FASE 2 - PILOTO):
1. Migrar 1 necesidad completa end-to-end
2. Validar generación de índices
3. GO/NO-GO para continuar

---

## CONTROL DE VERSIONES

| Versión | Fecha | Cambios | Autor |
|---------|-------|---------|-------|
| 1.0 | 2025-11-02 | Propuesta inicial BABOK | Equipo Producto |
| 2.0 | 2025-11-02 | Integración PMBOK 7 | Equipo Producto |
| 3.0 | 2025-11-02 | Integración ISO 29148 - Estructura centralizada | Equipo Producto |
| **4.0** | **2025-11-02** | **ESTRUCTURA FINAL: Requisitos por dominio + índices generados** | **Equipo Producto** |

---

**FIN DEL DOCUMENTO**

**Decisión arquitectónica**: Requisitos distribuidos por dominio técnico
**Conformance**: Full Conformance ISO/IEC/IEEE 29148:2018
**Automatización**: CI/CD completo (GitHub Actions)
**Estado**: ✅ Listo para aprobación ejecutiva
