# Ejemplos de Uso - Generación Automática de Tests

Este directorio contiene ejemplos prácticos y scripts de inicio rápido para el sistema de generación automática de tests.

## Contenido

```
examples/
├── README.md                       # Este archivo
├── GUIA_INICIO_RAPIDO.md          # Guía completa paso a paso
├── quickstart.sh                   # Script de inicio rápido
├── validate_environment.sh         # Validación exhaustiva del entorno
├── example_single_file.sh          # Ejemplo: Tests para 1 archivo
├── example_specific_module.py      # Ejemplo: Configuración custom
└── example_ci_integration.sh       # Ejemplo: Integración CI/CD
```

## Inicio Rápido (5 minutos)

### 1. Validar Entorno

```bash
./validate_environment.sh
```

O de forma rápida:

```bash
./quickstart.sh check
```

### 2. Ejecutar Demo

```bash
./quickstart.sh demo
```

Esto ejecuta el pipeline completo en modo simulación (sin modificar código).

### 3. Ejecución Real

```bash
./quickstart.sh basic
```

Genera tests y crea un Pull Request.

---

## Ejemplos Disponibles

### 1. quickstart.sh

Script principal de inicio rápido con 5 modos:

```bash
./quickstart.sh check          # Validar entorno
./quickstart.sh demo           # Demo sin modificar código
./quickstart.sh basic          # Configuración por defecto
./quickstart.sh aggressive     # Configuración agresiva (90% cobertura)
./quickstart.sh conservative   # Configuración conservadora (80% cobertura)
```

**Casos de uso**:
- Primera vez usando el sistema → `demo`
- Uso normal → `basic`
- Proyectos críticos → `aggressive`
- Proyectos legacy → `conservative`

### 2. validate_environment.sh

Validación exhaustiva del entorno:

```bash
./validate_environment.sh
```

**Valida**:
- Python 3.10+
- Dependencias (pytest, anthropic, etc)
- API keys
- Herramientas (git, gh)
- Estructura del proyecto
- Permisos
- Conectividad con API

**Output**:
```
[OK] Python 3.12.0
[OK] pytest 8.0.0
[OK] ANTHROPIC_API_KEY configurada
[OK] GitHub CLI autenticado
[OK] Conexión exitosa con API de Anthropic

TODO OK - Entorno completamente configurado
```

### 3. example_single_file.sh

Genera tests para un solo archivo específico:

```bash
./example_single_file.sh <ruta_al_archivo>
```

**Ejemplo**:
```bash
./example_single_file.sh ../../api/callcentersite/app/models.py
```

**Casos de uso**:
- Agregar tests a un módulo específico
- Desarrollo incremental
- Testing de archivos nuevos

### 4. example_specific_module.py

Uso programático con configuración avanzada:

```bash
python3 example_specific_module.py
```

**Características**:
- Configuración completamente customizable
- Filtros por patrones (include/exclude)
- Estrategias de generación configurables
- System prompts personalizados
- Few-shot examples

**Casos de uso**:
- Integración en pipelines custom
- Configuración muy específica
- Experimentación con prompts

### 5. example_ci_integration.sh

Integración en CI/CD:

```bash
export ANTHROPIC_API_KEY="$SECRET_KEY"
./example_ci_integration.sh
```

**Comportamiento**:
1. Analiza cobertura actual
2. Si < objetivo → genera tests
3. Crea PR automático
4. Si >= objetivo → sale sin hacer nada

**Casos de uso**:
- GitHub Actions
- GitLab CI
- Jenkins
- Cualquier sistema CI/CD

**Ejemplo GitHub Actions**:
```yaml
- name: Generate Tests
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    ./scripts/ai/examples/example_ci_integration.sh
```

---

## Configuraciones Disponibles

En `../config/`:

### 1. test_generation.json (Por Defecto)

Balanceada para uso general.

```json
{
  "min_coverage": 85,
  "max_tests_per_run": 5,
  "min_coverage_increase": 5.0
}
```

**Usar cuando**: Uso normal, proyectos medianos

### 2. test_generation_aggressive.json

Para proyectos críticos.

```json
{
  "min_coverage": 90,
  "max_tests_per_run": 10,
  "min_coverage_increase": 8.0,
  "run_mypy": true
}
```

**Usar cuando**: Aplicaciones críticas, alta calidad requerida

### 3. test_generation_conservative.json

Para empezar gradualmente.

```json
{
  "min_coverage": 80,
  "max_tests_per_run": 3,
  "min_coverage_increase": 3.0
}
```

**Usar cuando**: Proyectos legacy, primera vez

### 4. test_generation_dry_run.json

Para explorar sin cambios.

```json
{
  "dry_run": true,
  "skip_execution": true,
  "pr_creator": { "enabled": false }
}
```

**Usar cuando**: Testing del sistema, exploración

---

## Flujos de Trabajo Comunes

### Flujo 1: Primera Vez

```bash
# 1. Validar
./validate_environment.sh

# 2. Demo
./quickstart.sh demo

# 3. Revisar output
ls -la ../output/test_generation_dryrun/

# 4. Si todo OK, ejecutar real
./quickstart.sh basic
```

### Flujo 2: Desarrollo Iterativo

```bash
# Cada día/semana
./quickstart.sh conservative   # Generar 3 tests
# Revisar PR, mergear
# Repetir hasta alcanzar objetivo
```

### Flujo 3: Archivo Específico

```bash
# Acabas de crear models.py, necesitas tests
./example_single_file.sh ../api/app/models.py

# Revisar tests generados
cat ../api/tests/test_models_generated.py

# Editar si necesario
vim ../api/tests/test_models_generated.py

# Ejecutar
cd ../api && pytest tests/test_models_generated.py
```

### Flujo 4: CI/CD Automático

```yaml
# .github/workflows/generate-tests.yml
name: Auto Generate Tests

on:
  schedule:
    - cron: "0 2 * * 1"  # Lunes 2 AM

jobs:
  generate-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install pytest pytest-cov anthropic ruff black

      - name: Generate Tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          ./scripts/ai/examples/example_ci_integration.sh
```

---

## Personalización

### Crear Tu Propia Configuración

```bash
# Copiar base
cp ../config/test_generation.json ../config/my_config.json

# Editar
vim ../config/my_config.json

# Usar
cd ..
python3 test_generation_orchestrator.py \
  --project-path ../../api/callcentersite \
  --config config/my_config.json
```

### Opciones Configurables

```json
{
  "agents": {
    "coverage_analyzer": {
      "min_coverage": 85,
      "threshold_low": 70,
      "include_patterns": ["**/models.py", "**/views.py"],
      "exclude_patterns": ["**/migrations/**"]
    },
    "test_planner": {
      "max_tests_per_run": 5,
      "strategies": ["happy_path", "edge_cases", "error_handling"]
    },
    "llm_generator": {
      "llm_provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.3,
      "max_tokens": 4096
    },
    "syntax_validator": {
      "run_mypy": true,
      "run_ruff": true,
      "run_black": true
    },
    "coverage_verifier": {
      "min_coverage_increase": 5.0,
      "check_branch_coverage": true
    },
    "pr_creator": {
      "enabled": true,
      "labels": ["bot-generated-tests"],
      "draft": true
    }
  }
}
```

---

## Troubleshooting

### Problema: API Key Inválida

```bash
# Verificar
echo $ANTHROPIC_API_KEY

# Configurar
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Validar
./validate_environment.sh
```

### Problema: Tests Generados Fallan

**Causa**: El LLM generó tests incorrectos.

**Solución**:
1. Revisar logs: `../output/test_generation/03_LLMGenerator.json`
2. Bajar temperatura: `"temperature": 0.2`
3. Agregar few-shot examples en configuración

### Problema: Cobertura No Aumenta

**Causa**: Los archivos priorizados no son los correctos.

**Solución**:
1. Revisar: `../output/test_generation/01_CoverageAnalyzer.json`
2. Bajar `threshold_low` para incluir más archivos
3. Usar filtros: `include_patterns`, `exclude_patterns`

### Problema: Timeout

**Causa**: Generación muy lenta.

**Solución**:
1. Reducir `max_tests_per_run`
2. Aumentar timeout: `"timeout": 600`
3. Ejecutar en paralelo para múltiples archivos

---

## Mejores Prácticas

### 1. Empezar Pequeño

```bash
# Mal
./quickstart.sh aggressive  # 10 tests de golpe

# Bien
./quickstart.sh conservative  # 3 tests, iterar
```

### 2. Validar Siempre

```bash
# Antes de cada ejecución
./quickstart.sh check
```

### 3. Revisar Output

```bash
# Después de ejecución
ls -la ../output/test_generation/
cat ../output/test_generation/03_LLMGenerator.json
```

### 4. Iterar

```bash
# No esperar 85% de una vez
# Ejecutar múltiples veces:
./quickstart.sh conservative  # 60% → 65%
./quickstart.sh conservative  # 65% → 70%
./quickstart.sh basic         # 70% → 75%
./quickstart.sh aggressive    # 75% → 85%
```

### 5. CI/CD Integration

Integrar en tu pipeline para generación continua automática.

---

## Recursos

- [Guía de Inicio Rápido](GUIA_INICIO_RAPIDO.md)
- [Documentación Principal](../README.md)
- [Arquitectura de Agentes](../../../docs/desarrollo/arquitectura_servicios_especializados.md)
- [Guía de Automatización](../../../docs/desarrollo/automatizacion_servicios.md)

---

## FAQ

**P: ¿Cuánto cuesta ejecutar esto?**

R: Depende del modelo y cantidad de tests. Claude 3.5 Sonnet:
- 1 archivo simple: ~$0.01-0.05
- 5 archivos: ~$0.10-0.25
- 10 archivos: ~$0.25-0.50

**P: ¿Los tests generados son perfectos?**

R: No. Son un punto de partida (70-80% utilizables). Siempre revisa manualmente.

**P: ¿Puedo usar otro LLM?**

R: Sí, pero actualmente solo Anthropic está implementado. OpenAI vendrá pronto.

**P: ¿Funciona con otros frameworks además de Django?**

R: Sí, funciona con cualquier proyecto Python que use pytest.

**P: ¿Qué pasa si mi cobertura ya es 90%?**

R: El sistema detecta automáticamente y no hace nada (modo conservador de recursos).

---

## Contribuir

¿Encontraste un bug o tienes una mejora?

1. Crea un issue en GitHub
2. O envía un PR con tu ejemplo

---

**Última actualización**: 2025-11-05
**Mantenedor**: Equipo de Desarrollo IACT
