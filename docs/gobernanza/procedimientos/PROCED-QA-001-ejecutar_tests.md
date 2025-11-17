---
id: PROCED-QA-001
tipo: procedimiento
categoria: qa
subcategoria: testing
version: 1.0.0
fecha_creacion: 2025-11-17
autor: Claude Code (Sonnet 4.5)
estado: activo
relacionados: ["PROC-QA-001", "PROC-QA-002", "PROCED-DEV-001"]
---

# PROCED-QA-001: Ejecutar Tests

## Objetivo

Proporcionar instrucciones paso a paso para ejecutar la suite completa de tests del proyecto IACT, interpretar resultados y generar reportes de coverage.

## Alcance

Este procedimiento cubre:
- Ejecución de tests unitarios
- Ejecución de tests de integración
- Generación de reportes de coverage
- Interpretación de resultados
- Resolución de problemas comunes

NO cubre:
- Escritura de nuevos tests
- Configuración inicial del entorno de testing
- CI/CD pipelines

## Pre-requisitos

- Entorno de desarrollo configurado
- Dependencias instaladas
- Base de datos de test disponible (si aplica)
- Variables de entorno configuradas

## Roles y Responsabilidades

- **Developer**: Ejecuta tests antes de PR
- **QA Engineer**: Ejecuta suite completa y valida coverage
- **CI/CD**: Ejecuta automáticamente en cada push

## Procedimiento Detallado

### PASO 1: Preparación del Entorno

#### 1.1 Verificar dependencias instaladas

**Para Python/Django**:
```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Verificar pytest instalado
pytest --version
# Output esperado: pytest 7.x.x
```

**Para JavaScript/Node**:
```bash
# Verificar jest/mocha instalado
npm test -- --version
# Output esperado: jest 29.x.x
```

#### 1.2 Configurar variables de entorno de test

```bash
# Copiar archivo de configuración de test
cp .env.test.example .env.test

# O exportar variables manualmente
export DJANGO_SETTINGS_MODULE=config.settings.test
export DATABASE_URL=sqlite:///test.db
```

#### 1.3 Preparar base de datos de test

**Para Django**:
```bash
# Crear base de datos de test
python manage.py migrate --settings=config.settings.test

# Cargar fixtures si es necesario
python manage.py loaddata test_fixtures.json
```

**Criterio de éxito**: Comandos ejecutan sin errores

---

### PASO 2: Ejecutar Tests Unitarios

#### 2.1 Ejecutar TODOS los tests

**Python/pytest**:
```bash
# Ejecutar toda la suite
pytest

# Con output más verboso
pytest -v

# Mostrar print statements
pytest -s
```

**JavaScript/Jest**:
```bash
# Ejecutar todos los tests
npm test

# O directamente
jest
```

**Output esperado**:
```
======================== test session starts ========================
collected 156 items

tests/test_auth.py ........                                   [  5%]
tests/test_permissions.py ................                    [ 15%]
tests/test_models.py ......................                   [ 29%]
...

===================== 156 passed in 12.34s ======================
```

#### 2.2 Ejecutar tests de un módulo específico

```bash
# Python - Solo tests de autenticación
pytest tests/test_auth.py

# JavaScript - Solo tests de un archivo
jest tests/auth.test.js
```

#### 2.3 Ejecutar un test específico

```bash
# Python - Test específico por nombre
pytest tests/test_auth.py::test_login_success

# Python - Tests que coincidan con patrón
pytest -k "login"

# JavaScript - Test específico
jest -t "should login successfully"
```

---

### PASO 3: Ejecutar Tests de Integración

Los tests de integración requieren servicios externos (BD, cache, etc.)

#### 3.1 Iniciar servicios necesarios

```bash
# Usando Docker Compose
docker-compose -f docker-compose.test.yml up -d

# Verificar servicios activos
docker-compose ps
```

#### 3.2 Ejecutar suite de integración

```bash
# Python - Tests marcados como integration
pytest -m integration

# JavaScript - Tests en carpeta de integración
jest --testPathPattern=integration
```

**Criterio de éxito**: Todos los tests pasan

---

### PASO 4: Generar Reporte de Coverage

#### 4.1 Ejecutar tests con coverage

**Python**:
```bash
# Generar coverage en terminal
pytest --cov=src --cov-report=term

# Generar reporte HTML
pytest --cov=src --cov-report=html

# Generar reporte XML (para CI/CD)
pytest --cov=src --cov-report=xml
```

**JavaScript**:
```bash
# Jest incluye coverage por defecto
npm test -- --coverage

# O en package.json
npm run test:coverage
```

#### 4.2 Interpretar reporte de coverage

**Output en terminal**:
```
Name                      Stmts   Miss  Cover
---------------------------------------------
src/auth/service.py          45      3    93%
src/auth/middleware.py       32      0   100%
src/permissions/models.py    67      8    88%
src/permissions/utils.py     23      2    91%
---------------------------------------------
TOTAL                       167     13    92%
```

**Criterios de calidad**:
- ✅ **Excelente**: >= 90% coverage
- ⚠️ **Aceptable**: >= 80% coverage
- ❌ **Insuficiente**: < 80% coverage

#### 4.3 Revisar reporte HTML detallado

```bash
# Abrir reporte HTML
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

En el reporte HTML, identificar:
- 🔴 **Líneas no cubiertas** (rojo)
- 🟡 **Líneas parcialmente cubiertas** (amarillo)
- 🟢 **Líneas cubiertas** (verde)

---

### PASO 5: Analizar Resultados

#### 5.1 Tests que pasan ✅

Si todos los tests pasan:
```
===================== 156 passed in 12.34s ======================
```

**Acción**: Proceder con confianza (PR ready)

---

#### 5.2 Tests que fallan ❌

**Output de fallo**:
```
FAILED tests/test_auth.py::test_login_invalid_credentials - AssertionError
```

**Pasos de análisis**:

1. **Leer el traceback completo**:
```python
def test_login_invalid_credentials():
    response = client.post('/api/auth/login', {
        'username': 'user',
        'password': 'wrongpass'
    })
>   assert response.status_code == 401
E   AssertionError: assert 500 == 401
```

2. **Identificar el problema**:
   - Status code esperado: 401 (Unauthorized)
   - Status code recibido: 500 (Server Error)
   - Hay un error interno, no solo credenciales incorrectas

3. **Ejecutar test en modo debug**:
```bash
# Python - Con pdb
pytest --pdb tests/test_auth.py::test_login_invalid_credentials

# O agregar breakpoint en el test
import pdb; pdb.set_trace()
```

4. **Revisar logs de aplicación**:
```bash
# Ver logs detallados
pytest -s tests/test_auth.py::test_login_invalid_credentials
```

---

#### 5.3 Tests que se saltean (skipped) ⚠️

**Output**:
```
tests/test_external_api.py::test_api_call SKIPPED (requires network)
```

**Acciones**:
- Verificar por qué está skipped (decorador `@pytest.mark.skip`)
- Asegurar que tests críticos NO estén skipped sin razón
- Ejecutar tests skipped cuando sea posible:
```bash
pytest --run-skip-reason="requires network"
```

---

### PASO 6: Generar Reporte de Resultados

#### 6.1 Reporte en formato JUnit (para CI/CD)

```bash
# Python
pytest --junitxml=test-results.xml

# JavaScript
jest --reporters=jest-junit
```

#### 6.2 Reporte HTML completo

```bash
# Usando pytest-html
pytest --html=report.html --self-contained-html
```

#### 6.3 Reporte para QA

Crear reporte manual con:

```markdown
# Test Execution Report

**Fecha**: 2025-11-17
**Ejecutado por**: [Tu nombre]
**Branch**: feature/user-authentication
**Commit**: abc1234

## Resumen

- **Total tests**: 156
- **Passed**: 153 (98%)
- **Failed**: 3 (2%)
- **Skipped**: 0
- **Coverage**: 92%

## Tests Fallidos

### 1. test_login_invalid_credentials
- **Archivo**: tests/test_auth.py:42
- **Razón**: Server error (500) en lugar de Unauthorized (401)
- **Acción**: Investigar error en auth service

### 2. test_permission_check
- **Archivo**: tests/test_permissions.py:78
- **Razón**: Assertion failed - expected True, got False
- **Acción**: Revisar lógica de permissions

### 3. test_token_refresh
- **Archivo**: tests/test_auth.py:89
- **Razón**: Token expirado antes de tiempo
- **Acción**: Ajustar timing en test

## Coverage por Módulo

| Módulo | Coverage | Status |
|--------|----------|--------|
| auth | 95% | ✅ |
| permissions | 88% | ✅ |
| models | 92% | ✅ |
| utils | 75% | ⚠️ |

## Recomendaciones

1. Aumentar coverage de módulo utils (target: 80%)
2. Corregir 3 tests fallidos antes de merge
3. Agregar tests para edge cases de token refresh
```

---

### PASO 7: Acciones Post-Ejecución

#### 7.1 Si todos los tests pasan

1. ✅ Commit cambios
2. ✅ Push a branch
3. ✅ Crear o actualizar PR

#### 7.2 Si hay tests fallidos

1. ❌ NO hacer commit hasta corregir
2. 🔍 Investigar y corregir fallos
3. 🔄 Re-ejecutar tests
4. ✅ Commit solo cuando TODO pase

#### 7.3 Si coverage es insuficiente

1. 📊 Identificar módulos con bajo coverage
2. ✍️ Escribir tests adicionales
3. 🔄 Re-ejecutar con coverage
4. ✅ Commit cuando coverage >= 80%

---

## Problemas Comunes y Soluciones

### Problema 1: "ModuleNotFoundError"

**Error**:
```
ModuleNotFoundError: No module named 'pytest'
```

**Solución**:
```bash
# Instalar dependencias de test
pip install -r requirements-test.txt

# O instalar pytest directamente
pip install pytest pytest-cov pytest-django
```

---

### Problema 2: Tests pasan localmente pero fallan en CI

**Causas comunes**:
- Diferentes versiones de dependencias
- Tests dependientes de orden de ejecución
- Tests que dependen de datos locales
- Timezone o locale differences

**Solución**:
```bash
# Ejecutar en modo aleatorio para detectar dependencias
pytest --random-order

# Ejecutar con misma configuración que CI
docker run -v $(pwd):/app python:3.11 pytest
```

---

### Problema 3: Tests muy lentos

**Error**: Suite tarda > 5 minutos

**Soluciones**:

1. **Ejecutar en paralelo**:
```bash
# Python - Usando pytest-xdist
pytest -n auto  # Auto detecta cores

# JavaScript
jest --maxWorkers=4
```

2. **Identificar tests lentos**:
```bash
pytest --durations=10  # Muestra 10 tests más lentos
```

3. **Optimizar tests lentos**:
   - Usar fixtures compartidos
   - Mock servicios externos
   - Reducir datos de test

---

### Problema 4: Database locked

**Error**: `sqlite3.OperationalError: database is locked`

**Solución**:
```bash
# Usar base de datos en memoria para tests
export DATABASE_URL=sqlite:///:memory:

# O usar PostgreSQL de test
export DATABASE_URL=postgresql://user:pass@localhost/test_db
```

---

## Comandos Rápidos de Referencia

```bash
# Ejecutar todo
pytest

# Solo un archivo
pytest tests/test_auth.py

# Solo un test
pytest tests/test_auth.py::test_login

# Con coverage
pytest --cov=src

# En paralelo
pytest -n auto

# Modo verboso
pytest -v

# Con prints
pytest -s

# Solo tests que fallaron la última vez
pytest --lf

# Detener al primer fallo
pytest -x
```

---

## Métricas de Calidad

Monitorear:
- **Total de tests**: Debe crecer con el proyecto
- **Tiempo de ejecución**: Idealmente < 2 minutos
- **Coverage**: >= 80% mínimo
- **Flaky tests**: Identificar tests intermitentes
- **Tasa de fallos**: < 5% aceptable

---

## Referencias

- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [PROC-QA-002: Estrategia QA](../procesos/PROC-QA-002-estrategia_qa.md)

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2025-11-17 | Claude Code | Versión inicial |

## Aprobación

- **Autor**: Claude Code (Sonnet 4.5)
- **Revisado por**: Pendiente
- **Aprobado por**: Pendiente
- **Fecha de próxima revisión**: 2026-02-17
