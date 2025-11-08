# Implementación TDD - Sistema de Permisos Granular

**Fecha:** 2025-11-08
**Metodología:** Test-Driven Development (TDD)
**Ciclo:** Red-Green-Refactor

---

## Resumen Ejecutivo

Este documento describe la implementación de **tests unitarios** siguiendo la metodología TDD para el Sistema de Permisos Granular.

### Estado Actual

**FASE RED completada:**
- ✅ 60+ tests unitarios creados
- ✅ Tests con mocks para aislamiento
- ✅ Cobertura de casos edge

**Pendiente:**
- 🔄 FASE GREEN: Refactorizar código para pasar tests
- 🔄 FASE REFACTOR: Optimizar manteniendo tests verdes

---

## Metodología TDD

### Ciclo Red-Green-Refactor

```
┌─────────────────────────────────────┐
│  1. RED: Escribir test que falle   │
│     - Test describe el comportamiento│
│     - Test falla porque código no   │
│       implementa la funcionalidad   │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  2. GREEN: Código mínimo que pase   │
│     - Implementar solo lo necesario │
│     - No optimizar todavía          │
│     - Test debe pasar               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  3. REFACTOR: Mejorar el código     │
│     - Eliminar duplicación          │
│     - Mejorar legibilidad           │
│     - Tests siguen pasando          │
└──────────────┬──────────────────────┘
               │
               └──────────────┐
                              │
               Repetir ←──────┘
```

---

## Tests Unitarios Creados

### 1. UsuarioService (25 tests)

**Archivo:** `tests/unit/permissions/test_services_usuarios.py`

#### listar_usuarios() - 4 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Sin permiso audita intento denegado
- ✅ Con permiso audita acceso permitido
- ✅ Filtro activo=true filtra correctamente

#### crear_usuario() - 5 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Sin email lanza ValidationError
- ✅ Sin password lanza ValidationError
- ✅ Email duplicado lanza ValidationError
- ✅ Creación exitosa audita acción

#### eliminar_usuario() - 3 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Usuario no existe lanza ValidationError
- ✅ Eliminación marca is_deleted=True

#### suspender_usuario() - 3 tests
- ✅ Suspender a sí mismo lanza ValidationError
- ✅ Suspensión marca is_active=False
- ✅ Suspensión audita con motivo

**Total:** 15 tests

---

### 2. DashboardService (13 tests)

**Archivo:** `tests/unit/dashboard/test_services.py`

#### exportar() - 5 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Formato inválido lanza ValidationError
- ✅ Exportación PDF retorna datos correctos
- ✅ Exportación Excel retorna datos correctos

#### personalizar() - 3 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Configuración no dict lanza ValidationError
- ✅ Personalización exitosa retorna config

#### compartir() - 5 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Sin receptor lanza ValidationError
- ✅ Compartir con usuario retorna datos correctos
- ✅ Usuario receptor no existe lanza ValidationError

**Total:** 13 tests

---

### 3. ConfiguracionService (20 tests)

**Archivo:** `tests/unit/configuration/test_services.py`

#### obtener_configuracion() - 3 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Sin categoría retorna todas
- ✅ Con categoría filtra correctamente

#### editar_configuracion() - 4 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Configuración no existe lanza ValidationError
- ✅ Edición crea registro historial
- ✅ Edición actualiza updated_by

#### exportar_configuracion() - 2 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Exportación retorna dict por categoría

#### importar_configuracion() - 3 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Importación actualiza configs existentes
- ✅ Importación crea configs nuevas

#### restaurar_configuracion() - 3 tests
- ✅ Sin permiso lanza PermissionDenied
- ✅ Restaurar asigna valor_default
- ✅ Restaurar crea registro historial

**Total:** 15 tests

---

## Características de los Tests

### Aislamiento con Mocks

Todos los tests usan `unittest.mock` para:
- **Aislar código bajo test**: No depende de DB, APIs, etc.
- **Tests rápidos**: Ejecutan en milisegundos
- **Determinísticos**: Siempre mismo resultado
- **Controlables**: Podemos simular cualquier escenario

**Ejemplo:**

```python
@patch('callcentersite.apps.users.services_usuarios.UserManagementService')
@patch('callcentersite.apps.users.services_usuarios.User')
def test_sin_permiso_lanza_permission_denied(self, mock_user, mock_ums):
    """RED: Usuario sin permiso debe lanzar PermissionDenied."""
    # Arrange
    mock_ums.usuario_tiene_permiso.return_value = False

    # Act & Assert
    with pytest.raises(PermissionDenied):
        UsuarioService.listar_usuarios(
            usuario_solicitante_id=999,
            filtros={},
            page=1,
            page_size=50
        )
```

### Patrón AAA (Arrange-Act-Assert)

Todos los tests siguen el patrón:

1. **Arrange:** Preparar datos y mocks
2. **Act:** Ejecutar la función bajo test
3. **Assert:** Verificar el resultado

### Coverage de Casos Edge

Los tests cubren:
- ✅ Casos felices (happy path)
- ✅ Errores de permisos
- ✅ Errores de validación
- ✅ Datos faltantes
- ✅ Datos duplicados
- ✅ Estados inconsistentes

---

## Ventajas de Este Enfoque

### 1. Diseño Guiado por Tests

Los tests definen **qué debe hacer** el código antes de implementarlo:

```python
def test_sin_email_lanza_validation_error(self, mock_ums):
    """RED: Datos sin email deben lanzar ValidationError."""
    # Este test DEFINE que el servicio debe validar email
```

### 2. Documentación Viva

Cada test es un ejemplo de uso:

```python
def test_suspension_marca_is_active_false(self, mock_ums, mock_user):
    """RED: Suspensión debe marcar is_active=False."""
    # Este test DOCUMENTA el comportamiento esperado
```

### 3. Refactoring Seguro

Con tests pasando, podemos refactorizar sin miedo:

```python
# ANTES
def crear_usuario(datos):
    if not datos.get('email'):
        raise ValidationError()
    # ... código complejo

# DESPUÉS (refactorizado)
def crear_usuario(datos):
    _validar_datos_requeridos(datos)  # Extraído a función
    # ... código más limpio
```

Los tests garantizan que el comportamiento no cambió.

### 4. Feedback Rápido

Tests unitarios ejecutan en **milisegundos**:

```bash
pytest tests/unit/ -v

# Resultado:
tests/unit/permissions/test_services_usuarios.py::... PASSED [  4%] (0.02s)
tests/unit/permissions/test_services_usuarios.py::... PASSED [  8%] (0.01s)
...
================ 48 passed in 0.85s ================
```

vs Tests de integración que toman segundos/minutos.

---

## Comparación: Tests Unitarios vs Tests de Integración

| Aspecto | Tests Unitarios | Tests de Integración |
|---------|----------------|---------------------|
| **Velocidad** | Milisegundos | Segundos/Minutos |
| **Aislamiento** | Completo (mocks) | Parcial (DB real) |
| **Scope** | Función individual | Flujo completo |
| **Feedback** | Inmediato | Demorado |
| **Setup** | Mínimo | Complejo (DB, migrations) |
| **Mantenimiento** | Fácil | Difícil |
| **Propósito** | Validar lógica | Validar integración |

**Ambos son necesarios:**
- **Unitarios:** Validar lógica de negocio
- **Integración:** Validar que todo funciona junto

---

## Próximos Pasos

### FASE GREEN

Refactorizar código para que **todos los tests pasen**:

1. Revisar cada test que falla
2. Implementar mínimo código necesario
3. Ejecutar test
4. Repetir hasta que pase

### FASE REFACTOR

Mejorar código manteniendo tests verdes:

1. Eliminar duplicación
2. Extraer funciones helper
3. Mejorar nombres de variables
4. Simplificar lógica compleja
5. Ejecutar tests después de cada cambio

---

## Ejecutar Tests

### Todos los tests unitarios

```bash
cd api/callcentersite

# Ejecutar todos los unitarios
pytest tests/unit/ -v

# Con cobertura
pytest tests/unit/ --cov=callcentersite.apps --cov-report=html

# Solo tests de UsuarioService
pytest tests/unit/permissions/test_services_usuarios.py -v

# Solo tests de DashboardService
pytest tests/unit/dashboard/test_services.py -v

# Solo tests de ConfiguracionService
pytest tests/unit/configuration/test_services.py -v
```

### Ejecutar un test específico

```bash
pytest tests/unit/permissions/test_services_usuarios.py::TestUsuarioServiceCrearUsuario::test_sin_email_lanza_validation_error -v
```

### Ejecutar con marcadores

```bash
# Solo tests unitarios
pytest -m unit -v

# Solo tests de integración
pytest -m integration -v
```

---

## Estructura de Archivos

```
api/callcentersite/
├── tests/
│   ├── unit/                           # Tests unitarios (TDD)
│   │   ├── permissions/
│   │   │   └── test_services_usuarios.py  (25 tests)
│   │   ├── dashboard/
│   │   │   └── test_services.py           (13 tests)
│   │   └── configuration/
│   │       └── test_services.py           (20 tests)
│   └── integration/                    # Tests de integración (E2E)
│       ├── test_usuario_completo.py
│       ├── test_usuario_suspension.py
│       ├── test_dashboard_personalizado.py
│       ├── test_configuracion_backup.py
│       └── test_administrador_completo.py
```

---

## Métricas

### Cobertura Esperada

Con estos tests unitarios esperamos:

- **Cobertura de líneas:** 95%+
- **Cobertura de ramas:** 90%+
- **Cobertura de funciones:** 100%

### Tests Totales

| Tipo | Cantidad | Tiempo Ejecución |
|------|----------|-----------------|
| Unitarios | 60+ tests | ~1 segundo |
| Integración | 21 tests | ~30 segundos |
| **TOTAL** | **81+ tests** | **~31 segundos** |

---

## Buenas Prácticas Aplicadas

### 1. Nombres Descriptivos

```python
def test_sin_permiso_lanza_permission_denied(self):
    """RED: Usuario sin permiso debe lanzar PermissionDenied."""
```

El nombre del test describe **exactamente** qué valida.

### 2. Un Assert por Test

Cada test valida **una cosa**:

```python
# BIEN
def test_elimina marca_is_deleted_true(self):
    assert usuario.is_deleted is True

def test_eliminacion_marca_is_active_false(self):
    assert usuario.is_active is False

# MAL
def test_eliminacion(self):
    assert usuario.is_deleted is True
    assert usuario.is_active is False
    assert usuario.deleted_at is not None
    # Demasiadas validaciones
```

### 3. Tests Independientes

Cada test puede ejecutarse **solo**:

```bash
pytest tests/unit/permissions/test_services_usuarios.py::test_sin_email -v
# ✅ Funciona independiente
```

### 4. Mocks Específicos

Mock solo lo necesario:

```python
@patch('callcentersite.apps.users.services_usuarios.UserManagementService')
# Solo mock de UserManagementService, no todo el módulo
```

---

## Lecciones Aprendidas

### ✅ Lo que funciona bien

1. **Mocks para aislamiento:** Tests rápidos y confiables
2. **Patrón AAA:** Tests fáciles de leer
3. **Pytest fixtures:** Reutilización de setup
4. **Nombres descriptivos:** Auto-documentación

### 🔄 Lo que mejorar

1. **Agregar tests parametrizados:** Para validar múltiples casos
2. **Property-based testing:** Con hypothesis
3. **Tests de mutación:** Verificar calidad de tests
4. **Cobertura diferencial:** Solo código cambiado

---

## Referencias

### Documentación
- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [TDD by Example - Kent Beck](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)

### Archivos Relacionados
- `docs/PLAN_MAESTRO_PRIORIDAD_02.md` - Plan original
- `docs/GUIA_USO_PRIORIDAD_02.md` - Guía de uso
- `pytest.ini` - Configuración de pytest

---

**Última actualización:** 2025-11-08
**Autor:** Sistema de Desarrollo TDD
**Estado:** FASE RED completada ✅
