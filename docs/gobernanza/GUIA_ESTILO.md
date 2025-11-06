---
id: DOC-GUIA-ESTILO
tipo: guia
estado: activo
propietario: equipo-gobernanza
ultima_actualizacion: 2025-11-06
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

- ADR-010: Organizacion por Dominio
- ISO/IEC/IEEE 29148:2018
- BABOK v3
