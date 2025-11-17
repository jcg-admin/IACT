---
id: PLAN-EJECUCION-COMPLETO
tipo: plan_ejecucion
categoria: planificacion
version: 1.0.0
fecha_creacion: 2025-11-07
propietario: arquitecto-senior
relacionados: ["TAREAS_ACTIVAS.md", "ROADMAP.md", "CHANGELOG.md", "ANALISIS_GAPS_POST_DORA_2025.md"]
date: 2025-11-13
---

# PLAN DE EJECUCION COMPLETO - Proyecto IACT

Plan detallado para completar las 38 tareas pendientes identificadas en el proyecto IACT.

**Version:** 1.0.0
**Fecha creacion:** 2025-11-07
**Horizonte temporal:** 2025-11-07 a 2026-06-30
**Total tareas:** 38
**Total Story Points:** 184 SP
**Duracion estimada:** 45 dias (1 dev) o 22.5 dias (2 devs)

---

## Vision General del Plan

### Objetivos Estrategicos

1. Alcanzar 100 por ciento DORA AI Capabilities (actualmente 80 por ciento)
2. Completar todas las validaciones criticas de compliance
3. Implementar sistema de observabilidad completo
4. Automatizar SDLC con agentes IA
5. Establecer plataforma robusta para Q2 2026

### Metricas de Exito

- Coverage de tests mayor o igual a 80 por ciento
- DORA score 7/7 (100 por ciento)
- 0 violaciones de restricciones criticas (RNF-002)
- Deployment Frequency mayor o igual a 1/semana
- Lead Time menor a 2 dias
- Change Failure Rate menor a 15 por ciento
- MTTR menor a 4 horas

---

## SPRINT 1: Fundamentos Criticos (Semana 1)

**Fechas:** 2025-11-07 a 2025-11-13
**Objetivo:** Completar todas las validaciones P0 e iniciar sistema de metrics
**Story Points:** 14 SP
**Velocity objetivo:** 14 SP

### Tareas P0 - CRITICO (6 SP)

#### TASK-001: Ejecutar Suite Completa de Tests
**Prioridad:** P0
**Story Points:** 2 SP
**Asignado:** backend-lead
**Dependencias:** Ninguna
**Bloqueadores:** Ninguno

**Descripcion:**
Ejecutar suite completa de tests para validar coverage mayor o igual a 80 por ciento y compliance.

**Pasos de ejecucion:**
```bash
# 1. Navegar a directorio backend
cd api/callcentersite

# 2. Ejecutar tests con coverage
pytest --cov=callcentersite --cov-report=term --cov-report=html --cov-fail-under=80

# 3. Verificar resultados
# - Coverage >= 80%
# - 0 tests fallidos
# - HTML report generado en htmlcov/

# 4. Commit results
git add htmlcov/ .coverage
git commit -m "test: ejecutar suite completa - coverage validado >= 80%"
```

**Criterios de aceptacion:**
- [REQUERIDO] Coverage mayor o igual a 80 por ciento
- [REQUERIDO] 0 tests fallidos
- [REQUERIDO] HTML report generado
- [OPCIONAL] Coverage report en CI/CD

**Outputs:**
- htmlcov/index.html
- .coverage
- pytest.xml

---

#### TASK-002: Validar Restricciones Criticas
**Prioridad:** P0
**Story Points:** 1 SP
**Asignado:** backend-lead
**Dependencias:** Ninguna
**Bloqueadores:** Ninguno

**Descripcion:**
Ejecutar validacion completa de restricciones criticas RNF-002.

**Pasos de ejecucion:**
```bash
# 1. Ejecutar script de validacion
./scripts/validate_critical_restrictions.sh

# 2. Verificar output
# Expected: [OK] Todas las validaciones pasadas
# - NO Redis en requirements.txt
# - NO Redis en settings.py
# - NO SMTP/Email en codigo
# - SESSION_ENGINE = db

# 3. Si falla, corregir antes de continuar
# 4. Re-ejecutar hasta pasar

# 5. Commit validacion
git add scripts/validate_critical_restrictions.sh
git commit -m "validate: ejecutar restricciones criticas - RNF-002 compliant"
```

**Criterios de aceptacion:**
- [REQUERIDO] Script retorna exit code 0
- [REQUERIDO] NO Redis encontrado
- [REQUERIDO] NO Email/SMTP encontrado
- [REQUERIDO] SESSION_ENGINE = django.contrib.sessions.backends.db

**Outputs:**
- Validation report (stdout)

---

#### TASK-003: Verificar SESSION_ENGINE en Settings
**Prioridad:** P0
**Story Points:** 1 SP
**Asignado:** backend-lead
**Dependencias:** Ninguna
**Bloqueadores:** Ninguno

**Descripcion:**
Grep y verificar SESSION_ENGINE en todos los archivos settings.

**Pasos de ejecucion:**
```bash
# 1. Buscar SESSION_ENGINE
grep -r "SESSION_ENGINE" api/callcentersite/*/settings*.py

# 2. Verificar resultado esperado
# Expected: SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 3. Si no existe, agregar a settings.py
echo "SESSION_ENGINE = 'django.contrib.sessions.backends.db'" >> api/callcentersite/callcentersite/settings.py

# 4. Verificar en base de datos
python manage.py shell -c "from django.conf import settings; print(settings.SESSION_ENGINE)"

# 5. Commit si hubo cambios
git add api/callcentersite/callcentersite/settings.py
git commit -m "config: configurar SESSION_ENGINE = db (RNF-002)"
```

**Criterios de aceptacion:**
- [REQUERIDO] SESSION_ENGINE = django.contrib.sessions.backends.db
- [REQUERIDO] Tabla django_session existe en MySQL
- [REQUERIDO] 0 referencias a Redis

**Outputs:**
- settings.py actualizado (si necesario)

---

#### TASK-004: Tests de Auditoria Inmutable
**Prioridad:** P0
**Story Points:** 2 SP
**Asignado:** backend-lead
**Dependencias:** Ninguna
**Bloqueadores:** Ninguno

**Descripcion:**
Ejecutar y validar tests de auditoria inmutable (TEST-AUDIT-002) para compliance ISO 27001.

**Pasos de ejecucion:**
```bash
# 1. Navegar a tests
cd api/callcentersite

# 2. Ejecutar test especifico
pytest tests/audit/test_audit_log.py -v -k "test_audit_log_immutability"

# 3. Verificar criterios
# - Audit logs NO pueden ser modificados
# - Audit logs NO pueden ser eliminados
# - Timestamp automatico
# - User tracking automatico

# 4. Si falla, revisar AuditLog model
# 5. Re-ejecutar hasta pasar

# 6. Generar reporte
pytest tests/audit/test_audit_log.py --html=reports/audit_test_report.html

# 7. Commit
git add reports/audit_test_report.html
git commit -m "test(audit): validar inmutabilidad - ISO 27001 compliant"
```

**Criterios de aceptacion:**
- [REQUERIDO] test_audit_log_immutability PASS
- [REQUERIDO] AuditLog model sin metodo delete()
- [REQUERIDO] AuditLog model sin metodo save() que permita updates
- [REQUERIDO] HTML report generado

**Outputs:**
- reports/audit_test_report.html

---

### Tareas P1 - ALTA (8 SP iniciadas)

#### TASK-005: Sistema de Metrics Interno (MySQL)
**Prioridad:** P1
**Story Points:** 8 SP
**Asignado:** backend-lead
**Dependencias:** TASK-001 a TASK-004 completadas
**Bloqueadores:** Ninguno

**Descripcion:**
Implementar tabla dora_metrics en MySQL para centralizar metricas DORA, performance y usage.

**Pasos de ejecucion:**
```bash
# FASE 1: Crear Django app (1 SP)
cd api/callcentersite
python manage.py startapp dora_metrics

# FASE 2: Crear modelo (2 SP)
# Editar dora_metrics/models.py
cat > dora_metrics/models.py << 'EOF'
from django.db import models
from django.utils import timezone

class DORAMetric(models.Model):
    """Metricas DORA para rastreo de performance del equipo."""

    cycle_id = models.CharField(max_length=50, unique=True)
    feature_id = models.CharField(max_length=50)
    phase_name = models.CharField(max_length=50)  # planning, testing, deployment, maintenance
    decision = models.CharField(max_length=20)    # go, no-go, review, blocked
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'dora_metrics'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phase_name']),
            models.Index(fields=['feature_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.cycle_id} - {self.phase_name}"
EOF

# FASE 3: Crear migracion (1 SP)
python manage.py makemigrations dora_metrics
python manage.py migrate dora_metrics

# FASE 4: Crear API endpoints (2 SP)
# Editar dora_metrics/views.py
cat > dora_metrics/views.py << 'EOF'
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import DORAMetric
from datetime import timedelta
from django.utils import timezone

@require_http_methods(["GET"])
def dora_metrics_summary(request):
    """GET /api/dora/metrics - Summary ultimos 30 dias."""
    days = int(request.GET.get('days', 30))
    cutoff = timezone.now() - timedelta(days=days)

    metrics = DORAMetric.objects.filter(created_at__gte=cutoff)

    # Calcular Lead Time promedio
    deployment_metrics = metrics.filter(phase_name='deployment')
    avg_lead_time = deployment_metrics.aggregate(
        avg=models.Avg('duration_seconds')
    )['avg'] or 0

    # Calcular Deployment Frequency
    deployment_count = deployment_metrics.count()

    # Calcular Change Failure Rate
    testing_metrics = metrics.filter(phase_name='testing')
    failed_tests = testing_metrics.filter(decision='no-go').count()
    total_tests = testing_metrics.count()
    cfr = (failed_tests / total_tests * 100) if total_tests > 0 else 0

    return JsonResponse({
        'period_days': days,
        'metrics': {
            'lead_time_hours': avg_lead_time / 3600,
            'deployment_frequency': deployment_count,
            'change_failure_rate': cfr,
            'mttr_hours': 0  # TODO: implementar
        },
        'total_cycles': metrics.values('cycle_id').distinct().count()
    })

@require_http_methods(["POST"])
def dora_metrics_create(request):
    """POST /api/dora/metrics - Crear metrica."""
    import json
    data = json.loads(request.body)

    metric = DORAMetric.objects.create(
        cycle_id=data['cycle_id'],
        feature_id=data['feature_id'],
        phase_name=data['phase_name'],
        decision=data['decision'],
        duration_seconds=data['duration_seconds'],
        metadata=data.get('metadata', {})
    )

    return JsonResponse({
        'id': metric.id,
        'cycle_id': metric.cycle_id,
        'created_at': metric.created_at.isoformat()
    }, status=201)
EOF

# FASE 5: Configurar URLs (1 SP)
# Editar dora_metrics/urls.py
cat > dora_metrics/urls.py << 'EOF'
from django.urls import path
from . import views

urlpatterns = [
    path('metrics/', views.dora_metrics_summary, name='dora-metrics-summary'),
    path('metrics/create/', views.dora_metrics_create, name='dora-metrics-create'),
]
EOF

# Agregar a main urls.py
echo "path('api/dora/', include('dora_metrics.urls'))," >> callcentersite/urls.py

# FASE 6: Migrar datos de JSON (1 SP)
python scripts/migrate_dora_json_to_mysql.py

# FASE 7: Commit
git add dora_metrics/
git commit -m "feat(dora): agregar sistema metrics interno MySQL - completa practica 3"
```

**Criterios de aceptacion:**
- [REQUERIDO] Tabla dora_metrics creada
- [REQUERIDO] Modelo DORAMetric funcional
- [REQUERIDO] API GET /api/dora/metrics operativa
- [REQUERIDO] API POST /api/dora/metrics operativa
- [REQUERIDO] Datos de .dora_sdlc_metrics.json migrados
- [OPCIONAL] Django Admin configurado

**Outputs:**
- dora_metrics/ (nueva app Django)
- Migraciones
- API endpoints

---

#### TASK-006: Validar Estructura de Docs
**Prioridad:** P1
**Story Points:** 1 SP
**Asignado:** tech-writer
**Dependencias:** Ninguna
**Bloqueadores:** Ninguno

**Descripcion:**
Ejecutar validacion de estructura de docs para verificar no broken links.

**Pasos de ejecucion:**
```bash
# 1. Ejecutar script
./scripts/validar_estructura_docs.sh

# 2. Revisar output
# Expected: [OK] Estructura valida, 0 broken links

# 3. Si falla, corregir links rotos
# 4. Re-ejecutar

# 5. Commit si hubo correcciones
git add docs/
git commit -m "docs: validar estructura - 0 broken links"
```

**Criterios de aceptacion:**
- [REQUERIDO] 0 broken links
- [REQUERIDO] Todos los archivos en INDICE.md existen
- [REQUERIDO] 0 referencias a docs_legacy/

**Outputs:**
- Validation report

---

### Resumen Sprint 1

**Story Points completados objetivo:** 14 SP
**Duracion:** 7 dias
**Tareas completadas:** 6 de 38

**Estado esperado al final:**
- [OK] Todas las validaciones P0 pasadas
- [OK] Sistema de metrics MySQL iniciado (50 por ciento)
- [OK] Docs validados

---

## SPRINT 2: Sistema de Metrics y DORA Baseline (Semana 2)

**Fechas:** 2025-11-14 a 2025-11-20
**Objetivo:** Completar sistema de metrics y establecer DORA baseline
**Story Points:** 10 SP
**Velocity objetivo:** 10 SP

### Tareas

#### TASK-005 (Continuacion): Completar Sistema de Metrics
**Story Points restantes:** 4 SP (de 8 total)

Ver Sprint 1 TASK-005 para detalles completos.

**FASE 6-7:** Migrar datos y testing (continuacion)

---

#### TASK-007: Ejecutar Primer DORA Metrics Report
**Prioridad:** P1
**Story Points:** 1 SP
**Asignado:** devops-lead
**Dependencias:** GITHUB_TOKEN obtenido
**Bloqueadores:** GITHUB_TOKEN faltante

**Descripcion:**
Ejecutar primer reporte DORA para establecer baseline.

**Pasos de ejecucion:**
```bash
# PREREQUISITO: Obtener GITHUB_TOKEN
# 1. Ir a GitHub Settings > Developer settings > Personal access tokens
# 2. Generate new token (classic)
# 3. Scopes: repo (full control)
# 4. Export token

export GITHUB_TOKEN="ghp_..."

# 1. Ejecutar script DORA
python scripts/dora_metrics.py \
    --repo 2-Coatl/IACT---project \
    --days 30 \
    --format markdown \
    > DORA_REPORT_20251114.md

# 2. Revisar reporte
cat DORA_REPORT_20251114.md

# 3. Analizar metricas baseline
# - Deployment Frequency actual
# - Lead Time actual
# - Change Failure Rate actual
# - MTTR actual

# 4. Commit reporte
git add DORA_REPORT_20251114.md
git commit -m "metrics(dora): establecer baseline - primeros 30 dias"

# 5. Documentar baseline en CHANGELOG.md
```

**Criterios de aceptacion:**
- [REQUERIDO] Reporte markdown generado
- [REQUERIDO] 4 metricas calculadas
- [REQUERIDO] Clasificacion DORA (Elite/High/Medium/Low)
- [REQUERIDO] Baseline documentada

**Outputs:**
- DORA_REPORT_20251114.md

---

#### TASK-008: Configurar Cron Job DORA Mensuales
**Prioridad:** P1
**Story Points:** 1 SP
**Asignado:** devops-lead
**Dependencias:** TASK-007
**Bloqueadores:** Ninguno

**Descripcion:**
Configurar cron job para generar reportes DORA automaticamente cada mes.

**Pasos de ejecucion:**
```bash
# 1. Crear script wrapper
cat > /usr/local/bin/generate_dora_report.sh << 'EOF'
#!/bin/bash
export GITHUB_TOKEN="ghp_..."
cd /path/to/IACT---project
python scripts/dora_metrics.py \
    --repo 2-Coatl/IACT---project \
    --days 30 \
    --format markdown \
    > /var/log/iact/dora_$(date +%Y%m).md
EOF

chmod +x /usr/local/bin/generate_dora_report.sh

# 2. Agregar a crontab
crontab -e
# Add line:
# 0 0 1 * * /usr/local/bin/generate_dora_report.sh >> /var/log/iact/dora_cron.log 2>&1

# 3. Test manual
/usr/local/bin/generate_dora_report.sh

# 4. Verificar output
ls -la /var/log/iact/dora_*.md

# 5. Commit script
git add scripts/generate_dora_report.sh
git commit -m "automation(dora): agregar cron job mensual"
```

**Criterios de aceptacion:**
- [REQUERIDO] Cron job configurado
- [REQUERIDO] Script ejecuta exitosamente
- [REQUERIDO] Output en /var/log/iact/
- [REQUERIDO] Test manual exitoso

**Outputs:**
- /usr/local/bin/generate_dora_report.sh
- Cron entry

---

#### TASK-009: Comunicar AI Stance al Equipo
**Prioridad:** P1
**Story Points:** 1 SP
**Asignado:** arquitecto-senior
**Dependencias:** Ninguna
**Bloqueadores:** Ninguno

**Descripcion:**
Presentar ESTRATEGIA_IA.md al equipo con Q&A session.

**Pasos de ejecucion:**
```bash
# 1. Preparar presentacion
# - Slides de ESTRATEGIA_IA.md
# - Ejemplos de uso correcto/incorrecto IA
# - Guidelines practicas

# 2. Agendar meeting (1 hora)
# - Invite: Todo el equipo dev
# - Agenda: AI Stance + Q&A

# 3. Presentar contenido clave
# - 7 practicas DORA AI Capabilities
# - AI-First vs AI-Enabled
# - Cuando usar/no usar IA
# - Human oversight obligatorio
# - Checklist diario AI_CAPABILITIES.md

# 4. Q&A session (30 min)

# 5. Distribuir documentacion
# - Email con link a docs/gobernanza/ai/ESTRATEGIA_IA.md
# - Checklist AI_CAPABILITIES.md

# 6. Documentar feedback
# - Crear issue con preguntas frecuentes
# - Actualizar FAQ en ESTRATEGIA_IA.md

# 7. Commit actualizaciones
git add docs/gobernanza/ai/ESTRATEGIA_IA.md
git commit -m "docs(ai): actualizar FAQ post-presentacion equipo"
```

**Criterios de aceptacion:**
- [REQUERIDO] Presentacion realizada
- [REQUERIDO] Q&A session completada
- [REQUERIDO] Documentacion distribuida
- [REQUERIDO] Feedback documentado

**Outputs:**
- Slides de presentacion
- Minutes de meeting
- FAQ actualizado

---

#### TASK-010: Logging Estructurado (JSON)
**Prioridad:** P1
**Story Points:** 3 SP
**Asignado:** backend-lead
**Dependencias:** TASK-001 a TASK-004
**Bloqueadores:** Ninguno

**Descripcion:**
Configurar Python logging para output JSON estructurado.

**Pasos de ejecucion:**
```bash
# FASE 1: Crear JSON formatter (1 SP)
cat > api/callcentersite/callcentersite/logging_config.py << 'EOF'
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatter para logs en formato JSON."""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Agregar contexto extra
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_data['session_id'] = record.session_id

        # Agregar exception si existe
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)
EOF

# FASE 2: Actualizar settings.py (1 SP)
cat >> api/callcentersite/callcentersite/settings.py << 'EOF'

# Logging configuration - JSON structured
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'callcentersite.logging_config.JSONFormatter',
        },
    },
    'handlers': {
        'json_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/iact/app.json.log',
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['json_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'callcentersite': {
            'handlers': ['json_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
EOF

# FASE 3: Test logging (1 SP)
python manage.py shell << 'EOF'
import logging
logger = logging.getLogger('callcentersite')
logger.info('Test JSON logging', extra={'request_id': 'test-123', 'user_id': 1})
EOF

# Verificar output
tail -1 /var/log/iact/app.json.log | jq .

# FASE 4: Commit
git add api/callcentersite/callcentersite/logging_config.py
git add api/callcentersite/callcentersite/settings.py
git commit -m "feat(logging): agregar JSON structured logging - AI parseable"
```

**Criterios de aceptacion:**
- [REQUERIDO] JSONFormatter implementado
- [REQUERIDO] Logs en formato JSON valido
- [REQUERIDO] Campos requeridos presentes (timestamp, level, logger, message)
- [REQUERIDO] Log rotation configurado (100MB max)
- [REQUERIDO] Test exitoso

**Outputs:**
- callcentersite/logging_config.py
- Updated settings.py

---

### Resumen Sprint 2

**Story Points completados objetivo:** 10 SP
**Duracion:** 7 dias
**Tareas completadas:** 5 mas (11 de 38 total)

**Estado esperado al final:**
- [OK] Sistema de metrics MySQL completo (100 por ciento)
- [OK] DORA baseline establecida
- [OK] Logging JSON estructurado
- [OK] AI Stance comunicado al equipo

---

## SPRINT 3: Data Centralization y Configuracion (Semana 3)

**Fechas:** 2025-11-21 a 2025-11-27
**Objetivo:** Completar data centralization y configuracion de maintenance
**Story Points:** 11 SP
**Velocity objetivo:** 11 SP

### Tareas

#### TASK-011: Data Centralization Layer
**Prioridad:** P1
**Story Points:** 5 SP
**Asignado:** backend-lead + devops-lead
**Dependencias:** TASK-005, TASK-010
**Bloqueadores:** Ninguno

**Descripcion:**
Consolidar metrics, logs y health checks en capa unificada de consulta.

**Pasos de ejecucion:**
```bash
# FASE 1: Crear app centralization (1 SP)
cd api/callcentersite
python manage.py startapp data_centralization

# FASE 2: Implementar Query API unificada (2 SP)
cat > data_centralization/views.py << 'EOF'
from django.http import JsonResponse
from dora_metrics.models import DORAMetric
import json

def unified_query(request):
    """GET /api/data/query - Query unificada para metrics, logs, health."""
    query_type = request.GET.get('type')  # metrics, logs, health
    days = int(request.GET.get('days', 7))

    if query_type == 'metrics':
        # Query metrics de MySQL
        metrics = DORAMetric.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=days)
        )
        data = list(metrics.values())

    elif query_type == 'logs':
        # Query logs de Cassandra
        from cassandra.cluster import Cluster
        cluster = Cluster(['cassandra-1'])
        session = cluster.connect('logging')

        rows = session.execute(
            "SELECT * FROM application_logs WHERE log_date >= ? LIMIT 1000",
            [date.today() - timedelta(days=days)]
        )
        data = [dict(row) for row in rows]

    elif query_type == 'health':
        # Query health checks
        import subprocess
        result = subprocess.run(
            ['./scripts/health_check.sh', '--format', 'json'],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)

    else:
        return JsonResponse({'error': 'Invalid query type'}, status=400)

    return JsonResponse({
        'query_type': query_type,
        'days': days,
        'count': len(data),
        'data': data
    })
EOF

# FASE 3: Configurar retention policies (1 SP)
cat > data_centralization/management/commands/apply_retention.py << 'EOF'
from django.core.management.base import BaseCommand
from dora_metrics.models import DORAMetric
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Aplicar retention policies a datos antiguos'

    def handle(self, *args, **options):
        # Retention: Logs 90 dias (automatico en Cassandra)
        # Retention: Metrics permanente (NO delete)
        # Retention: Health checks 30 dias

        cutoff = timezone.now() - timedelta(days=30)
        # deleted = HealthCheck.objects.filter(created_at__lt=cutoff).delete()

        self.stdout.write(f'Retention policies aplicadas')
EOF

# FASE 4: Implementar backup automatizado (1 SP)
cat > scripts/backup_data_centralization.sh << 'EOF'
#!/bin/bash
# Backup de datos centralizados

BACKUP_DIR="/var/backups/iact"
DATE=$(date +%Y%m%d)

# Backup MySQL (metrics)
mysqldump -u root -p iact_db dora_metrics > "$BACKUP_DIR/dora_metrics_$DATE.sql"

# Backup Cassandra (logs - snapshot)
docker exec cassandra-1 nodetool snapshot logging

# Comprimir
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" "$BACKUP_DIR"/*.sql

# Retention: 30 dias
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete

echo "[OK] Backup completado: $BACKUP_DIR/backup_$DATE.tar.gz"
EOF

chmod +x scripts/backup_data_centralization.sh

# FASE 5: Commit
git add data_centralization/ scripts/backup_data_centralization.sh
git commit -m "feat(data): agregar centralization layer + backup - completa practica 7"
```

**Criterios de aceptacion:**
- [REQUERIDO] API GET /api/data/query operativa
- [REQUERIDO] Query type metrics, logs, health funcionando
- [REQUERIDO] Retention policies implementadas
- [REQUERIDO] Backup automatizado funcionando
- [REQUERIDO] Test de query exitoso

**Outputs:**
- data_centralization/ (nueva app)
- scripts/backup_data_centralization.sh

---

#### TASK-012: Agregar AI Guidelines a Onboarding
**Prioridad:** P1
**Story Points:** 2 SP
**Asignado:** tech-lead
**Dependencias:** TASK-009
**Bloqueadores:** Ninguno

**Descripcion:**
Actualizar onboarding guide con ESTRATEGIA_IA y checklist.

**Pasos de ejecucion:**
```bash
# 1. Actualizar ONBOARDING.md
cat >> docs/proyecto/ONBOARDING.md << 'EOF'

---

## AI Stance y Guidelines

### Vision de IA en IACT

El proyecto IACT adopta una postura **AI-Enabled Development**:
- Uso intensivo de AI assistants (Claude, GitHub Copilot)
- AI Code Review antes de human review
- AI-generated documentation con human oversight
- AI-powered testing

Documentacion completa: [ESTRATEGIA_IA.md](../gobernanza/ai/ESTRATEGIA_IA.md)

### Checklist Diario para Developers

Usar checklist [AI_CAPABILITIES.md](../gobernanza/ai/AI_CAPABILITIES.md):

**Uso de IA:**
- [ ] Codigo generado por IA revisado por humano
- [ ] AI suggestions evaluadas criticamente
- [ ] Documentacion AI-generated verificada
- [ ] Tests AI-generated validados

**Restricciones:**
- [ ] NO confiar ciegamente en AI
- [ ] NO skip human review
- [ ] NO commit AI code sin entender
- [ ] NO usar AI para decisiones criticas de seguridad

### Herramientas Recomendadas

1. **Claude Code** - Pair programming, code review
2. **GitHub Copilot** - Code completion
3. **ChatGPT** - Documentation, explanations

### Referencias

- [ESTRATEGIA_IA.md](../gobernanza/ai/ESTRATEGIA_IA.md)
- [AI_CAPABILITIES.md](../gobernanza/ai/AI_CAPABILITIES.md)
- [DORA Report 2025 - AI Capabilities](https://dora.dev/capabilities/ai/)
EOF

# 2. Commit
git add docs/proyecto/ONBOARDING.md
git commit -m "docs(onboarding): agregar AI guidelines - DORA AI Stance"
```

**Criterios de aceptacion:**
- [REQUERIDO] ONBOARDING.md actualizado
- [REQUERIDO] Link a ESTRATEGIA_IA.md
- [REQUERIDO] Checklist AI_CAPABILITIES.md incluido
- [REQUERIDO] Herramientas recomendadas listadas

**Outputs:**
- Updated ONBOARDING.md

---

#### TASK-013: Configurar Cron Jobs para Maintenance
**Prioridad:** P1
**Story Points:** 1 SP
**Asignado:** devops-lead
**Dependencias:** Scripts completados
**Bloqueadores:** Ninguno

**Descripcion:**
Configurar cron jobs para cleanup sessions y health checks.

**Pasos de ejecucion:**
```bash
# 1. Agregar a crontab
crontab -e

# 2. Agregar entradas
cat >> /tmp/crontab.txt << 'EOF'
# Cleanup sessions cada 6 horas
0 */6 * * * /path/to/scripts/cleanup_sessions.sh >> /var/log/iact/cleanup.log 2>&1

# Health check cada 5 minutos
*/5 * * * * /path/to/scripts/health_check.sh >> /var/log/iact/health.log 2>&1

# Backup data centralization diario 2 AM
0 2 * * * /path/to/scripts/backup_data_centralization.sh >> /var/log/iact/backup.log 2>&1
EOF

crontab /tmp/crontab.txt

# 3. Verificar cron activo
crontab -l

# 4. Test manual
/path/to/scripts/cleanup_sessions.sh --dry-run
/path/to/scripts/health_check.sh

# 5. Documentar en README
cat >> scripts/README.md << 'EOF'

## Cron Jobs Configurados

### Cleanup Sessions
- Frecuencia: Cada 6 horas
- Comando: cleanup_sessions.sh
- Log: /var/log/iact/cleanup.log

### Health Check
- Frecuencia: Cada 5 minutos
- Comando: health_check.sh
- Log: /var/log/iact/health.log

### Backup
- Frecuencia: Diario 2 AM
- Comando: backup_data_centralization.sh
- Log: /var/log/iact/backup.log
EOF

# 6. Commit
git add scripts/README.md
git commit -m "automation: configurar cron jobs maintenance"
```

**Criterios de aceptacion:**
- [REQUERIDO] 3 cron jobs configurados
- [REQUERIDO] Test manual exitoso
- [REQUERIDO] Logs en /var/log/iact/
- [REQUERIDO] Documentacion actualizada

**Outputs:**
- Cron entries
- Updated scripts/README.md

---

#### TASK-014: Custom Dashboards Django Admin (INICIO)
**Prioridad:** P2
**Story Points:** 5 SP (3 SP este sprint)
**Asignado:** backend-lead
**Dependencias:** TASK-005, TASK-011
**Bloqueadores:** Ninguno

**Descripcion:**
Crear dashboards custom en Django Admin para visualizacion de metrics.

**Pasos de ejecucion Sprint 3 (3 SP):**
```bash
# FASE 1: Registrar modelos en admin (1 SP)
cat > dora_metrics/admin.py << 'EOF'
from django.contrib import admin
from .models import DORAMetric

@admin.register(DORAMetric)
class DORAMetricAdmin(admin.ModelAdmin):
    list_display = ['cycle_id', 'feature_id', 'phase_name', 'decision', 'created_at']
    list_filter = ['phase_name', 'decision', 'created_at']
    search_fields = ['cycle_id', 'feature_id']
    readonly_fields = ['created_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing
            return self.readonly_fields + ['cycle_id']
        return self.readonly_fields
EOF

# FASE 2: Crear dashboard view (2 SP)
cat > dora_metrics/dashboard.py << 'EOF'
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import DORAMetric
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count

@staff_member_required
def dora_dashboard(request):
    """Dashboard de metricas DORA."""
    days = int(request.GET.get('days', 30))
    cutoff = timezone.now() - timedelta(days=days)

    metrics = DORAMetric.objects.filter(created_at__gte=cutoff)

    # Calculos
    deployment_metrics = metrics.filter(phase_name='deployment')
    avg_lead_time = deployment_metrics.aggregate(avg=Avg('duration_seconds'))['avg'] or 0
    deployment_count = deployment_metrics.count()

    testing_metrics = metrics.filter(phase_name='testing')
    failed = testing_metrics.filter(decision='no-go').count()
    total = testing_metrics.count()
    cfr = (failed / total * 100) if total > 0 else 0

    context = {
        'days': days,
        'lead_time_hours': avg_lead_time / 3600,
        'deployment_frequency': deployment_count,
        'change_failure_rate': cfr,
        'mttr_hours': 0,
        'total_cycles': metrics.values('cycle_id').distinct().count(),
    }

    return render(request, 'dora_metrics/dashboard.html', context)
EOF

# Continuara en Sprint 4 (FASE 3: Template HTML)

# Commit progreso
git add dora_metrics/admin.py dora_metrics/dashboard.py
git commit -m "feat(dora): agregar admin + dashboard view (WIP)"
```

**Criterios de aceptacion Sprint 3:**
- [REQUERIDO] Admin registrado
- [REQUERIDO] Dashboard view implementada
- [PENDIENTE] Template HTML (Sprint 4)

**Outputs parciales:**
- dora_metrics/admin.py
- dora_metrics/dashboard.py

---

### Resumen Sprint 3

**Story Points completados objetivo:** 11 SP
**Duracion:** 7 dias
**Tareas completadas:** 4 mas (15 de 38 total)

**Estado esperado al final:**
- [OK] Data Centralization Layer completo
- [OK] AI Guidelines en onboarding
- [OK] Cron jobs configurados
- [OK] Dashboards 60 por ciento completo

**HITO IMPORTANTE:** 100 por ciento DORA AI Capabilities alcanzado

---

## SPRINT 4-6: P2 - Media Prioridad (Semanas 4-6)

**Fechas:** 2025-11-28 a 2025-12-18
**Objetivo:** Completar tareas P2 y preparar para Q1 2026
**Story Points:** 28 SP (restantes de P2)
**Velocity objetivo:** 9-10 SP/semana

### Resumen de Tareas P2 Restantes

- TASK-014 (continuacion): Dashboards Django Admin - 2 SP restantes
- TASK-015: Pre-commit hooks - 2 SP
- TASK-016: Backend CI coverage report - 2 SP
- TASK-017: Security scan PR checks - 2 SP
- TASK-018: SDLCFeasibilityAgent - 8 SP
- TASK-019: SDLCDesignAgent - 13 SP
- TASK-020: GitHub API integration - 5 SP
- TASK-021: Migrations workflow - 5 SP

**Total Sprint 4-6:** 39 SP

---

## Q1 2026: P3 - Backlog (Enero - Marzo)

**Fechas:** 2026-01-01 a 2026-03-31
**Objetivo:** Implementar features avanzadas y AI telemetry
**Story Points:** 123 SP
**Duracion estimada:** 6 semanas (2 devs)

### Tareas Principales Q1

- TASK-022: AI-enabled telemetry pipeline - 13 SP
- TASK-027: Analytics portal setup - 3 SP
- TASK-028: Process analytics requests - 5 SP
- TASK-029: Mejorar SDLCPlannerAgent con LLM - 8 SP
- TASK-031: SDLCTestingAgent - 8 SP
- TASK-032: SDLCDeploymentAgent - 8 SP
- TASK-033: SDLCOrchestratorAgent - 13 SP
- TASK-034: SDLCMaintenanceAgent - 8 SP

---

## Q2 2026: P3 - Optimizacion (Abril - Junio)

**Fechas:** 2026-04-01 a 2026-06-30
**Objetivo:** Optimizacion y features predictivas
**Story Points:** 65 SP restantes
**Duracion estimada:** 3 semanas (2 devs)

### Tareas Principales Q2

- TASK-23: Predictive analytics dashboard - 21 SP
- TASK-30: Dashboard web agentes SDLC - 21 SP
- TASK-35: Predictive analytics SDLC - 21 SP
- TASK-36: Chaos Engineering - 13 SP
- TASK-37: Capacity planning - 13 SP
- TASK-38: Self-healing infrastructure - 21 SP

---

## Metricas de Progreso

### KPIs del Plan

**Metricas de velocidad:**
- Velocity objetivo: 20 SP/semana (1 dev) o 40 SP/semana (2 devs)
- Burndown rate objetivo: Lineal
- Sprint completion rate objetivo: mayor o igual a 90 por ciento

**Metricas de calidad:**
- Test coverage: mayor o igual a 80 por ciento
- DORA score: 7/7 (100 por ciento) al final Sprint 3
- Restricciones RNF-002: 0 violaciones
- Code review approval: 100 por ciento

**Metricas DORA objetivo (Q1 2026):**
- Deployment Frequency: mayor o igual a 1/semana
- Lead Time: menor a 2 dias
- Change Failure Rate: menor a 15 por ciento
- MTTR: menor a 4 horas

---

## Gestion de Riesgos

### Riesgos Identificados

#### RIESGO-001: GITHUB_TOKEN No Disponible
**Impacto:** ALTO
**Probabilidad:** MEDIA
**Mitigacion:**
- Obtener token en Sprint 1
- Escalate a management si bloqueado
- Alternativa: Usar datos mock para desarrollo

#### RIESGO-002: Sistema de Metrics Mas Complejo de lo Esperado
**Impacto:** MEDIO
**Probabilidad:** MEDIA
**Mitigacion:**
- Buffer de 2 SP adicionales si necesario
- Priorizar funcionalidad basica primero
- Postponer features avanzadas a Sprint 3

#### RIESGO-003: Cassandra Cluster Issues
**Impacto:** ALTO
**Probabilidad:** BAJA
**Mitigacion:**
- Scripts instalacion ya probados
- Documentacion completa disponible
- Soporte disponible en scripts/cassandra/README.md

#### RIESGO-004: Velocity Menor a Estimado
**Impacto:** MEDIO
**Probabilidad:** MEDIA
**Mitigacion:**
- Re-priorizar tareas cada sprint
- Postponer P3 si necesario
- Focus en P0 y P1 criticas

---

## Dependencias Externas

### Bloqueadores Criticos

1. **GITHUB_TOKEN**
   - Necesario para: TASK-007, TASK-008
   - Owner: devops-lead
   - ETA: Sprint 1

2. **Cassandra Cluster Running**
   - Necesario para: TASK-011, TASK-014
   - Owner: devops-lead
   - Status: READY (ya instalado)

3. **MySQL Database Access**
   - Necesario para: TASK-005
   - Owner: devops-lead
   - Status: READY

---

## Criterios de Aceptacion del Plan Completo

### Sprint 1-3 (Critico)
- [REQUERIDO] Todas las tareas P0 completadas
- [REQUERIDO] Sistema de metrics MySQL operativo
- [REQUERIDO] DORA baseline establecida
- [REQUERIDO] 100 por ciento DORA AI Capabilities
- [REQUERIDO] Data Centralization Layer funcionando

### Sprint 4-6 (Importante)
- [REQUERIDO] Pre-commit hooks instalados
- [REQUERIDO] Dashboards Django Admin operativos
- [DESEABLE] 2 agentes SDLC adicionales (Feasibility, Design)

### Q1 2026 (Nice to Have)
- [DESEABLE] AI-enabled telemetry pipeline
- [DESEABLE] 4 agentes SDLC adicionales
- [DESEABLE] Analytics service management

### Q2 2026 (Futuro)
- [OPCIONAL] Predictive analytics
- [OPCIONAL] Chaos engineering
- [OPCIONAL] Self-healing infrastructure

---

## Actualizacion del Plan

**Frecuencia:** Semanal (cada viernes)

**Responsable:** arquitecto-senior

**Proceso:**
1. Revisar tareas completadas vs. planeadas
2. Actualizar Story Points restantes
3. Identificar bloqueadores
4. Ajustar prioridades si necesario
5. Commit: `docs(plan): actualizar progreso semana [N]`

**Proximo checkpoint:** 2025-11-13 (fin Sprint 1)

---

## Referencias

### Documentos Relacionados

- [TAREAS_ACTIVAS.md](docs/proyecto/TAREAS_ACTIVAS.md) - Sprint actual
- [ROADMAP.md](docs/proyecto/ROADMAP.md) - Vision largo plazo
- [CHANGELOG.md](docs/proyecto/CHANGELOG.md) - Historial
- [ANALISIS_GAPS_POST_DORA_2025.md](docs/gobernanza/ai/ANALISIS_GAPS_POST_DORA_2025.md) - Gaps DORA

### Scripts Clave

- scripts/run_all_tests.sh
- scripts/validate_critical_restrictions.sh
- scripts/health_check.sh
- scripts/dora_metrics.py
- scripts/backup_data_centralization.sh

### Contactos

- **Arquitecto Senior:** @arquitecto-senior
- **Backend Lead:** @backend-lead
- **DevOps Lead:** @devops-lead
- **Tech Lead:** @tech-lead
- **QA Lead:** @qa-lead

---

**VERSION:** 1.0.0
**ESTADO:** ACTIVO
**PROXIMA REVISION:** 2025-11-13
**MANTENEDOR:** @arquitecto-senior
