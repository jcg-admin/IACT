# ADR-010: Organización del Proyecto por Dominio

**Estado:** Aceptado
**Fecha:** 2025-11-06
**Decisor:** Equipo Desarrollo
**Relacionado:** Estructura general del proyecto
**Actualizado:** 2025-11-06

---

## Contexto

El proyecto IACT es un sistema complejo que incluye múltiples componentes: backend (API Django), frontend (React - futuro), infraestructura (Vagrant, DevContainers, build systems), y documentación técnica.

### Problema

Tradicionalmente, los proyectos se organizan por **tipo de archivo** (seguir convenciones como src/, tests/, scripts/, docs/), pero esto puede generar problemas de cohesión cuando el proyecto crece:

- Archivos relacionados funcionalmente están dispersos en diferentes directorios raíz
- Dificulta la navegación: para trabajar en infraestructura, hay que tocar scripts/, tests/, docs/, artifacts/
- Escalabilidad limitada: cuando se agregan nuevos dominios (ui/, api/), la raíz se satura
- Falta de boundaries claros entre dominios

### Opciones Evaluadas

Se consideraron 3 enfoques principales:

1. **Organización por dominio** (opción seleccionada)
2. Organización por tipo de archivo (convención tradicional)
3. Organización híbrida (mix de ambas)

---

## Decisión

**Usaremos organización por DOMINIO** en la raíz del proyecto.

Cada dominio principal tendrá su propio directorio que contendrá TODO lo relacionado con ese dominio: código, tests, scripts específicos, y artefactos generados.

### Estructura Resultante

```
/IACT---project/
├── api/                      # Dominio: Backend Django
│   ├── (código de API)
│   ├── tests/               # (futuro: tests de API)
│   └── scripts/             # (futuro: scripts específicos de API)
│
├── ui/                       # Dominio: Frontend React (futuro)
│   ├── (código de UI)
│   ├── tests/               # (futuro: tests de UI)
│   └── scripts/             # (futuro: scripts de build UI)
│
├── infrastructure/           # Dominio: Infraestructura
│   ├── cpython/             # Subdomain: CPython (builder, feature, artifacts)
│   ├── devcontainer/        # Configuración DevContainer
│   ├── artifacts/           # Outputs compartidos (no CPython)
│   ├── scripts/             # Scripts de infraestructura no-CPython
│   ├── tests/               # Tests de infraestructura no-CPython
│   ├── vagrant/             # VMs de infraestructura no-CPython
│   └── box/
│
├── docs/                     # Dominio: Documentación
│   ├── specs/
│   ├── adr/
│   ├── infraestructura/
│   ├── api/
│   └── gobernanza/
│
├── features/                 # Features de DevContainer (convención)
│
├── scripts/                  # Scripts cross-cutting
│   ├── dev/                 # Herramientas de desarrollo
│   ├── ai/                  # Generación con IA
│   └── templates/           # Templates compartidos
│
├── .devcontainer/            # Convención VS Code
├── .github/                  # Convención GitHub
└── respaldo/                 # Temporal/legacy
```

---

## Justificación

### Por qué Organización por Dominio

**Cohesión:**
- Todo lo relacionado con infraestructura está en `infrastructure/`
- Fácil encontrar: scripts → `infrastructure/scripts/`, tests → `infrastructure/tests/`
- Boundaries claros entre dominios

**Escalabilidad:**
- Cuando se agregue `ui/`, tendrá su propia estructura completa
- No satura la raíz con directorios genéricos (scripts/, tests/, artifacts/)
- Cada dominio puede evolucionar independientemente

**Navegación:**
- "Trabajar en infraestructura" = entrar a `infrastructure/`
- "Trabajar en API" = entrar a `api/`
- No saltar entre 5 directorios raíz diferentes

**Consistencia con arquitectura:**
- Refleja la arquitectura del sistema (dominios separados)
- Facilita modularización futura
- Permite equipos especializados por dominio

### Por qué NO Organización por Tipo de Archivo

**Contra:**
- Dispersión: infraestructura necesitaría tocar scripts/, tests/, artifacts/ en raíz
- Raíz saturada: artifacts/, tests/, scripts/, features/, docs/, api/, ui/, etc.
- Boundaries difusos: ¿un test de infraestructura va en tests/ o infrastructure/?
- No escala: agregar nuevos dominios satura aún más la raíz

**Ejemplos problemáticos con tipo de archivo:**
```
/
├── scripts/
│   ├── api/          # Scripts de API
│   ├── infra/        # Scripts de infra
│   └── ui/           # Scripts de UI
├── tests/
│   ├── api/          # Tests de API
│   ├── infra/        # Tests de infra
│   └── ui/           # Tests de UI
└── artifacts/
    ├── api/          # Artifacts de API
    ├── infra/        # Artifacts de infra
    └── ui/           # Artifacts de UI
```

Resultado: para trabajar en infraestructura hay que tocar 3+ directorios raíz.

---

## Consecuencias

### Positivas

1. **Cohesión mejorada**: Todo lo de un dominio junto
2. **Escalabilidad**: Agregar dominios no satura raíz
3. **Navegación clara**: Un dominio = un directorio
4. **Modularización**: Boundaries claros entre dominios
5. **Onboarding más fácil**: Estructura intuitiva
6. **Migración futura facilitada**: Cada dominio puede convertirse en repo separado si es necesario

### Negativas (mitigadas)

1. **Duplicación de estructura**: Cada dominio tiene tests/, scripts/
   - **Mitigación**: Scripts cross-cutting en scripts/ raíz

2. **Convenciones tradicionales**: Difiere de proyectos tipo src/, tests/
   - **Mitigación**: Es más moderno y escalable (usado por monorepos)

3. **Descubrimiento inicial**: Desarrolladores nuevos deben aprender estructura
   - **Mitigación**: Este ADR + README documentan la decisión

### Neutrales

1. **features/ en raíz**: Mantenido por convención de DevContainers
2. **scripts/ raíz**: Mantiene herramientas cross-cutting (dev/, ai/)
3. **.devcontainer/, .github/**: Convenciones de herramientas externas

---

## Migración Realizada

La reorganización se aplicó al dominio `infrastructure/` moviendo:

```bash
artifacts/           → infrastructure/artifacts/
tests/integration/   → infrastructure/tests/
scripts/infra/       → infrastructure/scripts/
```

**Archivos actualizados:** 16
- Vagrantfile (synced folders)
- Makefile (paths de targets)
- Scripts wrapper (paths internos)
- Tests (variables BASE_DIR, SCRIPTS_INFRA_DIR, ARTIFACTS_DIR)
- Features (ejemplos de artifactUrl)
- Documentación (todas las referencias)

**Commit:** `341f95d` - refactor: reorganizar proyecto por dominio

### Fase 2: Reorganización de CPython como Subdomain

Se reorganizó todo CPython en `infrastructure/cpython/` como subdomain:

```bash
infrastructure/vagrant/cpython-builder/  → infrastructure/cpython/builder/
features/cpython-prebuilt/               → infrastructure/cpython/feature/
infrastructure/artifacts/cpython/        → infrastructure/cpython/artifacts/
infrastructure/scripts/build-cpython.sh  → infrastructure/cpython/scripts/build-cpython.sh
infrastructure/scripts/validate-*.sh     → infrastructure/cpython/scripts/validate-*.sh
infrastructure/tests/test_cpython_*.py   → infrastructure/cpython/tests/test_cpython_*.py
```

### Fase 3: Consolidación Completa en Builder

Se consolidó TODOS los componentes CPython dentro de `builder/` para máxima cohesión:

```bash
infrastructure/cpython/feature/     → infrastructure/cpython/builder/feature/
infrastructure/cpython/artifacts/   → infrastructure/cpython/builder/artifacts/
infrastructure/cpython/scripts/     → infrastructure/cpython/builder/scripts/ (renombrados a *-wrapper.sh)
infrastructure/cpython/tests/       → infrastructure/cpython/builder/tests/
```

**Archivos actualizados:** 20+
- Makefile (todos los targets CPython)
- Vagrantfile (synced folders, documentación)
- Scripts wrapper (PROJECT_ROOT, VAGRANT_DIR, ARTIFACT_PATH)
- Tests (BASE_DIR, FEATURE_DIR, paths)
- devcontainer-feature.json (documentationURL)
- Documentación (6 archivos en docs/)

**Resultado**: Máxima cohesión de CPython - todo en un solo lugar.

---

## Ejemplos de Uso Futuro

### Agregar Tests de API

```bash
# Antes (tipo de archivo):
tests/
  ├── api/
  │   └── test_endpoints.py
  └── infra/
      └── test_vagrant.py

# Después (por dominio):
api/
  └── tests/
      └── test_endpoints.py

infrastructure/
  └── tests/
      └── test_vagrant.py
```

### Agregar Scripts de UI

```bash
# Después (por dominio):
ui/
  ├── src/
  ├── scripts/
  │   ├── build.sh         # Build de producción
  │   └── analyze.sh       # Análisis de bundle
  └── tests/
```

### Scripts Cross-Cutting

Scripts que sirven a TODOS los dominios permanecen en raíz:

```bash
scripts/
  ├── dev/
  │   ├── check-all.sh        # Valida todo el proyecto
  │   ├── validate-spec.sh    # Valida specs
  │   └── generate-plan.sh    # Genera planes
  ├── ai/
  │   └── run_test_generation.sh
  └── templates/
      └── bash-script-template.sh
```

---

## Decisiones Complementarias

### Features en Raíz

**Decisión**: `features/` permanece en raíz
**Razón**: Convención de DevContainers Specification
- DevContainers espera features en `./features/` o `.devcontainer/features/`
- Mantener convención facilita adopción e integración

### Scripts Cross-Cutting

**Decisión**: `scripts/` raíz para herramientas cross-domain
**Razón**:
- Algunos scripts sirven a TODO el proyecto (check-all, validate-spec)
- Evita duplicación innecesaria
- Herramientas de desarrollo no pertenecen a un dominio específico

### Excepciones de Convenciones Externas

**Mantener en raíz**:
- `.devcontainer/` - Convención VS Code
- `.github/` - Convención GitHub Actions
- `.git/` - Obvio

**Razón**: Herramientas externas esperan estas ubicaciones

### Subdominios dentro de infrastructure/

**Decisión**: CPython organizado como subdominio en `infrastructure/cpython/`
**Razón**: Máxima cohesión de componentes relacionados

Cuando un dominio (como infrastructure) contiene subsistemas complejos con múltiples componentes (builder, feature, artifacts, scripts, tests), es mejor organizarlos como subdominios.

**Estructura de infrastructure/cpython/** (Fase 3 - Consolidación Completa):
```
infrastructure/
└── cpython/                    # Subdomain: Todo CPython
    └── builder/                # TODO el sistema CPython consolidado
        ├── Vagrantfile         # VM de compilación
        ├── bootstrap.sh        # Provisioning de VM
        ├── scripts/            # TODOS los scripts (VM + host wrapper)
        │   ├── build-cpython.sh          # Script de compilación (VM)
        │   ├── validate-build.sh         # Validación (VM)
        │   ├── build-wrapper.sh          # Wrapper host → VM
        │   ├── validate-wrapper.sh       # Wrapper host → VM
        │   └── feature-install.sh        # Instalación en DevContainer
        ├── feature/            # Dev Container Feature
        │   ├── devcontainer-feature.json
        │   ├── install.sh      # Symlink → ../scripts/feature-install.sh
        │   └── README.md
        ├── artifacts/          # Binarios compilados (.tgz)
        │   └── .gitkeep
        ├── tests/              # Tests de integración
        │   ├── test_cpython_build_system.py
        │   └── test_cpython_feature.py
        ├── utils/              # Utilidades de compilación
        └── README.md
```

**Ventajas del subdomain consolidado (Fase 3)**:
1. **Cohesión máxima absoluta**: TODO CPython en `builder/` - un solo punto de entrada
2. **Escalabilidad**: Permite agregar infrastructure/go/, infrastructure/node/ en el futuro
3. **Navegación clarísima**: "Trabajar en CPython" = "cd infrastructure/cpython/builder/"
4. **Modularización**: Cada subdomain puede tener su propia documentación y README
5. **Boundaries claros**: Separación completa entre subsistemas de infraestructura
6. **Eliminación de dispersión**: No más scripts/ separados de builder/, todo unificado
7. **Convención DevContainer respetada**: Symlink feature/install.sh mantiene compatibilidad

**Aplicación**:
- COMPLETADO Fase 2: Migración de CPython a subdomain (2025-11-06)
- COMPLETADO Fase 3: Consolidación completa en builder/ (2025-11-06)
- Todos los componentes unificados en infrastructure/cpython/builder/
- Referencias actualizadas en 30+ archivos:
  - Makefile (artifact paths)
  - devcontainer.json (feature path, artifact URL)
  - Vagrantfile (synced folders)
  - Scripts wrapper (PROJECT_ROOT, paths)
  - Tests (BASE_DIR, FEATURE_DIR, SCRIPTS_INFRA_DIR)
  - 11 archivos de documentación (*.md)

---

## Referencias

### Patrones Similares en la Industria

**Monorepos modernos:**
- Nx (Angular/React): Organiza por `apps/` y `libs/`
- Turborepo: Organiza por `packages/` (dominios)
- Lerna: Múltiples `packages/` independientes

**Arquitectura de software:**
- DDD (Domain-Driven Design): Organiza por dominios de negocio
- Clean Architecture: Separación por layers/dominios
- Microservicios: Cada servicio es un dominio separado

**Proyectos referencia:**
- Kubernetes: Organizado por dominios (api/, cmd/, pkg/)
- Terraform: Organizado por providers (dominios)

### Documentación del Proyecto

- Este ADR documenta la decisión y justificación
- README principal debe incluir mapa de navegación
- Cada dominio (`api/`, `ui/`, `infrastructure/`) debe tener su propio README

---

## Preguntas Frecuentes

### ¿Por qué no seguir la convención src/, tests/ tradicional?

Esa convención funciona bien para proyectos pequeños con un solo dominio. IACT tiene múltiples dominios (api, ui, infrastructure) que crecerán independientemente. Organización por dominio escala mejor.

### ¿Qué pasa con scripts que afectan múltiples dominios?

Van en `scripts/` raíz. Ejemplos:
- `scripts/dev/check-all.sh` - Valida todo el proyecto
- `scripts/ai/` - Herramientas de IA cross-cutting

### ¿Dónde van tests end-to-end que tocan API + UI?

Opción 1: En un nuevo directorio `e2e/` raíz
Opción 2: En el dominio principal que se está testeando
Decisión pendiente según caso de uso real.

### ¿Esto complica el proyecto?

Inicialmente puede parecer más complejo, pero:
- Facilita navegación a largo plazo
- Reduce búsqueda: "trabajar en X" = "cd X/"
- Escala mejor que saturar la raíz

---

## Estado de Implementación

- COMPLETADO: Migración de `infrastructure/` a dominio (2025-11-06)
- COMPLETADO: Reorganización de CPython como subdomain `infrastructure/cpython/` (2025-11-06)
- PENDIENTE: README principal actualizado con mapa de navegación
- PENDIENTE: Documentar en guía de desarrollo
- PENDIENTE: Aplicar a `api/` cuando se agreguen tests/scripts
- PENDIENTE: Aplicar a `ui/` cuando se implemente

---

**Mantenido por**: Equipo Desarrollo IACT
**Última revisión**: 2025-11-06
