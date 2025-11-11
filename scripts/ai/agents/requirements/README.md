---
id: SCRIPTS-REQ-INDEX
tipo: documentacion
titulo: Scripts para Gestión de Requisitos
fecha: 2025-11-03
relacionados: ["DOC-GOB-CODING-STANDARDS", "DOC-GOB-SHELL-GUIDE"]
---

# Scripts para Gestión de Requisitos

Scripts simples y fáciles de ejecutar para trabajar con requisitos en `docs/implementacion/`.

**IMPORTANTE**: Estos scripts implementan los estándares definidos en:
- [Estándares de Código](../../docs/gobernanza/estandares_codigo.md) - Regla Fundamental de Output Profesional
- [Shell Scripting Guide](../../docs/gobernanza/shell_scripting_guide.md) - Guía completa de shell scripting

---

## Estándares de Formato

Todos los scripts en esta carpeta siguen estos principios de diseño:

### 1. Formato Profesional
- **Sin emojis**: Código limpio y corporativo sin decoración innecesaria
- **Etiquetas de texto**: Uso de prefijos claros y consistentes para mensajes

### 2. Etiquetas Estándar

| Etiqueta | Uso | Ejemplo |
|----------|-----|---------|
| `ERROR:` | Errores críticos que requieren atención | `ERROR: No existe la carpeta docs/implementacion` |
| `ADVERTENCIA:` | Alertas que no son críticas | `ADVERTENCIA: No se encontraron requisitos funcionales` |
| `INFO:` | Información general | `INFO: Recopilando requisitos...` |
| `SUCCESS:` | Operación completada exitosamente | `SUCCESS: Índices generados exitosamente` |
| `GENERANDO:` | Proceso en ejecución | `GENERANDO: BRS (Business Requirements Specification)...` |
| `ACCION REQUERIDA:` | Usuario debe hacer algo | `ACCION REQUERIDA: Instalar dependencias` |

### 3. Principios de Diseño
- **Enfoque en funcionalidad**: Scripts directos sin complejidad innecesaria
- **Idempotencia**: Pueden ejecutarse múltiples veces de forma segura
- **Auto-detección inteligente**: Detectan y manejan problemas automáticamente
- **Sin opciones YAGNI**: No incluyen flags innecesarios como `--force` si la idempotencia está bien implementada
- **Información metodológica en documentación**: Explicaciones de metodología van en READMEs, no en código

---

## Scripts Disponibles

### 1. Generar Índices ISO 29148

**Archivo**: `generar_indices.py`

**¿Qué hace?**
- Escanea todos los requisitos en `docs/implementacion/`
- Genera índices ISO 29148 en `docs/requisitos/`:
  - BRS (Business Requirements Specification)
  - StRS (Stakeholder Requirements Specification)
  - SRS (Software Requirements Specification)
  - RTM (Requirements Traceability Matrix)

**Uso**:
```bash
# Desde la raíz del proyecto
python scripts/requisitos/generar_indices.py
```

**Salida ejemplo**:
```
INFO: Recopilando requisitos...
GENERANDO: BRS (Business Requirements Specification)...
GENERANDO: StRS (Stakeholder Requirements Specification)...
GENERANDO: SRS (Software Requirements Specification)...
GENERANDO: RTM (Requirements Traceability Matrix)...
SUCCESS: Índices generados exitosamente en docs/requisitos/

ESTADISTICAS:
   Total de requisitos: 22
   - Necesidades: 2
   - Negocio: 3
   - Stakeholders: 5
   - Funcionales: 8
   - No_funcionales: 4
```

**Cuándo ejecutar**:
- Después de crear/modificar cualquier requisito
- Antes de commit/push
- Para verificar trazabilidad

---

### 2. Contar Requisitos

**Archivo**: `contar_requisitos.sh`

**¿Qué hace?**
- Cuenta requisitos por tipo (necesidades, negocio, stakeholders, funcionales, no funcionales)
- Cuenta requisitos por dominio (backend, frontend, infrastructure)
- Muestra total

**Uso**:
```bash
# Desde la raíz del proyecto
bash scripts/requisitos/contar_requisitos.sh

# O dar permisos y ejecutar directamente
chmod +x scripts/requisitos/contar_requisitos.sh
./scripts/requisitos/contar_requisitos.sh
```

**Salida ejemplo**:
```
======================================
CONTADOR DE REQUISITOS
======================================

INFO: Buscando en: docs/implementacion

Requisitos por tipo:
  Necesidades (N-XXX):        2
  Negocio (RN-XXX):           3
  Stakeholders (RS-XXX):      5
  Funcionales (RF-XXX):       8
  No Funcionales (RNF-XXX):   4

======================================
  TOTAL:                      22
======================================

Requisitos por dominio:
  Backend:                    15
  Frontend:                   5
  Infrastructure:             2
```

---

### 3. Validar Frontmatter

**Archivo**: `validar_frontmatter.py`

**¿Qué hace?**
- Verifica que todos los requisitos tengan frontmatter YAML
- Valida campos obligatorios: `id`, `tipo`, `titulo`, `dominio`, `owner`, `estado`
- Reporta archivos con errores

**Uso**:
```bash
# Desde la raíz del proyecto
python scripts/requisitos/validar_frontmatter.py
```

**Salida ejemplo**:
```
======================================================================
VALIDADOR DE FRONTMATTER YAML
======================================================================

INFO: Validando 10 archivos...

VALIDO: implementacion/backend/requisitos/funcionales/rf001_api_stock.md
INVALIDO: implementacion/backend/requisitos/funcionales/rf002_alertas.md
   Error: Faltan campos obligatorios
   Faltan: trazabilidad_upward, stakeholders

======================================================================
RESUMEN
======================================================================
Validos:   8
Invalidos: 2

ADVERTENCIA: Archivos con errores:
   - implementacion/backend/requisitos/funcionales/rf002_alertas.md

Campos obligatorios:
   - id
   - tipo
   - titulo
   - dominio
   - owner
   - estado

Consulta las plantillas en: docs/plantillas/
```

---

### 4. Listar Requisitos

**Archivo**: `listar_requisitos.sh`

**¿Qué hace?**
- Lista todos los requisitos organizados por tipo
- Muestra ID, título y estado de cada uno
- Útil para overview rápido

**Uso**:
```bash
bash scripts/requisitos/listar_requisitos.sh

# O con permisos
chmod +x scripts/requisitos/listar_requisitos.sh
./scripts/requisitos/listar_requisitos.sh
```

**Salida ejemplo**:
```
======================================
LISTA DE REQUISITOS
======================================

NECESIDADES DE NEGOCIO (N-XXX):
  N-001 - Reducir roturas de stock [aprobado]
  N-002 - Mejorar satisfacción cliente [propuesto]

REQUISITOS DE NEGOCIO (RN-XXX):
  RN-001 - Sistema de alertas automáticas [aprobado]

REQUISITOS FUNCIONALES (RF-XXX):
  RF-001 - API calcular stock mínimo [aprobado]
  RF-002 - Dashboard de alertas [en_desarrollo]

REQUISITOS NO FUNCIONALES (RNF-XXX):
  RNF-001 - Tiempo de respuesta < 200ms [aprobado]
```

---

## Flujo de Trabajo Típico

### Al crear/modificar requisitos:

```bash
# 1. Crear o editar requisito
vim docs/implementacion/backend/requisitos/funcionales/rf001_nuevo.md

# 2. Validar frontmatter
python scripts/requisitos/validar_frontmatter.py

# 3. Generar índices actualizados
python scripts/requisitos/generar_indices.py

# 4. Ver conteo actualizado
bash scripts/requisitos/contar_requisitos.sh

# 5. Commit y push
git add docs/implementacion/ docs/requisitos/
git commit -m "feat(req): agregar RF-001 nuevo requisito"
git push
```

---

## Permisos de Ejecución

Si encuentras error de permisos:

```bash
# Dar permisos a todos los scripts
chmod +x scripts/requisitos/*.sh
chmod +x scripts/requisitos/*.py
```

---

## Ubicaciones Importantes

| Carpeta | Contenido |
|---------|-----------|
| `docs/implementacion/` | Requisitos originales (source of truth) |
| `docs/requisitos/` | Índices auto-generados (NO editar manualmente) |
| `docs/plantillas/` | Templates para crear requisitos |
| `scripts/requisitos/` | Scripts de gestión (este directorio) |

---

## Recordatorios

1. **Índices auto-generados**: NO editar manualmente archivos en `docs/requisitos/`
2. **Ejecutar después de cambios**: Siempre ejecutar `generar_indices.py` después de modificar requisitos
3. **Validar antes de commit**: Usar `validar_frontmatter.py` antes de hacer commit
4. **Desde raíz del proyecto**: Todos los scripts deben ejecutarse desde la raíz del proyecto

---

## Solución de Problemas

### "No se encontraron archivos"
- Verificar que estás en la raíz del proyecto
- Verificar que existe `docs/implementacion/`
- Verificar que hay archivos `.md` en subdirectorios

### "Error de Python: módulo yaml no encontrado"
```bash
pip install pyyaml
```

### "Permission denied"
```bash
chmod +x scripts/requisitos/*.sh
chmod +x scripts/requisitos/*.py
```

---

## Referencias

**Documentación del Proyecto:**
- [Estructura de Implementación](../../docs/implementacion/README.md)
- [Plantillas ISO 29148](../../docs/plantillas/readme.md)
- [Glosario BABOK/PMBOK/ISO](../../docs/anexos/glosario_babok_pmbok_iso.md)

**Estándares y Guías:**
- [Estándares de Código - Regla Fundamental](../../docs/gobernanza/estandares_codigo.md#regla-fundamental-output-profesional)
- [Shell Scripting Guide Completa](../../docs/gobernanza/shell_scripting_guide.md)
- [Plantillas de Scripts](../templates/README.md)

---

**Última actualización**: 2025-11-03
