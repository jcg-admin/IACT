# Scripts de Metricas y Reporting

Documentacion de scripts para calcular metricas DORA y generar reportes.

## dora_metrics.py

**Path:** `/home/user/IACT---project/scripts/dora_metrics.py`

**Proposito:** Calcular las 4 metricas DORA usando GitHub API.

### Metricas DORA

1. **Deployment Frequency**: Deployments por dia
2. **Lead Time for Changes**: Tiempo desde commit hasta production
3. **Change Failure Rate**: % de deployments que causan incidentes
4. **Mean Time to Recovery (MTTR)**: Tiempo promedio de recuperacion

### Uso Basico

```bash
# Ultimos 30 dias (default)
python scripts/dora_metrics.py --repo 2-Coatl/IACT---project

# Periodo especifico
python scripts/dora_metrics.py \
  --repo 2-Coatl/IACT---project \
  --start 2025-01-01 \
  --end 2025-01-31

# Output en JSON
python scripts/dora_metrics.py --repo 2-Coatl/IACT---project --format json

# Output en Markdown
python scripts/dora_metrics.py --repo 2-Coatl/IACT---project --format markdown > report.md

# Solo metricas de documentacion
python scripts/dora_metrics.py --docs-only
```

### Output Esperado

```
================================================================================
DORA METRICS REPORT
================================================================================

Repositorio: 2-Coatl/IACT---project
Periodo: 2025-10-01 → 2025-11-07
Duracion: 37 dias

Metrica                           Valor    Clasificacion
--------------------------------------------------------------------------------
Deployment Frequency              2.5 deployments/day    [ELITE] Elite
Lead Time For Changes             4.2 hours              [ELITE] Elite
Change Failure Rate               8.0 %                  [ELITE] Elite
Mean Time To Recovery             0.8 hours              [ELITE] Elite

--------------------------------------------------------------------------------
Clasificacion General: Elite
================================================================================
```

### Clasificacion DORA

| Metrica | Elite | High | Medium | Low |
|---------|-------|------|--------|-----|
| Deployment Frequency | >= 1/dia | >= 1/semana | >= 1/mes | < 1/mes |
| Lead Time | <= 1 dia | <= 1 semana | <= 1 mes | > 1 mes |
| Change Failure Rate | <= 15% | <= 30% | <= 45% | > 45% |
| MTTR | <= 1 hora | <= 1 dia | <= 1 semana | > 1 semana |

### Prerequisitos

```bash
# GitHub token requerido
export GITHUB_TOKEN="ghp_..."

# O pasar como parametro
python scripts/dora_metrics.py --github-token "ghp_..." --repo 2-Coatl/IACT---project
```

### Metricas de Documentacion

```bash
# Solo calcular metricas de documentacion (no requiere GITHUB_TOKEN)
python scripts/dora_metrics.py --docs-only
```

Output:
```
================================================================================
DOCUMENTATION METRICS REPORT
================================================================================

Coverage: 68% (100/147 guias)

Por categoria:
  - onboarding: 20 guias
  - workflows: 15 guias
  - testing: 12 guias
  - deployment: 10 guias
  - troubleshooting: 8 guias

Onboarding time: 160 min (target: 30 min)
Status: Needs optimization
================================================================================
```

---

## generate_dora_report.sh

**Path:** `/home/user/IACT---project/scripts/generate_dora_report.sh`

**Proposito:** Generar reporte HTML de DORA metrics.

**Uso:**
```bash
./scripts/generate_dora_report.sh
```

**Output:** `dora_report_YYYYMMDD_HHMMSS.html`

---

## Integration con SDLC

Los agentes SDLC registran timestamps en artefactos:

```markdown
---
generated_at: 2025-11-07T10:30:00Z
phase: planning
feature_id: TASK-123
---
```

Esto permite calcular:
- Lead time desde planning hasta deployment
- Tiempo en cada fase SDLC
- Blockers y delays

---

## Mejores Practicas

1. **Ejecutar weekly:**
   ```bash
   python scripts/dora_metrics.py --repo 2-Coatl/IACT---project --format markdown > reports/dora_weekly_$(date +%Y%m%d).md
   ```

2. **Track tendencias:**
   - Comparar metricas mes a mes
   - Identificar mejoras o degradaciones
   - Actuar sobre metricas Low/Medium

3. **Metas del proyecto:**
   - Target: Elite en todas las metricas
   - Current: (verificar con script)

---

**Mantenedores:** @devops-lead, @tech-lead
