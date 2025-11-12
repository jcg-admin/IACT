# Integration Tests Suite

Comprehensive integration tests for IACT DORA metrics system.

## Overview

This test suite validates the integration between:
- **Layer 1**: MySQL metrics storage
- **Layer 2**: JSON application logs
- **Layer 3**: Cassandra infrastructure logs
- **DORA Dashboard**: Web interface
- **ETL Pipeline**: Data extraction, transformation, loading
- **Alerting System**: Django signals-based alerts
- **Data Quality Framework**: Validation and anomaly detection

## Test Categories

### 1. DORA Metrics API Integration (`DORAMetricsAPIIntegrationTest`)
- API endpoint responses (JSON format)
- DORA summary calculations
- Performance classification (Elite/High/Medium/Low)
- Dashboard page rendering
- Chart data endpoints
- Rate limiting enforcement
- Time-based filtering
- Change failure detection
- MTTR calculations

### 2. Observability Layers (`ObservabilityLayersIntegrationTest`)
- Layer 1: MySQL metrics storage
- Layer 2: JSON logging format validation
- Layer 3: Cassandra logs (placeholder for future)

### 3. ETL Pipeline (`ETLPipelineIntegrationTest`)
- Extract phase validation
- Transform phase schema validation
- Load phase database storage

### 4. Data Quality (`DataQualityIntegrationTest`)
- Schema validation (Pydantic)
- Data quality score calculation
- Anomaly detection (IQR method)

### 5. Alerting System (`AlertingSystemIntegrationTest`)
- Critical alert signals
- Warning alert signals

### 6. Performance (`PerformanceIntegrationTest`)
- Bulk metric creation (1000 records < 5s)
- API response times (< 1s)

## Running Tests

### Run All Integration Tests
```bash
cd api/callcentersite
pytest tests/integration/ -v
```

### Run with Coverage
```bash
pytest tests/integration/ --cov=dora_metrics --cov=callcentersite --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/integration/test_dora_metrics_integration.py::DORAMetricsAPIIntegrationTest -v
```

### Run Specific Test Method
```bash
pytest tests/integration/test_dora_metrics_integration.py::DORAMetricsAPIIntegrationTest::test_dora_summary_calculation -v
```

### Run with Integration Markers
```bash
pytest -m integration -v
```

### Run Parallel (Faster)
```bash
pytest tests/integration/ -n auto
```

### Run with Detailed Output
```bash
pytest tests/integration/ -vv --tb=short
```

## Test Requirements

### Dependencies
```bash
pip install pytest pytest-django pytest-cov pytest-xdist pydantic numpy
```

### Database Setup
Integration tests use Django's test database. Ensure:
- MySQL is running
- Django settings are configured correctly
- Migrations are up to date

### Test Data
Tests create their own test data using Django fixtures and `setUp()` methods. No external data required.

## Coverage Goals

- **Target**: ≥80% code coverage
- **Critical paths**: 100% coverage
- **Integration points**: All tested

## CI/CD Integration

### GitHub Actions (Example)
```yaml
- name: Run Integration Tests
  run: |
    cd api/callcentersite
    pytest tests/integration/ --cov --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Performance Benchmarks

| Test | Target | Current |
|------|--------|---------|
| Bulk create 1000 metrics | < 5s | ~2s |
| API response time | < 1s | ~200ms |
| Dashboard load | < 2s | ~1.5s |

## Troubleshooting

### Test Failures

**Rate limit test fails:**
- Ensure rate limiting middleware is enabled
- Check `RATELIMIT_ENABLE = True` in settings

**Database connection errors:**
- Verify MySQL is running: `systemctl status mysql`
- Check credentials in `settings.py`

**Import errors:**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check PYTHONPATH includes project root

### Debug Mode

Run with pytest debug flag:
```bash
pytest tests/integration/ -vv --pdb
```

## Extending Tests

### Adding New Test Class
```python
class MyNewIntegrationTest(TestCase):
    """Test my new feature integration."""

    def setUp(self):
        # Setup test data
        pass

    def test_my_feature(self):
        # Test logic
        self.assertTrue(True)
```

### Adding Test Fixtures
```python
@pytest.fixture
def test_metrics():
    """Fixture providing test metrics."""
    return DORAMetric.objects.create(...)
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Cleanup**: Use `setUp()` and `tearDown()` properly
3. **Data**: Create minimal test data needed
4. **Assertions**: Use specific assertions (not just `assertTrue`)
5. **Performance**: Keep tests fast (< 5s each)
6. **Documentation**: Document complex test logic

## Compliance

[OK] **RNF-002 Compliant**
- No external dependencies (Redis, etc.)
- Self-hosted testing infrastructure
- Uses Django test database

## Maintenance

- **Update frequency**: After each feature addition
- **Review schedule**: Weekly during active development
- **Owner**: backend-lead + qa-lead
