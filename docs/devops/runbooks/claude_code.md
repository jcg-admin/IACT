---
id: RUNBOOK-CLAUDE-CODE
estado: activo
propietario: equipo-devops
ultima_actualizacion: 2025-11-02
relacionados: ["DOC-DEVOPS-INDEX", "DOC-DEVOPS-CONTAINERS"]
---
# Runbook: Desarrollo con Claude Code

## Propósito

Documentar el uso de Claude Code como asistente de IA para desarrollo, incluyendo limitaciones conocidas del entorno y soluciones alternativas.

## ¿Qué es Claude Code?

Claude Code es la CLI oficial de Anthropic para Claude, que permite:

- 🤖 Asistencia de IA directamente desde la terminal
- 📝 Generación y modificación de código
- 🔍 Análisis de codebase
- 🛠️ Ejecución de tareas de desarrollo automatizadas
- 💬 Interacción conversacional para resolver problemas

## Limitaciones del Entorno

### Comando `gh` (GitHub CLI) No Disponible

**Problema:**
El entorno de ejecución de Claude Code tiene restricciones de red y permisos que impiden la instalación de GitHub CLI (`gh`).

**Errores típicos:**
```
El comando gh no está disponible en este entorno
```

**Razones técnicas:**
1. ❌ **Repositorios bloqueados**: Error 403 al descargar desde GitHub releases
2. ❌ **Problemas de permisos**: Sistema apt con errores en archivos temporales
3. ❌ **Red restringida**: Proxy/firewall bloquea acceso a recursos externos

**Intentos fallidos de instalación:**
```bash
# ❌ Desde repositorio oficial (403 Forbidden)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg

# ❌ Desde GitHub releases (403 Forbidden)
wget https://github.com/cli/cli/releases/download/v2.62.0/gh_2.62.0_linux_amd64.tar.gz

# ❌ Vía apt (errores de permisos)
apt install gh
```

## Alternativas y Soluciones

### 1. Usar `git` en Lugar de `gh` (Recomendado)

Para la mayoría de operaciones, `git` es suficiente:

**Crear Pull Request:**
```bash
# En lugar de: gh pr create --title "..." --body "..."
# Hacer:
git push -u origin nombre-rama
# Luego crear PR manualmente en GitHub web
```

**Ver estado de ramas:**
```bash
# En lugar de: gh pr list
# Hacer:
git branch -a
git status
```

**Commits y push:**
```bash
# Esto funciona normalmente
git add .
git commit -m "feat: nueva funcionalidad"
git push -u origin rama
```

### 2. Proporcionar Información Manualmente

Cuando Claude Code necesite información de GitHub:

**Issues:**
```
❌ No funciona: gh issue view 123

✅ Alternativa:
- Ir a https://github.com/2-Coatl/IACT---project/issues/123
- Copiar título y descripción
- Pegar en el chat con Claude Code
```

**Pull Requests:**
```
❌ No funciona: gh pr view 456

✅ Alternativa:
- Ir a https://github.com/2-Coatl/IACT---project/pull/456
- Copiar información relevante
- Proporcionarla a Claude Code
```

### 3. Instalar `gh` en DevContainer Local

Si ejecutas el proyecto localmente con DevContainer (VS Code), puedes agregar `gh` a la configuración.

**Modificar `.devcontainer/Dockerfile`:**

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    git \
    postgresql-client \
    mariadb-client \
    build-essential \
    libpq-dev \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
    dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
    tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# ... resto de la configuración
```

**O usar DevContainer Features:**

Modificar `.devcontainer/devcontainer.json`:
```json
{
  "name": "IACT Development",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    },
    "ghcr.io/devcontainers/features/github-cli:1": {
      "installDirectlyFromGitHubRelease": true,
      "version": "latest"
    },
    "ghcr.io/devcontainers/features/git:1": {
      "version": "latest"
    }
  }
}
```

**Reconstruir DevContainer:**
```bash
# Desde VS Code Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
# > Dev Containers: Rebuild Container
```

## Flujo de Trabajo con Claude Code

### 1. Desarrollo Normal

```bash
# Claude Code puede ayudar con:
- Análisis de código
- Generación de funciones
- Refactoring
- Escritura de tests
- Documentación
- Debugging
```

### 2. Trabajo con Git

```bash
# Crear rama
git checkout -b feature/nueva-funcionalidad

# Desarrollar con ayuda de Claude Code
# (análisis, generación de código, etc.)

# Commit
git add .
git commit -m "feat: agregar nueva funcionalidad"

# Push
git push -u origin feature/nueva-funcionalidad
```

### 3. Pull Requests

```bash
# Opción A: Crear PR manualmente desde GitHub web
# 1. Ir a https://github.com/2-Coatl/IACT---project
# 2. Click en "Pull requests" > "New pull request"
# 3. Seleccionar rama y crear PR

# Opción B: Si tienes gh instalado localmente
gh pr create --title "Nueva funcionalidad" --body "Descripción..."
```

## Mejores Prácticas

### 1. Comunicación Clara

Cuando Claude Code pregunte por información de GitHub:
- ✅ Proporcionar URLs directas
- ✅ Copiar/pegar contenido relevante
- ✅ Incluir números de issue/PR cuando sea relevante

### 2. Uso de Git

- ✅ Hacer commits frecuentes y descriptivos
- ✅ Usar ramas descriptivas: `feature/`, `fix/`, `docs/`
- ✅ Seguir convenciones de commit: `feat:`, `fix:`, `docs:`, etc.

### 3. Trabajo con Issues

**Formato recomendado para proporcionar issues:**
```
Issue #123: Implementar autenticación de usuarios

Descripción:
Necesitamos agregar un sistema de autenticación para...

Criterios de aceptación:
- [ ] Login con email/password
- [ ] Registro de nuevos usuarios
- [ ] Reset de contraseña
```

## Troubleshooting

### Error: "gh no está disponible"

**Solución:**
- ✅ Usar alternativas con `git` (ver sección "Alternativas")
- ✅ Proporcionar información manualmente
- ✅ Si trabajas localmente, agregar `gh` al devcontainer

### Claude Code no puede crear PR

**Solución:**
```bash
# Hacer push normalmente
git push -u origin nombre-rama

# Crear PR desde GitHub web
# https://github.com/2-Coatl/IACT---project/compare/main...nombre-rama
```

### Claude Code necesita info de un issue

**Solución:**
```bash
# Ir al issue en GitHub
# https://github.com/2-Coatl/IACT---project/issues/NUM

# Copiar título, descripción, comentarios relevantes
# Pegarlos en el chat con Claude Code
```

## Limitaciones Adicionales

### Red y Conectividad

El entorno de Claude Code puede tener:
- Proxy/firewall restrictivo
- Acceso limitado a servicios externos
- Restricciones en instalación de paquetes

### Permisos

- Archivos del sistema pueden tener permisos restringidos
- `sudo` puede tener configuración no estándar
- `/tmp` puede tener permisos especiales

### Recomendación

Para desarrollo local con todas las herramientas:
- ✅ Usar DevContainer en VS Code
- ✅ Instalar herramientas necesarias en el Dockerfile
- ✅ Configurar features en devcontainer.json

## Comparación: Claude Code vs Desarrollo Local

| Aspecto | Claude Code (remoto) | DevContainer (local) |
|---------|---------------------|---------------------|
| **GitHub CLI (gh)** | ❌ No disponible | ✅ Instalable |
| **Git** | ✅ Disponible | ✅ Disponible |
| **Instalación de paquetes** | ⚠️ Limitado | ✅ Completo |
| **Acceso a red** | ⚠️ Restringido | ✅ Completo |
| **Asistencia de IA** | ✅ Claude Code | ⚠️ Requiere configurar |

## Referencias

- [Claude Code Docs](https://docs.claude.com/en/docs/claude-code)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [DevContainers](../contenedores_devcontainer.md)
- [Git Documentation](https://git-scm.com/doc)

## Ejemplos Prácticos

### Escenario 1: Trabajar en un Issue

```bash
# 1. Usuario proporciona info del issue
# Issue #125: Fix login error

# 2. Claude Code analiza el código relevante
# (usa Read, Grep, etc.)

# 3. Claude Code genera fix
# (usa Edit, Write, etc.)

# 4. Commit y push
git add .
git commit -m "fix(auth): corregir error en login (#125)"
git push -u origin fix/login-error

# 5. Crear PR manualmente en GitHub
```

### Escenario 2: Revisar un PR

```bash
# 1. Usuario proporciona URL del PR
# https://github.com/2-Coatl/IACT---project/pull/456

# 2. Claude Code hace checkout
git fetch origin pull/456/head:pr-456
git checkout pr-456

# 3. Claude Code analiza cambios
git diff main...pr-456

# 4. Claude Code proporciona feedback
```

### Escenario 3: Crear Nueva Feature

```bash
# 1. Crear rama
git checkout -b feature/nueva-feature

# 2. Desarrollar con Claude Code
# (análisis, código, tests, docs)

# 3. Commit incremental
git add .
git commit -m "feat(feature): implementar primera parte"

# 4. Más desarrollo...
git commit -m "feat(feature): agregar tests"
git commit -m "docs(feature): actualizar documentación"

# 5. Push
git push -u origin feature/nueva-feature

# 6. Crear PR en GitHub web
# Title: Implementar nueva feature
# Body: [descripción detallada]
```

## Changelog

- **2025-11-02**: Creación inicial
  - Documentar limitación de `gh` en Claude Code
  - Agregar alternativas y soluciones
  - Incluir configuración para DevContainer local
