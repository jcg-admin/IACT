---
task_id: TASK-034
title: Auto-remediation System
status: completed
story_points: 13
sprint: Sprint 4
category: features/ai
tags: [ai, auto-remediation, automation, incident-response, dora-2025]
created: 2025-11-07
updated: 2025-11-07
---

# Auto-remediation System

## Resumen Ejecutivo

Sistema que detecta problemas comunes en la infraestructura y aplicacion, propone fixes automaticos, y los ejecuta con aprobacion humana cuando es necesario. Incluye workflow de aprobacion basado en severidad, rollback automatico, y audit logging completo.

## Objetivo

Reducir MTTR (Mean Time To Recovery) mediante deteccion automatica de problemas y aplicacion de fixes conocidos, con safeguards apropiados para evitar acciones destructivas sin supervision humana.


## Técnicas de Prompt Engineering para Agente

Las siguientes técnicas deben aplicarse al ejecutar esta tarea con un agente:

1. **Code Generation** (fundamental_techniques.py)
   - Generar codigo base para nuevas features y componentes

2. **Task Decomposition** (structuring_techniques.py)
   - Dividir features en user stories y tareas implementables

3. **Few-Shot** (fundamental_techniques.py)
   - Usar ejemplos de features similares como referencia

4. **Expert Prompting** (specialized_techniques.py)
   - Aplicar patrones de diseno y mejores practicas de desarrollo

5. **Meta-prompting** (structuring_techniques.py)
   - Generar prompts especializados para diferentes aspectos de la feature

Agente recomendado: FeatureAgent o SDLCDesignAgent
## Story Points

13 SP - Complejidad Alta

## Arquitectura

### Componentes

1. **ProblemDetector**: Detecta problemas comunes
   - detect_disk_space_low()
   - detect_database_slow_queries()
   - detect_high_error_rate()
   - detect_memory_leak()

2. **RemediationEngine**: Propone y ejecuta fixes
   - propose_fix(problem)
   - execute_fix(plan, approved_by)
   - rollback_fix(execution_id)
   - audit_log_action()

3. **API Endpoints**:
   - GET /api/dora/remediation/problems/
   - POST /api/dora/remediation/propose-fix/
   - POST /api/dora/remediation/execute/
   - POST /api/dora/remediation/rollback/{id}/

### Problemas Detectables

#### 1. Disk Space Low
- **Deteccion**: disk usage > 80%
- **Severidad**: P2 (80-90%), P1 (>90%)
- **Fix**: Cleanup old Django sessions (>30 days)
- **Aprobacion**: P0/P1 require, P2/P3 auto

#### 2. Database Slow Queries
- **Deteccion**: queries running > 30 seconds
- **Severidad**: P2 (3-10 queries), P1 (>10 queries)
- **Fix**: Kill queries > 60 seconds
- **Aprobacion**: P0/P1 require, P2/P3 auto

#### 3. High Error Rate
- **Deteccion**: errors > 20 in last 5 min
- **Severidad**: P1 (20-100), P0 (>100)
- **Fix**: Restart application service
- **Aprobacion**: Siempre require (alta impact)

#### 4. Memory Leak
- **Deteccion**: memory growth > 3% per hour
- **Severidad**: P2 (3-8%), P1 (>8%)
- **Fix**: Clear application cache
- **Aprobacion**: P0/P1 require, P2/P3 auto

### Workflow de Aprobacion

**Workflow Diagram:**
```
┌─────────────────┐
│ Problem Detected│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Propose Fix     │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │Severity│
    └───┬────┘
        │
   ┌────┴────┐
   │         │
P0/P1      P2/P3
   │         │
   ▼         ▼
┌──────┐  ┌──────────────┐
│Require│  │Auto-execute │
│Approval│  │+ Notify     │
└───┬──┘  └──────┬───────┘
    │            │
    └────┬───────┘
         │
         ▼
    ┌────────┐
    │Execute │
    │  Fix   │
    └───┬────┘
        │
        ▼
    ┌────────┐
    │Monitor │
    │Result  │
    └───┬────┘
        │
   ┌────┴────┐
   │         │
Success    Fail
   │         │
   ▼         ▼
┌──────┐  ┌──────────┐
│Log   │  │Rollback  │
│Audit │  │+ Alert   │
└──────┘  └──────────┘
```

**Aprobacion Required:**
- P0 (Critical): Siempre require human approval
- P1 (High): Siempre require human approval
- P2 (Medium): Auto-execute, notify after
- P3 (Low): Auto-execute, notify after

**Timeout:**
- P0: 15 minutos sin aprobacion -> Escalate
- P1: 1 hora sin aprobacion -> Escalate
- P2/P3: Execute immediately

### Fixes Implementados

#### 1. Cleanup Old Sessions
```python
action: CLEANUP_SESSIONS
target: Django sessions older than 30 days
estimated_impact: Low
rollback: Sessions recreate on next login
```

**Implementation:**
```python
from django.contrib.sessions.models import Session
cutoff = timezone.now() - timedelta(days=30)
deleted = Session.objects.filter(expire_date__lt=cutoff).delete()
```

#### 2. Kill Slow Queries
```python
action: KILL_SLOW_QUERIES
target: MySQL queries running > 60 seconds
estimated_impact: Medium (may abort reports)
rollback: Users re-run queries
```

**Implementation:**
```sql
SELECT id, user, time, info 
FROM information_schema.processlist 
WHERE time > 60 AND command != 'Sleep';

KILL {query_id};
```

#### 3. Restart Service
```python
action: RESTART_SERVICE
target: Django application service
estimated_impact: High (~30 sec downtime)
rollback: Auto-restart
```

**Implementation:**
```bash
systemctl restart django-app
```

#### 4. Clear Cache
```python
action: CLEAR_CACHE
target: Application cache
estimated_impact: Low (cache rebuilds)
rollback: Auto-rebuild
```

**Implementation:**
```python
from django.core.cache import cache
cache.clear()
```

### Rollback Strategy

**Automatic Rollback:**
- Si fix empeora situacion (detected by monitoring)
- Timeout: 5 minutos post-fix
- Triggers:
  - Error rate increases 2x
  - Response time increases 3x
  - Service health check fails

**Manual Rollback:**
- POST /api/dora/remediation/rollback/{execution_id}/
- Requires admin privileges
- Audit logged

### Audit Trail

**Audit Log Entry:**
```json
{
  "execution_id": "exec-1699363200",
  "timestamp": "2025-11-07T10:30:00Z",
  "problem_type": "disk_space_low",
  "severity": "P2",
  "action": "cleanup_sessions",
  "approved_by": "user@example.com",
  "success": true,
  "duration_seconds": 2.5,
  "result": {
    "deleted_sessions": 150,
    "message": "Cleaned up 150 old sessions"
  }
}
```

**Retention:**
- Audit logs retained 90 days
- Critical (P0/P1) logs retained 1 year
- Searchable by: execution_id, timestamp, problem_type, approved_by

### Safety Mechanisms

1. **Approval Required for High Impact:**
   - Service restarts
   - Database operations
   - P0/P1 problems

2. **Dry Run Mode:**
   - Test fixes without executing
   - Validate rollback plans
   - Estimate impact

3. **Rate Limiting:**
   - Max 1 auto-remediation per minute
   - Max 10 per hour
   - Prevent cascading failures

4. **Circuit Breaker:**
   - Disable auto-remediation after 3 failures
   - Require manual reset
   - Alert on-call engineer

5. **Validation:**
   - Pre-execution health check
   - Post-execution validation
   - Rollback if validation fails

## API Endpoints

### 1. List Problems
**GET /api/dora/remediation/problems/**

Response:
```json
{
  "total_problems": 2,
  "problems": [
    {
      "problem_type": "disk_space_low",
      "severity": "P2",
      "description": "Disk space usage at 85.0% (threshold: 80%)",
      "detected_at": "2025-11-07T10:30:00Z",
      "metadata": {"percent_used": 85.0}
    },
    {
      "problem_type": "database_slow_queries",
      "severity": "P2",
      "description": "5 slow queries detected (threshold: 3)",
      "detected_at": "2025-11-07T10:30:05Z",
      "metadata": {"slow_query_count": 5}
    }
  ]
}
```

### 2. Propose Fix
**POST /api/dora/remediation/propose-fix/**

Request:
```json
{
  "problem_type": "disk_space_low"
}
```

Response:
```json
{
  "plan": {
    "problem": {...},
    "action": "cleanup_sessions",
    "description": "Cleanup old Django sessions from database",
    "requires_approval": false,
    "estimated_impact": "Low - Remove sessions older than 30 days",
    "rollback_plan": "Sessions can be recreated automatically on next login",
    "metadata": {"cleanup_age_days": 30},
    "created_at": "2025-11-07T10:31:00Z"
  }
}
```

### 3. Execute Fix
**POST /api/dora/remediation/execute/**

Request:
```json
{
  "problem_type": "disk_space_low",
  "approved_by": "admin@example.com"
}
```

Response:
```json
{
  "success": true,
  "execution_id": "exec-1699363200",
  "started_at": "2025-11-07T10:32:00Z",
  "completed_at": "2025-11-07T10:32:02.5Z",
  "duration_seconds": 2.5,
  "result": {
    "success": true,
    "deleted_sessions": 150,
    "message": "Cleaned up 150 old sessions"
  },
  "approved_by": "admin@example.com"
}
```

### 4. Rollback Fix
**POST /api/dora/remediation/rollback/{execution_id}/**

Response:
```json
{
  "success": true,
  "execution_id": "exec-1699363200",
  "message": "Rollback completed"
}
```

## Implementation

### Files Created
1. api/callcentersite/dora_metrics/auto_remediation.py
2. api/callcentersite/dora_metrics/views.py (updated)
3. api/callcentersite/dora_metrics/urls.py (updated)
4. docs/features/ai/TASK-034-auto-remediation-system.md

### Dependencies
- Django >= 4.2
- psutil (for disk/memory monitoring)
- mysqlclient (for database operations)

## Monitoring

### Metrics
- Problems detected per hour
- Auto-remediations executed per hour
- Manual approvals required per day
- Success rate of fixes
- Average MTTR improvement

### Alerts
- Auto-remediation failure rate > 20%
- Circuit breaker triggered
- Manual approval timeout (P0/P1)

## Usage Example

```python
import requests

# List problems
response = requests.get("https://api/dora/remediation/problems/")
problems = response.json()["problems"]

# Propose fix for first problem
problem_type = problems[0]["problem_type"]
response = requests.post(
    "https://api/dora/remediation/propose-fix/",
    json={"problem_type": problem_type}
)
plan = response.json()["plan"]

# Execute fix (with approval if required)
response = requests.post(
    "https://api/dora/remediation/execute/",
    json={
        "problem_type": problem_type,
        "approved_by": "admin@example.com"
    }
)
result = response.json()
```

## Compliance

**RNF-002:** 100% compliant
- NO Redis
- NO Prometheus
- NO Grafana
- Uses MySQL for audit logs
- Uses Django session database

## Roadmap

### Phase 2
- Machine learning for problem prediction
- Auto-tuning of thresholds
- Integration with TASK-033 (Predictive Analytics)
- Chatbot for approval workflow

## Conclusion

El Auto-remediation System reduce MTTR mediante deteccion y fix automatico de problemas comunes, con safeguards apropiados para mantener estabilidad del sistema.

---
**Autor:** Claude AI Agent
**Fecha:** 2025-11-07
**Version:** 1.0
**Estado:** Completado

## Detailed Problem Detection

### Disk Space Detection Algorithm

```python
def detect_disk_space_low():
    import shutil
    disk = shutil.disk_usage("/")
    percent_used = (disk.used / disk.total) * 100
    
    # Thresholds
    if percent_used > 90:
        severity = P1  # Critical
    elif percent_used > 80:
        severity = P2  # Warning
    else:
        return None  # OK
    
    return Problem(
        problem_type="disk_space_low",
        severity=severity,
        description=f"Disk at {percent_used:.1f}%",
        metadata={"percent": percent_used}
    )
```

### Slow Query Detection

```python
def detect_slow_queries():
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, user, time, info
            FROM information_schema.processlist
            WHERE time > 30 AND command != 'Sleep'
        """)
        slow_queries = cursor.fetchall()
    
    if len(slow_queries) > 10:
        severity = P1
    elif len(slow_queries) > 3:
        severity = P2
    else:
        return None
    
    return Problem(
        problem_type="slow_queries",
        severity=severity,
        description=f"{len(slow_queries)} slow queries",
        metadata={"count": len(slow_queries)}
    )
```

## Remediation Plan Structure

```python
class RemediationPlan:
    problem: Problem            # Original problem
    action: RemediationAction   # Action to take
    description: str            # Human-readable description
    requires_approval: bool     # Human approval needed?
    estimated_impact: str       # Impact description
    rollback_plan: str          # How to rollback
    metadata: dict              # Additional data
    created_at: datetime        # When plan created
```

## Execution Flow

1. **Detection Phase**
   - Run all problem detectors
   - Prioritize by severity
   - Deduplicate similar problems

2. **Planning Phase**
   - For each problem, propose fix
   - Estimate impact and risk
   - Determine if approval needed

3. **Approval Phase (if required)**
   - Notify on-call engineer
   - Wait for approval (with timeout)
   - Log approval decision

4. **Execution Phase**
   - Pre-execution health check
   - Execute remediation action
   - Monitor execution progress

5. **Validation Phase**
   - Post-execution health check
   - Validate problem resolved
   - If validation fails, rollback

6. **Audit Phase**
   - Log all actions and results
   - Update metrics
   - Notify stakeholders

## Error Handling

### Execution Errors

```python
try:
    result = execute_fix(plan)
except PermissionError:
    # Insufficient privileges
    return {"error": "Permission denied"}
except TimeoutError:
    # Operation took too long
    rollback_fix(execution_id)
    return {"error": "Timeout, rolled back"}
except Exception as e:
    # Unexpected error
    rollback_fix(execution_id)
    alert_on_call()
    return {"error": str(e)}
```

### Rollback Errors

If rollback fails:
1. Alert on-call immediately (P0)
2. Log detailed error information
3. Escalate to senior engineer
4. Document manual recovery steps

## Testing Strategy

### Unit Tests
- Test each problem detector
- Test each remediation action
- Test approval workflow
- Test rollback mechanism

### Integration Tests
- End-to-end problem -> fix -> validate
- Multi-problem scenarios
- Concurrent executions
- Failure scenarios

### Chaos Engineering
- Inject failures during execution
- Test circuit breaker
- Test rollback under load
- Validate audit logging

## Performance Metrics

### Detection Performance
- Detection latency: P95 < 100ms
- False positive rate: < 5%
- False negative rate: < 1%

### Execution Performance
- Fix execution time: varies by action
  - cleanup_sessions: ~2 seconds
  - kill_slow_queries: ~1 second
  - restart_service: ~30 seconds
  - clear_cache: ~500ms

### Success Rates
- Target: > 95% success rate
- Rollback success: > 99%
- Manual intervention: < 10% of cases

## Security Considerations

### Authentication
- API requires valid authentication token
- Approval requires admin privileges
- Audit logs are immutable

### Authorization
- Role-based access control
- Separate roles for:
  - Viewer (read problems)
  - Operator (execute auto-approved fixes)
  - Admin (approve P0/P1 fixes)
  - Super Admin (rollback, disable system)

### Audit Trail
- All actions logged immutably
- Logs include user identity
- Tamper-evident logging
- Regular audit reviews

## Operational Runbooks

### Runbook: Disk Space Low

1. **Detection**: Disk usage > 80%
2. **Immediate Actions**:
   - Check if legitimate growth or leak
   - Review largest files/directories
3. **Remediation**:
   - Auto: Cleanup old sessions (P2/P3)
   - Manual: Delete old logs, archives (P0/P1)
4. **Prevention**:
   - Set up log rotation
   - Monitor growth trends
   - Plan capacity increase

### Runbook: Slow Queries

1. **Detection**: Queries running > 30 seconds
2. **Immediate Actions**:
   - Identify query patterns
   - Check database load
3. **Remediation**:
   - Auto: Kill queries > 60 sec (P2/P3)
   - Manual: Optimize queries, add indexes (P0/P1)
4. **Prevention**:
   - Query performance testing
   - Regular index optimization
   - Query timeout enforcement

### Runbook: High Error Rate

1. **Detection**: > 20 errors in 5 minutes
2. **Immediate Actions**:
   - Review error logs
   - Check recent deployments
3. **Remediation**:
   - Manual: Investigate root cause
   - Last resort: Restart service
4. **Prevention**:
   - Improve error handling
   - Better input validation
   - Comprehensive testing

## Integration with Other Systems

### Integration with TASK-024 (AI Telemetry)
- Log remediation decisions as AI telemetry
- Track success rate of auto-remediations
- Improve fix selection based on feedback

### Integration with TASK-033 (Predictive Analytics)
- Predict when problems will occur
- Proactive remediation
- Optimize fix timing

### Integration with Monitoring
- Trigger on monitoring alerts
- Update monitoring dashboards
- Create incidents in ticket system

## Future Enhancements

1. **Smarter Detection**
   - Pattern recognition for recurring problems
   - Anomaly detection using ML
   - Predictive problem detection

2. **Advanced Remediation**
   - Multi-step remediation plans
   - Conditional logic in fixes
   - Self-learning remediation strategies

3. **Better Collaboration**
   - Slack/Teams integration for approvals
   - Collaborative troubleshooting
   - Knowledge base integration

4. **Compliance & Governance**
   - Change management integration
   - Compliance validation
   - Risk assessment automation
