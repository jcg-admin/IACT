---
id: DOC-QA-GUIA-ESTRUCTURA
estado: borrador
propietario: lider-qa
ultima_actualizacion: 2025-02-25
relacionados: ["CHECK-AUDIT-REST", "DOC-QA-001"]
---
# Guía rápida para nuevas guías de QA

Esta guía toma como referencia `checklist_auditoria_restricciones.md` para documentar la estructura mínima y las convenciones de nomenclatura que deben cumplir las futuras guías de QA.

## Mapeo del archivo de referencia
- **Metadatos YAML**: `id`, `tipo`, `categoria`, `version`, `fecha_creacion`, `propietario`, `relacionados`.
- **Encabezados principales** (en mayúsculas): Propósito, CÓMO USAR ESTE CHECKLIST, SECCIÓN 1 (restricciones críticas) con subsecciones numeradas, SECCIÓN 2 y SECCIÓN 3, RECURSOS Y REFERENCIAS, HISTORIAL DE AUDITORÍAS, FIRMA DE APROBACIÓN.
- **Secciones clave**:
  - Objetivo: se expone en “Propósito”.
  - Alcance: descrito en la sección de uso y en los bloques de restricciones (alcances CRÍTICO/ALTA/MEDIA/BAJA).
  - Checklist: tablas numeradas por categoría (1.x, 2.x, 3.x) con columnas `#`, `Ítem`, `Verificación`, `Estado`, `Evidencia` y sumarios de puntaje.
  - Métricas: scoring mínimo y puntajes por sección (Score 1.x, Score 2.x, Score 3.x).
  - Responsables: roles explícitos en la firma de aprobación (QA Lead, Security Lead, Tech Lead).
  - Frecuencia: subsección “Frecuencia de Auditoría” dentro de CÓMO USAR ESTE CHECKLIST.
- **Tablas**: usadas para checklist por sección, métricas de seguridad, recursos de archivos y firmas. Todas usan encabezados en mayúsculas y numeración alineada con el bloque (1.1, 1.2...).
- **Nomenclatura**: IDs en mayúsculas con prefijos (ej. `CHECK-AUDIT-REST`), versiones semánticas, subtítulos numerados (`### 1.1 Comunicaciones [CRÍTICO]`), listas de acciones pendientes con casillas `[ ]`.

## Elementos obligatorios para nuevas guías de QA
1. **Metadatos YAML** con `id`, `estado`, `propietario`, `ultima_actualizacion`, `relacionados` y, si aplica, `tipo`, `categoria`, `version`, `fecha_creacion`.
2. **Objetivo y alcance**: subsección corta que aclare propósito y límites del documento.
3. **Frecuencia y responsables**: bloque dedicado a cuándo se ejecuta la guía y quién la aprueba (roles mínimos: QA Lead; agregar Security/Tech Lead cuando proceda).
4. **Checklist estructurado**:
   - Numeración jerárquica por categoría (`1.x`, `2.x`, etc.).
   - Tablas con columnas `#`, `Ítem`, `Verificación`, `Estado`, `Evidencia`.
   - Cierre de cada subsección con puntaje o métricas de cumplimiento.
5. **Métricas y criterios de aceptación**: metas mínimas (ej. puntuación global, cobertura ≥ 80 %) y umbrales por severidad.
6. **Acciones pendientes**: lista de tareas o remediaciones con casillas `[ ]` vinculadas a cada sección.
7. **Recursos y referencias**: enlaces a documentos relacionados y herramientas sugeridas.
8. **Historial y firma**: tabla de auditorías previas y bloque de firmas para responsables.
9. **Nomenclatura**: mantener IDs en mayúsculas con prefijos descriptivos (`CHECK-`, `DOC-`, `PLAN-`), subtítulos numerados y uso consistente de mayúsculas en encabezados principales.

## Plantilla mínima sugerida
```markdown
---
id: CHECK-NNN
estado: borrador
propietario: rol-responsable
ultima_actualizacion: AAAA-MM-DD
relacionados: ["..."]
---
# Título de la guía

## Propósito y alcance
- Objetivo
- Alcance

## Frecuencia y responsables
- Frecuencia
- Roles: QA Lead / Security Lead / Tech Lead

## Checklist
### 1.1 Tema [CRÍTICO]
| # | Ítem | Verificación | Estado | Evidencia |
|---|------|--------------|--------|-----------|
| 1.1.1 | ... | ... | ... | ... |

**Score 1.1**: X/X - Estado

## Métricas y criterios
- Puntuación mínima global
- Criterios por severidad

## Acciones pendientes
- [ ] Acción

## Recursos y referencias
- ...

## Historial de auditorías
| Fecha | Auditor | Score Global | Estado | Notas |
| --- | --- | --- | --- | --- |

## Firma de aprobación
- QA Lead: ___ Fecha: ___
- Security Lead: ___ Fecha: ___
- Tech Lead: ___ Fecha: ___
```
