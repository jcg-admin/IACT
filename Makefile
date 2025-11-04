# Makefile para Proyecto IACT
# Gestión de documentación, pruebas y desarrollo

.PHONY: help docs-install docs-build docs-serve docs-clean docs-deploy clean test vagrant-up vagrant-down vagrant-ssh

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
	@echo "$(GREEN)✓ Dependencias instaladas$(NC)"

docs-build: ## Construir documentación estática
	@echo "$(BLUE)Construyendo documentación...$(NC)"
	mkdocs build -f $(MKDOCS_CONFIG)
	@echo "$(GREEN)✓ Documentación construida en $(SITE_DIR)/$(NC)"

docs-serve: ## Servir documentación con live reload (http://127.0.0.1:8000)
	@echo "$(BLUE)Iniciando servidor de documentación...$(NC)"
	@echo "$(YELLOW)Accede a: http://127.0.0.1:8000$(NC)"
	mkdocs serve -f $(MKDOCS_CONFIG)

docs-clean: ## Limpiar archivos de documentación generados
	@echo "$(BLUE)Limpiando archivos de documentación...$(NC)"
	rm -rf $(SITE_DIR)
	@echo "$(GREEN)✓ Archivos de documentación eliminados$(NC)"

docs-deploy: ## Desplegar documentación a GitHub Pages
	@echo "$(BLUE)Desplegando documentación a GitHub Pages...$(NC)"
	mkdocs gh-deploy -f $(MKDOCS_CONFIG)
	@echo "$(GREEN)✓ Documentación desplegada$(NC)"
	@echo "$(YELLOW)URL: https://2-coatl.github.io/IACT---project/$(NC)"

docs-check: ## Verificar enlaces y estructura de documentación
	@echo "$(BLUE)Verificando documentación...$(NC)"
	mkdocs build -f $(MKDOCS_CONFIG) --strict
	@echo "$(GREEN)✓ Documentación verificada$(NC)"

##@ Desarrollo

vagrant-up: ## Levantar VM Vagrant (PostgreSQL + MariaDB)
	@echo "$(BLUE)Levantando infraestructura Vagrant...$(NC)"
	vagrant up
	@echo "$(GREEN)✓ VM levantada$(NC)"
	@echo "$(YELLOW)PostgreSQL: 127.0.0.1:15432$(NC)"
	@echo "$(YELLOW)MariaDB: 127.0.0.1:13306$(NC)"

vagrant-down: ## Apagar VM Vagrant
	@echo "$(BLUE)Apagando VM Vagrant...$(NC)"
	vagrant halt
	@echo "$(GREEN)✓ VM apagada$(NC)"

vagrant-ssh: ## Conectar a VM Vagrant por SSH
	vagrant ssh

vagrant-destroy: ## Destruir VM Vagrant completamente
	@echo "$(YELLOW)⚠️  Esto eliminará completamente la VM$(NC)"
	@read -p "¿Continuar? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		vagrant destroy -f; \
		echo "$(GREEN)✓ VM destruida$(NC)"; \
	else \
		echo "$(YELLOW)Cancelado$(NC)"; \
	fi

check-services: ## Verificar servicios de base de datos
	@echo "$(BLUE)Verificando servicios...$(NC)"
	./scripts/verificar_servicios.sh

##@ Testing

test: ## Ejecutar pruebas del proyecto (cuando estén disponibles)
	@echo "$(YELLOW)⚠️  No hay tests configurados actualmente$(NC)"
	@echo "$(BLUE)Para configurar tests, crear pytest.ini y tests/$(NC)"

##@ Limpieza

clean: docs-clean ## Limpiar todos los archivos generados
	@echo "$(BLUE)Limpiando archivos generados...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Archivos limpiados$(NC)"

##@ Instalación completa

setup: docs-install ## Configurar entorno completo del proyecto
	@echo "$(BLUE)Configurando entorno del proyecto...$(NC)"
	@echo "$(GREEN)✓ Configuración completada$(NC)"
	@echo ""
	@echo "$(YELLOW)Próximos pasos:$(NC)"
	@echo "  1. make vagrant-up      # Levantar bases de datos"
	@echo "  2. make check-services  # Verificar conectividad"
	@echo "  3. make docs-serve      # Ver documentación"
	@echo ""

##@ Atajos comunes

docs: docs-build ## Alias para docs-build
serve: docs-serve ## Alias para docs-serve
deploy: docs-deploy ## Alias para docs-deploy
