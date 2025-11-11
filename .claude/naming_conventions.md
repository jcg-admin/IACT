# Clean Code Naming Conventions - Quick Reference

**Fuente oficial:** `docs/gobernanza/GUIA_ESTILO.md`

## TL;DR - Checklist Rapido

Antes de nombrar algo, verificar:

- [ ] **Revela intencion?** (no requiere comentario)
- [ ] **Es preciso?** (no desinforma)
- [ ] **Cada palabra aporta valor?** (sin "info", "data", "stuff")
- [ ] **Es pronunciable?** (se puede decir en voz alta)
- [ ] **Es buscable?** (terminos unicos y especificos)
- [ ] **Sin codificaciones?** (sin notacion hungara)
- [ ] **Sin traduccion mental?** (directamente comprensible)
- [ ] **Consistente?** (misma palabra por concepto)
- [ ] **Revela intencion?** (WHAT, no HOW)

---

## Principios Fundamentales

### 1. Nombres que Revelen Intenciones

```bash
# MALO
workflow_007.md

# BUENO
workflow-implement-feature-with-tdd.md
```

### 2. Evitar Desinformacion

```python
# MALO
accountList = {}  # No es una List!

# BUENO
account_by_id = {}
```

### 3. Distinciones con Sentido

```bash
# MALO - palabras sin valor
user-info.py
config-data.json

# BUENO - cada palabra aporta
user-profile.py
database-configuration.json
```

### 4. Nombres Pronunciables

```python
# MALO
gen_ymdhms = datetime.now()

# BUENO
generation_timestamp = datetime.now()
```

### 5. Nombres Buscables

```bash
# MALO
t.sh
v.json

# BUENO
test-git-pre-commit.sh
validate-hardware-requirements.json
```

### 6. Evitar Codificaciones

```python
# MALO - Hungarian Notation
str_name = "John"
int_count = 5

# BUENO - Type hints
name: str = "John"
count: int = 5
```

### 7. Sin Traduccion Mental

```bash
# MALO
workflow_t003.md  # Que es T003?

# BUENO
workflow-implement-authentication.md
```

### 8. Una Palabra por Concepto

```bash
# MALO - inconsistente
validate-permissions.sh
check-hardware.sh
verify-network.sh

# BUENO - consistente
validate-permissions.sh
validate-hardware-requirements.sh
validate-network-configuration.sh
```

### 9. Architecture Reveals Intent

```bash
# MALO - revela HOW (numeracion, frameworks)
workflow_007_feature.md
epic_456_authentication.md

# BUENO - revela WHAT (proposito)
workflow-implement-feature-with-tdd.md
guide-authentication-with-2fa.md
```

---

## Vocabulario Consistente del Proyecto

### Verbos por Accion

| Accion | Verbo Estandar | Ejemplo |
|--------|----------------|---------|
| Validacion | `validate-*` | `validate-permissions.sh` |
| Configuracion | `setup-*` | `setup-database-schema.sh` |
| Pruebas | `test-*` | `test-git-pre-commit.sh` |
| Limpieza | `cleanup-*` | `cleanup-temp-files.sh` |
| Procesamiento | `process-*` | `process-user-authentication.sh` |
| Obtencion | `retrieve-*` | `retrieve-user-profile.py` |
| Creacion | `create-*` | `create-django-application.sh` |
| Actualizacion | `update-*` | `update-database-schema.sh` |
| Eliminacion | `delete-*` | `delete-expired-sessions.sh` |

### Sustantivos Comunes

| Concepto | Nombre Estandar | Evitar |
|----------|-----------------|--------|
| Configuracion | `*-configuration.json` | `*-config.json`, `*-cfg.json` |
| Perfil | `*-profile.py` | `*-info.py`, `*-data.py` |
| Requisitos | `*-requirements.txt` | `*-reqs.txt`, `*-deps.txt` |
| Autenticacion | `*-authentication.py` | `*-auth.py` (OK en contexto obvio) |
| Documentacion | `*-documentation.md` | `*-docs.md`, `*-doc.md` |

---

## Patrones de Naming por Tipo

### Scripts Python

```bash
# Patron: {verbo}-{sustantivo}-{contexto}.py
validate-hardware-requirements.py
process-user-authentication.py
retrieve-user-profile.py
```

### Scripts Bash

```bash
# Patron: {verbo}-{sustantivo}-{contexto}.sh
test-git-pre-commit.sh
setup-database-schema.sh
cleanup-temporary-files.sh
```

### Archivos de Configuracion

```bash
# Patron: {componente}-configuration.{ext}
database-configuration.json
network-configuration.yaml
application-settings.ini
```

### Workflows

```bash
# Patron: workflow-{verbo}-{sustantivo}-with-{metodo}.md
workflow-implement-feature-with-tdd.md
workflow-deploy-application-to-production.md
workflow-create-django-application.md
```

### Funciones Python

```python
# Patron: {verbo}_{sustantivo}_{contexto}
def validate_user_permissions(user_id: int, permission: str) -> bool:
    pass

def process_authentication_request(credentials: Dict) -> AuthResult:
    pass

def retrieve_user_profile(user_id: int) -> UserProfile:
    pass
```

### Variables

```python
# Patron: {adjetivo}_{sustantivo} o {sustantivo}_{contexto}
current_timestamp = datetime.now()
authenticated_user = get_user()
database_configuration = load_config()
is_user_valid = validate_user()
has_permission = check_permission()
```

### Constantes

```python
# Patron: SCREAMING_SNAKE_CASE
DATABASE_CONNECTION_TIMEOUT = 30
MAXIMUM_RETRY_ATTEMPTS = 3
DEFAULT_USER_ROLE = "viewer"
```

---

## Ejemplos Malos vs Buenos

### Archivos

```bash
# MALO
wf_001.md
proc_usr.sh
cfg.json
t.py

# BUENO
workflow-create-django-application.md
process-user-authentication.sh
database-configuration.json
test-permission-validation.py
```

### Funciones

```python
# MALO
def proc(d):
    pass

def get_data(id):
    pass

def chk_usr(u):
    pass

# BUENO
def process_user_authentication(user_data: Dict) -> bool:
    pass

def retrieve_user_profile(user_id: int) -> UserProfile:
    pass

def validate_user_permissions(user: User) -> bool:
    pass
```

### Variables

```python
# MALO
t = datetime.now()
usr = get_user()
cfg = load()
d = {"key": "value"}
lst = []

# BUENO
current_timestamp = datetime.now()
authenticated_user = get_user()
application_configuration = load()
user_preferences = {"key": "value"}
active_sessions = []
```

---

## Casos Especiales del Proyecto IACT

### Restriccion: Sin Emojis

```markdown
# MALO
# Features Implementadas
- Autenticacion de usuarios
- Sistema de permisos

# BUENO (sin emojis)
# Features Implementadas
- Autenticacion de usuarios
- Sistema de permisos
```

### Convencion: Guiones vs Underscores

```bash
# Archivos: Preferir guiones (-)
workflow-implement-feature.md
validate-permissions.sh

# Python: Underscores segun PEP 8
def validate_user_permissions():
    pass

user_profile = get_profile()
```

### Convencion: README en Mayusculas

```bash
# CORRECTO
README.md

# INCORRECTO
readme.md
Readme.md
```

---

## Como Aplicar

### Durante Code Review

1. Verificar checklist de naming en cada archivo nuevo
2. Sugerir rename si viola principios
3. Validar consistencia con vocabulario establecido
4. Asegurar que nombres revelan intencion (WHAT, no HOW)

### Durante Desarrollo

1. Nombrar pensando en el lector, no en el escritor
2. Si necesitas comentario para explicar nombre, el nombre esta mal
3. Buscar nombres existentes similares para mantener consistencia
4. Preguntar: "Alguien nuevo entendera esto sin contexto?"

### Refactoring

1. Identificar nombres que violan principios
2. Renombrar usando buscar/reemplazar
3. Actualizar tests y documentacion
4. Commit con mensaje: `refactor: rename {old} to {new} for clarity`

---

**Recuerda:** La guia completa esta en `docs/gobernanza/GUIA_ESTILO.md`

**Referencia:** Robert Martin - Clean Code (2008)
