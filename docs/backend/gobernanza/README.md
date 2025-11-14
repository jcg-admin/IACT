---
title: Gobernanza del Backend IACT
date: 2025-11-13
domain: backend
status: active
---

# Gobernanza del Backend IACT

**Proposito**: Politicas y procesos de gobernanza de desarrollo

## Contenido

- Procesos SDLC
- Politicas de codigo
- Code review guidelines
- Definition of Done
- Politicas de seguridad

## Documentos

- `sdlc-process.md`: Proceso SDLC completo
- `code-standards.md`: Standards de codigo
- `code-review-checklist.md`: Checklist de review
- `definition-of-done.md`: Criterios de completitud
- `security-policies.md`: Politicas de seguridad

## Restricciones Criticas IACT

### RNF-002: NO Redis
- Sesiones en MySQL
- Validacion automatica en CI

### NO Emojis/Iconos
- ASCII puro solamente
- Validacion con check_no_emojis.py

### NO Email/SMTP
- Usar InternalMessage
- Validacion en CI

## Ownership

Maintainer: Tech Lead
Review: Arquitecto + Product Owner
