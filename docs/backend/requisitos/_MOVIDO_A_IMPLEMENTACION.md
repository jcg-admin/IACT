---
tipo: aviso_migracion
fecha: 2025-11-03
estrategia: Opción B - Separación clara
---

# WARNING AVISO: Requisitos Movidos a `docs/implementacion/`

## [PUNTO] Nueva Ubicación

Los requisitos del backend ahora viven en:

```
docs/backend/requisitos/
├── necesidades/
├── negocio/
├── stakeholders/
├── funcionales/
└── no_funcionales/
```

**👉 [IR A IMPLEMENTACION/BACKEND/REQUISITOS](../../backend/requisitos/README.md)**

---

## OBJETIVO Razón del Cambio

Se implementó **Opción B** de la propuesta de reestructuración:

### Separación Clara de Responsabilidades

| Ubicación | Responsabilidad |
|-----------|-----------------|
| **`docs/implementacion/`** | OK REQUISITOS (N-XXX, RN-XXX, RS-XXX, RF-XXX, RNF-XXX) |
| **`docs/backend/`** | OK DOCUMENTACIÓN TÉCNICA (arquitectura, ADRs, checklists, devops, diseño) |

**Beneficios**:
- OK Source of Truth único para requisitos
- OK No más duplicación entre `docs/requisitos/` y `docs/backend/requisitos/`
- OK Conformidad total con ISO/IEC/IEEE 29148:2018
- OK Escalabilidad y claridad conceptual

---

## 🔄 ¿Qué hacer con archivos legacy aquí?

Esta carpeta (`docs/backend/requisitos/`) contiene archivos legacy:
- `rq_plantilla.md` (antigua plantilla)
- `trazabilidad.md` (será reemplazado por RTM auto-generado)

**Estrategia**:
1. **Nuevos requisitos**: Crear en `docs/backend/requisitos/`
2. **Requisitos existentes**: Mantener aquí temporalmente (read-only)
3. **Migración gradual**: Usar guía de migración cuando sea necesario

---

## INFO Guía de Migración

Si necesitas migrar un requisito legacy a la nueva estructura, consulta:

**[GUÍA DE MIGRACIÓN](../../implementacion/MIGRATION_FROM_LEGACY.md)**

---

## START Crear Nuevo Requisito Backend

```bash
# Ir a la nueva ubicación
cd docs/backend/requisitos/funcionales/

# Copiar template
cp ../../../../plantillas/template_requisito_funcional.md rfXXX_mi_nuevo_requisito.md

# Editar y completar
vim rfXXX_mi_nuevo_requisito.md

# Commit
git add rfXXX_mi_nuevo_requisito.md
git commit -m "feat(req): agregar RF-XXX nuevo requisito"
git push
```

---

## DOCS Recursos

- [Estructura completa](../../implementacion/README.md)
- [Plantillas ISO 29148](../../plantillas/README.md)
- [Glosario BABOK/PMBOK/ISO](../../anexos/glosario_babok_pmbok_iso.md)
- [Propuesta de Reestructuración](../../PROPUESTA_FINAL_REESTRUCTURACION.md)

---

**Fecha de cambio**: 2025-11-03
**Responsable**: equipo-arquitectura
**Estrategia**: Opción B - docs/implementacion/
