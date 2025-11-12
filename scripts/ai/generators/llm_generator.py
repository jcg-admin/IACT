"""
LLMGenerator Agent

Responsabilidad: Generar código de tests usando LLM.
Input: Plan de tests
Output: Código de tests generado
"""

import os
from pathlib import Path
from typing import Any, Dict, List

from .base import Agent


class LLMGenerator(Agent):
    """
    Agente especializado en generación de tests con LLM.

    Usa un LLM (Anthropic/OpenAI/Ollama) para generar código de tests
    siguiendo los estándares del proyecto.

    Providers soportados:
    - anthropic: Claude API (requiere ANTHROPIC_API_KEY)
    - openai: ChatGPT API (requiere OPENAI_API_KEY)
    - ollama: Modelos locales (no requiere API key)

    Ejemplos de configuración:

    # Anthropic (default)
    config = {
        "llm_provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022"
    }

    # OpenAI
    config = {
        "llm_provider": "openai",
        "model": "gpt-4-turbo-preview"
    }

    # Ollama (local)
    config = {
        "llm_provider": "ollama",
        "model": "llama3.1:8b",  # o "deepseek-coder-v2", "qwen2.5-coder:32b"
        "ollama_base_url": "http://localhost:11434"  # opcional, default
    }
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(name="LLMGenerator", config=config)
        self.llm_provider = self.get_config("llm_provider", "anthropic")
        self.model = self.get_config("model", "claude-3-5-sonnet-20241022")
        self._client = None

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan planes de tests."""
        errors = []

        if "test_plans" not in input_data:
            errors.append("Falta 'test_plans' en input")

        if "project_path" not in input_data:
            errors.append("Falta 'project_path' en input")

        # Validar API key (solo para providers remotos)
        if self.llm_provider == "openai":
            if not os.getenv("OPENAI_API_KEY"):
                errors.append("Falta OPENAI_API_KEY en variables de entorno")
        elif self.llm_provider == "anthropic":
            if not os.getenv("ANTHROPIC_API_KEY"):
                errors.append("Falta ANTHROPIC_API_KEY en variables de entorno")
        # Ollama no requiere API key (es local)

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la generación de tests con LLM."""
        test_plans = input_data["test_plans"]
        project_path = Path(input_data["project_path"])

        self.logger.info(f"Generando tests para {len(test_plans)} archivos")

        generated_tests = []

        for plan in test_plans:
            self.logger.info(f"Generando tests para {plan['source_file']}")

            # Leer código fuente
            source_code = self._read_source(
                project_path / plan["source_file"]
            )

            # Generar prompt
            prompt = self._build_prompt(plan, source_code, project_path)

            # Llamar al LLM
            generated_code = self._call_llm(prompt)

            if generated_code:
                generated_tests.append({
                    "source_file": plan["source_file"],
                    "test_file": plan["test_file"],
                    "generated_code": generated_code,
                    "test_cases": plan["test_cases"]
                })

        return {
            "generated_tests": generated_tests,
            "total_generated": len(generated_tests),
            "llm_provider": self.llm_provider,
            "model": self.model
        }

    def _read_source(self, filepath: Path) -> str:
        """Lee el código fuente a testear."""
        try:
            with open(filepath) as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error leyendo {filepath}: {e}")
            return ""

    def _build_prompt(
        self,
        plan: Dict[str, Any],
        source_code: str,
        project_path: Path
    ) -> str:
        """
        Construye el prompt para el LLM.

        Args:
            plan: Plan de tests
            source_code: Código fuente a testear
            project_path: Ruta del proyecto

        Returns:
            Prompt formateado para el LLM
        """
        # Leer convenciones del proyecto si existen
        conventions = self._read_test_conventions(project_path)

        test_cases_desc = "\n".join([
            f"- {tc['name']}: {tc['description']}"
            for tc in plan["test_cases"]
        ])

        prompt = f"""Eres un experto en testing de Python con pytest.

Tu tarea es generar tests completos y de alta calidad para el siguiente código.

CÓDIGO FUENTE A TESTEAR:
```python
{source_code}
```

CASOS DE PRUEBA REQUERIDOS:
{test_cases_desc}

CONVENCIONES DEL PROYECTO:
{conventions}

REQUISITOS ESTRICTOS:

1. ESTRUCTURA:
   - Usa pytest (NO unittest)
   - Usa factory_boy para fixtures si es necesario
   - Sigue patrón AAA (Arrange, Act, Assert)
   - Máximo 50 líneas por test

2. ESTILO:
   - Nombres descriptivos en snake_case
   - Docstrings en todos los tests
   - Type hints donde sea apropiado
   - Sigue PEP 8

3. COBERTURA:
   - Happy path
   - Edge cases
   - Error handling
   - Validaciones

4. NO PERMITIDO:
   - NO uses datos hardcodeados sensibles
   - NO hagas llamadas a redes externas
   - NO uses filesystem real (usa mocks/tmp)
   - NO modifiques código de producción

5. FORMATO DE SALIDA:
   - Solo retorna el código de tests
   - Sin explicaciones adicionales
   - Sin comentarios de metadatos
   - Código ejecutable directamente

GENERA LOS TESTS AHORA:
"""

        return prompt

    def _read_test_conventions(self, project_path: Path) -> str:
        """
        Lee las convenciones de testing del proyecto.

        Args:
            project_path: Ruta del proyecto

        Returns:
            Convenciones como string
        """
        conventions_files = [
            "docs/desarrollo/testing.md",
            "docs/qa/testing_standards.md",
            "TESTING.md"
        ]

        for conv_file in conventions_files:
            filepath = project_path / conv_file
            if filepath.exists():
                try:
                    with open(filepath) as f:
                        return f.read()[:2000]  # Primeros 2000 chars
                except:
                    pass

        # Convenciones por defecto
        return """
- Usa pytest con fixtures
- Usa factory_boy para crear objetos de prueba
- Usa pytest-django para tests de Django
- Mockea dependencias externas
- Usa parametrize para múltiples casos
- Coverage mínimo 85%
"""

    def _call_llm(self, prompt: str) -> str:
        """
        Llama al LLM para generar código.

        Args:
            prompt: Prompt construido

        Returns:
            Código generado por el LLM
        """
        try:
            if self.llm_provider == "anthropic":
                return self._call_anthropic(prompt)
            elif self.llm_provider == "openai":
                return self._call_openai(prompt)
            elif self.llm_provider == "ollama":
                return self._call_ollama(prompt)
            else:
                self.logger.error(f"Provider no soportado: {self.llm_provider}")
                return ""
        except Exception as e:
            self.logger.error(f"Error llamando LLM: {e}")
            return ""

    def _call_anthropic(self, prompt: str) -> str:
        """Llama a la API de Anthropic."""
        try:
            import anthropic

            if self._client is None:
                self._client = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )

            message = self._client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,  # Más determinista
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            generated = message.content[0].text

            # Extraer código si está en bloques markdown
            if "```python" in generated:
                code = generated.split("```python")[1].split("```")[0]
                return code.strip()
            elif "```" in generated:
                code = generated.split("```")[1].split("```")[0]
                return code.strip()

            return generated.strip()

        except Exception as e:
            self.logger.error(f"Error en Anthropic API: {e}")
            return ""

    def _call_openai(self, prompt: str) -> str:
        """Llama a la API de OpenAI."""
        try:
            import openai

            if self._client is None:
                self._client = openai.OpenAI(
                    api_key=os.getenv("OPENAI_API_KEY")
                )

            response = self._client.chat.completions.create(
                model=self.model if self.model else "gpt-4-turbo-preview",
                messages=[{
                    "role": "system",
                    "content": "Eres un experto en testing de Python con pytest."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3,
                max_tokens=4096
            )

            generated = response.choices[0].message.content

            # Extraer código si está en bloques markdown
            if "```python" in generated:
                code = generated.split("```python")[1].split("```")[0]
                return code.strip()
            elif "```" in generated:
                code = generated.split("```")[1].split("```")[0]
                return code.strip()

            return generated.strip()

        except Exception as e:
            self.logger.error(f"Error en OpenAI API: {e}")
            return ""

    def _call_ollama(self, prompt: str) -> str:
        """
        Llama a Ollama local.

        Ollama es un servidor local que ejecuta modelos LLM open-source
        como Llama, DeepSeek Coder, Qwen, etc.

        Args:
            prompt: Prompt construido

        Returns:
            Código generado por Ollama

        Modelos recomendados:
        - llama3.1:8b (general purpose, rápido)
        - deepseek-coder-v2 (especializado en código)
        - qwen2.5-coder:32b (muy bueno para código)
        - codellama:13b (especializado en código)
        """
        try:
            import requests

            # Configuración de Ollama
            base_url = self.get_config("ollama_base_url", "http://localhost:11434")
            model = self.model if self.model else "llama3.1:8b"

            self.logger.info(f"Llamando a Ollama: {base_url} con modelo {model}")

            # Llamada a la API de Ollama
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Más determinista
                        "num_predict": 4096  # Max tokens
                    }
                },
                timeout=120  # Ollama puede ser lento con modelos grandes
            )
            response.raise_for_status()

            # Extraer respuesta
            generated = response.json()["response"]

            # Extraer código de bloques markdown
            if "```python" in generated:
                code = generated.split("```python")[1].split("```")[0]
                return code.strip()
            elif "```" in generated:
                code = generated.split("```")[1].split("```")[0]
                return code.strip()

            return generated.strip()

        except Exception as e:
            self.logger.error(f"Error en Ollama API: {e}")
            self.logger.error(
                "Asegúrate de que Ollama esté corriendo: ollama serve"
            )
            return ""

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Valida que el código generado sea seguro."""
        errors = []

        generated_tests = output_data.get("generated_tests", [])

        if not generated_tests:
            errors.append("No se generó ningún test")

        # Validar cada código generado
        for test in generated_tests:
            code = test.get("generated_code", "")

            if not code:
                errors.append(f"Código vacío para {test.get('test_file')}")
                continue

            # GUARDRAILS CRÍTICOS
            dangerous_patterns = [
                ("eval(", "Uso de eval() detectado"),
                ("exec(", "Uso de exec() detectado"),
                ("__import__", "Uso de __import__ detectado"),
                ("compile(", "Uso de compile() detectado"),
                ("open(", "Uso directo de open() - debe usar mocks/tmp"),
            ]

            for pattern, message in dangerous_patterns:
                if pattern in code:
                    errors.append(f"{message} en {test.get('test_file')}")

            # Validar que tenga estructura pytest
            if "def test_" not in code:
                errors.append(f"No hay funciones test_ en {test.get('test_file')}")

            # Validar longitud razonable
            lines = code.count('\n')
            if lines > 500:
                errors.append(
                    f"Código muy largo ({lines} líneas) en {test.get('test_file')}"
                )

        return errors
