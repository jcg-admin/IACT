# Biblioteca de Meta-Prompting para Agentes Copilot

Este compendio reúne los patrones de meta-prompting solicitados para el proyecto IACT. Cada bloque mantiene la estructura original
para que los agentes puedan generar, evaluar, optimizar y validar prompts complejos sin improvisar. Personaliza los marcadores `[]`
antes de ejecutar cada plantilla.

## 1. Generador Universal de Prompts

### Prompt Base para Generar Prompts Optimizados
```
Actúa como un experto en prompt engineering con 10+ años optimizando LLMs.

Genera un prompt altamente optimizado para esta tarea:

TAREA OBJETIVO: [descripción de la tarea]
DOMINIO: [área específica: desarrollo, análisis, etc.]
MODELO TARGET: [Claude/ChatGPT/específico]
AUDIENCIA: [nivel técnico del usuario]
CONTEXTO CRÍTICO: [información esencial]

ESTRUCTURA REQUERIDA PARA EL PROMPT GENERADO:
1. CONTEXTO/ROL específico y detallado
2. INSTRUCCIONES precisas con criterios medibles
3. EJEMPLOS cuando sea necesario para clarificar
4. FORMATO DE SALIDA estructurado
5. VALIDACIONES para prevenir alucinaciones
6. RESTRICCIONES técnicas y de seguridad

CRITERIOS DE CALIDAD:
- Debe ser específico, no genérico
- Debe incluir validaciones anti-alucinación
- Debe ser reproducible y consistente
- Debe incluir métricas de éxito
- Debe considerar edge cases

FORMATO DE RESPUESTA:
## Prompt Optimizado
[El prompt generado aquí]

## Explicación de Decisiones de Diseño
[Por qué cada elemento fue incluido]

## Casos de Prueba Sugeridos
[3-5 casos para validar efectividad]

## Métricas de Evaluación
[Cómo medir si el prompt funciona]

## Variaciones para Diferentes Contextos
[Adaptaciones para casos específicos]

Antes de generar, verifica:
- ¿El prompt resultante minimiza riesgo de alucinaciones?
- ¿Incluye validaciones específicas?
- ¿Es técnicamente preciso para el dominio especificado?
```

## 2. Optimizador Automático de Prompts Existentes

### Meta-Prompt para Mejorar Prompts
```
Analiza y optimiza este prompt existente aplicando principios avanzados de prompt engineering.

PROMPT ACTUAL A OPTIMIZAR:
[prompt existente]

PROBLEMAS IDENTIFICADOS CON EL PROMPT:
[si se conocen problemas específicos]

CONTEXTO DE USO:
- Frecuencia de uso: [diaria/semanal/ocasional]
- Criticidad: [alta/media/baja]
- Usuarios: [técnicos/no técnicos/mixto]

ANÁLISIS SISTEMÁTICO REQUERIDO:

## 1. Diagnóstico de Problemas
Identifica específicamente:
- Ambigüedades que pueden causar interpretaciones incorrectas
- Falta de contexto que puede llevar a alucinaciones
- Ausencia de validaciones de calidad
- Instrucciones poco específicas
- Formato de salida mal definido

## 2. Evaluación de Riesgo de Alucinaciones
Para cada parte del prompt, evalúa:
- ¿Qué información podría el modelo inventar?
- ¿Hay suficiente contexto para respuestas precisas?
- ¿Las instrucciones son lo suficientemente específicas?

## 3. Prompt Optimizado
Genera versión mejorada que:
- Elimine ambigüedades identificadas
- Agregue validaciones específicas
- Incluya contexto suficiente
- Defina formato de salida claro
- Incorpore checks de calidad

## 4. Comparación Lado a Lado
| Aspecto | Prompt Original | Prompt Optimizado | Mejora Esperada |
|---------|----------------|-------------------|-----------------|
| Claridad | | | |
| Especificidad | | | |
| Anti-alucinación | | | |
| Consistencia | | | |

## 5. Plan de Testing A/B
Define cómo validar que la versión optimizada es superior:
- Casos de prueba específicos
- Métricas de comparación
- Criterios de éxito

VALIDACIÓN FINAL:
Antes de entregar el prompt optimizado, verifica:
- ¿Cada instrucción es específica y medible?
- ¿Hay suficiente contexto para evitar alucinaciones?
- ¿El formato de salida está claramente definido?
- ¿Incluye validaciones de calidad?
```

## 3. Generador de Prompts Anti-Alucinación

### Meta-Prompt Especializado en Prevenir Alucinaciones
```
Genera un prompt ultra-robusto contra alucinaciones para esta tarea crítica.

TAREA CRÍTICA: [descripción]
RIESGO DE ALUCINACIÓN: [alto/medio/bajo]
CONSECUENCIAS DE ERROR: [críticas/moderadas/menores]

ESTRATEGIAS ANTI-ALUCINACIÓN A IMPLEMENTAR:

1. VALIDACIÓN MÚLTIPLE
- Verificación de información factual
- Cross-checking de datos
- Solicitar fuentes cuando sea aplicable

2. RESTRICCIONES ESPECÍFICAS
- Prohibir invención de información
- Requerir admisión de incertidumbre
- Limitar scope de respuesta a conocimiento confirmado

3. FORMATO DE RESPUESTA CONTROLADO
- Separar hechos confirmados de análisis
- Incluir nivel de confianza
- Requerir disclaimers cuando sea apropiado

GENERA EL PROMPT SIGUIENDO ESTA ESTRUCTURA:

## Prompt Anti-Alucinación
[Contexto específico con énfasis en precisión]
[Instrucciones que prohíben invención]
[Requerimientos de validación]
[Formato que separa hechos de análisis]
[Disclaimers obligatorios]

## Ejemplos de Respuestas Correctas
[2-3 ejemplos mostrando cómo responder correctamente]

## Ejemplos de Respuestas Incorrectas (a evitar)
[2-3 ejemplos de alucinaciones típicas para este dominio]

## Frases de Seguridad
Incluye estas frases obligatorias:
- "Basándome en información verificable..."
- "No tengo datos confirmados sobre..."
- "Requiere verificación adicional..."
- "Dentro de mi conocimiento actualizado hasta..."

## Métricas de Verificación
Cómo validar que las respuestas no contienen alucinaciones:
- [criterios específicos de verificación]
- [fuentes de validación recomendadas]
- [señales de alerta de posible alucinación]
```

## 4. Generador de Prompts por Dominio Técnico

### Meta-Prompt para Desarrollo de Software
```
Genera un prompt especializado para [DOMINIO ESPECÍFICO] que incorpore mejores prácticas del área.

DOMINIO TÉCNICO: [ej: desarrollo web, arquitectura de sistemas, etc.]
NIVEL DE EXPERTISE REQUERIDO: [junior/mid/senior]
STACK TECNOLÓGICO: [tecnologías específicas]

CONOCIMIENTO DEL DOMINIO A INCORPORAR:

## Mejores Prácticas del Dominio
Lista las mejores prácticas que el prompt debe reforzar:
- [práctica 1 con justificación técnica]
- [práctica 2 con justificación técnica]

## Errores Comunes a Evitar
Identifica errores típicos que el prompt debe prevenir:
- [error común 1 y cómo evitarlo]
- [error común 2 y cómo evitarlo]

## Terminología Técnica Precisa
Términos que deben usarse correctamente:
- [término 1: definición precisa]
- [término 2: definición precisa]

PROMPT ESPECIALIZADO GENERADO:

## Contexto Técnico Especializado
[Rol específico con credenciales técnicas del dominio]

## Instrucciones Técnicas Específicas
[Pasos que incorporan mejores prácticas del dominio]

## Criterios de Calidad Técnica
[Métricas específicas del dominio para evaluar calidad]

## Validaciones Técnicas
Verificar antes de responder:
- ¿La solución sigue mejores prácticas de [dominio]?
- ¿La terminología técnica es precisa?
- ¿Se consideraron las implicaciones de seguridad?
- ¿Es escalable y mantenible?

## Formato Técnico Estructurado
[Estructura específica para respuestas técnicas del dominio]

## Casos Edge Técnicos
Consideraciones especiales para:
- [escenario técnico complejo 1]
- [escenario técnico complejo 2]
```

## 5. Evaluador Automático de Calidad de Prompts

### Meta-Prompt para Evaluar Otros Prompts
```
Actúa como evaluador experto de prompts. Analiza sistemáticamente la calidad de este prompt.

PROMPT A EVALUAR:
[prompt a analizar]

CONTEXTO DE USO:
- Propósito: [objetivo del prompt]
- Frecuencia: [uso esperado]
- Usuarios: [perfil de usuarios]

EVALUACIÓN SISTEMÁTICA:

## 1. Análisis de Estructura (Puntuación: /10)
Evalúa presencia y calidad de:
- Contexto/Rol: [puntuación y comentarios]
- Instrucciones: [puntuación y comentarios]
- Ejemplos: [puntuación y comentarios]
- Formato de salida: [puntuación y comentarios]
- Restricciones: [puntuación y comentarios]

## 2. Riesgo de Alucinación (Puntuación: /10)
Analiza vulnerabilidades:
- ¿Qué información podría inventar el modelo?
- ¿Hay suficiente contexto para respuestas precisas?
- ¿Las instrucciones son específicas?
- ¿Incluye validaciones apropiadas?

## 3. Claridad y Especificidad (Puntuación: /10)
Evalúa:
- Ambigüedades presentes
- Nivel de especificidad de instrucciones
- Claridad de expectativas
- Facilidad de interpretación

## 4. Reproducibilidad (Puntuación: /10)
Analiza:
- Consistencia esperada de resultados
- Dependencia de interpretación subjetiva
- Factores que podrían causar variabilidad

## 5. Completitud (Puntuación: /10)
Verifica si incluye:
- Toda la información necesaria
- Contexto suficiente
- Criterios de éxito claros
- Manejo de casos edge

## REPORTE DE EVALUACIÓN

### Puntuación Total: [X/50]

### Fortalezas Identificadas:
- [fortaleza 1 con explicación]
- [fortaleza 2 con explicación]

### Debilidades Críticas:
- [debilidad 1 con impacto]
- [debilidad 2 con impacto]

### Recomendaciones de Mejora:
1. [mejora específica con justificación]
2. [mejora específica con justificación]

### Riesgo de Fallo:
- Probabilidad: [alta/media/baja]
- Factores de riesgo: [lista específica]
- Mitigaciones sugeridas: [acciones concretas]

### Prompt Mejorado Sugerido:
[Versión optimizada incorporando mejoras identificadas]
```

## 6. Generador de Variaciones de Prompts para A/B Testing

### Meta-Prompt para Testing Sistemático
```
Genera múltiples variaciones de este prompt para testing A/B sistemático.

PROMPT BASE:
[prompt original]

OBJETIVO DEL TESTING:
[qué aspecto específico se quiere optimizar]

GENERA 5 VARIACIONES SISTEMÁTICAS:

## Variación A: Enfoque en Especificidad
[Versión con instrucciones más específicas y detalladas]

## Variación B: Enfoque en Anti-Alucinación
[Versión con validaciones y restricciones más estrictas]

## Variación C: Enfoque en Estructura
[Versión con formato de salida más estructurado]

## Variación D: Enfoque en Contexto
[Versión con más contexto y ejemplos]

## Variación E: Enfoque en Simplicidad
[Versión simplificada pero efectiva]

## PLAN DE TESTING A/B

### Métricas de Comparación:
- Precisión de respuestas (escala 1-10)
- Relevancia al objetivo (escala 1-10)
- Consistencia entre ejecuciones (escala 1-10)
- Ausencia de alucinaciones (sí/no)
- Tiempo promedio de respuesta
- Satisfacción del usuario (escala 1-10)

### Casos de Prueba Estandarizados:
1. [caso de prueba típico]
2. [caso edge complejo]
3. [caso con potencial de alucinación]
4. [caso con información ambigua]
5. [caso que requiere razonamiento complejo]

### Metodología de Evaluación:
Para cada variación y caso de prueba:
1. Ejecutar prompt 3 veces
2. Evaluar cada respuesta según métricas
3. Promediar resultados
4. Documentar patrones y anomalías

### Hipótesis de Testing:
- Variación A debería mejorar precisión
- Variación B debería reducir alucinaciones
- Variación C debería mejorar consistencia
- Variación D debería mejorar relevancia
- Variación E debería mejorar velocidad

### Criterios de Selección del Ganador:
[Definir claramente qué combinación de métricas determina el prompt óptimo]
```

## 7. Meta-Prompt para Debugging de Prompts Problemáticos

### Diagnóstico y Corrección Automática
```
Diagnostica por qué este prompt está fallando y genera una versión corregida.

PROMPT PROBLEMÁTICO:
[prompt que no funciona correctamente]

SÍNTOMAS OBSERVADOS:
[descripción específica de los problemas]

EJEMPLOS DE RESPUESTAS PROBLEMÁTICAS:
[ejemplos de outputs incorrectos]

ANÁLISIS DE DIAGNÓSTICO:

## 1. Identificación de Causas Raíz
Para cada síntoma, identifica la causa probable:

### Alucinaciones Detectadas:
- Causa: [análisis específico]
- Ubicación en el prompt: [dónde está el problema]
- Mecanismo: [cómo ocurre la alucinación]

### Inconsistencias en Respuestas:
- Causa: [análisis de variabilidad]
- Elementos ambiguos: [identificación específica]
- Factores de variación: [qué causa inconsistencia]

### Respuestas Irrelevantes:
- Causa: [análisis de deriva del objetivo]
- Instrucciones vagas: [identificación específica]
- Falta de restricciones: [qué falta]

## 2. Análisis de Estructura Deficiente
Evalúa cada componente:
- Contexto: [problemas identificados]
- Instrucciones: [ambigüedades específicas]
- Ejemplos: [calidad y relevancia]
- Formato: [claridad de especificaciones]
- Validaciones: [ausencias críticas]

## 3. Prompt Corregido
Versión que aborda cada problema identificado:

[Nuevo prompt que específicamente corrige cada problema]

## 4. Explicación de Correcciones
Para cada cambio realizado:
- Problema original: [descripción]
- Corrección aplicada: [modificación específica]
- Razón de la corrección: [justificación técnica]
- Mejora esperada: [resultado anticipado]

## 5. Plan de Validación
Cómo verificar que las correcciones funcionan:
- Casos de prueba específicos para cada problema
- Métricas de éxito para cada corrección
- Señales de que el problema persiste

## 6. Monitoreo Continuo
Qué vigilar en uso futuro:
- Indicadores tempranos de problemas recurrentes
- Métricas de calidad a monitorear
- Triggers para revisión adicional
```

## 8. Generador de Prompts para Diferentes Modelos LLM

### Meta-Prompt para Optimización Multi-Modelo
```
Genera versiones optimizadas de este prompt para diferentes modelos LLM.

PROMPT BASE:
[prompt genérico]

MODELOS TARGET:
- Claude (Anthropic)
- ChatGPT (OpenAI)
- Gemini (Google)

CONSIDERA LAS CARACTERÍSTICAS ESPECÍFICAS:

## Claude-Optimized Version
Incorpora fortalezas de Claude:
- Capacidad de análisis detallado
- Manejo superior de instrucciones complejas
- Mejor adherencia a restricciones éticas
- Capacidad de reasoning estructurado

[Prompt optimizado para Claude]

## ChatGPT-Optimized Version
Incorpora fortalezas de ChatGPT:
- Creatividad en respuestas
- Flexibilidad en formato
- Capacidad conversacional
- Generación de contenido variado

[Prompt optimizado para ChatGPT]

## Gemini-Optimized Version
Incorpora fortalezas de Gemini:
- Integración con búsqueda
- Capacidades multimodales
- Procesamiento de información factual
- Análisis basado en datos actuales

[Prompt optimizado para Gemini]

## ANÁLISIS COMPARATIVO

### Diferencias Clave por Modelo:
| Aspecto | Claude | ChatGPT | Gemini |
|---------|--------|---------|--------|
| Longitud óptima | | | |
| Nivel de detalle | | | |
| Estructura preferida | | | |
| Tipo de ejemplos | | | |
| Restricciones necesarias | | | |

### Métricas de Evaluación por Modelo:
Para cada versión, medir:
- Adherencia a instrucciones
- Calidad de razonamiento
- Ausencia de alucinaciones
- Consistencia de formato
- Relevancia de respuestas

### Recomendaciones de Uso:
- Usar Claude cuando: [escenarios específicos]
- Usar ChatGPT cuando: [escenarios específicos]
- Usar Gemini cuando: [escenarios específicos]
```

## 9. Sistema Completo de Meta-Prompting Automatizado

### Orquestador de Múltiples Meta-Prompts
```
Sistema automatizado que genera, evalúa, optimiza y valida prompts usando múltiples meta-prompts.

TAREA INICIAL:
[descripción de la necesidad de prompt]

PARÁMETROS DEL SISTEMA:
- Criticidad: [alta/media/baja]
- Dominio: [técnico específico]
- Modelo target: [LLM específico]
- Nivel usuario: [expertise requerido]

PROCESO AUTOMATIZADO:

## Fase 1: Generación Inicial
Usar meta-prompt generador universal para crear prompt base

## Fase 2: Evaluación Automática
Usar meta-prompt evaluador para identificar debilidades

## Fase 3: Optimización Específica
Aplicar meta-prompts especializados según debilidades:
- Si hay riesgo de alucinación → meta-prompt anti-alucinación
- Si falta especificidad técnica → meta-prompt de dominio
- Si estructura es deficiente → meta-prompt de estructuración

## Fase 4: Generación de Variaciones
Crear múltiples versiones para A/B testing

## Fase 5: Testing Automatizado
Ejecutar casos de prueba estandarizados

## Fase 6: Selección Automática
Elegir versión óptima basada en métricas

## Fase 7: Validación Final
Verificación humana de prompt seleccionado

## OUTPUTS DEL SISTEMA:

### Prompt Final Optimizado:
[Mejor versión generada por el sistema]

### Reporte de Optimización:
- Iteraciones realizadas: [número]
- Problemas corregidos: [lista]
- Mejoras implementadas: [lista]
- Métricas finales: [puntuaciones]

### Documentación de Uso:
- Casos de uso recomendados
- Limitaciones identificadas
- Métricas de monitoreo sugeridas
- Plan de mantenimiento

### Plan de Evolución:
- Triggers para re-optimización
- Métricas de degradación
- Proceso de actualización
```

## 10. Meta-Prompt para Generación de Prompts de Validación

### Creador de Sistemas de Verificación
```
Genera un prompt especializado en validar y verificar respuestas de otros prompts.

PROMPT PRINCIPAL A VALIDAR:
[prompt que necesita sistema de validación]

RIESGOS ESPECÍFICOS IDENTIFICADOS:
[tipos de errores o alucinaciones esperados]

GENERA PROMPT VALIDADOR:

## Contexto del Validador
Actúa como auditor experto especializado en [dominio específico] con enfoque en detección de errores, alucinaciones y problemas de calidad.

## Instrucciones de Validación
Para cada respuesta del prompt principal, verifica sistemáticamente:

### 1. Verificación Factual
- Identifica afirmaciones específicas que requieren verificación
- Señala información que podría ser inventada
- Marca fechas, nombres, estadísticas para verificación

### 2. Consistencia Lógica
- Verifica coherencia interna de la respuesta
- Identifica contradicciones
- Evalúa validez de razonamiento

### 3. Adherencia a Instrucciones
- Confirma que se siguieron todas las instrucciones
- Verifica formato de salida correcto
- Evalúa completitud de respuesta

### 4. Calidad Técnica (para dominio específico)
- Verifica precisión técnica de soluciones
- Evalúa adherencia a mejores prácticas
- Identifica riesgos de seguridad o performance

## Formato de Reporte de Validación
Para cada aspecto evaluado:

### ✅ VERIFICADO / ❌ PROBLEMA DETECTADO / ⚠️ REQUIERE VERIFICACIÓN

**Verificación Factual:**
- [Elemento 1]: [Status y comentarios]
- [Elemento 2]: [Status y comentarios]

**Consistencia Lógica:**
- [Evaluación general]
- [Problemas específicos si los hay]

**Adherencia a Instrucciones:**
- [Checklist de cumplimiento]

**Calidad Técnica:**
- [Evaluación específica del dominio]

### DICTAMEN FINAL:
- ✅ APROBADO - Respuesta confiable
- ⚠️ APROBADO CON RESERVAS - Requiere verificación de [aspectos específicos]
- ❌ RECHAZADO - Problemas críticos: [lista de problemas]

### RECOMENDACIONES:
[Acciones específicas para mejorar o verificar]

## Casos de Alerta Automática
Rechazar inmediatamente respuestas que contengan:
- [Patrón de alucinación 1 específico del dominio]
- [Patrón de alucinación 2 específico del dominio]
- [Indicadores de información inventada]

## Métricas de Confiabilidad
Asignar puntuación de confiabilidad (1-10) basada en:
- Verificabilidad de afirmaciones (peso: 30%)
- Consistencia lógica (peso: 25%)
- Adherencia a instrucciones (peso: 25%)
- Calidad técnica (peso: 20%)
```

## Consideraciones Críticas para Meta-Prompting

### Prevención de Alucinaciones en Meta-Prompts
1. **Validación en Cascada**: Cada meta-prompt debe validar sus propios outputs.
2. **Restricciones Específicas**: Prohibir explícitamente invención de información.
3. **Contexto Suficiente**: Proporcionar información completa para evitar gaps.
4. **Verificación Cruzada**: Usar múltiples meta-prompts para validar resultados críticos.

### Mejores Prácticas para Implementación
1. **Testing Sistemático**: Cada meta-prompt debe ser probado extensivamente.
2. **Documentación Detallada**: Registrar casos de uso, limitaciones y resultados.
3. **Monitoreo Continuo**: Vigilar degradación de performance en el tiempo.
4. **Iteración Basada en Datos**: Mejorar basándose en métricas reales de uso.

### Limitaciones y Riesgos
1. **Complejidad Exponencial**: Meta-prompts pueden volverse muy complejos.
2. **Propagación de Errores**: Errores en meta-prompts afectan todos los prompts generados.
3. **Over-Engineering**: Riesgo de crear sistemas más complejos de lo necesario.
4. **Dependencia de Calidad**: La calidad de outputs depende completamente de la calidad del meta-prompt.
