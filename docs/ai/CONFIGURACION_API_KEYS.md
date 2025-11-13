# Configuración de API Keys para Agentes SDLC

Guía completa para configurar API keys de forma segura.

---

## Seguridad: NUNCA Guardes API Keys en el Repositorio

Las API keys son credenciales sensibles que dan acceso a tu cuenta de Anthropic/OpenAI. Si las commiteas al repositorio:

- Cualquiera con acceso al repo puede usarlas
- Pueden aparecer en GitHub/GitLab público
- Te pueden cobrar por uso no autorizado
- Es una violación de seguridad grave

**Solución:** Usar archivo `.env` que está en `.gitignore`

---

## Configuración Paso a Paso

### 1. Copiar el Template

```bash
cd /home/user/IACT---project
cp .env.example .env
```

### 2. Editar .env con tus API Keys

```bash
# Opción A: Usar editor
nano .env

# Opción B: Usar sed (reemplazar YOUR_KEY_HERE)
sed -i 's/sk-ant-api03-YOUR_KEY_HERE/sk-ant-api03-TU_KEY_REAL/' .env
```

Contenido de `.env`:

```bash
# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-c483Z3nf9T-qJU5UFWmEcEZ...

# OpenAI GPT (opcional)
OPENAI_API_KEY=sk-...

# Ollama (local, opcional)
OLLAMA_BASE_URL=http://localhost:11434

# Hugging Face (modelos locales fine-tuned, opcional)
HF_LOCAL_MODEL_PATH=/models/TinyLlama-1.1B-qlora
# HF_MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0
# HF_GENERATE_KWARGS={"max_new_tokens":512,"temperature":0.2}

# Presupuesto mensual en USD
LLM_MONTHLY_BUDGET=100

# Habilitar optimización
ENABLE_COST_OPTIMIZATION=true

# Proveedor preferido: "auto", "anthropic", "openai", "ollama", "huggingface"
PREFER_LLM_PROVIDER=auto
```

### 3. Verificar Configuración

```bash
python3 scripts/ai/shared/env_loader.py
```

Deberías ver:

```
======================================================================
VERIFICACION DE CONFIGURACION LLM
======================================================================

[OK] ANTHROPIC_API_KEY: sk-ant-api03-c4...tQAA
[  ] OPENAI_API_KEY: No configurada
[OK] OLLAMA_BASE_URL: http://localhost:11434

----------------------------------------------------------------------
Config Auto-Detectada: anthropic (claude-3-5-sonnet-20241022)
======================================================================
```

### 4. Probar con un Agente

```bash
python3 test_case1_viabilidad.py
```

Si funciona correctamente, verás análisis generado por Claude.

---

## Opciones de Configuración

### Opción 1: Solo Anthropic Claude (Recomendado)

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...
PREFER_LLM_PROVIDER=anthropic
```

**Ventajas:**
- Mejor calidad para análisis de código
- Precio competitivo ($0.018/1K tokens)
- Respuestas más precisas

### Opción 2: Solo OpenAI GPT

```bash
# .env
OPENAI_API_KEY=sk-...
PREFER_LLM_PROVIDER=openai
```

**Ventajas:**
- GPT-4o tiene buen precio/calidad ($0.010/1K tokens)
- Bien documentado
- Ampliamente usado

### Opción 3: Ambos Proveedores (Híbrido)

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
PREFER_LLM_PROVIDER=auto
```

**Ventajas:**
- Fallback automático si uno falla
- Usa el mejor modelo según tarea
- Claude para features complejas, GPT-4o para medias

### Opción 4: Solo Ollama (Local, Gratis)

```bash
# .env
OLLAMA_BASE_URL=http://localhost:11434
PREFER_LLM_PROVIDER=ollama
```

**Ventajas:**
- 100% gratis
- Privacidad total (no envía datos a cloud)
- Sin límites de uso

**Desventajas:**
- Requiere hardware potente (16GB+ RAM)
- Más lento que APIs cloud
- Calidad variable según modelo

### Opción 5: Hugging Face (Modelos Fine-Tuned)

```bash
# .env
HF_LOCAL_MODEL_PATH=/models/TinyLlama-1.1B-qlora
PREFER_LLM_PROVIDER=huggingface
```

**Ventajas:**
- Ejecuta modelos entrenados específicamente para el dominio
- No requiere enviar datos a proveedores externos si el modelo es local
- Permite integrar pipelines como TinyLlama QLoRA + DPO (ver guía de fine-tuning)

**Desventajas:**
- Necesitas descargar el modelo (~4GB+) y dependencias de `transformers`
- Performance depende del hardware disponible (GPU recomendada)
- Debes gestionar actualizaciones y almacenamiento de checkpoints manualmente

### Opción 6: Sin LLM (Solo Heurísticas)

```bash
# .env
# No configurar ninguna API key
```

**Ventajas:**
- Instantáneo (<0.1s)
- Sin costo
- Predecible y reproducible

**Desventajas:**
- Análisis más básico
- No detecta edge cases sutiles

---

## Uso en Código

### Automático (Recomendado)

Los agentes cargan automáticamente desde `.env`:

```python
from scripts.ai.shared.env_loader import get_llm_config_from_env
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

# Config automática desde .env
config = get_llm_config_from_env()

# Usar con agente
agent = SDLCFeasibilityAgent(config=config)
result = agent.run({"issue": {...}})
```

### Manual

Si prefieres control total:

```python
config = {
    "llm_provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "use_llm": True
}

agent = SDLCFeasibilityAgent(config=config)
```

### Con Optimización de Costos

```python
from scripts.ai.shared.llm_cost_optimizer import get_optimizer

optimizer = get_optimizer()

# Selecciona automáticamente el mejor modelo según complejidad
config = optimizer.get_optimal_config(
    issue={"estimated_story_points": 8, "labels": ["security"]},
    prefer_provider="auto"  # usa el de .env
)

agent = SDLCFeasibilityAgent(config=config)
```

---

## Verificar que .env NO está en Git

```bash
# Esto NO debe mostrar .env
git status

# Verificar que .env está ignorado
git check-ignore .env
# Debe mostrar: .env
```

Si `.env` aparece en `git status`, agregalo al `.gitignore`:

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: ensure .env is ignored"
```

---

## Variables de Entorno Disponibles

| Variable | Valores | Default | Descripción |
|----------|---------|---------|-------------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | - | API key de Claude |
| `OPENAI_API_KEY` | `sk-...` | - | API key de GPT |
| `OLLAMA_BASE_URL` | URL | `http://localhost:11434` | URL de Ollama local |
| `LLM_MONTHLY_BUDGET` | Número | `100` | Presupuesto mensual USD |
| `ENABLE_COST_OPTIMIZATION` | `true`/`false` | `false` | Habilitar optimización |
| `PREFER_LLM_PROVIDER` | `auto`/`anthropic`/`openai`/`ollama` | `auto` | Proveedor preferido |
| `ENVIRONMENT` | `development`/`staging`/`production` | `development` | Entorno |

---

## Troubleshooting

### Error: "API key not found"

```bash
# Verificar que .env existe
ls -la .env

# Verificar contenido (sin mostrar keys completas)
grep ANTHROPIC_API_KEY .env | head -c 50

# Recargar variables
source .env  # Bash
python3 scripts/ai/shared/env_loader.py  # Python
```

### Error: "Invalid API key"

La API key puede estar mal copiada. Verificar:
- No tiene espacios al inicio/final
- Empieza con `sk-ant-api03-` (Claude) o `sk-` (OpenAI)
- No tiene comillas adicionales

### Error: "Permission denied"

```bash
chmod 600 .env  # Solo tu usuario puede leerlo
```

### .env aparece en git status

```bash
# Remover del staging
git rm --cached .env

# Asegurar que esté en .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: ignore .env file"
```

---

## Mejores Prácticas

1. **NUNCA** commitees `.env` al repositorio
2. **SIEMPRE** usa `.env.example` como template (sin keys reales)
3. **Rota** tus API keys periódicamente (cada 3-6 meses)
4. **Limita** permisos del archivo: `chmod 600 .env`
5. **Monitorea** uso en dashboard de Anthropic/OpenAI
6. **Configura** alertas de presupuesto
7. **Usa** Ollama en desarrollo para ahorrar costos

---

## Obtener API Keys

### Anthropic Claude

1. Ir a: https://console.anthropic.com/
2. Crear cuenta o login
3. Settings → API Keys
4. Create Key
5. Copiar key (se muestra solo una vez)
6. Pegar en `.env`

**Costo:** $5 crédito gratis, luego pago por uso

### OpenAI GPT

1. Ir a: https://platform.openai.com/
2. Crear cuenta o login
3. API Keys → Create new secret key
4. Copiar key (se muestra solo una vez)
5. Pegar en `.env`

**Costo:** $5 crédito gratis (nuevo usuario), luego pago por uso

### Ollama (Gratis)

```bash
# Instalar
curl -fsSL https://ollama.com/install.sh | sh

# Iniciar servidor
ollama serve

# Descargar modelo
ollama pull qwen2.5-coder:32b

# No requiere API key
```

---

## Monitoreo de Costos

### Dashboard de Anthropic

https://console.anthropic.com/settings/usage

### Dashboard de OpenAI

https://platform.openai.com/usage

### Script Local

```bash
# Ver uso desde optimizer
cat metrics/llm_spending.json

# Ver métricas detalladas
cat metrics/llm_usage.json | tail -20
```

---

**Última actualización:** 2025-11-12
**Autor:** Sistema SDLC IACT
