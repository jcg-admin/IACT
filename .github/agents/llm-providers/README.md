# Agentes de Proveedores LLM

Estos agentes encapsulan las buenas prácticas para trabajar con diferentes proveedores de modelos de lenguaje. La información se mantiene libre de referencias a rutas específicas para facilitar su mantenimiento.

## ClaudeAgent
- Coordina el uso de modelos Anthropic en flujos multi-agente.
- Revisa credenciales, límites y cumplimiento de políticas.
- Recomienda técnicas de prompting y controles de factualidad.

## ChatGPTAgent
- Gestiona interacciones con modelos de OpenAI.
- Optimiza prompts para tareas de propósito general y generación rápida.
- Lleva registro de costos, decisiones y retroalimentación del equipo.

## HuggingFaceAgent
- Facilita experimentos con modelos hospedados o locales.
- Ajusta parámetros según restricciones de privacidad y recursos.
- Documenta configuraciones para reproducibilidad y evaluación comparativa.

### Recomendaciones Comunes
- Validar credenciales antes de iniciar sesiones largas.
- Mantener planes de trabajo actualizados con métricas de calidad y costo.
- Compartir aprendizajes de prompting entre equipos para acelerar iteraciones futuras.
