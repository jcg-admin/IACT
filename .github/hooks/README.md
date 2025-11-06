# Git Hooks - Proyecto IACT

## Descripción

Este directorio contiene la documentación de los Git hooks configurados para el proyecto IACT mediante pre-commit framework.

## Hooks Configurados

Los hooks se configuran en `api/callcentersite/.pre_commit_config.yaml` y se ejecutan automáticamente antes de cada commit.

### 1. Ruff - Linting y Formateo Python

**Propósito**: Linting ultra-rápido y formateo de código Python.

**Archivos afectados**: `*.py`, `*.pyi`, `*.ipynb`

**Acciones**:
- Linting con auto-fix de problemas comunes
- Formateo de código según estándares del proyecto

**Ejecutar manualmente**:
```bash
cd api/callcentersite
ruff check --fix .
ruff format .
```

### 2. MyPy - Type Checking

**Propósito**: Verificación estática de tipos en Python.

**Archivos afectados**: `*.py` (excepto migrations, tests)

**Configuración**: `pyproject.toml`

**Dependencias adicionales**:
- django-stubs
- djangorestframework-stubs
- types-python-dateutil
- types-pytz
- types-requests

**Ejecutar manualmente**:
```bash
cd api/callcentersite
mypy .
```

### 3. Pre-commit Standard Hooks

**Hooks incluidos**:
- `trailing-whitespace`: Eliminar espacios al final de líneas
- `end-of-file-fixer`: Asegurar EOF al final de archivos
- `check-yaml`: Validar sintaxis YAML
- `check-json`: Validar sintaxis JSON
- `check-toml`: Validar sintaxis TOML
- `check-added-large-files`: Prevenir commits de archivos grandes (>1MB)
- `check-case-conflict`: Detectar conflictos de nombres (case-sensitive)
- `check-merge-conflict`: Detectar marcadores de merge sin resolver
- `check-docstring-first`: Verificar que docstrings estén antes de código
- `debug-statements`: Detectar `print()`, `pdb.set_trace()`, etc.
- `mixed-line-ending`: Normalizar line endings a LF

### 4. Django Upgrade

**Propósito**: Modernizar código Django a versión target.

**Target**: Django 5.2

**Archivos afectados**: `*.py`

**Ejecutar manualmente**:
```bash
cd api/callcentersite
django-upgrade --target-version 5.2 **/*.py
```

### 5. Bandit - Security Scanning

**Propósito**: Detectar vulnerabilidades de seguridad en código Python.

**Archivos afectados**: `*.py` (excepto tests)

**Configuración**: `pyproject.toml`

**Ejecutar manualmente**:
```bash
cd api/callcentersite
bandit -r . -c pyproject.toml
```

**Severidades detectadas**:
- HIGH: Vulnerabilidades críticas
- MEDIUM: Vulnerabilidades moderadas
- LOW: Vulnerabilidades menores

### 6. Detect Secrets

**Propósito**: Prevenir commits de secretos y credenciales.

**Archivos afectados**: Todos (excepto `.env.example`, `package-lock.json`)

**Baseline**: `.secrets.baseline`

**Ejecutar manualmente**:
```bash
cd api/callcentersite
detect-secrets scan --baseline .secrets.baseline
```

**Actualizar baseline** (después de revisar falsos positivos):
```bash
detect-secrets scan --update .secrets.baseline
```

### 7. No Emojis (Custom Hook)

**Propósito**: Prevenir uso de emojis en documentación y código.

**Archivos afectados**: `*.md`, `*.txt`, `*.py`, `*.js`, `*.ts`, `*.jsx`, `*.tsx`, `*.yaml`, `*.yml`, `*.json`, `*.sh`, `*.bash`

**Script**: `scripts/check_no_emojis.py`

**Ejecutar manualmente**:
```bash
# Verificar archivos específicos
python scripts/check_no_emojis.py file1.md file2.py

# Verificar todos los archivos del proyecto
python scripts/check_no_emojis.py --all
```

**Razón**: Mantener profesionalismo, evitar problemas de encoding, facilitar búsqueda y procesamiento.

**Alternativas recomendadas**:
- En lugar de checkmarks: `[x]` o "Completado"
- En lugar de alerts: "ADVERTENCIA:" o "Nota:"
- Ver [Guía de Estilo](../../docs/gobernanza/GUIA_ESTILO.md) para más alternativas

---

## Git Hooks Nativos

Además de los pre-commit hooks configurados via framework, el proyecto incluye hooks nativos de Git para validaciones adicionales.

### 8. Pre-push Hook (Git Native)

**Propósito**: Validaciones antes de git push para prevenir errores en remote.

**Ubicación**: `.github/hooks/pre-push.sample` (instalable con `make install_hooks`)

**Validaciones que realiza**:

1. **Specs para feature branches**:
   - Detecta si el branch es `feature/*`
   - Busca especificación relacionada en `docs/specs/`
   - Valida la spec usando `validate_spec.sh`
   - Pregunta si continuar si no hay spec

2. **Detección de secrets**:
   - Escanea archivos staged con detect-secrets
   - Previene push de credenciales o tokens
   - Bloquea push si se detectan secrets

3. **Validación de emojis**:
   - Verifica archivos staged usando `check_no_emojis.py`
   - Previene push de emojis prohibidos
   - Bloquea push si se detectan emojis

4. **Tests críticos**:
   - Detecta cambios en archivos Python
   - Ejecuta tests marcados como `@pytest.mark.critical`
   - Bloquea push si tests críticos fallan

**Instalación**:
```bash
# Usando Makefile (recomendado)
make install_hooks

# O manualmente
./scripts/install_hooks.sh

# Verificar instalación
./scripts/install_hooks.sh --verify
```

**Ejecutar manualmente**:
```bash
# Simular pre-push sin hacer push real
.git/hooks/pre-push origin https://github.com/2-Coatl/IACT---project
```

**Bypass temporal** (solo para emergencias):
```bash
git push --no-verify
```

**Razones válidas para bypass**:
- Hotfix crítico en producción
- CI/CD está caído y necesitas push urgente
- False positive conocido que está siendo investigado

**NUNCA hacer bypass para**:
- Evitar crear especificación de feature
- Evitar corregir secrets expuestos
- Evitar corregir tests fallidos

**Desinstalar**:
```bash
./scripts/install_hooks.sh --uninstall
```

---

## Instalación

### Instalar pre-commit framework

```bash
# Con pip
pip install pre-commit

# O con homebrew (macOS)
brew install pre-commit
```

### Instalar hooks de pre-commit en el repositorio

```bash
cd api/callcentersite
pre-commit install
```

### Instalar hooks nativos de Git (pre-push)

```bash
# Desde la raíz del proyecto
make install_hooks

# O manualmente
./scripts/install_hooks.sh
```

Este comando instalará:
- Hook pre-push con validaciones antes de push
- Backups de hooks existentes (si los hay)
- Configuración automática de permisos

**Verificar instalación**:
```bash
./scripts/install_hooks.sh --verify
```

### Instalación completa (recomendado)

```bash
# 1. Instalar pre-commit framework
pip install pre-commit

# 2. Instalar hooks de pre-commit
cd api/callcentersite
pre-commit install

# 3. Instalar hooks nativos de Git
cd ../..  # Volver a raíz
make install_hooks

# 4. Verificar todo
make check_all
```

---

## Uso

### Ejecución Automática

Los hooks se ejecutan automáticamente al hacer `git commit`.

```bash
git add .
git commit -m "feat: nueva funcionalidad"
# Hooks se ejecutan automáticamente
```

### Ejecución Manual

**Ejecutar todos los hooks en archivos staged**:
```bash
cd api/callcentersite
pre-commit run
```

**Ejecutar todos los hooks en todos los archivos**:
```bash
cd api/callcentersite
pre-commit run --all-files
```

**Ejecutar hook específico**:
```bash
cd api/callcentersite
pre-commit run ruff --all-files
pre-commit run mypy --all-files
pre-commit run no-emojis --all-files
```

### Bypass de Hooks (NO RECOMENDADO)

**Solo usar en emergencias**:
```bash
git commit --no-verify -m "mensaje"
```

**Razones válidas para bypass**:
- Hotfix crítico en producción
- Fix de hook roto (debe seguirse con PR para arreglar hook)
- Commit de work-in-progress temporal (branch personal)

**NUNCA hacer bypass para**:
- Evitar corregir errores de linting
- Evitar escribir tests
- Evitar corregir problemas de seguridad

---

## Troubleshooting

### Hook falla con "command not found"

**Problema**: El comando del hook no se encuentra en PATH.

**Solución**:
```bash
# Reinstalar hooks
cd api/callcentersite
pre-commit uninstall
pre-commit install

# O reinstalar entorno virtual
deactivate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
pre-commit install
```

### Hook no-emojis falla

**Problema**: El script Python no se encuentra.

**Solución**:
```bash
# Verificar que el script existe
ls -la scripts/check_no_emojis.py

# Hacer ejecutable
chmod +x scripts/check_no_emojis.py

# Ejecutar manualmente para debug
python scripts/check_no_emojis.py archivo.md
```

### MyPy falla con "Module not found"

**Problema**: Falta alguna dependencia de type stubs.

**Solución**:
```bash
cd api/callcentersite
pip install -r requirements/dev.txt
pip install django-stubs djangorestframework-stubs types-python-dateutil types-pytz types-requests
```

### Bandit reporta falso positivo

**Solución 1: Suprimir en código** (preferido):
```python
# nosec: B601 - Razón específica por la que es seguro
subprocess.call(command, shell=True)  # nosec
```

**Solución 2: Configurar en pyproject.toml**:
```toml
[tool.bandit]
exclude_dirs = ["tests", "migrations"]
skips = ["B601"]  # Skip shell injection check
```

### Detect-secrets reporta falso positivo

**Solución**:
```bash
cd api/callcentersite

# Actualizar baseline (revisa que sea falso positivo primero)
detect-secrets scan --update .secrets.baseline

# Commit el baseline actualizado
git add .secrets.baseline
git commit -m "chore: actualizar baseline de secrets"
```

---

## CI/CD

### Pre-commit.ci

El proyecto usa [pre-commit.ci](https://pre-commit.ci) para ejecutar hooks automáticamente en PRs.

**Configuración**: Ver `ci:` section en `.pre_commit_config.yaml`

**Features**:
- Auto-fix en PRs
- Auto-update de hooks semanalmente
- Comentarios en PRs con resultados

### Deshabilitar hook temporalmente en CI

Editar `.pre_commit_config.yaml`:
```yaml
ci:
  skip: [mypy, bandit]  # Hooks a saltar en CI
```

---

## Métricas

### Hooks exitosos

Métrica objetivo: **>95%** de commits pasan hooks en primer intento.

### Falsos positivos

Métrica objetivo: **<5%** de hooks reportan falsos positivos.

### Tiempo de ejecución

Métrica objetivo: **<30 segundos** para ejecución completa de hooks.

---

## Actualización de Hooks

### Actualizar versiones manualmente

```bash
cd api/callcentersite
pre-commit autoupdate
```

### Auto-update semanal (CI)

Configurado en `.pre_commit_config.yaml`:
```yaml
ci:
  autoupdate_schedule: weekly
```

---

## Recursos Adicionales

- [Pre-commit Framework](https://pre-commit.com/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Detect Secrets Documentation](https://github.com/Yelp/detect-secrets)
- [Guía de Estilo IACT](../../docs/gobernanza/GUIA_ESTILO.md)

---

## Changelog

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.1.0 | 2025-11-06 | Agregado hook pre-push nativo con 4 validaciones |
| 1.0.0 | 2025-11-06 | Creación inicial con 7 hooks de pre-commit configurados |

---

## Contacto

Para preguntas sobre hooks:
- **Configuración general**: Tech Lead
- **Hook custom no-emojis**: Equipo Gobernanza
- **Seguridad (Bandit)**: Security Lead
