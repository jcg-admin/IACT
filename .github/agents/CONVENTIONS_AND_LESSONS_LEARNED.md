# Convenciones y Lecciones Aprendidas - Agentes IACT

Este documento registra convenciones del proyecto y lecciones aprendidas para evitar errores repetidos.

---

## Convenciones de Ubicación de Documentación

### Regla General: Documentación sigue al Código

**Principio**: La ubicación de la documentación debe reflejar el tipo de código que documenta.

### Estructura de Documentación

```
docs/
├── backend/          # Documentación de código backend
│   ├── planning/
│   ├── feasibility/
│   ├── design/
│   ├── testing/      # Tests de código backend
│   └── deployment/
│
├── frontend/         # Documentación de código frontend
│   ├── components/
│   ├── testing/      # Tests de código frontend
│   └── ...
│
├── infrastructure/   # Documentación de infraestructura
│   ├── terraform/
│   ├── kubernetes/
│   └── ...
│
├── ai/              # Documentación de sistema AI/ML
│   ├── prompting/
│   ├── agents/
│   └── ...
│
└── .github/agents/  # Documentación de DEFINICIÓN de agentes
    ├── README.md
    ├── sdlc/
    ├── automation/
    └── ...
```

### Casos Específicos

#### Tests de Código Backend
```
CORRECTO: docs/backend/testing/
INCORRECTO: docs/agent/testing/

Razón: Los tests son de código Python backend (técnicas de prompting)
```

#### Tests de Código Frontend
```
CORRECTO: docs/frontend/testing/
INCORRECTO: docs/ui/testing/

Razón: Consistencia con estructura docs/backend/
```

#### Documentación de Agentes (Definiciones)
```
CORRECTO: .github/agents/
INCORRECTO: docs/agents/

Razón: Definiciones de agentes van en .github/ para CI/CD integration
```

#### Ejecuciones SDLC de Proyectos Backend
```
CORRECTO: docs/backend/SDLC_*.md
INCORRECTO: docs/agent/SDLC_*.md

Razón: El SDLC documenta desarrollo de código backend
```

---

## Lecciones Aprendidas

### LL-001: Verificar Estructura Antes de Crear Directorios

**Fecha**: 2025-11-14

**Problema**: Documentación SDLC creada en `docs/agent/` cuando debía estar en `docs/backend/`.

**Causa Raíz**: No verificar la estructura existente de `docs/` antes de crear nuevas carpetas.

**Impacto**:
- 8 archivos en ubicación incorrecta
- Referencias incorrectas en documentos
- Tiempo perdido en corrección

**Solución Aplicada**:
1. Mover todos los archivos a `docs/backend/`
2. Actualizar todas las referencias
3. Documentar convención

**Prevención Futura**:

**ANTES** de crear una nueva carpeta en `docs/`:

1. **Verificar estructura existente**:
   ```bash
   ls -la docs/
   ```

2. **Preguntarse**:
   - ¿Qué tipo de código documenta esto?
   - ¿Ya existe una carpeta para ese tipo?
   - ¿Dónde están documentos similares?

3. **Si hay duda, PREGUNTAR al usuario**:
   ```
   "Voy a crear documentación para X.
    ¿Debería ir en docs/backend/, docs/frontend/,
    u otra ubicación?"
   ```

4. **Verificar ejemplos existentes**:
   ```bash
   find docs/ -name "README.md" -o -name "*testing*"
   ```

**Regla**: Si no estás 100% seguro, pregunta antes de crear.

---

### LL-002: Nomenclatura sin Números

**Fecha**: 2025-11-14

**Problema**: Documentos creados con números prefijos (01_, 02_, etc.) cuando el proyecto no usa números.

**Causa Raíz**: Asumir convención de numeración sin verificar el proyecto.

**Solución**:
- Documentos renombrados sin números
- Usar nombres descriptivos: `planning_output.md` no `01_planning_output.md`

**Prevención**:
1. Verificar nomenclatura en carpeta destino primero
2. Usar nombres descriptivos, no secuenciales
3. Preguntar sobre convenciones si hay duda

---

## Checklist Pre-Documentación

Antes de crear documentación nueva, verificar:

- [ ] Revisé `docs/` para ver estructura existente
- [ ] Identifiqué el tipo de código (backend/frontend/infra)
- [ ] Verifiqué nomenclatura en carpeta destino
- [ ] Si hay duda, pregunté al usuario
- [ ] Confirmé que la ubicación es consistente con docs similares

---

## Mapeo Rápido: Código → Documentación

| Tipo de Código | Ubicación Código | Ubicación Docs |
|----------------|------------------|----------------|
| Backend Python | `api/`, `scripts/coding/` | `docs/backend/` |
| Frontend React | `ui/`, `frontend/` | `docs/frontend/` |
| Infrastructure | `infrastructure/`, `terraform/` | `docs/infrastructure/` |
| Tests Backend | `scripts/coding/ai/tests/` | `docs/backend/testing/` |
| Tests Frontend | `ui/tests/`, `frontend/tests/` | `docs/frontend/testing/` |
| Definiciones Agentes | N/A | `.github/agents/` |
| Sistema AI/Prompting | `scripts/coding/ai/agents/` | `docs/ai/`, `docs/ai/prompting/` |

---

## Preguntas Frecuentes

### P: ¿Dónde va documentación de tests TDD para código backend?
**R**: `docs/backend/testing/`

### P: ¿Dónde va documentación de definiciones de agentes?
**R**: `.github/agents/` (para definiciones) o `docs/ai/` (para sistema AI)

### P: ¿Dónde va un SDLC pipeline para desarrollo backend?
**R**: `docs/backend/` con subdirectorios por fase

### P: Si no estoy seguro, ¿qué hago?
**R**: **PREGUNTA** antes de crear. Mejor preguntar que corregir después.

---

## Commits de Referencia

- `162087c`: Move SDLC documentation from docs/agent to docs/backend (esta lección)
- `00a3a70`: Remove numbers from document names

---

## Actualizaciones de Este Documento

**2025-11-14**: Documento inicial
- LL-001: Verificar estructura antes de crear directorios
- LL-002: Nomenclatura sin números
- Convenciones de ubicación de documentación

---

**Nota**: Este documento es VIVO. Actualizar cuando se aprendan nuevas lecciones.

**Propósito**: Evitar errores repetidos y mantener consistencia en el proyecto.
