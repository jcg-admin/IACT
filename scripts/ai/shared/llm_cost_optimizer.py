"""
LLM Cost Optimizer - Sistema inteligente de optimización de costos

Decide automáticamente cuándo usar LLM vs heurísticas, qué modelo usar,
y trackea gastos para mantenerse dentro de presupuesto.
"""

import hashlib
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LLMCache:
    """Cache para resultados de LLM."""

    def __init__(self, cache_dir="cache/llm"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_key(self, prompt: str, model: str) -> str:
        """Genera hash único para prompt + modelo."""
        content = f"{prompt}|{model}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, model: str) -> Optional[str]:
        """Obtiene resultado cacheado si existe y es válido."""
        cache_key = self.get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    data = json.load(f)
                    # Cache válido por 7 días
                    age_days = (time.time() - data['timestamp']) / 86400
                    if age_days < 7:
                        logger.info(f"Cache HIT (saved ~$0.012, age: {age_days:.1f} days)")
                        return data['response']
                    else:
                        logger.debug(f"Cache expired ({age_days:.1f} days old)")
            except Exception as e:
                logger.warning(f"Error reading cache: {e}")

        return None

    def set(self, prompt: str, model: str, response: str):
        """Guarda resultado en cache."""
        cache_key = self.get_cache_key(prompt, model)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'prompt_hash': cache_key,
                    'response': response,
                    'timestamp': time.time(),
                    'model': model,
                    'created_at': datetime.now().isoformat()
                }, f, indent=2)
            logger.debug(f"Response cached: {cache_key[:16]}...")
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")


class LLMCostOptimizer:
    """
    Optimizador inteligente de costos LLM.

    Decide automáticamente:
    - Cuándo usar LLM vs heurísticas
    - Qué modelo usar (Haiku/Sonnet/Opus)
    - Trackea gastos y respeta presupuesto
    """

    # Costos por 1K tokens (input + output promedio)
    # Precios actualizados Enero 2025
    MODEL_COSTS = {
        # Claude (Anthropic)
        "claude-3-5-sonnet-20241022": 0.018,  # $3 input + $15 output
        "claude-3-haiku-20240307": 0.0016,    # $0.25 input + $1.25 output
        "claude-3-opus-20240229": 0.090,      # $15 input + $75 output

        # OpenAI GPT
        "gpt-4-turbo-preview": 0.020,         # $10 input + $30 output
        "gpt-4o": 0.010,                      # $5 input + $15 output
        "gpt-4": 0.020,                       # Similar a turbo
        "gpt-3.5-turbo": 0.002,               # $0.5 input + $1.5 output

        # Ollama (local, gratis)
        "llama3.1:8b": 0.0,
        "qwen2.5-coder:32b": 0.0,
        "deepseek-coder-v2": 0.0
    }

    def __init__(self, monthly_budget: float = None):
        """
        Inicializa optimizador.

        Args:
            monthly_budget: Presupuesto mensual en USD (default: $100)
        """
        self.cache = LLMCache()
        self.monthly_budget = monthly_budget or float(os.getenv("LLM_MONTHLY_BUDGET", "100"))
        self.spent_this_month = self._load_spending()
        self.metrics_file = Path("metrics/llm_usage.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    def should_use_llm(self, issue: Dict[str, Any]) -> bool:
        """
        Decide si usar LLM basado en múltiples factores.

        Args:
            issue: Diccionario con información de la feature

        Returns:
            True si debe usar LLM, False para heurísticas
        """

        # 1. Verificar presupuesto (95% del límite)
        if self.spent_this_month >= self.monthly_budget * 0.95:
            logger.warning(
                f"Budget limit reached: ${self.spent_this_month:.2f} / ${self.monthly_budget}"
            )
            return False

        # 2. Verificar entorno
        env = os.getenv("ENVIRONMENT", "development")
        if env == "development":
            logger.debug("Development environment: using heuristics")
            return False

        # 3. Verificar complejidad
        story_points = issue.get('estimated_story_points', 0)
        if story_points < 5:
            logger.debug(f"Low complexity ({story_points} SP): using heuristics")
            return False

        # 4. Verificar criticidad (SIEMPRE LLM para críticos)
        labels = issue.get('labels', [])
        critical_labels = [
            'security', 'payment', 'auth', 'data-loss',
            'breaking-change', 'compliance'
        ]
        if any(label in critical_labels for label in labels):
            logger.info(f"Critical feature detected: using LLM")
            return True

        # 5. Verificar prioridad
        priority = issue.get('priority', 'medium')
        if priority in ['critical', 'high']:
            if story_points >= 3:
                logger.info(f"High priority + {story_points} SP: using LLM")
                return True

        # 6. Default: LLM solo para features complejas
        use_llm = story_points >= 8
        if use_llm:
            logger.info(f"Complex feature ({story_points} SP): using LLM")
        else:
            logger.debug(f"Standard feature ({story_points} SP): using heuristics")

        return use_llm

    def get_optimal_config(self, issue: Dict[str, Any], prefer_provider: str = "auto") -> Optional[Dict[str, Any]]:
        """
        Retorna configuración óptima considerando costos.

        Args:
            issue: Información de la feature
            prefer_provider: "auto", "anthropic", "openai", u "ollama"

        Returns:
            Config dict o None (heurísticas)
        """

        # Verificar si usar LLM
        if not self.should_use_llm(issue):
            return None

        # Determinar modelo según complejidad
        story_points = issue.get('estimated_story_points', 0)
        labels = issue.get('labels', [])

        # Auto-detectar mejor proveedor según disponibilidad de API keys
        if prefer_provider == "auto":
            prefer_provider = self._detect_available_provider()

        # Seleccionar modelo según complejidad y proveedor
        if prefer_provider == "anthropic":
            model, provider = self._select_claude_model(story_points, labels)
            reason = self._get_selection_reason(story_points, labels)

        elif prefer_provider == "openai":
            model, provider = self._select_openai_model(story_points, labels)
            reason = self._get_selection_reason(story_points, labels)

        elif prefer_provider == "ollama":
            # Ollama siempre gratis, usar mejor modelo
            model = "qwen2.5-coder:32b"
            provider = "ollama"
            reason = "local_development"

        else:
            # Fallback a Claude
            model, provider = self._select_claude_model(story_points, labels)
            reason = "fallback"

        logger.info(f"Selected {model} ({provider}) - reason: {reason}")

        return {
            "llm_provider": provider,
            "model": model,
            "use_llm": True,
            "_optimizer_reason": reason
        }

    def _select_claude_model(self, story_points: int, labels: list) -> tuple:
        """Selecciona modelo Claude óptimo según complejidad."""
        if 'security' in labels or 'compliance' in labels or story_points >= 13:
            return "claude-3-5-sonnet-20241022", "anthropic"
        elif story_points >= 8:
            return "claude-3-5-sonnet-20241022", "anthropic"
        else:
            return "claude-3-haiku-20240307", "anthropic"

    def _select_openai_model(self, story_points: int, labels: list) -> tuple:
        """Selecciona modelo OpenAI óptimo según complejidad."""
        if 'security' in labels or 'compliance' in labels or story_points >= 13:
            return "gpt-4-turbo-preview", "openai"
        elif story_points >= 8:
            return "gpt-4o", "openai"  # Mejor precio/calidad para complejidad media-alta
        else:
            return "gpt-3.5-turbo", "openai"

    def _get_selection_reason(self, story_points: int, labels: list) -> str:
        """Determina razón de selección de modelo."""
        if 'security' in labels or 'compliance' in labels:
            return "critical_security"
        elif story_points >= 13:
            return "very_complex"
        elif story_points >= 8:
            return "complex"
        else:
            return "medium"

    def _detect_available_provider(self) -> str:
        """Detecta qué proveedor está disponible según API keys."""
        import os

        if os.getenv("ANTHROPIC_API_KEY"):
            return "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            return "openai"
        else:
            # Intentar Ollama local
            return "ollama"

    def track_usage(self, tokens_used: int, model: str, cached: bool = False):
        """
        Trackea uso de tokens y costo.

        Args:
            tokens_used: Número de tokens usados
            model: Modelo usado
            cached: Si la respuesta vino del cache
        """

        if cached:
            logger.info("Response from cache: $0.00")
            self._record_metric("cache_hit")
            return

        # Calcular costo
        cost_per_1k = self.MODEL_COSTS.get(model, 0.018)
        cost = (tokens_used / 1000) * cost_per_1k

        # Actualizar gasto
        self.spent_this_month += cost
        self._save_spending()

        # Log
        logger.info(
            f"LLM usage: {tokens_used} tokens, ${cost:.4f} "
            f"(month: ${self.spent_this_month:.2f} / ${self.monthly_budget})"
        )

        # Alerta si cerca del límite
        if self.spent_this_month >= self.monthly_budget * 0.9:
            logger.warning(
                f"WARNING: 90% of monthly budget used "
                f"(${self.spent_this_month:.2f} / ${self.monthly_budget})"
            )

        self._record_metric("llm_call", cost=cost, tokens=tokens_used)

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso.

        Returns:
            Dict con métricas
        """
        return {
            "spent_this_month": self.spent_this_month,
            "monthly_budget": self.monthly_budget,
            "budget_used_pct": (self.spent_this_month / self.monthly_budget) * 100,
            "remaining_budget": self.monthly_budget - self.spent_this_month
        }

    def _load_spending(self) -> float:
        """Carga gasto del mes actual desde archivo."""
        spending_file = Path("metrics/llm_spending.json")

        if spending_file.exists():
            try:
                with open(spending_file) as f:
                    data = json.load(f)
                    current_month = datetime.now().strftime("%Y-%m")

                    if data.get("month") == current_month:
                        return data.get("spent", 0.0)
            except Exception as e:
                logger.warning(f"Error loading spending: {e}")

        return 0.0

    def _save_spending(self):
        """Guarda gasto actualizado."""
        spending_file = Path("metrics/llm_spending.json")
        spending_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(spending_file, 'w') as f:
                json.dump({
                    "month": datetime.now().strftime("%Y-%m"),
                    "spent": self.spent_this_month,
                    "budget": self.monthly_budget,
                    "last_updated": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"Error saving spending: {e}")

    def _record_metric(self, metric_type: str, **kwargs):
        """Registra métrica de uso."""
        try:
            metrics = []
            if self.metrics_file.exists():
                with open(self.metrics_file) as f:
                    metrics = json.load(f)

            metrics.append({
                "type": metric_type,
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                **kwargs
            })

            # Mantener solo últimas 1000 métricas
            if len(metrics) > 1000:
                metrics = metrics[-1000:]

            with open(self.metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)

        except Exception as e:
            logger.warning(f"Error recording metric: {e}")


# Instancia global (singleton)
_optimizer_instance = None


def get_optimizer() -> LLMCostOptimizer:
    """Obtiene instancia global del optimizador."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = LLMCostOptimizer()
    return _optimizer_instance
