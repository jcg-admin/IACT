# Project Scripts

This directory contains utility scripts for project automation and maintenance.

## Available Scripts

### `generate-requirements-index.js`

**Purpose**: Generate ISO 29148-compliant requirement indices from domain-specific requirement files.

**Created by**: GitHub Actions workflow (`.github/workflows/requirements-index.yml`)

**Auto-generated**: This script is created dynamically during CI/CD runs.

**Manual Usage**:
```bash
# Install dependencies first
npm install -g glob gray-matter js-yaml

# Run generator
node scripts/generate-requirements-index.js
```

**Input**:
- `implementacion/backend/requisitos/**/*.md`
- `implementacion/frontend/requisitos/**/*.md`
- `implementacion/infrastructure/requisitos/**/*.md`

**Output**:
- `docs/requisitos/brs_business_requirements.md` (ISO 9.3)
- `docs/requisitos/strs_stakeholder_requirements.md` (ISO 9.4)
- `docs/requisitos/syrs_system_requirements.md` (ISO 9.5)
- `docs/requisitos/srs_software_requirements.md` (ISO 9.6)
- `docs/requisitos/matriz_trazabilidad_rtm.md` (Traceability Matrix)
- `docs/requisitos/README.md`

**Features**:
- Parses YAML frontmatter from markdown files
- Validates requirement structure
- Generates bidirectional traceability (upward/downward)
- Creates ISO 29148-compliant documentation
- Detects broken traceability references

**Requirements in frontmatter**:
```yaml
---
id: RF-001
tipo: funcional
titulo: API para cálculo de stock
dominio: backend
owner: equipo-backend
prioridad: alta
estado: aprobado
trazabilidad_upward:
  - RN-001
  - RS-003
trazabilidad_downward:
  - TEST-001
iso29148_clause: "9.6"
---
```

---

## Future Scripts

This directory will contain additional automation scripts as the project grows:

- `validate-docs-links.sh` - Check for broken links in documentation
- `sync-adr-index.sh` - Update ADR (Architecture Decision Records) index
- `generate-glossary.sh` - Build project glossary from terms
- `check-requirements-coverage.sh` - Verify test coverage for requirements

---

## Standards Compliance

All scripts in this directory should follow:

1. **ISO/IEC/IEEE 29148:2018** - Requirements Engineering
2. **BABOK v3** - Business Analysis practices
3. **PMBOK Guide 7th Edition** - Project management standards

For more details, see: `docs/analisis_estructura_docs_v3_final.md`

---

## Contributing

When adding new scripts:

1. Document purpose and usage in this README
2. Include error handling and validation
3. Use exit codes: 0 (success), 1 (error)
4. Add to `.gitignore` if script is auto-generated
5. Test locally before committing

---

**Maintained by**: Development Team
**Last Updated**: 2025-11-02
