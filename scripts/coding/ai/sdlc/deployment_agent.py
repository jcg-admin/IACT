"""
SDLCDeploymentAgent - Fase 6: Deployment

Responsabilidad: Generar deployment plan, rollback plan, y procedimientos
para features listas para produccion.

Inputs:
- testing_result (dict): Output de SDLCTestingAgent
- design_result (dict): Output de SDLCDesignAgent
- issue (dict): Issue del SDLCPlannerAgent
- environment (str): Target environment (staging, production)

Outputs:
- Deployment plan completo
- Rollback plan
- Pre-deployment checklist
- Post-deployment checklist
- Monitoring plan
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .base_agent import SDLCAgent, SDLCPhaseResult

# Add parent paths for LLMGenerator import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from generators.llm_generator import LLMGenerator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    LLMGenerator = None

# Deployment method constants
DEPLOYMENT_METHOD_LLM = "llm"
DEPLOYMENT_METHOD_HEURISTIC = "heuristic"


class SDLCDeploymentAgent(SDLCAgent):
    """
    Agente para la fase de Deployment del SDLC.

    Genera deployment plan, rollback plan, y procedimientos completos.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCDeploymentAgent",
            phase="deployment",
            config=config
        )

        # Initialize LLM generator if config provided and LLM available
        self.llm_generator = None
        if config and LLM_AVAILABLE:
            try:
                self.llm_generator = LLMGenerator(config=config)
                self.logger.info(f"LLMGenerator initialized with {config.get('llm_provider', 'default')}")
            except Exception as e:
                self.logger.warning(f"Failed to initialize LLM: {e}. Falling back to heuristics.")

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """Valida que existan testing y design results."""
        errors = []

        if "testing_result" not in input_data:
            errors.append("Falta 'testing_result' en input (del SDLCTestingAgent)")

        if "design_result" not in input_data:
            errors.append("Falta 'design_result' en input (del SDLCDesignAgent)")

        if "issue" not in input_data:
            errors.append("Falta 'issue' en input (del SDLCPlannerAgent)")

        # Validar que tests pasaron
        if "testing_result" in input_data:
            phase_result = input_data["testing_result"].get("phase_result")
            if phase_result and phase_result.decision != "go":
                errors.append("No se puede deployar con tests fallidos. Resolver problemas primero.")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la fase de Deployment.

        Args:
            input_data: {
                "issue": dict,  # Output de SDLCPlannerAgent
                "design_result": dict,  # Output de SDLCDesignAgent
                "testing_result": dict,  # Output de SDLCTestingAgent
                "environment": str  # "staging" or "production"
            }

        Returns:
            Dict con deployment plan, rollback plan, checklists
        """
        issue = input_data["issue"]
        design_result = input_data["design_result"]
        testing_result = input_data["testing_result"]
        environment = input_data.get("environment", "staging")

        self.logger.info(f"Generando deployment plan para: {issue.get('issue_title', 'Unknown')} -> {environment}")

        # Determine deployment method
        deployment_method = DEPLOYMENT_METHOD_LLM if self.llm_generator else DEPLOYMENT_METHOD_HEURISTIC

        # Generar deployment plan
        deployment_plan = self._generate_deployment_plan(issue, design_result, testing_result, environment)

        # Generar rollback plan
        rollback_plan = self._generate_rollback_plan(issue, environment)

        # Generar pre-deployment checklist
        pre_deployment_checklist = self._generate_pre_deployment_checklist(issue, testing_result)

        # Generar post-deployment checklist
        post_deployment_checklist = self._generate_post_deployment_checklist(issue)

        # Generar monitoring plan
        monitoring_plan = self._generate_monitoring_plan(issue)

        # Guardar artefactos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts = []

        deployment_path = self.save_artifact(deployment_plan, f"DEPLOYMENT_PLAN_{environment}_{timestamp}.md")
        artifacts.append(str(deployment_path))

        rollback_path = self.save_artifact(rollback_plan, f"ROLLBACK_PLAN_{environment}_{timestamp}.md")
        artifacts.append(str(rollback_path))

        pre_checklist_path = self.save_artifact(pre_deployment_checklist, f"PRE_DEPLOYMENT_CHECKLIST_{timestamp}.md")
        artifacts.append(str(pre_checklist_path))

        post_checklist_path = self.save_artifact(post_deployment_checklist, f"POST_DEPLOYMENT_CHECKLIST_{timestamp}.md")
        artifacts.append(str(post_checklist_path))

        monitoring_path = self.save_artifact(monitoring_plan, f"MONITORING_PLAN_{timestamp}.md")
        artifacts.append(str(monitoring_path))

        # Crear resultado de fase
        phase_result = self.create_phase_result(
            decision="go",
            confidence=0.95,
            artifacts=artifacts,
            recommendations=[
                "Deployment plan completo generado",
                "Ejecutar pre-deployment checklist antes de deploy",
                "Mantener rollback plan accesible durante deploy",
                "Monitorear sistema durante y despues de deploy"
            ],
            next_steps=[
                "Ejecutar pre-deployment checklist",
                "Crear backup de base de datos",
                "Ejecutar deployment en horario de baja demanda",
                "Validar deployment con post-deployment checklist",
                "Activar monitoring",
                "Proceder con Maintenance phase"
            ]
        )

        return {
            "deployment_plan": deployment_plan,
            "deployment_path": str(deployment_path),
            "rollback_plan": rollback_plan,
            "rollback_path": str(rollback_path),
            "pre_deployment_checklist": pre_deployment_checklist,
            "pre_checklist_path": str(pre_checklist_path),
            "post_deployment_checklist": post_deployment_checklist,
            "post_checklist_path": str(post_checklist_path),
            "monitoring_plan": monitoring_plan,
            "monitoring_path": str(monitoring_path),
            "environment": environment,
            "artifacts": artifacts,
            "deployment_method": deployment_method,
            "phase_result": phase_result
        }

    def _generate_deployment_plan(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        testing_result: Dict[str, Any],
        environment: str
    ) -> str:
        """Genera deployment plan completo."""
        title = issue.get("issue_title", "Unknown Feature")

        plan = f"""# Deployment Plan

**Feature**: {title}
**Environment**: {environment.upper()}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Deploy Lead**: _________
**Version**: 1.0

---

## 1. Executive Summary

### Deployment Objective
Deploy feature: {title} to {environment} environment

### Deployment Window
- **Scheduled Date**: ___________
- **Start Time**: _________ (preferably during low traffic hours)
- **Estimated Duration**: 30-60 minutes
- **Downtime Expected**: None (rolling deployment)

### Key Stakeholders
- **Deploy Lead**: _________
- **Backend Lead**: _________
- **DevOps Lead**: _________
- **On-call Engineer**: _________

---

## 2. Prerequisites

### Code Ready
- [ ] All code merged to main branch
- [ ] All tests passing (coverage > 80%)
- [ ] Code review approved
- [ ] Static analysis passed

### Infrastructure Ready
- [ ] Target environment available
- [ ] Database migrations prepared
- [ ] Environment variables configured
- [ ] Secrets updated if needed

### Team Ready
- [ ] Deploy team notified
- [ ] On-call engineer available
- [ ] Rollback plan reviewed
- [ ] Communication channels active

---

## 3. Database Changes

### Migrations Required
{self._list_database_migrations(design_result)}

### Migration Steps
```bash
# Backup database FIRST
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD iact_{environment} > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
cd api/callcentersite
python manage.py migrate --no-input

# Verify migrations
python manage.py showmigrations
```

### Data Migration
{self._list_data_migrations(design_result)}

---

## 4. Deployment Steps

### Step 1: Pre-deployment Validation
```bash
# Execute pre-deployment checklist
./scripts/validate_critical_restrictions.sh
./scripts/validate_security_config.sh
./scripts/run_all_tests.sh
```

### Step 2: Create Backup
```bash
# Database backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD iact_{environment} > backup_$(date +%Y%m%d_%H%M%S).sql

# Code backup (tag current version)
git tag -a pre-deploy-$(date +%Y%m%d-%H%M%S) -m "Backup before {title} deployment"
git push origin --tags
```

### Step 3: Deploy Code
```bash
# Pull latest code
git fetch origin
git checkout main
git pull origin main

# Install dependencies (if changed)
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input
```

### Step 4: Run Migrations
```bash
# Apply database migrations
python manage.py migrate --no-input

# Verify migrations
python manage.py showmigrations
```

### Step 5: Restart Services
```bash
# Restart application server
sudo systemctl restart gunicorn-iact-{environment}

# Reload web server
sudo systemctl reload nginx

# Verify services running
sudo systemctl status gunicorn-iact-{environment}
sudo systemctl status nginx
```

### Step 6: Health Check
```bash
# Wait for app to start
sleep 10

# Health check
curl -f http://localhost/api/health || echo "HEALTH CHECK FAILED"

# Check specific feature endpoint
curl -f http://localhost/api/feature-endpoint || echo "FEATURE CHECK FAILED"
```

### Step 7: Smoke Tests
```bash
# Run smoke tests
python manage.py test callcentersite.tests.smoke_tests --tag=smoke

# Verify critical paths
./scripts/smoke_test_{environment}.sh
```

---

## 5. Verification Steps

### Functional Verification
- [ ] Feature accessible via UI/API
- [ ] All acceptance criteria verified
- [ ] No errors in application logs
- [ ] Database queries executing correctly

### Performance Verification
- [ ] Response times < 2s
- [ ] No significant increase in CPU/memory
- [ ] Database connection pool stable
- [ ] No N+1 query issues

### Security Verification
- [ ] Authentication working
- [ ] Authorization rules applied
- [ ] No sensitive data exposed
- [ ] HTTPS enforced

---

## 6. Rollback Criteria

### Automatic Rollback Triggers
- Health check fails after deployment
- Critical errors in logs
- Database migrations fail

### Manual Rollback Triggers
- Feature breaks existing functionality
- Performance degradation > 50%
- Security vulnerability discovered
- Stakeholder request

---

## 7. Communication Plan

### Pre-deployment Communication
- [ ] Notify team 24h before deployment
- [ ] Send deployment window to stakeholders
- [ ] Update status page (if applicable)

### During Deployment
- [ ] Update team via Slack/Teams channel
- [ ] Log progress in deployment doc
- [ ] Alert on any issues immediately

### Post-deployment Communication
- [ ] Announce successful deployment
- [ ] Share monitoring dashboard
- [ ] Document lessons learned

---

## 8. Monitoring

### Key Metrics to Monitor
- Application response time
- Error rate
- Database query performance
- Session table size (MySQL)
- CPU and memory usage

### Monitoring Duration
- **Intensive monitoring**: First 2 hours post-deployment
- **Regular monitoring**: 24 hours post-deployment
- **Follow-up check**: 1 week post-deployment

### Monitoring Commands
```bash
# Check application logs
sudo tail -f /var/log/iact/gunicorn.log

# Check error logs
sudo tail -f /var/log/iact/error.log

# Check database connections
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SHOW PROCESSLIST;"

# Check session table
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM django_session;" iact_{environment}
```

---

## 9. Success Criteria

- [ ] All deployment steps completed without errors
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] No increase in error rate
- [ ] Response times within acceptable range
- [ ] No rollback required
- [ ] Stakeholders notified

---

## 10. Post-deployment Tasks

- [ ] Execute post-deployment checklist
- [ ] Update documentation
- [ ] Archive deployment artifacts
- [ ] Conduct post-deployment review (if issues occurred)
- [ ] Update issue tracker
- [ ] Schedule follow-up monitoring

---

## 11. Contacts

### Escalation Path
1. **Deploy Lead**: _________ (phone: _________)
2. **Backend Lead**: _________ (phone: _________)
3. **DevOps Lead**: _________ (phone: _________)
4. **CTO**: _________ (phone: _________)

---

*Generated by SDLCDeploymentAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return plan

    def _generate_rollback_plan(self, issue: Dict[str, Any], environment: str) -> str:
        """Genera rollback plan."""
        title = issue.get("issue_title", "Unknown Feature")

        plan = f"""# Rollback Plan

**Feature**: {title}
**Environment**: {environment.upper()}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Rollback Lead**: _________

---

## 1. Rollback Decision

### When to Rollback
- Health checks failing after deployment
- Critical functionality broken
- Security vulnerability discovered
- Unacceptable performance degradation
- Database corruption detected

### Decision Maker
- **Primary**: Deploy Lead
- **Escalate to**: DevOps Lead or CTO

---

## 2. Rollback Steps

### Step 1: Stop Services
```bash
# Stop application server
sudo systemctl stop gunicorn-iact-{environment}
```

### Step 2: Restore Code
```bash
# Revert to previous version
git fetch origin
git checkout <previous-commit-sha>

# Or use backup tag
git checkout pre-deploy-YYYYMMDD-HHMMSS
```

### Step 3: Restore Database
```bash
# ONLY if migrations were run and caused issues
# WARNING: This will lose any data created since deployment

# Restore from backup
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD iact_{environment} < backup_YYYYMMDD_HHMMSS.sql

# OR Reverse migrations
cd api/callcentersite
python manage.py migrate <app_name> <previous_migration_number>
```

### Step 4: Restart Services
```bash
# Restart application server
sudo systemctl start gunicorn-iact-{environment}

# Reload web server
sudo systemctl reload nginx
```

### Step 5: Verify Rollback
```bash
# Health check
curl -f http://localhost/api/health

# Smoke tests
python manage.py test callcentersite.tests.smoke_tests --tag=smoke
```

---

## 3. Database Rollback Considerations

### Migrations Rollback
- **Safe to rollback**: Additive migrations (add column, add table)
- **DANGEROUS**: Destructive migrations (drop column, drop table)
- **Requires data migration**: Column renames, data transformations

### Data Loss Risk
- Rolling back database = potential data loss
- Evaluate: Is data created since deployment critical?
- Alternative: Keep DB as-is, only rollback code

---

## 4. Rollback Verification

### Critical Checks
- [ ] Application starts successfully
- [ ] Health check endpoint returns 200
- [ ] User can log in
- [ ] Critical workflows function
- [ ] No errors in logs
- [ ] Database connections stable

---

## 5. Post-rollback Actions

### Immediate Actions
- [ ] Notify team of rollback
- [ ] Update status page
- [ ] Begin incident postmortem
- [ ] Document rollback reason

### Follow-up Actions
- [ ] Analyze root cause
- [ ] Fix issues in development
- [ ] Re-test thoroughly
- [ ] Plan re-deployment

---

## 6. Rollback Time Estimate

- **Code-only rollback**: 5-10 minutes
- **Code + database rollback**: 15-30 minutes
- **Complex rollback with data migration**: 30-60 minutes

---

## 7. Communication During Rollback

### Notify
- Development team
- Product owner
- Stakeholders
- Support team

### Message Template
```
ROLLBACK IN PROGRESS

Feature: {title}
Environment: {environment}
Reason: [describe reason]
Expected completion: [time]
Status updates: [frequency]
```

---

## 8. Prevention for Next Deployment

### What Went Wrong
- [Document issue that caused rollback]

### How to Prevent
- [Document preventive measures]

### Additional Testing
- [Document additional tests needed]

---

*Generated by SDLCDeploymentAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return plan

    def _generate_pre_deployment_checklist(
        self,
        issue: Dict[str, Any],
        testing_result: Dict[str, Any]
    ) -> str:
        """Genera pre-deployment checklist."""
        checklist = f"""# Pre-Deployment Checklist

**Feature**: {issue.get('issue_title', 'Unknown')}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Checked by**: _________

---

## Code Quality

- [ ] All code merged to main branch
- [ ] Code review approved by senior developer
- [ ] No merge conflicts
- [ ] All TODOs resolved or documented
- [ ] Code follows project conventions

---

## Testing

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing (if applicable)
- [ ] Code coverage > 80%
- [ ] Manual QA completed
- [ ] Performance tested
- [ ] Security tested

---

## Critical IACT Restrictions

- [ ] NO Redis usage (RNF-002)
- [ ] Sessions in MySQL (django.contrib.sessions.backends.db)
- [ ] NO Email/SMTP usage
- [ ] InternalMessage used for notifications
- [ ] Restrictions validated: ./scripts/validate_critical_restrictions.sh

---

## Database

- [ ] Migrations created and tested
- [ ] Migrations are reversible (or documented as irreversible)
- [ ] Database backup created
- [ ] Migration tested on staging
- [ ] Data migration scripts prepared (if needed)

---

## Configuration

- [ ] Environment variables updated
- [ ] Secrets rotated if needed
- [ ] Configuration validated
- [ ] No hardcoded secrets in code

---

## Documentation

- [ ] README updated
- [ ] API documentation updated
- [ ] Deployment notes documented
- [ ] Known issues documented
- [ ] Rollback plan reviewed

---

## Infrastructure

- [ ] Target environment available
- [ ] Disk space sufficient
- [ ] Dependencies updated
- [ ] Services healthy
- [ ] Monitoring configured

---

## Team Readiness

- [ ] Deploy team notified
- [ ] On-call engineer available
- [ ] Stakeholders notified
- [ ] Communication channels active
- [ ] Rollback plan accessible

---

## Final Validation

- [ ] Deployment plan reviewed
- [ ] Rollback plan reviewed
- [ ] All checklist items completed
- [ ] Go/No-Go decision: _________

---

**Sign-off**

**Deploy Lead**: _________________ Date: _____
**Backend Lead**: _________________ Date: _____
**DevOps Lead**: _________________ Date: _____

---

*Generated by SDLCDeploymentAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return checklist

    def _generate_post_deployment_checklist(self, issue: Dict[str, Any]) -> str:
        """Genera post-deployment checklist."""
        checklist = f"""# Post-Deployment Checklist

**Feature**: {issue.get('issue_title', 'Unknown')}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Verified by**: _________

---

## Immediate Verification (0-15 min)

- [ ] Services restarted successfully
- [ ] Health check endpoint returns 200
- [ ] Application logs show no errors
- [ ] Database connections stable
- [ ] No 500 errors in last 15 minutes

---

## Functional Verification (15-30 min)

- [ ] Feature accessible via UI/API
- [ ] User can log in
- [ ] Core workflows function correctly
- [ ] All acceptance criteria verified
- [ ] No JavaScript errors in console
- [ ] No Django errors in logs

---

## Performance Verification (30-60 min)

- [ ] Response times < 2s
- [ ] No significant increase in response time
- [ ] Database query performance acceptable
- [ ] No N+1 query issues
- [ ] Memory usage stable
- [ ] CPU usage stable

---

## Data Verification

- [ ] Sessions stored in MySQL (check django_session table)
- [ ] Data created by feature persisting correctly
- [ ] No data corruption
- [ ] No orphaned records
- [ ] Database indexes performing well

---

## Security Verification

- [ ] Authentication working correctly
- [ ] Authorization rules applied
- [ ] No sensitive data exposed in logs
- [ ] No sensitive data in responses
- [ ] HTTPS enforced
- [ ] CORS configured correctly

---

## Monitoring

- [ ] Application monitoring active
- [ ] Error tracking active
- [ ] Performance monitoring active
- [ ] Alerts configured
- [ ] Dashboard accessible
- [ ] No critical alerts triggered

---

## Communication

- [ ] Team notified of successful deployment
- [ ] Stakeholders notified
- [ ] Documentation updated
- [ ] Issue tracker updated
- [ ] Deployment logged

---

## Follow-up Tasks

- [ ] Schedule 24h follow-up check
- [ ] Schedule 1-week follow-up check
- [ ] Plan post-deployment review (if issues occurred)
- [ ] Update lessons learned
- [ ] Archive deployment artifacts

---

## Rollback Decision

**Is rollback needed?**: YES / NO

**If NO**: Deployment successful, continue monitoring

**If YES**: Execute rollback plan immediately

**Reason for rollback** (if applicable):
___________________________________

---

**Sign-off**

**Deploy Lead**: _________________ Date: _____
**Backend Lead**: _________________ Date: _____
**DevOps Lead**: _________________ Date: _____

---

*Generated by SDLCDeploymentAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return checklist

    def _generate_monitoring_plan(self, issue: Dict[str, Any]) -> str:
        """Genera monitoring plan."""
        plan = f"""# Monitoring Plan

**Feature**: {issue.get('issue_title', 'Unknown')}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. Monitoring Objectives

- Ensure feature is functioning correctly
- Detect issues early
- Track performance metrics
- Monitor user adoption

---

## 2. Key Metrics

### Application Metrics
- **Response time**: Target < 2s
- **Error rate**: Target < 1%
- **Request volume**: Track trend
- **Success rate**: Target > 99%

### Database Metrics
- **Query performance**: Track slow queries
- **Connection pool**: Monitor usage
- **Session table size**: Track django_session growth
- **Deadlocks**: Should be 0

### Infrastructure Metrics
- **CPU usage**: Track trend
- **Memory usage**: Track trend
- **Disk I/O**: Monitor spikes
- **Network I/O**: Monitor spikes

---

## 3. Monitoring Tools

### Application Logs
```bash
# Real-time logs
sudo tail -f /var/log/iact/gunicorn.log

# Error logs
sudo tail -f /var/log/iact/error.log

# Filter for feature-related logs
sudo grep "feature-keyword" /var/log/iact/gunicorn.log
```

### Database Monitoring
```bash
# Active connections
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SHOW PROCESSLIST;"

# Slow queries
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT * FROM mysql.slow_log ORDER BY start_time DESC LIMIT 10;"

# Session table size
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT COUNT(*) FROM django_session;" iact_production
```

### Health Checks
```bash
# Application health
curl -f http://localhost/api/health

# Feature health
curl -f http://localhost/api/feature-health

# Database health
curl -f http://localhost/api/db-check
```

---

## 4. Alerting Thresholds

### Critical Alerts (Immediate Response)
- Health check fails
- Error rate > 5%
- Response time > 5s
- Database connections exhausted

### Warning Alerts (Monitor Closely)
- Error rate > 2%
- Response time > 3s
- Memory usage > 80%
- Session table > 100k records

---

## 5. Monitoring Schedule

### First 2 Hours (Intensive)
- Check metrics every 15 minutes
- Review logs continuously
- Be ready to rollback

### First 24 Hours (Regular)
- Check metrics every hour
- Review logs every 2 hours
- Monitor alerts

### First Week (Follow-up)
- Daily metrics review
- Weekly summary report

---

## 6. Incident Response

### If Issue Detected
1. Assess severity
2. Notify team
3. Gather data (logs, metrics)
4. Decide: Fix forward or rollback
5. Execute decision
6. Verify resolution
7. Document incident

### Escalation Path
1. Deploy Lead
2. Backend Lead
3. DevOps Lead
4. CTO

---

## 7. Success Indicators

- No critical alerts in first 24h
- Error rate < 1%
- Response times stable
- User adoption positive
- No rollback required

---

*Generated by SDLCDeploymentAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return plan

    def _list_database_migrations(self, design_result: Dict[str, Any]) -> str:
        """Lista migraciones de base de datos."""
        return """
- Migration 0001: Create feature_table
- Migration 0002: Add indexes for performance
"""

    def _list_data_migrations(self, design_result: Dict[str, Any]) -> str:
        """Lista migraciones de datos."""
        return """
No data migrations required for this deployment.
"""

    # LLM Integration Methods

    def _generate_deployment_strategy_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        testing_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Genera estrategia de deployment usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            return self._generate_deployment_strategy_heuristic(issue, environment)

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])
            story_points = issue.get("story_points", 0)

            prompt = f"""Genera una estrategia de deployment detallada para el siguiente feature del proyecto IACT.

**Feature**: {title}
**Environment**: {environment}
**Story Points**: {story_points}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Contexto del Diseño**: {design_result.get('hld', '')[:500]}

**Estado de Testing**: Tests pasados, coverage > 80%

Considera:
1. Tipo de deployment (rolling, blue-green, canary)
2. Fases del deployment
3. Estrategias de mitigación de riesgos
4. Downtime esperado
5. Dependencias y coordinación requerida

Responde en formato JSON:
{{
  "deployment_strategy": {{
    "approach": "rolling|blue-green|canary",
    "phases": ["fase 1", "fase 2"],
    "risk_mitigation": ["estrategia 1", "estrategia 2"],
    "estimated_downtime": "X minutes",
    "rollback_time": "Y minutes"
  }}
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_deployment_strategy(
                llm_response, issue, design_result, testing_result, environment
            )

        except Exception as e:
            self.logger.warning(f"LLM deployment strategy generation failed: {e}, using fallback")
            return self._generate_deployment_strategy_heuristic(issue, environment)

    def _generate_deployment_strategy_heuristic(
        self,
        issue: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Genera estrategia de deployment con heurísticas (fallback)."""
        story_points = issue.get("story_points", 0)

        # Simple heuristic: larger features need more careful deployment
        if story_points >= 8:
            approach = "rolling"
            phases = ["deploy to staging", "test thoroughly", "deploy to 25% production", "monitor", "deploy to 100%"]
        else:
            approach = "standard"
            phases = ["deploy to staging", "test", "deploy to production"]

        return {
            "deployment_strategy": {
                "approach": approach,
                "phases": phases,
                "risk_mitigation": ["backup database", "gradual rollout", "monitor metrics"],
                "estimated_downtime": "0 minutes",
                "rollback_time": "5-10 minutes"
            }
        }

    def _parse_llm_deployment_strategy(
        self,
        llm_response: str,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        testing_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Parse LLM response para extraer estrategia de deployment."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                # Validate structure
                if "deployment_strategy" in result:
                    strategy = result["deployment_strategy"]

                    # Normalize
                    normalized_strategy = {
                        "deployment_strategy": {
                            "approach": strategy.get("approach", "standard"),
                            "phases": strategy.get("phases", []),
                            "risk_mitigation": strategy.get("risk_mitigation", []),
                            "estimated_downtime": strategy.get("estimated_downtime", "0 minutes"),
                            "rollback_time": strategy.get("rollback_time", "5-10 minutes")
                        }
                    }

                    return normalized_strategy

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM deployment strategy as JSON: {e}")

        # Fallback to heuristic
        return self._generate_deployment_strategy_heuristic(issue, environment)

    def _identify_deployment_risks_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        testing_result: Dict[str, Any],
        environment: str
    ) -> List[Dict[str, Any]]:
        """Identifica riesgos de deployment usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            return self._identify_deployment_risks_heuristic(issue, environment)

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])

            prompt = f"""Identifica riesgos específicos de deployment para el siguiente feature del proyecto IACT.

**Feature**: {title}
**Environment**: {environment}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Contexto del Diseño**: {design_result.get('hld', '')[:500]}

Identifica riesgos considerando:
1. Riesgos de deployment (downtime, rollback, data loss)
2. Riesgos de integración (dependencies, services)
3. Riesgos de performance (load, response time)
4. Riesgos de seguridad (vulnerabilities, data exposure)

Responde en formato JSON:
{{
  "risks": [
    {{
      "type": "deployment|integration|performance|security",
      "severity": "critical|high|medium|low",
      "description": "descripción del riesgo",
      "mitigation": "estrategia de mitigación"
    }}
  ]
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_deployment_risks(
                llm_response, issue, design_result, testing_result
            )

        except Exception as e:
            self.logger.warning(f"LLM deployment risks identification failed: {e}, using fallback")
            return self._identify_deployment_risks_heuristic(issue, environment)

    def _identify_deployment_risks_heuristic(
        self,
        issue: Dict[str, Any],
        environment: str
    ) -> List[Dict[str, Any]]:
        """Identifica riesgos de deployment con heurísticas (fallback)."""
        risks = []
        story_points = issue.get("story_points", 0)
        technical_requirements = issue.get("technical_requirements", [])

        # Risk: Large/complex feature
        if story_points >= 8:
            risks.append({
                "type": "deployment",
                "severity": "medium",
                "description": f"Feature complejo ({story_points} story points) puede tener deployment más riesgoso",
                "mitigation": "Deployment gradual con monitoreo intensivo"
            })

        # Risk: Database changes
        if any("database" in req.lower() or "migration" in req.lower() for req in technical_requirements):
            risks.append({
                "type": "deployment",
                "severity": "high",
                "description": "Cambios de base de datos pueden causar problemas de rollback",
                "mitigation": "Backup completo antes de deployment, testear migraciones en staging"
            })

        # Risk: Production deployment
        if environment == "production":
            risks.append({
                "type": "deployment",
                "severity": "high",
                "description": "Deployment a producción requiere precauciones adicionales",
                "mitigation": "Ejecutar durante horario de baja demanda, equipo en standby"
            })

        return risks

    def _parse_llm_deployment_risks(
        self,
        llm_response: str,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        testing_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse LLM response para extraer riesgos de deployment."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                risks = result.get("risks", [])

                # Validate and normalize
                normalized_risks = []
                for risk in risks:
                    if isinstance(risk, dict) and "description" in risk:
                        normalized_risk = {
                            "type": risk.get("type", "deployment"),
                            "severity": risk.get("severity", "medium"),
                            "description": risk.get("description", ""),
                            "mitigation": risk.get("mitigation", "")
                        }
                        normalized_risks.append(normalized_risk)

                if normalized_risks:
                    return normalized_risks

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM deployment risks as JSON: {e}")

        # Fallback to heuristic
        return self._identify_deployment_risks_heuristic(issue, "staging")

    def _generate_rollback_strategy_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Genera estrategia de rollback usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            return self._generate_rollback_strategy_heuristic(issue, environment)

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])

            prompt = f"""Genera una estrategia de rollback detallada para el siguiente feature del proyecto IACT.

**Feature**: {title}
**Environment**: {environment}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Contexto del Diseño**: {design_result.get('hld', '')[:500]}

Considera:
1. Triggers para activar rollback (cuando hacer rollback)
2. Pasos específicos de rollback
3. Tiempo estimado de rollback
4. Riesgo de pérdida de datos
5. Estrategia de validación post-rollback

Responde en formato JSON:
{{
  "rollback_strategy": {{
    "triggers": ["trigger 1", "trigger 2"],
    "steps": ["paso 1", "paso 2"],
    "estimated_time": "X minutes",
    "data_loss_risk": "low|medium|high",
    "validation_steps": ["validación 1", "validación 2"]
  }}
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_rollback_strategy(llm_response, issue, design_result, environment)

        except Exception as e:
            self.logger.warning(f"LLM rollback strategy generation failed: {e}, using fallback")
            return self._generate_rollback_strategy_heuristic(issue, environment)

    def _generate_rollback_strategy_heuristic(
        self,
        issue: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Genera estrategia de rollback con heurísticas (fallback)."""
        return {
            "rollback_strategy": {
                "triggers": [
                    "Health check fails after deployment",
                    "Critical errors in logs",
                    "Performance degradation > 50%"
                ],
                "steps": [
                    "Stop application services",
                    "Restore code to previous version",
                    "Reverse database migrations if needed",
                    "Restart services",
                    "Verify rollback"
                ],
                "estimated_time": "5-10 minutes",
                "data_loss_risk": "low",
                "validation_steps": [
                    "Health check passes",
                    "No errors in logs",
                    "Core functionality works"
                ]
            }
        }

    def _parse_llm_rollback_strategy(
        self,
        llm_response: str,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Parse LLM response para extraer estrategia de rollback."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                if "rollback_strategy" in result:
                    strategy = result["rollback_strategy"]

                    # Normalize
                    normalized_strategy = {
                        "rollback_strategy": {
                            "triggers": strategy.get("triggers", []),
                            "steps": strategy.get("steps", []),
                            "estimated_time": strategy.get("estimated_time", "5-10 minutes"),
                            "data_loss_risk": strategy.get("data_loss_risk", "low"),
                            "validation_steps": strategy.get("validation_steps", [])
                        }
                    }

                    return normalized_strategy

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM rollback strategy as JSON: {e}")

        # Fallback to heuristic
        return self._generate_rollback_strategy_heuristic(issue, environment)

    def _generate_monitoring_strategy_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Genera estrategia de monitoring usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            return self._generate_monitoring_strategy_heuristic(issue, environment)

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])

            prompt = f"""Genera una estrategia de monitoring post-deployment para el siguiente feature del proyecto IACT.

**Feature**: {title}
**Environment**: {environment}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Contexto del Diseño**: {design_result.get('hld', '')[:500]}

Considera:
1. Métricas clave a monitorear
2. Umbrales de alertas (critical, warning)
3. Duración del monitoring intensivo
4. Herramientas de monitoring recomendadas
5. Frecuencia de checks

Responde en formato JSON:
{{
  "monitoring_strategy": {{
    "key_metrics": ["metric 1", "metric 2"],
    "alert_thresholds": {{
      "error_rate": "X%",
      "response_time": "Y seconds"
    }},
    "monitoring_duration": "X hours intensive, Y hours regular",
    "tools": ["tool 1", "tool 2"],
    "check_frequency": "every X minutes"
  }}
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_monitoring_strategy(llm_response, issue, design_result, environment)

        except Exception as e:
            self.logger.warning(f"LLM monitoring strategy generation failed: {e}, using fallback")
            return self._generate_monitoring_strategy_heuristic(issue, environment)

    def _generate_monitoring_strategy_heuristic(
        self,
        issue: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Genera estrategia de monitoring con heurísticas (fallback)."""
        return {
            "monitoring_strategy": {
                "key_metrics": [
                    "response_time",
                    "error_rate",
                    "database_connections",
                    "cpu_usage",
                    "memory_usage"
                ],
                "alert_thresholds": {
                    "error_rate": "5%",
                    "response_time": "2 seconds"
                },
                "monitoring_duration": "2 hours intensive, 24 hours regular",
                "tools": ["application logs", "database monitoring", "health checks"],
                "check_frequency": "every 15 minutes for first 2 hours"
            }
        }

    def _parse_llm_monitoring_strategy(
        self,
        llm_response: str,
        issue: Dict[str, Any],
        design_result: Dict[str, Any],
        environment: str
    ) -> Dict[str, Any]:
        """Parse LLM response para extraer estrategia de monitoring."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                if "monitoring_strategy" in result:
                    strategy = result["monitoring_strategy"]

                    # Normalize
                    normalized_strategy = {
                        "monitoring_strategy": {
                            "key_metrics": strategy.get("key_metrics", []),
                            "alert_thresholds": strategy.get("alert_thresholds", {}),
                            "monitoring_duration": strategy.get("monitoring_duration", "24 hours"),
                            "tools": strategy.get("tools", []),
                            "check_frequency": strategy.get("check_frequency", "every 15 minutes")
                        }
                    }

                    return normalized_strategy

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM monitoring strategy as JSON: {e}")

        # Fallback to heuristic
        return self._generate_monitoring_strategy_heuristic(issue, environment)

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Guardrails especificos para Deployment phase."""
        errors = []

        # Validar que se genero deployment plan
        if "deployment_plan" not in output_data or not output_data["deployment_plan"]:
            errors.append("No se genero deployment plan")

        # Validar que se genero rollback plan
        if "rollback_plan" not in output_data or not output_data["rollback_plan"]:
            errors.append("No se genero rollback plan")

        # Validar que se generaron checklists
        if "pre_deployment_checklist" not in output_data:
            errors.append("No se genero pre-deployment checklist")

        if "post_deployment_checklist" not in output_data:
            errors.append("No se genero post-deployment checklist")

        # Validar que deployment plan menciona backup
        if "deployment_plan" in output_data:
            plan_content = output_data["deployment_plan"].lower()
            if "backup" not in plan_content:
                errors.append("Deployment plan debe mencionar backup de base de datos")

        return errors
