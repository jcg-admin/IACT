---
id: DOC-SOL-SC02
estado: en_progreso
propietario: equipo-backend
ultima_actualizacion: 2025-11-04
relacionados: ["DOC-SOL-INDEX", "DOC-BACKEND-INDEX", "DOC-ARQ-BACKEND", "DOC-DIS-BACKEND"]
---
# Solicitud SC02 - Documentación de la carpeta API

Esta solicitud documenta el proceso de creación de documentación técnica completa para la carpeta `api/` del proyecto IACT, específicamente para el proyecto Django `callcentersite` y sus aplicaciones modulares.

## Página padre
- [`../readme.md`](../readme.md)

## Páginas hijas
- [`alcance.md`](alcance.md) - Definición del alcance y objetivos
- [`checklist.md`](checklist.md) - Lista de verificación y seguimiento
- [`analisis_plantillas.md`](analisis_plantillas.md) - Análisis de plantillas disponibles
- [`analisis_estructura_api.md`](analisis_estructura_api.md) - Análisis estructural de la carpeta API
- [`analisis_funcion_real_apps.md`](analisis_funcion_real_apps.md) - ⭐ Análisis funcional crítico de cada app
- [`entregables/`](entregables/) - Documentos técnicos generados

## Contexto

Durante la revisión del proyecto se identificó que la carpeta `api/` carece de documentación técnica formal. Esta carpeta contiene el backend del proyecto IACT, un monolito modular Django con las siguientes aplicaciones:

- **analytics**: Análisis y métricas
- **audit**: Auditoría del sistema
- **authentication**: Autenticación de usuarios
- **common**: Utilidades comunes
- **dashboard**: Tableros de control
- **etl**: Extract, Transform, Load
- **ivr_legacy**: Integración con sistema IVR heredado
- **notifications**: Sistema de notificaciones
- **reports**: Generación de reportes
- **users**: Gestión de usuarios

## Objetivo

Crear documentación técnica completa que incluya:

1. Descripción de cada aplicación Django
2. Modelos de datos y relaciones
3. API endpoints (actuales y futuros)
4. Servicios y lógica de negocio
5. Patrones de diseño implementados
6. Guías de desarrollo y convenciones

## Beneficios esperados

- Facilitar onboarding de nuevos desarrolladores
- Mejorar mantenibilidad del código
- Documentar decisiones técnicas y arquitectónicas
- Crear referencia única para el equipo de desarrollo
- Cumplir con estándares de calidad documental del proyecto

## Ubicación de entregables

Los documentos técnicos se crearán en:
- `docs/backend/diseno_detallado/` - Documentación de diseño detallado
- `docs/backend/arquitectura/` - Documentación arquitectónica
- `docs/solicitudes/sc02/entregables/` - Versiones de trabajo y borradores

## Referencias cruzadas

- [Backend - Arquitectura](../../backend/arquitectura/readme.md)
- [Backend - Diseño Detallado](../../backend/diseno_detallado/readme.md)
- [Arquitectura General](../../arquitectura/readme.md)
- [Patrones Arquitectónicos](../../backend/arquitectura/patrones_arquitectonicos.md) ⭐ NUEVO
- [Guía de Decisión de Patrones](../../backend/arquitectura/guia_decision_patrones.md) ⭐ NUEVO
- [Plantilla API Reference](../../plantillas/plantilla_api_reference.md)
- [Plantilla Database Design](../../plantillas/plantilla_database_design.md)
- [Plantilla Django App](../../plantillas/plantilla_django_app.md)
- [Plantilla ETL Job](../../plantillas/plantilla_etl_job.md)

## Estado actual

| Elemento | Estado | Responsable | Fecha estimada |
| --- | --- | --- | --- |
| Definición de alcance | ✅ Completado | Equipo Backend | 2025-11-04 |
| Análisis de plantillas | ✅ Completado | Equipo Backend | 2025-11-04 |
| Análisis estructural API | ✅ Completado | Equipo Backend | 2025-11-04 |
| Análisis funcional de apps | ✅ Completado | Equipo Backend | 2025-11-04 |
| Documentación patrones arquitectónicos | ✅ Completado | Equipo Backend | 2025-11-04 |
| Documentación app analytics | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app etl | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app reports | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app dashboard | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app authentication | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app users | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app audit | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app ivr_legacy | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app notifications | ⏸️ Pendiente | Equipo Backend | Por definir |
| Documentación app common | ⏸️ Pendiente | Equipo Backend | Por definir |
| Consolidación en backend/diseno_detallado/ | ⏸️ Pendiente | Equipo Backend | Por definir |

## Checklist operativo

- [x] Crear estructura de solicitud SC02
- [x] Definir alcance y objetivos
- [x] Analizar estructura de cada app Django
- [x] Analizar función real de cada app
- [x] Documentar patrones arquitectónicos existentes
- [x] Crear guías de decisión de patrones
- [ ] Documentar apps individuales (modelos, servicios, vistas)
- [ ] Crear guía de API endpoints
- [ ] Revisar con equipo de arquitectura
- [ ] Publicar documentación de apps en docs/backend/
- [ ] Actualizar índice de backend
- [ ] Cerrar solicitud

## Próximos pasos

1. Crear documento de alcance detallado
2. Analizar cada aplicación Django en detalle
3. Priorizar apps críticas (ETL, Analytics, Reports)
4. Comenzar documentación por apps prioritarias
5. Iterar con revisiones del equipo
