# Instrucciones para Crear el Pull Request

## Opcion 1: GitHub Web UI (Recomendado)

### Paso 1: Ir a GitHub

Visita la pagina del repositorio en GitHub y navega a:

**URL del PR:**
```
https://github.com/2-Coatl/IACT---project/compare/develop...claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh
```

### Paso 2: Crear Pull Request

1. Haz click en el boton verde "Create pull request"
2. Titulo: `feat: Completar proyecto IACT - 38/38 tareas (184 SP) + Analisis guias workflows`
3. Copia y pega el contenido de `PR_DESCRIPTION.md` en la descripcion
4. Haz click en "Create pull request"

## Opcion 2: GitHub CLI (Si esta configurado)

```bash
# Desde el directorio del proyecto
gh pr create \
  --base develop \
  --head claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh \
  --title "feat: Completar proyecto IACT - 38/38 tareas (184 SP) + Analisis guias workflows" \
  --body-file PR_DESCRIPTION.md
```

## Opcion 3: Git Push con Flag

```bash
# Crear PR automaticamente al hacer push
git push -u origin claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh \
  --set-upstream \
  --force-with-lease
```

Luego visita la URL que GitHub muestra en la consola para completar el PR.

## Informacion del PR

**Branch origen:** claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh
**Branch destino:** develop
**Commits:** 611 commits totales
**Archivos cambiados:** ~150+ archivos
**Lineas agregadas:** ~50,000+

## Links Directos

### Link del Comparison (para crear PR):
```
https://github.com/2-Coatl/IACT---project/compare/develop...claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh
```

### Link del Branch:
```
https://github.com/2-Coatl/IACT---project/tree/claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh
```

### Link de Commits:
```
https://github.com/2-Coatl/IACT---project/commits/claude/analiza-do-011CUreJt9Sfhy9C1CeExCkh
```

## Reviewers Sugeridos

Basado en CODEOWNERS:

- @arquitecto-senior
- @tech-lead
- @devops-lead
- @qa-lead
- @product-owner
- @security-lead

## Labels Sugeridos

- `feature`
- `documentation`
- `dora-metrics`
- `production-ready`
- `sprint-complete`

## Milestone

- Sprint 4 - Final
- Q4 2025

## Descripcion del PR

El contenido completo de la descripcion esta en: `PR_DESCRIPTION.md`

Copiar todo el contenido de ese archivo en la descripcion del PR.

---

Una vez creado el PR, el link sera algo como:

```
https://github.com/2-Coatl/IACT---project/pull/XXX
```

Donde XXX sera el numero del PR asignado por GitHub.
