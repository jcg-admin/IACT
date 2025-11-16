---
id: TASK-025-dora-ai-capability-6
tipo: documentacion_ai_capabilities
categoria: ai_capabilities
prioridad: P2
story_points: 8
estado: completado
fecha_inicio: 2025-11-07
fecha_fin: 2025-11-07
asignado: backend-lead + ai-lead
relacionados: ["TASK-026", "TASK-024"]
date: 2025-11-13
---

# TASK-025: DORA 2025 AI Capability 6 - AI-accessible Internal Data

Implementacion de DORA 2025 AI Capability 6: Making internal data accessible to AI systems.

## Objetivo

Exponer datos internos del sistema de manera estructurada y accesible para AI agents, permitiendo:
- Data discovery automatizada
- Query programatica de datos
- Analisis AI-driven
- Decision making basado en datos
- Self-service data access

## Técnicas de Prompt Engineering para Agente

Las siguientes técnicas deben aplicarse al ejecutar esta tarea con un agente:

1. **RAG** (search_optimization_techniques.py)
 - Implementar Retrieval Augmented Generation para data catalog

2. **Expert Prompting** (specialized_techniques.py)
 - Aplicar conocimiento experto de AI/ML y prompt engineering

3. **Meta-prompting** (structuring_techniques.py)
 - Generar prompts dinamicos para diferentes casos de uso

4. **Task Decomposition** (structuring_techniques.py)
 - Dividir capabilities AI en componentes reutilizables

5. **Few-Shot** (fundamental_techniques.py)
 - Usar ejemplos para entrenar modelos de AI

Agente recomendado: FeatureAgent o SDLCDesignAgent
## DORA 2025 AI Capability 6

### Definition

"Organizations make internal data accessible to AI systems through structured APIs, data catalogs, and AI-friendly formats, enabling AI agents to discover, query, and analyze organizational data autonomously."

### Key Requirements

1. **Data Catalog**: Comprehensive catalog of available datasets
2. **Structured APIs**: RESTful APIs with clear schemas
3. **AI-friendly Formats**: JSON/YAML with metadata
4. **Query Interface**: Flexible querying capabilities
5. **Documentation**: Clear API documentation for AI consumption

## Arquitectura Implementada

```
AI Agent
 ↓
 ├─ GET /api/dora/data-catalog/
 │ └─ Returns: Complete catalog with 4 datasets
 │
 ├─ GET /api/dora/data-catalog/dora-metrics/
 │ └─ Returns: DORA metrics data (filtered)
 │
 ├─ GET /api/dora/data-catalog/deployment-cycles/
 │ └─ Returns: Deployment cycle information
 │
 └─ GET /api/dora/data-catalog/aggregated-stats/
 └─ Returns: Aggregated statistics

Response Format: JSON with:
- Schema information
- Query parameters
- Example queries
- Metadata
- Actual data
```

## Implementacion

### 1. Data Catalog Engine

**File:** `dora_metrics/data_catalog.py`

**Classes:**
- `DataCatalog`: Catalog de todos los datasets disponibles
- `DataQueryEngine`: Motor de queries para AI agents

**Datasets Catalogados:**

1. **dora_metrics**: Core DORA performance metrics
 - Fields: cycle_id, feature_id, phase_name, decision, duration_seconds, created_at
 - Type: time_series
 - Update frequency: real_time

2. **deployment_cycles**: Complete deployment cycle information
 - Fields: cycle_id, feature_id, start_time, end_time, total_duration_hours, phases_count, failed
 - Type: aggregated
 - Update frequency: real_time

3. **performance_metrics**: System performance and health
 - Fields: metric_name, value, timestamp
 - Type: time_series
 - Update frequency: 5_minutes

4. **quality_metrics**: Data quality scores
 - Fields: dataset_name, quality_score, null_rate, anomaly_rate, schema_violations, checked_at
 - Type: aggregated
 - Update frequency: daily

### 2. API Endpoints

#### GET /api/dora/data-catalog/

Returns complete data catalog.

**Response:**
```json
{
 "catalog_version": "1.0.0",
 "generated_at": "2025-11-07T10:30:00Z",
 "total_datasets": 4,
 "datasets": [
 {
 "dataset_id": "dora_metrics",
 "name": "DORA Metrics",
 "description": "Core DORA performance metrics",
 "type": "time_series",
 "update_frequency": "real_time",
 "schema": {
 "fields": [
 {
 "name": "cycle_id",
 "type": "string",
 "description": "Unique deployment cycle identifier",
 "required": true,
 "example": "cycle-2025-001"
 },
 ...
 ]
 },
 "api_endpoint": "/api/dora/data-catalog/dora-metrics/",
 "query_parameters": [...],
 "example_queries": [...]
 },
 ...
 ]
}
```

#### GET /api/dora/data-catalog/dora-metrics/

Query DORA metrics data.

**Query Parameters:**
- `days` (integer, default: 30): Number of days to query
- `phase_name` (string, optional): Filter by phase
- `feature_id` (string, optional): Filter by feature

**Example:**
```bash
GET /api/dora/data-catalog/dora-metrics/?days=7&phase_name=deployment
```

**Response:**
```json
{
 "query": {
 "days": 7,
 "phase_name": "deployment",
 "feature_id": null,
 "executed_at": "2025-11-07T10:30:00Z"
 },
 "metadata": {
 "total_records": 25,
 "date_range": {
 "start": "2025-10-31T10:30:00Z",
 "end": "2025-11-07T10:30:00Z"
 }
 },
 "data": [
 {
 "cycle_id": "cycle-001",
 "feature_id": "FEAT-123",
 "phase_name": "deployment",
 "decision": "approved",
 "duration_seconds": 1200.5,
 "created_at": "2025-11-07T09:00:00Z"
 },
 ...
 ]
}
```

#### GET /api/dora/data-catalog/deployment-cycles/

Query deployment cycles.

**Query Parameters:**
- `days` (integer, default: 30): Number of days to query
- `failed_only` (boolean, default: false): Show only failed deployments

**Example:**
```bash
GET /api/dora/data-catalog/deployment-cycles/?days=30&failed_only=true
```

**Response:**
```json
{
 "query": {
 "days": 30,
 "failed_only": true,
 "executed_at": "2025-11-07T10:30:00Z"
 },
 "metadata": {
 "total_cycles": 5,
 "failed_cycles": 5
 },
 "data": [
 {
 "cycle_id": "cycle-002",
 "feature_id": "FEAT-124",
 "start_time": "2025-11-01T08:00:00Z",
 "end_time": "2025-11-01T12:00:00Z",
 "total_duration_hours": 4.0,
 "phases_count": 5,
 "failed": true
 },
 ...
 ]
}
```

#### GET /api/dora/data-catalog/aggregated-stats/

Get aggregated statistics.

**Query Parameters:**
- `days` (integer, default: 30): Number of days to analyze

**Example:**
```bash
GET /api/dora/data-catalog/aggregated-stats/?days=30
```

**Response:**
```json
{
 "period": {
 "days": 30,
 "start_date": "2025-10-08T10:30:00Z",
 "end_date": "2025-11-07T10:30:00Z"
 },
 "total_metrics": 150,
 "by_phase": {
 "development": 50,
 "testing": 40,
 "deployment": 30,
 "incident": 5,
 "recovery": 5
 },
 "by_decision": {
 "approved": 120,
 "rejected": 10,
 "rollback": 5,
 "resolved": 5
 },
 "duration_stats": {
 "avg_seconds": 1800.0,
 "min_seconds": 300,
 "max_seconds": 7200,
 "avg_hours": 0.5
 },
 "deployment_frequency": 30,
 "change_failure_rate": 16.67,
 "lead_time_hours": 2.5,
 "mttr_hours": 1.0
}
```

## AI Agent Usage Examples

### Example 1: Data Discovery

```python
import requests

# Discover available datasets
response = requests.get('http://localhost:8000/api/dora/data-catalog/')
catalog = response.json()

print(f"Available datasets: {catalog['total_datasets']}")
for dataset in catalog['datasets']:
 print(f" - {dataset['name']}: {dataset['description']}")
 print(f" API: {dataset['api_endpoint']}")
```

### Example 2: Query DORA Metrics

```python
# Query last 7 days of deployment metrics
params = {
 'days': 7,
 'phase_name': 'deployment'
}
response = requests.get(
 'http://localhost:8000/api/dora/data-catalog/dora-metrics/',
 params=params
)
data = response.json()

print(f"Total records: {data['metadata']['total_records']}")
for metric in data['data']:
 print(f" Cycle {metric['cycle_id']}: {metric['duration_seconds']}s")
```

### Example 3: Analyze Failures

```python
# Query failed deployments
params = {
 'days': 30,
 'failed_only': True
}
response = requests.get(
 'http://localhost:8000/api/dora/data-catalog/deployment-cycles/',
 params=params
)
data = response.json()

print(f"Failed deployments: {data['metadata']['failed_cycles']}")
for cycle in data['data']:
 print(f" {cycle['cycle_id']}: {cycle['total_duration_hours']}h")
```

### Example 4: Get Aggregated Stats

```python
# Get 30-day aggregated statistics
response = requests.get(
 'http://localhost:8000/api/dora/data-catalog/aggregated-stats/',
 params={'days': 30}
)
stats = response.json()

print(f"Deployment Frequency: {stats['deployment_frequency']}")
print(f"Change Failure Rate: {stats['change_failure_rate']}%")
print(f"Lead Time: {stats['lead_time_hours']}h")
print(f"MTTR: {stats['mttr_hours']}h")
```

## AI-Friendly Features

### 1. Self-Describing APIs

Every endpoint includes:
- Complete schema information
- Field descriptions and types
- Example values
- Query parameters documentation
- Example queries

### 2. Metadata-Rich Responses

Every response includes:
- Query parameters used
- Execution timestamp
- Total record count
- Date ranges
- Additional context

### 3. Flexible Querying

- Time-based filtering (days, hours)
- Field-based filtering (phase, feature)
- Boolean filters (failed_only)
- Aggregation options

### 4. Consistent Format

All responses follow consistent structure:
```json
{
 "query": {...},
 "metadata": {...},
 "data": [...]
}
```

## Testing

### Manual Testing

```bash
# Test catalog endpoint
curl http://localhost:8000/api/dora/data-catalog/ | jq

# Test metrics query
curl "http://localhost:8000/api/dora/data-catalog/dora-metrics/?days=7" | jq

# Test deployment cycles
curl "http://localhost:8000/api/dora/data-catalog/deployment-cycles/?failed_only=true" | jq

# Test aggregated stats
curl "http://localhost:8000/api/dora/data-catalog/aggregated-stats/?days=30" | jq
```

### Automated Testing

Integration tests included in `tests/integration/test_dora_metrics_integration.py`.

## Benefits

### For AI Agents

1. **Autonomous Discovery**: AI agents can discover available data without human intervention
2. **Programmatic Access**: Structured APIs enable automated querying
3. **Rich Metadata**: Schema information enables validation and type checking
4. **Flexible Queries**: Agents can filter and aggregate data as needed
5. **Self-Documentation**: APIs are self-describing

### For Organization

1. **Data Democratization**: Internal data accessible to AI systems
2. **Automation**: Enable AI-driven decision making
3. **Insights**: AI agents can analyze patterns and trends
4. **Efficiency**: Reduce manual data extraction efforts
5. **Scalability**: Standard interfaces for data access

## Compliance

### RNF-002
[OK] **100% COMPLIANT**
- No external dependencies
- Self-hosted APIs
- Uses existing MySQL database
- Django-native implementation

### Security

- Rate limiting applied (100/min, 1000/hour)
- Authentication required for sensitive endpoints
- No PII exposed
- Audit logging enabled

### Performance

- Efficient database queries with indices
- Pagination support (future enhancement)
- Caching strategies (future enhancement)
- Response time < 500ms

## Future Enhancements

### Phase 2 Features

1. **GraphQL API**: More flexible querying for AI agents
2. **Real-time Streaming**: WebSocket support for live data
3. **Advanced Filtering**: Complex query DSL
4. **Pagination**: Cursor-based pagination for large datasets
5. **Caching**: Redis caching for frequently accessed data
6. **Data Versioning**: Track data schema versions

### Phase 3 Features

1. **Natural Language Queries**: AI agents query using natural language
2. **Automatic Schema Evolution**: Self-updating schemas
3. **AI-Driven Insights**: Pre-computed insights for AI agents
4. **Cross-Dataset Joins**: Query across multiple datasets
5. **Data Lineage**: Track data provenance and transformations

## Maintenance

### Update Schedule
- **Schema changes**: Document immediately
- **New datasets**: Add to catalog within 1 week
- **API changes**: Follow versioning policy (TASK-031)

### Ownership
- **Primary**: backend-lead
- **Secondary**: ai-lead
- **Review**: arquitecto-senior

## Success Metrics

### Capability Metrics
- [OK] 4 datasets cataloged
- [OK] 4 API endpoints implemented
- [OK] Self-describing schemas
- [OK] AI-friendly JSON format
- [OK] Query flexibility

### Usage Metrics (Future)
- API calls per day
- Unique AI agents using APIs
- Average query complexity
- Response time p95
- Error rate

## DORA 2025 Compliance

### AI Capability 6 Checklist

- [OK] Data catalog implemented
- [OK] Structured APIs with schemas
- [OK] AI-friendly JSON format
- [OK] Query interfaces available
- [OK] Self-describing endpoints
- [OK] Example queries provided
- [OK] Metadata-rich responses
- [OK] Flexible filtering
- [OK] Documentation complete

**Status:** [OK] **COMPLIANT** (100%)

---

**VERSION:** 1.0.0
**ESTADO:** COMPLETADO
**STORY POINTS:** 8 SP
**FECHA:** 2025-11-07
**DORA 2025 AI CAPABILITY:** 6/7 (86%)
