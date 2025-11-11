---
id: DOC-GUIA-ESTILO
tipo: guia
estado: activo
propietario: equipo-gobernanza
ultima_actualizacion: 2025-01-15
---
# Guia de Estilo - Proyecto IACT

## Restricciones IACT

### 1. Sin Emojis
NO usar emojis en ningun archivo del proyecto (codigo, documentacion, commits).

### 2. Sin JavaScript para Scripts
Usar Python para todos los scripts de automatizacion. JavaScript solo para frontend (React).

### 3. Sin Redis
Sesiones almacenadas en MySQL/PostgreSQL. NO usar Redis.

### 4. Sin Email
Alertas via sistema de inbox interno. NO enviar emails.

### 5. Base de Datos IVR Read-Only
La base de datos IVR es solo lectura (cero escrituras).

### 6. ETL Batch
ETL ejecutado cada 6-12 horas. NO es tiempo real.

### 7. Nombres de Archivo
Preferir guiones bajos (_) sobre guiones (-) en nombres de archivo.

## Codigo Python

### Estilo
- PEP 8 compliance
- Type hints obligatorios
- Docstrings estilo Google

### Imports
```python
# Orden: stdlib, third-party, local
import os
from pathlib import Path

from django.db import models

from apps.core.models import BaseModel
```

## Documentacion

### Front Matter YAML
Todos los documentos markdown deben incluir front matter:

```yaml
---
id: DOC-XXX-YYY
tipo: guia|procedimiento|adr|requisito
estado: borrador|activo|archivado
propietario: equipo-xxx
ultima_actualizacion: YYYY-MM-DD
---
```

### Nomenclatura
- README siempre en mayusculas: `README.md`
- Sin emojis en documentacion
- Titulos descriptivos sin acrónimos oscuros

## Clean Code Naming Principles

### Fundamento

**Robert Martin (Clean Code)**: "En el software, los nombres son omnipresentes. Aparecen en variables, funciones, argumentos, clases y paquetes. Usamos nombres constantemente. Por ello, debemos hacerlo bien."

### 1. Usar Nombres que Revelen Intenciones

El nombre debe indicar por que existe, que hace y como se usa.

```bash
# MALO (requiere comentario)
workflow_007.md  # Workflow para implementar features con TDD

# BUENO (auto-explicativo)
workflow-implement-feature-with-tdd.md
```

**Aplicacion**: Los nombres de archivos, funciones y variables deben ser tan descriptivos que eliminen la necesidad de comentarios explicativos.

### 2. Evitar la Desinformacion

No haga referencia a conceptos que el nombre no representa.

```python
# MALO (desinformativo)
accountList = []  # No es una List, es un dict
user_data = validate_user()  # No retorna data, retorna bool

# BUENO (informativo)
account_by_id = {}
is_user_valid = validate_user()
```

**Aplicacion**: Los nombres deben ser precisos y no sugerir caracteristicas que el codigo no posee.

### 3. Realizar Distinciones con Sentido

Cada palabra en el nombre debe anadir valor semantico real.

```bash
# MALO (palabras adicionales sin sentido)
user-info.py       # "info" es palabra adicional
config-data.json   # "data" es palabra adicional
process-stuff.sh   # "stuff" es palabra adicional

# BUENO (distincion clara)
user-profile.py
network-configuration.json
validate-permissions.sh
```

**Aplicacion**: Evitar palabras como "info", "data", "stuff", "manager", "processor" a menos que aporten significado especifico.

### 4. Usar Nombres que se Puedan Pronunciar

```python
# MALO (impronunciable)
gen_ymdhms = datetime.now()  # "gen y-m-d-h-m-s"
prc_usr_dat = process_data()  # "prc usr dat"

# BUENO (pronunciable)
generation_timestamp = datetime.now()
process_user_data = process_data()
```

**Aplicacion**: La capacidad de pronunciar nombres facilita la comunicacion en equipos.

### 5. Usar Nombres que se Puedan Buscar

```bash
# MALO (dificil de buscar)
t.sh              # Imposible buscar "t"
proc.py           # Demasiado generico
v.json            # Aparece en todo el codigo

# BUENO (facil de buscar)
test-git-pre-commit.sh
validate-permissions.py
validate-hardware-requirements.json
```

**Aplicacion**: Los nombres deben ser unicos y especificos para facilitar busquedas. La longitud debe reflejar el scope de uso.

### 6. Evitar Codificaciones

```python
# MALO (codificado - Hungarian Notation)
str_name = "John"        # Prefijo de tipo innecesario
int_count = 5            # Python tiene type hints
lst_users = []           # El tipo ya es evidente

# BUENO (sin codificacion)
name: str = "John"
count: int = 5
users: List[User] = []
```

**Aplicacion**: Usar type hints en lugar de notacion hungara. Los nombres deben usar lenguaje natural.

### 7. Evitar Asignaciones Mentales

```bash
# MALO (requiere traduccion mental)
workflow_t003.md          # Que es T003?
validate_r1.sh           # Que es r1?
config_x.json            # Que es x?

# BUENO (sin traduccion mental)
workflow-implement-authentication.md
validate-network-configuration.sh
database-configuration.json
```

**Aplicacion**: Los nombres deben ser directamente comprensibles sin requerir conocimiento contextual adicional.

### 8. Una Palabra por Concepto

Mantener consistencia en el vocabulario reduce la carga cognitiva.

```bash
# MALO (inconsistente - multiples palabras para mismo concepto)
validate-permissions.sh   # validate
check-hardware.sh         # check
verify-network.sh         # verify
inspect-database.sh       # inspect

# BUENO (consistente - una palabra por concepto)
validate-permissions.sh
validate-hardware-requirements.sh
validate-network-configuration.sh
validate-database-schema.sh
```

**Aplicacion**: Elegir un verbo por accion y mantenerlo en todo el proyecto. Ejemplos:
- Validacion: `validate-*`
- Configuracion: `setup-*`
- Pruebas: `test-*`
- Limpieza: `cleanup-*`

### 9. Architecture Reveals Intent (Clean Architecture)

**Uncle Bob**: "Architecture is about intent. The architecture should tell you what it does, not how it's made."

```bash
# MALO (implementation-driven)
workflow_007_feature.md           # Revela numeracion (HOW)
epic_456_authentication.md        # Revela gestion de proyecto (HOW)

# BUENO (intent-driven)
workflow-implement-feature-with-tdd.md      # Revela proposito (WHAT)
guide-authentication-with-2fa.md            # Revela funcionalidad (WHAT)
```

**Aplicacion**: Los nombres deben revelar la intencion del negocio, no los detalles de implementacion, frameworks o sistemas de gestion.

### Ejemplos Aplicados al Proyecto

#### Archivos de Scripts

```bash
# MALO
t003.sh
validate.sh
proc_usr.sh

# BUENO
test-git-pre-commit.sh
validate-hardware-requirements.sh
process-user-authentication.sh
```

#### Archivos de Workflows

```bash
# MALO
workflow_001.md
wf_feature_impl.md
proc_007.md

# BUENO
workflow-create-django-application.md
workflow-implement-feature-with-tdd.md
workflow-deploy-to-production.md
```

#### Funciones Python

```python
# MALO
def proc_data(d):
    pass

def get_usr_info(id):
    pass

# BUENO
def process_user_authentication(user_data: Dict) -> bool:
    pass

def retrieve_user_profile(user_id: int) -> UserProfile:
    pass
```

#### Variables y Constantes

```python
# MALO
t = datetime.now()
usr = get_user()
cfg = load_config()

# BUENO
current_timestamp = datetime.now()
authenticated_user = get_user()
database_configuration = load_config()
```

### Checklist de Naming

Antes de nombrar un archivo, funcion o variable, verificar:

- [ ] Revela intencion? (no requiere comentario)
- [ ] Es preciso? (no desinforma)
- [ ] Cada palabra aporta valor? (sin "info", "data", "stuff")
- [ ] Es pronunciable? (se puede decir en voz alta)
- [ ] Es buscable? (terminos unicos y especificos)
- [ ] Sin codificaciones? (sin notacion hungara)
- [ ] Sin traduccion mental? (directamente comprensible)
- [ ] Consistente? (misma palabra por concepto)
- [ ] Revela intencion? (WHAT, no HOW)

## Git

### Commits
Formato Conventional Commits:

```
tipo(scope): descripcion breve

Detalles adicionales si son necesarios.

Refs: #123
```

Tipos: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Branches
- `main` - produccion
- `develop` - desarrollo
- `claude/*` - branches de trabajo de Claude Code

## Referencias

- ADR_010: Organizacion por Dominio
- ISO/IEC/IEEE 29148:2018
- BABOK v3
