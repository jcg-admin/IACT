# Makefile para automatización de tareas en el proyecto Django
# Uso: make <comando>

.PHONY: help install dev-install test test-fast test-coverage lint format type-check security clean migrate run shell profile benchmark pre-commit-install pre-commit-run docs

# Variables
PYTHON := python
MANAGE := $(PYTHON) manage.py
PYTEST := pytest
RUFF := ruff
MYPY := mypy
BANDIT := bandit

# Colores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Ayuda por defecto
help:
	@echo "$(GREEN)Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(YELLOW)Instalación:$(NC)"
	@echo "  make install           - Instalar dependencias de producción"
	@echo "  make dev-install       - Instalar dependencias de desarrollo"
	@echo "  make pre-commit-install - Instalar hooks de pre-commit"
	@echo ""
	@echo "$(YELLOW)Calidad de Código:$(NC)"
	@echo "  make lint              - Ejecutar linter (Ruff)"
	@echo "  make format            - Formatear código (Ruff)"
	@echo "  make type-check        - Verificar tipos (MyPy)"
	@echo "  make security          - Análisis de seguridad (Bandit)"
	@echo "  make pre-commit-run    - Ejecutar todos los pre-commit hooks"
	@echo "  make quality           - Ejecutar todas las verificaciones de calidad"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  make test              - Ejecutar todos los tests"
	@echo "  make test-fast         - Ejecutar tests en paralelo"
	@echo "  make test-coverage     - Ejecutar tests con coverage"
	@echo "  make test-watch        - Ejecutar tests en modo watch"
	@echo "  make benchmark         - Ejecutar benchmarks de rendimiento"
	@echo ""
	@echo "$(YELLOW)Django:$(NC)"
	@echo "  make migrate           - Ejecutar migraciones"
	@echo "  make migrations        - Crear nuevas migraciones"
	@echo "  make run               - Iniciar servidor de desarrollo"
	@echo "  make shell             - Abrir shell de Django"
	@echo "  make superuser         - Crear superusuario"
	@echo ""
	@echo "$(YELLOW)Performance:$(NC)"
	@echo "  make profile           - Ejecutar profiling de código"
	@echo "  make profile-snakeviz  - Profiling con visualización SnakeViz"
	@echo ""
	@echo "$(YELLOW)Utilidades:$(NC)"
	@echo "  make clean             - Limpiar archivos temporales"
	@echo "  make clean-cache       - Limpiar cache de Python"
	@echo "  make clean-all         - Limpieza completa"
	@echo "  make docs              - Generar documentación"

# ============================================
# INSTALACIÓN
# ============================================

install:
	@echo "$(GREEN)Instalando dependencias de producción...$(NC)"
	pip install -r requirements/base.txt

dev-install:
	@echo "$(GREEN)Instalando dependencias de desarrollo...$(NC)"
	pip install -r requirements/dev.txt
	pip install -r requirements/test.txt

pre-commit-install:
	@echo "$(GREEN)Instalando hooks de pre-commit...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks instalados$(NC)"

# ============================================
# CALIDAD DE CÓDIGO
# ============================================

lint:
	@echo "$(GREEN)Ejecutando Ruff linter...$(NC)"
	$(RUFF) check callcentersite

lint-fix:
	@echo "$(GREEN)Ejecutando Ruff linter con auto-fix...$(NC)"
	$(RUFF) check callcentersite --fix

format:
	@echo "$(GREEN)Formateando código con Ruff...$(NC)"
	$(RUFF) format callcentersite

format-check:
	@echo "$(GREEN)Verificando formato de código...$(NC)"
	$(RUFF) format --check callcentersite

type-check:
	@echo "$(GREEN)Verificando tipos con MyPy...$(NC)"
	$(MYPY) callcentersite --show-error-codes --pretty

security:
	@echo "$(GREEN)Ejecutando análisis de seguridad con Bandit...$(NC)"
	$(BANDIT) -r callcentersite -c pyproject.toml

security-report:
	@echo "$(GREEN)Generando reporte de seguridad...$(NC)"
	$(BANDIT) -r callcentersite -c pyproject.toml -f json -o bandit-report.json
	$(BANDIT) -r callcentersite -c pyproject.toml -f html -o bandit-report.html
	@echo "$(GREEN)✓ Reportes generados: bandit-report.json, bandit-report.html$(NC)"

safety-check:
	@echo "$(GREEN)Verificando vulnerabilidades en dependencias...$(NC)"
	safety check --json --output safety-report.json || true
	safety check

pip-audit:
	@echo "$(GREEN)Auditando dependencias con pip-audit...$(NC)"
	pip-audit --desc

pre-commit-run:
	@echo "$(GREEN)Ejecutando todos los pre-commit hooks...$(NC)"
	pre-commit run --all-files

quality: lint format-check type-check security
	@echo "$(GREEN)✓ Todas las verificaciones de calidad completadas$(NC)"

# ============================================
# TESTING
# ============================================

test:
	@echo "$(GREEN)Ejecutando tests...$(NC)"
	$(PYTEST) -v

test-fast:
	@echo "$(GREEN)Ejecutando tests en paralelo...$(NC)"
	$(PYTEST) -n auto -v

test-coverage:
	@echo "$(GREEN)Ejecutando tests con coverage...$(NC)"
	$(PYTEST) --cov=callcentersite --cov-report=html --cov-report=term-missing --cov-report=xml -v
	@echo "$(GREEN)✓ Reporte de coverage generado en htmlcov/index.html$(NC)"

test-watch:
	@echo "$(GREEN)Ejecutando tests en modo watch...$(NC)"
	ptw -- -v

test-unit:
	@echo "$(GREEN)Ejecutando tests unitarios...$(NC)"
	$(PYTEST) -m unit -v

test-integration:
	@echo "$(GREEN)Ejecutando tests de integración...$(NC)"
	$(PYTEST) -m integration -v

test-failed:
	@echo "$(GREEN)Re-ejecutando tests fallidos...$(NC)"
	$(PYTEST) --lf -v

benchmark:
	@echo "$(GREEN)Ejecutando benchmarks de rendimiento...$(NC)"
	$(PYTEST) --benchmark-only --benchmark-autosave -v

# ============================================
# DJANGO
# ============================================

migrate:
	@echo "$(GREEN)Ejecutando migraciones...$(NC)"
	$(MANAGE) migrate

migrations:
	@echo "$(GREEN)Creando nuevas migraciones...$(NC)"
	$(MANAGE) makemigrations

run:
	@echo "$(GREEN)Iniciando servidor de desarrollo...$(NC)"
	$(MANAGE) runserver

shell:
	@echo "$(GREEN)Abriendo shell de Django...$(NC)"
	$(MANAGE) shell_plus --ipython

shell-plain:
	@echo "$(GREEN)Abriendo shell de Django (plain)...$(NC)"
	$(MANAGE) shell

superuser:
	@echo "$(GREEN)Creando superusuario...$(NC)"
	$(MANAGE) createsuperuser

collectstatic:
	@echo "$(GREEN)Recolectando archivos estáticos...$(NC)"
	$(MANAGE) collectstatic --noinput

check:
	@echo "$(GREEN)Verificando configuración de Django...$(NC)"
	$(MANAGE) check

# ============================================
# PERFORMANCE
# ============================================

profile:
	@echo "$(GREEN)Ejecutando profiling de código...$(NC)"
	@echo "$(YELLOW)Ejemplo: make profile CODE='your_code_here'$(NC)"
	@if [ -z "$(CODE)" ]; then \
		echo "$(RED)Error: Especifica CODE='tu_codigo'$(NC)"; \
	else \
		$(MANAGE) profile_code --code="$(CODE)" --output=profile.prof; \
	fi

profile-snakeviz:
	@echo "$(GREEN)Abriendo SnakeViz para visualización...$(NC)"
	snakeviz profile.prof

profile-memory:
	@echo "$(GREEN)Ejecutando profiling de memoria...$(NC)"
	python -m memory_profiler your_script.py

# ============================================
# LIMPIEZA
# ============================================

clean:
	@echo "$(GREEN)Limpiando archivos temporales...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*~' -delete
	find . -type f -name '.coverage' -delete
	@echo "$(GREEN)✓ Limpieza completada$(NC)"

clean-cache:
	@echo "$(GREEN)Limpiando cache de Python...$(NC)"
	find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.mypy_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '.ruff_cache' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cache limpiado$(NC)"

clean-test:
	@echo "$(GREEN)Limpiando archivos de test...$(NC)"
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	@echo "$(GREEN)✓ Archivos de test limpiados$(NC)"

clean-all: clean clean-cache clean-test
	@echo "$(GREEN)✓ Limpieza completa realizada$(NC)"

# ============================================
# DOCUMENTACIÓN
# ============================================

docs:
	@echo "$(GREEN)Generando documentación...$(NC)"
	@echo "$(YELLOW)TODO: Configurar generación de documentación$(NC)"

# ============================================
# CI/CD
# ============================================

ci: quality test-coverage
	@echo "$(GREEN)✓ Pipeline CI completado exitosamente$(NC)"

# ============================================
# DESARROLLO
# ============================================

setup: dev-install pre-commit-install migrate
	@echo "$(GREEN)✓ Configuración de desarrollo completada$(NC)"

update:
	@echo "$(GREEN)Actualizando dependencias...$(NC)"
	pip install --upgrade -r requirements/dev.txt
	pre-commit autoupdate
	@echo "$(GREEN)✓ Dependencias actualizadas$(NC)"

# ============================================
# DOCKER (si aplica)
# ============================================

docker-build:
	@echo "$(GREEN)Construyendo imagen Docker...$(NC)"
	docker build -t callcentersite:latest .

docker-run:
	@echo "$(GREEN)Ejecutando contenedor Docker...$(NC)"
	docker run -p 8000:8000 callcentersite:latest

docker-compose-up:
	@echo "$(GREEN)Iniciando servicios con Docker Compose...$(NC)"
	docker-compose up -d

docker-compose-down:
	@echo "$(GREEN)Deteniendo servicios Docker Compose...$(NC)"
	docker-compose down
