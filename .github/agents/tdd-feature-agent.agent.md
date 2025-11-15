---
name: Feature Agent
description: Agente especializado en implementacion completa de features usando TDD, desde user stories hasta codigo produccion con tests, siguiendo BDD y acceptance criteria.
---

# Feature Agent

Agente experto en implementacion end-to-end de features que convierte user stories en codigo funcional usando TDD/BDD, generando acceptance tests, tests unitarios y codigo de produccion siguiendo ciclo completo de desarrollo.

## Capacidades

### User Story Processing
- Parsing de user stories (Given-When-Then)
- Extraccion de acceptance criteria
- Identificacion de scenarios
- Generacion de ejemplos

### BDD Implementation
- Generacion de feature files (Gherkin)
- Step definitions
- Acceptance tests
- Integration con Behave/Cucumber

### TDD Integration
- Tests unitarios para cada componente
- Test doubles (mocks, stubs, spies)
- Test fixtures
- Test data builders

### End-to-End Implementation
- API endpoints
- Business logic
- Data access layer
- Integration tests

## Cuando Usar

- Implementacion de nuevas features
- Conversion de user stories a codigo
- Desarrollo guiado por comportamiento
- Features con multiple scenarios
- Integracion frontend-backend
- Validation de acceptance criteria

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/tdd/feature_agent.py \
  --user-story "As a user, I want to reset my password" \
  --implement-feature
```

### Implementacion Completa

```bash
python scripts/coding/ai/tdd/feature_agent.py \
  --user-story-file stories/password-reset.md \
  --generate-feature-file \
  --generate-tests \
  --implement-code \
  --output-dir features/password_reset/
```

### Solo Acceptance Tests

```bash
python scripts/coding/ai/tdd/feature_agent.py \
  --user-story "User registration" \
  --action generate-acceptance-tests \
  --framework behave \
  --output-file features/registration.feature
```

### Implementacion con TDD

```bash
python scripts/coding/ai/tdd/feature_agent.py \
  --feature-file features/login.feature \
  --action implement-with-tdd \
  --iterations 5 \
  --coverage-target 100
```

## Parametros

- `--user-story`: User story en formato texto
- `--user-story-file`: Archivo con user story
- `--implement-feature`: Implementar feature completa
- `--generate-feature-file`: Generar archivo Gherkin
- `--generate-tests`: Generar tests
- `--implement-code`: Generar codigo produccion
- `--action`: Accion especifica
- `--framework`: Framework BDD (behave, cucumber)
- `--iterations`: Numero de ciclos TDD
- `--coverage-target`: Cobertura objetivo
- `--output-dir`: Directorio de salida

## Salida

### User Story Input

```markdown
# User Story: Password Reset

As a registered user
I want to reset my forgotten password
So that I can regain access to my account

## Acceptance Criteria

### Scenario 1: Request password reset
Given I am on the login page
And I have forgotten my password
When I click "Forgot Password"
And I enter my registered email address
Then I should receive a password reset email
And the email should contain a reset link valid for 24 hours

### Scenario 2: Reset password with valid token
Given I have received a password reset email
When I click the reset link
And I enter a new password
And I confirm the new password
Then my password should be updated
And I should be redirected to login page
And I should see a success message

### Scenario 3: Reset with expired token
Given I have a password reset link that is older than 24 hours
When I try to use the expired link
Then I should see an error message
And I should be offered to request a new reset link
```

### Generated Feature File (Gherkin)

```gherkin
# features/password_reset.feature
Feature: Password Reset
  As a registered user
  I want to reset my forgotten password
  So that I can regain access to my account

  Background:
    Given the following users exist:
      | email              | password  | active |
      | user@example.com   | oldpass123| true   |

  Scenario: Request password reset
    Given I am on the login page
    When I click "Forgot Password"
    And I enter "user@example.com" in the email field
    And I click "Send Reset Link"
    Then I should see a confirmation message
    And a password reset email should be sent to "user@example.com"
    And the reset token should expire in 24 hours

  Scenario: Reset password with valid token
    Given I have a valid password reset token
    When I visit the password reset page with the token
    And I enter "newpass123" as the new password
    And I enter "newpass123" as the password confirmation
    And I click "Reset Password"
    Then my password should be updated to "newpass123"
    And I should be redirected to "/login"
    And I should see "Password successfully reset"

  Scenario: Reset with expired token
    Given I have a password reset token that expired 25 hours ago
    When I visit the password reset page with the expired token
    Then I should see "Reset link has expired"
    And I should see a link to "Request new reset link"

  Scenario: Reset with mismatched passwords
    Given I have a valid password reset token
    When I visit the password reset page with the token
    And I enter "newpass123" as the new password
    And I enter "differentpass" as the password confirmation
    And I click "Reset Password"
    Then I should see "Passwords do not match"
    And my password should not be changed
```

### Generated Step Definitions

```python
# features/steps/password_reset_steps.py
from behave import given, when, then
from django.urls import reverse
from api.models import User, PasswordResetToken
from django.utils import timezone
from datetime import timedelta


@given('the following users exist')
def step_create_users(context):
    for row in context.table:
        User.objects.create_user(
            email=row['email'],
            password=row['password'],
            is_active=row['active'] == 'true'
        )


@given('I am on the login page')
def step_on_login_page(context):
    context.response = context.client.get(reverse('login'))
    assert context.response.status_code == 200


@when('I click "Forgot Password"')
def step_click_forgot_password(context):
    # Simulated - in real scenario would click link
    context.forgot_password_clicked = True


@when('I enter "{email}" in the email field')
def step_enter_email(context, email):
    context.email = email


@when('I click "Send Reset Link"')
def step_click_send_reset(context):
    url = reverse('password-reset-request')
    context.response = context.client.post(url, {'email': context.email})


@then('I should see a confirmation message')
def step_see_confirmation(context):
    assert context.response.status_code == 200
    assert 'confirmation' in context.response.content.decode().lower()


@then('a password reset email should be sent to "{email}"')
def step_email_sent(context, email):
    from django.core import mail
    assert len(mail.outbox) == 1
    assert email in mail.outbox[0].to


@then('the reset token should expire in 24 hours')
def step_token_expires_24h(context):
    token = PasswordResetToken.objects.latest('created_at')
    expected_expiry = token.created_at + timedelta(hours=24)
    assert token.expires_at == expected_expiry
```

### Generated Unit Tests

```python
# tests/test_password_reset_service.py
import pytest
from datetime import timedelta
from django.utils import timezone
from api.services import PasswordResetService
from api.models import User, PasswordResetToken
from api.exceptions import InvalidTokenError, ExpiredTokenError


class TestPasswordResetService:
    
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            email='test@example.com',
            password='oldpass123'
        )
    
    @pytest.fixture
    def service(self):
        return PasswordResetService()
    
    def test_generate_reset_token(self, service, user):
        """Should generate valid reset token"""
        token = service.generate_reset_token(user)
        
        assert token is not None
        assert len(token) == 64  # hex token length
        assert PasswordResetToken.objects.filter(
            user=user,
            token=token
        ).exists()
    
    def test_token_expires_in_24_hours(self, service, user):
        """Reset token should expire in 24 hours"""
        token = service.generate_reset_token(user)
        token_obj = PasswordResetToken.objects.get(token=token)
        
        expected_expiry = timezone.now() + timedelta(hours=24)
        time_diff = abs((token_obj.expires_at - expected_expiry).total_seconds())
        
        assert time_diff < 1  # Within 1 second
    
    def test_validate_valid_token(self, service, user):
        """Should validate non-expired token"""
        token = service.generate_reset_token(user)
        
        is_valid = service.validate_token(token)
        
        assert is_valid is True
    
    def test_reject_expired_token(self, service, user):
        """Should reject expired token"""
        token = service.generate_reset_token(user)
        
        # Manually expire token
        token_obj = PasswordResetToken.objects.get(token=token)
        token_obj.expires_at = timezone.now() - timedelta(hours=1)
        token_obj.save()
        
        with pytest.raises(ExpiredTokenError):
            service.validate_token(token)
    
    def test_reset_password_with_valid_token(self, service, user):
        """Should reset password with valid token"""
        token = service.generate_reset_token(user)
        new_password = "newpass123"
        
        service.reset_password(token, new_password)
        
        user.refresh_from_db()
        assert user.check_password(new_password)
    
    def test_invalidate_token_after_use(self, service, user):
        """Should invalidate token after password reset"""
        token = service.generate_reset_token(user)
        service.reset_password(token, "newpass123")
        
        with pytest.raises(InvalidTokenError):
            service.validate_token(token)
```

### Generated Production Code

```python
# api/services/password_reset_service.py
import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from api.models import User, PasswordResetToken
from api.exceptions import InvalidTokenError, ExpiredTokenError, UserNotFoundError


class PasswordResetService:
    """Service for handling password reset functionality"""
    
    TOKEN_EXPIRY_HOURS = 24
    TOKEN_LENGTH = 32  # bytes (64 hex characters)
    
    def generate_reset_token(self, user: User) -> str:
        """
        Generate a password reset token for user
        
        Args:
            user: User requesting password reset
            
        Returns:
            Reset token string
        """
        # Invalidate any existing tokens
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)
        
        # Generate secure random token
        token = secrets.token_hex(self.TOKEN_LENGTH)
        
        # Create token record
        expiry = timezone.now() + timedelta(hours=self.TOKEN_EXPIRY_HOURS)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expiry
        )
        
        return token
    
    def send_reset_email(self, user: User, token: str) -> None:
        """Send password reset email to user"""
        reset_url = f"{settings.FRONTEND_URL}/password-reset/{token}"
        
        send_mail(
            subject="Password Reset Request",
            message=f"Click here to reset your password: {reset_url}\n\n"
                    f"This link expires in {self.TOKEN_EXPIRY_HOURS} hours.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    
    def validate_token(self, token: str) -> bool:
        """
        Validate reset token
        
        Raises:
            InvalidTokenError: If token doesn't exist or already used
            ExpiredTokenError: If token has expired
        """
        try:
            token_obj = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            raise InvalidTokenError("Invalid reset token")
        
        if token_obj.is_used:
            raise InvalidTokenError("Token already used")
        
        if token_obj.expires_at < timezone.now():
            raise ExpiredTokenError("Reset link has expired")
        
        return True
    
    def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset user password with valid token
        
        Args:
            token: Password reset token
            new_password: New password to set
        """
        self.validate_token(token)
        
        token_obj = PasswordResetToken.objects.get(token=token)
        user = token_obj.user
        
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        token_obj.is_used = True
        token_obj.save()
```

## Metricas Feature Implementation

| Metric | Value |
|--------|-------|
| User Stories Processed | 1 |
| Scenarios Generated | 4 |
| Acceptance Tests | 4 |
| Unit Tests | 6 |
| Step Definitions | 8 |
| Production Classes | 1 |
| Test Coverage | 100% |
| All Tests Passing | YES |

## Mejores Practicas

1. **Start with user story**: Always begin with business value
2. **Acceptance criteria first**: Define success before coding
3. **Outside-in TDD**: Acceptance test → unit tests → code
4. **Gherkin clarity**: Use clear Given-When-Then
5. **Reusable steps**: Create composable step definitions
6. **Data builders**: Use factories for test data
7. **Continuous validation**: Run tests frequently

## Restricciones

- Requiere user stories bien definidas
- BDD frameworks pueden tener learning curve
- Acceptance tests mas lentos que unit tests
- Generacion automatica puede requerir ajustes
- Contexto de negocio necesario para escenarios completos

## Ubicacion

Archivo: `scripts/coding/ai/tdd/feature_agent.py`
