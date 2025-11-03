---
id: DOC-IMPLEMENTACION-INDEX
estado: activo
propietario: equipo-arquitectura
fecha_creacion: 2025-11-03
relacionados: ["DOC-PROPUESTA-FINAL-REESTRUCTURACION"]
---

# Documentación de Implementación - IACT Project

Esta carpeta contiene la documentación de requisitos organizada por dominio técnico, siguiendo la propuesta de reestructuración ISO 29148 + BABOK v3.

## 📋 Estructura

```
implementacion/
├── backend/              ← Requisitos del dominio backend
│   ├── requisitos/
│   │   ├── necesidades/      ← N-XXX (Business Needs)
│   │   ├── negocio/          ← RN-XXX (Business Requirements)
│   │   ├── stakeholders/     ← RS-XXX (Stakeholder Requirements)
│   │   ├── funcionales/      ← RF-XXX (Functional Requirements)
│   │   └── no_funcionales/   ← RNF-XXX (Non-Functional Requirements)
│   ├── diseño/               ← Documentos de diseño detallado
│   └── tests/                ← Documentación de tests
│
├── frontend/             ← Requisitos del dominio frontend
│   ├── requisitos/
│   │   ├── _necesidades_vinculadas.md  ← Enlaces a necesidades (no duplica)
│   │   ├── stakeholders/
│   │   ├── funcionales/
│   │   └── no_funcionales/
│   └── tests/
│
└── infrastructure/       ← Requisitos del dominio infrastructure
    ├── requisitos/
    │   ├── _necesidades_vinculadas.md  ← Enlaces a necesidades (no duplica)
    │   ├── funcionales/
    │   └── no_funcionales/
    └── tests/
```

## 🎯 Principios de Organización

### 1. Requisitos por Dominio
- Cada dominio técnico (backend, frontend, infrastructure) tiene sus propios requisitos
- Evita duplicación masiva manteniendo requisitos cerca del código que los implementa

### 2. Source of Truth
- Las **necesidades de negocio** viven en `backend/requisitos/necesidades/`
- Frontend e Infrastructure **enlazan** a estas necesidades (no duplican)
- Cada requisito funcional/no funcional está en UN solo lugar

### 3. Trazabilidad
- Cada requisito usa frontmatter YAML con `trazabilidad_upward` y `trazabilidad_downward`
- Los índices ISO 29148 se generan automáticamente en `docs/requisitos/`

## 📝 Uso de Plantillas

Para crear nuevos requisitos, use las plantillas en `docs/plantillas/`:

- `template_necesidad.md` → Para N-XXX
- `template_requisito_negocio.md` → Para RN-XXX
- `template_requisito_stakeholder.md` → Para RS-XXX
- `template_requisito_funcional.md` → Para RF-XXX
- `template_requisito_no_funcional.md` → Para RNF-XXX

## 🤖 Automatización

Los índices en `docs/requisitos/` se regeneran automáticamente mediante GitHub Actions cuando se modifica cualquier requisito en esta carpeta.

**NO edite manualmente los archivos en `docs/requisitos/`** - son auto-generados.

## 📚 Referencias

- [Propuesta de Reestructuración](../PROPUESTA_FINAL_REESTRUCTURACION.md)
- [Glosario BABOK/PMBOK/ISO](../anexos/glosario_babok_pmbok_iso.md)
- [Plantillas](../plantillas/readme.md)

---

**Última actualización**: 2025-11-03
