# Regla de Negocio: Ubicacion Canonica segun ADR-010

## Metadatos
- Codigo: RN-002
- Tipo: Restriccion
- Fuente: ADR-010 (Arquitectura por Dominios)
- Estado: Aprobado
- Fecha: 2025-11-16
- Owner: arquitecto-senior

## Descripcion

El sistema DEBE determinar la ubicacion canonica de cada artefacto siguiendo la estructura de directorios definida en ADR-010 (Arquitectura por Dominios). La ubicacion depende del tipo de artefacto, ownership y temporalidad.

### Estructura de Directorios ADR-010

```
docs/
├── gobernanza/           # Contenido transversal (cross-domain)
│   ├── adr/              # Architecture Decision Records
│   ├── guias/            # Guias transversales
│   ├── procedimientos/   # Procedimientos transversales
│   ├── sesiones/         # Sesiones de trabajo
│   │   └── analisis_YYYY_MM/  # Analisis historicos
│   ├── plantillas/       # Plantillas de documentos
│   └── qa/               # Registros de calidad
│
├── backend/              # Dominio Backend
│   ├── arquitectura/     # Decisiones arquitectonicas
│   ├── diseno_detallado/ # HLD/LLD
│   ├── guias/            # Guias especificas backend
│   ├── procedimientos/   # Procedimientos backend
│   ├── qa/               # QA backend
│   ├── requisitos/       # Requisitos backend
│   ├── sesiones/         # Sesiones backend
│   ├── tareas/           # Tareas backend
│   └── testing/          # Planes de testing
│
├── frontend/             # Dominio Frontend (misma estructura)
├── infraestructura/      # Dominio Infraestructura (misma estructura)
└── ai/                   # Dominio AI/ML (misma estructura)
```

### Mapeo Tipo → Ubicacion

#### Artefactos Transversales (docs/gobernanza/)

- **adr**: `docs/gobernanza/adr/`
- **guia** (si transversal): `docs/gobernanza/guias/`
- **procedimiento** (si transversal): `docs/gobernanza/procedimientos/`
- **analisis**: `docs/gobernanza/sesiones/analisis_YYYY_MM/`
- **reporte_limpieza**: `docs/gobernanza/sesiones/analisis_YYYY_MM/`
- **sesion**: `docs/gobernanza/sesiones/`
- **plantilla**: `docs/gobernanza/plantillas/`
- **registro_qa** (si transversal): `docs/gobernanza/qa/registros/`

#### Artefactos de Dominio (docs/{dominio}/)

- **task**: `docs/{dominio}/tareas/` si dominio-especifico, `docs/gobernanza/` si transversal
- **guia** (si dominio): `docs/{dominio}/guias/`
- **procedimiento** (si dominio): `docs/{dominio}/procedimientos/`
- **diseno_detallado**: `docs/{dominio}/diseno_detallado/`
- **diagrama** (si transversal): `docs/gobernanza/anexos/diagramas/`, sino `docs/{dominio}/diseno_detallado/diagramas/`
- **plan_testing**: `docs/{dominio}/testing/`
- **registro_qa** (si dominio): `docs/{dominio}/qa/registros/`

#### Artefactos de Agentes (scripts/coding/ai/)

- **documentacion_agente**: `scripts/coding/ai/agents/`
- **configuracion_agente**: `scripts/coding/ai/config/`
- **script** (si reutilizable): `scripts/coding/ai/automation/`
- **script** (si temporal): `/tmp/`

#### Artefactos DevOps (docs/infraestructura/)

- **pipeline_ci_cd**: `docs/infraestructura/devops/ci_cd/`
- **script_devops** (git): `docs/infraestructura/devops/git/`
- **script_devops** (otros): `docs/infraestructura/devops/automatizacion/`

### Determinacion de Ownership

Para decidir si un artefacto es transversal o dominio-especifico:

1. **Verificar contexto explícito**: Si contexto incluye `dominio: backend`, es dominio-especifico
2. **Analizar contenido**: Detectar dominios mencionados en contenido
   - Si menciona 1 dominio → dominio-especifico
   - Si menciona 2+ dominios → transversal
3. **Tipos siempre transversales**: adr, plantilla, guia_transversal
4. **Tipos siempre agente**: documentacion_agente, configuracion_agente, script
5. **Tipos siempre devops**: pipeline_ci_cd, script_devops

## Impacto en Requisitos

- **RF-002**: Determinar ownership (transversal vs dominio especifico)
- **RF-003**: Construir ubicacion canonica basada en tipo, ownership, temporalidad
- **RNF-002**: Precision ≥ 95% en clasificacion de ubicacion

## Evidencia

- ADR-010 - Arquitectura por Dominios (definicion oficial de estructura)
- Auditoria nov 2025 - confirma estructura de 12 subdirectorios estandar por dominio

## Observaciones

- La temporalidad afecta ubicacion: scripts temporales van a `/tmp/`, analisis historicos van a `sesiones/analisis_YYYY_MM/`
- Si ownership es ambiguo (REQUIERE_CLARIFICACION), solicitar contexto adicional al usuario
- Estructura de 12 subdirectorios estandar se aplica a cada dominio (backend, frontend, infraestructura, ai)
