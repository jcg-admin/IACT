---
title: Low-Level Design - ADR Management Agent
date: 2025-11-13
issue_number: IACT-ADR-AGENT-001
phase: design
type: lld
status: draft
domain: ai
version: 1.0.0
---

# Low-Level Design: ADR Management Agent

**Issue**: IACT-ADR-AGENT-001
**Phase**: DESIGN (Phase 3 of 6)
**Document Type**: Low-Level Design (LLD)
**Author**: Claude AI Agent
**Date**: 2025-11-13
**Version**: 1.0.0
**Status**: Draft

---

## 1. Overview

This document provides detailed implementation specifications for the ADR Management Agent, including algorithms, data structures, pseudo-code, and edge case handling.

**Reference Documents**:
- High-Level Design (HLD): `hld_adr_management_agent.md`
- Feature Request: `ISSUE_ADR_MANAGEMENT_AGENT.md`
- Feasibility Analysis: `FEASIBILITY_ANALYSIS_ADR_MANAGEMENT_AGENT.md`

---

## 2. Class Implementation

### 2.1 ADRManagementAgent Class Definition

```python
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from scripts.coding.ai.sdlc.base_agent import SDLCAgent, SDLCPhaseResult


class ADRManagementAgent(SDLCAgent):
    """
    SDLC Agent for managing Architecture Decision Records (ADRs).

    Capabilities:
    - create: Create new ADR with standard format
    - validate: Validate existing ADRs for compliance
    - standardize: Standardize nomenclature (hyphens to underscores)
    - update_index: Update master index
    - update_references: Update ADR references in documentation
    """

    # Class constants
    VALID_DOMAINS = ["ai", "backend", "frontend", "infraestructura", "gobernanza"]

    # Regex pattern for valid ADR filenames: ADR_YYYY_XXX_description.md
    ADR_PATTERN = re.compile(r'^ADR_(\d{4})_(\d{3})_(.+)\.md$')

    # Old format pattern (hyphens): ADR-YYYY-XXX-description.md
    OLD_PATTERN = re.compile(r'^ADR-(\d{4})-(\d{3})-(.+)\.md$')

    # ADR template (see section 2.2 for full template)
    ADR_TEMPLATE = """..."""  # See below

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize ADRManagementAgent.

        Args:
            config: Configuration dictionary
                - project_root: str (default: ".")
        """
        super().__init__(
            name="ADRManagementAgent",
            phase="documentation",
            config=config
        )

        # Initialize paths
        self.project_root = Path(self.config.get("project_root", "."))
        self.docs_dir = self.project_root / "docs"
        self.index_path = self.docs_dir / "gobernanza" / "INDICE_ADRs.md"

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Apply custom guardrails for ADR operations.

        Args:
            output_data: Output data from operation

        Returns:
            List of guardrail violations (empty if all pass)
        """
        errors = []
        operation = output_data.get("operation", "")

        if operation == "create":
            # Validate ADR was created
            if "adr_path" not in output_data:
                errors.append("No ADR path in output")

            # Validate filename format
            adr_path = output_data.get("adr_path", "")
            if adr_path:
                filename = Path(adr_path).name
                if not self.ADR_PATTERN.match(filename):
                    errors.append(f"Invalid ADR filename format: {filename}")

        elif operation == "validate":
            # Validate results exist
            if "validation_results" not in output_data:
                errors.append("No validation results in output")

        return errors

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Validate input data for ADR operations.

        Args:
            input_data: Input data dictionary

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check operation exists
        if "operation" not in input_data:
            errors.append("Falta 'operation' en input")
            return errors

        operation = input_data["operation"]
        valid_operations = ["create", "validate", "standardize", "update_index", "update_references"]

        if operation not in valid_operations:
            errors.append(f"Operation invalida: {operation}. Validas: {valid_operations}")
            return errors

        # Operation-specific validation
        if operation == "create":
            errors.extend(self._validate_create_input(input_data))
        elif operation == "update_references":
            errors.extend(self._validate_update_references_input(input_data))

        return errors

    def _validate_create_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input for create operation."""
        errors = []

        if "adr_data" not in input_data:
            errors.append("Falta 'adr_data' para operation create")
            return errors

        adr_data = input_data["adr_data"]

        # Required fields
        required = ["titulo", "dominio", "decisores", "contexto_problema"]
        for field in required:
            if field not in adr_data or not adr_data[field]:
                errors.append(f"Falta campo requerido en adr_data: {field}")

        # Validate domain
        dominio = adr_data.get("dominio", "")
        if dominio and dominio not in self.VALID_DOMAINS:
            errors.append(f"Dominio invalido: {dominio}. Validos: {self.VALID_DOMAINS}")

        return errors

    def _validate_update_references_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Validate input for update_references operation."""
        errors = []

        if "old_reference" not in input_data or not input_data["old_reference"]:
            errors.append("Falta 'old_reference' para operation update_references")

        if "new_reference" not in input_data or not input_data["new_reference"]:
            errors.append("Falta 'new_reference' para operation update_references")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ADR management operation.

        Args:
            input_data: {
                "operation": str,  # create | validate | standardize | update_index | update_references
                "adr_data": Dict,  # For create
                "adr_paths": List[str],  # For validate
                "old_reference": str,  # For update_references
                "new_reference": str,  # For update_references
            }

        Returns:
            Dict with operation results
        """
        operation = input_data["operation"]

        self.logger.info(f"Executing ADR operation: {operation}")

        try:
            if operation == "create":
                return self._create_adr(input_data["adr_data"])
            elif operation == "validate":
                return self._validate_adrs(input_data.get("adr_paths", None))
            elif operation == "standardize":
                return self._standardize_naming()
            elif operation == "update_index":
                return self._update_index()
            elif operation == "update_references":
                old_ref = input_data["old_reference"]
                new_ref = input_data["new_reference"]
                return self._update_references(old_ref, new_ref)
            else:
                return {"error": f"Operation not implemented: {operation}"}
        except Exception as e:
            self.logger.error(f"Operation {operation} failed: {e}")
            return {"error": str(e)}
```

### 2.2 ADR Template Constant

```python
ADR_TEMPLATE = """---
id: {adr_id}
estado: {estado}
propietario: {propietario}
ultima_actualizacion: {fecha}
relacionados: {relacionados}
date: {fecha}
---

# {adr_id}: {titulo}

**Estado:** {estado}

**Fecha:** {fecha}

**Decisores:** {decisores}

**Contexto tecnico:** {contexto_tecnico}

## Contexto y Problema

{contexto_problema}

## Factores de Decision

{factores}

## Opciones Consideradas

{opciones}

## Decision

{decision}

## Consecuencias

### Positivas

{consecuencias_positivas}

### Negativas

{consecuencias_negativas}

## Referencias

{referencias}

---

**VERSION:** {version}
**ESTADO:** {estado}
**PROXIMA REVISION:** {proxima_revision}
"""
```

---

## 3. Operation Implementations

### 3.1 Create ADR Operation

#### 3.1.1 Algorithm

```
FUNCTION _create_adr(adr_data: Dict) -> Dict:
    // Step 1: Get next sequential number
    next_number = _get_next_adr_number()

    // Step 2: Generate ADR ID
    year = current_year()
    adr_id = format("ADR_{year}_{next_number:03d}")

    // Step 3: Generate filename
    titulo_slug = _to_snake_case(adr_data["titulo"])
    filename = format("{adr_id}_{titulo_slug}.md")

    // Step 4: Determine domain directory
    dominio = adr_data["dominio"]
    domain_dir = docs_dir / dominio

    IF NOT domain_dir.exists():
        RETURN {"error": "Directorio de dominio no existe"}

    adr_path = domain_dir / filename

    // Step 5: Prepare template data
    fecha = today()
    relacionados = adr_data.get("relacionados", [])

    template_data = {
        "adr_id": adr_id,
        "titulo": adr_data["titulo"],
        "estado": adr_data.get("estado", "propuesta"),
        "propietario": adr_data.get("propietario", "@equipo-arquitectura"),
        "fecha": fecha,
        "relacionados": str(relacionados),
        "decisores": adr_data["decisores"],
        "contexto_tecnico": adr_data.get("contexto_tecnico", ""),
        "contexto_problema": adr_data["contexto_problema"],
        "factores": adr_data.get("factores", ""),
        "opciones": adr_data.get("opciones", ""),
        "decision": adr_data.get("decision", ""),
        "consecuencias_positivas": adr_data.get("consecuencias_positivas", ""),
        "consecuencias_negativas": adr_data.get("consecuencias_negativas", ""),
        "referencias": adr_data.get("referencias", ""),
        "version": "1.0.0",
        "proxima_revision": calculate_next_review_date(fecha, weeks=4)
    }

    // Step 6: Render template
    content = ADR_TEMPLATE.format(**template_data)

    // Step 7: Write file
    adr_path.write_text(content, encoding="utf-8")

    logger.info(f"ADR created: {adr_path}")

    // Step 8: Update index
    _update_index()

    // Step 9: Return result
    RETURN {
        "operation": "create",
        "adr_id": adr_id,
        "adr_path": str(adr_path),
        "filename": filename,
        "dominio": dominio
    }
END FUNCTION
```

#### 3.1.2 Implementation Details

**Step 1: Get Next ADR Number**

```python
def _get_next_adr_number(self) -> int:
    """
    Get next sequential ADR number.

    Algorithm:
    1. Scan all domain directories
    2. Find all files matching ADR_YYYY_XXX_*.md
    3. Extract XXX (number) from each
    4. Return max + 1

    Returns:
        Next available ADR number (001-999)
    """
    max_number = 0

    for domain in self.VALID_DOMAINS:
        domain_dir = self.docs_dir / domain
        if not domain_dir.exists():
            continue

        # Find all ADR files
        for adr_path in domain_dir.glob("ADR_*.md"):
            match = self.ADR_PATTERN.match(adr_path.name)
            if match:
                year, number, description = match.groups()
                max_number = max(max_number, int(number))

    return max_number + 1
```

**Edge Cases**:
- No existing ADRs: Returns 1
- Gaps in sequence (e.g., 001, 002, 005): Returns max + 1 (006), gaps are preserved
- Multiple domains: Scans all, finds global max
- Invalid filenames: Ignored (won't match pattern)

**Step 3: Convert to Snake Case**

```python
def _to_snake_case(self, text: str) -> str:
    """
    Convert text to snake_case.

    Algorithm:
    1. Remove special characters (keep alphanumeric, spaces, hyphens)
    2. Replace spaces and hyphens with underscores
    3. Lowercase
    4. Remove consecutive underscores

    Args:
        text: Input text

    Returns:
        snake_case version

    Examples:
        "Sistema de Permisos" -> "sistema_de_permisos"
        "React-Native Setup" -> "react_native_setup"
        "API Gateway (v2)" -> "api_gateway_v2"
    """
    # Remove special characters (keep alphanumeric, spaces, hyphens)
    text = re.sub(r'[^\w\s-]', '', text)

    # Replace spaces and hyphens with underscores
    text = re.sub(r'[-\s]+', '_', text)

    # Lowercase
    text = text.lower()

    # Remove consecutive underscores
    text = re.sub(r'_+', '_', text)

    # Remove leading/trailing underscores
    text = text.strip('_')

    return text
```

**Test Cases**:
```python
assert _to_snake_case("Sistema de Permisos") == "sistema_de_permisos"
assert _to_snake_case("React-Native Setup") == "react_native_setup"
assert _to_snake_case("API Gateway (v2)") == "api_gateway_v2"
assert _to_snake_case("  Multiple   Spaces  ") == "multiple_spaces"
assert _to_snake_case("UPPERCASE") == "uppercase"
```

### 3.2 Validate ADRs Operation

#### 3.2.1 Algorithm

```
FUNCTION _validate_adrs(adr_paths: Optional[List[str]]) -> Dict:
    // Step 1: Determine paths to validate
    IF adr_paths IS None:
        adr_paths = _find_all_adr_paths()

    validation_results = {
        "total": len(adr_paths),
        "valid": 0,
        "invalid": 0,
        "errors": []
    }

    // Step 2: Validate each ADR
    FOR EACH adr_path_str IN adr_paths:
        adr_path = Path(adr_path_str)
        filename = adr_path.name

        // Validation 1: Filename format
        match = ADR_PATTERN.match(filename)
        IF NOT match:
            validation_results["invalid"] += 1
            validation_results["errors"].append({
                "file": str(adr_path),
                "error": "Formato de nombre invalido"
            })
            CONTINUE

        // Validation 2: File readable
        TRY:
            content = adr_path.read_text(encoding="utf-8")
        EXCEPT Exception as e:
            validation_results["invalid"] += 1
            validation_results["errors"].append({
                "file": str(adr_path),
                "error": f"Error al leer: {e}"
            })
            CONTINUE

        // Validation 3: Frontmatter exists
        IF NOT content.startswith("---"):
            validation_results["invalid"] += 1
            validation_results["errors"].append({
                "file": str(adr_path),
                "error": "Falta frontmatter YAML"
            })
            CONTINUE

        // Validation 4: Required frontmatter fields
        required_fields = ["id:", "estado:", "date:"]
        missing_fields = []
        FOR EACH field IN required_fields:
            IF field NOT IN content[:500]:  // Check first 500 chars
                missing_fields.append(field)

        IF missing_fields NOT EMPTY:
            validation_results["invalid"] += 1
            validation_results["errors"].append({
                "file": str(adr_path),
                "error": f"Faltan campos: {missing_fields}"
            })
            CONTINUE

        // Validation 5: Required sections
        required_sections = [
            "## Contexto y Problema",
            "## Decision",
            "## Consecuencias"
        ]
        missing_sections = []
        FOR EACH section IN required_sections:
            IF section NOT IN content:
                missing_sections.append(section)

        IF missing_sections NOT EMPTY:
            validation_results["invalid"] += 1
            validation_results["errors"].append({
                "file": str(adr_path),
                "error": f"Faltan secciones: {missing_sections}"
            })
            CONTINUE

        // All validations passed
        validation_results["valid"] += 1

    // Step 3: Return results
    RETURN {
        "operation": "validate",
        "validation_results": validation_results
    }
END FUNCTION
```

#### 3.2.2 Validation Rules

| Rule | Check | Pass Criteria | Failure Message |
|------|-------|---------------|-----------------|
| **R1: Filename Format** | Regex match `ADR_YYYY_XXX_*.md` | Matches pattern | "Formato de nombre invalido" |
| **R2: File Readable** | Can read file with UTF-8 encoding | No exception | "Error al leer: {exception}" |
| **R3: Frontmatter** | Content starts with `---` | First 3 chars are `---` | "Falta frontmatter YAML" |
| **R4: Required Fields** | `id:`, `estado:`, `date:` present | All fields in first 500 chars | "Faltan campos: {list}" |
| **R5: Required Sections** | Contexto, Decision, Consecuencias | All sections present | "Faltan secciones: {list}" |

#### 3.2.3 Helper Function: Find All ADR Paths

```python
def _find_all_adr_paths(self) -> List[str]:
    """
    Find all ADR file paths across all domains.

    Returns:
        List of absolute paths to ADR files
    """
    adr_paths = []

    for domain in self.VALID_DOMAINS:
        domain_dir = self.docs_dir / domain
        if domain_dir.exists():
            # Find all files starting with "ADR_"
            for adr_path in domain_dir.glob("ADR_*.md"):
                adr_paths.append(str(adr_path))

    return adr_paths
```

### 3.3 Standardize Naming Operation

#### 3.3.1 Algorithm

```
FUNCTION _standardize_naming() -> Dict:
    renamed_count = 0
    errors = []

    // Pattern for old format: ADR-YYYY-XXX-description.md
    old_pattern = compile_regex(r'^ADR-(\d{4})-(\d{3})-(.+)\.md$')

    // Step 1: Scan all domains for old-format ADRs
    FOR EACH domain IN VALID_DOMAINS:
        domain_dir = docs_dir / domain
        IF NOT domain_dir.exists():
            CONTINUE

        // Find all ADR- files (old format)
        FOR EACH adr_path IN domain_dir.glob("ADR-*.md"):
            filename = adr_path.name
            match = old_pattern.match(filename)

            IF NOT match:
                CONTINUE  // Not an ADR file

            year, number, description = match.groups()

            // Step 2: Generate new filename
            new_filename = f"ADR_{year}_{number}_{description}.md"
            new_path = adr_path.parent / new_filename

            TRY:
                // Step 3: Read content
                content = adr_path.read_text(encoding="utf-8")

                // Step 4: Update ID in frontmatter
                new_id = f"ADR_{year}_{number}"
                content = regex_replace(
                    pattern=r'^id:\s*ADR-\d{4}-\d{3}.*$',
                    replacement=f'id: {new_id}',
                    string=content,
                    flags=MULTILINE
                )

                // Step 5: Update title if contains old ID
                content = regex_replace(
                    pattern=r'^#\s*ADR-(\d{4})-(\d{3}):',
                    replacement=f'# {new_id}:',
                    string=content,
                    flags=MULTILINE
                )

                // Step 6: Write new file
                new_path.write_text(content, encoding="utf-8")

                // Step 7: Delete old file
                adr_path.unlink()

                renamed_count += 1
                logger.info(f"Renamed: {filename} -> {new_filename}")

            EXCEPT Exception as e:
                errors.append({
                    "file": str(adr_path),
                    "error": str(e)
                })

    // Step 8: Update all references in documentation
    IF renamed_count > 0:
        _update_all_references_to_underscores()
        _update_index()

    // Step 9: Return result
    RETURN {
        "operation": "standardize",
        "renamed_count": renamed_count,
        "errors": errors
    }
END FUNCTION
```

#### 3.3.2 Reference Update Algorithm

```python
def _update_all_references_to_underscores(self) -> None:
    """
    Update all references from hyphen format to underscore format.

    Finds patterns like "ADR-2025-001" and replaces with "ADR_2025_001".
    """
    # Pattern: ADR-YYYY-XXX
    pattern = re.compile(r'ADR-(\d{4})-(\d{3})')

    # Scan all markdown files
    for md_file in self.docs_dir.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")

            # Replace all occurrences
            new_content = pattern.sub(r'ADR_\1_\2', content)

            if new_content != content:
                md_file.write_text(new_content, encoding="utf-8")
                self.logger.info(f"Updated references in: {md_file.name}")

        except Exception as e:
            self.logger.warning(f"Error updating {md_file}: {e}")
```

### 3.4 Update Index Operation

#### 3.4.1 Algorithm

```
FUNCTION _update_index() -> Dict:
    adrs_by_domain = {}
    adrs_by_number = {}

    // Step 1: Scan all ADRs across domains
    FOR EACH domain IN VALID_DOMAINS:
        domain_dir = docs_dir / domain
        IF NOT domain_dir.exists():
            CONTINUE

        domain_adrs = []

        FOR EACH adr_path IN sorted(domain_dir.glob("ADR_*.md")):
            filename = adr_path.name
            match = ADR_PATTERN.match(filename)

            IF NOT match:
                CONTINUE

            year, number, description = match.groups()
            adr_id = f"ADR_{year}_{number}"

            // Step 2: Extract metadata from ADR
            TRY:
                content = adr_path.read_text(encoding="utf-8")

                estado = _extract_frontmatter_field(content, "estado", "aceptada")
                fecha = _extract_frontmatter_field(content, "date", "")
                propietario = _extract_frontmatter_field(content, "propietario", "")

                // Extract title from heading
                titulo_match = regex_search(r'^#\s*ADR_\d{4}_\d{3}:\s*(.+)$', content, MULTILINE)
                titulo = titulo_match.group(1) IF titulo_match ELSE description.replace("_", " ").title()

                adr_info = {
                    "id": adr_id,
                    "number": int(number),
                    "titulo": titulo,
                    "path": str(adr_path.relative_to(docs_dir)),
                    "fecha": fecha,
                    "estado": estado,
                    "dominio": domain,
                    "propietario": propietario
                }

                domain_adrs.append(adr_info)
                adrs_by_number[int(number)] = adr_info

            EXCEPT Exception as e:
                logger.warning(f"Error reading {adr_path}: {e}")

        IF domain_adrs NOT EMPTY:
            adrs_by_domain[domain] = domain_adrs

    // Step 3: Generate index content
    index_content = _generate_index_content(adrs_by_domain, adrs_by_number)

    // Step 4: Write index file
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(index_content, encoding="utf-8")

    logger.info(f"Index updated: {index_path}")

    // Step 5: Return result
    RETURN {
        "operation": "update_index",
        "index_path": str(index_path),
        "total_adrs": len(adrs_by_number),
        "by_domain": {domain: len(adrs) for domain, adrs in adrs_by_domain.items()}
    }
END FUNCTION
```

#### 3.4.2 Metadata Extraction

```python
def _extract_frontmatter_field(self, content: str, field: str, default: str = "") -> str:
    """
    Extract a field from YAML frontmatter.

    Args:
        content: Full file content
        field: Field name (without colon)
        default: Default value if not found

    Returns:
        Field value or default

    Algorithm:
    1. Search for pattern "field: value" in content
    2. Extract value (strip whitespace)
    3. Return value or default if not found
    """
    pattern = rf'^{field}:\s*(.+)$'
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default
```

**Example**:
```python
content = """---
id: ADR_2025_001
estado: aceptada
propietario: @equipo-backend
---
..."""

_extract_frontmatter_field(content, "estado")  # Returns: "aceptada"
_extract_frontmatter_field(content, "missing")  # Returns: ""
_extract_frontmatter_field(content, "missing", "default")  # Returns: "default"
```

#### 3.4.3 Index Content Generation

```python
def _generate_index_content(
    self,
    adrs_by_domain: Dict[str, List[Dict]],
    adrs_by_number: Dict[int, Dict]
) -> str:
    """
    Generate markdown content for master index.

    Args:
        adrs_by_domain: ADRs grouped by domain
        adrs_by_number: ADRs keyed by number

    Returns:
        Full markdown content for index
    """
    total_adrs = len(adrs_by_number)
    fecha = datetime.now().strftime("%Y-%m-%d")

    content = f"""---
title: Indice Maestro de Architecture Decision Records (ADRs)
date: {fecha}
domain: gobernanza
tipo: indice
status: active
---

# Indice Maestro de ADRs

Este documento contiene el indice completo de todas las decisiones arquitectonicas del proyecto IACT.

**Ultima actualizacion**: {fecha}
**Total ADRs**: {total_adrs}

---

## Sistema de Numeracion

**Formato Estandar**: `ADR_YYYY_XXX_descripcion.md`

- **YYYY**: Año de la decision
- **XXX**: Numero secuencial (001-999)
- **descripcion**: Descripcion corta en snake_case (guiones bajos)

---

## Indice por Numero

"""

    # ADRs sorted by number
    for number in sorted(adrs_by_number.keys()):
        adr = adrs_by_number[number]
        content += f"""### {adr['id']}: {adr['titulo']}
**Ubicacion**: `{adr['path']}`
**Fecha**: {adr['fecha']}
**Estado**: {adr['estado']}
**Dominio**: {adr['dominio'].title()}
**Propietario**: {adr['propietario']}

---

"""

    # Index by domain
    content += "## Indice por Dominio\n\n"
    for domain in sorted(adrs_by_domain.keys()):
        domain_adrs = adrs_by_domain[domain]
        content += f"### {domain.title()} ({len(domain_adrs)} ADRs)\n"
        for adr in sorted(domain_adrs, key=lambda x: x['number']):
            content += f"- {adr['id']}: {adr['titulo']}\n"
        content += "\n"

    # Statistics
    content += f"""---

## Estadisticas

**Total ADRs**: {total_adrs}
**Por Dominio**:
"""
    for domain in sorted(adrs_by_domain.keys()):
        count = len(adrs_by_domain[domain])
        percentage = (count / total_adrs * 100) if total_adrs > 0 else 0
        content += f"- {domain.title()}: {count} ({percentage:.1f}%)\n"

    content += f"""
---

**Ultima actualizacion**: {fecha}
**Responsable**: @arquitecto-senior @tech-lead
**Proxima revision**: {self._calculate_next_review_date(fecha, weeks=4)}
"""

    return content
```

### 3.5 Update References Operation

#### 3.5.1 Algorithm

```
FUNCTION _update_references(old_reference: str, new_reference: str) -> Dict:
    updated_files = []
    errors = []

    // Step 1: Find all markdown files
    FOR EACH md_file IN docs_dir.rglob("*.md"):
        TRY:
            // Step 2: Read content
            content = md_file.read_text(encoding="utf-8")

            // Step 3: Check if old reference exists
            IF old_reference NOT IN content:
                CONTINUE  // Skip, no matches

            // Step 4: Replace old with new
            new_content = content.replace(old_reference, new_reference)

            // Step 5: Write updated content
            md_file.write_text(new_content, encoding="utf-8")

            // Step 6: Track updated file
            updated_files.append(str(md_file.relative_to(docs_dir)))

        EXCEPT Exception as e:
            errors.append({
                "file": str(md_file),
                "error": str(e)
            })

    logger.info(f"Updated references in {len(updated_files)} files")

    // Step 7: Return result
    RETURN {
        "operation": "update_references",
        "old_reference": old_reference,
        "new_reference": new_reference,
        "updated_files": updated_files,
        "errors": errors
    }
END FUNCTION
```

#### 3.5.2 Edge Cases

| Case | Behavior | Example |
|------|----------|---------|
| No matches | Return empty updated_files | `old_reference` not found in any file |
| Multiple matches in one file | Replace all occurrences | File has 3 refs, all replaced |
| File read error | Add to errors, continue | Permission denied |
| File write error | Add to errors, continue | Disk full |
| Binary files | Skip (glob only finds .md) | Images, PDFs ignored |

---

## 4. Helper Methods

### 4.1 Calculate Next Review Date

```python
def _calculate_next_review_date(self, date_str: str, weeks: int = 4) -> str:
    """
    Calculate next review date from given date.

    Args:
        date_str: Date in YYYY-MM-DD format
        weeks: Number of weeks to add (default: 4)

    Returns:
        Next review date in YYYY-MM-DD format

    Example:
        _calculate_next_review_date("2025-11-13", 4)  # Returns: "2025-12-11"
    """
    from datetime import datetime, timedelta

    date = datetime.strptime(date_str, "%Y-%m-%d")
    next_date = date + timedelta(weeks=weeks)
    return next_date.strftime("%Y-%m-%d")
```

---

## 5. Error Handling

### 5.1 Exception Hierarchy

```
Exception
  ├── ADRManagementError (base)
  │   ├── ADRValidationError
  │   │   ├── InvalidFilenameError
  │   │   ├── MissingFrontmatterError
  │   │   └── MissingSectionError
  │   ├── ADRFileError
  │   │   ├── FileNotFoundError (stdlib)
  │   │   ├── PermissionError (stdlib)
  │   │   └── FileExistsError (stdlib)
  │   └── ADRDomainError
  │       └── InvalidDomainError
```

### 5.2 Error Handling Patterns

**Pattern 1: Try-Except with Logging**
```python
try:
    content = adr_path.read_text(encoding="utf-8")
except Exception as e:
    self.logger.error(f"Failed to read {adr_path}: {e}")
    return {"error": f"File read error: {e}"}
```

**Pattern 2: Collect Errors, Continue Processing**
```python
errors = []
for item in items:
    try:
        process(item)
    except Exception as e:
        errors.append({"item": item, "error": str(e)})
        continue  # Process remaining items
return {"errors": errors}
```

**Pattern 3: Validation with Early Return**
```python
errors = validate_input(input_data)
if errors:
    return {"status": "error", "errors": errors}

# Proceed with processing
```

---

## 6. Performance Optimizations

### 6.1 File Scanning Optimization

**Problem**: Scanning 1000+ files can be slow

**Solution**: Use `Path.glob()` with specific patterns

```python
# Efficient: Only matches ADR_*.md
for adr_path in domain_dir.glob("ADR_*.md"):
    ...

# Inefficient: Matches all, then filters
for file in domain_dir.iterdir():
    if file.name.startswith("ADR_") and file.name.endswith(".md"):
        ...
```

### 6.2 Regex Compilation

**Problem**: Recompiling regex patterns in loops

**Solution**: Compile once as class constants

```python
# Efficient: Compile once
ADR_PATTERN = re.compile(r'^ADR_(\d{4})_(\d{3})_(.+)\.md$')

def validate(filename):
    return ADR_PATTERN.match(filename)

# Inefficient: Recompile every call
def validate(filename):
    pattern = re.compile(r'^ADR_(\d{4})_(\d{3})_(.+)\.md$')
    return pattern.match(filename)
```

### 6.3 Content Reading Optimization

**Problem**: Reading entire file when only need frontmatter

**Solution**: Read first N lines for validation

```python
# Efficient for validation: Read first 500 chars
with open(adr_path, 'r', encoding='utf-8') as f:
    frontmatter = f.read(500)
    if "id:" in frontmatter and "estado:" in frontmatter:
        # Valid, no need to read rest
        pass

# Less efficient: Read entire file
content = adr_path.read_text(encoding='utf-8')
if "id:" in content[:500]:
    pass
```

**Note**: For update operations, we must read entire file anyway.

---

## 7. Testing Strategy Details

### 7.1 Test Data Structures

**Fixture: temp_project**
```python
@pytest.fixture
def temp_project(tmp_path):
    """
    Create temporary project structure:

    tmp_path/
      docs/
        ai/
        backend/
        frontend/
        infraestructura/
        gobernanza/
    """
    docs_dir = tmp_path / "docs"
    for domain in ["ai", "backend", "frontend", "infraestructura", "gobernanza"]:
        (docs_dir / domain).mkdir(parents=True)
    return tmp_path
```

**Fixture: existing_adr**
```python
@pytest.fixture
def existing_adr(temp_project):
    """
    Create ADR_2025_001_test_decision.md in backend.
    """
    adr_path = temp_project / "docs" / "backend" / "ADR_2025_001_test_decision.md"
    content = """---
id: ADR_2025_001
estado: aceptada
date: 2025-11-13
---

# ADR_2025_001: Test Decision

## Contexto y Problema
...

## Decision
...

## Consecuencias

### Positivas
...

### Negativas
...
"""
    adr_path.write_text(content, encoding="utf-8")
    return adr_path
```

### 7.2 Test Coverage Matrix

| Component | Test Class | Coverage Target |
|-----------|------------|-----------------|
| Initialization | TestInitialization | 100% |
| Input Validation | TestInputValidation | 100% |
| Create ADR | TestADRCreation | >= 95% |
| Validate ADRs | TestADRValidation | >= 95% |
| Standardize | TestStandardization | >= 90% |
| Update Index | TestIndexMaintenance | >= 90% |
| Update Refs | TestReferenceUpdate | >= 90% |
| Integration | TestIntegration | >= 85% |
| Edge Cases | TestEdgeCases | >= 80% |
| Helper Methods | TestHelperMethods | >= 95% |

**Overall Target**: >= 90% line coverage, >= 85% branch coverage

### 7.3 Critical Test Cases

**Test: Sequential Number Assignment**
```python
def test_sequential_number_assignment(agent, existing_adr):
    """
    Given: ADR_2025_001 exists
    When: Create new ADR
    Then: Should be numbered ADR_2025_002
    """
    result = agent.execute({
        "operation": "create",
        "adr_data": {...}
    })
    assert "ADR_2025_002" in result.output["adr_id"]
```

**Test: Standardization Idempotency**
```python
def test_standardization_idempotency(agent):
    """
    Given: All ADRs already have correct format
    When: Run standardize operation
    Then: Should rename 0 files
    """
    result = agent.execute({"operation": "standardize"})
    assert result.output["renamed_count"] == 0
```

**Test: Index Completeness**
```python
def test_index_includes_all_adrs(agent, multiple_adrs):
    """
    Given: 5 ADRs across 3 domains
    When: Update index
    Then: Index should list all 5 ADRs
    """
    result = agent.execute({"operation": "update_index"})
    assert result.output["total_adrs"] == 5
```

---

## 8. Security Considerations

### 8.1 Path Traversal Prevention

```python
def _validate_path_within_docs(self, path: Path) -> bool:
    """
    Ensure path is within docs/ directory (prevent path traversal).

    Args:
        path: Path to validate

    Returns:
        True if safe, False if potential traversal attack
    """
    try:
        # Resolve to absolute path
        abs_path = path.resolve()
        abs_docs = self.docs_dir.resolve()

        # Check if path is under docs/
        return abs_path.is_relative_to(abs_docs)
    except Exception:
        return False
```

**Usage**:
```python
adr_path = domain_dir / filename

if not self._validate_path_within_docs(adr_path):
    raise ValueError("Invalid path: potential traversal attack")
```

### 8.2 Input Sanitization

**Domain Validation**:
```python
if dominio not in self.VALID_DOMAINS:
    raise ValueError(f"Invalid domain: {dominio}")
```

**Filename Sanitization**:
```python
# Remove path separators from title
titulo = adr_data["titulo"].replace("/", "").replace("\\", "")
titulo_slug = self._to_snake_case(titulo)
```

---

## 9. Deployment Considerations

### 9.1 File Permissions

**Required Permissions**:
- Read: `docs/**/*.md` (all markdown files)
- Write: `docs/{domain}/ADR_*.md` (create/update ADRs)
- Write: `docs/gobernanza/INDICE_ADRs.md` (update index)

**Permission Check** (optional):
```python
def _check_permissions(self) -> List[str]:
    """Check required file permissions."""
    errors = []

    # Check docs directory readable
    if not os.access(self.docs_dir, os.R_OK):
        errors.append("docs/ not readable")

    # Check domain directories writable
    for domain in self.VALID_DOMAINS:
        domain_dir = self.docs_dir / domain
        if domain_dir.exists() and not os.access(domain_dir, os.W_OK):
            errors.append(f"docs/{domain}/ not writable")

    return errors
```

### 9.2 Concurrent Access

**Issue**: Multiple users running agent simultaneously

**Mitigation**:
1. **File Locking** (optional, for high-concurrency environments):
   ```python
   import fcntl

   with open(lock_file, 'w') as f:
       fcntl.flock(f, fcntl.LOCK_EX)
       # Perform operation
       fcntl.flock(f, fcntl.LOCK_UN)
   ```

2. **Atomic Operations**:
   ```python
   # Write to temp file, then rename (atomic)
   temp_path = adr_path.with_suffix('.tmp')
   temp_path.write_text(content)
   temp_path.rename(adr_path)  # Atomic on POSIX
   ```

3. **Optimistic Locking** (check file hasn't changed):
   ```python
   original_mtime = adr_path.stat().st_mtime
   # ... process file ...
   if adr_path.stat().st_mtime != original_mtime:
       raise ConcurrentModificationError()
   ```

**Recommendation**: For MVP, no locking (documentation updates are rare and typically single-user).

---

## 10. Monitoring and Metrics

### 10.1 Operation Metrics

```python
def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    operation = input_data["operation"]
    start_time = time.time()

    try:
        result = self._execute_operation(operation, input_data)

        duration = time.time() - start_time
        self.logger.info(f"Operation {operation} completed in {duration:.2f}s")

        # Add metrics to result
        result["metrics"] = {
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat()
        }

        return result
    except Exception as e:
        duration = time.time() - start_time
        self.logger.error(f"Operation {operation} failed after {duration:.2f}s: {e}")
        raise
```

### 10.2 Logging Best Practices

**Log Levels**:
- **DEBUG**: Detailed operation steps (for development)
  ```python
  self.logger.debug(f"Scanning domain: {domain}")
  ```

- **INFO**: Major operation milestones
  ```python
  self.logger.info(f"ADR created: {adr_path}")
  self.logger.info(f"Index updated with {total} ADRs")
  ```

- **WARNING**: Non-critical issues
  ```python
  self.logger.warning(f"ADR {adr_path} missing metadata, using defaults")
  ```

- **ERROR**: Operation failures
  ```python
  self.logger.error(f"Failed to create ADR: {e}")
  ```

---

## 11. Maintenance Procedures

### 11.1 Adding New Operation

**Steps**:
1. Add operation name to `valid_operations` list
2. Implement `_operation_name()` method
3. Add case in `run()` method
4. Write tests in `test_adr_management_agent.py`
5. Update HLD and LLD documentation
6. Update CLI help text

**Example**:
```python
# Step 1: Add to validation
valid_operations = [..., "new_operation"]

# Step 2: Implement method
def _new_operation(self, input_data: Dict) -> Dict:
    # Implementation
    pass

# Step 3: Add to run()
if operation == "new_operation":
    return self._new_operation(input_data)
```

### 11.2 Modifying ADR Template

**Steps**:
1. Update `ADR_TEMPLATE` constant
2. Test with `test_create_adr_content_structure`
3. Update existing ADRs if needed (migration script)
4. Update documentation

### 11.3 Supporting New Domain

**Steps**:
1. Add domain to `VALID_DOMAINS` list
2. Create directory `docs/{new_domain}/`
3. Run tests to verify
4. Update index with new domain section

---

## 12. Appendix: Regex Patterns Reference

### 12.1 Filename Patterns

```python
# Current format: ADR_YYYY_XXX_description.md
ADR_PATTERN = re.compile(r'^ADR_(\d{4})_(\d{3})_(.+)\.md$')
# Groups: (year, number, description)

# Old format: ADR-YYYY-XXX-description.md
OLD_PATTERN = re.compile(r'^ADR-(\d{4})-(\d{3})-(.+)\.md$')
# Groups: (year, number, description)
```

**Test Cases**:
```python
# Valid matches
assert ADR_PATTERN.match("ADR_2025_001_test_decision.md")
assert ADR_PATTERN.match("ADR_2025_999_long_description_with_underscores.md")

# Invalid (should not match)
assert not ADR_PATTERN.match("ADR-2025-001-test.md")  # Hyphens
assert not ADR_PATTERN.match("ADR_2025_1_test.md")  # Missing zero-padding
assert not ADR_PATTERN.match("ADR_25_001_test.md")  # 2-digit year
```

### 12.2 Content Patterns

```python
# Frontmatter field extraction
FIELD_PATTERN = r'^{field}:\s*(.+)$'  # Multiline mode

# Title extraction
TITLE_PATTERN = r'^#\s*ADR_\d{4}_\d{3}:\s*(.+)$'  # Multiline mode

# Section detection
SECTION_PATTERN = r'^##\s+(.+)$'  # Multiline mode
```

### 12.3 Reference Patterns

```python
# Old format reference in text
REF_PATTERN = re.compile(r'ADR-(\d{4})-(\d{3})')
# Replacement: r'ADR_\1_\2'

# Link format: [ADR-2025-001](path)
LINK_PATTERN = re.compile(r'\[ADR-(\d{4})-(\d{3})\]')
# Replacement: r'[ADR_\1_\2]'
```

---

**Document Status**: Draft (awaiting review)
**Next Phase**: Testing & Implementation (Phase 4)
**Last Updated**: 2025-11-13
**Version**: 1.0.0
