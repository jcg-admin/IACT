---
id: PROC-DEV-LOCAL
tipo: procedimiento
categoria: desarrollo
version: 1.1.0
fecha_creacion: 2025-11-04
fecha_actualizacion: 2025-11-06
propietario: equipo-desarrollo
relacionados: ["PROC-INSTALL-ENV", "PROC-QA", "PROC-GIT-HOOKS"]
date: 2025-11-13
---
# Procedimiento: Desarrollo Local

## Propósito

Guía paso a paso para configurar y trabajar en el entorno de desarrollo local del proyecto IACT.

## Alcance

Este procedimiento aplica a todos los desarrolladores (backend, frontend, infrastructure) que necesiten trabajar localmente en el proyecto.

## Pre-requisitos

- [ ] Vagrant instalado (ver [procedimiento_instalacion_entorno.md](procedimiento_instalacion_entorno.md))
- [ ] Git configurado
- [ ] IDE/Editor de código (VS Code recomendado)
- [ ] Acceso al repositorio GitHub

## Procedimiento

### 1. Clonar el Repositorio

```bash
git clone https://github.com/2-Coatl/IACT---project.git
cd IACT---project
```

### 2. Configurar Entorno Virtual

#### Opción A: Usando Vagrant (Recomendado)

```bash
# Iniciar VM
vagrant up

# Conectar a la VM
vagrant ssh

# Dentro de la VM
cd /vagrant/api
source venv/bin/activate
```

#### Opción B: Desarrollo Directo (Sin VM)

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
cd api
pip install -r requirements/dev.txt
pip install -r requirements/test.txt
```

### 3. Configurar Base de Datos

```bash
# Dentro del entorno (VM o local)
cd api

# Aplicar migraciones
python manage.py migrate

# Cargar datos de prueba (opcional)
python manage.py loaddata fixtures/initial_data.json
```

### 4. Instalar Git Hooks

Instalar hooks de validación antes de commit y push:

```bash
# Desde la raíz del proyecto
make install-hooks

# O manualmente
./scripts/install-hooks.sh
```

Los hooks instalados realizan validaciones automáticas:
- **Pre-push**: Valida specs, secrets, emojis y tests antes de push

Verificar instalación:
```bash
./scripts/install-hooks.sh --verify
```

Para más información sobre hooks: [Git Hooks README](../.github/hooks/README.md)

### 5. Ejecutar Servidor de Desarrollo

```bash
# Iniciar servidor Django
python manage.py runserver 0.0.0.0:8000

# El servidor estará disponible en:
# http://localhost:8000 (o http://localhost:8080 si estás en Vagrant)
```

### 6. Ejecutar Tests

```bash
# Tests completos
pytest

# Tests con cobertura
pytest --cov=. --cov-report=html

# Tests específicos
pytest api/tests/test_authentication.py
```

### 7. Trabajar con Git

#### Crear Nueva Feature

```bash
# Crear rama desde main
git checkout main
git pull origin main
git checkout -b feature/nombre-descriptivo

# Hacer cambios...
git add .
git commit -m "feat: descripción del cambio"
```

#### Antes de Commit

Ejecutar checklist:

```bash
# Formatear código
black .
isort .

# Linting
pylint api/**/*.py
flake8 .

# Tests
pytest

# Ver estado
git status
git diff
```

Ver: [Checklist de Desarrollo](../checklists/checklist_desarrollo.md)

### 8. Crear Pull Request

```bash
# Push a tu rama
git push -u origin feature/nombre-descriptivo

# Crear PR en GitHub
gh pr create --title "feat: título del PR" --body "Descripción"
```

Ver: [Procedimiento de Gestión de Cambios](procedimiento_gestion_cambios.md)

## Tareas Comunes

### Actualizar Dependencias

```bash
pip install -r requirements/dev.txt --upgrade
pip freeze > requirements/dev.txt
```

### Regenerar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Acceder a Shell Django

```bash
python manage.py shell
# o para shell mejorado
python manage.py shell_plus
```

### Ver Logs

```bash
# Logs de Django
tail -f logs/django.log

# Logs de tests
tail -f logs/test.log
```

## Troubleshooting

### Problema: Puerto 8000 en uso

```bash
# Encontrar proceso
lsof -i :8000
# o
netstat -tulpn | grep 8000

# Matar proceso
kill -9 <PID>
```

### Problema: Migraciones conflictivas

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Crear migración de merge
python manage.py makemigrations --merge
```

### Problema: Vagrant no inicia

```bash
# Destruir y recrear VM
vagrant destroy -f
vagrant up

# Ver logs
vagrant up --debug
```

### Problema: Tests fallan

```bash
# Limpiar cache de pytest
pytest --cache-clear

# Recrear base de datos de test
python manage.py test --keepdb=false
```

## Herramientas Recomendadas

### VS Code Extensions

- Python
- Pylance
- Black Formatter
- Django
- GitLens
- SQLTools

### Configuración VS Code

Agregar a `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

## Recursos Relacionados

- [Procedimiento: Instalación de Entorno](procedimiento_instalacion_entorno.md)
- [Procedimiento: QA](procedimiento_qa.md)
- [Procedimiento: Gestión de Cambios](procedimiento_gestion_cambios.md)
- [Checklist de Desarrollo](../checklists/checklist_desarrollo.md)
- [Lineamientos de Código](../arquitectura/lineamientos_codigo.md)
- [Runbooks DevOps](../devops/runbooks/)

## Notas

- **Siempre** trabaja en una rama feature, nunca directamente en main
- **Ejecuta tests** antes de cada commit
- **Sigue** los lineamientos de código del proyecto
- **Documenta** cambios significativos
- **Pide ayuda** en el canal de desarrollo si te atoras

## Changelog

- 2025-11-04: Creación inicial del procedimiento
