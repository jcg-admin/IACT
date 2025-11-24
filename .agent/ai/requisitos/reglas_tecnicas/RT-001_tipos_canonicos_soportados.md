---
id: RT-001
tipo: regla_tecnica
relacionado: [ADR-046]
fecha: 2025-11-16
---

# RT-001: Tipos Canonicos Soportados

## Constraint

El sistema DEBE soportar exactamente estos 19 tipos canonicos de artefactos.

## Tipos Definidos

```python
TIPOS_VALIDOS = [
    "task",                  # Tareas de desarrollo
    "adr",                   # Architecture Decision Records
    "solicitud",             # Solicitudes de cambio
    "analisis",              # Documentos de analisis
    "sesion",                # Sesiones de trabajo
    "reporte_limpieza",      # Reportes de cleanup
    "documentacion_agente",  # Documentacion de agentes
    "configuracion_agente",  # Configs de agentes
    "script",                # Scripts de automatizacion
    "guia",                  # Guias de procedimientos
    "indice",                # Indices de directorios
    "procedimiento",         # Procedimientos operativos
    "diseno_detallado",      # HLD/LLD
    "diagrama",              # Diagramas arquitectonicos
    "plan_testing",          # Planes de pruebas
    "registro_qa",           # Registros de calidad
    "pipeline_ci_cd",        # Pipelines CI/CD
    "script_devops",         # Scripts DevOps
    "plantilla",             # Plantillas de documentos
]
```

## Deteccion por Patron de Nombre

```python
PATRONES_NOMBRE = {
    r"^TASK-\d+": "task",
    r"^ADR-\d+": "adr",
    r"^REQ-\d+": "solicitud",
    r"^ANALISIS_": "analisis",
    r"^SESSION_": "sesion",
    r"^CLEANUP_REPORT_": "reporte_limpieza",
    r"^README_.*Agent": "documentacion_agente",
    r"_config\.json$": "configuracion_agente",
    r"^GUIA_": "guia",
    r"^INDEX\.md$": "indice",
    r"^PROC-\d+": "procedimiento",
    r"^TEST_PLAN_": "plan_testing",
}
```

## Deteccion por Patron de Contenido

```python
PATRONES_CONTENIDO = {
    ("## Sub-Agentes", "## Arquitectura"): "documentacion_agente",
    ("## Decision", "## Status"): "adr",
    ("## Casos de Prueba", "## Cobertura"): "plan_testing",
}
```

## Fallback

Si ningun patron coincide:
```python
tipo_detectado = "documento_general"
requiere_clarificacion = True
```

## Implementacion

Archivo: `scripts/coding/ai/agents/placement/detector.py`

```python
def detectar_tipo(nombre: str, contenido: str) -> str:
    # 1. Verificar patrones de nombre
    for patron, tipo in PATRONES_NOMBRE.items():
        if re.match(patron, nombre):
            return tipo

    # 2. Verificar patrones de contenido
    for (header1, header2), tipo in PATRONES_CONTENIDO.items():
        if header1 in contenido and header2 in contenido:
            return tipo

    # 3. Fallback
    return "documento_general"
```

## Validacion

Test: `scripts/coding/tests/ai/test_placement_detector.py::TestDetectarTipoPorNombre`

```gherkin
Given nombre "TASK-001-feature.md"
When detectar_tipo(nombre, contenido)
Then tipo == "task"
```

## Referencias

- ADR-046: Define arquitectura de clasificacion
- `placement/detector.py`: Implementacion
