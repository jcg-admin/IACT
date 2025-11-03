---
id: DOC-GLOSARIO-STANDARDS
titulo: Glosario Integrado BABOK v3, PMBOK 7th Ed, ISO 29148
version: 1.0.0
fecha_creacion: 2025-11-03
propietario: equipo-ba
relacionados: ["DOC-PROPUESTA-FINAL-REESTRUCTURACION"]
---

# Glosario Integrado: BABOK v3, PMBOK 7th Ed, ISO/IEC/IEEE 29148:2018

Este glosario consolida términos clave de los tres estándares utilizados en el proyecto IACT.

---

## Términos BABOK v3 (Business Analysis Body of Knowledge)

| Término | Definición | Ejemplo en IACT |
|---------|------------|-----------------|
| **Business Need** | Problema u oportunidad que debe abordarse para lograr objetivos organizacionales | N-001: Reducir roturas de stock |
| **Business Requirement (BR)** | Objetivo, meta o resultado de alto nivel que el negocio debe lograr | RN-001: Sistema de alertas automáticas |
| **Stakeholder Requirement (SR)** | Necesidad específica de usuarios, clientes y partes interesadas | RS-001: Gerente necesita alertas en dashboard |
| **Solution Requirement** | Capacidades que debe tener la solución (Funcionales + No Funcionales) | RF-001: API calcular stock mínimo |
| **Functional Requirement (FR)** | Comportamiento, acción o capacidad que el sistema debe realizar | RF-001: Sistema DEBERÁ calcular stock |
| **Non-Functional Requirement (NFR)** | Característica de calidad que el sistema debe poseer | RNF-001: Tiempo respuesta < 200ms |
| **Business Analyst (BA)** | Rol responsable de elicitar, analizar y documentar requisitos | Equipo BA del proyecto IACT |
| **Requirements Traceability** | Relación bidireccional entre requisitos de diferentes niveles | N-001 → RN-001 → RF-001 |

---

## Términos PMBOK Guide 7th Ed (Project Management)

| Término | Definición | Uso en IACT |
|---------|------------|-------------|
| **Project Charter** | Documento que autoriza formalmente el proyecto | Charter para implementación de requisitos |
| **Stakeholder** | Individuo, grupo u organización afectado por el proyecto | Gerentes de compras, analistas, usuarios |
| **Scope** | Trabajo requerido para entregar producto/servicio | Alcance definido en necesidades (N-XXX) |
| **Work Breakdown Structure (WBS)** | Descomposición jerárquica del trabajo | Fases 0-6 de la propuesta |
| **Risk** | Evento incierto que puede impactar objetivos | Riesgos documentados en cada requisito |
| **Deliverable** | Producto, resultado o capacidad entregable | BRS, StRS, SyRS, SRS, RTM |
| **Milestone** | Punto significativo en el cronograma | Hitos en cada fase de migración |
| **Baseline** | Versión aprobada de un artefacto | Baselines en docs/gobernanza/ |

---

## Términos ISO/IEC/IEEE 29148:2018 (Requirements Engineering)

| Término | Definición | Implementación en IACT |
|---------|------------|------------------------|
| **BRS (Business Requirements Specification)** | Documento con requisitos de negocio (Clause 9.3) | `docs/requisitos/brs_business_requirements.md` |
| **StRS (Stakeholder Requirements Specification)** | Documento con requisitos de stakeholders (Clause 9.4) | `docs/requisitos/strs_stakeholder_requirements.md` |
| **SyRS (System Requirements Specification)** | Documento con requisitos de sistema (Clause 9.5) | `docs/requisitos/syrs_system_requirements.md` |
| **SRS (Software Requirements Specification)** | Documento con requisitos de software (Clause 9.6) | `docs/requisitos/srs_software_requirements.md` |
| **RTM (Requirements Traceability Matrix)** | Matriz de trazabilidad bidireccional | `docs/requisitos/matriz_trazabilidad_rtm.md` |
| **Requirement Construct** | Estructura: Subject + Modal Verb + Action + Object + Condition | "El sistema DEBERÁ calcular..." |
| **Verification** | Confirmar que requisito está correctamente especificado | Tests, inspecciones, análisis |
| **Validation** | Confirmar que requisito satisface necesidad real | UAT con stakeholders |
| **Full Conformance** | Cumplir todos los requisitos de Clause 4.2 | Objetivo de la reestructuración |

---

## Jerarquía de Requisitos (Integrada)

```
Objetivos Estratégicos (OE-XXX)
    ↓
Necesidades de Negocio (N-XXX) ← BABOK: Business Need
    ↓
Requisitos de Negocio (RN-XXX) ← BABOK: BR / ISO 29148: BRS (Clause 9.3)
    ↓
Requisitos de Stakeholders (RS-XXX) ← BABOK: SR / ISO 29148: StRS (Clause 9.4)
    ↓
    ├─ Requisitos de Sistema (SyRS) ← ISO 29148: SyRS (Clause 9.5)
    │     ↓
    │  Requisitos Funcionales (RF-XXX) ← BABOK: FR / ISO 29148: SRS (Clause 9.6)
    │     ↓
    └─ Requisitos No Funcionales (RNF-XXX) ← BABOK: NFR / ISO 25010
          ↓
Tests/Casos de Prueba (TEST-XXX)
```

---

## Verbos Modales (ISO 29148 - Clause 5.2.4)

| Verbo Modal | Significado | Uso en IACT |
|-------------|-------------|-------------|
| **SHALL / DEBERÁ** | Requisito obligatorio | "El sistema DEBERÁ validar..." |
| **SHOULD / DEBERÍA** | Requisito recomendado pero no obligatorio | "El sistema DEBERÍA notificar..." |
| **MAY / PUEDE** | Requisito opcional | "El sistema PUEDE incluir..." |
| **MUST NOT / NO DEBERÁ** | Prohibición | "El sistema NO DEBERÁ exponer..." |

---

## Métodos de Verificación (ISO 29148 - Clause 6.5.2.2)

| Método | Descripción | Ejemplo en IACT |
|--------|-------------|-----------------|
| **Test** | Ejecutar el sistema con inputs específicos | Tests automatizados pytest |
| **Inspection** | Examen visual del producto | Code review, revisión de documentación |
| **Analysis** | Uso de modelos analíticos sin ejecutar | Análisis estático, revisión de diseño |
| **Demonstration** | Observación del comportamiento operacional | Demo a stakeholders, UAT |

---

## Abreviaturas Comunes

| Abreviatura | Significado |
|-------------|-------------|
| **BA** | Business Analyst |
| **BABOK** | Business Analysis Body of Knowledge |
| **BR** | Business Requirement |
| **BRS** | Business Requirements Specification |
| **FR** | Functional Requirement |
| **NFR** | Non-Functional Requirement |
| **PMBOK** | Project Management Body of Knowledge |
| **PMO** | Project Management Office |
| **RTM** | Requirements Traceability Matrix |
| **SR** | Stakeholder Requirement |
| **SRS** | Software Requirements Specification |
| **StRS** | Stakeholder Requirements Specification |
| **SyRS** | System Requirements Specification |
| **UAT** | User Acceptance Testing |

---

## Referencias

1. **BABOK® Guide v3** (2015). International Institute of Business Analysis (IIBA)
2. **A Guide to the Project Management Body of Knowledge (PMBOK® Guide)** – 7th Edition (2021). Project Management Institute (PMI)
3. **ISO/IEC/IEEE 29148:2018** - Systems and software engineering — Life cycle processes — Requirements engineering

---

**Nota**: Este glosario debe mantenerse actualizado conforme el proyecto evolucione.

**Última actualización**: 2025-11-03
