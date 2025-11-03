---
id: DOC-IMPL-BACKEND-REQ
dominio: backend
owner: equipo-backend
fecha_creacion: 2025-11-03
---

# Requisitos del Dominio Backend

Esta carpeta contiene todos los requisitos relacionados con el backend del proyecto IACT.

## 📁 Estructura

- **necesidades/** - Necesidades de negocio (N-XXX) que originan requisitos backend
- **negocio/** - Requisitos de negocio (RN-XXX) específicos del backend
- **stakeholders/** - Requisitos de stakeholders (RS-XXX) del backend
- **funcionales/** - Requisitos funcionales (RF-XXX) del backend
- **no_funcionales/** - Requisitos no funcionales (RNF-XXX) del backend

## ✅ Convenciones de Nombres

- **Necesidades**: `nXXX_descripcion_corta.md` (ej: `n001_reducir_roturas_stock.md`)
- **Req. Negocio**: `rnXXX_descripcion_corta.md`
- **Req. Stakeholders**: `rsXXX_descripcion_corta.md`
- **Req. Funcionales**: `rfXXX_descripcion_corta.md`
- **Req. No Funcionales**: `rnfXXX_descripcion_corta.md`

## 🔗 Trazabilidad

Cada requisito debe incluir en su frontmatter:

```yaml
trazabilidad_upward:
  - N-XXX  # Necesidad que origina
  - RN-XXX # Req. negocio relacionado

trazabilidad_downward:
  - TEST-XXX  # Tests que verifican
  - TASK-XXX  # Tareas de implementación
```

## 🚀 Próximos Pasos

1. Migrar requisitos existentes de `docs/backend/requisitos/` a esta estructura
2. Asegurar que cada requisito use el template correspondiente
3. Validar trazabilidad completa

---

Owner: **equipo-backend**
