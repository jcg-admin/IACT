---
id: DOC-IMPL-BACKEND-REQ
dominio: backend
owner: equipo-backend
fecha_creacion: 2025-11-03
---

# Requisitos del Dominio Backend

**Source of Truth** para todos los requisitos relacionados con el backend del proyecto IACT.

---

## 📁 Estructura

| Carpeta | Contenido | IDs |
|---------|-----------|-----|
| **necesidades/** | Necesidades de negocio que originan requisitos backend | N-001, N-002, ... |
| **negocio/** | Requisitos de negocio específicos del backend | RN-001, RN-002, ... |
| **stakeholders/** | Requisitos de stakeholders del backend | RS-001, RS-002, ... |
| **funcionales/** | Requisitos funcionales del backend | RF-001, RF-002, ... |
| **no_funcionales/** | Requisitos no funcionales del backend | RNF-001, RNF-002, ... |

---

## 🎯 Responsabilidad

Las **necesidades de negocio** (N-XXX) se documentan aquí en backend porque:
- Backend es el dominio principal del sistema IACT
- Frontend e Infrastructure **enlazan** a estas necesidades (no duplican)
- Un solo source of truth para cada necesidad

---

## ✅ Convenciones

### Nombres de Archivo
```
necesidades/n001_reducir_roturas_stock.md
negocio/rn001_sistema_alertas_automaticas.md
stakeholders/rs001_alertas_para_gerente_compras.md
funcionales/rf001_api_calcular_stock_minimo.md
no_funcionales/rnf001_tiempo_respuesta_200ms.md
```

### Estructura del Frontmatter
```yaml
---
id: RF-001
tipo: funcional
titulo: [Título conciso]
dominio: backend
owner: equipo-backend
prioridad: [critica|alta|media|baja]
estado: [propuesto|aprobado|en_desarrollo|implementado|verificado]

trazabilidad_upward:
  - N-001
  - RN-001

trazabilidad_downward:
  - TEST-001

stakeholders:
  - [stakeholder-1]
---
```

---

## 🔗 Trazabilidad Típica Backend

```
N-001: Reducir roturas de stock
  └─ RN-001: Sistema de alertas automáticas
      ├─ RS-001: Gerente necesita alertas en dashboard
      │   └─ RF-001: API calcular stock mínimo
      │       └─ RNF-001: Tiempo respuesta < 200ms
      │           └─ TEST-001: Test performance API
      └─ RF-002: Servicio notificación email
          └─ RNF-002: Disponibilidad 99.9%
```

---

## 🚀 Crear Nuevo Requisito Backend

```bash
# 1. Navegar a la carpeta correcta
cd docs/implementacion/backend/requisitos/funcionales/

# 2. Copiar template
cp ../../../../plantillas/template_requisito_funcional.md rf999_nuevo_requisito.md

# 3. Editar con tu editor favorito
vim rf999_nuevo_requisito.md

# 4. Completar frontmatter y contenido

# 5. Commit y push
git add rf999_nuevo_requisito.md
git commit -m "feat(req): agregar RF-999 nuevo requisito backend"
git push
```

Los índices ISO 29148 se regenerarán automáticamente.

---

## 📚 Plantillas

- [Necesidad](../../../plantillas/template_necesidad.md)
- [Req. Negocio](../../../plantillas/template_requisito_negocio.md)
- [Req. Stakeholder](../../../plantillas/template_requisito_stakeholder.md)
- [Req. Funcional](../../../plantillas/template_requisito_funcional.md)
- [Req. No Funcional](../../../plantillas/template_requisito_no_funcional.md)

---

**Owner**: equipo-backend
