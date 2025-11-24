---
id: CICD-BACKEND-001
tipo: documentacion
categoria: cicd
version: 1.0.0
fecha_creacion: 2025-11-18
---

# CI/CD Backend

Documentación de CI/CD para el backend.

---

## Pipeline Actual

### GitHub Actions

**Ubicación:** `.github/workflows/backend-*.yml`

**Stages:**

1. **Lint**
 - flake8 para estilo de código
 - black para formato
 - isort para imports

2. **Test**
 - pytest con coverage
 - Coverage mínimo: 80%

3. **Security**
 - Safety para dependencies vulnerables
 - Bandit para security issues en código

4. **Build**
 - Validar que proyecto se construye correctamente

---

## Comandos Locales

### Ejecutar Tests
```bash
# Tests completos
pytest

# Con coverage
pytest --cov=myapp --cov-report=html

# Tests específicos
pytest tests/test_services.py
```

### Linting
```bash
# flake8
flake8 myapp/

# black
black --check myapp/

# isort
isort --check myapp/
```

### Fix Automático
```bash
# Formatear código
black myapp/

# Ordenar imports
isort myapp/
```

---

## Configuración

### pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = --cov --cov-report=html --cov-fail-under=80
```

### .flake8
```ini
[flake8]
max-line-length = 100
exclude = migrations,__pycache__,.git
```

---

## Deployment

### Staging
1. Merge a branch `staging`
2. CI/CD ejecuta tests
3. Deploy automático a staging

### Production
1. Merge a branch `main`
2. CI/CD ejecuta tests completos
3. Deploy manual tras aprobación

---

## Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [flake8](https://flake8.pycqa.org/)

---

**Última actualización:** 2025-11-18
