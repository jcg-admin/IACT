# ADR-AI-020: Validación de planes con rutas múltiples y consenso mínimo

- **Estado:** Aceptado
- **Fecha:** 2025-11-17
- **Dominio:** Gobernanza / Agentes SDLC
- **Propietario:** Equipo de Gobernanza SDLC
- **Decisión vinculada a RNF:** RNF-PROC-001 (Gobernanza de agentes IA)

## Contexto
La validación automática de planes SDLC necesita equilibrar cobertura (evitar omisiones en riesgos o tareas críticas) con velocidad de respuesta. Las ejecuciones previas mostraron falsos negativos cuando solo se empleaba una ruta de razonamiento y falsos positivos cuando se permitía aprobar con baja evidencia. Además, los planes deben dejar trazabilidad hacia BR/RNF/UC y cumplir con los límites operativos definidos en RNF-PROC-001.

## Decisión
Adoptar un esquema de **cinco rutas de razonamiento paralelas (n=5)** y exigir un **umbral de consenso del 80%** para aprobar un plan de desarrollo. Si el consenso es menor, el agente debe devolver observaciones y solicitar correcciones.

## Justificación
- **Cobertura:** Cinco rutas capturan variaciones suficientes de contexto sin degradar el tiempo de respuesta de manera significativa.
- **Calidad de decisión:** El consenso del 80% reduce aprobaciones con evidencia débil y alinea la validación con el estándar de gobernanza (RNF-PROC-001).
- **Trazabilidad:** El agente reporta las referencias BR/RNF/UC detectadas por cada ruta, facilitando la auditoría posterior.

## Opciones consideradas
- **Tres rutas con consenso 66%:** Más rápido pero generó omisiones en BR de seguridad durante pruebas internas.
- **Siete rutas con consenso 85%:** Mejor cobertura pero conlatencia y costo computacional altos; no aportó mejoras significativas frente a 5/80.

## Consecuencias
- **Positivas:**
  - Menos riesgo de aprobar planes sin cubrir reglas críticas (BR-SEG, RNF-AUD).
  - Evidencia clara de cómo se alcanzó el consenso, útil para auditorías.
- **Negativas / Riesgos:**
  - Mayor tiempo de ejecución vs. 3 rutas; mitigado con caché de contextos frecuentes.
  - Necesidad de mantener pruebas de regresión para cambios en heurísticas.

## Implementación
- **Código:** `scripts/coding/ai/sdlc/plan_validation_agent.py` aplica las 5 rutas y calcula el consenso.
- **Pruebas:** `scripts/coding/tests/ai/sdlc/test_plan_validation_agent.py` valida el umbral del 80% y la agregación de evidencias.
- **Telemetría:** Registrar métricas de tasa de aprobación, falsos positivos/negativos y tiempo promedio por validación en `logs_data/` para seguimiento DORA.

## Trazabilidad
- **RNF-PROC-001:** Define el marco de gobernanza y límites operativos para agentes SDLC.
- **INDICE_TRAZABILIDAD_MAESTRA_IACT:** Este ADR documenta el puente entre la política de consenso y la ejecución en código, asegurando Nivel 2 del estándar.
