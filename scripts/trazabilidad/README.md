# Scripts de Trazabilidad de Requisitos

Implementación de scripts de validación y generación de matrices de trazabilidad según **ADR-GOB-009: Trazabilidad entre Artefactos de Requisitos**.

## Ubicación

```
scripts/
├── validar-trazabilidad.sh          # Script bash para validación
├── generar-matriz-trazabilidad.py   # Script Python para matrices
└── trazabilidad/
    └── README.md                    # Esta documentación
```

## Arquitectura del Sistema de Trazabilidad

```
┌─────────────────────────────────────────────────────────────┐
│                    ARTEFACTOS DE REQUISITOS                 │
│  docs/gobernanza/requisitos/                                │
│                                                              │
│  ┌──────┐    ┌────────┐    ┌─────┐    ┌─────┐    ┌─────┐  │
│  │  RN  │ → │  RNEG  │ → │ UC  │ → │ RF  │ → │ RNF │  │
│  └──────┘    └────────┘    └─────┘    └─────┘    └─────┘  │
│   Reglas     Reqs.Neg.     Casos      Reqs.      Atributos │
│   Negocio                   de Uso    Func.      Calidad   │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Analiza
                           ↓
        ┌──────────────────────────────────────┐
        │   SCRIPTS DE TRAZABILIDAD            │
        │                                      │
        │  1. validar-trazabilidad.sh         │
        │     - Extrae IDs                    │
        │     - Valida referencias            │
        │     - Detecta errores               │
        │                                      │
        │  2. generar-matriz-trazabilidad.py  │
        │     - Construye grafo               │
        │     - Genera matrices               │
        │     - Análisis de cobertura         │
        └──────────────────────────────────────┘
                           │
                           │ Genera
                           ↓
        ┌──────────────────────────────────────┐
        │   OUTPUTS                            │
        │                                      │
        │  - Reportes de validación           │
        │  - Matrices de trazabilidad         │
        │  - Análisis de cobertura            │
        │  - Detección de problemas           │
        └──────────────────────────────────────┘
```

## 1. validar-trazabilidad.sh

### Descripción

Script bash que valida la integridad y correctitud de las referencias entre artefactos de requisitos.

### Características

- ✅ Validación de IDs únicos (patrón TIPO-DOMINIO-###)
- ✅ Detección de referencias rotas
- ✅ Identificación de IDs duplicados
- ✅ Detección de artefactos huérfanos
- ✅ Validación de referencias bidireccionales
- ✅ Output coloreado en terminal
- ✅ Modo verbose para debugging

### Uso

```bash
# Validación estándar
./scripts/validar-trazabilidad.sh

# Con detalles verbose
./scripts/validar-trazabilidad.sh -v

# Directorio personalizado
./scripts/validar-trazabilidad.sh -d docs/requisitos

# Sin colores (para logs)
./scripts/validar-trazabilidad.sh --no-color
```

### Exit Codes

- `0` - Validación exitosa
- `1` - Errores encontrados
- `2` - Uso incorrecto

### Output Ejemplo

```
Validando trazabilidad de requisitos...

[OK] IDs existentes encontrados: 6
[OK] Referencias totales encontradas: 36

[ERROR] Referencia rota: UC-BACK-003 mencionado en RNF-BACK-005 pero no existe
[WARNING] Artefacto huérfano: UC-FRONT-001 - no hay referencias desde otros

═══════════════════════════════════════════════════════════
           REPORTE DE VALIDACIÓN DE TRAZABILIDAD
═══════════════════════════════════════════════════════════

IDs únicos encontrados:      6
Referencias verificadas:     36
IDs duplicados:              0
Artefactos huérfanos:        1
Sin referencias salientes:   1

✓ Resultado: EXITOSO
```

### Validaciones Realizadas

| Validación | Descripción | Nivel |
|------------|-------------|-------|
| Formato de ID | Verifica patrón TIPO-DOMINIO-### | ERROR |
| Referencias rotas | IDs referenciados que no existen | ERROR |
| IDs duplicados | Mismo ID en múltiples archivos | ERROR |
| Artefactos huérfanos | Sin referencias entrantes | WARNING |
| Sin referencias salientes | UC/RF sin referencias a otros | WARNING |

## 2. generar-matriz-trazabilidad.py

### Descripción

Script Python que genera matrices de trazabilidad en formato Markdown para visualizar y analizar relaciones entre artefactos.

### Características

- ✅ Construcción automática de grafo de trazabilidad
- ✅ Tres tipos de matrices (vertical, horizontal, dominio)
- ✅ Análisis de cobertura
- ✅ Navegación ascendente y descendente
- ✅ Detección de artefactos sin referencias
- ✅ Solo usa stdlib (sin dependencias externas)

### Uso

#### Matriz Vertical (cadena completa)

```bash
python3 scripts/generar-matriz-trazabilidad.py --tipo vertical --dominio BACK
```

Muestra la cadena de trazabilidad vertical: RN → RNEG → UC → RF → RNF

#### Matriz Horizontal (análisis de un artefacto)

```bash
python3 scripts/generar-matriz-trazabilidad.py --tipo horizontal --id UC-BACK-001
```

Muestra todas las relaciones de un artefacto específico:
- Referencias salientes (a qué referencia)
- Referencias entrantes (quién lo referencia)
- Cadena ascendente (por qué existe)
- Cadena descendente (qué implementa)

#### Matriz de Dominio (análisis completo)

```bash
python3 scripts/generar-matriz-trazabilidad.py \
  --tipo dominio \
  --dominio BACK \
  --output docs/gobernanza/trazabilidad/matrices/MATRIZ-BACK-autenticacion.md
```

Genera matriz completa para un dominio con:
- Resumen ejecutivo
- Matriz vertical
- Artefactos por tipo
- Análisis de cobertura

### Tipos de Matrices

#### 1. Matriz Vertical

```markdown
| RN          | RNEG          | UC          | RF          | RNF          |
|-------------|---------------|-------------|-------------|--------------|
| RN-BACK-001 | RNEG-BACK-001 | UC-BACK-001 | RF-BACK-010 | RNF-BACK-005 |
```

#### 2. Matriz Horizontal

```markdown
# Matriz de Trazabilidad: UC-BACK-001

## Referencias Salientes
- RF-BACK-010: Validar Credenciales
- RN-BACK-001: Usuario Debe Estar Autenticado

## Referencias Entrantes
- RNEG-BACK-001: Sistema de Autenticación Seguro

## Cadena Ascendente (Por qué existe)
- RN-BACK-001: Usuario Debe Estar Autenticado

## Cadena Descendente (Qué implementa)
- RF-BACK-010: Validar Credenciales
```

#### 3. Matriz de Dominio

Documento completo con todas las secciones anteriores más análisis de cobertura.

### Argumentos

| Argumento | Valores | Descripción |
|-----------|---------|-------------|
| `--tipo` | vertical, horizontal, dominio | Tipo de matriz a generar |
| `--dominio` | BACK, FRONT, DEVOPS, QA, AI, GOB | Dominio a analizar |
| `--id` | UC-BACK-001, etc. | ID del artefacto (para horizontal) |
| `--output` | ruta/archivo.md | Archivo de salida (default: stdout) |
| `--dir` | ruta/directorio | Directorio de requisitos |

## Patrones de IDs

### Formato

```
TIPO-DOMINIO-###
```

### Tipos Válidos

| Código | Descripción |
|--------|-------------|
| RN | Reglas de Negocio |
| RNEG | Requerimientos de Negocio |
| UC | Casos de Uso |
| RF | Requisitos Funcionales |
| RNF | Atributos de Calidad (No Funcionales) |

### Dominios Válidos

| Código | Descripción |
|--------|-------------|
| BACK | Backend |
| FRONT | Frontend |
| DEVOPS | DevOps/Infraestructura |
| QA | Quality Assurance |
| AI | Inteligencia Artificial |
| GOB | Gobernanza |

### Ejemplos

```
RN-BACK-001    → Regla de Negocio #1 del Backend
UC-FRONT-025   → Caso de Uso #25 del Frontend
RF-DEVOPS-010  → Requisito Funcional #10 de DevOps
RNF-BACK-005   → Requisito No Funcional #5 del Backend
```

## Integración con CI/CD

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Validando trazabilidad de requisitos..."
if ! scripts/validar-trazabilidad.sh --no-color; then
    echo "❌ Validación de trazabilidad fallida"
    echo "   Corrige los errores antes de hacer commit"
    exit 1
fi
```

### GitHub Actions

```yaml
name: Validar Trazabilidad

on: [push, pull_request]

jobs:
  validar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Validar trazabilidad
        run: |
          ./scripts/validar-trazabilidad.sh

      - name: Generar matriz
        if: success()
        run: |
          python3 scripts/generar-matriz-trazabilidad.py \
            --tipo dominio --dominio BACK \
            --output matriz-back.md
```

## Casos de Uso Comunes

### 1. Validar antes de commit

```bash
scripts/validar-trazabilidad.sh -v
```

### 2. Generar matriz para revisión

```bash
python3 scripts/generar-matriz-trazabilidad.py \
  --tipo dominio --dominio BACK \
  --output docs/gobernanza/trazabilidad/matrices/MATRIZ-BACK-$(date +%Y%m%d).md
```

### 3. Analizar impacto de cambio en UC-BACK-001

```bash
python3 scripts/generar-matriz-trazabilidad.py \
  --tipo horizontal --id UC-BACK-001
```

### 4. Verificar cobertura de un dominio

```bash
python3 scripts/generar-matriz-trazabilidad.py \
  --tipo dominio --dominio FRONT | grep -A 20 "Análisis de Cobertura"
```

## Troubleshooting

### Error: "Referencia rota"

**Causa**: Se referencia un ID que no existe

**Solución**:
1. Verificar que el archivo del ID existe
2. Verificar que el ID está en el frontmatter del archivo
3. Crear el artefacto faltante si es necesario

### Warning: "Artefacto huérfano"

**Causa**: El artefacto no es referenciado por ningún otro

**Solución**:
1. Agregar referencias en artefactos de nivel superior
2. Si es intencional (ej: RN de alto nivel), ignorar el warning

### Warning: "Sin referencias salientes"

**Causa**: UC o RF no referencia a otros artefactos

**Solución**:
1. Agregar referencias a RN, RNEG relacionados
2. Documentar la justificación del artefacto

## Mantenimiento

### Actualizar scripts

Los scripts están en:
- `/home/user/IACT---project/scripts/validar-trazabilidad.sh`
- `/home/user/IACT---project/scripts/generar-matriz-trazabilidad.py`

### Ejecutar tests

```bash
# Validar con archivos de ejemplo
scripts/validar-trazabilidad.sh -d docs/gobernanza/requisitos/ejemplos_test

# Generar matrices de prueba
python3 scripts/generar-matriz-trazabilidad.py \
  --tipo vertical --dominio BACK \
  --dir docs/gobernanza/requisitos/ejemplos_test
```

## Referencias

- **ADR-GOB-009**: Trazabilidad entre Artefactos de Requisitos
- **ADR-GOB-005**: Jerarquía de Requerimientos en 5 Niveles
- **ISO/IEC/IEEE 29148:2018**: Requirements Engineering

## Contacto

**Mantenedor**: Equipo de Arquitectura IACT
**Versión**: 1.0.0
**Última actualización**: 2025-11-17
