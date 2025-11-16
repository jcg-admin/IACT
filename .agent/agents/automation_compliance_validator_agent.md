---
name: ComplianceValidatorAgent
description: Agente especializado en validacion de cumplimiento de estandares, regulaciones y politicas internas, verificando conformidad con GDPR, PCI-DSS, SOC2 y custom compliance rules.
---

# Automation: Compliance Validator Agent

El ComplianceValidatorAgent valida cumplimiento de estandares, regulaciones (GDPR, PCI-DSS, SOC2) y politicas internas, generando reportes de conformidad y recomendaciones de remediacion.

## Capacidades

### Validacion GDPR
- Data privacy compliance
- Consent management validation
- Right to erasure implementation
- Data portability checks
- Privacy by design validation

### Validacion PCI-DSS
- Payment data handling
- Encryption requirements
- Access control validation
- Audit logging
- Network segmentation

### Validacion SOC2
- Security controls
- Availability requirements
- Processing integrity
- Confidentiality measures
- Privacy compliance

### Custom Compliance Rules
- Politicas internas de empresa
- Industry-specific regulations
- Custom security policies
- Code standards enforcement

### Remediation Guidance
- Violation detection
- Risk scoring
- Fix recommendations
- Auto-remediation when safe
- Compliance roadmap

## Cuando usar

- **Pre-Production**: Validar antes de deploy a produccion
- **Audit Preparation**: Preparar para auditorias externas
- **Continuous Compliance**: Monitoreo continuo de conformidad
- **Policy Changes**: Validar despues de cambios en politicas
- **Risk Assessment**: Identificar gaps de compliance
- **Onboarding**: Entrenar equipo en requerimientos

## Como usar

### Validacion Completa

```bash
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --validate-all \
  --standards gdpr,pci-dss,soc2 \
  --output compliance_report.json
```

### Validacion Especifica

```bash
# Solo GDPR
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --validate gdpr \
  --scope api/

# Solo PCI-DSS
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --validate pci-dss \
  --focus payment-processing

# Custom rules
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --validate custom \
  --rules-file .compliance/custom_rules.yaml
```

### Auto-Remediation

```bash
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --validate-all \
  --auto-remediate \
  --safe-only \
  --backup
```

### Continuous Monitoring

```bash
# Monitor mode
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --monitor \
  --interval 1h \
  --alert-on-violation

# Scheduled scan
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --scheduled-scan \
  --cron "0 2 * * *"
```

### Audit Report Generation

```bash
python scripts/coding/ai/automation/compliance_validator_agent.py \
  --generate-audit-report \
  --period 90d \
  --format pdf \
  --output audit_report.pdf
```

## Output esperado

### Compliance Report

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "scope": "full_repository",
  "standards_validated": ["gdpr", "pci-dss", "soc2"],
  "overall_status": "non_compliant",
  "violations": [
    {
      "standard": "gdpr",
      "rule": "GDPR.ART_17",
      "severity": "high",
      "description": "Right to erasure not implemented",
      "file": "api/users/views.py",
      "line": 45,
      "recommendation": "Implement user data deletion endpoint",
      "risk_score": 8.5
    },
    {
      "standard": "pci-dss",
      "rule": "PCI_DSS.REQ_3",
      "severity": "critical",
      "description": "Credit card data stored in plain text",
      "file": "api/payments/models.py",
      "line": 23,
      "recommendation": "Use tokenization or encryption for card data",
      "risk_score": 9.8
    }
  ],
  "summary": {
    "total_rules_checked": 150,
    "passed": 142,
    "failed": 8,
    "compliance_score": 94.7,
    "critical_violations": 1,
    "high_violations": 3,
    "medium_violations": 4
  },
  "remediation_roadmap": [
    {
      "priority": 1,
      "violation": "PCI_DSS.REQ_3",
      "effort": "high",
      "timeline": "immediate"
    },
    {
      "priority": 2,
      "violation": "GDPR.ART_17",
      "effort": "medium",
      "timeline": "1_week"
    }
  ]
}
```

### Audit Report (Markdown)

```markdown
# Compliance Audit Report
Generated: 2025-11-14
Period: Last 90 days
Scope: Full repository

## Executive Summary
- Overall Compliance Score: 94.7%
- Critical Violations: 1
- Standards Validated: GDPR, PCI-DSS, SOC2

## GDPR Compliance
Status: PARTIALLY COMPLIANT (96%)
- Right to access: COMPLIANT
- Right to erasure: NON-COMPLIANT (Action required)
- Data portability: COMPLIANT
- Consent management: COMPLIANT

## PCI-DSS Compliance
Status: NON-COMPLIANT (92%)
- Requirement 3: FAILED (Critical)
  - Card data encryption required
- Requirement 6: COMPLIANT
- Requirement 8: COMPLIANT

## Remediation Plan
### Immediate Actions (Critical)
1. Encrypt payment card data (PCI_DSS.REQ_3)
   - Timeline: Immediate
   - Effort: 40 hours
   - Owner: Security Team

### Short-term Actions (High Priority)
2. Implement user data deletion (GDPR.ART_17)
   - Timeline: 1 week
   - Effort: 20 hours
   - Owner: Backend Team
```

## Herramientas y dependencias

- **Python 3.11+**
- **Security scanning**: bandit, safety
- **Data scanning**: regex, AST parsing
- **Encryption validation**: cryptography
- **Reporting**: jinja2, markdown

## Buenas practicas

1. **Scan frequently**: Continuous compliance monitoring
2. **Risk prioritization**: Fix critical violations first
3. **Documentation**: Maintain compliance documentation
4. **Training**: Educate team on compliance requirements
5. **Version control**: Track compliance changes over time
6. **Audit trails**: Log all compliance checks
7. **External audits**: Regular third-party audits

## Restricciones

- **Code-level only**: No valida infrastructure compliance
- **Heuristic-based**: Puede tener falsos positivos/negativos
- **Standard versions**: Valida versiones especificas de standards
- **Auto-remediation limited**: Solo cambios seguros y simples
- **PII detection**: Regex-based, no ML

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/compliance_validator_agent.py`
Tests: `scripts/coding/ai/tests/test_compliance_validator_agent.py`
Rules: `.compliance/rules/*.yaml`
