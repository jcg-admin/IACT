---
name: TDD Agent
description: Agente especializado en Test-Driven Development, generacion de tests antes de codigo, ciclo Red-Green-Refactor y mejores practicas de TDD.
---

# TDD Agent

Agente experto en Test-Driven Development que guia el proceso TDD, genera tests antes del codigo de produccion, implementa ciclo Red-Green-Refactor y asegura cobertura completa siguiendo principios FIRST.

## Capacidades

### Ciclo TDD
- Red: Generar test que falla
- Green: Implementar codigo minimo para pasar
- Refactor: Mejorar sin cambiar comportamiento
- Iteracion continua

### Generacion de Tests
- Tests unitarios con AAA pattern
- Tests parametrizados con multiples casos
- Tests de integracion cuando necesario
- Mocks y stubs apropiados

### Principios FIRST
- Fast: Tests rapidos (<1s)
- Independent: Tests aislados
- Repeatable: Resultados consistentes
- Self-validating: Pass/fail claro
- Timely: Tests antes de codigo

### Cobertura
- Line coverage
- Branch coverage
- Path coverage
- Mutation testing

## Cuando Usar

- Desarrollo de nueva funcionalidad
- Refactorizacion de codigo existente
- Bug fixing (test del bug primero)
- Mejora de diseno de codigo
- Documentacion ejecutable
- Confidence building

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/agents/tdd/tdd_agent.py \
  --feature "User registration" \
  --start-tdd-cycle
```

### TDD Cycle Completo

```bash
python scripts/coding/ai/agents/tdd/tdd_agent.py \
  --feature "Email validation" \
  --generate-test \
  --implement-minimal \
  --refactor \
  --iterate
```

### Generar Test Inicial (RED)

```bash
python scripts/coding/ai/agents/tdd/tdd_agent.py \
  --action red \
  --feature-description "User should not register with invalid email" \
  --output-file tests/test_user_registration.py
```

### Implementar Codigo (GREEN)

```bash
python scripts/coding/ai/agents/tdd/tdd_agent.py \
  --action green \
  --test-file tests/test_user_registration.py \
  --output-file api/validators.py
```

### Refactorizar (REFACTOR)

```bash
python scripts/coding/ai/agents/tdd/tdd_agent.py \
  --action refactor \
  --target-file api/validators.py \
  --preserve-tests
```

## Parametros

- `--feature`: Descripcion de feature a implementar
- `--action`: Fase TDD (red, green, refactor)
- `--feature-description`: Descripcion detallada
- `--generate-test`: Generar test inicial
- `--implement-minimal`: Implementar codigo minimo
- `--refactor`: Refactorizar codigo
- `--test-file`: Archivo de tests
- `--target-file`: Archivo de codigo
- `--iterate`: Ejecutar multiples ciclos
- `--preserve-tests`: Mantener tests pasando

## Salida

### Fase RED: Test que Falla

```python
# tests/test_user_registration.py
import pytest
from api.validators import EmailValidator
from api.exceptions import ValidationError


class TestEmailValidation:
    """
    TDD Cycle 1: Email validation
    Feature: User should not register with invalid email
    Status: RED (test should fail)
    """
    
    def test_reject_email_without_at_symbol(self):
        """Email without @ should be rejected"""
        # Arrange
        validator = EmailValidator()
        invalid_email = "userexample.com"
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(invalid_email)
        
        assert "Invalid email format" in str(exc_info.value)
    
    def test_reject_email_without_domain(self):
        """Email without domain should be rejected"""
        validator = EmailValidator()
        invalid_email = "user@"
        
        with pytest.raises(ValidationError):
            validator.validate(invalid_email)
    
    def test_accept_valid_email(self):
        """Valid email should be accepted"""
        validator = EmailValidator()
        valid_email = "user@example.com"
        
        # Should not raise exception
        result = validator.validate(valid_email)
        assert result is True
```

**Run tests**: 
```bash
pytest tests/test_user_registration.py
# Result: 3 failed (expected - RED phase)
```

### Fase GREEN: Implementacion Minima

```python
# api/validators.py
import re
from api.exceptions import ValidationError


class EmailValidator:
    """Validates email addresses"""
    
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def validate(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If email is invalid
        """
        if not re.match(self.EMAIL_PATTERN, email):
            raise ValidationError("Invalid email format")
        
        return True
```

**Run tests**: 
```bash
pytest tests/test_user_registration.py
# Result: 3 passed (GREEN phase achieved)
```

### Fase REFACTOR: Mejora sin Cambiar Comportamiento

```python
# api/validators.py (refactored)
import re
from typing import Optional
from dataclasses import dataclass
from api.exceptions import ValidationError


@dataclass
class ValidationResult:
    """Result of validation"""
    is_valid: bool
    error_message: Optional[str] = None


class EmailValidator:
    """
    Validates email addresses according to RFC 5322
    
    Improvements:
    - Added comprehensive regex
    - Better error messages
    - Extracted constants
    - Added domain validation
    - Type hints
    """
    
    # RFC 5322 simplified pattern
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@'
        r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?'
        r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    )
    
    MAX_EMAIL_LENGTH = 254  # RFC 5321
    
    def validate(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If email is invalid with specific reason
        """
        if not email:
            raise ValidationError("Email cannot be empty")
        
        if len(email) > self.MAX_EMAIL_LENGTH:
            raise ValidationError(
                f"Email too long (max {self.MAX_EMAIL_LENGTH} characters)"
            )
        
        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError("Invalid email format")
        
        # Additional validation
        self._validate_domain(email)
        
        return True
    
    def _validate_domain(self, email: str) -> None:
        """Validate email domain part"""
        try:
            _, domain = email.rsplit('@', 1)
            if '.' not in domain:
                raise ValidationError("Email domain must contain a dot")
        except ValueError:
            raise ValidationError("Invalid email format")
```

**Run tests**: 
```bash
pytest tests/test_user_registration.py
# Result: 3 passed (tests still pass after refactor)

pytest --cov=api.validators
# Coverage: 100%
```

## Metricas TDD

| Metric | Value | Status |
|--------|-------|--------|
| Test Coverage | 100% | EXCELLENT |
| Tests Written First | 100% | TDD COMPLIANT |
| Red-Green Cycles | 3 | GOOD |
| Refactoring Steps | 1 | ADEQUATE |
| Test Execution Time | 0.05s | FAST |

## Beneficios TDD

1. **Better Design**: Tests drive API design
2. **High Coverage**: 100% by default
3. **Living Documentation**: Tests document behavior
4. **Confidence**: Refactor without fear
5. **Bug Prevention**: Catch bugs before they exist
6. **Rapid Feedback**: Know immediately if broken

## Mejores Practicas

1. **Write test first**: Always RED before GREEN
2. **Minimal implementation**: Just enough to pass
3. **Refactor regularly**: Keep code clean
4. **Fast tests**: Sub-second execution
5. **One assertion**: Focus on single behavior
6. **Descriptive names**: Test names explain intent
7. **FIRST principles**: Follow consistently

## Restricciones

- Requiere disciplina para seguir ciclo
- Initial learning curve
- Puede parecer mas lento al inicio
- No apto para exploratory coding
- Requiere tests automatizados ejecutables

## Ubicacion

Archivo: `scripts/coding/ai/agents/tdd/tdd_agent.py`
