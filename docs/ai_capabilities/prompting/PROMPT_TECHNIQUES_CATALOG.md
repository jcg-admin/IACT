---
title: Catálogo Completo de Técnicas de Prompts multi-LLM
date: 2025-11-13
domain: general
status: active
---

# Catálogo Completo de Técnicas de Prompts multi-LLM

Este catálogo unifica las técnicas de prompting aplicables a los tres proveedores soportados por el proyecto (Claude, ChatGPT y Hugging Face) y funciona como referencia canónica para los agentes descritos en `.agent/agents/` y los planes activos `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` y `docs/plans/EXECPLAN_agents_domain_alignment.md`. Cada sección indica cómo reutilizar la técnica dentro del flujo SDLC y enlaza con los dominios Backend (API), Frontend (UI), Infrastructure, Docs y Scripts cuando existen lineamientos específicos.

> **Uso operativo:** Los agentes de dominio (ApiAgent, UiAgent, InfrastructureAgent, DocsAgent, ScriptsAgent) y los agentes por proveedor (ClaudeAgent, ChatGPTAgent, HuggingFaceAgent) deben enlazar a este catálogo para seleccionar la estrategia de prompting adecuada antes de invocar los orquestadores (`scripts/coding/ai/orchestrators/codex_mcp_workflow.py`) o los generadores (`scripts/coding/ai/generators/llm_generator.py`).

## 1. Técnicas de In-Context Learning (ICL)

### 1.1 Few-Shot Prompting
- **Few-Shot Prompting**: paradigma donde el LLM aprende la tarea con pocos ejemplos.
- **K-Nearest Neighbor (KNN)**: selecciona ejemplos similares al caso actual.
- **Vote-K**: preserva diversidad mientras se eligen ejemplos parecidos.
- **Self-Generated In-Context Learning (SG-ICL)**: genera ejemplos automáticamente.
- **Prompt Mining**: descubre formulaciones intermedias óptimas a partir de corpus.
- **LENS**: aplica filtrado iterativo para refinar ejemplos.
- **UDR**: combina embeddings y recuperación.
- **Active Example Selection**: usa refuerzo para escoger ejemplos.

### 1.2 Zero-Shot Prompting
- **Role Prompting**: asigna un rol o persona al modelo.
- **Style Prompting**: controla estilo, tono o género del resultado.
- **Emotion Prompting**: incorpora frases con carga emocional.
- **System 2 Attention (S2A)**: elimina información irrelevante del prompt.
- **SimToM**: restringe el conocimiento usado por el modelo.
- **Rephrase and Respond (RaR)**: obliga a reformular y luego responder.
- **Re-reading (RE2)**: añade instrucciones para releer la pregunta.
- **Self-Ask**: decide si es necesario pedir información adicional.

## 2. Técnicas de Generación de Pensamientos

### 2.1 Chain-of-Thought (CoT)
- **Chain-of-Thought Prompting**: fomenta la explicitación del razonamiento paso a paso.

### 2.2 Zero-Shot CoT
- **Zero-Shot Chain-of-Thought**: CoT sin ejemplos.
- **Step-Back Prompting**: primero formula una pregunta de alto nivel.
- **Analogical Prompting**: genera ejemplos análogos con cadenas de pensamiento.
- **Thread-of-Thought (ThoT)**: mejora el inductor de pensamiento para CoT.
- **Tabular Chain-of-Thought (Tab-CoT)**: representa razonamiento en tablas Markdown.

### 2.3 Few-Shot CoT
- **Contrastive CoT Prompting**: combina explicaciones correctas e incorrectas.
- **Uncertainty-Routed CoT**: muestrea múltiples rutas de razonamiento.
- **Complexity-based Prompting**: usa ejemplos complejos como entrenamiento.
- **Active Prompting**: solicita a humanos reescribir ejemplos inciertos.
- **Memory-of-Thought**: reutiliza datos no etiquetados.
- **Automatic Chain-of-Thought (Auto-CoT)**: genera cadenas de pensamiento automáticamente.

## 3. Técnicas de Descomposición

- **Least-to-Most Prompting**: divide un problema en subproblemas.
- **Decomposed Prompting (DECOMP)**: muestra cómo usar funciones específicas.
- **Plan-and-Solve Prompting**: versión mejorada de Zero-Shot CoT.
- **Tree-of-Thought (ToT)**: explora soluciones como un árbol.
- **Recursion-of-Thought**: delega subproblemas complejos a otros prompts.
- **Program-of-Thoughts**: traduce el problema a código ejecutable.
- **Faithful Chain-of-Thought**: mezcla razonamiento natural con símbolos.
- **Skeleton-of-Thought**: acelera mediante paralelización.
- **Metacognitive Prompting**: simula procesos metacognitivos humanos.

## 4. Técnicas de Ensembling

- **Demonstration Ensembling (DENSE)**: crea múltiples prompts few-shot.
- **Mixture of Reasoning Experts (MoRE)**: agrupa expertos de razonamiento diversos.
- **Max Mutual Information Method**: combina plantillas y ejemplos variados.
- **Self-Consistency**: genera varias rutas y escoge la respuesta coherente.
- **Universal Self-Consistency**: usa prompting para elegir la respuesta mayoritaria.
- **Meta-Reasoning over Multiple CoTs**: agrega múltiples cadenas de razonamiento.
- **DiVeRSe**: produce varios prompts para el mismo problema.
- **Consistency-based Self-adaptive Prompting (COSP)**: genera prompts Few-Shot CoT.
- **Universal Self-Adaptive Prompting (USP)**: generaliza COSP.
- **Prompt Paraphrasing**: reescribe el prompt original para variar formulaciones.

## 5. Técnicas de Auto-Crítica

- **Self-Calibration**: pregunta al modelo si su respuesta es correcta.
- **Self-Refine**: itera respuesta y retroalimentación.
- **Reversing Chain-of-Thought (RCoT)**: reconstruye el problema desde la respuesta.
- **Self-Verification**: genera múltiples soluciones candidatas.
- **Chain-of-Verification (COVE)**: crea preguntas de verificación.
- **Cumulative Reasoning**: acumula pasos potenciales antes de resolver.

## 6. Técnicas Multilingües

### 6.1 Prompting General Multilingüe
- **Translate First Prompting**: traduce primero al inglés.

### 6.2 Chain-of-Thought Multilingüe
- **XLT (Cross-Lingual Thought) Prompting**: seis instrucciones coordinadas.
- **Cross-Lingual Self Consistent Prompting (CLSP)**: ensemble multilingüe.

### 6.3 In-Context Learning Multilingüe
- **X-InSTA Prompting**: alinea ejemplos en contexto.
- **In-CLT (Cross-lingual Transfer) Prompting**: usa idioma fuente y destino.

### 6.4 Selección de Ejemplos en Contexto
- **PARC**: recupera ejemplos desde un idioma de alto recurso.
- **Semantically-Aligned Examples**: elige ejemplos cercanos semánticamente.
- **Semantically-Distant Examples**: usa ejemplos disímiles para robustez.

### 6.5 Traducción Automática
- **Multi-Aspect Prompting and Selection (MAPS)**: imita traducción humana.
- **Chain-of-Dictionary (CoD)**: lista significados de palabras clave.
- **Dictionary-based Prompting for MT (DiPMT)**: enfoque basado en diccionarios.
- **Decomposed Prompting for MT (DecoMT)**: divide el texto en fragmentos.
- **Interactive-Chain-Prompting (ICP)**: maneja ambigüedades mediante diálogo.
- **Iterative Prompting**: involucra humanos durante la traducción.

## 7. Técnicas Multimodales

### 7.1 Prompting de Imágenes
- **Prompt Modifiers**: modificadores que alteran la imagen generada.
- **Negative Prompting**: pondera términos a evitar.
- **Paired-Image Prompting**: compara imágenes antes/después.
- **Image-as-Text Prompting**: describe una imagen como texto.
- **Duty Distinct Chain-of-Thought (DDCoT)**: extiende Least-to-Most a entornos multimodales.
- **Multimodal Graph-of-Thought**: extiende Graph-of-Thought.
- **Chain-of-Images (CoI)**: cadena de pensamiento en imágenes.

### 7.2 Otras Modalidades
- **Audio Prompting**: técnicas aplicadas a audio.
- **Video Prompting**: prompting para video.
- **Segmentation Prompting**: segmentación guiada por prompt.
- **3D Prompting**: prompting para entornos tridimensionales.

## 8. Técnicas de Agentes

### 8.1 Agentes de Uso de Herramientas
- **MRKL System**: integración modular de razonamiento y herramientas.
- **Self-Correcting with Tool-Interactive Critiquing (CRITIC)**: usa herramientas para auto-corregirse.

### 8.2 Agentes de Generación de Código
- **Program-aided Language Model (PAL)**: traduce a código.
- **Tool-Integrated Reasoning Agent (ToRA)**: alterna razonamiento y código.
- **TaskWeaver**: usa plugins definidos por el usuario.

### 8.3 Agentes Basados en Observación
- **Reasoning and Acting (ReAct)**: combina pensamiento, acción y observación.
- **Reflexion**: añade introspección al patrón ReAct.
- **Voyager**: aprendizaje continuo con tres componentes.
- **Ghost in the Minecraft (GITM)**: descompone objetivos en subobjetivos.

### 8.4 Generación Aumentada por Recuperación (RAG)
- **Verify-and-Edit**: mejora la consistencia generando múltiples CoTs.
- **Demonstrate-Search-Predict**: descompone en subpreguntas.
- **Interleaved Retrieval guided by Chain-of-Thought (IRCoT)**: recupera información en múltiples pasos.
- **Iterative Retrieval Augmentation**: realiza recuperación iterativa.

## 9. Técnicas de Evaluación

### 9.1 Prompting para Evaluación
- **In-Context Learning para Evaluación**: usa ejemplos para evaluar.
- **Role-based Evaluation**: roles distintos para ampliar cobertura.
- **Chain-of-Thought para Evaluación**: mejora la calidad evaluativa.
- **Model-Generated Guidelines**: el modelo genera pautas de evaluación.

### 9.2 Formatos de Salida
- **Binary Score**: respuesta binaria.
- **Linear Scale**: escala lineal simple.
- **Likert Scale**: escala Likert.
- **Styling**: salidas formateadas (XML, JSON, etc.).

### 9.3 Marcos de Prompting
- **LLM-EVAL**: marco básico de evaluación.
- **G-EVAL**: incorpora Auto-CoT en la evaluación.
- **ChatEval**: usa debate multi-agente.

### 9.4 Otras Metodologías
- **Batch Prompting**: evalúa múltiples instancias a la vez.
- **Pairwise Evaluation**: compara dos respuestas directamente.

## 10. Técnicas de Ingeniería de Prompts

- **Meta Prompting**: el modelo mejora el prompt.
- **AutoPrompt**: usa tokens disparadores en un LLM congelado.
- **Automatic Prompt Engineer (APE)**: genera prompts zero-shot.
- **Gradientfree Instructional Prompt Search (GrIPS)**: busca prompts sin gradientes.
- **Prompt Optimization with Textual Gradients (ProTeGi)**: optimiza con gradientes textuales.
- **RLPrompt**: agrega un módulo de refuerzo.
- **Dialogue-comprised Policy-gradient-based Discrete Prompt Optimization (DP2O)**: optimización avanzada basada en diálogos.

## 11. Ingeniería de Respuestas

### 11.1 Componentes
- **Answer Shape**: formato de la respuesta.
- **Answer Space**: dominio de valores permitidos.
- **Answer Extractor**: regla para extraer la respuesta final.

### 11.2 Técnicas
- **Verbalizer**: asigna tokens a etiquetas.
- **Regex**: usa expresiones regulares para extraer respuestas.
- **Separate LLM**: un modelo evalúa la salida de otro.

## 12. Técnicas Especializadas por Dominio

### 12.1 Seguridad
- **Prompt-based Defenses**: instrucciones defensivas explícitas.
- **Detectors**: detectores de entradas maliciosas.
- **Guardrails**: reglas para guiar la salida.

### 12.2 Alineación
- **Vanilla Prompting**: instrucción imparcial.
- **Selecting Balanced Demonstrations**: equilibra ejemplos según métricas de equidad.
- **Cultural Awareness**: adapta culturalmente las respuestas.
- **AttrPrompt**: reduce sesgos en texto generado.
- **Ambiguous Demonstrations**: usa ejemplos con etiquetas ambiguas.
- **Question Clarification**: identifica preguntas ambiguas.

### 12.3 Calibración
- **Verbalized Score**: genera puntuación de confianza.
- **Sycophancy**: considera tendencia a complacer al usuario.

## Notas Importantes

- Las técnicas pueden combinarse para mejorar resultados.
- La efectividad depende del modelo (Claude, ChatGPT, Hugging Face), la tarea y el contexto.
- Algunas técnicas requieren ajustes específicos por dominio (API, UI, Infrastructure, Docs, Scripts).
- La investigación evoluciona rápidamente; validar empíricamente antes de estandarizar.
- Registrar hallazgos y variantes en `docs/ai/SDLC_AGENTS_GUIDE.md` cuando se descubran nuevas combinaciones.
