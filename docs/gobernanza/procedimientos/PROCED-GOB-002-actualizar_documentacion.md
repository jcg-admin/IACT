---
id: PROCED-GOB-002
tipo: procedimiento
categoria: gobernanza
subcategoria: documentacion
version: 1.0.0
fecha_creacion: 2025-11-17
autor: Claude Code (Sonnet 4.5)
estado: activo
relacionados: ["PROC-GOB-001", "GUIA-GOB-002", "PROCED-GOB-001"]
---

# PROCED-GOB-002: Actualizar Documentación

## Objetivo

Establecer proceso claro para mantener la documentación del proyecto IACT actualizada, precisa y útil.

## Alcance

Este procedimiento cubre:
- Actualización de documentación existente
- Identificación de docs que requieren actualización
- Proceso de revisión y aprobación
- Versionado de documentación

NO cubre:
- Creación de documentación nueva desde cero
- Creación de ADRs (ver PROCED-GOB-001)
- Documentación de código (docstrings)

## Pre-requisitos

- Acceso al repositorio de documentación
- Conocimiento del tema a documentar
- Revisión de guía de estilo de documentación

## Roles y Responsabilidades

- **Developer**: Actualiza docs técnicas de su área
- **Tech Lead**: Revisa y aprueba cambios significativos
- **Documentation Owner**: Mantiene índices y estructura general

## Procedimiento Detallado

### PASO 1: Identificar Necesidad de Actualización

#### 1.1 Triggers para actualización

La documentación debe actualizarse cuando:

- ✅ **Cambio de código**: Implementación difiere de docs
- ✅ **Nueva funcionalidad**: Feature agregada no documentada
- ✅ **Deprecación**: Funcionalidad obsoleta documentada
- ✅ **Error encontrado**: Información incorrecta en docs
- ✅ **Feedback de usuario**: Docs confusas o incompletas
- ✅ **Decisión arquitectónica**: ADR aprobada requiere update
- ✅ **Cambio de proceso**: Workflow modificado

---

#### 1.2 Audit periódico

Realizar audit trimestral:

```bash
# Listar docs modificadas hace > 6 meses
find docs/ -name "*.md" -mtime +180

# Revisar cada una y determinar si requiere update
```

---

### PASO 2: Categorizar el Cambio

#### 2.1 Clasificar severidad

| Tipo | Descripción | Acción Requerida |
|------|-------------|------------------|
| **CRÍTICO** | Información incorrecta que puede causar errores | Actualizar inmediatamente |
| **MAYOR** | Funcionalidad significativa no documentada | Actualizar en < 1 semana |
| **MENOR** | Mejoras de claridad, typos, formato | Actualizar en próximo sprint |
| **COSMÉTICO** | Estilo, organización | Actualizar cuando sea conveniente |

---

### PASO 3: Crear Branch para Actualización

```bash
# Crear branch específico
git checkout -b docs/update-auth-guide

# O si es parte de feature
git checkout -b feature/jwt-auth  # Incluye docs en mismo branch
```

**Nomenclatura**:
- Cambios solo docs: `docs/descripcion-del-cambio`
- Docs + código: `feature/descripcion-funcionalidad`

---

### PASO 4: Actualizar el Documento

#### 4.1 Abrir documento a actualizar

```bash
# Encontrar documento
find docs/ -name "*autenticacion*"

# Abrir en editor
code docs/guias/GUIA-BACK-003-authentication-guide.md
```

---

#### 4.2 Actualizar contenido

##### Ejemplos de Cambios Comunes:

**A. Actualizar comando/código**

**ANTES**:
```markdown
## Login

Para autenticar usuario:

```python
response = requests.post('/api/login', {
    'username': 'user',
    'password': 'pass'
})
token = response.json()['token']
```
```

**DESPUÉS**:
```markdown
## Login

Para autenticar usuario:

```python
response = requests.post('/api/auth/login', {  # ← Endpoint actualizado
    'username': 'user',
    'password': 'pass'
})
# ← Nueva estructura de respuesta
data = response.json()
access_token = data['access_token']
refresh_token = data['refresh_token']
```

**Nota**: Desde v1.2.0, el sistema usa JWT con refresh tokens.
Ver [ADR-BACK-006](../adr/ADR-BACK-006-django-orm-vs-sqlalchemy.md).
```

---

**B. Agregar nueva sección**

```markdown
## Refresh Token

Cuando el access token expira (15 minutos), usar el refresh token:

```bash
curl -X POST https://api.iact-project.com/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

Response:
```json
{
  "access_token": "new_access_token_here",
  "expires_in": 900
}
```

**Nota**: Refresh tokens expiran a los 7 días.
```

---

**C. Marcar como obsoleto**

```markdown
## ~~Login con Basic Auth~~ (OBSOLETO)

> ⚠️ **OBSOLETO desde v1.2.0**
>
> Basic Auth fue reemplazado por JWT authentication.
> Ver sección [Login con JWT](#login-con-jwt).
>
> Esta sección se mantendrá hasta v2.0.0 para referencia histórica.

```bash
# NO USAR - Solo para referencia
curl -u username:password https://api.iact-project.com/api/users
```
```

---

#### 4.3 Actualizar metadata del documento

**Actualizar frontmatter**:

```markdown
---
id: GUIA-BACK-003
tipo: guia
categoria: backend
subcategoria: authentication
version: 2.0.0  # ← Incrementar versión
fecha_creacion: 2025-10-15
ultima_actualizacion: 2025-11-17  # ← Agregar/actualizar
autor: Original Author
contribuidores:
  - Tu Nombre (2025-11-17)  # ← Agregar tu nombre
estado: activo
relacionados: ["ADR-BACK-006", "PROC-DEV-001"]  # ← Actualizar relaciones
---
```

**Reglas de versionado (Semantic Versioning)**:

- `MAJOR` (X.0.0): Cambios que rompen compatibilidad o restructuración completa
- `MINOR` (1.X.0): Agregar nueva sección significativa
- `PATCH` (1.0.X): Correcciones, aclaraciones, typos

---

#### 4.4 Agregar sección de changelog (si no existe)

Al final del documento:

```markdown
---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 2.0.0 | 2025-11-17 | Tu Nombre | Actualizado a JWT authentication |
| 1.1.0 | 2025-11-01 | Otro Dev | Agregada sección de error handling |
| 1.0.0 | 2025-10-15 | Original | Versión inicial |
```

---

### PASO 5: Verificar Calidad

#### 5.1 Checklist de calidad

- [ ] **Precisión**: Información correcta y actualizada
- [ ] **Completitud**: No faltan pasos críticos
- [ ] **Claridad**: Lenguaje claro y conciso
- [ ] **Ejemplos**: Código de ejemplo funcional y actualizado
- [ ] **Links**: Todos los links internos/externos funcionan
- [ ] **Formato**: Markdown válido, sintaxis correcta
- [ ] **Consistencia**: Sigue estilo del resto de docs

---

#### 5.2 Validar ejemplos de código

Si hay código de ejemplo, ejecutarlo:

```bash
# Python
python -m doctest docs/guias/GUIA-BACK-003-authentication-guide.md

# O manualmente copiar y ejecutar ejemplos
```

---

#### 5.3 Validar links

```bash
# Herramienta para verificar links rotos
npx markdown-link-check docs/guias/GUIA-BACK-003-authentication-guide.md

# O manualmente verificar cada link
```

---

#### 5.4 Verificar formato Markdown

```bash
# Linter de Markdown
npx markdownlint docs/guias/GUIA-BACK-003-authentication-guide.md

# Corregir issues reportados
```

---

### PASO 6: Actualizar Referencias Cruzadas

#### 6.1 Buscar documentos que referencian el actualizado

```bash
# Buscar referencias al doc actualizado
grep -r "GUIA-BACK-003" docs/

# O buscar por nombre del archivo
grep -r "authentication-guide" docs/
```

---

#### 6.2 Actualizar documentos relacionados

Si otros docs referencian contenido que cambió, actualizarlos también.

**Ejemplo**:

Si `README.md` dice:

```markdown
Para autenticación ver [Guía de Auth](docs/guias/GUIA-BACK-003-authentication-guide.md#basic-auth)
```

Actualizar a:

```markdown
Para autenticación ver [Guía de Auth](docs/guias/GUIA-BACK-003-authentication-guide.md#login-con-jwt)
```

---

### PASO 7: Commit y PR

#### 7.1 Commit con mensaje descriptivo

```bash
# Stage cambios
git add docs/guias/GUIA-BACK-003-authentication-guide.md

# Commit
git commit -m "$(cat <<'EOF'
docs(auth): actualizar guía a JWT authentication

Cambios principales:
- Reemplazar ejemplos de Basic Auth con JWT
- Agregar sección de Refresh Tokens
- Marcar Basic Auth como obsoleto
- Actualizar todos los ejemplos de código
- Agregar referencia a ADR-BACK-006

Versión: 1.2.0 -> 2.0.0

Relacionado: ADR-BACK-006, TASK-089
EOF
)"
```

---

#### 7.2 Crear Pull Request

```bash
# Push
git push -u origin docs/update-auth-guide

# Crear PR (usando gh cli)
gh pr create --title "docs(auth): actualizar guía a JWT authentication" \
  --body "$(cat <<'EOF'
## Resumen

Actualizar documentación de autenticación para reflejar migración a JWT.

## Cambios

- ✅ Actualizado endpoint de `/api/login` a `/api/auth/login`
- ✅ Agregada sección de Refresh Tokens
- ✅ Marcado Basic Auth como obsoleto
- ✅ Todos los ejemplos de código actualizados y probados
- ✅ Links verificados

## Checklist

- [x] Información técnicamente precisa
- [x] Ejemplos de código probados
- [x] Links validados
- [x] Markdown lint passing
- [x] Versionado actualizado
- [x] Changelog agregado
- [x] Documentos relacionados actualizados

## Relacionado

- Implementa: ADR-BACK-006-django-orm-vs-sqlalchemy
- Cierra: TASK-089
EOF
)"
```

---

### PASO 8: Revisión y Merge

#### 8.1 Self-review

Antes de solicitar review, hacer self-review:

```bash
# Ver diff final
git diff main...docs/update-auth-guide
```

Verificar:
- No hay typos
- Formato consistente
- Links funcionan
- Código de ejemplo correcto

---

#### 8.2 Solicitar review

Asignar reviewers:
- **Mínimo**: 1 tech lead o documentation owner
- **Recomendado**: 1 person del área técnica afectada

---

#### 8.3 Incorporar feedback

Si reviewers solicitan cambios:

```bash
# Hacer cambios solicitados
vim docs/guias/GUIA-BACK-003-authentication-guide.md

# Commit adicional
git add docs/guias/GUIA-BACK-003-authentication-guide.md
git commit -m "docs(auth): incorporar feedback de review

- Aclarar sección de token expiration
- Agregar diagrama de flujo JWT
- Corregir typo en ejemplo de curl"

git push
```

---

#### 8.4 Merge

Una vez aprobado:

```bash
# Squash merge (recomendado para docs)
gh pr merge --squash --delete-branch
```

---

### PASO 9: Publicación

#### 9.1 Verificar en entorno publicado

Si docs están en GitHub Pages, Read the Docs, etc.:

```bash
# Esperar a que CI/CD publique (usualmente < 5 minutos)

# Verificar URL publicada
open https://docs.iact-project.com/guias/GUIA-BACK-003-authentication-guide
```

---

#### 9.2 Notificar al equipo

Mensaje en canal de equipo:

```
📚 Documentación actualizada: Authentication Guide

Cambios principales:
- Migrado de Basic Auth a JWT
- Agregada guía de Refresh Tokens
- Todos los ejemplos actualizados

Link: https://docs.iact-project.com/guias/GUIA-BACK-003-authentication-guide

Please review y reportar cualquier issue.
```

---

## Mejores Prácticas

### DO ✅

1. **Actualizar docs en mismo PR que código**
   - Cambio de código + update de docs = 1 PR
   - Mantiene docs sincronizados

2. **Usar ejemplos ejecutables**
   - Código que realmente funciona
   - Testeado antes de documentar

3. **Ser específico**
   - "Ejecutar `npm test`" mejor que "correr tests"
   - Incluir outputs esperados

4. **Mantener histórico**
   - No borrar secciones obsoletas, marcarlas como tal
   - Mantener changelog

5. **Links relativos**
   - `[ADR](../adr/ADR-BACK-001.md)` no `[ADR](https://github.com/...)`
   - Funciona en cualquier entorno

### DON'T ❌

1. **Dejar docs desactualizados**
   - Docs incorrectos peores que no docs

2. **Hacer cambios sin versionar**
   - Siempre actualizar versión y fecha

3. **Olvidar links cruzados**
   - Actualizar referencias en otros docs

4. **Documentar "en el futuro"**
   - Solo documentar lo que YA existe

5. **Asumir conocimiento previo excesivo**
   - Explicar desde nivel apropiado para audiencia

---

## Plantilla de Actualización

```markdown
---
id: [ID-EXISTENTE]
version: [INCREMENTAR-VERSION]
ultima_actualizacion: [FECHA-HOY]
contribuidores:
  - [TU-NOMBRE] ([FECHA])
---

# [Título Existente]

> 📝 **Última actualización**: [FECHA] - [Resumen breve del cambio]

[CONTENIDO ACTUALIZADO]

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| [NUEVA] | [HOY] | [TU] | [CAMBIOS] |
| [PREV]  | [FECHA] | [AUTOR] | [CAMBIOS ANTERIORES] |
```

---

## Problemas Comunes y Soluciones

### Problema 1: No sé qué versión usar

**Solución**: Aplicar Semantic Versioning

- Typo fix → PATCH (1.0.0 → 1.0.1)
- Nueva sección → MINOR (1.0.0 → 1.1.0)
- Restructuración completa → MAJOR (1.0.0 → 2.0.0)

---

### Problema 2: Links rotos después de renombrar archivos

**Solución**: Buscar y reemplazar

```bash
# Encontrar todos los refs al archivo viejo
grep -r "old-filename.md" docs/

# Actualizar cada uno manualmente o con sed
find docs/ -name "*.md" -exec sed -i 's/old-filename.md/new-filename.md/g' {} +
```

---

### Problema 3: Conflictos de merge en docs

**Solución**: Usualmente aceptar AMBOS

Docs rara vez tienen conflictos lógicos. Si dos personas agregaron secciones diferentes, combinar ambas.

---

## Métricas de Calidad de Documentación

Monitorear:
- **Freshness**: % de docs actualizadas en últimos 6 meses
- **Accuracy**: # de issues reportados por docs incorrectos
- **Coverage**: % de funcionalidades documentadas
- **Usability**: Feedback de usuarios (surveys)

**Targets**:
- Freshness: >= 80%
- Accuracy issues: < 5/mes
- Coverage: >= 90%

---

## Referencias

- [PROC-GOB-001: Mapeo de Procesos y Templates](../procesos/PROC-GOB-001-mapeo_procesos_templates.md)
- [GUIA-GOB-002: Convenciones de Nomenclatura](../guias/GUIA-GOB-002-convenciones_nomenclatura.md)
- [PROCED-GOB-001: Crear ADR](PROCED-GOB-001-crear_adr.md)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)

## Historial de Cambios

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0.0 | 2025-11-17 | Claude Code | Versión inicial |

## Aprobación

- **Autor**: Claude Code (Sonnet 4.5)
- **Revisado por**: Pendiente
- **Aprobado por**: Pendiente
- **Fecha de próxima revisión**: 2026-02-17
