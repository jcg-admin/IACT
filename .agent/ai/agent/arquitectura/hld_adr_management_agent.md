---
title: High-Level Design - ADR Management Agent
date: 2025-11-13
issue_number: IACT-ADR-AGENT-001
phase: design
type: hld
status: draft
domain: ai
version: 1.0.0
---

# High-Level Design: ADR Management Agent

**Issue**: IACT-ADR-AGENT-001
**Phase**: DESIGN (Phase 3 of 6)
**Document Type**: High-Level Design (HLD)
**Author**: Claude AI Agent
**Date**: 2025-11-13
**Version**: 1.0.0
**Status**: Draft

---

## 1. Overview

### 1.1 Purpose

The ADR Management Agent is an SDLC agent responsible for managing the complete lifecycle of Architecture Decision Records (ADRs) in the IACT project. 

> **Note:** "IACT project" refers to [clarify: either a specific project within the organization, or is intended as a placeholder for any project name. If this document is reused, replace "IACT project" with the relevant project name.]

It provides automated operations for creating, validating, standardizing, and maintaining ADRs and their index.
### 1.2 Scope

**In Scope**:
- Create new ADRs with standard format and sequential numbering
- Validate existing ADRs for format and content compliance
- Standardize ADR nomenclature (hyphens to underscores)
- Maintain master index at `docs/gobernanza/INDICE_ADRs.md`
- Update references to ADRs across documentation
- CLI and programmatic interfaces

**Out of Scope**:
- ADR content authoring (templates provide structure, humans write content)
- Version control operations (git add/commit/push)
- Multi-language support (English/Spanish only)
- Real-time collaboration features
- Web UI or REST API

### 1.3 Goals and Non-Goals

**Goals**:
1. Eliminate manual ADR maintenance through automation
2. Ensure consistent ADR format across all domains
3. Maintain accurate and up-to-date master index
4. Provide fast and reliable ADR operations (< 5 seconds)
5. Achieve >= 90% test coverage
6. Integrate seamlessly with existing SDLC pipeline

**Non-Goals**:
- Replace human decision-making in architecture
- Enforce specific architectural patterns
- Automatically generate ADR content from code
- Provide AI-powered content suggestions

---

## 2. Architecture Overview

### 2.1 System Context

```
+------------------+
|   User / CLI     |
+--------+---------+
         |
         v
+--------+---------+        +-----------------------+
| sdlc_agent.py   |------->| ADRManagementAgent   |
|  (CLI Entry)    |        |                       |
+------------------+        |  - create()           |
                            |  - validate()         |
         ^                  |  - standardize()      |
         |                  |  - update_index()     |
         |                  |  - update_references()|
+--------+---------+        +-----------+-----------+
| Python Scripts   |                    |
| (Programmatic)   |                    |
+------------------+                    v
                            +-----------+-----------+
                            | File System           |
                            |                       |
                            | docs/                 |
                            |   ├── ai/             |
                            |   ├── backend/        |
                            |   ├── frontend/       |
                            |   ├── infraestructura/|
                            |   └── gobernanza/     |
                            |         └── INDICE_ADRs.md
                            +-----------------------+
```

### 2.2 Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   ADRManagementAgent                        │
│                   (extends SDLCAgent)                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Public API:                                                │
│  ┌────────────────────────────────────────────────┐         │
│  │ run(input_data: Dict) -> Dict                 │         │
│  │ execute(input_data: Dict) -> AgentResult      │         │
│  │ validate_input(input_data: Dict) -> List[str] │         │
│  └────────────────────────────────────────────────┘         │
│                                                             │
│  Operations (Private):                                      │
│  ┌───────────────┬──────────────────┬──────────────────┐   │
│  │ _create_adr() │ _validate_adrs() │ _standardize_    │   │
│  │               │                  │  naming()         │   │
│  └───────────────┴──────────────────┴──────────────────┘   │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │ _update_index()      │ _update_references()         │   │
│  └──────────────────────┴──────────────────────────────┘   │
│                                                             │
│  Helper Methods:                                            │
│  ┌──────────────────┬────────────────┬───────────────────┐ │
│  │ _get_next_adr_   │ _to_snake_case │ _extract_front    │ │
│  │  number()        │ ()             │  matter_field()   │ │
│  └──────────────────┴────────────────┴───────────────────┘ │
│  ┌──────────────────┬────────────────┬───────────────────┐ │
│  │ _calculate_next_ │ _generate_     │ _update_all_      │ │
│  │  review_date()   │  index_content │  references_to_   │ │
│  │                  │ ()             │  underscores()    │ │
│  └──────────────────┴────────────────┴───────────────────┘ │
│                                                             │
│  Constants:                                                 │
│  - VALID_DOMAINS: List[str]                                │
│  - ADR_PATTERN: re.Pattern                                 │
│  - ADR_TEMPLATE: str                                       │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Class Hierarchy

```
Agent (from shared.agent_base)
  │
  └── SDLCAgent (from sdlc.base_agent)
        │
        ├── Properties:
        │   - name: str
        │   - phase: str
        │   - project_root: Path
        │   - output_dir: Path
        │
        ├── Abstract Methods:
        │   - run(input_data: Dict) -> Dict
        │   - validate_input(input_data: Dict) -> List[str]
        │
        └── ADRManagementAgent
              │
              ├── Properties:
              │   - VALID_DOMAINS: List[str] = [...]
              │   - ADR_PATTERN: re.Pattern
              │   - ADR_TEMPLATE: str
              │   - docs_dir: Path
              │   - index_path: Path
              │
              ├── Public Methods:
              │   - run(input_data: Dict) -> Dict
              │   - validate_input(input_data: Dict) -> List[str]
              │
              ├── Operation Methods:
              │   - _create_adr(adr_data: Dict) -> Dict
              │   - _validate_adrs(adr_paths: List[str]) -> Dict
              │   - _standardize_naming() -> Dict
              │   - _update_index() -> Dict
              │   - _update_references(old: str, new: str) -> Dict
              │
              └── Helper Methods:
                  - _get_next_adr_number() -> int
                  - _to_snake_case(text: str) -> str
                  - _extract_frontmatter_field(content, field, default) -> str
                  - _calculate_next_review_date(date_str, weeks) -> str
                  - _generate_index_content(by_domain, by_number) -> str
                  - _update_all_references_to_underscores() -> None
```

---

## 3. Data Flow

### 3.1 Create ADR Flow

```
┌─────────────┐
│  User Input │
│             │
│ operation:  │
│   "create"  │
│             │
│ adr_data:   │
│  - titulo   │
│  - dominio  │
│  - ...      │
└──────┬──────┘
       │
       v
┌──────────────────────┐
│ validate_input()     │
│                      │
│ - Check operation    │
│ - Check adr_data     │
│ - Check domain valid │
└──────┬───────────────┘
       │
       v  [Valid]
┌──────────────────────┐
│ run()                │
│   └─> _create_adr()  │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ _get_next_adr_      │
│  number()            │
│                      │
│ Scan docs/**/ADR_*   │
│ Find max number      │
│ Return max + 1       │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Generate filename    │
│                      │
│ ADR_{year}_{num}_    │
│ {snake_case_title}.md│
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Render template      │
│                      │
│ Fill in frontmatter  │
│ Fill in sections     │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Write to file        │
│                      │
│ docs/{domain}/       │
│   ADR_YYYY_XXX_*.md  │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ _update_index()      │
│                      │
│ Regenerate master    │
│ index                │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Return result        │
│                      │
│ - adr_id             │
│ - adr_path           │
│ - filename           │
│ - dominio            │
└──────────────────────┘
```

### 3.2 Validate ADRs Flow

```
┌─────────────┐
│  User Input │
│             │
│ operation:  │
│  "validate" │
│             │
│ adr_paths:  │
│  (optional) │
└──────┬──────┘
       │
       v
┌──────────────────────┐
│ run()                │
│   └─> _validate_     │
│       adrs()         │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Get ADR paths        │
│                      │
│ If paths provided:   │
│   Use those          │
│ Else:                │
│   Scan all domains   │
│   Find all ADR_*.md  │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ For each ADR:        │
│                      │
│ 1. Validate filename │
│    (ADR_YYYY_XXX_*)  │
│                      │
│ 2. Validate          │
│    frontmatter       │
│    - id: present     │
│    - estado: present │
│    - date: present   │
│                      │
│ 3. Validate sections │
│    - Contexto        │
│    - Decision        │
│    - Consecuencias   │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Collect results      │
│                      │
│ - total: int         │
│ - valid: int         │
│ - invalid: int       │
│ - errors: List[Dict] │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Return validation    │
│ results              │
└──────────────────────┘
```

### 3.3 Update Index Flow

```
┌─────────────┐
│  Trigger    │
│  (manual or │
│   auto)     │
└──────┬──────┘
       │
       v
┌──────────────────────┐
│ run()                │
│   └─> _update_       │
│       index()        │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Scan all domains     │
│                      │
│ For each domain:     │
│   Find ADR_*.md      │
│   Extract metadata:  │
│     - id, number     │
│     - titulo         │
│     - fecha, estado  │
│     - propietario    │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Build data structures│
│                      │
│ adrs_by_domain:      │
│   {domain: [adrs]}   │
│                      │
│ adrs_by_number:      │
│   {number: adr}      │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ _generate_index_     │
│  content()           │
│                      │
│ Generate markdown:   │
│ - Frontmatter        │
│ - Indice por Numero  │
│ - Indice por Dominio │
│ - Estadisticas       │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Write index file     │
│                      │
│ docs/gobernanza/     │
│   INDICE_ADRs.md     │
└──────┬───────────────┘
       │
       v
┌──────────────────────┐
│ Return result        │
│                      │
│ - index_path         │
│ - total_adrs         │
│ - by_domain counts   │
└──────────────────────┘
```

---

## 4. Component Details

### 4.1 ADRManagementAgent Class

**Responsibility**: Coordinate all ADR lifecycle operations

**Key Attributes**:
- `VALID_DOMAINS`: List of valid ADR domains
- `ADR_PATTERN`: Regex pattern for ADR filename validation
- `ADR_TEMPLATE`: Template string for new ADRs
- `docs_dir`: Path to docs directory
- `index_path`: Path to master index file

**Key Methods**:
- `run()`: Execute requested operation
- `validate_input()`: Validate operation parameters
- `_create_adr()`: Create new ADR
- `_validate_adrs()`: Validate existing ADRs
- `_standardize_naming()`: Standardize nomenclature
- `_update_index()`: Update master index
- `_update_references()`: Update references

### 4.2 Create ADR Operation

**Input**:
```python
{
    "operation": "create",
    "adr_data": {
        "titulo": str,
        "dominio": str,  # One of VALID_DOMAINS
        "decisores": str,
        "contexto_problema": str,
        "decision": str (optional),
        "consecuencias_positivas": str (optional),
        "consecuencias_negativas": str (optional),
        # ... other fields
    }
}
```

**Process**:
1. Get next ADR number (scan existing)
2. Generate ADR ID: `ADR_{year}_{number:03d}`
3. Convert title to snake_case
4. Render template with provided data
5. Write to `docs/{dominio}/ADR_{year}_{number}_{title}.md`
6. Update master index
7. Return result with path and ID

**Output**:
```python
{
    "operation": "create",
    "adr_id": "ADR_2025_022",
    "adr_path": "docs/backend/ADR_2025_022_sistema_permisos.md",
    "filename": "ADR_2025_022_sistema_permisos.md",
    "dominio": "backend"
}
```

### 4.3 Validate ADRs Operation

**Input**:
```python
{
    "operation": "validate",
    "adr_paths": List[str] (optional)  # If None, validate all
}
```

**Process**:
1. Determine ADR paths (provided or scan all)
2. For each ADR:
   a. Validate filename format (regex match)
   b. Validate frontmatter (YAML parsing)
   c. Validate required sections (string search)
3. Collect validation results
4. Return summary with errors

**Output**:
```python
{
    "operation": "validate",
    "validation_results": {
        "total": 21,
        "valid": 20,
        "invalid": 1,
        "errors": [
            {
                "file": "docs/backend/ADR-old-format.md",
                "error": "Formato de nombre invalido"
            }
        ]
    }
}
```

### 4.4 Standardize Naming Operation

**Input**:
```python
{
    "operation": "standardize"
}
```

**Process**:
1. Scan all domains for ADRs with old format (hyphens)
2. For each old-format ADR:
   a. Generate new filename (underscores)
   b. Read content
   c. Update ID in frontmatter (hyphens to underscores)
   d. Update title if contains old ID
   e. Write new file
   f. Delete old file
3. Update all references in documentation (global find-replace)
4. Update master index
5. Return count of renamed files

**Output**:
```python
{
    "operation": "standardize",
    "renamed_count": 3,
    "errors": []
}
```

### 4.5 Update Index Operation

**Input**:
```python
{
    "operation": "update_index"
}
```

**Process**:
1. Scan all domains for ADR_*.md files
2. Extract metadata from each ADR (frontmatter + content)
3. Build data structures:
   - `adrs_by_domain`: Dict[str, List[Dict]]
   - `adrs_by_number`: Dict[int, Dict]
4. Generate index markdown content
5. Write to `docs/gobernanza/INDICE_ADRs.md`
6. Return result with statistics

**Output**:
```python
{
    "operation": "update_index",
    "index_path": "docs/gobernanza/INDICE_ADRs.md",
    "total_adrs": 21,
    "by_domain": {
        "ai": 2,
        "backend": 8,
        "frontend": 6,
        "infraestructura": 6,
        "gobernanza": 1
    }
}
```

### 4.6 Update References Operation

**Input**:
```python
{
    "operation": "update_references",
    "old_reference": "ADR-2025-001",
    "new_reference": "ADR_2025_001"
}
```

**Process**:
1. Find all markdown files in docs/
2. For each file:
   a. Read content
   b. If old_reference found:
      - Replace with new_reference
      - Write updated content
      - Add to updated_files list
3. Return list of updated files

**Output**:
```python
{
    "operation": "update_references",
    "old_reference": "ADR-2025-001",
    "new_reference": "ADR_2025_001",
    "updated_files": [
        "docs/backend/IMPLEMENTACION_PERMISOS.md",
        "docs/gobernanza/INDICE_ADRs.md"
    ],
    "errors": []
}
```

---

## 5. Data Structures

### 5.1 ADR File Format

```markdown
---
id: ADR_YYYY_XXX
estado: propuesta | aceptada | rechazada | obsoleta
propietario: @equipo-nombre
ultima_actualizacion: YYYY-MM-DD
relacionados: ["ADR_YYYY_YYY", ...]
date: YYYY-MM-DD
---

# ADR_YYYY_XXX: Titulo del ADR

**Estado:** aceptada

**Fecha:** YYYY-MM-DD

**Decisores:** Nombre1, Nombre2

**Contexto tecnico:** Dominio1, Dominio2

## Contexto y Problema

Descripcion del contexto...

## Factores de Decision

| Factor | Peso | Descripcion |
|--------|------|-------------|
| ...    | ...  | ...         |

## Opciones Consideradas

### Opcion 1: ...

**Pros**: ...
**Contras**: ...

## Decision

Opcion elegida: ...

Justificacion: ...

## Consecuencias

### Positivas

- Consecuencia 1
- Consecuencia 2

### Negativas

- Consecuencia 1
- Consecuencia 2

## Referencias

- Referencia 1
- Referencia 2

---

**VERSION:** 1.0.0
**ESTADO:** aceptada
**PROXIMA REVISION:** YYYY-MM-DD
```

### 5.2 Validation Result Structure

```python
{
    "total": int,                    # Total ADRs validated
    "valid": int,                    # Count of valid ADRs
    "invalid": int,                  # Count of invalid ADRs
    "errors": [                      # List of errors
        {
            "file": str,             # Path to ADR file
            "error": str             # Error description
        },
        ...
    ]
}
```

### 5.3 ADR Metadata Structure

```python
{
    "id": str,                       # ADR_YYYY_XXX
    "number": int,                   # XXX (as integer)
    "titulo": str,                   # Title extracted from content
    "path": str,                     # Relative path from docs/
    "fecha": str,                    # YYYY-MM-DD
    "estado": str,                   # propuesta | aceptada | ...
    "dominio": str,                  # ai | backend | frontend | ...
    "propietario": str               # @equipo-nombre
}
```

---

## 6. Interfaces

### 6.1 CLI Interface

```bash
# Create new ADR
python scripts/cli/sdlc_agent.py \
  --phase adr_management \
  --operation create \
  --titulo "Sistema de Permisos Granular" \
  --dominio backend \
  --decisores "Arquitecto Senior, Tech Lead" \
  --contexto "Necesitamos permisos flexibles"

# Validate all ADRs
python scripts/cli/sdlc_agent.py \
  --phase adr_management \
  --operation validate

# Standardize nomenclature
python scripts/cli/sdlc_agent.py \
  --phase adr_management \
  --operation standardize

# Update master index
python scripts/cli/sdlc_agent.py \
  --phase adr_management \
  --operation update_index

# Update references
python scripts/cli/sdlc_agent.py \
  --phase adr_management \
  --operation update_references \
  --old-reference "ADR-2025-001" \
  --new-reference "ADR_2025_001"
```

### 6.2 Programmatic Interface

```python
from scripts.coding.ai.sdlc.adr_management_agent import ADRManagementAgent

# Initialize agent
config = {"project_root": "/path/to/project"}
agent = ADRManagementAgent(config=config)

# Create ADR
result = agent.execute({
    "operation": "create",
    "adr_data": {
        "titulo": "Sistema de Permisos Granular",
        "dominio": "backend",
        "decisores": "Arquitecto Senior",
        "contexto_problema": "..."
    }
})

if result.status == AgentStatus.SUCCESS:
    print(f"ADR created: {result.output['adr_path']}")
else:
    print(f"Error: {result.error}")

# Validate ADRs
result = agent.execute({"operation": "validate"})

# Update index
result = agent.execute({"operation": "update_index"})
```

---

## 7. Error Handling

### 7.1 Error Types

| Error Type | Example | Handling Strategy |
|------------|---------|-------------------|
| **Input Validation** | Missing required field | Return error with clear message |
| **File System** | Permission denied | Graceful failure with error details |
| **Format** | Invalid frontmatter YAML | Log error, mark ADR as invalid |
| **Domain** | Invalid domain name | Reject with list of valid domains |
| **Number** | Number gap in sequence | Warning (not error), continue |
| **Reference** | Broken ADR reference | Report but don't block operation |

### 7.2 Error Response Format

```python
{
    "status": "error",
    "error_code": "INVALID_INPUT | FILE_ERROR | FORMAT_ERROR | ...",
    "error_message": str,
    "details": Dict,  # Additional context
    "recoverable": bool,  # Can user fix and retry?
    "suggestions": List[str]  # How to fix
}
```

---

## 8. Performance Considerations

### 8.1 Performance Requirements

| Operation | Target | Max ADRs | Constraint |
|-----------|--------|----------|------------|
| Create ADR | < 1s | N/A | Single file write |
| Validate ADRs | < 3s | 50 | File read + regex |
| Standardize | < 5s | 21 | File rename + update |
| Update Index | < 2s | 50 | Scan + generate |
| Update References | < 5s | 500 docs | Find-replace |

### 8.2 Optimization Strategies

1. **Lazy Loading**: Only load ADR content when needed (not for index scanning)
2. **Caching**: Cache index data in memory during bulk operations
3. **Batch Processing**: Process ADRs in batches for validation
4. **Early Exit**: Stop validation on first error (optional dry-run mode)
5. **Regex Optimization**: Compile regex patterns once at initialization

---

## 9. Security Considerations

### 9.1 Security Threats

| Threat | Risk | Mitigation |
|--------|------|------------|
| **Path Traversal** | MEDIUM | Validate paths are within docs/ |
| **Code Injection** | LOW | No eval/exec, only template rendering |
| **File Overwrite** | MEDIUM | Check file exists before create |
| **Permission Issues** | LOW | Graceful error handling |
| **Malicious Input** | LOW | Input validation, sanitization |

### 9.2 Security Controls

1. **Input Validation**: Strict validation of all inputs (operation, domain, paths)
2. **Path Validation**: Ensure all paths are within project docs/
3. **File Existence Checks**: Check before overwriting files
4. **No Shell Execution**: Pure Python file operations, no shell commands
5. **Error Messages**: Don't expose sensitive file system details

---

## 10. Extensibility

### 10.1 Future Enhancements

**Priority 1** (Next Sprint):
- Dry-run mode for all operations
- Batch create from CSV/JSON
- ADR template customization per domain

**Priority 2** (Future):
- Git integration (auto-commit after operations)
- ADR status workflow (propuesta -> aceptada)
- Webhook notifications
- Metrics dashboard

**Priority 3** (Nice to Have):
- Multi-language support (English, Spanish, French)
- ADR diff viewer
- ADR search and query DSL
- Integration with issue trackers (JIRA, GitHub Issues)

### 10.2 Extension Points

1. **Template System**: Allow custom ADR templates per domain
2. **Validators**: Pluggable validators for different ADR formats
3. **Outputs**: Support multiple index formats (Markdown, HTML, JSON)
4. **Storage**: Abstract file system operations for cloud storage support

---

## 11. Dependencies

### 11.1 Internal Dependencies

- `scripts.coding.ai.sdlc.base_agent.SDLCAgent` - Base class
- `scripts.coding.ai.shared.agent_base.Agent` - Root agent class
- `scripts.cli.sdlc_agent.py` - CLI entry point

### 11.2 External Dependencies

**Python Standard Library**:
- `pathlib` - File path operations
- `re` - Regular expressions
- `datetime` - Date/time operations
- `typing` - Type hints

**Testing**:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting

**No Third-Party Dependencies Required**

---

## 12. Testing Strategy

### 12.1 Test Coverage Goals

- **Unit Tests**: >= 90% line coverage
- **Integration Tests**: All 5 operations end-to-end
- **Edge Cases**: Invalid inputs, file errors, format errors
- **Performance Tests**: Operations complete within targets

### 12.2 Test Structure

```
tests/ai/sdlc/test_adr_management_agent.py
  ├── TestInitialization
  ├── TestInputValidation
  ├── TestADRCreation
  ├── TestADRValidation
  ├── TestStandardization
  ├── TestIndexMaintenance
  ├── TestReferenceUpdate
  ├── TestIntegration
  ├── TestEdgeCases
  └── TestHelperMethods
```

### 12.3 Test Fixtures

- `temp_project`: Temporary project directory structure
- `agent`: Configured ADRManagementAgent instance
- `sample_adr_data`: Valid ADR data for creation
- `existing_adr`: Pre-created ADR file
- `old_format_adr`: ADR with old format (hyphens)

---

## 13. Monitoring and Logging

### 13.1 Logging Strategy

**Log Levels**:
- **INFO**: Operation start/complete, files created/modified
- **WARNING**: Non-blocking issues (format warnings, missing metadata)
- **ERROR**: Operation failures, validation errors
- **DEBUG**: Detailed operation steps (for development)

**Log Format**:
```
[YYYY-MM-DD HH:MM:SS] ADRManagementAgent - LEVEL - message
```

### 13.2 Metrics (if DORA integration enabled)

- `adr_created_count`: Total ADRs created
- `adr_validation_errors`: Count of validation errors
- `adr_operations_duration`: Operation execution time
- `adr_index_update_count`: Index update frequency

---

## 14. Deployment Considerations

### 14.1 Deployment Requirements

- Python 3.10+ environment
- Read/write access to `docs/` directory
- Git repository (optional, for version control)

### 14.2 Installation Steps

1. No installation required (part of project)
2. Ensure `scripts/coding/ai/sdlc/adr_management_agent.py` exists
3. Test CLI access: `python scripts/cli/sdlc_agent.py --help`

### 14.3 Configuration

**Minimal Configuration**:
```python
config = {
    "project_root": "/path/to/project"
}
```

**Advanced Configuration** (future):
```python
config = {
    "project_root": "/path/to/project",
    "adr_template_path": "custom_template.md",
    "index_path": "custom/index.md",
    "enable_dora_metrics": True
}
```

---

## 15. Maintenance

### 15.1 Maintenance Tasks

**Weekly**:
- Run validation on all ADRs
- Update master index
- Check for orphaned references

**Monthly**:
- Review validation errors
- Update ADR template if needed
- Audit ADR status (propuesta -> aceptada)

**Quarterly**:
- Review agent performance metrics
- Update documentation
- Plan enhancements

### 15.2 Known Limitations

1. **Sequential Numbering**: Numbers are assigned sequentially, gaps are not filled
2. **Single Language**: ADR content in Spanish/English only
3. **No Workflow**: No built-in status transition workflow
4. **Manual Content**: Agent provides structure, humans write content
5. **No Versioning**: ADRs are not versioned (use git for history)

---

## 16. References

### 16.1 Related Documentation

- ISSUE_ADR_MANAGEMENT_AGENT.md - Feature request and requirements
- FEASIBILITY_ANALYSIS_ADR_MANAGEMENT_AGENT.md - Feasibility analysis
- ADR_2025_003 - DORA SDLC Integration (agent pattern)
- ADR_2025_014 - Organizacion Proyecto por Dominio

### 16.2 Related Code

- `scripts/coding/ai/sdlc/base_agent.py` - SDLCAgent base class
- `scripts/coding/ai/sdlc/planner_agent.py` - Example SDLC agent
- `scripts/cli/sdlc_agent.py` - CLI entry point
- `docs/gobernanza/plantilla_adr.md` - ADR template

---

**Document Status**: Draft (awaiting review)
**Next Phase**: Low-Level Design (LLD)
**Last Updated**: 2025-11-13
**Version**: 1.0.0
