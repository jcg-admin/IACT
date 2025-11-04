---
id: DOC-REQ-INDEX
estado: activo
propietario: equipo-producto
fecha_creacion: 2025-11-04
auto_generado: true
relacionados: ["DOC-IMPLEMENTACION-INDEX", "DOC-PROPUESTA-FINAL-REESTRUCTURACION"]
---
# Índices de Requisitos ISO 29148

Este espacio contiene los índices consolidados de requisitos del proyecto IACT, generados automáticamente desde la carpeta `implementacion/`.

## Página padre
- [Índice de espacios documentales](../index.md)

## 🤖 Documentos Auto-Generados

Según [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html), estos documentos se generan automáticamente:

- **BRS** (Business Requirements Specification) - ISO 29148 Clause 9.3
- **StRS** (Stakeholder Requirements Specification) - ISO 29148 Clause 9.4
- **SyRS** (System Requirements Specification) - ISO 29148 Clause 9.5
- **SRS** (Software Requirements Specification) - ISO 29148 Clause 9.6
- **RTM** (Requirements Traceability Matrix)

## ⚠️ NO EDITAR MANUALMENTE

Los archivos en esta carpeta son **auto-generados** mediante GitHub Actions desde los requisitos documentados en:

```
implementacion/
├── backend/requisitos/
├── frontend/requisitos/
└── infrastructure/requisitos/
```

**Cualquier cambio manual será sobrescrito** en la próxima ejecución del workflow.

## 🎯 Source of Truth

El **Source of Truth** para requisitos está en:
- [Implementación - Requisitos](../implementacion/README.md)

## 🔄 Generación Manual

Si necesitas regenerar los índices manualmente:

```bash
# Desde raíz del proyecto
python .github/workflows/scripts/generate_requirements_index.py

# Resultado: docs/requisitos/ actualizado
```

## 📊 Estado Actual

| Documento | Estado | Última generación |
|-----------|--------|-------------------|
| BRS (Business Requirements) | ⏳ Pendiente | No generado aún |
| StRS (Stakeholder Requirements) | ⏳ Pendiente | No generado aún |
| SyRS (System Requirements) | ⏳ Pendiente | No generado aún |
| SRS (Software Requirements) | ⏳ Pendiente | No generado aún |
| RTM (Traceability Matrix) | ⏳ Pendiente | No generado aún |

> **Nota:** Los índices se generarán automáticamente una vez que se documenten requisitos en `implementacion/`.

## 📚 Recursos

### Para Documentar Requisitos
- [Guía de Implementación](../implementacion/README.md)
- [Plantillas de Requisitos](../plantillas/readme.md)
- [Propuesta de Reestructuración](../PROPUESTA_FINAL_REESTRUCTURACION.md)

### Estándares de Referencia
- [BABOK v3](../anexos/glosario_babok_pmbok_iso.md) - Business Analysis Body of Knowledge
- [PMBOK Guide 7th Ed](../anexos/glosario_babok_pmbok_iso.md) - Project Management Body of Knowledge
- ISO/IEC/IEEE 29148:2018 - Systems and software engineering — Life cycle processes — Requirements engineering

## 🔗 Trazabilidad

La trazabilidad completa se mantiene mediante frontmatter YAML en cada requisito:

```yaml
---
id: RF-001
tipo: funcional
trazabilidad_upward:
  - N-001  # Necesidad origen
  - RN-001 # Requisito negocio
trazabilidad_downward:
  - TEST-001  # Tests verificación
---
```

## ✅ Conformidad ISO 29148

Una vez generados, estos índices proporcionarán:
- ✅ Full Conformance con ISO/IEC/IEEE 29148:2018
- ✅ Trazabilidad bidireccional completa
- ✅ Documentación auditable y certificable
- ✅ Separación clara entre requisitos y solución

---

**Última actualización**: 2025-11-04
**Owner**: equipo-producto
**Tipo**: Índice auto-generado
