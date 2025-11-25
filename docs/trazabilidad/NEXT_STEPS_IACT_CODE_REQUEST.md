# NEXT_STEPS_IACT_CODE_REQUEST.md

## 1. Archivos Críticos para la Trazabilidad (TRZ-001)

Hemos formalizado el **Catálogo BR (Nivel 1)** a partir del módulo `politicas` y el **RNF-AUD-001 (Nivel 3)** con el módulo `audit`. El paso restante es cerrar la **Autorización (BR-SEG-XXX)** antes de actualizar el UC-010.

A continuación, se listan los archivos de código fuente pendientes para completar estos artefactos:

| Rol de Trazabilidad | Módulo | Archivo/s Solicitado/s | Razón para el Análisis de Trazabilidad |
| :--- | :--- | :--- | :--- |
| **Nivel 1: Autorización/Privilegios** | `permissions` | `permissions/models.py` y `permissions/services.py` | **CRÍTICO:** Necesario para formalizar el permiso **BR-SEG-007** (Autorización) y la implementación de `PermisoService` que se usa en UC-010. |
| **Nivel 3: RNF de Auditoría** | `audit` | `audit/*` | **COMPLETADO.** Se utilizó para crear el **RNF-AUD-001_AUDITORIA.md**. |
| **Nivel 1: Reglas de Negocio** | `politicas` | `politicas/*` | **COMPLETADO.** Se utilizó para crear el **CATALOGO_BR.md**. |
| **Nivel 4: CU Central de Negocio** | `llamadas` | `llamadas/services.py` | **COMPLETADO.** Se utilizó para crear el **UC-010**. |

## 2. Instrucción para Continuar

Una vez proporcionado el contenido de los **dos archivos restantes** (`permissions/models.py` y `permissions/services.py`), continuaremos con la generación del índice **BR-SEG-XXX** y actualizaremos el UC-010 con las referencias finales en la carpeta **PRODUCTO_DASHBOARD_ANALYTICS/**.
