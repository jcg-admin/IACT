---
name: Design Patterns Agent
description: Agente especializado en identificacion, recomendacion e implementacion de patrones de diseno (GoF, enterprise, arquitectonicos) en codigo existente.
---

# Design Patterns Agent

Agente experto en patrones de diseno que analiza codigo existente, identifica oportunidades para aplicar patrones, recomienda implementaciones y genera codigo siguiendo patrones establecidos (Gang of Four, Enterprise Patterns, Domain-Driven Design).

## Capacidades

### Deteccion de Patrones
- Identificacion de patrones existentes en codigo
- Deteccion de anti-patrones
- Analisis de uso correcto/incorrecto de patrones
- Catalogacion de patrones por categoria (creacionales, estructurales, comportamiento)

### Recomendacion
- Sugerencias de patrones aplicables segun contexto
- Evaluacion de trade-offs de cada patron
- Priorizacion por impacto y complejidad
- Alternativas y variaciones de patrones

### Generacion de Codigo
- Implementacion de patrones especificos
- Refactorizacion de codigo existente aplicando patrones
- Generacion de ejemplos y plantillas
- Adaptacion a lenguaje y framework del proyecto

### Documentacion
- Explicacion de patrones aplicados
- Diagramas UML de patrones
- Guias de uso y mejores practicas
- Referencias a documentacion canonical

## Cuando Usar

- Refactorizacion de codigo legacy
- Diseno de nuevos modulos o features
- Resolucion de problemas comunes de diseno
- Mejora de extensibilidad y mantenibilidad
- Training y onboarding de equipo
- Code reviews enfocados en patrones

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/meta/design_patterns_agent.py \
  --project-root /ruta/al/proyecto \
  --action detect \
  --language python
```

### Detectar Patrones Existentes

```bash
python scripts/coding/ai/meta/design_patterns_agent.py \
  --project-root . \
  --action detect \
  --target-file api/services/notification.py \
  --categories creational,structural,behavioral
```

### Recomendar Patrones

```bash
python scripts/coding/ai/meta/design_patterns_agent.py \
  --project-root . \
  --action recommend \
  --problem-description "Multiple payment providers, need extensible integration" \
  --context ecommerce
```

### Generar Implementacion

```bash
python scripts/coding/ai/meta/design_patterns_agent.py \
  --project-root . \
  --action implement \
  --pattern strategy \
  --target-file api/payments/processor.py \
  --language python \
  --framework django
```

### Analisis de Anti-Patrones

```bash
python scripts/coding/ai/meta/design_patterns_agent.py \
  --project-root . \
  --action detect-antipatterns \
  --severity medium,high \
  --output-format json
```

## Parametros

- `--project-root`: Directorio raiz del proyecto
- `--action`: Accion (detect, recommend, implement, detect-antipatterns)
- `--target-file`: Archivo especifico a analizar
- `--pattern`: Patron especifico (singleton, factory, strategy, observer, etc.)
- `--problem-description`: Descripcion del problema a resolver
- `--context`: Contexto del proyecto (web, ecommerce, api, etc.)
- `--categories`: Categorias de patrones (creational, structural, behavioral)
- `--language`: Lenguaje (python, javascript, java)
- `--framework`: Framework (django, react, spring)
- `--severity`: Severidad de anti-patrones (low, medium, high)

## Salida

### Deteccion de Patrones

```markdown
# Design Patterns Analysis
File: api/services/notification.py

## Detected Patterns

### 1. Observer Pattern
Location: Lines 45-78
Confidence: HIGH (95%)
Description: NotificationService implements observer pattern for event handling
Subjects: EventEmitter
Observers: EmailNotifier, SMSNotifier, PushNotifier

Implementation Quality: GOOD
- Proper separation of concerns
- Loosely coupled observers
- Easy to add new observers

### 2. Factory Method Pattern
Location: Lines 120-145
Confidence: MEDIUM (75%)
Description: NotifierFactory creates appropriate notifier instances
Products: EmailNotifier, SMSNotifier, PushNotifier

Implementation Quality: FAIR
Suggestions:
- Consider Abstract Factory for multiple product families
- Add validation for unsupported notifier types

## Anti-Patterns Detected

### 1. God Object
Location: Class NotificationManager (lines 200-450)
Severity: HIGH
Description: Class has too many responsibilities (sending, logging, retry, rate-limiting)
Recommendation: Apply Single Responsibility Principle, extract separate classes

### 2. Spaghetti Code
Location: Method process_notification (lines 380-420)
Severity: MEDIUM
Description: Complex conditional logic, difficult to follow
Recommendation: Apply Strategy or State pattern

[End of Analysis]
```

### Recomendacion de Patrones

```markdown
# Pattern Recommendations
Problem: Multiple payment providers, need extensible integration

## Recommended Patterns

### 1. Strategy Pattern (HIGHLY RECOMMENDED)
Confidence: 95%
Benefits:
- Easy to add new payment providers
- Runtime selection of payment method
- Testable in isolation

Implementation:
- PaymentStrategy interface
- ConcreteStrategies: StripePayment, PayPalPayment, BraintreePayment
- PaymentContext to manage strategies

Trade-offs:
+ Excellent extensibility
+ Clean separation
- Slight increase in number of classes

### 2. Adapter Pattern (RECOMMENDED)
Confidence: 80%
Benefits:
- Uniform interface for different payment APIs
- Isolate external dependencies

Use Case: When payment providers have very different APIs

### 3. Chain of Responsibility (OPTIONAL)
Confidence: 60%
Benefits:
- Sequential validation and processing
- Easy to add processing steps

Use Case: If payment flow has multiple validation/enrichment steps

[End of Recommendations]
```

## Patrones Soportados

### Creacionales
- Singleton
- Factory Method
- Abstract Factory
- Builder
- Prototype

### Estructurales
- Adapter
- Bridge
- Composite
- Decorator
- Facade
- Flyweight
- Proxy

### Comportamiento
- Chain of Responsibility
- Command
- Iterator
- Mediator
- Memento
- Observer
- State
- Strategy
- Template Method
- Visitor

### Enterprise
- Repository
- Unit of Work
- Service Layer
- Domain Model
- CQRS
- Event Sourcing

## Mejores Practicas

1. No aplicar patrones por aplicar (evitar over-engineering)
2. Entender el problema antes de elegir patron
3. Considerar trade-offs de cada patron
4. Documentar decision de patron en ADRs
5. Mantener simplicidad cuando sea posible
6. Refactorizar hacia patrones gradualmente
7. Validar patron con code review

## Restricciones

- Deteccion automatica puede tener falsos positivos/negativos
- Requiere contexto para recomendaciones precisas
- Algunos patrones requieren refactorizacion mayor
- No todos los patrones aplican a todos los lenguajes
- Over-engineering es riesgo si se abusa

## Ubicacion

Archivo: `scripts/coding/ai/meta/design_patterns_agent.py`
