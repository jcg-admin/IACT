# TASK-057: Validar Metadatos YAML

## Metadatos
- **ID**: TASK-057
- **Fase**: FASE 4 - Validación y Limpieza
- **Prioridad**: ALTA 🟡
- **Estimación**: 20 minutos
- **Estado**: PENDIENTE
- **Metodología**: Auto-CoT + Self-Consistency + Chain-of-Verification

## Descripción
Validar que todos los archivos de metadatos YAML (frontmatter en .md, archivos .yml, .yaml) tengan formato correcto, campos obligatorios y valores válidos.

## Auto-CoT: Razonamiento Paso a Paso

### Paso 1: Identificar Archivos con Metadatos
**Pensamiento**: ¿Dónde están los metadatos YAML?
1. **Frontmatter en Markdown**:
   - Archivos .md con sección `---` al inicio
   - READMEs con metadatos
   - Documentos con información estructurada

2. **Archivos YAML dedicados**:
   - Archivos .yml en configuración
   - Archivos .yaml en docs/
   - Manifiestos de proyectos

3. **Archivos de configuración**:
   - package.json (JSON pero puede tener refs a YAML)
   - docker-compose.yml
   - CI/CD configs (.github/, .gitlab-ci.yml)

### Paso 2: Definir Esquema Esperado
**Pensamiento**: ¿Qué campos son obligatorios/opcionales?

**Para Frontmatter en Documentos**:
```yaml
---
title: string (obligatorio)
description: string (obligatorio)
category: string (recomendado)
tags: array (opcional)
date: YYYY-MM-DD (opcional)
author: string (opcional)
version: string (opcional)
status: [draft|review|published] (recomendado)
---
```

**Para Archivos de Configuración**:
- Validar según schema específico del tipo
- docker-compose: version, services
- CI/CD: jobs, steps, etc.

### Paso 3: Determinar Métodos de Validación
**Pensamiento**: ¿Cómo valido sintaxis y contenido?
1. **Sintaxis YAML**: Parser YAML para detectar errores
2. **Esquema**: Validación contra JSON Schema
3. **Valores**: Verificar tipos y rangos permitidos
4. **Completitud**: Verificar campos obligatorios presentes

### Paso 4: Planificar Correcciones
**Pensamiento**: ¿Qué hago con YAML inválido?
- Documentar errores de sintaxis
- Agregar campos faltantes obligatorios
- Corregir formatos de fechas
- Estandarizar valores de enumeraciones

## Chain-of-Verification (CoVe)

### Verificación 1: Baseline Response
**Pregunta**: ¿Todos los archivos YAML son sintácticamente válidos?
**Método**: Parsear cada archivo YAML con un parser estricto

### Verificación 2: Plan Questions
**Preguntas de verificación**:
1. ¿El archivo se parsea sin errores?
2. ¿Tiene los campos obligatorios definidos en el esquema?
3. ¿Los tipos de datos son correctos? (string vs number vs array)
4. ¿Los valores están en rangos permitidos?
5. ¿Las fechas tienen formato válido (ISO 8601)?
6. ¿Los enums tienen valores permitidos?
7. ¿Las referencias a otros archivos son válidas?

### Verificación 3: Answer Questions Independently
Para cada archivo YAML:
```
Archivo: docs/backend/core/README.md
---
✅ Sintaxis: VÁLIDA
✅ Campo 'title': Presente, tipo string
✅ Campo 'description': Presente, tipo string
⚠️ Campo 'category': Ausente (recomendado)
✅ Campo 'status': Valor 'published' (válido)
❌ Campo 'date': Formato inválido '2024-1-5' -> debe ser '2024-01-05'
---
Estado: NECESITA CORRECCIÓN
```

### Verificación 4: Generate Final Verified Response
**Reporte Consolidado**:
- Total archivos YAML: X
- Sintácticamente válidos: Y
- Con errores de esquema: Z
- Lista de correcciones necesarias
- Prioridad de correcciones

## Self-Consistency: Validación Múltiple

### Enfoque 1: Parser Python (PyYAML)
```python
import yaml
import sys

def validate_yaml_file(filepath):
    try:
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return True, data
    except yaml.YAMLError as e:
        return False, str(e)

# Validar todos los archivos
# ...
```

### Enfoque 2: Parser JavaScript (js-yaml)
```javascript
const yaml = require('js-yaml');
const fs = require('fs');

function validateYAML(filepath) {
    try {
        const content = fs.readFileSync(filepath, 'utf8');
        const data = yaml.load(content);
        return { valid: true, data };
    } catch (e) {
        return { valid: false, error: e.message };
    }
}
```

### Enfoque 3: Herramienta CLI (yamllint)
```bash
# Instalar yamllint
pip install yamllint

# Validar archivos
yamllint docs/backend/**/*.yml
yamllint docs/backend/**/*.yaml

# Validar frontmatter en Markdown
# Extraer y validar sección entre ---
```

### Convergencia de Resultados
- Archivos que pasan en 3 parsers: ✅ VÁLIDO
- Archivos que fallan en 2+: ❌ INVÁLIDO
- Diferencias entre parsers: ⚠️ REVISAR (edge cases)

## Criterios de Aceptación
- [ ] Todos los archivos YAML identificados
- [ ] Sintaxis validada para 100% de archivos
- [ ] Esquema validado para archivos con frontmatter
- [ ] Errores documentados con ubicación exacta
- [ ] Campos obligatorios verificados
- [ ] Valores de enum validados
- [ ] Fechas en formato ISO 8601
- [ ] Reporte de validación generado

## Entregables
1. **REPORTE-VALIDACION-YAML.md**
   - Lista de archivos YAML encontrados
   - Errores de sintaxis por archivo
   - Errores de esquema por archivo
   - Estadísticas de validación
   - Recomendaciones

2. **YAML-SCHEMA.json**
   - JSON Schema para frontmatter estándar
   - Esquemas para tipos de documentos
   - Validación automática

3. **script-validar-yaml.py** o **.js**
   - Script de validación automatizada
   - Soporte para múltiples esquemas
   - Reporte en formato markdown

4. **CORRECCIONES-YAML.md**
   - Lista de correcciones aplicadas
   - Archivos modificados
   - Valores antes/después

## Esquema de Frontmatter Estándar

```yaml
---
# OBLIGATORIO
title: "Título del Documento"
description: "Descripción breve y clara"

# RECOMENDADO
category: "core|packages|components|services|utils|docs"
status: "draft|review|published|deprecated"

# OPCIONAL
tags:
  - tag1
  - tag2
date: "2025-11-18"  # ISO 8601: YYYY-MM-DD
updated: "2025-11-18"
author: "Nombre o ID"
version: "1.0.0"
related:
  - path/to/related/doc.md
  - path/to/another/doc.md
---
```

## Comandos Útiles

### Encontrar archivos YAML
```bash
# Archivos .yml y .yaml
find docs/backend -type f \( -name "*.yml" -o -name "*.yaml" \)

# Archivos Markdown con frontmatter
grep -l "^---$" docs/backend/**/*.md
```

### Validar sintaxis YAML
```bash
# Con yamllint
yamllint -f parsable docs/backend/**/*.yml

# Con Python
python -c "import yaml; yaml.safe_load(open('file.yml'))"

# Con Ruby
ruby -ryaml -e "YAML.load_file('file.yml')"
```

### Extraer frontmatter de Markdown
```bash
# Extraer sección entre --- y ---
awk '/^---$/,/^---$/' file.md | sed '1d;$d'
```

### Validar con JSON Schema
```bash
# Usando ajv-cli
npm install -g ajv-cli
ajv validate -s schema.json -d data.yml
```

## Validaciones Específicas

### 1. Sintaxis YAML
- [ ] No hay errores de indentación
- [ ] Comillas balanceadas
- [ ] Arrays con formato correcto
- [ ] Objetos anidados válidos

### 2. Tipos de Datos
- [ ] Strings entre comillas cuando contienen caracteres especiales
- [ ] Numbers sin comillas
- [ ] Booleans: true/false (no "true"/"false")
- [ ] Null explícito cuando necesario
- [ ] Arrays con elementos del mismo tipo esperado

### 3. Campos Obligatorios
- [ ] title presente y no vacío
- [ ] description presente y no vacío
- [ ] Otros según tipo de documento

### 4. Formatos Específicos
- [ ] Fechas en ISO 8601 (YYYY-MM-DD)
- [ ] URLs válidas (si hay campos url)
- [ ] Emails válidos (si hay campos email)
- [ ] Versiones semánticas (X.Y.Z)

### 5. Valores Enumerados
- [ ] status en [draft, review, published, deprecated]
- [ ] category en valores predefinidos
- [ ] priority en [low, medium, high, critical]

## Prioridades de Corrección

### P1 - CRÍTICO
- Errores de sintaxis que impiden parseo
- Campos obligatorios faltantes
- Valores de tipo incorrecto

### P2 - ALTO
- Campos recomendados faltantes
- Formatos de fecha incorrectos
- Valores de enum inválidos

### P3 - MEDIO
- Campos opcionales con formato incorrecto
- Inconsistencias de estilo
- Metadatos legacy a actualizar

## Dependencias
- TASK-003: Crear READMEs (frontmatter agregado)
- Estructura de carpetas finalizada

## Notas
- YAML es sensible a indentación (usar espacios, no tabs)
- Frontmatter en Markdown debe empezar en línea 1
- Validar encoding (UTF-8) en archivos con caracteres especiales
- Considerar agregar validación YAML al pre-commit hook

## Referencias
- [YAML Specification](https://yaml.org/spec/1.2.2/)
- [JSON Schema](https://json-schema.org/)
- [yamllint](https://yamllint.readthedocs.io/)
- [ISO 8601 Date Format](https://www.iso.org/iso-8601-date-and-time-format.html)
- Auto-CoT: Wei et al. (2022)
- Chain-of-Verification: Dhuliawala et al. (2023)
