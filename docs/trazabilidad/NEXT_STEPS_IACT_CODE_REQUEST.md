# NEXT_STEPS_IACT_CODE_REQUEST.md

## 1. Archivos Críticos para la Trazabilidad (TRZ-001)

Hemos formalizado el **Catálogo BR (Nivel 1)** a partir del módulo `politicas`. Ahora, debemos formalizar los artefactos **RNF (Nivel 3)** y la **Autorización (BR-SEG-XXX)**.

A continuación, se listan los archivos de código fuente pendientes para construir estos artefactos:

| Rol de Trazabilidad | Módulo | Archivo/s Solicitado/s | Razón para el Análisis de Trazabilidad |
| :--- | :--- | :--- | :--- |
| **Nivel 3: RNF de Auditoría** | `audit` | `audit/models.py` | **CRÍTICO:** Define el esquema del `AuditLog`. Necesario para formalizar la **Postcondición RNF-AUD-001** que debe aplicarse al final de UC-010. |
| **Nivel 1: Autorización/Privilegios** | `permissions` | `permissions/models.py` y `permissions/services.py` | **CRÍTICO:** Necesario para formalizar el permiso **BR-SEG-007** (Autorización) y la implementación de `PermisoService` que se usa en UC-010. |
| **Nivel 1: Reglas de Negocio** | `politicas` | `politicas/*` | **COMPLETADO.** Se utilizó para crear el **CATALOGO_BR.md**. |
| **Nivel 4: CU Central de Negocio** | `llamadas` | `llamadas/services.py` | **COMPLETADO.** Se utilizó para crear el **UC-010**. |

## 2. Instrucción para Continuar

Una vez proporcionado el contenido de los **tres archivos restantes** (`audit/models.py`, `permissions/models.py`, `permissions/services.py`), continuaremos con la generación de los artefactos fundacionales **RNF-AUD-001** y el índice de **BR-SEG-XXX** en la carpeta **PRODUCTO_DASHBOARD_ANALYTICS/**.
