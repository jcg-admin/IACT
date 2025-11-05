# Guía de Inicio Rápido - Generación Automática de Tests

Esta guía te ayudará a comenzar a usar el sistema de generación automática de tests en menos de 5 minutos.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalacion)
3. [Configuración](#configuracion)
4. [Primer Uso](#primer-uso)
5. [Ejemplos Comunes](#ejemplos-comunes)
6. [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

### Software Necesario

- Python 3.10+
- pip
- git
- GitHub CLI (opcional, para crear PRs)

### Validar Entorno

```bash
# Validar que todo esté instalado
./scripts/ai/examples/quickstart.sh check
```

---

## Instalación

### 1. Instalar Dependencias Python

```bash
pip install pytest pytest-cov anthropic ruff black isort mypy
```

### 2. Configurar API Key

#### Opción A: Variable de Entorno (Recomendado)

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

Para hacerlo permanente, agrega la línea a tu `~/.bashrc` o `~/.zshrc`.

#### Opción B: Archivo .env

```bash
# En el directorio raíz del proyecto
echo "ANTHROPIC_API_KEY=sk-ant-api03-..." > .env
```

### 3. Verificar Instalación

```bash
cd scripts/ai/examples
./quickstart.sh check
```

Deberías ver:

```
[OK] Python 3 encontrado: 3.12.0
[OK] pip3 encontrado
[OK] pytest encontrado: 8.0.0
[OK] pytest-cov encontrado
[OK] anthropic SDK encontrado
[OK] ANTHROPIC_API_KEY configurada
[OK] GitHub CLI encontrado

Entorno OK - Listo para ejecutar
```

---

## Configuración

El sistema viene con 4 configuraciones predefinidas:

### 1. Configuración por Defecto (`test_generation.json`)

Balanceada para uso general.

- Objetivo: 85% cobertura
- Tests por ejecución: 5
- Incremento mínimo: 5%

### 2. Configuración Agresiva (`test_generation_aggressive.json`)

Para proyectos que requieren alta cobertura.

- Objetivo: 90% cobertura
- Tests por ejecución: 10
- Incremento mínimo: 8%
- Type checking estricto (mypy)

### 3. Configuración Conservadora (`test_generation_conservative.json`)

Para empezar con objetivos más alcanzables.

- Objetivo: 80% cobertura
- Tests por ejecución: 3
- Incremento mínimo: 3%
- Sin type checking

### 4. Configuración Dry-Run (`test_generation_dry_run.json`)

Para explorar sin modificar código.

- Simula el pipeline completo
- NO genera archivos reales
- NO crea PRs
- Útil para testing

---

## Primer Uso

### Demo (Sin Modificar Código)

La forma más segura de probar el sistema:

```bash
cd scripts/ai/examples
./quickstart.sh demo
```

Esto ejecutará el pipeline completo en modo simulación. Revisa los resultados en `output/test_generation_dryrun/`.

### Ejecución Básica

Una vez que hayas validado la demo:

```bash
cd scripts/ai/examples
./quickstart.sh basic
```

El sistema:
1. Analizará la cobertura actual
2. Identificará gaps
3. Generará tests
4. Los validará y ejecutará
5. Creará un Pull Request

Tiempo estimado: 5-10 minutos

---

## Ejemplos Comunes

### Ejemplo 1: Generar Tests para Todo el Proyecto

```bash
cd scripts/ai
python3 test_generation_orchestrator.py \
  --project-path ../../api/callcentersite
```

### Ejemplo 2: Generar Tests con Configuración Agresiva

```bash
cd scripts/ai/examples
./quickstart.sh aggressive
```

Se te pedirá confirmación debido a los requisitos estrictos.

### Ejemplo 3: Generar Tests para un Solo Archivo

```bash
cd scripts/ai/examples
./example_single_file.sh ../../api/callcentersite/app/models.py
```

### Ejemplo 4: Uso Programático (Python)

```bash
cd scripts/ai/examples
python3 example_specific_module.py
```

Este ejemplo muestra cómo usar el orquestador desde Python con configuración custom.

### Ejemplo 5: Integración con CI/CD

```bash
# En tu pipeline CI/CD
export ANTHROPIC_API_KEY="$SECRET_ANTHROPIC_KEY"
./scripts/ai/examples/example_ci_integration.sh
```

---

## Salidas del Sistema

Después de ejecutar, encontrarás:

### Directorio de Output

```
output/test_generation/
├── 01_CoverageAnalyzer.json     # Análisis de cobertura
├── 02_TestPlanner.json          # Plan de tests
├── 03_LLMGenerator.json         # Tests generados (código)
├── 04_SyntaxValidator.json      # Validación de sintaxis
├── 05_TestRunner.json           # Resultados de ejecución
├── 06_CoverageVerifier.json     # Verificación de cobertura
└── 07_PRCreator.json            # Info del Pull Request
```

### Tests Generados

Los tests se crean en:

```
tests/
├── test_models_generated.py
├── test_views_generated.py
└── test_serializers_generated.py
```

### Pull Request

Si habilitaste `pr_creator`, se creará un PR con:
- Branch: `bot/generated-tests-{timestamp}`
- Label: `bot-generated-tests`
- Estado: Draft (requiere review)

---

## Configuración Avanzada

### Personalizar Configuración

Copia una configuración base:

```bash
cd scripts/ai/config
cp test_generation.json my_custom_config.json
```

Edita `my_custom_config.json`:

```json
{
  "agents": {
    "coverage_analyzer": {
      "min_coverage": 90,
      "threshold_low": 75
    },
    "test_planner": {
      "max_tests_per_run": 10,
      "prioritize_critical_files": true
    },
    "llm_generator": {
      "temperature": 0.2,
      "model": "claude-3-5-sonnet-20241022"
    }
  }
}
```

Úsala:

```bash
python3 test_generation_orchestrator.py \
  --project-path ../../api/callcentersite \
  --config config/my_custom_config.json
```

---

## Troubleshooting

### Error: "ANTHROPIC_API_KEY no encontrada"

**Solución**:
```bash
export ANTHROPIC_API_KEY="tu-api-key"
```

### Error: "ModuleNotFoundError: No module named 'anthropic'"

**Solución**:
```bash
pip install anthropic
```

### Error: "gh: command not found"

**Solución**: Instalar GitHub CLI o deshabilitar PR creation:

```json
{
  "agents": {
    "pr_creator": {
      "enabled": false
    }
  }
}
```

### Tests Generados No Pasan

El LLM puede generar tests incorrectos ocasionalmente.

**Solución**:
1. Revisar logs en `output/test_generation/03_LLMGenerator.json`
2. Ajustar `temperature` en configuración (menor = más conservador)
3. Agregar ejemplos en `few_shot_examples`

### Cobertura No Aumenta

**Causas comunes**:
- Los archivos priorizados ya tienen buena cobertura
- Tests generados no cubren las líneas correctas

**Solución**:
1. Bajar `threshold_low` para incluir más archivos
2. Aumentar `max_tests_per_run`
3. Revisar `prioritized_targets` en `01_CoverageAnalyzer.json`

### Timeout en LLM Generator

**Solución**: Reducir `max_tests_per_run` o aumentar timeout:

```json
{
  "agents": {
    "test_planner": {
      "max_tests_per_run": 3
    },
    "test_runner": {
      "timeout": 600
    }
  }
}
```

---

## Mejores Prácticas

### 1. Empezar con Demo

Siempre ejecuta `./quickstart.sh demo` antes de la primera ejecución real.

### 2. Incrementos Pequeños

Configura `max_tests_per_run: 3-5` para mejor control.

### 3. Revisar Manualmente

Los tests generados son un punto de partida. Revisa y mejora antes de mergear.

### 4. Iterar

Ejecuta el pipeline múltiples veces. Cada ejecución mejora la cobertura gradualmente.

### 5. CI/CD Integration

Integra en tu pipeline CI/CD para generación automática continua.

---

## Recursos Adicionales

- [Documentación Completa](../README.md)
- [Arquitectura de Agentes](../../../docs/desarrollo/arquitectura_agentes_especializados.md)
- [Guía de Automatización](../../../docs/desarrollo/agentes_automatizacion.md)

---

## Siguientes Pasos

1. Ejecuta la demo: `./quickstart.sh demo`
2. Revisa los resultados en `output/test_generation_dryrun/`
3. Ejecuta básico: `./quickstart.sh basic`
4. Revisa el PR generado
5. Personaliza la configuración según tus necesidades

¿Preguntas? Revisa la [documentación completa](../README.md) o abre un issue en GitHub.
