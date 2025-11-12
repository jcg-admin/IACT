# Estrategia de Optimización de Créditos LLM

Análisis y recomendaciones para uso eficiente de créditos Claude/OpenAI en producción.

---

## Análisis de Costos Actuales

### Precios Claude (Enero 2025)

**Claude 3.5 Sonnet:**
- Input: $3 / 1M tokens (~$0.003 por 1K tokens)
- Output: $15 / 1M tokens (~$0.015 por 1K tokens)

**Ejemplo de costos por operación:**

| Operación | Input Tokens | Output Tokens | Costo |
|-----------|-------------|---------------|-------|
| Feasibility Analysis | ~1,500 | ~500 | $0.012 |
| Design (HLD/LLD) | ~2,000 | ~1,500 | $0.028 |
| Test Strategy | ~1,800 | ~800 | $0.017 |
| Deployment Plan | ~1,500 | ~600 | $0.013 |
| **Pipeline Completo** | ~6,800 | ~3,400 | **$0.071** |

**Uso intensivo estimado:**
- 100 features/mes = $7.10
- 500 features/mes = $35.50
- 1000 features/mes = $71.00

---

## ESTRATEGIA RECOMENDADA: Híbrida Inteligente

### Nivel 1: Heurísticas por Defecto (Gratis)

**Cuándo usar:**
- Features simples (≤3 story points)
- Evaluaciones rápidas
- Decisiones GO/NO-GO obvias
- Desarrollo/testing

**Ahorro:** 90% de llamadas LLM

```python
# Por defecto, sin LLM
agent = SDLCFeasibilityAgent(config=None)
```

**Casos de uso:**
- "Add dark mode toggle" (2 SP) → Heurística suficiente
- "Fix typo in button" (1 SP) → Heurística suficiente
- "Update CSS padding" (1 SP) → Heurística suficiente

---

### Nivel 2: LLM Selectivo (Inteligente)

**Cuándo usar LLM:**
- Features complejas (≥8 story points)
- Alta criticidad (security, payments, auth)
- Decisiones ambiguas
- Arquitectura nueva

**Implementación con lógica de decisión:**

```python
def get_llm_config(issue):
    """Decide si usar LLM basado en complejidad y criticidad."""

    story_points = issue.get('estimated_story_points', 0)
    labels = issue.get('labels', [])

    # Criterios para usar LLM
    is_complex = story_points >= 8
    is_critical = any(label in labels for label in ['security', 'payment', 'auth'])
    is_architectural = 'architecture' in labels

    if is_complex or is_critical or is_architectural:
        return {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "use_llm": True
        }
    else:
        return None  # Usa heurísticas

# Uso
config = get_llm_config(issue)
agent = SDLCFeasibilityAgent(config=config)
```

**Ahorro estimado:** 70% de llamadas LLM

---

### Nivel 3: Caching Inteligente

**Problema:** Features similares generan prompts similares.

**Solución:** Cache de resultados LLM.

```python
import hashlib
import json
from pathlib import Path

class LLMCache:
    """Cache para resultados de LLM."""

    def __init__(self, cache_dir="cache/llm"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, prompt, model):
        """Genera hash único para prompt."""
        content = f"{prompt}|{model}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt, model):
        """Obtiene resultado cacheado."""
        cache_key = self.get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                # Cache válido por 7 días
                if (time.time() - data['timestamp']) < 7 * 24 * 3600:
                    return data['response']
        return None

    def set(self, prompt, model, response):
        """Guarda resultado en cache."""
        cache_key = self.get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with open(cache_file, 'w') as f:
            json.dump({
                'prompt_hash': cache_key,
                'response': response,
                'timestamp': time.time(),
                'model': model
            }, f)

# Integrar en LLMGenerator
class LLMGenerator(Agent):
    def __init__(self, config=None):
        super().__init__(name="LLMGenerator", config=config)
        self.cache = LLMCache()
        # ...

    def _call_llm(self, prompt):
        # Intentar cache primero
        cached = self.cache.get(prompt, self.model)
        if cached:
            self.logger.info("LLM response from cache (saved $0.012)")
            return cached

        # Llamar LLM
        response = self._call_anthropic(prompt)

        # Guardar en cache
        self.cache.set(prompt, self.model, response)

        return response
```

**Ahorro estimado:** 40-60% en features repetitivas

---

### Nivel 4: Prompt Optimization

**Problema:** Prompts largos = más tokens = más costo.

**Estrategia:**

1. **Comprimir contexto**
```python
# MAL (2000 tokens)
prompt = f"""
Aquí está el código completo:
{entire_codebase}

Genera tests para todo.
"""

# BIEN (500 tokens)
prompt = f"""
Clase: {class_name}
Métodos: {method_names}
Complejidad: {complexity}

Genera tests para métodos críticos.
"""
```

2. **Usar referencias en lugar de duplicación**
```python
# MAL: Enviar HLD completo en cada fase
prompt = f"HLD:\n{hld_document}\n\nGenera LLD..."

# BIEN: Enviar solo resumen
hld_summary = {
    "components": ["API", "Database", "Cache"],
    "patterns": ["Repository", "Factory"],
    "constraints": ["NO Redis", "NO Email"]
}
prompt = f"HLD Summary:\n{json.dumps(hld_summary)}\n\nGenera LLD..."
```

3. **Reutilizar prompts base**
```python
BASE_PROMPT = """Eres experto en arquitectura de software.
Restricciones IACT:
- NO Redis
- NO Email directo
- Solo PostgreSQL
"""

# Reutilizar en cada llamada
full_prompt = BASE_PROMPT + specific_task
```

**Ahorro estimado:** 30% en tokens input

---

### Nivel 5: Modelo Escalonado

**Estrategia:** Usar modelos más baratos cuando sea posible.

```python
def get_model_config(task_complexity):
    """Selecciona modelo según complejidad."""

    if task_complexity == "simple":
        # Claude Haiku (más barato)
        return {
            "model": "claude-3-haiku-20240307",
            "llm_provider": "anthropic"
        }
    elif task_complexity == "medium":
        # Claude Sonnet
        return {
            "model": "claude-3-5-sonnet-20241022",
            "llm_provider": "anthropic"
        }
    else:
        # Claude Opus (más caro, mejor)
        return {
            "model": "claude-3-opus-20240229",
            "llm_provider": "anthropic"
        }

# Uso
config = get_model_config("simple")
agent = SDLCFeasibilityAgent(config=config)
```

**Precios comparativos:**
- Haiku: $0.25/$1.25 por 1M tokens (5x más barato)
- Sonnet: $3/$15 por 1M tokens (baseline)
- Opus: $15/$75 por 1M tokens (5x más caro)

**Ahorro estimado:** 50% usando Haiku para tareas simples

---

### Nivel 6: Ollama para Desarrollo

**Estrategia:** Ollama en desarrollo, Claude en producción.

```python
import os

def get_environment_config():
    """Config según entorno."""

    if os.getenv("ENVIRONMENT") == "production":
        # Claude en producción
        return {
            "llm_provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "use_llm": True
        }
    else:
        # Ollama en desarrollo/staging
        return {
            "llm_provider": "ollama",
            "model": "qwen2.5-coder:32b",
            "use_llm": True
        }

config = get_environment_config()
```

**Ahorro:** 100% en desarrollo/testing

---

## Implementación Completa: Sistema de Decisión

```python
"""
Sistema inteligente de decisión LLM con optimización de costos.
"""
import os
import time
from typing import Dict, Any, Optional

class LLMCostOptimizer:
    """Optimizador de costos para llamadas LLM."""

    def __init__(self):
        self.cache = LLMCache()
        self.monthly_budget = float(os.getenv("LLM_MONTHLY_BUDGET", "100"))
        self.spent_this_month = self._load_spending()

    def should_use_llm(self, issue: Dict[str, Any]) -> bool:
        """Decide si usar LLM basado en múltiples factores."""

        # 1. Verificar presupuesto
        if self.spent_this_month >= self.monthly_budget * 0.95:
            self.logger.warning(f"Budget limit reached: ${self.spent_this_month:.2f}")
            return False

        # 2. Verificar complejidad
        story_points = issue.get('estimated_story_points', 0)
        if story_points < 5:
            return False  # Heurísticas suficientes

        # 3. Verificar criticidad
        labels = issue.get('labels', [])
        critical_labels = ['security', 'payment', 'auth', 'data-loss', 'breaking-change']
        if any(label in critical_labels for label in labels):
            return True  # Siempre LLM para críticos

        # 4. Verificar prioridad
        priority = issue.get('priority', 'medium')
        if priority == 'critical' or priority == 'high':
            return story_points >= 3  # Umbral más bajo para alta prioridad

        # 5. Default: LLM solo para complejos
        return story_points >= 8

    def get_optimal_config(self, issue: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retorna configuración óptima considerando costos."""

        # Verificar entorno
        env = os.getenv("ENVIRONMENT", "development")

        # Desarrollo: Ollama
        if env == "development":
            return {
                "llm_provider": "ollama",
                "model": "qwen2.5-coder:32b",
                "use_llm": True
            }

        # Producción: Decidir si usar LLM
        if not self.should_use_llm(issue):
            return None  # Heurísticas

        # Determinar modelo según complejidad
        story_points = issue.get('estimated_story_points', 0)

        if story_points >= 13:
            # Features muy complejas: Sonnet
            model = "claude-3-5-sonnet-20241022"
        elif story_points >= 8:
            # Features complejas: Sonnet
            model = "claude-3-5-sonnet-20241022"
        else:
            # Features medias: Haiku
            model = "claude-3-haiku-20240307"

        return {
            "llm_provider": "anthropic",
            "model": model,
            "use_llm": True
        }

    def track_usage(self, tokens_used: int, model: str):
        """Trackea uso de tokens y costo."""

        # Calcular costo
        costs = {
            "claude-3-5-sonnet-20241022": 0.003,  # por 1K tokens input
            "claude-3-haiku-20240307": 0.00025,
            "claude-3-opus-20240229": 0.015
        }

        cost_per_1k = costs.get(model, 0.003)
        cost = (tokens_used / 1000) * cost_per_1k

        # Actualizar gasto
        self.spent_this_month += cost
        self._save_spending()

        self.logger.info(f"LLM call: {tokens_used} tokens, ${cost:.4f}")
        self.logger.info(f"Month total: ${self.spent_this_month:.2f} / ${self.monthly_budget}")

    def _load_spending(self) -> float:
        """Carga gasto del mes actual."""
        # Implementar persistencia (Redis, SQLite, etc.)
        return 0.0

    def _save_spending(self):
        """Guarda gasto actualizado."""
        # Implementar persistencia
        pass

# Uso en agentes
class SDLCFeasibilityAgent(SDLCAgent):
    def __init__(self, config=None):
        # Auto-optimización si no se pasa config
        if config is None and os.getenv("ENABLE_COST_OPTIMIZATION") == "true":
            optimizer = LLMCostOptimizer()
            config = optimizer.get_optimal_config(self.current_issue)

        super().__init__(name="SDLCFeasibilityAgent", config=config)
```

---

## Monitoreo y Alertas

```python
"""
Sistema de monitoreo de costos LLM.
"""

class LLMCostMonitor:
    """Monitor de costos con alertas."""

    def __init__(self):
        self.daily_limit = 10.0  # $10/día
        self.today_spent = 0.0
        self.alert_sent = False

    def check_and_alert(self, new_cost: float):
        """Verifica límites y envía alertas."""

        self.today_spent += new_cost

        # Alerta al 80%
        if self.today_spent >= self.daily_limit * 0.8 and not self.alert_sent:
            self._send_alert(
                f"Warning: LLM spending at 80% of daily limit (${self.today_spent:.2f})"
            )
            self.alert_sent = True

        # Bloquear al 100%
        if self.today_spent >= self.daily_limit:
            raise Exception(
                f"Daily LLM limit reached: ${self.today_spent:.2f}. "
                "Switching to heuristics-only mode."
            )

    def _send_alert(self, message: str):
        """Envía alerta (email, Slack, etc.)."""
        print(f"ALERT: {message}")
```

---

## Métricas Clave a Trackear

```python
class LLMMetrics:
    """Métricas de uso LLM."""

    def __init__(self):
        self.metrics = {
            "total_calls": 0,
            "cached_responses": 0,
            "heuristic_fallbacks": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_tokens_per_call": 0,
            "cache_hit_rate": 0.0
        }

    def record_call(self, cached=False, tokens=0, cost=0.0):
        """Registra llamada LLM."""
        self.metrics["total_calls"] += 1

        if cached:
            self.metrics["cached_responses"] += 1
        else:
            self.metrics["total_tokens"] += tokens
            self.metrics["total_cost"] += cost

        # Calcular tasas
        self.metrics["cache_hit_rate"] = (
            self.metrics["cached_responses"] / self.metrics["total_calls"]
        )
        self.metrics["avg_tokens_per_call"] = (
            self.metrics["total_tokens"] /
            (self.metrics["total_calls"] - self.metrics["cached_responses"])
        )

    def get_report(self) -> str:
        """Genera reporte de métricas."""
        return f"""
LLM Usage Report:
- Total calls: {self.metrics['total_calls']}
- Cache hits: {self.metrics['cached_responses']} ({self.metrics['cache_hit_rate']:.1%})
- Total tokens: {self.metrics['total_tokens']:,}
- Avg tokens/call: {self.metrics['avg_tokens_per_call']:.0f}
- Total cost: ${self.metrics['total_cost']:.2f}
- Savings from cache: ${self.metrics['cached_responses'] * 0.012:.2f}
"""
```

---

## Resumen de Estrategias

| Estrategia | Ahorro | Implementación | Prioridad |
|------------|--------|----------------|-----------|
| **Heurísticas por defecto** | 90% | Fácil | ALTA |
| **LLM selectivo** | 70% | Media | ALTA |
| **Caching** | 40-60% | Media | MEDIA |
| **Prompt optimization** | 30% | Difícil | MEDIA |
| **Modelo escalonado** | 50% | Fácil | MEDIA |
| **Ollama en dev** | 100% dev | Fácil | ALTA |

---

## Plan de Implementación Recomendado

### Fase 1: Inmediata (Semana 1)
1. Configurar heurísticas por defecto
2. LLM solo para story_points >= 8
3. Ollama en desarrollo

**Ahorro esperado:** 85%

### Fase 2: Corto plazo (Semana 2-4)
1. Implementar cache básico
2. Agregar lógica de criticidad
3. Monitoreo de costos

**Ahorro esperado:** 90%

### Fase 3: Mediano plazo (Mes 2-3)
1. Optimización de prompts
2. Modelo escalonado (Haiku/Sonnet)
3. Alertas automatizadas

**Ahorro esperado:** 93%

---

## Costo Proyectado con Optimización

**Sin optimización:**
- 1000 features/mes × $0.071 = $71/mes

**Con optimización completa:**
- 100 features complejas con LLM × $0.071 = $7.10
- 200 features medias con Haiku × $0.015 = $3.00
- 700 features simples con heurísticas × $0 = $0
- **Total: $10.10/mes (86% ahorro)**

---

**Conclusión:** Con estrategia híbrida inteligente, el costo se reduce de $71 a $10 por mes, manteniendo alta calidad en features críticas.

**Última actualización:** 2025-11-12
