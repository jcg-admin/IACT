# Documentation Index

Complete documentation for the AI Agents Framework v1.0.0

## Quick Navigation

### Getting Started
- **[README.md](README.md)** - Start here! Complete user guide with installation, quick start, and module overview
- **[EXAMPLES.md](EXAMPLES.md)** - 17 runnable examples for all modules and complete workflows

### Development
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation for all modules
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture with diagrams and design patterns
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Guidelines for contributing to the project

### Integration & Deployment
- **[INTEGRATION.md](INTEGRATION.md)** - Integration patterns for Django, FastAPI, CLI, LLM, and production deployment

### Project Management
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and release notes
- **[.pre-commit-config.yaml](.pre-commit-config.yaml)** - Pre-commit hooks configuration

## Documentation by Purpose

### For New Users

**Getting Started:**
1. Read [README.md](README.md) - Overview and quick start
2. Try examples from [EXAMPLES.md](EXAMPLES.md) - Hands-on learning
3. Review [INTEGRATION.md](INTEGRATION.md) - See integration patterns

**Recommended Reading Order:**
```
README.md → EXAMPLES.md → API_REFERENCE.md → INTEGRATION.md
```

### For Developers

**Implementation Reference:**
1. [API_REFERENCE.md](API_REFERENCE.md) - All APIs with type signatures
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design and patterns
3. [EXAMPLES.md](EXAMPLES.md) - Code examples

**Contributing:**
1. [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
2. [.pre-commit-config.yaml](.pre-commit-config.yaml) - Set up pre-commit hooks
3. [CHANGELOG.md](CHANGELOG.md) - Version history

### For Integrators

**Integration Guides:**
1. [INTEGRATION.md](INTEGRATION.md) - All integration patterns
2. [EXAMPLES.md](EXAMPLES.md#complete-workflows) - End-to-end workflows
3. [API_REFERENCE.md](API_REFERENCE.md) - API details

### For Architects

**Architecture Documentation:**
1. [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture
2. [README.md](README.md#architecture) - Module overview
3. [API_REFERENCE.md](API_REFERENCE.md) - Component details

## Documentation by Module

### Planning Module (RF-011, RF-012)
- **Overview**: [README.md#planning-module](README.md#planning-module)
- **API**: [API_REFERENCE.md#planning-module](API_REFERENCE.md#planning-module)
- **Examples**: [EXAMPLES.md#planning-examples](EXAMPLES.md#planning-examples)
- **Architecture**: [ARCHITECTURE.md#planning-module-architecture](ARCHITECTURE.md#planning-module-architecture)

### Protocols Module (RF-013)
- **Overview**: [README.md#protocols-module](README.md#protocols-module)
- **API**: [API_REFERENCE.md#protocols-module](API_REFERENCE.md#protocols-module)
- **Examples**: [EXAMPLES.md#protocol-examples](EXAMPLES.md#protocol-examples)
- **Architecture**: [ARCHITECTURE.md#protocols-module-architecture](ARCHITECTURE.md#protocols-module-architecture)

### UX Module (RF-016)
- **Overview**: [README.md#ux-module](README.md#ux-module)
- **API**: [API_REFERENCE.md#ux-module](API_REFERENCE.md#ux-module)
- **Examples**: [EXAMPLES.md#ux-examples](EXAMPLES.md#ux-examples)
- **Architecture**: [ARCHITECTURE.md#ux-module-architecture](ARCHITECTURE.md#ux-module-architecture)

### Security Module (RF-017)
- **Overview**: [README.md#security-module](README.md#security-module)
- **API**: [API_REFERENCE.md#security-module](API_REFERENCE.md#security-module)
- **Examples**: [EXAMPLES.md#security-examples](EXAMPLES.md#security-examples)
- **Architecture**: [ARCHITECTURE.md#security-module-architecture](ARCHITECTURE.md#security-module-architecture)

## Documentation Statistics

| Document | Size | Purpose |
|----------|------|---------|
| README.md | ~850 lines | User guide & quick start |
| INTEGRATION.md | ~1,100 lines | Integration patterns |
| API_REFERENCE.md | ~1,100 lines | Complete API reference |
| EXAMPLES.md | ~1,100 lines | 17 runnable examples |
| ARCHITECTURE.md | ~850 lines | Architecture & diagrams |
| CHANGELOG.md | ~280 lines | Version history |
| CONTRIBUTING.md | ~550 lines | Contribution guidelines |
| DOCUMENTATION_INDEX.md | This file | Navigation guide |

**Total Documentation**: ~5,830 lines across 8 files

## Quick Reference

### Common Tasks

**Run Tests:**
```bash
PYTHONPATH=/path/to/IACT---project python3 -m pytest scripts/coding/tests/test_agents/ -v
```

**Check Coverage:**
```bash
python3 -m pytest scripts/coding/tests/test_agents/ --cov=scripts/coding/ai/agents --cov-report=term
```

**Format Code:**
```bash
ruff format scripts/coding/ai/agents/
```

**Type Check:**
```bash
mypy scripts/coding/ai/agents/ --ignore-missing-imports
```

### Key Concepts

1. **Planning**: Goal → Plan → Execution → Feedback → Revision
2. **Protocols**: MCP (tools), A2A (agents), NLWeb (web)
3. **UX**: Transparency, Control, Consistency
4. **Security**: Threat detection, HITL, Audit logging

### Performance Targets

- Goal parsing: <10ms ✓
- Plan decomposition: <50ms ✓
- Tool discovery: <100ms ✓
- Failure transparency: <500ms ✓

## External Resources

### Test Files
- `scripts/coding/tests/test_agents/` - 140 tests demonstrating all features

### CI/CD
- `.github/workflows/agents-ci.yml` - GitHub Actions workflow

### Requirements
- Python 3.11+
- Pydantic 2.5+
- pytest (for testing)

## Version Information

- **Current Version**: 1.0.0
- **Release Date**: 2025-11-16
- **Status**: Production Ready
- **Coverage**: 92% (140/140 tests passing)

## Getting Help

### Troubleshooting
- See [README.md#troubleshooting](README.md#troubleshooting)

### Common Issues
- Import errors: Check PYTHONPATH
- Pydantic errors: Verify all required fields
- Test failures: Run with `-v` flag for details

### Contributing
- Read [CONTRIBUTING.md](CONTRIBUTING.md)
- Check open issues
- Follow coding standards

### Support Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and ideas
- Documentation: This index and linked files

## Roadmap

See [CHANGELOG.md#unreleased](CHANGELOG.md#unreleased) for planned features.

**Upcoming:**
- v1.1.0: Bug fixes, Pydantic v2 migration, real browser automation
- v2.0.0: Breaking changes, optimization, new features

## License

See project LICENSE file.

---

**Last Updated**: 2025-11-16
**Documentation Version**: 1.0.0
**Framework Version**: 1.0.0

---

## Quick Links

- [README](README.md) | [Examples](EXAMPLES.md) | [API](API_REFERENCE.md) | [Integration](INTEGRATION.md) | [Architecture](ARCHITECTURE.md) | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)
