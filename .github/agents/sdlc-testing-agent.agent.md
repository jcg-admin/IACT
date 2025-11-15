---
name: SDLCTestingAgent
description: Agente especializado en generación automática de tests unitarios, integración y E2E, casos de prueba, estrategias de testing y validación de cobertura según pirámide de tests.
---

# SDLC Testing Agent

SDLCTestingAgent es un agente Python especializado en la fase de Testing del ciclo SDLC. Su función principal es generar automáticamente tests unitarios, de integración y end-to-end, definir casos de prueba, crear estrategias de testing y validar cobertura de código según la pirámide de tests (70% unitarios, 20% integración, 10% E2E).

## Capacidades

### Generación de Tests Unitarios

- Generación automática de unit tests para funciones y métodos
- Tests parametrizados con múltiples casos
- Mocking de dependencias externas
- Fixtures y setup/teardown apropiados
- Tests de edge cases y error handling

### Tests de Integración

- Generación de integration tests para APIs
- Tests de base de datos con fixtures
- Tests de servicios externos con mocks
- Validación de contratos entre componentes
- Tests de workflows completos

### Tests End-to-End

- Generación de tests E2E con Selenium/Playwright
- Scenarios de usuario completos
- Validación de flujos críticos
- Tests de UI y navegación
- Verificación de integraciones reales

### Estrategia de Testing

- Definición de plan de testing según feature
- Identificación de casos de prueba críticos
- Cálculo de cobertura esperada
- Priorización de tests
- Estimación de esfuerzo de testing

## Cuándo Usarlo

### Durante Desarrollo

- Generación de tests para nuevo código
- TDD: generar tests antes de implementación
- Actualización de tests existentes
- Validación de refactorings

### Code Review

- Verificación de cobertura de tests
- Identificación de casos no cubiertos
- Sugerencias de mejora en tests
- Validación de calidad de tests

### CI/CD Pipeline

- Generación de tests para pipelines
- Actualización automática de test suites
- Validación de regression tests
- Optimización de tiempo de ejecución

## Cómo Usarlo

### Ejecución Básica

```bash
python scripts/coding/ai/sdlc/testing_agent.py \
  --target-module api/authentication \
  --test-type unit \
  --project-root .
```

### Generación Completa de Test Suite

```bash
python scripts/coding/ai/sdlc/testing_agent.py \
  --target-module api/notifications \
  --test-type all \
  --coverage-threshold 80 \
  --include-integration \
  --include-e2e \
  --output-dir tests/
```

### Parámetros Principales

- `--target-module`: Módulo/archivo a testear
- `--test-type`: Tipo de tests (unit, integration, e2e, all)
- `--project-root`: Directorio raíz del proyecto
- `--coverage-threshold`: Umbral mínimo de cobertura (%)
- `--framework`: Framework de testing (pytest, unittest, jest)
- `--include-fixtures`: Generar fixtures de datos
- `--mock-external`: Mockear servicios externos
- `--output-dir`: Directorio para tests generados

## Ejemplos de Uso

### Ejemplo 1: Tests Unitarios para Módulo

```bash
python scripts/coding/ai/sdlc/testing_agent.py \
  --target-module api/users/services.py \
  --test-type unit \
  --framework pytest \
  --coverage-threshold 90
```

Genera:
- test_services.py con tests para cada función
- Fixtures para objetos User
- Mocks para base de datos
- Tests parametrizados para edge cases
- Assertions completas

### Ejemplo 2: Tests de Integración para API

```bash
python scripts/coding/ai/sdlc/testing_agent.py \
  --target-module api/authentication/ \
  --test-type integration \
  --include-fixtures \
  --mock-external
```

Genera:
- Tests de endpoints REST
- Fixtures de usuarios de prueba
- Mocks para servicios OAuth
- Tests de flujo completo de autenticación
- Validación de responses y status codes

### Ejemplo 3: Test Suite Completa

```bash
python scripts/coding/ai/sdlc/testing_agent.py \
  --target-module api/payments/ \
  --test-type all \
  --coverage-threshold 85 \
  --include-e2e
```

Genera:
- Tests unitarios (70% del total)
- Tests de integración (20% del total)
- Tests E2E (10% del total)
- Estrategia de testing documentada
- Plan de cobertura

## Outputs Generados

### Tests Unitarios (pytest)

```python
# test_payment_service.py
import pytest
from unittest.mock import Mock, patch
from api.payments.service import PaymentService

class TestPaymentService:
    @pytest.fixture
    def payment_service(self):
        return PaymentService()
    
    @pytest.fixture
    def mock_payment_data(self):
        return {
            "amount": 100.50,
            "currency": "USD",
            "user_id": "user123"
        }
    
    def test_process_payment_success(self, payment_service, mock_payment_data):
        # Given
        with patch('api.payments.gateway.charge') as mock_charge:
            mock_charge.return_value = {"status": "success"}
            
            # When
            result = payment_service.process(mock_payment_data)
            
            # Then
            assert result["status"] == "success"
            mock_charge.assert_called_once()
    
    @pytest.mark.parametrize("amount,expected", [
        (0, "invalid_amount"),
        (-10, "invalid_amount"),
        (1000000, "amount_exceeded")
    ])
    def test_process_payment_validation(self, payment_service, amount, expected):
        with pytest.raises(ValueError, match=expected):
            payment_service.process({"amount": amount})
```

### Tests de Integración

```python
# test_api_integration.py
import pytest
from django.test import TestCase, Client
from django.urls import reverse

class TestPaymentAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@example.com', 'pass')
        self.client.force_login(self.user)
    
    def test_create_payment_flow(self):
        # Given
        url = reverse('payments:create')
        data = {"amount": 50.00, "currency": "USD"}
        
        # When
        response = self.client.post(url, data, content_type='application/json')
        
        # Then
        self.assertEqual(response.status_code, 201)
        self.assertIn('payment_id', response.json())
```

### Estrategia de Testing

```markdown
# Test Strategy: Payment Module

## Coverage Target: 85%

### Unit Tests (70%)
- PaymentService: 15 tests
- PaymentValidator: 8 tests
- PaymentRepository: 10 tests

### Integration Tests (20%)
- API endpoints: 6 tests
- Database operations: 4 tests

### E2E Tests (10%)
- Complete payment flow: 2 scenarios
- Error handling flow: 1 scenario

## Critical Test Cases
1. Successful payment processing
2. Invalid payment data validation
3. Payment gateway failure handling
4. Database transaction rollback
```

## Herramientas y Dependencias

- **Testing Frameworks**: pytest, unittest, Jest, Mocha
- **Mocking**: unittest.mock, pytest-mock, sinon
- **E2E**: Selenium, Playwright, Cypress
- **Coverage**: coverage.py, istanbul
- **Fixtures**: Factory Boy, faker
- **LLM**: Claude, GPT-4 para generación de tests

## Mejores Prácticas

### Calidad de Tests

- Tests deben ser independientes y repetibles
- Usar nombres descriptivos de tests
- Seguir patrón Given-When-Then
- Mockear dependencias externas
- Validar tanto happy path como error cases

### Cobertura

- Apuntar a 80%+ de cobertura
- Priorizar código crítico de negocio
- No obsesionarse con 100% cobertura
- Medir cobertura de branches, no solo líneas

### Mantenimiento

- Actualizar tests cuando cambia código
- Refactorizar tests como código de producción
- Eliminar tests redundantes
- Mantener velocidad de ejecución razonable

## Restricciones

- Tests generados requieren revisión manual
- Fixtures pueden necesitar ajustes
- Mocks deben validarse con comportamiento real
- Cobertura no garantiza ausencia de bugs

## Archivo de Implementación

Ubicación: `scripts/coding/ai/sdlc/testing_agent.py`
