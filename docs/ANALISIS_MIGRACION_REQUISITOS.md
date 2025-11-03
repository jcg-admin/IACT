---
id: DOC-ANALISIS-MIGRACION
tipo: analisis
titulo: Análisis de Migración de Requisitos Legacy
fecha: 2025-11-03
responsable: equipo-arquitectura
estado: completado
---

# 📊 Análisis de Migración de Requisitos Legacy

## 🎯 Objetivo

Analizar requisitos existentes en estructura antigua para migrar a `docs/implementacion/` (Opción B).

---

## 🔍 Metodología

1. ✅ Escaneo exhaustivo de carpetas legacy:
   - `docs/backend/requisitos/`
   - `docs/frontend/requisitos/`
   - `docs/infrastructure/requisitos/`
   - `docs/requisitos/`
   - `docs/solicitudes/`

2. ✅ Clasificación de archivos encontrados

3. ✅ Determinación de estrategia de migración

---

## 📄 Hallazgos

### Archivos Encontrados

| Ubicación | Archivos | Tipo | ¿Requisito Formal? |
|-----------|----------|------|-------------------|
| `docs/backend/requisitos/` | 3 archivos | Plantilla + docs trazabilidad | ❌ NO |
| `docs/frontend/requisitos/` | 1 archivo | README | ❌ NO |
| `docs/infrastructure/requisitos/` | 1 archivo | README | ❌ NO |
| `docs/requisitos/` | 2 archivos | Plantilla + trazabilidad | ❌ NO |
| `docs/solicitudes/sc00/` | 4+ archivos | Documentación de evento | ❌ NO |
| `docs/solicitudes/sc01/` | 1 archivo | Guía operativa MkDocs | ❌ NO |

### Detalle de Archivos

#### `docs/backend/requisitos/`
- `readme.md` - README guía (mantener)
- `rq_plantilla.md` - Plantilla antigua (mantener como referencia)
- `trazabilidad.md` - Documentación de trazabilidad (será reemplazado por RTM auto-generado)

#### `docs/frontend/requisitos/`
- `readme.md` - README guía (mantener)

#### `docs/infrastructure/requisitos/`
- `readme.md` - README guía (mantener)

#### `docs/requisitos/`
- `rq_plantilla.md` - Plantilla antigua (mantener como referencia)
- `trazabilidad.md` - Documentación de trazabilidad (será reemplazado por RTM auto-generado)

#### `docs/solicitudes/sc00/`
**Tipo**: Documentación de evento/conferencia
**Contenido**: Supercomputing Conference 2000 - Denver, CO
**Conclusión**: NO es un requisito del sistema IACT. Es documentación de proyecto/evento.
**Acción**: MANTENER en su ubicación actual

#### `docs/solicitudes/sc01/`
**Tipo**: Documentación operativa
**Contenido**: Guía de instalación de MkDocs
**Conclusión**: NO es un requisito del sistema. Es documentación de setup.
**Acción**: MANTENER en su ubicación actual

---

## 🎯 Conclusión Principal

### ⚠️ NO HAY REQUISITOS FORMALES QUE MIGRAR

El proyecto IACT **NO tiene requisitos formales creados todavía** con la estructura esperada (N-XXX, RN-XXX, RS-XXX, RF-XXX, RNF-XXX).

Los archivos existentes son:
- ✅ Plantillas de documentación
- ✅ Documentación de guías y procesos
- ✅ READMEs instructivos
- ✅ Documentación de eventos/proyectos

**Ninguno de estos debe migrarse** porque no son requisitos formales del sistema.

---

## 🚀 Estrategia Implementada

Dado que no hay requisitos que migrar, se implementó:

### 1. ✅ Script de Migración Automatizada

**Ubicación**: `scripts/migrate_requirements.py`

**Capacidades**:
- Detección automática de tipo de requisito
- Detección de dominio (backend/frontend/infrastructure)
- Generación de frontmatter YAML
- Migración a ubicación correcta en `docs/implementacion/`
- Modo dry-run para preview

**Estado**: Listo para usar cuando se creen requisitos formales

### 2. ✅ Guía de Migración Completa

**Ubicación**: `docs/implementacion/MIGRATION_FROM_LEGACY.md`

**Contenido**:
- 3 métodos de migración (automatizada, manual, desde cero)
- Ejemplos detallados
- Checklist completa
- Troubleshooting
- Comandos listos para usar

**Estado**: Documentación completa lista

### 3. ✅ Avisos en Carpetas Legacy

**Ubicación**: `docs/backend/requisitos/_MOVIDO_A_IMPLEMENTACION.md`

**Propósito**: Informar a usuarios que nuevos requisitos van en `docs/implementacion/`

---

## 📊 Verificación con Script

### Ejecución

```bash
$ python scripts/migrate_requirements.py

======================================================================
🔄 SCRIPT DE MIGRACIÓN DE REQUISITOS LEGACY
======================================================================

⚠️  MODO DRY-RUN: No se modificarán archivos
    Ejecutar con --execute para realizar migración real

ℹ️  No se encontraron archivos para migrar

Archivos excluidos automáticamente:
   - readme.md
   - README.md
   - _MOVIDO_A_IMPLEMENTACION.md
   - rq_plantilla.md
   - trazabilidad.md
```

### Interpretación

✅ El script confirmó el análisis manual:
- No hay archivos `.md` que sean requisitos formales
- Solo existen plantillas y documentación (correctamente excluidos)

---

## 🔄 Próximos Pasos

### Inmediato

1. ✅ Documentar hallazgos (este documento)
2. ✅ Commit de herramientas de migración
3. ⏳ Comunicar al equipo situación actual

### A Futuro (FASE 2 - Piloto)

Cuando se cree el **primer requisito formal**, usar:

#### Opción A: Crear desde cero usando templates

```bash
cd docs/implementacion/backend/requisitos/necesidades/
cp ../../../../plantillas/template_necesidad.md n001_mi_primera_necesidad.md
# Editar y completar
```

#### Opción B: Si hay requisito legacy futuro

```bash
python scripts/migrate_requirements.py --execute
```

---

## 📋 Recomendaciones

### 1. No Migrar Archivos Actuales ✅

Los archivos en `docs/backend/requisitos/`, etc. NO deben moverse porque:
- Son plantillas de referencia
- Son documentación guía
- No son requisitos formales

### 2. Mantener Carpetas Legacy Read-Only ✅

- Dejar `docs/backend/requisitos/` con su contenido actual
- Agregar aviso `_MOVIDO_A_IMPLEMENTACION.md` (ya hecho)
- Nuevos requisitos van directo a `docs/implementacion/`

### 3. Iniciar FASE 2 - Piloto ⏳

Crear el primer requisito formal:
- Identificar necesidad real de negocio IACT
- Documentar como N-001 usando template
- Derivar requisitos en 3 dominios
- Validar proceso completo

### 4. Capacitar Equipo 📚

- Mostrar nueva estructura `docs/implementacion/`
- Enseñar uso de templates
- Practicar con requisito piloto
- Documentar lecciones aprendidas

---

## 🎓 Lecciones Aprendidas

### 1. Análisis Previo es Crítico

Antes de implementar migración masiva:
- ✅ Analizar QUÉ existe realmente
- ✅ NO asumir que "requisitos/" contiene requisitos
- ✅ Verificar con herramientas automatizadas

### 2. Estructura Preparada para Crecimiento

Aunque no hay requisitos ahora:
- ✅ Estructura `docs/implementacion/` lista
- ✅ Templates profesionales disponibles
- ✅ Herramientas de migración preparadas
- ✅ Proceso documentado

### 3. Documentación != Requisitos

Clarificar diferencia:
- **Requisito**: Describe QUÉ debe hacer el sistema (formal, trazable, verificable)
- **Documentación**: Guías, procedimientos, eventos, setups

---

## 📊 Métricas Finales

| Métrica | Valor |
|---------|-------|
| Requisitos encontrados | **0** |
| Plantillas encontradas | 2 |
| Documentación guía | 5 archivos |
| Archivos SC00/SC01 | 5+ archivos |
| Script de migración | ✅ Listo |
| Guía de migración | ✅ Completa |
| Estructura preparada | ✅ 100% |

---

## ✅ Estado del Proyecto

| Aspecto | Estado | Comentario |
|---------|--------|------------|
| **Estructura `docs/implementacion/`** | ✅ Completa | 3 dominios con 5 tipos de requisitos |
| **Templates ISO 29148** | ✅ Completos | 5 plantillas profesionales |
| **Script de migración** | ✅ Listo | Para uso futuro |
| **Guía de migración** | ✅ Completa | Documentación exhaustiva |
| **Requisitos formales** | ❌ 0 | Pendiente crear en FASE 2 |
| **Avisos en legacy** | ✅ Colocados | En docs/backend/requisitos/ |
| **MkDocs configurado** | ✅ Actualizado | Navegación a implementacion/ |

---

## 🔚 Conclusión Final

El proyecto IACT está en **etapa inicial** sin requisitos formales creados.

**Beneficio**: Podemos aplicar estructura ISO 29148 + BABOK **desde el inicio** sin necesidad de migración compleja.

**Próximo paso crítico**: **FASE 2 - Piloto**
- Crear primer requisito N-001 (necesidad de negocio real)
- Derivar requisitos completos
- Validar proceso end-to-end
- Entrenar equipo con ejemplo real

---

**Fecha de análisis**: 2025-11-03
**Responsable**: equipo-arquitectura
**Herramientas usadas**:
- Análisis manual de estructura
- Script `migrate_requirements.py` (dry-run)
- Revisión de contenido de archivos

**Estado**: ✅ Análisis completo y herramientas listas para uso futuro
