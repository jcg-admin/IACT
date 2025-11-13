---
title: Requisitos - Infraestructura
date: 2025-11-13
domain: infraestructura
---

# Requisitos - Infraestructura

## Jerarquía de Requerimientos (5 Niveles)

Ver marco conceptual en: `docs/gobernanza/marco_integrado/marco_reglas_negocio.md`

```
Nivel 1: REGLAS DE NEGOCIO → reglas_negocio/
Nivel 2: REQUERIMIENTOS DE NEGOCIO → requerimientos_negocio/
Nivel 3: REQUERIMIENTOS DE USUARIO → requerimientos_usuario/
Nivel 4: REQUERIMIENTOS FUNCIONALES → requerimientos_funcionales/
Nivel 5: ATRIBUTOS DE CALIDAD → atributos_calidad/
```

## Estructura

- `reglas_negocio/` - 5 tipos: Hechos, Restricciones, Desencadenadores, Inferencias, Cálculos
- `requerimientos_negocio/` - Objetivos organizacionales
- `requerimientos_usuario/` - Casos de uso (VERBO+OBJETO), historias de usuario
- `requerimientos_funcionales/` - Features, especificaciones funcionales
- `atributos_calidad/` - Performance, seguridad, usabilidad, etc.
- `analisis_negocio/` - Análisis del contexto
- `trazabilidad.md` - Matriz de trazabilidad
