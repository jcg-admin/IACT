---
name: SchemaValidatorAgent
description: Agente especializado en validacion de schemas JSON/YAML, verificando conformidad con especificaciones, deteccion de inconsistencias y validacion de migraciones de schema.
---

# Automation: Schema Validator Agent

El SchemaValidatorAgent valida schemas JSON/YAML contra especificaciones, detecta inconsistencias, valida migraciones de schema y asegura backward compatibility.

## Capacidades

### Validacion de Schema
- Conformidad con JSON Schema Draft 7/2019-09
- Validacion de YAML schemas
- Verificacion de tipos de datos
- Validacion de constraints (min, max, pattern, enum)
- Required fields presentes

### Validacion de Migraciones
- Backward compatibility
- Breaking changes detection
- Field additions/removals
- Type changes
- Constraint modifications

### Validacion de Consistencia
- Cross-schema consistency
- Naming conventions
- Field type consistency
- Enum value consistency

### Validacion de Buenas Practicas
- Descripcion fields presentes
- Examples incluidos
- Deprecation warnings
- Version tracking

### Auto-Generacion
- Schema desde data samples
- OpenAPI schema generation
- GraphQL schema generation
- Documentation generation

## Cuando usar

- **Pre-Commit**: Validar cambios en schemas antes de commit
- **API Changes**: Validar modificaciones de API contracts
- **Migration Planning**: Verificar backward compatibility
- **Documentation**: Generar docs desde schemas
- **Contract Testing**: Validar payloads contra schemas
- **Integration Testing**: Verificar conformidad API-Schema

## Como usar

### Validacion Basica

```bash
python scripts/coding/ai/automation/schema_validator_agent.py \
  --schema api_schema.json \
  --validate
```

### Validacion de Data contra Schema

```bash
python scripts/coding/ai/automation/schema_validator_agent.py \
  --schema user_schema.json \
  --data user_payload.json \
  --validate-data
```

### Validacion de Migracion

```bash
python scripts/coding/ai/automation/schema_validator_agent.py \
  --old-schema api_v1_schema.json \
  --new-schema api_v2_schema.json \
  --validate-migration \
  --detect-breaking-changes
```

### Auto-Generacion de Schema

```bash
# Desde data samples
python scripts/coding/ai/automation/schema_validator_agent.py \
  --data-samples samples/*.json \
  --generate-schema \
  --output generated_schema.json

# Desde modelos Django
python scripts/coding/ai/automation/schema_validator_agent.py \
  --django-models api.models \
  --generate-openapi \
  --output openapi.yaml
```

### Validacion Batch

```bash
# Validar multiples schemas
python scripts/coding/ai/automation/schema_validator_agent.py \
  --schema-dir schemas/ \
  --validate-all \
  --output validation_report.json
```

### Integracion CI

```bash
python scripts/coding/ai/automation/schema_validator_agent.py \
  --schema-dir schemas/ \
  --validate-all \
  --fail-on-error \
  --check-breaking-changes
```

## Output esperado

### Validacion de Schema

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "schema": "api_schema.json",
  "valid": false,
  "errors": [
    {
      "path": "properties.user.properties.email",
      "error": "Missing 'format' for email field",
      "severity": "warning"
    },
    {
      "path": "properties.address",
      "error": "Required field 'postalCode' not defined in properties",
      "severity": "error"
    }
  ],
  "warnings": 1,
  "errors": 1
}
```

### Validacion de Migracion

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "old_schema": "api_v1_schema.json",
  "new_schema": "api_v2_schema.json",
  "backward_compatible": false,
  "breaking_changes": [
    {
      "type": "field_removed",
      "path": "properties.user.properties.middleName",
      "severity": "error",
      "impact": "Clients using middleName will break"
    },
    {
      "type": "type_changed",
      "path": "properties.age",
      "old_type": "string",
      "new_type": "integer",
      "severity": "error",
      "impact": "Type mismatch will cause validation errors"
    }
  ],
  "non_breaking_changes": [
    {
      "type": "field_added",
      "path": "properties.user.properties.phoneNumber",
      "severity": "info"
    }
  ],
  "recommendation": "Version bump required: v1 -> v2"
}
```

### Auto-Generated Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "User",
  "description": "User entity schema",
  "properties": {
    "id": {
      "type": "integer",
      "description": "User unique identifier"
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "User email address"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "User full name"
    }
  },
  "required": ["id", "email", "name"],
  "additionalProperties": false
}
```

## Herramientas y dependencias

- **Python 3.11+**
- **JSON Schema**: jsonschema
- **YAML**: PyYAML
- **OpenAPI**: openapi-spec-validator
- **GraphQL**: graphql-core

## Buenas practicas

1. **Version schemas**: Trackear versiones de schemas
2. **Backward compatibility**: Evitar breaking changes cuando posible
3. **Documentation**: Incluir descriptions y examples
4. **Validation en CI**: Validar schemas en cada PR
5. **Contract testing**: Validar payloads contra schemas
6. **Deprecation warnings**: Anunciar cambios con anticipacion
7. **Migration guides**: Documentar path para upgrades

## Restricciones

- **JSON Schema draft**: Soporta Draft 7 y 2019-09
- **YAML subset**: Solo schemas YAML validos
- **Breaking changes**: Deteccion heuristica, no exhaustiva
- **Type inference**: Auto-generation puede necesitar ajustes

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/schema_validator_agent.py`
Tests: `scripts/coding/ai/tests/test_schema_validator_agent.py`
