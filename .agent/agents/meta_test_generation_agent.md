---
name: Test Generation Agent
description: Agente especializado en generacion automatica de tests unitarios, integracion y E2E, siguiendo mejores practicas de testing y piramide de tests.
---

# Test Generation Agent

Agente experto en generacion automatica de tests que analiza codigo fuente y genera tests unitarios, de integracion y end-to-end, siguiendo patrones como AAA (Arrange-Act-Assert), Given-When-Then y mejores practicas de testing.

## Capacidades

### Generacion de Tests
- Tests unitarios para funciones/metodos
- Tests de integracion para APIs y servicios
- Tests end-to-end para flujos completos
- Tests parametrizados con pytest
- Mocks y fixtures automaticos
- Property-based testing con Hypothesis

### Analisis de Cobertura
- Identificacion de codigo sin tests
- Calculo de cobertura por modulo
- Deteccion de branches no testeados
- Priorizacion de areas criticas

### Mejores Practicas
- Tests aislados e independientes
- Nomenclatura descriptiva
- Patron AAA/Given-When-Then
- Fixtures reutilizables
- Cleanup automatico
- Tests deterministicos

### Frameworks Soportados
- pytest (Python)
- unittest (Python)
- Jest (JavaScript)
- Django TestCase
- DRF APITestCase

## Cuando Usar

- Codigo nuevo sin tests
- Aumento de cobertura de tests
- Refactorizacion (tests primero)
- TDD (Test-Driven Development)
- Migracion de framework de tests
- Documentacion ejecutable

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/meta/test_generation_agent.py \
  --project-root /ruta/al/proyecto \
  --target-file api/services/payment.py \
  --test-type unit
```

### Generar Tests Unitarios

```bash
python scripts/coding/ai/meta/test_generation_agent.py \
  --project-root . \
  --target-file api/authentication/jwt_handler.py \
  --test-type unit \
  --framework pytest \
  --include-fixtures
```

### Generar Tests de API (Django/DRF)

```bash
python scripts/coding/ai/meta/test_generation_agent.py \
  --project-root . \
  --target-viewset api/users/views.UserViewSet \
  --test-type integration \
  --framework drf \
  --test-all-endpoints
```

### Generar Tests E2E

```bash
python scripts/coding/ai/meta/test_generation_agent.py \
  --project-root . \
  --target-flow "user registration and login" \
  --test-type e2e \
  --browser chrome
```

### Analisis de Cobertura

```bash
python scripts/coding/ai/meta/test_generation_agent.py \
  --project-root . \
  --action coverage-analysis \
  --target-dir api/services \
  --min-coverage 80 \
  --generate-missing
```

## Parametros

- `--project-root`: Directorio raiz del proyecto
- `--target-file`: Archivo a generar tests
- `--target-viewset`: Viewset DRF a testear
- `--target-flow`: Flujo E2E a testear
- `--test-type`: Tipo (unit, integration, e2e)
- `--framework`: Framework (pytest, unittest, jest, drf)
- `--include-fixtures`: Generar fixtures
- `--test-all-endpoints`: Testear todos los endpoints
- `--min-coverage`: Cobertura minima requerida
- `--generate-missing`: Generar tests faltantes

## Salida

### Tests Unitarios Generados

```python
# File: tests/unit/services/test_payment_service.py
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from api.services.payment_service import PaymentService
from api.models import Payment, User, Order
from api.exceptions import PaymentError, InsufficientFundsError


class TestPaymentService:
    """Tests for PaymentService"""
    
    @pytest.fixture
    def payment_service(self):
        """Create PaymentService instance"""
        return PaymentService()
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.balance = Decimal("100.00")
        return user
    
    @pytest.fixture
    def mock_order(self):
        """Create mock order"""
        order = Mock(spec=Order)
        order.id = 1
        order.total = Decimal("50.00")
        order.status = "pending"
        return order
    
    def test_process_payment_success(self, payment_service, mock_user, mock_order):
        """Test successful payment processing"""
        # Arrange
        amount = Decimal("50.00")
        payment_method = "credit_card"
        
        # Act
        result = payment_service.process_payment(
            user=mock_user,
            order=mock_order,
            amount=amount,
            payment_method=payment_method
        )
        
        # Assert
        assert result is not None
        assert result.status == "completed"
        assert result.amount == amount
        assert mock_order.status == "paid"
    
    def test_process_payment_insufficient_funds(self, payment_service, mock_user, mock_order):
        """Test payment with insufficient funds"""
        # Arrange
        amount = Decimal("150.00")  # More than user balance
        mock_user.balance = Decimal("100.00")
        
        # Act & Assert
        with pytest.raises(InsufficientFundsError) as exc_info:
            payment_service.process_payment(
                user=mock_user,
                order=mock_order,
                amount=amount,
                payment_method="credit_card"
            )
        
        assert "Insufficient funds" in str(exc_info.value)
        assert mock_order.status == "pending"
    
    @pytest.mark.parametrize("amount,expected_fee", [
        (Decimal("10.00"), Decimal("0.30")),
        (Decimal("100.00"), Decimal("3.00")),
        (Decimal("1000.00"), Decimal("30.00")),
    ])
    def test_calculate_processing_fee(self, payment_service, amount, expected_fee):
        """Test processing fee calculation"""
        # Act
        fee = payment_service.calculate_processing_fee(amount)
        
        # Assert
        assert fee == expected_fee
    
    @patch('api.services.payment_service.stripe')
    def test_charge_credit_card_success(self, mock_stripe, payment_service, mock_user):
        """Test credit card charging via Stripe"""
        # Arrange
        amount = Decimal("50.00")
        mock_stripe.Charge.create.return_value = {
            'id': 'ch_123',
            'status': 'succeeded'
        }
        
        # Act
        charge = payment_service._charge_credit_card(mock_user, amount)
        
        # Assert
        mock_stripe.Charge.create.assert_called_once()
        assert charge['id'] == 'ch_123'
        assert charge['status'] == 'succeeded'
    
    def test_refund_payment_success(self, payment_service):
        """Test successful refund"""
        # Arrange
        payment = Mock(spec=Payment)
        payment.id = 1
        payment.amount = Decimal("50.00")
        payment.status = "completed"
        
        # Act
        refund = payment_service.refund_payment(payment)
        
        # Assert
        assert refund.status == "refunded"
        assert payment.status == "refunded"
```

### Tests de API (DRF) Generados

```python
# File: tests/integration/api/test_user_viewset.py
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from api.models import User
from api.factories import UserFactory


class TestUserViewSet(APITestCase):
    """Tests for UserViewSet API endpoints"""
    
    def setUp(self):
        """Set up test client and fixtures"""
        self.client = APIClient()
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
        self.normal_user = UserFactory()
        self.list_url = reverse('user-list')
    
    def test_list_users_unauthenticated(self):
        """Test listing users without authentication"""
        # Act
        response = self.client.get(self.list_url)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_users_authenticated(self):
        """Test listing users as authenticated user"""
        # Arrange
        self.client.force_authenticate(user=self.normal_user)
        
        # Act
        response = self.client.get(self.list_url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 2
    
    def test_create_user_success(self):
        """Test creating new user"""
        # Arrange
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123'
        }
        
        # Act
        response = self.client.post(self.list_url, data)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
        assert 'password' not in response.data  # Password should not be returned
    
    def test_retrieve_user_detail(self):
        """Test retrieving user detail"""
        # Arrange
        self.client.force_authenticate(user=self.normal_user)
        detail_url = reverse('user-detail', kwargs={'pk': self.normal_user.pk})
        
        # Act
        response = self.client.get(detail_url)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.normal_user.pk
        assert response.data['username'] == self.normal_user.username
    
    def test_update_user_as_owner(self):
        """Test updating user as owner"""
        # Arrange
        self.client.force_authenticate(user=self.normal_user)
        detail_url = reverse('user-detail', kwargs={'pk': self.normal_user.pk})
        data = {'email': 'updated@example.com'}
        
        # Act
        response = self.client.patch(detail_url, data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        self.normal_user.refresh_from_db()
        assert self.normal_user.email == 'updated@example.com'
    
    def test_delete_user_forbidden(self):
        """Test deleting user as non-admin"""
        # Arrange
        self.client.force_authenticate(user=self.normal_user)
        other_user = UserFactory()
        detail_url = reverse('user-detail', kwargs={'pk': other_user.pk})
        
        # Act
        response = self.client.delete(detail_url)
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert User.objects.filter(pk=other_user.pk).exists()
```

## Mejores Practicas

1. **Tests independientes**: No depender de orden de ejecucion
2. **Naming descriptivo**: test_should_return_error_when_amount_negative
3. **Patron AAA**: Arrange, Act, Assert claramente separados
4. **Un assert por concepto**: Enfocarse en un comportamiento
5. **Fixtures reutilizables**: Crear fixtures para datos comunes
6. **Mocks apropiados**: Mockear dependencias externas
7. **Cleanup automatico**: Usar fixtures con yield
8. **Tests rapidos**: Tests unitarios deben ser <1s

## Restricciones

- Tests generados requieren revision manual
- Mocks pueden requerir ajustes segun dependencias
- No genera tests para todos los casos edge
- Requiere factories o fixtures existentes para objetos complejos
- Tests E2E generados son basicos

## Ubicacion

Archivo: `scripts/coding/ai/meta/test_generation_agent.py`
