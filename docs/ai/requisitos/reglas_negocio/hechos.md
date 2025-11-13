---
title: Reglas de Negocio - Hechos (Dominio AI)
date: 2025-11-13
domain: ai
tipo: reglas_negocio_hechos
status: draft
---

# Reglas de Negocio - Hechos (Dominio AI)

## Marco Conceptual

Ver: `docs/gobernanza/marco_integrado/marco_reglas_negocio.md`

## Definicion

Los **Hechos** son verdades inmutables del negocio que no cambian con el tiempo. Representan realidades fundamentales que el sistema debe reconocer y respetar.

Caracteristicas:
- Son afirmaciones declarativas
- No se pueden violar
- No contienen logica condicional
- Describen el "que es" no el "que debe ser"

---

## Hechos del Dominio AI

### RN-AI-H-001: Naturaleza de los Modelos de IA

**Hecho**: Un modelo de inteligencia artificial es una representacion matematica entrenada con datos historicos.

**Implicacion**: Los modelos NO pueden predecir eventos completamente fuera de su distribucion de entrenamiento.

**Impacto en requisitos**:
- Requerimientos de monitoreo de drift
- Necesidad de reentrenamiento periodico
- Validacion continua de desempeno

---

### RN-AI-H-002: Sesgo en Datos de Entrenamiento

**Hecho**: Todo conjunto de datos refleja sesgos del contexto en que fue recolectado.

**Implicacion**: Los modelos heredan y pueden amplificar sesgos presentes en los datos de entrenamiento.

**Impacto en requisitos**:
- Auditoria de datasets
- Metricas de fairness
- Procesos de deteccion de sesgo

---

### RN-AI-H-003: Tradeoff Accuracy vs Interpretability

**Hecho**: Existe un tradeoff fundamental entre la precision de un modelo y su interpretabilidad.

**Implicacion**: Modelos mas complejos (deep learning) son mas precisos pero menos interpretables que modelos simples (regresion logistica).

**Impacto en requisitos**:
- Seleccion de modelo segun caso de uso
- Requisitos de explicabilidad
- Documentacion de decisiones de arquitectura

---

### RN-AI-H-004: Dependencia de Infraestructura Computacional

**Hecho**: El entrenamiento y despliegue de modelos de IA requiere recursos computacionales significativos (GPU/TPU).

**Implicacion**: El costo de infraestructura es proporcional a la complejidad del modelo y volumen de datos.

**Impacto en requisitos**:
- Presupuesto de infraestructura
- Seleccion de proveedores cloud
- Optimizacion de modelos para produccion

---

### RN-AI-H-005: Ciclo de Vida de Modelos

**Hecho**: Los modelos de IA se degradan con el tiempo a medida que los datos reales divergen de los datos de entrenamiento.

**Implicacion**: Los modelos requieren mantenimiento continuo (reentrenamiento, ajuste) para mantener su desempeno.

**Impacto en requisitos**:
- MLOps y pipelines de CI/CD
- Monitoreo de desempeno en produccion
- Procesos de reentrenamiento automatizado

---

## Trazabilidad

| ID Hecho | Afecta RNE | Afecta RU | Afecta RF |
|----------|-----------|-----------|-----------|
| RN-AI-H-001 | RNE-AI-001 | - | RF-AI-005 |
| RN-AI-H-002 | RNE-AI-002 | UC-AI-010 | RF-AI-012 |
| RN-AI-H-003 | RNE-AI-003 | UC-AI-002 | RF-AI-003 |
| RN-AI-H-004 | RNE-AI-004 | - | RF-AI-020 |
| RN-AI-H-005 | RNE-AI-005 | UC-AI-008 | RF-AI-015 |

*IDs de RNE, UC, RF son placeholders - actualizar cuando se creen*

---

## Proximos Pasos

- [ ] Validar hechos con stakeholders del dominio AI
- [ ] Extender con hechos especificos del proyecto IACT
- [ ] Vincular con requerimientos de negocio (RNE)
- [ ] Actualizar matriz de trazabilidad

---

**Ultima actualizacion**: 2025-11-13
**Responsable**: Equipo AI
**Estado**: Draft - Pendiente validacion
