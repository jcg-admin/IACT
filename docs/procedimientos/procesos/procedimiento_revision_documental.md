---
id: PROC-REV-DOC
tipo: procedimiento
categoria: qa
version: 1.0.0
fecha_creacion: 2025-11-04
propietario: equipo-qa
relacionados: ["PROC-CAMBIOS", "PROC-QA"]
---
# Procedimiento: Revisión Documental

## Propósito

Definir el proceso para revisar y aprobar cambios en la documentación del proyecto.

## Alcance

Aplica a toda la documentación en `docs/` y README files del proyecto.

## Tipos de Cambios Documentales

### Cambios Menores (Fast-track)
- Corrección de typos
- Formato (markdown, indentación)
- Links rotos
- Actualizaciones de fechas

**Proceso**: Self-review y merge directo

### Cambios Mayores (Review requerido)
- Nueva sección o documento
- Reestructuración
- Cambios de contenido significativos
- Actualización de procedimientos

**Proceso**: PR con review de QA documental

### Cambios Críticos (Review extendido)
- ADRs (Architecture Decision Records)
- Cambios de procesos establecidos
- Documentación de compliance/seguridad

**Proceso**: PR con reviews múltiples + aprobación de arquitectura

## Procedimiento de Revisión

### 1. Preparación del Cambio

#### 1.1 Crear Branch

```bash
git checkout main
git pull origin main
git checkout -b docs/actualizar-procedimiento-qa-20251104
```

#### 1.2 Hacer Cambios

- [ ] Seguir [Estándares de Documentación](../gobernanza/documentacion_corporativa.md)
- [ ] Mantener formato markdown consistente
- [ ] Actualizar front matter (YAML)
  ```yaml
  ---
  id: DOC-PROC-QA
  estado: draft  # draft, review, approved, active, deprecated
  propietario: equipo-qa
  ultima_actualizacion: 2025-11-04
  relacionados: ["DOC-PROC-DEV"]
  ---
  ```

#### 1.3 Verificar Localmente

```bash
# Si usa MkDocs (futuro)
mkdocs serve

# Verificar links
find docs -name "*.md" -exec grep -l "](.*)" {} \; | \
  xargs -I {} bash -c 'echo "Checking {}"; grep -o "](.*)" {}'

# Spell check (opcional)
aspell check docs/procedimientos/procesos/procedimiento_qa.md
```

### 2. Checklist de Auto-Revisión

Ver: [Checklist de Cambios Documentales](../checklists/checklist_cambios_documentales.md)

#### Contenido

- [ ] Propósito claro del documento
- [ ] Alcance definido
- [ ] Audiencia identificada
- [ ] Estructura lógica
- [ ] Ejemplos claros (si aplica)
- [ ] Sin ambigüedades

#### Formato

- [ ] Markdown válido
- [ ] Títulos jerárquicos (# ## ###)
- [ ] Code blocks con lenguaje especificado
- [ ] Links válidos (internos y externos)
- [ ] Imágenes con alt text
- [ ] Tablas bien formateadas

#### Metadata

- [ ] Front matter completo
- [ ] ID único
- [ ] Estado correcto
- [ ] Propietario asignado
- [ ] Fecha actualizada
- [ ] Referencias cruzadas

#### Calidad

- [ ] Sin typos evidentes
- [ ] Lenguaje claro y conciso
- [ ] Terminología consistente
- [ ] Tono profesional
- [ ] Español correcto

### 3. Crear Pull Request

```bash
# Commit
git add .
git commit -m "docs: actualizar procedimiento de QA

- Agregar sección de tests de integración
- Actualizar checklist de revisión
- Corregir typos en ejemplos"

# Push
git push -u origin docs/actualizar-procedimiento-qa-20251104

# PR
gh pr create \
  --title "docs: Actualizar procedimiento de QA" \
  --body "$(cat <<EOF
## Tipo de Cambio
- [x] Mayor (requiere review)

## Summary
- Agrega sección de tests de integración
- Actualiza checklist con nuevos items
- Corrige ejemplos de código

## Impacto
- **Quién lo usa**: Equipo QA, desarrolladores
- **Breaking changes**: No
- **Documentos relacionados**: procedimiento_desarrollo_local.md

## Checklist
- [x] Front matter actualizado
- [x] Links verificados
- [x] Formato markdown correcto
- [x] Auto-revisión completada

## Screenshots (si aplica)
N/A
EOF
)" \
  --label "documentation" \
  --reviewer equipo-qa
```

### 4. Review

#### 4.1 Como Reviewer

Verificar:

**Contenido:**
- [ ] Información precisa y actualizada
- [ ] Completo (no falta info importante)
- [ ] Ejemplos correctos y funcionan
- [ ] Procedimientos probables de seguir

**Estructura:**
- [ ] Organización lógica
- [ ] Navegación clara
- [ ] Índices/ToC actualizados
- [ ] Referencias cruzadas correctas

**Estilo:**
- [ ] Sigue guía de estilo del proyecto
- [ ] Lenguaje claro y accesible
- [ ] Sin jerga innecesaria
- [ ] Consistente con otros docs

**Técnico:**
- [ ] Comandos son válidos
- [ ] Paths son correctos
- [ ] Variables de entorno documentadas
- [ ] Configuraciones actualizadas

#### 4.2 Dejar Feedback

```markdown
# Comentarios de revisión

**Contenido**
- ✅ La nueva sección de tests de integración es clara
- ⚠️ Falta mencionar timeout de tests
- ❌ El comando en línea 45 tiene un typo

**Formato**
- ✅ Markdown correcto
- ⚠️ Considerar agregar diagrama de flujo

**Sugerencias**
- Agregar ejemplo de pytest con fixtures
- Link al procedimiento de desarrollo local
```

### 5. Aprobar y Merge

```bash
# Si cambios menores
gh pr merge --squash --delete-branch

# Si cambios mayores, esperar aprobaciones necesarias
# Luego
gh pr merge --squash --delete-branch
```

### 6. Post-Merge

- [ ] Verificar que doc se ve bien en repo
- [ ] Actualizar índices si es necesario
- [ ] Notificar a equipo si el cambio les afecta
- [ ] Actualizar MkDocs site (futuro)

## ADRs (Architecture Decision Records)

Requieren proceso especial:

### Crear ADR

```bash
# Usar plantilla
cp docs/arquitectura/adr/plantilla_adr.md \
   docs/arquitectura/adr/adr_2025_002_nombre_decision.md

# Completar todas las secciones
# Status: Proposed
```

### Review de ADR

- [ ] Contexto bien explicado
- [ ] Opciones consideradas documentadas
- [ ] Pros/cons analizados objetivamente
- [ ] Decisión justificada
- [ ] Consecuencias identificadas
- [ ] Stakeholders consultados

### Aprobar ADR

Requiere:
- Review de arquitectura
- Review de equipo afectado
- Sign-off de tech lead

```bash
# Una vez aprobado, actualizar status
# Status: Accepted
# Decision Date: 2025-11-04
```

## Métricas de Documentación

Medir:
- Docs obsoletos: < 10%
- PRs de docs pendientes: < 5
- Tiempo de review: < 24 horas
- Cobertura de features: > 90%

## Herramientas

- **markdownlint**: Validar formato
- **markdown-link-check**: Verificar links
- **aspell**: Spell checking
- **MkDocs**: Site generation (futuro)

## Recursos Relacionados

- [Documentación Corporativa](../gobernanza/documentacion_corporativa.md)
- [Checklist de Cambios Documentales](../checklists/checklist_cambios_documentales.md)
- [Plantilla de ADR](../arquitectura/adr/plantilla_adr.md)

## Changelog

- 2025-11-04: Creación inicial del procedimiento
