---
title: Fine-tuning de TinyLlama con QLoRA + DPO
date: 2025-11-13
domain: ai
status: active
---

# Fine-tuning de TinyLlama con QLoRA + DPO

Esta guía resume el cuaderno de referencia **Chapter 12 - Fine-tuning Generation Models** para
acoplar un modelo TinyLlama entrenado localmente dentro del ecosistema de agentes SDLC.

Se cubre un flujo en dos etapas:

1. **Supervised Fine-Tuning (SFT)** utilizando QLoRA en precisión de 4 bits.
2. **Preference Optimization (DPO)** para alinear el modelo con respuestas preferidas.

El resultado final se integra mediante el nuevo `llm_provider="huggingface"` que expone el
checkpoint directamente a `LLMGenerator` y al resto de agentes.

---

## 1. Preparar el entorno

Requisitos mínimos:

- GPU con soporte CUDA (T4 o superior) o entornos equivalentes (AWS g5, GCP A2, etc.).
- Drivers y `nvidia-smi` operativos.
- Python 3.10+.

Instalar dependencias clave (coinciden con el notebook de referencia):

```bash
pip install \
  accelerate==0.31.0 \
  bitsandbytes==0.43.1 \
  peft==0.11.1 \
  transformers==4.41.2 \
  trl==0.9.4 \
  sentencepiece==0.2.0 \
  triton==3.1.0
```

> **Sugerencia:** en Google Colab seleccionar `Runtime > Change runtime type > GPU > T4`.

Opcionalmente configurar `HF_TOKEN` si se descargan modelos privados.

---

## 2. Preprocesar datos (UltraChat 200k)

```python
from transformers import AutoTokenizer
from datasets import load_dataset

template_tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

def format_prompt(example):
    chat = example["messages"]
    prompt = template_tokenizer.apply_chat_template(chat, tokenize=False)
    return {"text": prompt}

dataset = (
    load_dataset("HuggingFaceH4/ultrachat_200k", split="test_sft")
    .shuffle(seed=42)
    .select(range(3_000))
)
dataset = dataset.map(format_prompt)
```

Se emplea la plantilla de TinyLlama para mantener coherencia de tokens y roles
(`<|user|>`, `<|assistant|>`). Esta estructura es la misma que consumen los
agentes cuando utilizan el proveedor `huggingface`.

---

## 3. Cargar TinyLlama con cuantización 4-bit

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_name = "TinyLlama/TinyLlama-1.1B-intermediate-step-1431k-3T"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    quantization_config=bnb_config,
)
model.config.use_cache = False
model.config.pretraining_tp = 1

tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = "<PAD>"
tokenizer.padding_side = "left"
```

La cuantización de 4 bits reduce memoria y permite entrenar modelos de 1B
parámetros en una sola GPU T4.

---

## 4. Configurar QLoRA

```python
from peft import LoraConfig, prepare_model_for_kbit_training, get_peft_model

peft_config = LoraConfig(
    lora_alpha=32,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=['k_proj','gate_proj','v_proj','up_proj','q_proj','o_proj','down_proj']
)

model = prepare_model_for_kbit_training(model)
model = get_peft_model(model, peft_config)
```

---

## 5. Entrenar con `SFTTrainer`

```python
from transformers import TrainingArguments
from trl import SFTTrainer

training_arguments = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    optim="paged_adamw_32bit",
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    num_train_epochs=1,
    logging_steps=10,
    fp16=True,
    gradient_checkpointing=True
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    tokenizer=tokenizer,
    args=training_arguments,
    max_seq_length=512,
    peft_config=peft_config,
)

trainer.train()
trainer.model.save_pretrained("TinyLlama-1.1B-qlora")
```

Se guardan los pesos LoRA en `TinyLlama-1.1B-qlora/`.

---

## 6. Mezclar adaptadores

```python
from peft import AutoPeftModelForCausalLM

model = AutoPeftModelForCausalLM.from_pretrained(
    "TinyLlama-1.1B-qlora",
    low_cpu_mem_usage=True,
    device_map="auto",
)
merged_model = model.merge_and_unload()
```

Este merge produce un checkpoint listo para inferencia SFT (`merged_model`).

---

## 7. Ajuste por preferencias (DPO)

1. Formatear dataset DPO (`argilla/distilabel-intel-orca-dpo-pairs`) usando la misma
   plantilla TinyLlama (`<|system|>`, `<|user|>`, `<|assistant|>`).
2. Cargar el modelo SFT cuantizado.
3. Aplicar LoRA con la misma configuración.
4. Entrenar con `DPOTrainer`:

```python
from trl import DPOTrainer, DPOConfig

training_arguments = DPOConfig(
    output_dir="./results",
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    optim="paged_adamw_32bit",
    learning_rate=1e-5,
    lr_scheduler_type="cosine",
    max_steps=200,
    logging_steps=10,
    fp16=True,
    gradient_checkpointing=True,
    warmup_ratio=0.1
)

dpo_trainer = DPOTrainer(
    model,
    args=training_arguments,
    train_dataset=dpo_dataset,
    tokenizer=tokenizer,
    peft_config=peft_config,
    beta=0.1,
    max_prompt_length=512,
    max_length=512,
)

dpo_trainer.train()
dpo_trainer.model.save_pretrained("TinyLlama-1.1B-dpo-qlora")
```

5. Unir los adaptadores SFT + DPO y generar el checkpoint final para inferencia.

---

## 8. Inferencia

```python
from transformers import pipeline

prompt = """<|user|>\nTell me something about Large Language Models.</s>\n<|assistant|>\n"""

pipe = pipeline(
    task="text-generation",
    model="/ruta/al/checkpoint/dpo_merge",
    tokenizer=tokenizer,
)
print(pipe(prompt, max_new_tokens=256, temperature=0.2)[0]["generated_text"])
```

---

## 9. Integrar con el proveedor `huggingface`

1. Guardar el checkpoint final (por ejemplo `TinyLlama-1.1B-dpo-merged`).
2. Actualizar `.env`:

```bash
PREFER_LLM_PROVIDER=huggingface
HF_LOCAL_MODEL_PATH=/models/TinyLlama-1.1B-dpo-merged
HF_GENERATE_KWARGS={"max_new_tokens":512,"temperature":0.2}
```

3. Configurar los agentes con:

```python
config = {
    "llm_provider": "huggingface",
    "model": "/models/TinyLlama-1.1B-dpo-merged",
    "hf_generate_kwargs": {"max_new_tokens": 512, "temperature": 0.2},
    "use_llm": True
}
```

Los tests unitarios (`test_llm_generator.py`) verifican que el generador de
pruebas consuma Hugging Face mediante el nuevo método `_call_huggingface`.

---

## 10. Buenas prácticas

- Versionar únicamente los adaptadores (`TinyLlama-1.1B-qlora`, `TinyLlama-1.1B-dpo-qlora`)
  y almacenar el merge final en artefactos (por peso).
- Registrar métricas clave: pérdida SFT, recompensa DPO, evaluación manual.
- Mantener una GPU dedicada para entrenamiento; la inferencia puede ejecutarse en CPU
  con menor throughput.
- Documentar cualquier cambio en hiperparámetros dentro de `docs/ai/FINE_TUNING_TINYLLAMA.md`.

---

Con estos pasos se habilita un tercer modelo especializado que complementa
las integraciones existentes (Claude y GPT). El `llm_provider="huggingface"`
permite reutilizar directamente los checkpoints fine-tuned en los agentes SDLC,
manteniendo trazabilidad completa desde el dataset hasta la inferencia.
