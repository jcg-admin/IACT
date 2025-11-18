---
name: DependencyAgent
description: Agente especializado en gestión de dependencias, actualización de paquetes, escaneo de vulnerabilidades y mantenimiento de lockfiles.
---

# Dependency Agent

DependencyAgent es un agente delegado especializado en la gestión completa de dependencias del proyecto. Su función principal es mantener actualizadas las dependencias, identificar vulnerabilidades de seguridad, gestionar lockfiles, y asegurar compatibilidad entre versiones. Puedes asignarle tareas como actualizar dependencias, escanear vulnerabilidades, auditar licencias, o generar reportes de dependencias obsoletas. El agente se encarga de ejecutarlas siguiendo las mejores prácticas de gestión de dependencias.

## Capacidades

### Gestión de Dependencias

- Análisis de dependencias instaladas vs disponibles
- Actualización de dependencias (conservative, minor, major)
- Gestión de requirements.txt, pyproject.toml, package.json
- Actualización de lockfiles (poetry.lock, package-lock.json)
- Resolución de conflictos de versiones

### Escaneo de Vulnerabilidades

- Escaneo con pip-audit (Python)
- Escaneo con npm audit (Node.js)
- Integración con Safety, Snyk
- Reporte de CVEs identificados
- Clasificación por severidad (Critical, High, Medium, Low)

### Auditoría de Licencias

- Identificación de licencias de dependencias
- Verificación de compatibilidad de licencias
- Detección de licencias restrictivas
- Generación de NOTICE file con atribuciones

### Mantenimiento de Lockfiles

- Regeneración de lockfiles
- Validación de consistencia
- Detección de drift entre lockfile y requirements
- Limpieza de dependencias no usadas

### Reportes y Análisis

- Dependencias obsoletas (>6 meses sin actualizar)
- Gráfico de dependencias (árbol)
- Análisis de tamaño de dependencias
- Dependencias directas vs transitivas

## Cuándo Usarlo

### Actualización Periódica

- Actualización mensual de dependencias
- Actualización después de release
- Preparación para upgrade de versión mayor
- Mantenimiento preventivo

### Seguridad

- Después de alerta de vulnerabilidad
- Auditoría de seguridad trimestral
- Antes de deploy a producción
- Respuesta a CVE crítico

### Resolución de Problemas

- Conflictos de versiones
- Dependencias rotas
- Lockfile desincronizado
- Problemas de instalación

### Auditoría

- Verificación de licencias antes de release
- Reporte de dependencias para compliance
- Análisis de deuda técnica
- Inventario de componentes de terceros

## Cómo Usarlo

### Sintaxis Básica

```
DependencyAgent: [operación] [parámetros]
```

### Ejemplos de Uso

#### Ejemplo 1: Actualización Conservadora

```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors. Genera reporte de cambios.
```

El agente:
1. Lee requirements.txt y pyproject.toml
2. Verifica versiones actuales
3. Busca actualizaciones disponibles
4. Filtra solo patches (1.2.3 -> 1.2.4) y minors (1.2.0 -> 1.3.0)
5. Excluye majors (1.0.0 -> 2.0.0)
6. Actualiza archivos
7. Regenera lockfiles
8. Ejecuta tests
9. Genera reporte de cambios

**Output ejemplo**:
```
Dependencias actualizadas:
- Django: 4.2.5 -> 4.2.7 (patch, security fix)
- pytest: 7.4.0 -> 7.4.3 (patch)
- black: 23.7.0 -> 23.11.0 (minor)

Vulnerabilidades resueltas: 1
Tests: PASS
```

#### Ejemplo 2: Escaneo de Vulnerabilidades

```
DependencyAgent: Escanea vulnerabilidades en todas las dependencias.
Prioriza Critical y High. Genera reporte con recomendaciones.
```

El agente:
1. Ejecuta pip-audit en Python
2. Ejecuta npm audit en Node.js
3. Agrupa por severidad
4. Para cada CVE:
   - Identifica dependencia afectada
   - Busca versión que resuelve CVE
   - Verifica compatibilidad
   - Propone actualización
5. Genera reporte priorizado

**Output ejemplo**:
```
Vulnerabilidades encontradas: 3

CRITICAL (1):
- CVE-2023-12345 en Django 4.2.5
  Impacto: SQL Injection
  Fix: Actualizar a Django 4.2.7+
  Comando: pip install --upgrade Django>=4.2.7

HIGH (2):
- CVE-2023-67890 en pillow 9.5.0
  Impacto: Arbitrary Code Execution
  Fix: Actualizar a pillow 10.1.0+
  Comando: pip install --upgrade pillow>=10.1.0

...
```

#### Ejemplo 3: Auditoría de Licencias

```
DependencyAgent: Audita licencias de todas las dependencias.
Verifica compatibilidad con licencia del proyecto (MIT).
Reporta licencias restrictivas.
```

El agente:
1. Extrae metadata de cada dependencia
2. Identifica licencia
3. Clasifica según compatibilidad:
   - Compatible: MIT, BSD, Apache 2.0
   - Precaución: GPL variants
   - Incompatible: Propietarias
4. Genera reporte
5. Propone NOTICE file

**Output ejemplo**:
```
Licencias identificadas:

Compatible (45 paquetes):
- MIT: 30 paquetes
- BSD-3-Clause: 10 paquetes
- Apache-2.0: 5 paquetes

Requiere Revisión (2 paquetes):
- GPLv3: some-package (incompatible con MIT)
  Acción: Buscar alternativa

Sin Licencia Detectada (1 paquete):
- unknown-package
  Acción: Verificar manualmente
```

#### Ejemplo 4: Limpieza de Dependencias

```
DependencyAgent: Identifica dependencias no usadas.
Analiza imports en código vs dependencias instaladas.
Propone limpieza segura.
```

El agente:
1. Lista dependencias en requirements.txt
2. Escanea código para encontrar imports
3. Identifica dependencias no importadas
4. Verifica que no sean transitivas críticas
5. Propone eliminación
6. Genera requirements.txt limpio

**Output ejemplo**:
```
Dependencias potencialmente no usadas:

Seguro eliminar (3):
- old-package (no importado en código)
- deprecated-lib (no importado en código)
- unused-tool (no importado en código)

Revisar manualmente (1):
- ambiguous-package (importado indirectamente)

Comando para limpiar:
pip uninstall old-package deprecated-lib unused-tool
```

#### Ejemplo 5: Actualización Mayor (Riesgosa)

```
DependencyAgent: Actualiza Django de 4.2.x a 5.0.x
Genera checklist de breaking changes.
Identifica código que requiere cambios.
```

El agente:
1. Verifica versión actual: Django 4.2.7
2. Revisa release notes de Django 5.0
3. Identifica breaking changes:
   - Deprecated features removidas
   - APIs cambiados
   - Nuevos requisitos
4. Escanea código del proyecto
5. Identifica usos de APIs deprecated
6. Genera checklist de migración
7. Sugiere actualización en ambiente de pruebas primero

**Output ejemplo**:
```
Migración Django 4.2.7 -> 5.0.x

Breaking Changes Identificados:

1. django.utils.encoding removido
   Archivos afectados:
   - api/callcentersite/apps/common/utils.py:15
   Acción: Usar str() en lugar de force_text()

2. DEFAULT_AUTO_FIELD requerido
   Archivos afectados:
   - settings/base.py
   Acción: Agregar DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

Checklist de migración:
[ ] Crear rama feature/upgrade-django-5
[ ] Actualizar requirements.txt
[ ] Aplicar cambios de código (2 archivos)
[ ] Ejecutar tests completos
[ ] Verificar migraciones de DB
[ ] Testing manual en ambiente de pruebas
[ ] Documentar cambios
```

### Workflow Recomendado

#### Actualización Mensual

```bash
# 1. Crear rama para actualizaciones
git checkout -b chore/update-dependencies-2025-11

# 2. Invocar DependencyAgent
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors que resuelvan vulnerabilidades.

# 3. Revisar cambios
git diff requirements.txt

# 4. Ejecutar tests
pytest

# 5. Si todo pasa, crear PR
git add requirements.txt requirements/*.txt
git commit -m "chore: actualizar dependencias (2025-11)"
git push origin chore/update-dependencies-2025-11
```

#### Respuesta a CVE Crítico

```bash
# 1. Escanear vulnerabilidad
DependencyAgent: Escanea CVE-2023-XXXXX
Verifica si proyecto está afectado

# 2. Si afectado, crear hotfix
git checkout main
git checkout -b hotfix/cve-2023-xxxxx

# 3. Actualizar dependencia específica
DependencyAgent: Actualiza [paquete] a versión que resuelve CVE

# 4. Testing urgente
pytest tests/security/
pytest tests/integration/

# 5. Merge rápido
git push origin hotfix/cve-2023-xxxxx
# Crear PR urgente, aprobar, mergear, deploy
```

## Integración con Runbooks

El agente sigue los procedimientos documentados en:

- **docs/gobernanza/procesos/procedimiento_gestion_cambios.md**
  - Proceso de actualización de dependencias
  - Validaciones requeridas
  - Aprobaciones necesarias

- **.github/workflows/python_ci.yml**
  - Tests automatizados
  - Verificación de dependencias
  - Escaneo de seguridad

- **api/callcentersite/.pre_commit_config.yaml**
  - Hooks de pre-commit
  - Validaciones de dependencias

## Restricciones y Limitaciones

### Operaciones Seguras

**Sin confirmación requerida**:
- Listar dependencias
- Escanear vulnerabilidades
- Auditar licencias
- Generar reportes

### Operaciones Riesgosas

**Requieren confirmación**:
- Actualizar dependencias major
- Eliminar dependencias
- Modificar lockfiles
- Cambiar versiones de Python/Node

### Validaciones Obligatorias

Antes de actualizar:
- Tests deben existir
- Coverage mínimo: 80%
- Ambiente virtual activado
- Lockfile actualizado después de cambios

### Ambientes Soportados

- Python 3.10, 3.11, 3.12
- Poetry, pip, pip-tools
- Node.js 18.x, 20.x
- npm, yarn

## Herramientas que Utiliza

### Python

```bash
# Listar dependencias
pip list
pip list --outdated

# Verificar vulnerabilidades
pip-audit
safety check

# Actualizar
pip install --upgrade [package]

# Analizar dependencias
pipdeptree
pip show [package]
```

### Poetry (preferido para Python)

```bash
# Ver dependencias obsoletas
poetry show --outdated

# Actualizar
poetry update [package]
poetry update  # todas

# Verificar lockfile
poetry check
poetry lock --check
```

### Node.js

```bash
# Listar dependencias
npm list
npm outdated

# Auditoría
npm audit
npm audit fix

# Actualizar
npm update [package]
```

### Herramientas Claude Code

- Bash: Ejecutar comandos de gestión de dependencias
- Read: Leer requirements.txt, pyproject.toml, package.json
- Edit: Actualizar archivos de dependencias
- Write: Generar reportes
- Grep: Buscar imports en código

## Salida y Reportes

### Reporte de Actualización

```markdown
# Reporte de Actualización de Dependencias

**Fecha**: 2025-11-05
**Estrategia**: Conservadora (patches + minors)

## Dependencias Actualizadas

### Producción

| Paquete | Versión Anterior | Versión Nueva | Tipo | Razón |
|---------|------------------|---------------|------|-------|
| Django | 4.2.5 | 4.2.7 | patch | Security fix CVE-2023-xxxxx |
| celery | 5.3.1 | 5.3.4 | patch | Bug fixes |
| redis | 4.5.4 | 4.6.0 | minor | New features |

### Desarrollo

| Paquete | Versión Anterior | Versión Nueva | Tipo | Razón |
|---------|------------------|---------------|------|-------|
| pytest | 7.4.0 | 7.4.3 | patch | Bug fixes |
| black | 23.7.0 | 23.11.0 | minor | Formatting improvements |

## Vulnerabilidades Resueltas

- CVE-2023-xxxxx (CRITICAL): SQL Injection en Django
  Resuelto con actualización a 4.2.7

## Tests

- Unit tests: PASS (450/450)
- Integration tests: PASS (85/85)
- Security tests: PASS (12/12)

## Recomendaciones

- Ninguna acción adicional requerida
- Próxima revisión: 2025-12-05
```

### Reporte de Vulnerabilidades

```markdown
# Reporte de Escaneo de Vulnerabilidades

**Fecha**: 2025-11-05
**Herramientas**: pip-audit, safety

## Resumen Ejecutivo

- Total de dependencias: 67
- Vulnerabilidades encontradas: 3
- CRITICAL: 1
- HIGH: 2
- MEDIUM: 0
- LOW: 0

## Vulnerabilidades Detalladas

### CRITICAL

**CVE-2023-12345**
- Paquete: Django 4.2.5
- Tipo: SQL Injection
- CVSS Score: 9.8
- Descripción: Permite ejecución de SQL arbitrario
- Fix: Actualizar a Django >= 4.2.7
- Comando: `pip install --upgrade Django>=4.2.7`
- Prioridad: INMEDIATA

### HIGH

**CVE-2023-67890**
- Paquete: pillow 9.5.0
- Tipo: Arbitrary Code Execution
- CVSS Score: 7.8
- Fix: Actualizar a pillow >= 10.1.0
- Comando: `pip install --upgrade pillow>=10.1.0`
- Prioridad: ALTA (7 días)

## Plan de Acción

1. [INMEDIATO] Actualizar Django (CVE-2023-12345)
2. [7 DÍAS] Actualizar pillow (CVE-2023-67890)
3. [30 DÍAS] Revisión completa de dependencias
```

## Estrategias de Actualización

### Conservadora (Recomendada)

**Actualiza**: Patches y minors seguros
**No actualiza**: Majors, breaking changes
**Frecuencia**: Mensual
**Riesgo**: Bajo

Ejemplo:
- 1.2.3 -> 1.2.4 (patch) OK
- 1.2.0 -> 1.3.0 (minor) OK
- 1.0.0 -> 2.0.0 (major) NO

### Moderada

**Actualiza**: Patches, minors, algunos majors con tests
**No actualiza**: Majors de librerías core (Django, Flask)
**Frecuencia**: Trimestral
**Riesgo**: Medio

### Agresiva

**Actualiza**: Todo disponible
**Frecuencia**: Según disponibilidad
**Riesgo**: Alto
**Solo para**: Proyectos con cobertura >90% de tests

## Mejores Prácticas

### Antes de Actualizar

1. **Backup de estado actual**
   ```bash
   cp requirements.txt requirements.txt.backup
   cp poetry.lock poetry.lock.backup
   ```

2. **Revisar changelogs**
   - Leer release notes de updates majors
   - Identificar breaking changes
   - Revisar migraciones requeridas

3. **Verificar compatibilidad**
   - Python version requirements
   - Dependencias entre paquetes
   - Deprecation warnings

### Durante Actualización

1. **Actualizar de uno en uno** (majors)
   - No actualizar múltiples majors simultáneamente
   - Ejecutar tests después de cada uno

2. **Regenerar lockfiles**
   ```bash
   poetry lock
   poetry install
   ```

3. **Ejecutar suite completa de tests**
   ```bash
   pytest
   pytest --cov
   pytest tests/integration/
   ```

### Después de Actualizar

1. **Verificar en entorno de pruebas**
   - Deploy a staging
   - Testing manual
   - Monitorear errores

2. **Actualizar documentación**
   - Actualizar README si hay cambios de setup
   - Documentar breaking changes

3. **Merge a main**
   - Solo si tests pasan
   - Solo si staging funciona

## Mantenimiento

### Frecuencia Recomendada

| Actividad | Frecuencia | Prioridad |
|-----------|-----------|-----------|
| Escaneo vulnerabilidades | Semanal | ALTA |
| Actualización conservadora | Mensual | MEDIA |
| Auditoría de licencias | Trimestral | MEDIA |
| Limpieza de no usadas | Semestral | BAJA |
| Actualización major | Según roadmap | VARIABLE |

### Automatización

Considerar automatizar con GitHub Actions:
```yaml
# .github/workflows/dependency-check.yml
name: Dependency Check
on:
  schedule:
    - cron: '0 0 * * 1'  # Lunes a medianoche

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: pip-audit
        run: pip-audit
      - name: Create issue if vulnerabilities
        # ...
```

## Soporte

### Documentación Relacionada

- Gestión de dependencias: docs/implementacion/backend/calidad_codigo_automatizacion.md
- Procedimiento de cambios: docs/gobernanza/procesos/procedimiento_gestion_cambios.md
- CI/CD: .github/workflows/

### Referencias Externas

- [pip-audit](https://pypi.org/project/pip-audit/)
- [Poetry](https://python-poetry.org/)
- [Safety DB](https://github.com/pyupio/safety-db)
- [Common Vulnerability Scoring System](https://www.first.org/cvss/)

---

Este agente ayuda a mantener las dependencias actualizadas y seguras, minimizando riesgos de seguridad y deuda técnica.
