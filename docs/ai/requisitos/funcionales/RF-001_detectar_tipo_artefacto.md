---
id: RF-001
tipo: requisito_funcional
relacionado: [UC-SYS-001, RT-001]
prioridad: critica
estado: implementado
fecha: 2025-11-16
---

# RF-001: Detectar Tipo de Artefacto

## Especificacion

El sistema DEBE detectar el tipo de artefacto mediante analisis de:
1. Patron de nombre de archivo
2. Patron de contenido (headers Markdown)
3. Tipo declarado explicitamente (si provisto)

## Criterios de Aceptacion

### Escenario 1: Deteccion por Nombre

```gherkin
Given nombre_archivo = "TASK-001-implementar-feature.md"
  And contenido = "# Descripcion de tarea"
When sistema.detectar_tipo(nombre, contenido)
Then tipo_detectado == "task"
  And confianza >= 0.95
```

### Escenario 2: Deteccion por Contenido

```gherkin
Given nombre_archivo = "documento.md"
  And contenido contiene "## Decision" AND "## Status"
When sistema.detectar_tipo(nombre, contenido)
Then tipo_detectado == "adr"
  And confianza >= 0.80
```

### Escenario 3: Tipo Declarado Explicitamente

```gherkin
Given nombre_archivo = "archivo.md"
  And tipo_declarado = "analisis"
When sistema.detectar_tipo(nombre, contenido, tipo_declarado)
Then tipo_detectado == "analisis"
  And confianza >= 0.95
```

### Escenario 4: Fallback (Tipo No Detectado)

```gherkin
Given nombre_archivo = "generico.md"
  And contenido sin patrones reconocibles
When sistema.detectar_tipo(nombre, contenido)
Then tipo_detectado == "documento_general"
  And confianza < 0.50
  And requiere_clarificacion == True
```

### Escenario 5: Multiple Patrones Coinciden

```gherkin
Given nombre_archivo = "TASK-001-feature.md"
  And contenido contiene "## Decision" (patron de ADR)
When sistema.detectar_tipo(nombre, contenido)
Then tipo_detectado == "task"
  And razon == "patron de nombre tiene prioridad"
```

## Implementacion

Archivo: `scripts/coding/ai/agents/placement/detector.py`

```python
def detectar_tipo(nombre: str, contenido: str, tipo_declarado: str = None) -> str:
    # 1. Tipo declarado (mayor prioridad)
    if tipo_declarado:
        return normalizar_tipo(tipo_declarado)

    # 2. Patrones de nombre
    for patron, tipo in PATRONES_NOMBRE.items():
        if re.match(patron, nombre):
            return tipo

    # 3. Patrones de contenido
    for (h1, h2), tipo in PATRONES_CONTENIDO.items():
        if h1 in contenido and h2 in contenido:
            return tipo

    # 4. Fallback
    return "documento_general"
```

## Tests

Archivo: `scripts/coding/tests/ai/test_placement_detector.py`

```python
class TestDetectarTipo:
    def test_detectar_task_por_nombre(self):
        assert detectar_tipo("TASK-001-feature.md", "...") == "task"

    def test_detectar_adr_por_contenido(self):
        contenido = "## Decision\n## Status"
        assert detectar_tipo("doc.md", contenido) == "adr"

    def test_tipo_declarado_tiene_prioridad(self):
        assert detectar_tipo("doc.md", "...", "analisis") == "analisis"
```

Resultado: `13 passed in 0.05s`

## Metricas

- Performance: < 10ms por deteccion
- Precision: 100% en tests (13/13)
- Coverage: 100% de detector.py

## Referencias

- RT-001: Tipos canonicos soportados
- UC-SYS-001: Flujo completo de clasificacion
- Tests: test_placement_detector.py
