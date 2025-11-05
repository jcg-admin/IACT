---
id: CLAUDE-CODE-CONVENTIONS
estado: activo
propietario: equipo-desarrollo
ultima_actualizacion: 2025-11-02
relacionados: ["copilot-instructions.md"]
---

# Convenciones de Claude Code para IACT Project

Este documento establece las reglas específicas que Claude Code debe seguir al trabajar en este repositorio.

## 1. Nomenclatura de Ramas

### Patrón Obligatorio
**TODAS** las ramas creadas por Claude Code deben seguir este patrón:

```
feature/<descripción-kebab-case>-<timestamp>
```

### Ejemplos del Repositorio
Basado en el historial del proyecto:

- OK: `feature/update-documentation-structure-20-07-56`
- OK: `feature/organize-documentation-into-respective-folders-02-11-38`
- OK: `feature/add-infrastructure-folder-in-docs-20-56-36`
- OK: `feature/fix-missing-.devcontainer/dockerfile-09-46-11`
- NO: `claude/code-session-setup-*` (solo para sesiones, NO para features)

### Otros Prefijos Permitidos
- `hotfix/` - Para correcciones urgentes en producción
- `bugfix/` - Para corrección de bugs no urgentes
- `docs/` - Para cambios exclusivos de documentación
- `refactor/` - Para refactorizaciones sin cambio funcional
- `test/` - Para adición o mejora de pruebas

### Ramas Especiales de Claude Code
- `claude/code-session-setup-<session-id>` - **ÚNICAMENTE** para sesiones de trabajo
- WARNING: **NUNCA** crear PRs desde ramas `claude/*` hacia main/develop
- WARNING: **SIEMPRE** crear una rama `feature/*` antes de hacer un PR

## 2. Flujo de Trabajo con Git

### Crear una Nueva Feature
```bash
# 1. Crear rama feature desde la rama base
git checkout -b feature/mi-nueva-funcionalidad-$(date +%H-%M-%S)

# 2. Realizar cambios y commits
git add .
git commit -m "tipo(alcance): descripción clara"

# 3. Push con upstream tracking
git push -u origin feature/mi-nueva-funcionalidad-HH-MM-SS
```

### Reintentos en Operaciones de Red
**CRÍTICO**: Para `git push` y `git fetch`:
- Reintentar hasta 4 veces con backoff exponencial
- Esperas: 2s, 4s, 8s, 16s
- Solo reintentar en errores de red, NO en errores 403

### Comandos Git Preferidos
```bash
# Fetch específico (preferido)
git fetch origin <branch-name>

# Pull específico (preferido)
git pull origin <branch-name>

# Push con upstream (SIEMPRE)
git push -u origin <branch-name>
```

## 3. Mensajes de Commit

### Formato: Conventional Commits
```
<tipo>(<alcance>): <descripción>

[cuerpo opcional]

[footer opcional]
```

### Tipos Válidos
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `refactor`: Refactorización sin cambio funcional
- `test`: Adición o modificación de tests
- `chore`: Cambios en build, configuración, etc.
- `perf`: Mejoras de rendimiento
- `style`: Formateo, punto y coma faltantes, etc.

### Ejemplos del Proyecto
```bash
OK: docs(mkdocs): reubicar configuración en directorio documental
OK: docs(solicitudes): centralizar guia sc00
OK: feat: agregar estructura transversal de requisitos
OK: feat: agregar tests de infraestructura y configuración
OK: merge: integrar cambios de documentación desde docs
```

## 4. Pull Requests

### Estructura de PR
Cuando se solicite crear un PR, SIEMPRE seguir este flujo:

```bash
# 1. Asegurarse de estar en rama feature/*
git checkout -b feature/descripcion-timestamp

# 2. Hacer commits
git add .
git commit -m "tipo(alcance): descripción"

# 3. Push
git push -u origin feature/descripcion-timestamp

# 4. Crear PR usando gh (si disponible) o solicitar al usuario
gh pr create --title "Título descriptivo" --body "$(cat <<'EOF'
## Summary
- Punto 1
- Punto 2

## Test plan
- [ ] Tests unitarios pasan
- [ ] Tests de integración pasan
- [ ] Revisión manual completada
EOF
)"
```

### Título del PR
- Descriptivo y conciso
- Indica el propósito principal del cambio
- Ejemplo: "Agregar estructura de documentación para solicitudes SC01"

### Descripción del PR
Siempre incluir:
1. **Summary**: Qué se cambió y por qué
2. **Test plan**: Checklist de verificación
3. **Related issues**: Referencias a issues (si aplica)

## 5. Estructura de Documentación

### Ubicación
- **Toda documentación** → `docs/`
- **Sin numeración** heredada (`00_`, `01_`, etc.)
- **Estructura replicada** de espacios corporativos

### Metadatos en Archivos Markdown
Todos los `readme.md` deben incluir frontmatter:

```yaml
---
id: IDENTIFICADOR-UNICO
estado: borrador|activo|deprecado
propietario: equipo-responsable
ultima_actualizacion: YYYY-MM-DD
relacionados: ["DOC-ID-1", "DOC-ID-2"]
---
```

### Navegación
- Cada carpeta tiene `readme.md` como portada
- Enlaces relativos entre documentos
- Índice maestro en `docs/index.md`

## 6. Testing y Calidad

### Principios TDD
1. **Escribir test primero** (failing test)
2. **Implementar código** mínimo para pasar
3. **Refactorizar** manteniendo tests verdes

### Cobertura Mínima
- **80%** de cobertura obligatoria
- Ejecutar tests ANTES de crear PR
- Verificar que todos los tests pasen

### Comando de Verificación
```bash
# Ejecutar suite completa
pytest

# Con cobertura
pytest --cov=. --cov-report=html
```

## 7. Estructura del Proyecto

### Directorio Raíz
```
IACT---project/
├── .github/                    # Configuración GitHub
│   ├── copilot-instructions.md # Guía para AI agents
│   ├── claude-code-conventions.md # Este archivo
│   └── agents/                 # Agentes personalizados
├── docs/                       # Toda la documentación
│   ├── index.md               # Índice maestro
│   ├── mkdocs.yml             # Configuración MkDocs
│   ├── backend/               # Docs backend
│   ├── frontend/              # Docs frontend
│   ├── infrastructure/        # Docs infra
│   ├── solicitudes/           # Docs por solicitud
│   └── spaces/                # Espacios corporativos
├── infrastructure/            # Código de infraestructura
│   └── devcontainer/         # Configuración DevContainer
├── provisioning/             # Scripts de aprovisionamiento
├── scripts/                  # Scripts de utilidad
├── tasks/                    # Playbooks operativos
├── requirements.txt          # Dependencias Python
└── readme.md                 # README principal
```

### Convenciones de Nombres
- **Archivos**: `kebab-case` (ej: `mi-archivo.py`)
- **Carpetas**: `snake_case` o `kebab-case` según contexto
- **Variables Python**: `snake_case`
- **Clases Python**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`

## 8. Stack Tecnológico

### Backend
- **Framework**: Django 5
- **Base de datos analítica**: PostgreSQL (puerto 15432)
- **Base de datos IVR**: MariaDB (puerto 13306)
- **Python**: 3.11+

### Infraestructura Local
- **Virtualización**: Vagrant + VirtualBox 7+
- **Credenciales**: `django_user` / `django_pass`

### Documentación
- **Motor**: MkDocs
- **Formato**: Markdown (CommonMark)

## 9. Checklist Pre-Commit

Antes de crear commits, verificar:

- [ ] Código sigue convenciones de estilo del proyecto
- [ ] Tests escritos y pasando
- [ ] Cobertura >= 80%
- [ ] Documentación actualizada (si aplica)
- [ ] Sin código comentado o debug
- [ ] Sin secrets o credenciales
- [ ] Mensaje de commit sigue Conventional Commits
- [ ] Cambios atómicos y enfocados

## 10. Checklist Pre-PR

Antes de crear Pull Request, verificar:

- [ ] Rama sigue patrón `feature/*`
- [ ] Todos los commits tienen mensajes descriptivos
- [ ] Tests pasan localmente
- [ ] Cobertura cumple mínimo 80%
- [ ] Documentación actualizada
- [ ] Sin conflictos con rama base
- [ ] PR description completa (Summary + Test plan)
- [ ] Referencias a issues relacionados

## 11. Prohibiciones Estrictas

### NUNCA hacer esto:
1. Push directo a `main` o `master`
2. Commit de secrets, API keys, credenciales
3. Push force a ramas compartidas
4. Amend commits de otros desarrolladores
5. Skip de hooks sin autorización explícita
6. Crear archivos sin leer primero si ya existen
7. Modificar código sin entenderlo
8. Commits con código comentado
9. PRs desde ramas `claude/*`
10. Ignorar fallos en tests

### Requiere autorización explícita:
- Force push a main/master
- Amend commits
- Rebase interactivo
- Cambios en `.gitconfig`
- Bypass de pre-commit hooks

## 12. Flujo Completo: Feature → PR

### Ejemplo Paso a Paso

```bash
# 1. Verificar estado actual
git status
git branch

# 2. Crear rama feature
TIMESTAMP=$(date +%H-%M-%S)
BRANCH_NAME="feature/agregar-analytics-dashboard-${TIMESTAMP}"
git checkout -b ${BRANCH_NAME}

# 3. Implementar cambios con TDD
# - Escribir test
# - Implementar código
# - Verificar test pasa
pytest

# 4. Commit siguiendo convenciones
git add .
git commit -m "feat(analytics): agregar dashboard de métricas

Implementa visualización de KPIs principales:
- Llamadas por hora
- Tiempo promedio de atención
- Tasa de abandono

Refs: #123"

# 5. Push con reintentos si falla
for i in {1..4}; do
  git push -u origin ${BRANCH_NAME} && break
  sleep $((2**i))
done

# 6. Crear PR
gh pr create --title "Agregar dashboard de analytics" \
  --body "## Summary
- Dashboard con 3 KPIs principales
- Integración con API de PostgreSQL
- Tests unitarios con cobertura 85%

## Test plan
- [x] Tests unitarios pasan
- [x] Verificación manual en entorno local
- [ ] Revisión por equipo frontend
"

# 7. Esperar revisión y merge
```

## 13. Scripts: Reglas de Output Profesional

### REGLA FUNDAMENTAL

**NUNCA usar emojis, iconos Unicode decorativos, ni símbolos especiales en el output de scripts de producción.**

### Política Estricta: Output Profesional

**TODOS** los scripts (`.sh`, `.bash`, `.ps1`, `.py` scripts CLI) deben producir output libre de decoraciones Unicode para garantizar:
- **Compatibilidad** con terminales antiguos y sistemas legacy
- **Profesionalismo** en entornos corporativos
- **Robustez** en sistemas sin soporte Unicode completo
- **Legibilidad** en logs, archivos y sistemas de CI/CD
- **Portabilidad** entre diferentes plataformas y encodings

### PROHIBICIONES ESTRICTAS

#### 1. Emojis
```bash
# NO HACER ESTO
echo "[COMPLETADO]"
echo "[ERROR]"
echo "[ADVERTENCIA]"
echo "[INICIANDO]"
echo "[PROCESANDO]"
echo "[GUARDANDO]"
echo "[BUSCANDO]"
echo "[ESPERANDO]"
echo "[NUEVO]"
echo "[EXITO]"
```

#### 2. Iconos Unicode Decorativos
```bash
# NO HACER ESTO
echo "[EJECUTANDO]"
echo "- Item"
echo "-> Siguiente"
echo "[IMPORTANTE]"
echo "[NOTA]"
echo "- Opción"
echo "- Paso"
echo "[INFO]"
```

#### 3. Box Drawing Characters
```bash
# NO HACER ESTO
echo "╔════════════╗"
echo "║   Título   ║"
echo "╚════════════╝"
echo "┌──────────┐"
echo "│  Caja    │"
echo "└──────────┘"
```

### SISTEMA DE PREFIJOS ESTÁNDAR

#### Niveles de Log
```bash
# HACER ESTO
echo "[INFO]    Información general"
echo "[DEBUG]   Detalles de depuración"
echo "[WARN]    Advertencia"
echo "[ERROR]   Error encontrado"
echo "[FATAL]   Error crítico"
echo "[SUCCESS] Operación exitosa"
echo "[OK]      Todo bien"
echo "[FAIL]    Operación falló"
```

#### Estados de Proceso
```bash
# HACER ESTO
echo "[PENDING]  Operación pendiente"
echo "[RUNNING]  En ejecución"
echo "[DONE]     Completado"
echo "[SKIPPED]  Omitido"
echo "[RETRY]    Reintentando"
echo "[START]    Iniciando"
echo "[STOP]     Deteniendo"
```

#### Viñetas y Listas
```bash
# HACER ESTO - Viñetas
echo "Options:"
echo "  - Option 1"
echo "  - Option 2"
echo "  * Alternative"

# HACER ESTO - Numeradas
echo "Steps:"
echo "  1. First step"
echo "  2. Second step"
echo "  3. Third step"
```

### Tabla de Referencia Rápida

| Concepto        | No Usar   | Usar                    |
| --------------- | --------- | ----------------------- |
| **Completado**  | emojis    | [OK] [SUCCESS] [DONE]   |
| **Error**       | emojis    | [ERROR] [FAIL] [FAILED] |
| **Advertencia** | emojis    | [WARN] [WARNING]        |
| **Información** | emojis    | [INFO] [NOTE]           |
| **Depuración**  | emojis    | [DEBUG]                 |
| **En proceso**  | emojis    | [RUNNING] [PROCESSING]  |
| **Esperando**   | emojis    | [PENDING] [WAITING]     |
| **Inicio**      | emojis    | [START] Starting...     |
| **Fin**         | emojis    | [STOP] [END] Finished   |
| **Archivo**     | emojis    | FILE: file.txt          |
| **Carpeta**     | emojis    | DIRECTORY: /path/       |
| **Red**         | emojis    | [NETWORK]               |
| **Usuario**     | emojis    | USER: username          |
| **Tiempo**      | emojis    | TIME: 10:30             |
| **Fecha**       | emojis    | DATE: 2025-10-21        |
| **Viñetas**     | Unicode   | - * 1. 2.               |
| **Flechas**     | Unicode   | -> =>                   |
| **Check**       | Unicode   | [OK] PASS               |
| **Cross**       | Unicode   | [FAIL] ERROR            |

### Ejemplos Completos

#### Script Incorrecto
```bash
#!/bin/bash
echo "[START] Iniciando proceso..."
echo "[INFO] Procesando archivos"
echo "  - Archivo 1"
echo "  - Archivo 2"
echo "[SUCCESS] Completado exitosamente"
echo ""
echo "RESUMEN"
echo "Archivos: 2"
echo "Errores: 0"
echo "[DONE] Proceso finalizado"
```

#### Script Correcto
```bash
#!/bin/bash
echo "[START] Iniciando proceso..."
echo "[INFO] Procesando archivos"
echo "  - Archivo 1"
echo "  - Archivo 2"
echo "[SUCCESS] Completado exitosamente"
echo ""
echo "RESUMEN"
echo "-------"
echo "Archivos: 2"
echo "Errores: 0"
echo "[DONE] Proceso finalizado"
```

### Alcance de la Regla

Esta regla aplica a:
- **Scripts Shell**: `.sh`, `.bash`, `.zsh`
- **Scripts PowerShell**: `.ps1`, `.psm1`
- **Scripts Python CLI**: scripts ejecutables que producen output de terminal
- **Scripts de CI/CD**: GitHub Actions, GitLab CI, Jenkins
- Ubicaciones específicas:
  - `.github/workflows/scripts/`
  - `infrastructure/devcontainer/scripts/`
  - `infrastructure/vagrant/scripts/`
  - `scripts/` (raíz del proyecto)
- **TODOS** los nuevos scripts creados
- **TODOS** los scripts existentes al modificarlos

### Excepciones

**No aplica a:**
- Archivos Markdown (`.md`) - pueden usar emojis para documentación
- Archivos de configuración (`.yml`, `.json`, `.toml`)
- Interfaces gráficas (GUI)
- Código fuente NO ejecutable (funciones internas, bibliotecas)
- Mensajes de commit Git
- Documentación técnica

### Verificación

Existe un script de verificación en:
```bash
infrastructure/devcontainer/scripts/check_no_emojis.sh
```

**IMPORTANTE**:
- Al crear o modificar scripts, verificar que no contengan emojis antes de hacer commit
- Los pre-commit hooks pueden rechazar commits con emojis en scripts
- En code reviews, verificar cumplimiento de esta regla

## Referencias

- [Copilot Instructions](copilot-instructions.md) - Guía general del proyecto
- [Conventional Commits](https://www.conventionalcommits.org) - Estándar de commits
- [MkDocs](https://www.mkdocs.org) - Documentación técnica

---

**Última actualización**: 2025-11-04
**Mantenedores**: Equipo de Desarrollo IACT

Este documento debe actualizarse cuando se establezcan nuevas convenciones o se identifiquen patrones recurrentes.
