# Makefile para Proyecto IACT
# Gestión de documentación, pruebas y desarrollo

.PHONY: help docs-install docs-build docs-serve docs-clean docs-deploy clean test vagrant-up vagrant-down vagrant-ssh validate-spec check-all generate-plan

# Variables
MKDOCS_CONFIG = docs/mkdocs.yml
SITE_DIR = site
DOCS_REQUIREMENTS = docs/requirements.txt
PYTHON = python3
PIP = pip

# Colores para output
BLUE = \033[0;34m
GREEN = \033[0;32m
YELLOW = \033[0;33m
NC = \033[0m # No Color

##@ General

help: ## Mostrar esta ayuda
	@echo ""
	@echo "$(BLUE)Comandos disponibles para proyecto IACT:$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf ""} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
	@echo ""

##@ Documentación

docs-install: ## Instalar dependencias de MkDocs
	@echo "$(BLUE)Instalando dependencias de documentación...$(NC)"
	$(PIP) install -r $(DOCS_REQUIREMENTS)
	@echo "$(GREEN)[OK] Dependencias instaladas$(NC)"

docs-build: ## Construir documentación estática
	@echo "$(BLUE)Construyendo documentación...$(NC)"
	mkdocs build -f $(MKDOCS_CONFIG)
	@echo "$(GREEN)[OK] Documentación construida en $(SITE_DIR)/$(NC)"

docs-serve: ## Servir documentación con live reload (http://127.0.0.1:8000)
	@echo "$(BLUE)Iniciando servidor de documentación...$(NC)"
	@echo "$(YELLOW)Accede a: http://127.0.0.1:8000$(NC)"
	mkdocs serve -f $(MKDOCS_CONFIG)

docs-clean: ## Limpiar archivos de documentación generados
	@echo "$(BLUE)Limpiando archivos de documentación...$(NC)"
	rm -rf $(SITE_DIR)
	@echo "$(GREEN)[OK] Archivos de documentación eliminados$(NC)"

docs-deploy: ## Desplegar documentación a GitHub Pages
	@echo "$(BLUE)Desplegando documentación a GitHub Pages...$(NC)"
	mkdocs gh-deploy -f $(MKDOCS_CONFIG)
	@echo "$(GREEN)[OK] Documentación desplegada$(NC)"
	@echo "$(YELLOW)URL: https://2-coatl.github.io/IACT---project/$(NC)"

docs-check: ## Verificar enlaces y estructura de documentación
	@echo "$(BLUE)Verificando documentación...$(NC)"
	mkdocs build -f $(MKDOCS_CONFIG) --strict
	@echo "$(GREEN)[OK] Documentación verificada$(NC)"

##@ Desarrollo

vagrant-up: ## Levantar VM Vagrant (PostgreSQL + MariaDB)
	@echo "$(BLUE)Levantando infraestructura Vagrant...$(NC)"
	vagrant up
	@echo "$(GREEN)[OK] VM levantada$(NC)"
	@echo "$(YELLOW)PostgreSQL: 127.0.0.1:15432$(NC)"
	@echo "$(YELLOW)MariaDB: 127.0.0.1:13306$(NC)"

vagrant-down: ## Apagar VM Vagrant
	@echo "$(BLUE)Apagando VM Vagrant...$(NC)"
	vagrant halt
	@echo "$(GREEN)[OK] VM apagada$(NC)"

vagrant-ssh: ## Conectar a VM Vagrant por SSH
	vagrant ssh

vagrant-destroy: ## Destruir VM Vagrant completamente
	@echo "$(YELLOW)[WARN] Esto eliminará completamente la VM$(NC)"
	@read -p "¿Continuar? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		vagrant destroy -f; \
		echo "$(GREEN)[OK] VM destruida$(NC)"; \
	else \
		echo "$(YELLOW)Cancelado$(NC)"; \
	fi

check-services: ## Verificar servicios de base de datos
	@echo "$(BLUE)Verificando servicios...$(NC)"
	./scripts/verificar_servicios.sh

##@ Spec-Driven Development

validate-spec: ## Validar especificaciones de features
	@echo "$(BLUE)Validando especificaciones...$(NC)"
	@if [ -z "$(SPEC)" ]; then \
		./scripts/dev/validate-spec.sh --all; \
	else \
		./scripts/dev/validate-spec.sh $(SPEC); \
	fi

check-all: ## Ejecutar todos los checks de calidad (pre-commit, emojis, specs)
	@echo "$(BLUE)Ejecutando todos los checks...$(NC)"
	./scripts/dev/check-all.sh

check-all-fix: ## Ejecutar checks con auto-corrección
	@echo "$(BLUE)Ejecutando checks con auto-corrección...$(NC)"
	./scripts/dev/check-all.sh --fix

generate-plan: ## Generar plan de implementación desde spec
	@if [ -z "$(SPEC)" ]; then \
		echo "$(YELLOW)Uso: make generate-plan SPEC=docs/specs/mi-feature.md$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Generando plan desde: $(SPEC)$(NC)"
	./scripts/dev/generate-plan.sh $(SPEC)

##@ Testing

test: ## Ejecutar pruebas del proyecto (cuando estén disponibles)
	@echo "$(YELLOW)[WARN] No hay tests configurados actualmente$(NC)"
	@echo "$(BLUE)Para configurar tests, crear pytest.ini y tests/$(NC)"

##@ Limpieza

clean: docs-clean ## Limpiar todos los archivos generados
	@echo "$(BLUE)Limpiando archivos generados...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)[OK] Archivos limpiados$(NC)"

##@ Instalación completa

setup: docs-install ## Configurar entorno completo del proyecto
	@echo "$(BLUE)Configurando entorno del proyecto...$(NC)"
	@echo "$(GREEN)[OK] Configuración completada$(NC)"
	@echo ""
	@echo "$(YELLOW)Próximos pasos:$(NC)"
	@echo "  1. make vagrant-up      # Levantar bases de datos"
	@echo "  2. make check-services  # Verificar conectividad"
	@echo "  3. make docs-serve      # Ver documentación"
	@echo "  4. make check-all       # Validar código antes de commit"
	@echo ""

##@ Atajos comunes

docs: docs-build ## Alias para docs-build
serve: docs-serve ## Alias para docs-serve
deploy: docs-deploy ## Alias para docs-deploy
