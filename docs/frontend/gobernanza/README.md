---
id: DOC-GOB-FRONTEND
estado: activo
propietario: equipo-frontend
ultima_actualizacion: 2025-01-17
relacionados: ["DOC-FRONTEND-INDEX", "DOC-GOB-INDEX", "ADR-GOB-010"]
date: 2025-11-13
---
# Gobernanza del Frontend

Políticas, estándares y lineamientos que rigen el desarrollo, mantenimiento y evolución del frontend.

## ⚠️ Gobernanza Multi-nivel

El proyecto IACT utiliza una arquitectura de gobernanza en dos niveles:

1. **Gobernanza Global** ([`/docs/gobernanza/`](../gobernanza/)): Decisiones que afectan a TODO el proyecto
2. **Gobernanza Frontend** (este directorio): Decisiones específicas del frontend

### Enlaces Rápidos a Gobernanza Global

**ANTES de crear un ADR aquí, consulta la gobernanza global:**

| Recurso | Ubicación |
|---------|-----------|
| **ADRs Globales** | [`/docs/gobernanza/adr/`](../gobernanza/adr/) |
| **Guías Compartidas** | [`/docs/gobernanza/guias/`](../gobernanza/guias/) |
| **Procedimientos** | [`/docs/gobernanza/procedimientos/`](../gobernanza/procedimientos/) |
| **Templates** | [`/docs/gobernanza/templates/`](../gobernanza/templates/) |
| **Diseño Global** | [`/docs/gobernanza/diseno/`](../gobernanza/diseno/) |

**Documento clave**: [`ADR-GOB-010: Gobernanza Multi-nivel`](../gobernanza/adr/ADR-GOB-010-gobernanza-multinivel.md)

### ¿Cuándo crear ADR aquí vs. Global?

**✅ ADR de Frontend (aquí)**: Solo afecta frontend, stack-specific (React/TypeScript), no rompe interoperabilidad

**❌ ADR Global**: Afecta múltiples dominios, define estándares del proyecto, cross-cutting concerns

## Página padre
- [`../README.md`](../README.md)

## Páginas hijas
- [`adr/`](adr/) - ADRs específicos del frontend
- [`lineamientos_gobernanza.md`](lineamientos_gobernanza.md) - Lineamientos específicos
- [`registro_decisiones.md`](registro_decisiones.md) - Bitácora de decisiones de gobernanza

## Información clave

### Estándares de código
- Guía de estilo (ESLint, Prettier)
- Convenciones de naming
- Estructura de archivos y directorios
- Documentación de código (JSDoc, TSDoc)
- Accesibilidad (WCAG 2.1)

### Proceso de desarrollo
- Workflow de Git (branching strategy)
- Code review requirements
- Testing requirements
- Definition of Done
- CI/CD pipeline

### Gestión de dependencias
- Política de actualización de dependencias
- Evaluación de nuevas librerías
- Gestión de security vulnerabilities
- Documentación de dependencias críticas

### Performance y optimización
- Métricas objetivo (LCP, FID, CLS)
- Bundle size limits
- Code splitting strategy
- Lazy loading guidelines
- Caching strategy

### Seguridad frontend
- Input validation
- XSS prevention
- CSRF protection
- Content Security Policy
- Secrets management

## Lineamientos corporativos aplicables
Se heredan los siguientes lineamientos del nivel corporativo:
- [`../../gobernanza/estandares_codigo.md`](../../gobernanza/estandares_codigo.md)
- [`../../gobernanza/lineamientos_gobernanza.md`](../../gobernanza/lineamientos_gobernanza.md)

## Estado de cumplimiento
| Elemento en la base maestra | ¿Existe en repositorio? | Observaciones |
| --- | --- | --- |
| Portada de Gobernanza frontend | Sí | Este archivo documenta políticas y estándares del frontend |
| Lineamientos de gobernanza | Pendiente | Crear documento con políticas específicas de frontend |
| Estándares de código | Parcial | Definidos en configuración ESLint/Prettier, falta documentación |
| Registro de decisiones | Pendiente | Crear bitácora de decisiones de gobernanza |

## Acciones prioritarias
- [ ] Documentar lineamientos de gobernanza frontend
- [ ] Formalizar estándares de código en documento
- [ ] Establecer métricas y objetivos de performance
- [ ] Crear registro de decisiones de gobernanza
