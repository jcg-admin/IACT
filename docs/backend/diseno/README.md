# Diseño del Backend - IACT

Diseño arquitectónico y diagramas específicos del dominio Backend.

## Estructura

```
diseno/
├── arquitectura/                ← Decisiones arquitectónicas backend
│   ├── patrones/               ← Patrones de diseño aplicados
│   ├── capas/                  ← Arquitectura en capas
│   └── integraciones/          ← Integraciones con sistemas externos
└── diagramas/                   ← Diagramas UML backend
    ├── clases/                 ← Modelos Django (ER, Clases)
    ├── secuencia/              ← Flujos backend (Secuencia)
    ├── actividad/              ← Procesos backend (Actividad)
    └── componentes/            ← Arquitectura componentes
```

## Gobernanza Multi-nivel

Consulta **primero** la gobernanza global:
- [Diseño Global](../../gobernanza/diseno/)
- [ADR-GOB-004: PlantUML para Diagramas](../../gobernanza/adr/ADR-GOB-004-plantuml-para-diagramas.md)
- [GUIA-GOB-008: Crear Diagramas PlantUML](../../gobernanza/guias/GUIA-GOB-008-crear-diagramas-plantuml.md)
- [GUIA-GOB-009: Documentación UML Completa](../../gobernanza/guias/GUIA-GOB-009-documentacion-uml-completa.md)

## Estado Actual

Según análisis 2025-01-17:

| Tipo Diagrama | Cantidad Actual | Objetivo | Gap |
|---------------|-----------------|----------|-----|
| **Diagramas ER** | 1 (permisos) | ~5 (módulos core) | -4 |
| **Diagramas Secuencia** | 8 | ~20 | -12 |
| **Diagramas Actividad** | 3 | ~10 | -7 |
| **Diagramas Componentes** | 0 | ~3 | -3 |
| **Diagramas Clases** | 1 (permisos) | ~5 | -4 |

## Prioridades de Diagramación

### Prioridad CRÍTICA

1. **Diagramas ER Módulos Core**
   - `CLASS-BACK-020-modelo-llamadas.puml`: Módulo llamadas (core negocio)
   - `CLASS-BACK-030-modelo-analytics.puml`: Módulo analytics/métricas
   - `CLASS-BACK-040-modelo-etl.puml`: Módulo ETL (integración IVR)

2. **Diagramas Secuencia UC-CALL**
   - `SEQ-CALL-001-registrar-llamada.puml`: UC-CALL-001 flujo completo
   - `SEQ-CALL-002-atender-llamada.puml`: UC-CALL-002 flujo completo
   - `SEQ-CALL-003-transferir-llamada.puml`: UC-CALL-003 flujo completo

### Prioridad ALTA

3. **Diagramas Componentes Arquitectura**
   - `COMP-BACK-001-arquitectura-general.puml`: Vista 10,000 ft backend
   - `COMP-BACK-002-integracion-ivr.puml`: Integración IVR legacy
   - `COMP-BACK-003-analytics-pipeline.puml`: Pipeline analytics

4. **Diagramas Actividad Workflows**
   - `ACT-ETL-001-pipeline-ivr-analytics.puml`: ETL IVR → Analytics
   - `ACT-BACK-010-generacion-reportes.puml`: Workflow reportes

## Nomenclatura Diagramas

Según ADR-GOB-004:

```
TIPO-DOMINIO-###-descripcion.puml

Tipos Backend:
- CLASS: Modelos Django (ER, Clases)
- SEQ: Flujos backend (Secuencia)
- ACT: Procesos (Actividad)
- COMP: Arquitectura componentes
- STATE: Estados (Máquinas estado)
- PKG: Paquetes (Apps Django)

Ejemplos:
- CLASS-BACK-020-modelo-llamadas.puml
- SEQ-CALL-001-registrar-llamada.puml
- COMP-BACK-001-arquitectura-general.puml
```

## Generación Diagramas

```bash
# Generar todos los diagramas backend
plantuml -tsvg docs/backend/diseno/diagramas/**/*.puml

# Generar un diagrama específico
plantuml -tsvg docs/backend/diseno/diagramas/clases/CLASS-BACK-020-modelo-llamadas.puml
```

## Referencias

- [Procedimiento: Generar Diagrama PlantUML](../../gobernanza/procedimientos/PROCED-GOB-006-generar-diagrama-uml-plantuml.md)
- [Templates PlantUML](../../gobernanza/templates/)
- [Diseño Global](../../gobernanza/diseno/)
