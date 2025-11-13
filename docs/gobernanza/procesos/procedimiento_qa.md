---
id: DOC-PROC-QA
tipo: procedimiento
estado: activo
propietario: equipo-qa
ultima_actualizacion: 2025-11-06
date: 2025-11-13
---
# Procedimiento de Control de Calidad (QA)

## Objetivo

Asegurar calidad del codigo y documentacion antes de integracion.

## Checklists de Calidad

### Codigo Python

- [ ] Cumple PEP 8
- [ ] Type hints presentes
- [ ] Docstrings completos
- [ ] Tests unitarios >70% coverage
- [ ] Sin emojis en codigo o comentarios
- [ ] Sin dependencia de Redis

### Codigo React/JavaScript

- [ ] ESLint sin errores
- [ ] Componentes con PropTypes o TypeScript
- [ ] Tests con Testing Library
- [ ] Sin console.log en produccion
- [ ] Sin emojis en codigo

### Documentacion

- [ ] Front matter YAML completo
- [ ] Sin emojis
- [ ] Enlaces internos funcionan
- [ ] README actualizado
- [ ] Trazabilidad de requisitos

### Scripts

- [ ] Python, NO JavaScript/Bash para logica compleja
- [ ] Shebang correcto
- [ ] Manejo de errores
- [ ] Logging apropiado

## Proceso de Revision

1. Auto-revision usando checklist
2. Ejecutar tests localmente
3. Commit y push
4. CI/CD ejecuta validaciones
5. Revision de pares si es PR

## Herramientas

- pylint / flake8 / black (Python)
- ESLint / Prettier (JavaScript)
- markdownlint (Documentacion)
- pytest (Tests Python)
- Jest (Tests JavaScript)

## Referencias

- GUIA_ESTILO.md
- ADR_014: Testing Strategy
