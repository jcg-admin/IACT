# RT-016: Security and Threat Mitigation Standards

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Security
**Relación**:
- Implementa [ADR-057: Trustworthy AI Architecture](../../../gobernanza/adr/ADR-057-trustworthy-ai-architecture.md)

---

## Propósito

Defines security standards and threat mitigation requirements to ensure AI agents operate safely and securely.

---

## Threat Detection Standards

### Task Injection
| Standard | Requirement | Enforcement |
|----------|-------------|-------------|
| Detection Rate | > 95% | Pattern matching + ML |
| False Positive Rate | < 5% | Regular pattern review |
| Response Time | < 100ms | Synchronous validation |
| Sanitization | 100% of inputs | Pre-processing filter |

**Code**:
```python
def enforce_injection_detection():
    detector = ThreatDetector()

    if detector.detect_task_injection(user_input):
        logger.security(f"Injection attempt blocked: {user_input[:100]}")
        return sanitize_input(user_input)
    return user_input
```

### Access Control
| Standard | Requirement |
|----------|-------------|
| Permission Check | 100% of resource access |
| Audit Logging | All access attempts logged |
| Deny-by-Default | No access without explicit permission |
| Least Privilege | Minimum permissions required |

### Resource Quotas
| Resource | Quota | Enforcement |
|----------|-------|-------------|
| API Calls | 1000/hour/agent | Rate limiter |
| Token Usage | 1M tokens/day | Counter + block |
| Compute Time | 10 CPU-hours/day | Timer + throttle |
| Memory | 4GB max | Memory monitor |

---

## Human-in-the-Loop Standards

| Action Risk | Approval Required | Timeout | Approvers |
|-------------|-------------------|---------|-----------|
| CRITICAL (> $10K) | Yes | 120s | 2 |
| HIGH ($1K-$10K) | Yes | 60s | 1 |
| MEDIUM | Quick approval | 10s | 1 |
| LOW | No | N/A | 0 |

**Code**:
```python
def enforce_hitl():
    risk = classify_risk(action)

    if risk == RiskLevel.CRITICAL:
        approval1 = request_approval(timeout=120)
        approval2 = request_approval(timeout=120, approver=2)
        return approval1.approved and approval2.approved
    elif risk == RiskLevel.HIGH:
        return request_approval(timeout=60).approved
    return True
```

---

## Audit Logging Standards

| Event Type | Logging Required | Retention |
|------------|------------------|-----------|
| HIGH/CRITICAL actions | 100% | 7 years |
| Access violations | 100% | 3 years |
| Security events | 100% | 5 years |
| All actions | 100% | 1 year |

---

## Circuit Breaker Standards

| Metric | Threshold | Action |
|--------|-----------|--------|
| Failure Rate | 50% in 5 min | Open circuit |
| Consecutive Failures | 5 | Open circuit |
| Recovery Time | 60s | Half-open test |
| Success Rate for Close | 90% in 2 min | Close circuit |

---

## Metrics

```yaml
security_metrics:
  - name: "Injection Detection Rate"
    target: "> 95%"
  - name: "Access Violations"
    target: "< 0.1%"
  - name: "HITL Approval Rate"
    target: "100% for HIGH+"
  - name: "Audit Completeness"
    target: "100%"
  - name: "MTTD"
    target: "< 5 min"
  - name: "MTTR"
    target: "< 15 min"
```

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
