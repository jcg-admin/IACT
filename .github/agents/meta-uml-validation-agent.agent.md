---
name: UML Validation Agent
description: Agente especializado en validacion de diagramas UML, verificacion de consistencia, correccion de errores y sugerencias de mejora en diagramas.
---

# UML Validation Agent

Agente experto en validacion de diagramas UML que verifica consistencia, correccion sintactica, adherencia a estandares UML, y genera sugerencias de mejora para diagramas de clases, secuencia, componentes y otros.

## Capacidades

### Validacion Sintactica
- Verificacion de sintaxis PlantUML/Mermaid
- Deteccion de errores de formato
- Validacion de relaciones invalidas
- Comprobacion de multiplicidad correcta

### Validacion Semantica
- Consistencia de relaciones (herencia, composicion)
- Validacion de tipos de datos
- Verificacion de visibilidad (public, private, protected)
- Deteccion de referencias circular

es
- Validacion de dependencias logicas

### Mejores Practicas UML
- Nomenclatura de clases y metodos
- Uso correcto de estereotipos
- Organizacion de paquetes
- Nivel apropiado de detalle
- Legibilidad y claridad

### Sugerencias de Mejora
- Refactorizacion de diagramas complejos
- Simplificacion de relaciones
- Agrupacion de elementos relacionados
- Aplicacion de patrones de diseno visibles

## Cuando Usar

- Revision de diagramas antes de documentacion
- Validacion de arquitectura
- Code reviews con diagramas
- Capacitacion en UML
- Preparacion de presentaciones tecnicas
- Auditoria de documentacion

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/meta/uml_validation_agent.py \
  --diagram-file docs/diagrams/class_diagram.puml \
  --diagram-type class
```

### Validacion Completa

```bash
python scripts/coding/ai/meta/uml_validation_agent.py \
  --diagram-file docs/architecture.puml \
  --diagram-type component \
  --check-all \
  --severity medium \
  --suggest-improvements
```

### Validacion Batch

```bash
python scripts/coding/ai/meta/uml_validation_agent.py \
  --diagram-dir docs/diagrams \
  --recursive \
  --output-format json \
  --fix-auto
```

### Comparacion con Codigo

```bash
python scripts/coding/ai/meta/uml_validation_agent.py \
  --diagram-file docs/models.puml \
  --compare-with-code api/models.py \
  --detect-drift
```

## Parametros

- `--diagram-file`: Archivo de diagrama a validar
- `--diagram-dir`: Directorio con multiples diagramas
- `--diagram-type`: Tipo (class, sequence, component, activity)
- `--check-all`: Ejecutar todas las validaciones
- `--severity`: Severidad minima (info, warning, error)
- `--suggest-improvements`: Generar sugerencias
- `--compare-with-code`: Comparar con codigo fuente
- `--detect-drift`: Detectar diferencias codigo vs diagrama
- `--fix-auto`: Corregir errores automaticamente
- `--recursive`: Escanear recursivamente

## Salida

### Reporte de Validacion

```markdown
# UML Validation Report
Diagram: docs/diagrams/class_diagram.puml
Type: Class Diagram
Validated: 2025-11-15

## Syntax Validation: PASS

No syntax errors detected.

## Semantic Validation: FAIL (3 errors, 2 warnings)

### Errors

#### 1. Invalid Relationship
Line 45: `User --|> Profile`
Severity: ERROR

Description:
Inheritance relationship (--|>) is incorrect. User should have a composition 
or aggregation relationship with Profile, not inheritance.

Recommendation:
```plantuml
User "1" *-- "1" Profile : has
```

#### 2. Missing Multiplicity
Line 67: `Order -- Product`
Severity: ERROR

Description:
Relationship between Order and Product lacks multiplicity specification.

Recommendation:
```plantuml
Order "1" -- "1..*" Product : contains
```

#### 3. Circular Dependency
Lines 89, 102, 115
Severity: ERROR

Description:
Circular dependency detected: User -> Group -> Permission -> User

Recommendation:
Break circular dependency by introducing an intermediary class or 
using dependency inversion.

### Warnings

#### 1. Inconsistent Naming
Class: user_profile
Severity: WARNING

Description:
Class name uses snake_case. UML convention is PascalCase.

Recommendation:
Rename to `UserProfile`

#### 2. Too Many Attributes
Class: Order (28 attributes)
Severity: WARNING

Description:
Class has excessive number of attributes, reducing diagram readability.

Recommendation:
- Group related attributes
- Extract value objects
- Use notes for less important attributes

## Best Practices: 6/10

### Issues

1. Missing visibility modifiers on 12 attributes
2. No method parameters documented
3. Stereotypes not used where applicable
4. No package organization
5. Diagram complexity: HIGH (87 elements)

### Recommendations

1. Add visibility (+, -, #) to all attributes and methods
2. Document method signatures with parameter types
3. Use <<interface>>, <<abstract>>, <<entity>> stereotypes
4. Organize classes into logical packages
5. Consider splitting into multiple focused diagrams

## Code Comparison: DRIFT DETECTED

Compared with: api/models.py

### Missing in Diagram

- Class: AuditLog (not in diagram)
- Attribute: User.last_login_ip (not in diagram)
- Method: Order.calculate_total() (not in diagram)

### Missing in Code

- Class: ShippingAddress (in diagram, not in code)
- Attribute: User.middle_name (in diagram, not in code)

### Type Mismatches

- User.created_at: datetime in code, Date in diagram

## Suggested Improvements

### 1. Simplify Diagram
Current complexity: HIGH (87 elements)
Target: Split into 3 diagrams (Core, Authentication, Orders)

### 2. Apply Design Patterns
Detected opportunity for:
- Strategy pattern in Payment processing
- Observer pattern in Notification system
- Factory pattern in Report generation

### 3. Improve Organization
```plantuml
package "Core" {
    class User
    class Profile
}

package "Orders" {
    class Order
    class OrderItem
}
```

## Summary

| Category | Status | Count |
|----------|--------|-------|
| Syntax Errors | PASS | 0 |
| Semantic Errors | FAIL | 3 |
| Warnings | - | 2 |
| Code Drift | DETECTED | 5 |
| Quality Score | - | 6/10 |

Action Required: Fix 3 errors before using diagram in documentation.

[End of Report]
```

## Herramientas Utilizadas

- **plantuml**: Parser de diagramas PlantUML
- **pyplantuml**: Validacion de sintaxis PlantUML
- **pylint**: Comparacion con codigo Python
- **pydot**: Procesamiento de grafos
- **networkx**: Analisis de dependencias circulares

## Mejores Practicas

1. **Validar antes de documentar**: No publicar diagramas con errores
2. **Mantener sincronizado**: Validar diagrama vs codigo periodicamente
3. **Simplicidad**: Validar complejidad de diagramas
4. **Estandares**: Seguir convenciones UML 2.5
5. **Automatizar**: Integrar validacion en CI
6. **Iteracion**: Validar despues de cada cambio significativo
7. **Documentar excepciones**: Justificar desviaciones de estandares

## Restricciones

- Validacion semantica limitada sin contexto de dominio
- Algunas validaciones requieren interpretacion humana
- No detecta todos los problemas de diseno
- Comparacion con codigo limitada a lenguajes soportados
- Correcciones automaticas pueden no ser optimas

## Ubicacion

Archivo: `scripts/coding/ai/meta/uml_validation_agent.py`
