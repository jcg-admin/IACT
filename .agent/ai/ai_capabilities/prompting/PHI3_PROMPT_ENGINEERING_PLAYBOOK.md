# Prompt Engineering con Phi-3 Mini

Guía de integración para aprovechar el notebook de referencia **Chapter 6 - Prompt Engineering**
utilizando el modelo `microsoft/Phi-3-mini-4k-instruct`. Complementa las capacidades actuales
del proyecto (Claude + ChatGPT + modelos Hugging Face) con un flujo reproducible para
experimentar localmente con Phi-3, sin perder alineación con los agentes SDLC.

---

## 1. Preparación del entorno

- **Hardware recomendado:** GPU con 16 GB (T4, RTX 4090, etc.) o CPU x86_64 con AVX2.
- **Dependencias base:**

```bash
pip install \
  langchain>=0.1.17 \
  openai>=1.13.3 \
  langchain_openai>=0.1.6 \
  transformers>=4.40.1 \
  datasets>=2.18.0 \
  accelerate>=0.27.2 \
  sentence-transformers>=2.5.1 \
  duckduckgo-search>=5.2.2

CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python
```

- **Credenciales:** no se requieren API keys para descargar Phi-3 desde Hugging Face, pero es
  recomendable configurar `HF_TOKEN` si se accede a repositorios privados.
- **GPU en Colab:** `Runtime > Change runtime type > Hardware accelerator > GPU > T4`.

El ecosistema del proyecto seguirá prefiriendo `PREFER_LLM_PROVIDER=auto`, pero al declarar
`PREFER_LLM_PROVIDER=huggingface` + `HF_MODEL_ID=microsoft/Phi-3-mini-4k-instruct`, el
`LLMGenerator` cargará este modelo para escenarios offline o de laboratorio.

---

## 2. Carga del modelo

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_name = "microsoft/Phi-3-mini-4k-instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cuda",          # usar "auto" en CPU o multi-GPU
    torch_dtype="auto",
    trust_remote_code=False,
)

tokenizer = AutoTokenizer.from_pretrained(model_name)

pipe = pipeline(
    task="text-generation",
    model=model,
    tokenizer=tokenizer,
    return_full_text=False,
    max_new_tokens=500,
    do_sample=False,
)
```

- `return_full_text=False` mantiene la salida sin duplicar el prompt.
- `max_new_tokens` controla el tamaño de la respuesta; ajústalo según presupuesto de tokens.
- El pipeline puede moverse a CPU fijando `device_map="cpu"` con la penalización de latencia
  esperada.

---

## 3. Plantilla de chat de Phi-3

```python
messages = [
    {"role": "user", "content": "Create a funny joke about chickens."}
]

prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False)
print(prompt)
# <s><|user|>\nCreate a funny joke about chickens.<|end|>\n<|assistant|>\n
```

- Phi-3 usa delimitadores `<|user|>`, `<|assistant|>`, `<|end|>` y un prefijo `<s>`.
- Respetar la plantilla evita desalineaciones cuando se alterna entre Claude / ChatGPT /
  Hugging Face en los agentes multi-modelo.

---

## 4. Control de temperatura y Top-p

```python
pipe(messages, do_sample=True, temperature=1.0)
pipe(messages, do_sample=True, top_p=1.0)
```

- `temperature` alto aumenta diversidad; `top_p` regula la probabilidad acumulada.
- Para reproducibilidad en validaciones automáticas se recomienda `do_sample=False`,
  `temperature=0` y `top_p=0.9` o inferior.

---

## 5. Componentes clave del prompt

```python
persona = "You are an expert in Large Language Models...\n"
instruction = "Summarize the key findings...\n"
context = "Your summary should extract the most crucial points...\n"
formatting = "Create a bullet-point summary...\n"
audience = "The summary is designed for busy researchers...\n"
tone = "The tone should be professional and clear.\n"

query = persona + instruction + context + formatting + audience + tone
messages = [{"role": "user", "content": query}]
```

- Mantener cada capa (persona, instrucción, contexto, formato, audiencia, tono) permite que el
  agente `PromptTemplateEngine` combine fragmentos reutilizables.
- Documentar estos bloques facilita portar el prompt entre Claude (Anthropic), GPT-4o (OpenAI)
  y Phi-3 (Hugging Face) sin pérdida de intención.

---

## 6. Patrones de prompting cubiertos

| Técnica | Ejemplo Phi-3 | Uso recomendado |
| --- | --- | --- |
| **Zero-shot** | Pedir resumen directo | Consultas rápidas |
| **One-shot** | Proveer una muestra de JSON | Uniformar formato |
| **Few-shot** | Varias instrucciones/respuestas | Calibrar estilo |
| **In-context learning** | Palabras inventadas (Gigamuru, screeg) | Sintaxis específicas |
| **Chain-of-thought (CoT)** | Resolver aritmética paso a paso | QA y debugging |
| **Zero-shot CoT** | Añadir `Let's think step-by-step` | Preguntas de control |
| **Tree-of-thought (ToT)** | Simular expertos colaborativos | Evaluaciones complejas |
| **Chain prompting** | Nombre → Pitch | Copywriting multi-etapa |
| **Output verification** | JSON válido con `response_format` | Validadores automáticos |
| **Grammar constraints** | `llama_cpp` con `response_format={"type": "json_object"}` | Forzar esquemas |

Cada técnica puede orquestarse desde los agentes existentes:

- `PromptChaining` (scripts/ai/agents/base/structuring_techniques.py).
- `TreeOfThoughtsAgent` y `SelfConsistencyAgent` para razonamiento.
- `HybridSearchOptimization` para seleccionar prompts según dominio.

---

## 7. Integración con los 3 proveedores

| Proveedor | Variable `.env` | Caso de uso |
| --- | --- | --- |
| **Anthropic (Claude)** | `ANTHROPIC_API_KEY` | Análisis críticos, refactors |
| **OpenAI (ChatGPT)** | `OPENAI_API_KEY` | Tutores interactivos, QA |
| **Hugging Face (Phi-3/TinyLlama)** | `HF_MODEL_ID` o `HF_LOCAL_MODEL_PATH` | Laboratorios, entornos aislados |

- El `EnvLoader` ya detecta automáticamente el proveedor activo; esta guía describe cómo
  provisionar Phi-3 para cubrir el tercer pilar documentado en el README.
- Para notebooks experimentales puede usarse `llama_cpp` con el checkpoint GGUF publicado
  por Microsoft (`microsoft/Phi-3-mini-4k-instruct-gguf`).

---

## 8. Buenas prácticas operativas

1. **Reutiliza plantillas:** centraliza las piezas del prompt en `PromptTemplateEngine` y evita
   duplicación de cadenas literales.
2. **Versiona ejemplos:** guarda las variaciones de few-shot en el repositorio para comparar
   resultados entre LLMs.
3. **Evalúa regresiones:** usa `SelfConsistencyAgent` con 3 rutas (Claude, GPT, Phi-3) y
   compara convergencia ≥ 0.85 antes de promover prompts a producción.
4. **Controla costos:** en entornos cloud prioriza Claude/GPT solo cuando Phi-3 no alcanza el
   criterio de calidad definido.
5. **Valida outputs:** mantén pruebas de `docs/testing/test_documentation_alignment.py` para
   asegurar que los manuales y scripts estén sincronizados.

---

## 9. Referencias adicionales

- Notebook original: *Hands-On Large Language Models – Chapter 6: Prompt Engineering*.
- Documentación oficial de Phi-3: [https://huggingface.co/microsoft/Phi-3-mini-4k-instruct](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct)
- Guía de agentes multi-LLM: [`docs/ai/SDLC_AGENTS_GUIDE.md`](../SDLC_AGENTS_GUIDE.md)
- Playbook de fine-tuning TinyLlama (para comparar flujos): [`../FINE_TUNING_TINYLLAMA.md`](../FINE_TUNING_TINYLLAMA.md)

Esta guía asegura que el tercer modelo documentado (Phi-3) cuente con un playbook oficial y
alineado a las prácticas de prompting del proyecto.
