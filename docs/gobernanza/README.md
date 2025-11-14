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

### Procesos Operativos
- [Procesos de Gobernanza](procesos/readme.md) ⭐ NUEVO
  - [Procedimiento: Diseño Técnico](procesos/procedimiento_diseno_tecnico.md)
  - [Procedimiento: Análisis de Seguridad](procesos/procedimiento_analisis_seguridad.md)
  - [Procedimiento: Trazabilidad de Requisitos](procesos/procedimiento_trazabilidad_requisitos.md)

### Guías y Estándares
- [Estándares de Código](estandares_codigo.md)
- [Guía de Casos de Uso](casos_de_uso_guide.md)
- [Guía de Shell Scripting](shell_scripting_guide.md)

### Gobernanza por Dominio
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
- **Output profesional**: Prohibido uso de emojis en scripts de producción
- Revisión de seguridad en dependencias
- Documentación obligatoria para APIs públicas
- Pruebas de integración para flujos críticos

Ver detalles completos en: [Estándares de Código](estandares_codigo.md)

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
| Políticas documentadas | OK Sí | Documentado en este archivo |
| Estándares de código establecidos | OK Sí | Ver `estandares_codigo.md` |
| Proceso de revisión definido | OK Sí | Requiere PR review antes de merge |
| Procedimientos operativos | OK Sí | 3 procedimientos core creados (2025-11-04) |
| Trazabilidad ISO 29148 | 🔶 Parcial | Procedimiento creado, pendiente workflows CI/CD |
| Métricas de calidad activas | WARNING Parcial | Falta dashboard de métricas |

## Acciones prioritarias

### Corto Plazo (1-2 semanas)
- [ ] Implementar workflows CI/CD para trazabilidad ISO 29148
- [ ] Capacitar equipos en procedimientos operativos (4h sesión)
- [ ] Aplicar PROC-DISENO-TEC-001 a 3 componentes (piloto)

### Mediano Plazo (1-2 meses)
- [ ] Implementar dashboard de métricas de calidad
- [ ] Establecer SLAs para revisión de PRs
- [ ] Auditar cumplimiento de frontmatter YAML en requisitos
- [ ] Validar generación de índices ISO 29148 end-to-end

### Largo Plazo (3-6 meses)
- [ ] Documentar proceso de releases
- [ ] Definir proceso de escalamiento para decisiones arquitectónicas
- [ ] Crear registro de decisiones de gobernanza (GDR - Governance Decision Records)
- [ ] Certificar conformidad ISO/IEC/IEEE 29148:2018 Full Conformance

## Recursos relacionados
- [Convenciones de Claude Code](../../.github/claude-code-conventions.md)
- [Copilot Instructions](../../.github/copilot-instructions.md)
- [Estrategia de QA](../qa/estrategia_qa.md)
