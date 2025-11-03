---
id: RUNBOOK-POST-CREATE
estado: activo
propietario: equipo-devops
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-DEVOPS-INDEX", "RUNBOOK-VERIFY-SERVICES"]
---
# Runbook: Post-Create Setup - Vagrant

## Propósito

Ejecutar configuración inicial después de `vagrant up` para preparar el entorno de desarrollo completo.

## Cuándo Usar

- Primera vez que ejecutas `vagrant up`
- Después de `vagrant destroy` y re-creación
- Al resetear entorno de desarrollo
- Al onboardear nuevo desarrollador

## Pre-requisitos

- Vagrant VM corriendo exitosamente
- Servicios PostgreSQL y MariaDB operativos (ver [verificar_servicios](verificar_servicios.md))
- Python 3.11+ instalado en máquina host
- Git configurado con usuario y email

## Procedimiento

### 1. Verificar Vagrant VM

```bash
vagrant status
```

**Output esperado:**
```
default                   running (virtualbox)
```

**Si no está corriendo:**
```bash
vagrant up
```

### 2. Verificar Servicios de Base de Datos

```bash
./scripts/verificar_servicios.sh
```

Debe reportar que todos los servicios están operativos.

### 3. Crear Entorno Virtual Python

```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Verificar versión Python
python --version
```

**Output esperado:**
```
Python 3.11.x
```

### 4. Instalar Dependencias Python

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt

# Verificar instalación
pip list
```

**Paquetes clave que deben aparecer:**
- Django==5.x
- psycopg2-binary (PostgreSQL driver)
- mysqlclient (MariaDB driver)
- pytest
- pytest-cov

### 5. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus valores (si es necesario)
nano .env  # o vim, code, etc.
```

**Valores por defecto en `.env`:**
```bash
# PostgreSQL (Analytics)
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=15432
POSTGRES_DB=iact_analytics
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_pass

# MariaDB (IVR)
MYSQL_HOST=127.0.0.1
MYSQL_PORT=13306
MYSQL_DB=iact_ivr
MYSQL_USER=django_user
MYSQL_PASSWORD=django_pass

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Generar SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Verificar Configuración Django

```bash
python manage.py check
```

**Output esperado:**
```
System check identified no issues (0 silenced).
```

### 7. Ejecutar Migraciones

```bash
# Verificar migraciones pendientes
python manage.py showmigrations

# Aplicar migraciones
python manage.py migrate

# Verificar que aplicaron correctamente
python manage.py showmigrations | grep "\[X\]"
```

### 8. Crear Superusuario

```bash
python manage.py createsuperuser
```

**Input requerido:**
- Username: `admin` (o el que prefieras)
- Email: `admin@example.com`
- Password: (elige uno seguro)
- Password (again): (repite)

**Output esperado:**
```
Superuser created successfully.
```

### 9. Cargar Datos de Prueba (Opcional)

```bash
# Si existen fixtures
python manage.py loaddata initial_data.json

# O ejecutar script de seed
python manage.py shell < scripts/seed_database.py
```

### 10. Ejecutar Tests

```bash
# Ejecutar suite completa
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Verificar cobertura
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Output esperado:**
```
======== X passed in Y.ZZ seconds ========
Coverage: 80%+
```

### 11. Iniciar Servidor de Desarrollo

```bash
python manage.py runserver
```

**Output esperado:**
```
Django version 5.x, using settings 'project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### 12. Verificar Aplicación Funciona

**Abrir navegador:**
```
http://127.0.0.1:8000/
```

Deberías ver la página de inicio de Django o tu aplicación.

**Admin:**
```
http://127.0.0.1:8000/admin/
```

Login con el superusuario creado en paso 8.

### 13. Configurar Pre-commit Hooks (Opcional pero Recomendado)

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks
pre-commit install

# Ejecutar manualmente (primera vez)
pre-commit run --all-files
```

## Checklist de Verificación

Completa estos pasos para confirmar que setup fue exitoso:

- [ ] Vagrant VM corriendo
- [ ] PostgreSQL conectado en 127.0.0.1:15432
- [ ] MariaDB conectado en 127.0.0.1:13306
- [ ] Entorno virtual Python creado y activado
- [ ] Dependencias instaladas (`pip list` muestra paquetes)
- [ ] Archivo `.env` configurado
- [ ] `python manage.py check` pasa sin errores
- [ ] Migraciones aplicadas correctamente
- [ ] Superusuario creado
- [ ] Tests pasan (`pytest`)
- [ ] Servidor de desarrollo arranca
- [ ] Puedes acceder a http://127.0.0.1:8000/
- [ ] Puedes acceder a http://127.0.0.1:8000/admin/ y login

## Troubleshooting

### Error: "No module named 'django'"

**Causa:** Entorno virtual no activado o dependencias no instaladas.

**Solución:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: "django.db.utils.OperationalError: could not connect to server"

**Causa:** PostgreSQL no está corriendo o puerto incorrecto.

**Solución:**
```bash
./scripts/verificar_servicios.sh
```

Ver [Runbook: Verificar Servicios](verificar_servicios.md) para debugging.

### Error: "CommandError: You must set settings.ALLOWED_HOSTS"

**Causa:** `.env` no configurado o `ALLOWED_HOSTS` faltante.

**Solución:**
```bash
# En .env
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Error: "psycopg2.OperationalError: FATAL: password authentication failed"

**Causa:** Credenciales incorrectas en `.env`.

**Solución:** Verificar que `POSTGRES_PASSWORD=django_pass` (o el password correcto).

### Tests Fallan

**Revisar:**
```bash
# Ejecutar con verbose
pytest -vv

# Ejecutar test específico
pytest path/to/test_file.py::test_function_name

# Ver logs completos
pytest --log-cli-level=DEBUG
```

### Migraciones No Aplican

```bash
# Ver migraciones pendientes
python manage.py showmigrations

# Fake migrations si es necesario (desarrollo)
python manage.py migrate --fake

# Resetear DB (CUIDADO: borra datos)
python manage.py flush
python manage.py migrate
```

## Script Automatizado (Futuro)

Eventualmente se creará un script que automatice estos pasos:

```bash
#!/bin/bash
# scripts/post_create.sh

set -e

echo "🚀 Ejecutando post-create setup..."

# 1. Verificar servicios
./scripts/verificar_servicios.sh

# 2. Crear venv si no existe
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# 3. Activar venv e instalar deps
source .venv/bin/activate
pip install -r requirements.txt

# 4. Configurar .env si no existe
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# 5. Migrar
python manage.py migrate

# 6. Crear superuser (no-interactive)
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
EOF

# 7. Ejecutar tests
pytest

echo "✅ Setup completado!"
```

## Tiempo Estimado

- Desarrollador experimentado: ~15 minutos
- Nuevo en el proyecto: ~30 minutos
- Primera vez con Django: ~1 hora

## Próximos Pasos

Una vez completado el setup:

1. Leer [README.md](../../../readme.md) para contexto del proyecto
2. Revisar [Arquitectura](../../arquitectura/readme.md) para entender diseño
3. Revisar [Lineamientos de Código](../../arquitectura/lineamientos_codigo.md)
4. Explorar código en tu editor favorito
5. Hacer tu primer cambio y PR

## Referencias

- [README principal](../../../readme.md)
- [Runbook: Verificar Servicios](verificar_servicios.md)
- [Vagrantfile](../../../vagrantfile)
- [Requirements.txt](../../../requirements.txt)

## Changelog

- 2025-11-02: Creación inicial del runbook
