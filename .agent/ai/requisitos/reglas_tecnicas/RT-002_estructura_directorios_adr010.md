---
id: RT-002
tipo: regla_tecnica
relacionado: [ADR-046, ADR-010, ADR-047]
fecha: 2025-11-16
---

# RT-002: Estructura de Directorios segun ADR-010

## Constraint

El sistema DEBE mapear tipos a ubicaciones siguiendo estructura de ADR-010.

## Mapeo Tipo → Ubicacion

### Transversales (docs/gobernanza/)

```python
UBICACIONES_TRANSVERSALES = {
    "adr": "docs/gobernanza/adr/",
    "guia_transversal": "docs/gobernanza/guias/",
    "procedimiento_transversal": "docs/gobernanza/procedimientos/",
    "analisis": "docs/gobernanza/sesiones/analisis_YYYY_MM/",
    "reporte_limpieza": "docs/gobernanza/sesiones/analisis_YYYY_MM/",
    "sesion": "docs/gobernanza/sesiones/",
    "plantilla_generica": "docs/gobernanza/plantillas/",
}
```

### Por Dominio (docs/{dominio}/)

```python
UBICACIONES_DOMINIO = {
    "task": "docs/{dominio}/tareas/",
    "guia": "docs/{dominio}/guias/",
    "procedimiento": "docs/{dominio}/procedimientos/",
    "diseno_detallado": "docs/{dominio}/diseno_detallado/",
    "plan_testing": "docs/{dominio}/testing/",
    "registro_qa": "docs/{dominio}/qa/registros/",
}
```

### Agentes AI (scripts/coding/ai/)

```python
UBICACIONES_AGENTES = {
    "documentacion_agente": "scripts/coding/ai/agents/",
    "configuracion_agente": "scripts/coding/ai/config/",
    "script_reutilizable": "scripts/coding/ai/automation/",
}
```

### Temporales

```python
UBICACIONES_TEMPORALES = {
    "script_temporal": "/tmp/",
}
```

## Decision Tree

```python
def construir_ubicacion(tipo: str, ownership: str, temporalidad: str) -> str:
    # 1. Scripts temporales
    if temporalidad == "temporal":
        return "/tmp/"

    # 2. Agentes
    if ownership == "agente":
        return UBICACIONES_AGENTES[tipo]

    # 3. Transversales
    if ownership == "transversal":
        return UBICACIONES_TRANSVERSALES[tipo]

    # 4. Dominio especifico
    if ownership.startswith("dominio:"):
        dominio = ownership.split(":")[1]
        return UBICACIONES_DOMINIO[tipo].format(dominio=dominio)

    raise ValueError(f"Ownership desconocido: {ownership}")
```

## 12 Subdirectorios Estandar por Dominio

Segun ADR-010:

```
docs/{dominio}/
├── arquitectura/
├── diseno_detallado/
├── guias/
├── procedimientos/
├── qa/
├── requisitos/
├── sesiones/
├── tareas/
├── testing/
├── planificacion_y_releases/
├── plans/
└── solicitudes/
```

## Ubicaciones Prohibidas

```python
UBICACIONES_PROHIBIDAS = [
    "/home/",
    "/root/",
    "/etc/",
    "/var/",
]
```

## Validacion

Si ubicacion calculada en UBICACIONES_PROHIBIDAS → ERROR

```python
if any(ubicacion.startswith(prohibida) for prohibida in UBICACIONES_PROHIBIDAS):
    raise SecurityError(f"Ubicacion prohibida: {ubicacion}")
```

## Implementacion

Archivo: `scripts/coding/ai/agents/placement/ubicacion.py`

## Referencias

- ADR-010: Organizacion por dominios
- ADR-047: Relacion gobernanza-dominios
- ADR-046: Arquitectura de clasificacion
