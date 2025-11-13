# META-AGENTE CODEX: Generador Autónomo de Artefactos Técnicos con Razonamiento Complejo

**Versión:** 2.0.0 (Enfoque Técnico-Científico Riguroso)
**Fecha:** Enero 2025
**Continuación desde:** Pipeline de Generación - Etapa 4

---

> **Serie documental**: Esta es la Parte 2 de 3 del manual del META-AGENTE CODEX. Consulte la Parte 1 en `docs/analisis/META_AGENTE_CODEX_PARTE_1.md` y el ExecPlan rector en [`docs/plans/EXECPLAN_meta_agente_codex.md`](../plans/EXECPLAN_meta_agente_codex.md). El ETA-AGENTE CODEX exige que cada entrega permanezca autocontenida en `docs/analisis/` y enlazada desde los catálogos oficiales.

## 3. Pipeline de Generación del Artefacto (Continuación)

### 3.5 Etapa 4: Construcción de Estructura

**Objetivo:**
Generar la estructura completa del artefacto CODEX con todas sus secciones, pobladas con contenido extraído de la literatura y derivaciones formales.

**Entradas:**
- Especificación YAML completa.
- Corpus de literatura clasificada (Etapa 2).
- Propiedades formales, anti-patterns y restricciones (Etapa 3).

**Actividades:**

**Actividad 4.1: Generación de Sección 0 (Propósito)**

```
Extraer de especificación:
  - Nombre de especialización.
  - Clasificación.
  - Nivel de madurez.
  - Problema fundamental.

Generar contenido:
  Propósito = template con:
    "Este artefacto CODEX documenta [nombre] para [objetivo].
     La especialización [nombre] aborda el problema fundamental de
     [problema], resolviendo [qué resuelve específicamente].
     Nivel de madurez: [nivel]."
```

**Actividad 4.2: Generación de Sección 1 (Supuestos y Alcance)**

```
De especificación, extraer:
  - Restricciones técnicas del entorno.
  - Supuestos de contexto.

De Etapa 1, incluir:
  - Flags: solo_evidencia_empirica, baja_formalizabilidad.
  - Advertencias generadas.

Generar sección con:
  1.1 Supuestos Fundamentales.
  1.2 Dentro del Alcance.
  1.3 Fuera del Alcance.
  1.4 Restricciones Técnicas.
  1.5 Dependencias Externas.
```

**Actividad 4.3: Generación de Sección 2 (Fundamentos Teóricos)**

```
De propiedades formales (Etapa 3):
  Para cada propiedad:
    Generar subsección con:
      - Teorema/Propiedad: [Enunciado formal].
      - Condiciones de aplicabilidad.
      - Implicaciones para [especialización].
      - Referencia: [Paper fundacional].

De restricciones cuantitativas (Etapa 3):
  Para cada restricción:
    Generar subsección con:
      - Cota inferior: Ω(f(n)).
      - Cota superior: O(g(n)).
      - Demostración o referencia.
      - Gap analysis si f(n) < g(n).
      - Implicación práctica.

Si flag solo_evidencia_empirica:
  Agregar nota:
    "No se encontraron fundamentos teóricos formales en literatura.
     Esta sección se basa en propiedades observadas empíricamente."
```

**Actividad 4.4: Generación de Sección 3 (Literatura Académica)**

```
Del corpus (Etapa 2):
  Agrupar papers por tipo:
    - Seminales (teóricos/fundacionales).
    - Empíricos recientes.
    - Meta-análisis.

  Para cada grupo:
    Para cada paper:
      Generar ficha con:
        - Referencia completa.
        - Calidad metodológica evaluada.
        - Contribución principal.
        - Relevancia para este artefacto.
        - Limitaciones documentadas por autores.

  Generar subsección "Gaps Identificados":
    Listar áreas donde literatura es escasa o contradictoria.
```

**Actividad 4.5: Generación de Sección 4 (Catálogo de Anti-Patterns)**

```
De anti-patterns (Etapa 3):
  Para cada anti-pattern:
    Generar sección completa con:
      - ID: AP-[número].
      - Definición formal.
      - Evidencia empírica (con referencia).
      - Mecanismo causal.
      - Síntomas observables.
      - Impacto cuantificado (si disponible).
      - Estrategias de mitigación.
      - Validador automático asociado: VAL-[número].
      - Limitaciones de la evidencia.
      - Contextos de no-aplicabilidad.

Generar resumen al final:
  Total de anti-patterns: [N].
  Por nivel de evidencia:
    - Fuerte (>= 3 estudios): [N1].
    - Moderada (2 estudios): [N2].
    - Débil (1 estudio): [N3].
  Por severidad:
    - Crítico: [N4].
    - Alto: [N5].
    - Medio: [N6].
```

**Actividad 4.6: Generación de Secciones 5-N (Fases de Implementación)**

```
De especificación YAML, extraer fases propuestas.
Si no están explícitas, derivar fases estándar basadas en:
  - Análisis de dependencias entre componentes.
  - Mejores prácticas de la literatura.
  - Orden lógico de construcción.

Para cada fase:
  Generar sección completa con:
    5.X.1 Objetivo de la Fase.
    5.X.2 Componentes Fundamentales.
    5.X.3 Grafo de Dependencias.
    5.X.4 Precondiciones.
    5.X.5 Postcondiciones.
    5.X.6 Tareas.
      Para cada tarea:
        - ID: T-X.Y.
        - Objetivo.
        - Complejidad analizada (cognitiva, integración, riesgo).
        - Entradas.
        - Actividades.
        - Salidas.
        - Criterios de aceptación.
        - Validaciones formales.
        - Anti-patterns a evitar.
        - Propiedades formales garantizadas.
        - Análisis de trade-offs.
        - Dependencias.
        - Rol responsable.
        - Estimación de esfuerzo.
    5.X.7 Estimación de duración de la fase.
```

**Actividad 4.7: Generación de Sección N+4 (Validadores Automáticos)**

```
De restricciones formales (Etapa 3):
  Para cada restricción R_i:
    Derivar validador VAL-i con:
      - Restricción formal que verifica.
      - Derivación (de dónde viene).
      - Anti-pattern que previene.
      - Tipo (estructural/sintáctico/semántico).
      - Algoritmo formal de validación.
      - Complejidad computacional.
      - Condiciones de fallo.
      - Momento de ejecución.
      - Severidad.
      - Análisis de falsos positivos/negativos.
      - Limitaciones.
      - Implementación recomendada.
```

**Salidas:**
- Estructura completa del artefacto con todas las secciones N+1 a N+8.
- Contenido poblado desde literatura y derivaciones.

**Criterio de Aceptación:**
- Todas las secciones obligatorias están presentes.
- Cada sección tiene contenido (no está vacía).
- Referencias están completas y formateadas correctamente.

**Duración:** 5-8 minutos.

### 3.6 Etapa 5: Aplicación de Auto-CoT y Self-Consistency

**Objetivo:**
Aplicar técnicas de razonamiento complejo para validar y enriquecer decisiones críticas del artefacto.

**Entradas:**
- Artefacto con estructura completa (Etapa 4).
- Lista de decisiones críticas identificadas.

**Actividades:**

**Actividad 5.1: Identificación de Decisiones Críticas**

```
Criterios para decisión crítica:
  1. Afecta arquitectura fundamental.
  2. Tiene impacto en múltiples fases.
  3. Es difícil o costosa de revertir.
  4. Requiere trade-off significativo.
  5. Tiene alternativas no triviales.

Escanear artefacto en busca de:
  - Decisiones de diseño arquitectónico.
  - Selección de patrones o tecnologías.
  - Trade-offs documentados.
  - Elecciones con consecuencias de largo plazo.

Objetivo: Identificar 5-10 decisiones críticas.
```

**Actividad 5.2: Aplicación de Auto-CoT a Cada Decisión Crítica**

```
Para cada decision_critica:
  Generar cadena causal completa:
    1. Listar supuestos fundamentales.
    2. Construir razonamiento paso a paso.
    3. Derivar consecuencias verificables.
    4. Documentar limitaciones.
    5. Agregar referencias.

  Validar cadena:
    - Supuestos explícitos: >= 2.
    - Saltos lógicos: 0.
    - Consecuencias verificables: >= 90%.
    - Limitaciones documentadas: >= 1.

  Insertar en artefacto en Sección N+2.
```

**Actividad 5.3: Aplicación de Self-Consistency**

```
Para cada decision_critica:
  Analizar desde 3 perspectivas INDEPENDIENTES:

  Ruta A (Formal-Teórica):
    Buscar en papers teóricos:
      - Teoremas aplicables.
      - Propiedades formales.
      - Cotas de complejidad.
    Concluir: APROBADO / CONDICIONAL / RECHAZADO.
    Justificar basado en teoría.

  Ruta B (Empírica-Experimental):
    Buscar en estudios empíricos:
      - Benchmarks.
      - Métricas observadas.
      - Case studies.
    Concluir: APROBADO / CONDICIONAL / RECHAZADO.
    Justificar basado en datos.

  Ruta C (Pragmática-Operacional):
    Analizar desde perspectiva práctica:
      - Costo operacional.
      - Skill requirements.
      - Mantenibilidad.
      - TCO (Total Cost of Ownership).
    Concluir: APROBADO / CONDICIONAL / RECHAZADO.
    Justificar basado en viabilidad.

  Comparar conclusiones:
    Si las 3 coinciden:
      Estado: CONVERGENCIA TOTAL.
      Acción: Documentar consenso.

    Si 2 de 3 coinciden:
      Estado: CONVERGENCIA PARCIAL.
      Acción: Analizar divergencia.

    Si ninguna coincide:
      Estado: DIVERGENCIA TOTAL.
      Acción: Análisis profundo, posible rechazo.

  Clasificar divergencias:
    - CONTRADICCIÓN LÓGICA: Crítico.
    - PRIORIZACIÓN DIFERENTE: Media.
    - INFORMACIÓN COMPLEMENTARIA: Baja.

  Generar síntesis final:
    Integrar las 3 perspectivas.
    Documentar divergencias resueltas.
    Proporcionar recomendación contextual.

  Insertar en artefacto en Sección N+3.
```

**Actividad 5.4: Cálculo de Score de Convergencia**

```
decisiones_convergentes = 0
total_decisiones = len(decisiones_criticas)

Para cada decision_critica:
  Si las 3 rutas tienen misma conclusión:
    decisiones_convergentes += 1

score_convergencia = decisiones_convergentes / total_decisiones

Evaluar:
  Si score >= 0.85:
    Estado: ALTA COHERENCIA.
  Si 0.70 <= score < 0.85:
    Estado: COHERENCIA ACEPTABLE.
  Si score < 0.70:
    Estado: BAJA COHERENCIA.
    Acción: Requiere revisión profunda.
```

**Salidas:**
- Sección N+2 con cadenas causales Auto-CoT completas.
- Sección N+3 con análisis Self-Consistency.
- Score de convergencia calculado.

**Criterio de Aceptación:**
- Todas las decisiones críticas (>= 5) tienen Auto-CoT completo.
- Todas las decisiones críticas tienen Self-Consistency analizado.
- Score de convergencia >= 0.70.

**Duración:** 3-5 minutos.

### 3.7 Etapa 6: Validación Multi-Capa

**Objetivo:**
Ejecutar validación exhaustiva del artefacto completo en 3 capas independientes con métricas cuantitativas.

**Entradas:**
- Artefacto completo con Auto-CoT y Self-Consistency.

**Actividades:**

**Actividad 6.1: Validación Capa 1 (Coherencia Lógica)**

Métricas evaluadas:

**Métrica 1.1: Completitud de Cadenas Causales**

```
Definición: % de decisiones críticas con cadena completa.
Umbral: >= 95%.
Proceso:
  decisiones_con_cadena = contar decisiones con Auto-CoT completo.
  ratio = decisiones_con_cadena / total_decisiones_criticas.
  Si ratio < 0.95: FAIL.
```

**Métrica 1.2: Ausencia de Saltos Lógicos**

```
Definición: Número de inferencias sin justificación.
Umbral: 0.
Proceso:
  Para cada cadena Auto-CoT:
    Para cada paso de razonamiento R_i:
      Verificar que tiene:
        - Justificación (lógica formal o referencia).
        - Derivación explícita desde paso anterior.
      Si no tiene: marcar como salto lógico.
  total_saltos = contar saltos.
  Si total_saltos > 0: FAIL.
```

**Métrica 1.3: Verificabilidad de Consecuencias**

```
Definición: % de consecuencias con criterio objetivo.
Umbral: >= 90%.
Proceso:
  Para cada consecuencia en todas las cadenas:
    Verificar que tiene:
      - Métrica cuantitativa o.
      - Condición binaria verificable.
    Si tiene: marcar como verificable.
  ratio = verificables / total_consecuencias.
  Si ratio < 0.90: FAIL.
```

**Métrica 1.4: Coverage de Mitigaciones**

```
Definición: % de riesgos altos con mitigación.
Umbral: 100%.
Proceso:
  riesgos_altos = riesgos con P > 0.5 y I > 3.
  con_mitigacion = contar riesgos altos con estrategia documentada.
  ratio = con_mitigacion / riesgos_altos.
  Si ratio < 1.00: FAIL.
```

**Métrica 1.5: Transitividad de Decisiones**

```
Definición: Violaciones de transitividad.
Umbral: 0.
Proceso:
  Para cada triple (decisión_A, decisión_B, decisión_C):
    Si A implica B y B implica C:
      Verificar que A implica C.
      Si no implica: marcar violación.
  total_violaciones = contar violaciones.
  Si total_violaciones > 0: FAIL.
```

**Métrica 1.6: Ausencia de Contradicciones**

```
Definición: Pares de decisiones con consecuencias contradictorias.
Umbral: 0.
Proceso:
  Para cada par (decisión_i, decisión_j):
    Extraer consecuencias Ci, Cj.
    Si existe c en Ci tal que NOT(c) en Cj:
      marcar como contradicción.
  total_contradicciones = contar contradicciones.
  Si total_contradicciones > 0: FAIL.
```

Estado Capa 1:
- Si todas las métricas pasan: PASS.
- Si alguna métrica falla: FAIL.

**Actividad 6.2: Validación Capa 2 (Self-Consistency)**

Métricas evaluadas:

**Métrica 2.1: Score de Convergencia Global**

```
Definición: % de decisiones donde 3 rutas convergen.
Umbral: >= 85%.
Proceso:
  (Ya calculado en Etapa 5, Actividad 5.4).
  Si score_convergencia < 0.85: FAIL.
```

**Métrica 2.2: Divergencias No Resueltas**

```
Definición: Número de contradicciones lógicas sin resolver.
Umbral: 0.
Proceso:
  divergencias_contradiccion = contar divergencias tipo CONTRADICCIÓN.
  sin_resolver = contar contradicciones sin síntesis final.
  Si sin_resolver > 0: FAIL.
```

**Métrica 2.3: Calidad de Resoluciones**

```
Definición: % de divergencias con síntesis válida.
Umbral: >= 90%.
Proceso:
  total_divergencias = contar todas las divergencias.
  con_sintesis = contar divergencias con recomendación final.
  ratio = con_sintesis / total_divergencias.
  Si ratio < 0.90: WARNING (no bloqueante).
```

**Métrica 2.4: Documentación de Trade-offs**

```
Definición: % de divergencias de priorización con trade-off documentado.
Umbral: 100%.
Proceso:
  divergencias_priorizacion = contar tipo PRIORIZACIÓN.
  con_tradeoff = contar con análisis costo-beneficio.
  ratio = con_tradeoff / divergencias_priorizacion.
  Si ratio < 1.00: FAIL.
```

Estado Capa 2:
- Si todas las métricas pasan: PASS.
- Si alguna métrica FAIL: FAIL.
- Si solo WARNING: PASS con advertencias.

**Actividad 6.3: Validación Capa 3 (Viabilidad y Riesgos)**

Métricas evaluadas:

**Métrica 3.1: Coverage de Anti-Patterns**

```
Definición: % de anti-patterns conocidos cubiertos.
Umbral: >= 90%.
Proceso:
  Buscar anti-patterns de la especialización en literatura.
  total_literatura = contar anti-patterns en papers.
  total_artefacto = contar anti-patterns en Sección 4.
  ratio = total_artefacto / total_literatura.
  Si ratio < 0.90: WARNING.
```

**Métrica 3.2: Evidencia Empírica de Anti-Patterns**

```
Definición: % de anti-patterns con evidencia peer-reviewed.
Umbral: >= 80%.
Proceso:
  Para cada anti-pattern:
    Verificar que tiene:
      - Al menos 1 referencia peer-reviewed y
      - Descripción de metodología del estudio.
    Si tiene: marcar como con evidencia.
  ratio = con_evidencia / total_antipatterns.
  Si ratio < 0.80: WARNING.
```

**Métrica 3.3: Mitigación de Riesgos Críticos**

```
Definición: % de riesgos críticos con mitigación.
Umbral: 100%.
Proceso:
  (Igual que Métrica 1.4).
  Si ratio < 1.00: FAIL.
```

**Métrica 3.4: Documentación de Limitaciones**

```
Definición: Secciones sin limitaciones documentadas.
Umbral: 0.
Proceso:
  secciones_relevantes = [todas las secciones de decisiones].
  sin_limitaciones = contar secciones sin subsección "Limitaciones".
  Si sin_limitaciones > 0: FAIL.
```

**Métrica 3.5: Calidad de Referencias Académicas**

```
Definición: % de afirmaciones críticas con referencia peer-reviewed.
Umbral: >= 85%.
Proceso:
  afirmaciones_criticas = identificar claims sobre:
    - Propiedades formales.
    - Impacto de anti-patterns.
    - Métricas de performance.
    - Trade-offs cuantificados.
  con_referencia = contar afirmaciones con cita peer-reviewed.
  ratio = con_referencia / afirmaciones_criticas.
  Si ratio < 0.85: FAIL.
```

Estado Capa 3:
- Si todas las métricas pasan: PASS.
- Si métricas FAIL: FAIL.
- Si solo WARNING: PASS con recomendaciones.

**Actividad 6.4: Consolidación de Resultados**

```
Calcular score global:
  score_capa1 = promedio de métricas Capa 1.
  score_capa2 = promedio de métricas Capa 2.
  score_capa3 = promedio de métricas Capa 3.

  score_global = (
    score_capa1 * 0.40 +
    score_capa2 * 0.35 +
    score_capa3 * 0.25
  )

Decisión final:
  Si score_global >= 0.90 y Capa1 == PASS:
    VALIDADO.
  Si 0.85 <= score_global < 0.90:
    CONDICIONAL (requiere revisión).
  Si score_global < 0.85 o Capa1 == FAIL:
    RECHAZADO (requiere regeneración).

Generar reporte de validación:
  - Estado de cada capa.
  - Métricas detalladas.
  - Score global.
  - Acciones requeridas si RECHAZADO o CONDICIONAL.
```

**Salidas:**
- Reporte de validación completo (archivo separado).
- Estado: VALIDADO / CONDICIONAL / RECHAZADO.
- Score global.

**Criterio de Aceptación:**
- Estado == VALIDADO.

**Duración:** 2-3 minutos.

---

## 4. Formato de Entrada: Especificación de Especialización

### 4.1 Template YAML

```yaml
especializacion:
  nombre: "Event Sourcing"
  clasificacion: "Patrón Arquitectónico"
  nivel_madurez: "Establecido"  # Experimental / Emergente / Establecido / Maduro
  
problema_fundamental:
  descripcion: |
    Capturar todos los cambios de estado como secuencia inmutable de eventos,
    permitiendo reconstrucción del estado en cualquier punto del tiempo.
  desde_primeros_principios: |
    En sistemas tradicionales CRUD, el estado actual sobrescribe el anterior,
    perdiendo información histórica. Event Sourcing preserva la secuencia
    completa de cambios mediante append-only log, derivando el estado como
    función de proyección sobre eventos.

propiedades_deseadas:
  - nombre: "Auditoría Completa"
    verificable: true
    criterio: "100% de cambios de estado tienen evento asociado"
    
  - nombre: "Performance Aceptable"
    verificable: true
    criterio: "P99 latencia de writes <= 100ms"
    
  - nombre: "Reconstrucción de Estado"
    verificable: true
    criterio: "Reconstrucción en <= 1 segundo para entidad típica"

restricciones_tecnicas:
  entorno:
    - "Event store debe soportar >= 10K eventos/segundo"
    - "Sistema debe operar en cloud con eventual consistency"
    - "Compliance con GDPR (derecho al olvido)"
  
  equipo:
    - "Equipo tiene experiencia en sistemas distribuidos"
    - "Disponibilidad de 6 meses para implementación"
    - "Budget permite +50% de costo infraestructura"

contexto:
  dominio: "Finanzas"
  criticidad: "Alta"
  regulacion: "SOX, GDPR"
  volumetria_esperada:
    eventos_por_segundo: 5000
    entidades_activas: 100000
    retencion_anos: 7

objetivos_especificos:
  - "Implementar event sourcing para módulo de transacciones"
  - "Migrar desde sistema CRUD existente"
  - "Garantizar zero downtime durante migración"
  - "Habilitar auditoría en tiempo real"
```

### 4.2 Instrucciones de Completar el Template

**Campo: nombre**
- Usar nombre técnico preciso de la especialización.
- Evitar nombres de productos comerciales.
- Ejemplo correcto: "Event Sourcing".
- Ejemplo incorrecto: "EventStoreDB" (es un producto, no la especialización).

**Campo: clasificacion**
- Opciones válidas:
  - Patrón Arquitectónico (ej.: Event Sourcing, CQRS, Microservices).
  - Técnica de Programación (ej.: Memoization, Lazy Evaluation).
  - Algoritmo (ej.: Consistent Hashing, Bloom Filters).
  - Estructura de Datos (ej.: CRDT, Skip List).
  - Protocolo (ej.: Raft, Paxos).
  - Metodología (ej.: Test-Driven Development).

**Campo: nivel_madurez**
- Experimental: < 5 papers peer-reviewed, < 3 años en uso.
- Emergente: 5-20 papers, 3-7 años en uso, adopción creciente.
- Establecido: >= 20 papers, >= 7 años, amplia adopción.
- Maduro: >= 50 papers, >= 15 años, estándar de la industria.

**Campo: problema_fundamental**
- Describir QUÉ problema resuelve, no CÓMO lo resuelve.
- Incluir derivación desde primeros principios.
- Explicar por qué enfoques tradicionales no son suficientes.

**Campo: propiedades_deseadas**
- Cada propiedad DEBE ser verificable objetivamente.
- Incluir criterio cuantitativo o binario.
- Evitar propiedades vagas ("debe ser rápido" → especificar umbral).

**Campo: restricciones_tecnicas**
- Ser específico sobre el entorno (cloud, on-premise, edge).
- Documentar limitaciones conocidas.
- Incluir restricciones regulatorias si aplican.

**Campo: contexto**
- Proporcionar contexto real del proyecto.
- Criticidad: Baja / Media / Alta / Crítica.
- Volumetría con números realistas.

### 4.3 Checklist Pre-Envío

Antes de enviar la especificación al meta-agente, verificar:

```
[ ] Nombre de especialización es técnico y preciso.
[ ] Clasificación es una de las opciones válidas.
[ ] Nivel de madurez refleja la realidad (buscar en Google Scholar).
[ ] Problema fundamental está descrito desde primeros principios.
[ ] Todas las propiedades deseadas son verificables objetivamente.
[ ] Restricciones técnicas son específicas, no genéricas.
[ ] Contexto incluye dominio, criticidad y volumetría.
[ ] Objetivos son medibles.
[ ] Budget y timeline son realistas.
```

---

## 5. Estructura del Artefacto CODEX Generado

### 5.1 Secciones Obligatorias

Todo artefacto generado contiene exactamente estas secciones en orden:

**Sección 0: Propósito**
- Objetivo del artefacto.
- Contexto de la especialización.
- Problema fundamental desde primeros principios.
- Nivel de madurez.

**Sección 1: Supuestos y Alcance**
- Supuestos fundamentales (técnicos, operacionales, de contexto).
- Dentro del alcance.
- Fuera del alcance.
- Restricciones técnicas.
- Dependencias externas.

**Sección 2: Fundamentos Teóricos de la Especialización**
- Teoremas fundamentales aplicables.
- Cotas de complejidad (inferiores y superiores).
- Propiedades formales (safety, liveness, security).
- Invariantes del sistema.
- Referencias fundacionales.

**Sección 3: Análisis de Literatura Académica**
- Papers seminales con evaluación de calidad.
- Estudios empíricos recientes.
- Meta-análisis y revisiones sistemáticas.
- Gaps identificados en la literatura.

**Sección 4: Catálogo de Anti-Patterns**
- Para cada anti-pattern:
  - ID, definición formal.
  - Evidencia empírica peer-reviewed.
  - Mecanismo causal.
  - Síntomas observables.
  - Impacto cuantificado.
  - Estrategias de mitigación.
  - Validador automático asociado.
  - Limitaciones del validador.

**Secciones 5-N: Fases de Implementación**
- Cada fase contiene:
  - Objetivo formal.
  - Componentes fundamentales.
  - Grafo de dependencias.
  - Precondiciones y postcondiciones.
  - Tareas atómicas con:
    - Complejidad analizada.
    - Validaciones formales.
    - Anti-patterns a evitar.
    - Propiedades garantizadas.
    - Trade-offs.
    - Estimación de esfuerzo.

**Sección N+1: Análisis de Trade-offs Multi-Perspectiva**
- Trade-offs identificados desde las 3 rutas.
- Cuantificación desde perspectiva empírica.
- Impacto operacional desde perspectiva pragmática.
- Estrategias de mitigación con efectividad documentada.

**Sección N+2: Decisiones Críticas con Cadenas Causales (Auto-CoT)**
- Cada decisión crítica con:
  - Supuestos explícitos.
  - Razonamiento paso a paso.
  - Consecuencias verificables.
  - Limitaciones documentadas.
  - Referencias.

**Sección N+3: Resultados de Self-Consistency**
- Análisis desde 3 perspectivas para cada decisión.
- Convergencias y divergencias identificadas.
- Resolución de divergencias.
- Score de convergencia global.

**Sección N+4: Especificación de Validadores Automáticos**
- Para cada validador:
  - Restricción formal que verifica.
  - Derivación desde propiedades.
  - Algoritmo con complejidad.
  - Análisis de falsos positivos/negativos.
  - Implementación recomendada.

**Sección N+5: Criterios de Aceptación del Artefacto**
- Checklist de validación técnica.
- Métricas de éxito con umbrales.
- Validadores a ejecutar por fase.
- Condiciones de Go/No-Go.

**Sección N+6: Limitaciones y Contextos de No-Aplicabilidad**
- Limitaciones generales del enfoque.
- Limitaciones por decisión crítica.
- Contextos donde NO aplicar.
- Uncertainty residual.
- Gaps de conocimiento reconocidos.

**Sección N+7: Referencias Académicas Completas**
- Clasificadas por tipo (teórico, empírico, meta-análisis).
- Con evaluación de calidad metodológica.
- Distribuidas por sección del artefacto.

**Sección N+8: Roadmap de Implementación**
- Orden de ejecución recomendado.
- Duración total del proyecto.
- Estrategia de rollout.
- Hitos de validación críticos.
- Monitoreo durante implementación.
- Criterios de Go/No-Go por fase.
- Plan de rollback.

### 5.2 Formato Markdown

El artefacto se genera en Markdown puro con:
- Headers de nivel 1-5 para jerarquía.
- Listas con guiones (-) para ítems.
- Bloques de código con triple backtick para algoritmos.
- Tablas en formato Markdown para comparaciones.
- Links internos para referencias cruzadas.

**Sin:**
- Emojis.
- Iconos Unicode decorativos.
- Cajas ASCII.
- Separadores decorativos.

### 5.3 Tamaño Esperado

Dependiendo de la especialización:
- Mínimo: 30 KB (especializaciones simples).
- Típico: 50-100 KB (especializaciones establecidas).
- Máximo: 200 KB (especializaciones muy complejas).

---

> **Próximo paso**: La Parte 3 documentará las secciones 6-9 (Instrucciones de uso, formato de salida, limitaciones y conclusión), completando el alcance definido en el ExecPlan.
