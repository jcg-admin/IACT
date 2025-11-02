---
id: DOC-GOB-INDEX
estado: activo
propietario: equipo-gobernanza
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-INDEX-GENERAL", "DOC-REQ-INDEX", "DOC-ARQ-INDEX"]
---
# Gobernanza del Proyecto IACT

Este espacio documenta las políticas, estándares, procesos de revisión y control de cambios que rigen el desarrollo del proyecto IACT.

## Página padre
- [Índice de espacios documentales](../index.md)

## Páginas hijas
- [Backend - Gobernanza](../backend/gobernanza/readme.md)
- [Frontend - Gobernanza](../frontend/gobernanza/readme.md)
- [Infrastructure - Gobernanza](../infrastructure/gobernanza/readme.md)

## Información clave

### Políticas de Desarrollo
- **Test-Driven Development (TDD)**: Implementación obligatoria para nuevas funcionalidades
- **Cobertura mínima**: 80% en todas las capas
- **Revisión de código**: Obligatoria antes de merge a develop/main
- **Conventional Commits**: Estándar para mensajes de commit

### Estándares de Calidad
- Análisis estático de código mediante linters
- Revisión de seguridad en dependencias
- Documentación obligatoria para APIs públicas
- Pruebas de integración para flujos críticos

### Proceso de Control de Cambios
1. Crear issue describiendo el cambio propuesto
2. Crear rama `feature/` desde develop
3. Implementar cambios siguiendo TDD
4. Crear Pull Request con descripción detallada
5. Pasar revisión de código y tests automatizados
6. Merge solo después de aprobación

### Arquitectura de Ramas
- `main/master`: Código en producción
- `develop`: Integración continua
- `feature/*`: Nuevas funcionalidades
- `hotfix/*`: Correcciones urgentes
- `bugfix/*`: Corrección de bugs
- `docs/*`: Cambios exclusivos de documentación

## Estado de cumplimiento

| Elemento | Estado | Observaciones |
|----------|--------|---------------|
| Políticas documentadas | ✅ Sí | Documentado en este archivo |
| Estándares de código establecidos | ✅ Sí | Ver `.github/copilot-instructions.md` |
| Proceso de revisión definido | ✅ Sí | Requiere PR review antes de merge |
| Métricas de calidad activas | ⚠️ Parcial | Falta dashboard de métricas |

## Acciones prioritarias
- [ ] Implementar dashboard de métricas de calidad
- [ ] Establecer SLAs para revisión de PRs
- [ ] Documentar proceso de releases
- [ ] Definir proceso de escalamiento para decisiones arquitectónicas
- [ ] Crear registro de decisiones de gobernanza (GDR - Governance Decision Records)

## Recursos relacionados
- [Convenciones de Claude Code](../../.github/claude-code-conventions.md)
- [Copilot Instructions](../../.github/copilot-instructions.md)
- [Estrategia de QA](../qa/estrategia_qa.md)
