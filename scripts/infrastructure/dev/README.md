# Scripts de Desarrollo - Spec-Driven Development

Scripts de utilidad para desarrollo local guiado por especificaciones formales.

## Scripts Disponibles

### 1. validate_spec.sh

Valida especificaciones de features contra esquema requerido.

**Uso**:
```bash
# Validar una spec específica
./scripts/dev/validate_spec.sh docs/specs/mi-feature.md

# Validar todas las specs en docs/specs/
./scripts/dev/validate_spec.sh --all

# Usando Makefile
make validate_spec SPEC=docs/specs/mi-feature.md
make validate_spec  # Valida todas
```

**Validaciones que realiza**:
- Front matter YAML presente
- Campos de metadata requeridos (id, tipo, version, fecha_creacion)
- Secciones requeridas (12 secciones principales)
- ID de especificación en formato SPEC-XXX-NNN
- Criterios de aceptación en formato Given-When-Then
- Trazabilidad a requisitos (REQ-*, SPEC-*, ADR-*)
- Sin emojis

**Exit codes**:
- `0`: Especificación válida
- `1`: Especificación inválida o error

---

### 2. check_all.sh

Ejecuta todos los checks de calidad localmente antes de commit/push.

**Uso**:
```bash
# Ejecutar todos los checks
./scripts/dev/check_all.sh

# Con auto-corrección
./scripts/dev/check_all.sh --fix

# Output detallado
./scripts/dev/check_all.sh --verbose

# Usando Makefile
make check_all
make check_all-fix
```

**Checks que ejecuta**:
1. **Pre-commit hooks**:
   - Ruff (linting y formatting)
   - MyPy (type checking)
   - Bandit (security scanning)
   - detect-secrets (secrets detection)
   - Pre-commit estándar (trailing whitespace, etc.)
   - Django-upgrade
   - No-emojis

2. **Validación de emojis**: Verifica archivos modificados

3. **Validación de specs**: Si existen especificaciones en docs/specs/

4. **Estado de Git**: Muestra archivos modificados y staged

**Flags**:
- `--fix`: Intenta auto-corregir issues (ejecuta ruff format, etc.)
- `--verbose, -v`: Output detallado de cada check
- `--help, -h`: Muestra ayuda

**Exit codes**:
- `0`: Todos los checks pasaron
- `1`: Al menos un check falló

---

### 3. generate_plan.sh

Genera plan de implementación desde una especificación existente.

**Uso**:
```bash
# Generar plan (nombre auto-generado)
./scripts/dev/generate_plan.sh docs/specs/mi-feature.md

# Especificar nombre del plan
./scripts/dev/generate_plan.sh docs/specs/mi-feature.md docs/plans/custom-plan.md

# Usando Makefile
make generate_plan SPEC=docs/specs/mi-feature.md
```

**Qué hace**:
1. Valida la especificación (opcional pero recomendado)
2. Copia plantilla de plan (docs/plantillas/desarrollo/plantilla_plan.md)
3. Extrae metadata de la spec (ID, título, versión)
4. Pre-llena el plan con datos de la spec:
   - ID del plan (PLAN-XXX-NNN)
   - Nombre de la feature
   - Referencia a la spec
   - Fecha de creación
5. Crea archivo en docs/plans/

**Próximos pasos después de generar**:
1. Abrir el plan generado
2. Completar secciones marcadas con [...]
3. Agregar tareas detalladas en Fases 1-7
4. Actualizar estimaciones de tiempo
5. Commit del plan

**Exit codes**:
- `0`: Plan generado exitosamente
- `1`: Error (spec no válida o archivo ya existe)

---

## Workflow Típico

### Para Features Complejas

1. **Crear especificación**:
   ```bash
   cp docs/plantillas/desarrollo/plantilla_spec.md docs/specs/mi-feature.md
   # Editar y completar spec
   ```

2. **Validar especificación**:
   ```bash
   make validate_spec SPEC=docs/specs/mi-feature.md
   ```

3. **Generar plan de implementación**:
   ```bash
   make generate_plan SPEC=docs/specs/mi-feature.md
   # Editar y completar plan
   ```

4. **Desarrollar feature** (siguiendo el plan)

5. **Validar antes de commit**:
   ```bash
   make check_all
   ```

6. **Auto-corregir si hay errores menores**:
   ```bash
   make check_all-fix
   ```

7. **Commit y push**

### Para Cambios Simples

1. **Hacer cambios en código**

2. **Validar antes de commit**:
   ```bash
   make check_all
   ```

3. **Commit y push**

---

## Integración con CI/CD

Estos scripts son complementarios a los workflows de GitHub Actions. Se recomienda ejecutar `check_all.sh` localmente antes de push para detectar problemas temprano.

Los mismos checks se ejecutan en CI/CD:
- `.github/workflows/python_ci.yml`: Ruff, MyPy, Bandit, pytest
- `.github/workflows/lint.yml`: Markdown, YAML linting

---

## Troubleshooting

### "pre-commit no está instalado"

```bash
pip install pre-commit
cd api/callcentersite
pre-commit install
```

### "Script no encontrado"

Verificar que el script tiene permisos de ejecución:
```bash
chmod +x scripts/dev/*.sh
```

### "python: command not found"

Asegurar que Python 3.11+ está instalado y en PATH:
```bash
python3 --version
```

### Checks fallan en CI pero pasan localmente

Ejecutar con exactamente las mismas versiones:
```bash
cd api/callcentersite
pip install -r requirements/dev.txt
pre-commit run --all-files
```

---

## Referencias

- [Constitution para Agentes AI](../../docs/gobernanza/agentes/constitution.md)
- [Plantilla de Especificación](../../docs/plantillas/desarrollo/plantilla_spec.md)
- [Plantilla de Plan](../../docs/plantillas/desarrollo/plantilla_plan.md)
- [Guía de Desarrollo de Features](../../docs/gobernanza/procesos/guia_completa_desarrollo_features.md)
- [Guía de Estilo](../../docs/gobernanza/GUIA_ESTILO.md)

---

**Versión**: 1.0.0
**Fecha**: 2025-11-06
**Mantenido por**: equipo-desarrollo
