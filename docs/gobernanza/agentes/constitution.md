---
id: DOC-AGENTES-CONSTITUTION
tipo: constitution
estado: activo
propietario: equipo-ia
ultima_actualizacion: 2025-11-06
---
# Constitution para Agentes IA - Proyecto IACT

## Principios Fundamentales

### 1. Restricciones IACT
Los agentes DEBEN respetar todas las restricciones del proyecto:
- Sin emojis
- Python para scripts (NO JavaScript excepto frontend)
- Sin Redis
- Sin email
- Base de datos IVR read-only
- ETL batch (6-12h)

### 2. Documentacion
- Siempre incluir front matter YAML
- Mantener trazabilidad de requisitos
- Actualizar README cuando sea relevante

### 3. Conformidad con Estandares
- ISO/IEC/IEEE 29148:2018 para requisitos
- BABOK v3 para analisis de negocio
- PMBOK 7th Ed para gestion de proyectos
- ADRs para decisiones arquitectonicas

### 4. Calidad de Codigo
- PEP 8 para Python
- ESLint para JavaScript
- Type hints obligatorios
- Tests >70% coverage

### 5. Organizacion por Dominio
Seguir ADR_010:
- Codigo en: `/api/`, `/ui/`, `/infrastructure/`
- Documentacion en: `docs/implementacion/{dominio}/`
- Requisitos co-localizados con codigo

## Comportamientos Esperados

### Al Generar Codigo
1. Usar Python para scripts de automatizacion
2. Incluir type hints y docstrings
3. Escribir tests
4. NO usar emojis en codigo o comentarios

### Al Generar Documentacion
1. Incluir front matter YAML
2. Usar nomenclatura consistente
3. Mantener trazabilidad de requisitos
4. NO usar emojis

### Al Trabajar con Requisitos
1. Usar formato ISO 29148
2. Mantener trazabilidad bidireccional
3. Actualizar indices auto-generados
4. Vincular con necesidades de negocio

## Ejemplos

### Correcto
```python
#!/usr/bin/env python3
"""
Script de procesamiento ETL.

Restricciones IACT:
- IVR DB read-only
- ETL batch cada 6-12h
- Sin Redis
"""
from typing import List, Dict
from pathlib import Path

def procesar_datos(archivos: List[Path]) -> Dict[str, int]:
    """
    Procesa archivos de datos IVR.

    Args:
        archivos: Lista de paths a archivos

    Returns:
        Diccionario con estadisticas
    """
    # Implementacion...
    pass
```

### Incorrecto
```javascript
// Script de procesamiento - INCORRECTO: usar Python
const fs = require('fs');

function procesarDatos(archivos) {
    // Procesamiento con emojis
    console.log('Procesando archivos'); // INCORRECTO: emoji
    // ...
}
```

## Referencias

- docs/gobernanza/GUIA_ESTILO.md
- ADR_010: Organizacion por Dominio
- ISO/IEC/IEEE 29148:2018
