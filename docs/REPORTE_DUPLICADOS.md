# 📋 REPORTE DE ARCHIVOS DUPLICADOS EN docs/

**Fecha de análisis**: 2025-11-04  
**Rama**: claude/reorganize-docs-folders-011CUneVZ43BHmb7pSbeFxK1  
**Motivo**: Reorganización de carpetas backend, frontend, infrastructure a docs/implementacion/

---

## 📊 Resumen Ejecutivo

Se encontraron **13 archivos con nombres duplicados** en diferentes ubicaciones:

| Archivo | Ubicaciones | Idénticos | Diferentes |
|---------|------------|-----------|------------|
| checklist_testing.md | 2 | ✅ Sí | |
| checklist_trazabilidad_requisitos.md | 2 | ✅ Sí | |
| checklist_cambios_documentales.md | 2 | ✅ Sí | |
| checklist_desarrollo.md | 2 | | ⚠️ Diferentes |
| contenedores_devcontainer.md | 2 | | ⚠️ Diferentes |
| github_copilot_codespaces.md | 2 | | ⚠️ Diferentes |
| lineamientos_codigo.md | 2 | | ⚠️ Diferentes |
| lineamientos_gobernanza.md | 2 | | ⚠️ Diferentes |
| reprocesar_etl_fallido.md | 2 | | ⚠️ Diferentes |
| verificar_servicios.md | 2 | | ⚠️ Diferentes |
| post_create.md | 2 | | ⚠️ Diferentes |
| adr_2025_001_vagrant_mod_wsgi.md | 2 | | ⚠️ Diferentes |
| plantilla_adr.md | 2 | | ⚠️ Diferentes |

**Total**: 3 idénticos, 10 diferentes

---

## ✅ ARCHIVOS IDÉNTICOS (Eliminar duplicados)

### 1. checklist_testing.md
**MD5**: `e5f5bac2865cf269307336867b4c82a2`


📄 **checklist_testing.md**
- MD5: `e5f5bac2865cf269307336867b4c82a2`
- Tamaño: 297 bytes

**Ubicaciones:**
- `docs/checklists/checklist_testing.md`
- `docs/implementacion/backend/checklists/checklist_testing.md`

**Recomendación**: Estos archivos son 100% idénticos. Mantener solo la versión en `docs/checklists/` (general) o en `docs/implementacion/` (específica). Se recomienda eliminar el duplicado según el propósito del archivo.


📄 **checklist_trazabilidad_requisitos.md**
- MD5: `38567ea7af2e76bc3e5625ee20c4e15a`
- Tamaño: 440 bytes

**Ubicaciones:**
- `docs/checklists/checklist_trazabilidad_requisitos.md`
- `docs/implementacion/backend/checklists/checklist_trazabilidad_requisitos.md`

**Recomendación**: Estos archivos son 100% idénticos. Mantener solo la versión en `docs/checklists/` (general) o en `docs/implementacion/` (específica). Se recomienda eliminar el duplicado según el propósito del archivo.


📄 **checklist_cambios_documentales.md**
- MD5: `24f0fb136a60243ac9a79c20344addba`
- Tamaño: 304 bytes

**Ubicaciones:**
- `docs/checklists/checklist_cambios_documentales.md`
- `docs/implementacion/infrastructure/checklists/checklist_cambios_documentales.md`

**Recomendación**: Estos archivos son 100% idénticos. Mantener solo la versión en `docs/checklists/` (general) o en `docs/implementacion/` (específica). Se recomienda eliminar el duplicado según el propósito del archivo.


---

## ⚠️ ARCHIVOS DIFERENTES (Revisar propósito)


Estos archivos tienen el mismo nombre pero contenido diferente. Requieren revisión para determinar si:
1. Son versiones diferentes (general vs específica)
2. Uno está desactualizado
3. Deben fusionarse
4. Deben mantenerse separados con nombres diferentes

### 1. checklist_desarrollo.md

**Ubicación 1**: `docs/checklists/checklist_desarrollo.md`
- **MD5**: `aa30a7807f04bc9e6a156d44bd22205b`
- **Tamaño**: 883 bytes (23 líneas)
- **Propósito**: Checklist GENERAL de desarrollo del proyecto

**Ubicación 2**: `docs/implementacion/backend/checklists/checklist_desarrollo.md`
- **MD5**: `3545127f3d895bd06141f17a681e2c1f`
- **Tamaño**: 299 bytes (8 líneas)
- **Propósito**: Checklist ESPECÍFICO de backend

**Análisis**: La versión general (docs/checklists) es mucho más completa con reglas de output profesional y estándares de código. La versión de backend es más simple.

**Recomendación**: ✅ MANTENER AMBOS. La versión general tiene contenido más robusto que debería aplicarse a todo el proyecto. La versión de backend es un stub que podría expandirse con elementos específicos del backend.

---

### 2. contenedores_devcontainer.md

**Ubicación 1**: `docs/devops/contenedores_devcontainer.md`
- **MD5**: `6a8670348ebf9ad230d4abc3b11f0015`
- **Tamaño**: 8,590 bytes (320 líneas)
- **Propósito**: Documentación COMPLETA sobre devcontainers

**Ubicación 2**: `docs/implementacion/infrastructure/devops/contenedores_devcontainer.md`
- **MD5**: `fc4ad99a3387b70ebabeefbb14a59768`
- **Tamaño**: 1,953 bytes (29 líneas)
- **Propósito**: Stub/placeholder de documentación

**Análisis**: Versión en docs/devops es 4.4x más grande y mucho más completa. La versión en implementacion/infrastructure parece ser un placeholder o resumen.

**Recomendación**: ⚠️ ELIMINAR versión en implementacion/infrastructure/devops/ (es redundante). Mantener solo la versión completa en docs/devops/.

---

### 3. github_copilot_codespaces.md

**Ubicación 1**: `docs/devops/runbooks/github_copilot_codespaces.md`
- **MD5**: `84703f70455823dfd239a7698eccee4b`
- **Tamaño**: 9,526 bytes (428 líneas)
- **Propósito**: Runbook completo

**Ubicación 2**: `docs/implementacion/infrastructure/devops/runbooks/github_copilot_codespaces.md`
- **MD5**: `612a10506a3173e01210c73a951286f9`
- **Tamaño**: 13,618 bytes (252 líneas)
- **Propósito**: Runbook completo (¿versión diferente?)

**Análisis**: Ambas versiones son extensas pero con contenido diferente. La versión en implementacion es más grande en bytes pero tiene menos líneas.

**Recomendación**: ⚠️ REVISAR MANUALMENTE. Pueden ser versiones diferentes o una puede estar más actualizada. Comparar contenido para decidir cuál conservar.

---

### 4. lineamientos_codigo.md

**Ubicación 1**: `docs/arquitectura/lineamientos_codigo.md`
- **MD5**: `3265672fc034450f2092cd636d67a56c`
- **Tamaño**: 11,041 bytes (453 líneas)
- **Propósito**: Lineamientos GENERALES de código del proyecto

**Ubicación 2**: `docs/implementacion/backend/arquitectura/lineamientos_codigo.md`
- **MD5**: `e13b8c5717cbe1841ce1e844cecd9646`
- **Tamaño**: 618 bytes (20 líneas)
- **Propósito**: Lineamientos ESPECÍFICOS de backend (stub)

**Análisis**: Versión general es 17.8x más grande. Versión de backend es un placeholder.

**Recomendación**: ⚠️ EXPANDIR versión de backend con lineamientos específicos de Django/Python, o eliminarla y referenciar a la general.

---

### 5. lineamientos_gobernanza.md

**Ubicación 1**: `docs/gobernanza/lineamientos_gobernanza.md`
- **MD5**: `e8eeb2f86336f7a751b1c22a3a480279`
- **Tamaño**: 358 bytes (13 líneas)
- **Propósito**: Lineamientos generales

**Ubicación 2**: `docs/implementacion/infrastructure/gobernanza/lineamientos_gobernanza.md`
- **MD5**: `4cc25f2007ed1920d673dea85546ae08`
- **Tamaño**: 417 bytes (13 líneas)
- **Propósito**: Lineamientos de infrastructure

**Análisis**: Tamaños similares pero checksums diferentes. Misma cantidad de líneas.

**Recomendación**: ⚠️ REVISAR contenido para identificar diferencias. Pueden fusionarse o mantener separados según el alcance.

---

### 6. reprocesar_etl_fallido.md

**Ubicación 1**: `docs/devops/runbooks/reprocesar_etl_fallido.md`
- **MD5**: `602f0a3fdc6bc87de56dc496006f7940`
- **Tamaño**: 9,622 bytes (424 líneas)
- **Propósito**: Runbook completo general

**Ubicación 2**: `docs/implementacion/backend/devops/runbooks/reprocesar_etl_fallido.md`
- **MD5**: `58e462ec839120c83f9644c909481e15`
- **Tamaño**: 1,206 bytes (32 líneas)
- **Propósito**: Runbook específico de backend (stub)

**Análisis**: Versión general es 8x más grande. Versión de backend es un resumen/stub.

**Recomendación**: ⚠️ ELIMINAR stub de backend y mantener solo la versión completa en docs/devops/. Los runbooks deberían ser transversales.

---

### 7. verificar_servicios.md

**Ubicación 1**: `docs/devops/runbooks/verificar_servicios.md`
- **MD5**: `9df7908bb08c625b79884f4530fa84bf`
- **Tamaño**: 7,579 bytes (352 líneas)
- **Propósito**: Runbook completo

**Ubicación 2**: `docs/implementacion/infrastructure/devops/runbooks/verificar_servicios.md`
- **MD5**: `78900708eccd59c14003b04f2f46996b`
- **Tamaño**: 1,028 bytes (30 líneas)
- **Propósito**: Stub

**Análisis**: Mismo patrón - versión general completa, versión específica es stub.

**Recomendación**: ⚠️ ELIMINAR stub. Los runbooks operativos deberían centralizarse en docs/devops/.

---

### 8. post_create.md

**Ubicación 1**: `docs/devops/runbooks/post_create.md`
- **MD5**: `79fbb7fd7f8efa958e9172559c16f3a5`
- **Tamaño**: 8,026 bytes (399 líneas)
- **Propósito**: Runbook completo

**Ubicación 2**: `docs/implementacion/infrastructure/devops/runbooks/post_create.md`
- **MD5**: `837ac1fbd729eaad74e4499ab48228bc`
- **Tamaño**: 1,033 bytes (29 líneas)
- **Propósito**: Stub

**Análisis**: Mismo patrón.

**Recomendación**: ⚠️ ELIMINAR stub.

---

### 9. adr_2025_001_vagrant_mod_wsgi.md

**Ubicación 1**: `docs/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md`
- **MD5**: `1e43278e94c4be97d2d71fa90922c706`
- **Tamaño**: 7,596 bytes (260 líneas)
- **Propósito**: ADR completo

**Ubicación 2**: `docs/implementacion/infrastructure/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md`
- **MD5**: `f4edf7e92049505ac76b535d9671fef4`
- **Tamaño**: 1,263 bytes (23 líneas)
- **Propósito**: Stub/resumen

**Análisis**: ADR completo vs stub.

**Recomendación**: ⚠️ ELIMINAR stub. Los ADRs deberían centralizarse en docs/arquitectura/adr/.

---

### 10. plantilla_adr.md

**Ubicación 1**: `docs/arquitectura/adr/plantilla_adr.md`
- **MD5**: `7ab301ecd44d15c35bdc52e09cefaf3b`
- **Tamaño**: 4,682 bytes (198 líneas)
- **Propósito**: Plantilla completa

**Ubicación 2**: `docs/implementacion/infrastructure/arquitectura/adr/plantilla_adr.md`
- **MD5**: `40f698d0ce480636689a983ff4171641`
- **Tamaño**: 709 bytes (34 líneas)
- **Propósito**: Plantilla simplificada

**Análisis**: Plantilla completa vs simplificada.

**Recomendación**: ⚠️ ELIMINAR versión simplificada. Las plantillas deberían estar en docs/plantillas/ o docs/arquitectura/adr/.

---

## 📋 Resumen de Recomendaciones

### Acción Inmediata - Eliminar Duplicados Idénticos (3 archivos)

```bash
# Eliminar archivos 100% duplicados
rm docs/implementacion/backend/checklists/checklist_testing.md
rm docs/implementacion/backend/checklists/checklist_trazabilidad_requisitos.md
rm docs/implementacion/infrastructure/checklists/checklist_cambios_documentales.md
```

**Justificación**: Estos archivos están en docs/checklists/ (general) y son idénticos a los movidos.

### Acción Recomendada - Eliminar Stubs/Placeholders (7 archivos)

```bash
# Eliminar stubs que duplican documentación completa en docs/ raíz
rm docs/implementacion/infrastructure/devops/contenedores_devcontainer.md
rm docs/implementacion/backend/devops/runbooks/reprocesar_etl_fallido.md
rm docs/implementacion/infrastructure/devops/runbooks/verificar_servicios.md
rm docs/implementacion/infrastructure/devops/runbooks/post_create.md
rm docs/implementacion/infrastructure/arquitectura/adr/adr_2025_001_vagrant_mod_wsgi.md
rm docs/implementacion/infrastructure/arquitectura/adr/plantilla_adr.md
rm docs/implementacion/backend/arquitectura/lineamientos_codigo.md  # opcional - puede expandirse
```

**Justificación**: Estos son stubs/placeholders que duplican documentación más completa en docs/ raíz. Los runbooks, ADRs y lineamientos deberían estar centralizados.

### Revisión Manual Requerida (3 archivos)

1. **github_copilot_codespaces.md** - Ambas versiones son extensas, revisar diferencias
2. **lineamientos_gobernanza.md** - Contenidos diferentes, determinar si fusionar
3. **checklist_desarrollo.md** - Versión general más completa, decidir si mantener ambas

---

## 📊 Estadísticas Finales

- **Total archivos duplicados encontrados**: 13
- **Duplicados idénticos (100%)**: 3 archivos
- **Stubs/Placeholders recomendados eliminar**: 7 archivos  
- **Requieren revisión manual**: 3 archivos
- **Bytes potenciales a ahorrar**: ~15 KB eliminando stubs

---

## 🎯 Conclusión

La reorganización movió correctamente las carpetas a docs/implementacion/, pero creó duplicación con documentación general que ya existía en docs/ raíz. La estrategia recomendada es:

1. **Documentación general** (runbooks, ADRs, plantillas, lineamientos): Mantener en docs/ raíz
2. **Documentación específica de implementación** (requisitos, diseño detallado): Mantener en docs/implementacion/
3. **Eliminar stubs** que solo son placeholders de documentación más completa

Esta estructura evita duplicación y mantiene clara la separación entre documentación general del proyecto y documentación específica de implementación.

