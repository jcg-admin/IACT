---
id: ONBOARDING-GUIDE
tipo: guia
categoria: proyecto
fecha: 2025-11-07
version: 1.0.0
propietario: tech-lead
relacionados: ["README.md", "docs/gobernanza/ai/AI_STANCE.md", "docs/proyecto/ROADMAP.md"]
---

# Guia de Onboarding - Proyecto IACT

Bienvenido al proyecto IACT. Esta guia te ayudara a configurar tu entorno, entender la estructura del proyecto y comenzar a contribuir efectivamente.

---

## 1. Configuracion Inicial

### 1.1 Requisitos Previos

```bash
# Verificar versiones
python --version    # >= 3.11
node --version      # >= 18.0
git --version       # >= 2.40
```

### 1.2 Clonar Repositorio

```bash
git clone <repository-url>
cd IACT---project
```

### 1.3 Configurar Entorno Python

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r api/callcentersite/requirements.txt

# Instalar pre-commit hooks
pip install pre-commit
pre-commit install
```

### 1.4 Configurar Entorno Django

```bash
cd api/callcentersite

# Copiar settings de desarrollo
cp callcentersite/settings/development.py.example callcentersite/settings/development.py

# Ejecutar migraciones
python manage.py migrate

# Crear superuser
python manage.py createsuperuser

# Ejecutar tests
pytest

# Iniciar servidor desarrollo
python manage.py runserver
```

---

## 2. Estructura del Proyecto

### 2.1 Organizacion General

```
IACT---project/
├── api/                    Backend Django
├── docs/                   Documentacion transversal
├── scripts/                Scripts automatizacion
├── .github/                CI/CD workflows
└── implementacion/         Codigo + Requisitos
```

Ver `docs/README.md` para estructura detallada.

### 2.2 Directorios Clave

| Directorio | Proposito |
|------------|-----------|
| `api/callcentersite/` | Backend Django (monolito modular) |
| `docs/adr/` | Architecture Decision Records |
| `docs/gobernanza/` | Gobernanza, procesos, estandares |
| `scripts/logging/` | Scripts Cassandra logging (centralized) |
| `.github/workflows/` | CI/CD automatizacion |

---

## 3. AI Guidelines y DORA 2025

### 3.1 AI Stance del Proyecto

Este proyecto adopta una **AI Stance proactiva** segun DORA 2025:

**[OK] AI-Enabled Development:**
- Uso intensivo de AI assistants (Claude, GitHub Copilot)
- AI Code Review antes de human review
- AI-generated documentation (auto-sync)
- AI-powered testing (generacion casos de prueba)

**[OK] AI-Accessible Data:**
- Logs centralizados en Cassandra (AI-queryable)
- Metrics DORA expuestos via API
- Documentacion en formato estructurado (YAML frontmatter)

**Ver**: `docs/gobernanza/ai/AI_STANCE.md` para detalles completos.

### 3.2 Uso de AI Assistants

#### Claude Code (Recomendado)

```bash
# Instalar Claude CLI
npm install -g @anthropic-ai/claude-cli

# Configurar API key
export ANTHROPIC_API_KEY=<your-key>

# Uso basico
claude "Explicame la arquitectura de analytics app"
claude "Genera tests para el servicio AuditService"
claude "Documenta el endpoint /api/dashboard/widgets"
```

#### GitHub Copilot

```bash
# Activar en tu IDE (VS Code, PyCharm, etc.)
# Settings -> Extensions -> GitHub Copilot

# Uso:
# 1. Escribir comentario describiendo funcion
# 2. Copilot sugiere implementacion
# 3. Aceptar (Tab) o rechazar (Esc)
```

### 3.3 Lineamientos AI

1. **Code Review AI-First**:
   - Antes de crear PR, ejecuta AI code review
   - AI identifica bugs, security issues, code smells
   - Corregir issues antes de human review

2. **Documentation AI-Generated**:
   - Comentarios de codigo: AI genera docstrings
   - READMEs: AI genera estructura base
   - Diagramas: AI genera PlantUML desde codigo

3. **Testing AI-Powered**:
   - AI genera casos de prueba desde requisitos
   - AI genera fixtures desde modelos Django
   - AI sugiere edge cases

4. **Limitaciones AI** (Critical Thinking Required):
   - NO confiar ciegamente en AI para logica critica de negocio
   - Validar AI output manualmente
   - AI es asistente, NO reemplaza pensamiento critico
   - Decisiones arquitecturales requieren human expertise

---

## 4. Workflow de Desarrollo

### 4.1 Feature Development (TDD + AI)

```bash
# 1. Crear branch desde main
git checkout -b feature/analytics-export

# 2. Escribir tests PRIMERO (TDD)
# AI asiste: "Claude, genera tests para exportar analytics a CSV"
# Archivo: api/callcentersite/tests/test_analytics_export.py

# 3. Implementar feature
# AI asiste: "GitHub Copilot sugiere implementacion"

# 4. Ejecutar tests
pytest api/callcentersite/tests/test_analytics_export.py

# 5. AI Code Review
claude "Revisa mi codigo en analytics_export.py, identifica bugs y mejoras"

# 6. Corregir issues AI

# 7. Pre-commit hooks (automatico)
git add .
git commit -m "feat(analytics): exportar analytics a CSV"
# Pre-commit ejecuta: black, flake8, bandit, tests

# 8. Push
git push -u origin feature/analytics-export

# 9. Create PR
gh pr create --title "feat(analytics): exportar analytics a CSV" --body "..."

# 10. Human Review + Merge
```

### 4.2 Conventional Commits

Formato: `<type>(<scope>): <description>`

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Bug fix
- `docs`: Documentacion
- `refactor`: Refactorizacion
- `test`: Tests
- `chore`: Mantenimiento

Ejemplos:
```bash
git commit -m "feat(analytics): exportar analytics a CSV"
git commit -m "fix(auth): corregir validacion de password"
git commit -m "docs(api): documentar endpoint /dashboard/widgets"
git commit -m "refactor(etl): simplificar transformers"
```

---

## 5. DORA Metrics y Observability

### 5.1 3 Capas de Observabilidad

| Capa | Que Mide | Herramienta |
|------|----------|-------------|
| Capa 1: DORA Metrics | Proceso desarrollo (Lead Time, CFR, MTTR) | `scripts/dora_metrics.py` |
| Capa 2: Application Logs | Runtime Django (errores, requests) | Cassandra + `scripts/logging/` |
| Capa 3: Infrastructure Logs | Sistema operativo (nginx, postgresql) | Cassandra (futuro) |

Ver: `docs/gobernanza/ai/DORA_CASSANDRA_INTEGRATION.md`

### 5.2 Baseline DORA (Objetivos)

| Metrica | Objetivo Elite | Objetivo Actual |
|---------|----------------|-----------------|
| Deployment Frequency | Multiple por dia | 1 por semana |
| Lead Time for Changes | < 1 dia | < 7 dias |
| Change Failure Rate | < 5% | < 15% |
| Mean Time to Restore | < 1 hora | < 4 horas |

### 5.3 Request ID Tracing

Cada request tiene un `request_id` UUID que traza todo el flujo:

```python
# En logs Django
logger.info("Processing request", extra={"request_id": request_id})

# Query Cassandra por request_id
SELECT * FROM logging.application_logs
WHERE request_id = '123e4567-e89b-12d3-a456-426614174000';
```

---

## 6. Calidad de Codigo

### 6.1 Pre-commit Hooks

Ver `.pre-commit-hooks-readme.md` para detalles.

Hooks configurados:
- Black (formateo Python)
- isort (ordenar imports)
- flake8 (linting)
- bandit (seguridad)
- markdownlint (docs)
- detect-secrets (secrets)

### 6.2 Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests de una app
pytest api/callcentersite/callcentersite/apps/analytics/tests/

# Ejecutar con coverage
pytest --cov=callcentersite --cov-report=html

# Ver coverage report
open htmlcov/index.html
```

### 6.3 Code Quality Metrics

Objetivos:
- Test coverage: >= 80%
- Flake8: 0 warnings
- Bandit: 0 security issues
- Type hints coverage: >= 70% (gradual)

---

## 7. Documentacion

### 7.1 Frontmatter YAML

Todos los documentos Markdown tienen frontmatter:

```yaml
---
id: DOC-UNIQUE-ID
tipo: guia|adr|spec|procedimiento
categoria: backend|frontend|infrastructure
fecha: 2025-11-07
version: 1.0.0
propietario: tech-lead
relacionados: ["DOC-ID-1", "DOC-ID-2"]
---
```

### 7.2 Plantillas

Ver `docs/plantillas/` para plantillas de documentos:
- `plantilla_django_app.md`: Documentar apps Django
- `plantilla_etl_job.md`: Documentar ETL jobs
- `plantilla_api_reference.md`: Documentar APIs REST

### 7.3 MkDocs

```bash
# Instalar dependencias
pip install -r docs/requirements.txt

# Servir documentacion localmente
mkdocs serve -f docs/mkdocs.yml

# Build estatico
mkdocs build -f docs/mkdocs.yml

# Abrir en navegador
open http://127.0.0.1:8000
```

---

## 8. Collaboration Protocols

### 8.1 AI Specialists + Platform Team

**Roles:**
- **Platform Team**: Infraestructura, CI/CD, logging, monitoring
- **AI Specialists**: AI models, data pipelines, analytics

**Collaboration:**
1. **Data Access**: Platform expone APIs para AI team
2. **Logging**: AI team usa Cassandra logging via Platform scripts
3. **Metrics**: Platform expone DORA metrics, AI team consume
4. **Deployment**: Platform gestiona deployments, AI team provee artifacts

**Communication Channels:**
- Slack: #platform-team, #ai-specialists
- Weekly sync: Viernes 10:00 AM
- On-call: Platform team 24/7, AI team business hours

**Escalation:**
- L1: Desarrollador contacta AI specialist o Platform engineer
- L2: Team lead (AI Lead o Platform Lead)
- L3: Arquitecto Senior + CTO

Ver: `docs/gobernanza/ai/COLLABORATION_PROTOCOLS.md` (futuro)

### 8.2 Code Review

**Proceso:**
1. AI Code Review (Claude/Copilot)
2. Self-review checklist
3. Request human review (2 approvals requeridos)
4. Address feedback
5. Merge (squash commits)

**Reviewers:**
- Backend: @equipo-backend-lead, @arquitecto-senior
- Frontend: @equipo-frontend-lead
- Infrastructure: @devops-lead

Ver: `.github/CODEOWNERS`

---

## 9. Recursos y Referencias

### 9.1 Documentacion Clave

| Documento | Proposito |
|-----------|-----------|
| `README.md` | Estructura proyecto |
| `docs/proyecto/ROADMAP.md` | Roadmap features |
| `docs/proyecto/CHANGELOG.md` | Historial cambios |
| `docs/adr/` | Decisiones arquitecturales |
| `docs/gobernanza/ai/AI_STANCE.md` | AI guidelines |

### 9.2 Links Externos

- DORA Research: https://dora.dev
- Django 4.2 Docs: https://docs.djangoproject.com/en/4.2/
- Cassandra Docs: https://cassandra.apache.org/doc/
- Pre-commit: https://pre-commit.com
- Conventional Commits: https://www.conventionalcommits.org/

### 9.3 Canales de Comunicacion

- Slack: #iact-general, #iact-backend, #iact-frontend
- Email: iact-dev@company.com
- Issues: GitHub Issues
- Meetings: Standup diario 9:00 AM, Retro cada 2 semanas

---

## 10. FAQ

### Q: Donde reporto bugs?

GitHub Issues con label `bug`. Template auto-generado.

### Q: Como pido acceso a Cassandra production?

Contactar Platform Lead via Slack. Requiere aprobacion arquitecto.

### Q: Puedo usar AI para escribir tests?

Si, pero DEBES validar manualmente. AI genera estructura, tu validas logica.

### Q: Como actualizo documentacion?

1. Editar .md con frontmatter YAML
2. Pre-commit valida formato
3. PR con 1 aprobacion (arquitecto-senior)

### Q: Donde encuentro metricas DORA?

Dashboard: http://dora.internal.company.com (futuro)
Script: `python scripts/dora_metrics.py --show`

### Q: Como accedo a logs Cassandra?

```bash
# Logs ultimas 24h nivel ERROR
python scripts/logging/cassandra_query.py --level ERROR --hours 24

# Logs por request_id
python scripts/logging/cassandra_query.py --request-id <uuid>
```

---

## 11. Proximos Pasos

### Tu Primera Semana

**Dia 1-2: Setup**
- [x] Configurar entorno Python + Django
- [x] Ejecutar tests localmente
- [x] Instalar pre-commit hooks

**Dia 3-4: Exploracion**
- [ ] Leer docs/adr/ (ADRs principales)
- [ ] Explorar codigo api/callcentersite/
- [ ] Ejecutar Django admin (http://localhost:8000/admin)

**Dia 5: Primera Contribucion**
- [ ] Elegir good-first-issue de GitHub
- [ ] Crear branch feature/
- [ ] Implementar con AI assistance
- [ ] Crear PR

### Tu Primer Mes

- [ ] Completar 3 features
- [ ] Documentar 1 app Django (plantilla_django_app.md)
- [ ] Revisar 5 PRs de otros desarrolladores
- [ ] Asistir a 2 retros + 1 planning

---

**Contacto Onboarding:**
- Tech Lead: tech-lead@company.com
- Arquitecto Senior: arquitecto-senior@company.com
- HR: hr@company.com

**Feedback:**
Ayudanos a mejorar esta guia: https://github.com/company/IACT---project/issues/new?template=onboarding-feedback.md

---

**Creado**: 2025-11-07
**Version**: 1.0.0
**Responsable**: Tech Lead
**Relacionados**: README.md, docs/gobernanza/ai/AI_STANCE.md

---

**Bienvenido al equipo IACT!**
