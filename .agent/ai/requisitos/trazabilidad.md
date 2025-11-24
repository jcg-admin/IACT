---
title: Matriz de Trazabilidad - Dominio AI
date: 2025-11-13
domain: ai
tipo: trazabilidad
status: active
---

# Matriz de Trazabilidad - Dominio AI

## Objetivo

Mantener la trazabilidad bidireccional entre los 5 niveles de requerimientos del dominio AI, asegurando que cada nivel esté correctamente vinculado con los niveles superiores e inferiores.

## Jerarquía de 5 Niveles

```
Nivel 1: REGLAS DE NEGOCIO (RN)
          ↓
Nivel 2: REQUERIMIENTOS DE NEGOCIO (RNE)
          ↓
Nivel 3: REQUERIMIENTOS DE USUARIO (RU)
          ↓
Nivel 4: REQUERIMIENTOS FUNCIONALES (RF)
          ↓
Nivel 5: ATRIBUTOS DE CALIDAD (AC)
```

## Marco Conceptual

Ver marcos de gobernanza:
- Reglas de Negocio: `docs/gobernanza/marco_integrado/marco_reglas_negocio.md`
- Casos de Uso: `docs/gobernanza/marco_integrado/marco_casos_uso.md`

---

## RN → RNE: Reglas de Negocio a Requerimientos de Negocio

| ID Regla | Tipo | Descripción | RNE Derivados | Estado |
|----------|------|-------------|---------------|--------|
| RN-AI-001 | Hecho | TBD | - | Pendiente |
| RN-AI-002 | Restricción | TBD | - | Pendiente |
| RN-AI-003 | Desencadenador | TBD | - | Pendiente |
| RN-AI-004 | Inferencia | TBD | - | Pendiente |
| RN-AI-005 | Cálculo | TBD | - | Pendiente |

**Acción requerida**: Documentar reglas de negocio en `reglas_negocio/` usando los 5 tipos definidos en el marco conceptual.

---

## RNE → RU: Requerimientos de Negocio a Requerimientos de Usuario

| ID RNE | Objetivo Organizacional | Casos de Uso (RU) | Prioridad | Estado |
|--------|------------------------|-------------------|-----------|--------|
| RNE-AI-001 | TBD | - | Alta | Pendiente |
| RNE-AI-002 | TBD | - | Media | Pendiente |

**Acción requerida**: Documentar objetivos organizacionales del dominio AI en `requerimientos_negocio/`.

---

## RU → RF: Requerimientos de Usuario a Requerimientos Funcionales

### Casos de Uso a Features

| ID Caso de Uso | Nombre (VERBO+OBJETO) | Features (RF) | Prioridad | Estado |
|----------------|----------------------|---------------|-----------|--------|
| UC-AI-001 | TBD | - | Alta | Pendiente |
| UC-AI-002 | TBD | - | Media | Pendiente |

**Nomenclatura**: Los casos de uso deben seguir formato VERBO+OBJETO (ej. "Entrenar Modelo", "Generar Respuesta").

**Acción requerida**: Especificar casos de uso en formato completo de dos columnas en `requerimientos_usuario/casos_uso/`.

### Historias de Usuario a Features

| ID Historia | Como... quiero... para... | Features (RF) | Sprint | Estado |
|-------------|---------------------------|---------------|--------|--------|
| US-AI-001 | TBD | - | - | Pendiente |
| US-AI-002 | TBD | - | - | Pendiente |

**Acción requerida**: Crear historias de usuario en `requerimientos_usuario/historias_usuario/`.

---

## RF → AC: Requerimientos Funcionales a Atributos de Calidad

| ID Feature | Descripción | Atributos de Calidad | Métricas | Estado |
|------------|-------------|---------------------|----------|--------|
| RF-AI-001 | TBD | - | - | Pendiente |
| RF-AI-002 | TBD | - | - | Pendiente |

**Acción requerida**: Documentar features en `requerimientos_funcionales/features/`.

---

## RF → CÓDIGO: Requerimientos Funcionales a Implementación

| ID Feature | Módulo/Componente | Archivos de Código | Tests | Estado |
|------------|-------------------|-------------------|-------|--------|
| RF-AI-001 | TBD | - | - | Pendiente |
| RF-AI-002 | TBD | - | - | Pendiente |

**Ubicación del código**: `src/ai/` (por definir estructura específica)

**Acción requerida**: Establecer convención de ubicación del código para el dominio AI.

---

## AC → NFR: Atributos de Calidad a Requerimientos No Funcionales

| Atributo de Calidad | Descripción | NFR | Métrica Objetivo | Estado |
|---------------------|-------------|-----|-----------------|--------|
| Performance | Tiempo de respuesta | - | TBD | Pendiente |
| Seguridad | Protección de datos | - | TBD | Pendiente |
| Usabilidad | Facilidad de uso | - | TBD | Pendiente |
| Reliability | Disponibilidad | - | TBD | Pendiente |
| Maintainability | Mantenibilidad | - | TBD | Pendiente |

**Acción requerida**: Documentar atributos de calidad en `atributos_calidad/`.

---

## Trazabilidad Inversa

### CÓDIGO → RF → RU → RNE → RN

La trazabilidad inversa permite responder preguntas como:
- ¿Qué regla de negocio justifica este código?
- ¿Qué necesidad de usuario se satisface con esta feature?
- ¿Qué objetivo organizacional se cumple?

**Herramientas**:
- Anotaciones en código (comments con ID de requisito)
- Tags en commits (ej. `[RF-AI-001]`)
- Issues vinculados en GitHub

---

## Métricas de Trazabilidad

| Métrica | Objetivo | Actual | Estado |
|---------|----------|--------|--------|
| RN documentadas | 100% (5 tipos mínimo) | 0% | Pendiente |
| RNE con RN trazables | 100% | 0% | Pendiente |
| UC con RNE trazables | 100% | 0% | Pendiente |
| RF con UC trazables | 100% | 0% | Pendiente |
| Código con RF trazables | 80% | 0% | Pendiente |

---

## Proceso de Actualización

### Agregar Nueva Regla de Negocio

1. Documentar en `reglas_negocio/{tipo}.md`
2. Asignar ID (RN-AI-XXX)
3. Actualizar sección "RN → RNE" en esta matriz
4. Vincular RNE derivados

### Agregar Nuevo Caso de Uso

1. Crear especificación en `requerimientos_usuario/casos_uso/UC-XXX-{verbo_objeto}.md`
2. Usar formato de dos columnas (Actor | Sistema)
3. Asignar ID (UC-AI-XXX)
4. Actualizar sección "RU → RF" en esta matriz
5. Vincular con RNE y Features

### Agregar Nueva Feature

1. Documentar en `requerimientos_funcionales/features/`
2. Asignar ID (RF-AI-XXX)
3. Actualizar secciones "RU → RF" y "RF → CÓDIGO"
4. Vincular con UC y código fuente

---

## Referencias

- **Marco de Reglas de Negocio**: `docs/gobernanza/marco_integrado/marco_reglas_negocio.md`
- **Marco de Casos de Uso**: `docs/gobernanza/marco_integrado/marco_casos_uso.md`
- **Matriz de Trazabilidad Backend**: `docs/backend/requisitos/trazabilidad.md`
- **Matriz de Trazabilidad Frontend**: `docs/frontend/analisis_negocio/marco_integrado/03_matrices_trazabilidad_iact.md`
- **Matriz de Trazabilidad Infraestructura**: `docs/infraestructura/matriz_trazabilidad_rtm.md`

---

**Última actualización**: 2025-11-13
**Responsable**: Equipo AI
**Estado**: Estructura creada - Contenido pendiente
**Próxima revisión**: Cuando se documente el primer conjunto de RN, RNE, RU, RF
