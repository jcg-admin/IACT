"""
SDLCDesignAgent - Fase 3: System Design

Responsabilidad: Generar diseno de sistema (HLD/LLD), ADRs, y diagramas
para features aprobados en fase de Feasibility.

Inputs:
- feasibility_result (dict): Output de SDLCFeasibilityAgent
- issue (dict): Issue del SDLCPlannerAgent
- project_context (str): Contexto arquitectonico del proyecto

Outputs:
- HLD (High-Level Design) document
- LLD (Low-Level Design) document
- ADRs (Architecture Decision Records) si aplica
- Diagramas Mermaid (arquitectura, secuencia, componentes)
- Design review checklist
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

# Design method constants
DESIGN_METHOD_LLM = "llm"
DESIGN_METHOD_HEURISTIC = "heuristic"


class SDLCDesignAgent(SDLCAgent):
    """
    Agente para la fase de System Design del SDLC.

    Genera documentacion de diseno completa: HLD, LLD, ADRs, diagramas.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCDesignAgent",
            phase="design",
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
        """Valida que exista feasibility result e issue."""
        errors = []

        if "feasibility_result" not in input_data:
            errors.append("Falta 'feasibility_result' en input (del SDLCFeasibilityAgent)")

        if "issue" not in input_data:
            errors.append("Falta 'issue' en input (del SDLCPlannerAgent)")

        # Validar que feasibility fue GO o REVIEW
        if "feasibility_result" in input_data:
            decision = input_data["feasibility_result"].get("decision", "")
            if decision == "no-go":
                errors.append("No se puede disenar feature con decision NO-GO. Resolver blockers primero.")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la fase de System Design.

        Args:
            input_data: {
                "issue": dict,  # Output de SDLCPlannerAgent
                "feasibility_result": dict,  # Output de SDLCFeasibilityAgent
                "project_context": str
            }

        Returns:
            Dict con HLD, LLD, ADRs, diagramas, design review checklist
        """
        issue = input_data["issue"]
        feasibility_result = input_data["feasibility_result"]
        project_context = input_data.get("project_context", "")

        self.logger.info(f"Generando diseno para: {issue.get('issue_title', 'Unknown')}")

        # Generar HLD (High-Level Design)
        hld = self._generate_hld(issue, feasibility_result, project_context)

        # Generar LLD (Low-Level Design)
        lld = self._generate_lld(issue, hld)

        # Generar ADRs si hay decisiones arquitectonicas
        adrs = self._generate_adrs(issue, hld)

        # Generar diagramas Mermaid
        diagrams = self._generate_diagrams(issue, hld, lld)

        # Generar design review checklist
        review_checklist = self._generate_review_checklist(hld, lld, adrs)

        # Guardar artefactos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts = []

        hld_path = self.save_artifact(hld, f"HLD_{timestamp}.md")
        artifacts.append(str(hld_path))

        lld_path = self.save_artifact(lld, f"LLD_{timestamp}.md")
        artifacts.append(str(lld_path))

        if adrs:
            for i, adr in enumerate(adrs, 1):
                adr_path = self.save_artifact(adr, f"ADR_{timestamp}_{i:03d}.md")
                artifacts.append(str(adr_path))

        diagrams_doc = self._format_diagrams_document(diagrams)
        diagrams_path = self.save_artifact(diagrams_doc, f"DIAGRAMS_{timestamp}.md")
        artifacts.append(str(diagrams_path))

        review_path = self.save_artifact(review_checklist, f"DESIGN_REVIEW_CHECKLIST_{timestamp}.md")
        artifacts.append(str(review_path))

        # Crear resultado de fase
        phase_result = self.create_phase_result(
            decision="go",  # Design phase siempre es GO si llego aqui
            confidence=0.9,
            artifacts=artifacts,
            recommendations=[
                "Diseno completo generado",
                "Revisar HLD con arquitecto senior",
                "Validar LLD con equipo de desarrollo",
                "Aprobar ADRs con stakeholders antes de implementar"
            ],
            next_steps=[
                "Design review meeting con equipo",
                "Refinar detalles tecnicos si es necesario",
                "Proceder con Implementation phase (TDD)"
            ]
        )

        return {
            "hld": hld,
            "hld_path": str(hld_path),
            "lld": lld,
            "lld_path": str(lld_path),
            "adrs": adrs,
            "diagrams": diagrams,
            "diagrams_path": str(diagrams_path),
            "review_checklist": review_checklist,
            "review_path": str(review_path),
            "artifacts": artifacts,
            "phase_result": phase_result
        }

    def _generate_hld(
        self,
        issue: Dict[str, Any],
        feasibility_result: Dict[str, Any],
        project_context: str
    ) -> str:
        """Genera High-Level Design document."""
        title = issue.get("issue_title", "Unknown Feature")
        technical_requirements = issue.get("technical_requirements", [])
        acceptance_criteria = issue.get("acceptance_criteria", [])
        risks = feasibility_result.get("risks", [])

        hld = f"""# High-Level Design (HLD)

**Feature**: {title}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Designer**: SDLCDesignAgent
**Version**: 1.0

---

## 1. Executive Summary

### Purpose
{self._extract_purpose(issue)}

### Scope
- In scope: {chr(10).join(f"  - {ac}" for ac in acceptance_criteria[:3])}
- Out of scope: Non-functional enhancements not in acceptance criteria

### Stakeholders
- Product Owner: Requirements approval
- Development Team: Implementation
- QA Team: Test planning
- DevOps: Deployment planning

---

## 2. System Context

### Current Architecture
{self._describe_current_architecture(project_context)}

### Proposed Changes
{self._describe_proposed_changes(technical_requirements)}

---

## 3. High-Level Architecture

### Component Overview
{self._identify_components(technical_requirements)}

### Data Flow
{self._describe_data_flow(technical_requirements)}

### External Interfaces
{self._identify_external_interfaces(technical_requirements)}

---

## 4. Technology Stack

### Backend
- Framework: Django 4.2+
- Database: MySQL (primary), PostgreSQL (secondary)
- Session Storage: MySQL (django.contrib.sessions.backends.db) - RNF-002

### Frontend
- Framework: React 18+
- State Management: Redux/Context API
- UI Library: Material-UI

### Infrastructure
- Deployment: Linux servers
- Web Server: Nginx + Gunicorn
- Monitoring: Shell scripts + MySQL logs

---

## 5. Critical Constraints (IACT)

**MUST FOLLOW**:
- NO Redis/Memcached (RNF-002)
- NO Email/SMTP (use InternalMessage)
- Sessions in MySQL only
- Cache in MySQL if needed

---

## 6. Non-Functional Requirements

### Performance
- Response time: < 2s for API calls
- Concurrent users: 100+

### Security
- Authentication: Django session-based
- Authorization: Permission-based (django.contrib.auth)
- Data validation: Django forms + serializers

### Scalability
- Horizontal scaling: Supported via load balancer
- Database: Read replicas if needed

---

## 7. Risk Mitigation

"""

        # Add risk mitigation from feasibility
        if risks:
            hld += "| Risk | Severity | Mitigation Strategy |\n"
            hld += "|------|----------|---------------------|\n"
            for risk in risks[:5]:  # Top 5 risks
                hld += f"| {risk.get('description', 'N/A')} | {risk.get('severity', 'N/A')} | {risk.get('mitigation', 'N/A')} |\n"
        else:
            hld += "No significant risks identified.\n"

        hld += f"""
---

## 8. Design Decisions

### Key Decisions
{self._identify_key_decisions(technical_requirements)}

### Trade-offs
{self._identify_tradeoffs(technical_requirements)}

---

## 9. Success Metrics

- Feature adoption: 80% of target users
- Performance: 99% requests < 2s
- Error rate: < 1%
- Test coverage: > 80%

---

## 10. Next Steps

1. Review this HLD with arquitecto-senior
2. Generate detailed LLD for implementation
3. Create ADRs for significant decisions
4. Proceed with TDD implementation

---

*Generated by SDLCDesignAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return hld

    def _generate_lld(self, issue: Dict[str, Any], hld: str) -> str:
        """Genera Low-Level Design document."""
        title = issue.get("issue_title", "Unknown Feature")
        technical_requirements = issue.get("technical_requirements", [])

        lld = f"""# Low-Level Design (LLD)

**Feature**: {title}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Designer**: SDLCDesignAgent
**Version**: 1.0
**Related HLD**: HLD_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md

---

## 1. Module Breakdown

{self._generate_module_breakdown(technical_requirements)}

---

## 2. Database Schema

### New Tables
{self._design_database_schema(technical_requirements)}

### Modified Tables
- (List any existing tables that need modifications)

### Indexes
- (List indexes needed for performance)

---

## 3. API Endpoints

{self._design_api_endpoints(technical_requirements)}

---

## 4. Data Models

```python
# models.py
{self._generate_model_code(technical_requirements)}
```

---

## 5. Business Logic

```python
# services.py or views.py
{self._generate_service_code(technical_requirements)}
```

---

## 6. Frontend Components

{self._design_frontend_components(technical_requirements)}

---

## 7. State Management

### Redux Slices / Context
{self._design_state_management(technical_requirements)}

---

## 8. Validation Rules

### Backend Validation
{self._define_validation_rules(technical_requirements)}

### Frontend Validation
- Client-side validation mirrors backend rules
- Real-time feedback for user input

---

## 9. Error Handling

### Error Codes
{self._define_error_codes(technical_requirements)}

### Error Messages
- User-friendly messages in Spanish
- Technical details logged for debugging

---

## 10. Testing Strategy

### Unit Tests
- Test all models, serializers, views
- Test all utility functions
- Coverage target: > 80%

### Integration Tests
- Test API endpoints end-to-end
- Test database transactions
- Test authentication/authorization

### E2E Tests (if applicable)
- Test critical user flows
- Test error scenarios

---

## 11. Implementation Checklist

- [ ] Create database migrations
- [ ] Implement models with tests
- [ ] Implement serializers/forms with tests
- [ ] Implement views/endpoints with tests
- [ ] Implement frontend components with tests
- [ ] Update documentation
- [ ] Code review
- [ ] QA testing

---

## 12. Deployment Notes

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Static Files
```bash
python manage.py collectstatic --no-input
```

### Service Restart
```bash
sudo systemctl restart gunicorn-iact
```

---

*Generated by SDLCDesignAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return lld

    def _generate_adrs(self, issue: Dict[str, Any], hld: str) -> List[str]:
        """Genera ADRs (Architecture Decision Records) si aplica."""
        technical_requirements = issue.get("technical_requirements", [])
        adrs = []

        # Detectar decisiones arquitectonicas significativas
        if self._has_significant_architecture_decision(technical_requirements):
            adr = self._create_adr(
                title="Almacenamiento de Sesiones en MySQL",
                context="Sistema requiere manejo de sesiones de usuario",
                decision="Usar django.contrib.sessions.backends.db (MySQL)",
                rationale=[
                    "RNF-002: Redis prohibido en IACT",
                    "MySQL ya disponible en infraestructura",
                    "Cumple requisitos de performance (<2s response time)"
                ],
                consequences=[
                    "Positivo: Cumple con restricciones IACT",
                    "Positivo: Menor complejidad de infraestructura",
                    "Negativo: Requiere cleanup periodico (clearsessions)",
                    "Mitigacion: Cron job para limpieza automatica"
                ]
            )
            adrs.append(adr)

        return adrs

    def _create_adr(
        self,
        title: str,
        context: str,
        decision: str,
        rationale: List[str],
        consequences: List[str]
    ) -> str:
        """Crea un ADR individual."""
        adr = f"""# ADR: {title}

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Status**: Proposed
**Deciders**: SDLCDesignAgent, arquitecto-senior
**Technical Story**: Related to current feature implementation

---

## Context

{context}

---

## Decision

{decision}

---

## Rationale

{chr(10).join(f"- {r}" for r in rationale)}

---

## Consequences

{chr(10).join(f"- {c}" for c in consequences)}

---

## References

- RNF-002: Sesiones en MySQL (NO Redis)
- docs/backend/requisitos/restricciones_y_lineamientos.md

---

*Generated by SDLCDesignAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return adr

    def _generate_diagrams(
        self,
        issue: Dict[str, Any],
        hld: str,
        lld: str
    ) -> Dict[str, str]:
        """Genera diagramas Mermaid."""
        diagrams = {}

        # Architecture diagram
        diagrams["architecture"] = self._generate_architecture_diagram()

        # Sequence diagram
        diagrams["sequence"] = self._generate_sequence_diagram()

        # Component diagram
        diagrams["components"] = self._generate_component_diagram()

        # Database ER diagram
        diagrams["database"] = self._generate_database_diagram()

        return diagrams

    def _generate_architecture_diagram(self) -> str:
        """Genera diagrama de arquitectura."""
        return """```plantuml
@startuml
!define RECTANGLE class

package "Frontend" {
    component [React App] as ReactApp
    component [Redux Store] as ReduxStore
}

package "Backend" {
    component [Django Views] as DjangoViews
    component [Business Logic] as BusinessLogic
    component [Models] as Models
}

package "Database" {
    database "MySQL Primary" as MySQL #4CAF50
    database "PostgreSQL Secondary" as PostgreSQL #2196F3
}

ReactApp -down-> DjangoViews : API Calls
ReduxStore -up-> ReactApp : State Management
DjangoViews -down-> BusinessLogic : Process Request
BusinessLogic -down-> Models : Data Access
Models -down-> MySQL : Read/Write
Models -down-> PostgreSQL : Read

@enduml
```"""

    def _generate_sequence_diagram(self) -> str:
        """Genera diagrama de secuencia."""
        return """```plantuml
@startuml
actor User
participant Frontend
participant API
participant Service
database DB

User -> Frontend : Interact with UI
Frontend -> API : POST /api/endpoint
API -> API : Validate Request
API -> Service : Process Business Logic
Service -> DB : Query/Update Data
DB --> Service : Return Data
Service --> API : Return Result
API --> Frontend : JSON Response
Frontend --> User : Update UI

@enduml
```"""

    def _generate_component_diagram(self) -> str:
        """Genera diagrama de componentes."""
        return """```plantuml
@startuml
package "Frontend Components" {
    [Container Component] as Container
    [Presentation Component] as Presentation
    [Form Component] as Form
}

package "Backend Components" {
    [View Layer] as View
    [Service Layer] as Service
    [Data Layer] as Data
}

Container --> Presentation
Container --> Form
Form --> View : API Call
View --> Service
Service --> Data

@enduml
```"""

    def _generate_database_diagram(self) -> str:
        """Genera diagrama ER de base de datos."""
        return """```plantuml
@startuml
entity "USER" as user {
    * id : int <<PK>>
    --
    username : string
    email : string
    created_at : datetime
}

entity "SESSION" as session {
    * session_key : string <<PK>>
    --
    session_data : text
    expire_date : datetime
}

entity "INTERNAL_MESSAGE" as message {
    * id : int <<PK>>
    --
    user_id : int <<FK>>
    subject : string
    body : text
    created_at : datetime
}

user ||--o{ session : has
user ||--o{ message : receives

@enduml
```"""

    def _format_diagrams_document(self, diagrams: Dict[str, str]) -> str:
        """Formatea todos los diagramas en un documento."""
        doc = f"""# System Diagrams

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Generated by**: SDLCDesignAgent

---

## Architecture Diagram

{diagrams.get('architecture', 'N/A')}

---

## Sequence Diagram

{diagrams.get('sequence', 'N/A')}

---

## Component Diagram

{diagrams.get('components', 'N/A')}

---

## Database ER Diagram

{diagrams.get('database', 'N/A')}

---

*Generated by SDLCDesignAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return doc

    def _generate_review_checklist(
        self,
        hld: str,
        lld: str,
        adrs: List[str]
    ) -> str:
        """Genera design review checklist."""
        checklist = f"""# Design Review Checklist

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Reviewer**: _________
**Designer**: SDLCDesignAgent

---

## HLD Review

- [ ] Architecture is clear and well-documented
- [ ] Component responsibilities are well-defined
- [ ] Data flow is logical and efficient
- [ ] Technology stack is appropriate
- [ ] Non-functional requirements are addressed
- [ ] IACT constraints are respected (NO Redis, NO Email)
- [ ] Risks are identified and mitigated
- [ ] Success metrics are defined

---

## LLD Review

- [ ] Module breakdown is comprehensive
- [ ] Database schema is normalized and efficient
- [ ] API endpoints are RESTful and consistent
- [ ] Data models are well-designed
- [ ] Business logic is separated from presentation
- [ ] Validation rules are complete
- [ ] Error handling is comprehensive
- [ ] Testing strategy is adequate (>80% coverage)

---

## ADRs Review

- [ ] {len(adrs)} ADR(s) documented
- [ ] Decisions are justified with clear rationale
- [ ] Consequences are identified (positive and negative)
- [ ] Alternatives were considered
- [ ] References are provided

---

## Diagrams Review

- [ ] Architecture diagram is accurate
- [ ] Sequence diagram shows complete flow
- [ ] Component diagram shows relationships
- [ ] Database ER diagram is normalized

---

## Critical Constraints Check (IACT)

- [ ] NO Redis usage
- [ ] Sessions in MySQL (django.contrib.sessions.backends.db)
- [ ] NO Email/SMTP usage
- [ ] InternalMessage for notifications
- [ ] MySQL for cache if needed

---

## Overall Assessment

**Rating**: _____ / 5
**Go/No-Go for Implementation**: _____
**Comments**:

---

## Sign-off

**Arquitecto Senior**: _________________ Date: _____
**Tech Lead**: _________________ Date: _____
**Product Owner**: _________________ Date: _____

---

*Generated by SDLCDesignAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        return checklist

    # Helper methods for content generation

    def _extract_purpose(self, issue: Dict[str, Any]) -> str:
        """Extrae proposito del feature."""
        title = issue.get("issue_title", "")
        return f"This design document describes the implementation of: {title}"

    def _describe_current_architecture(self, project_context: str) -> str:
        """Describe arquitectura actual."""
        return """
Current IACT architecture:
- Monolithic Django application
- MySQL primary database
- PostgreSQL secondary database
- React frontend
- Session-based authentication
- MySQL session storage (RNF-002)
"""

    def _describe_proposed_changes(self, technical_requirements: List[str]) -> str:
        """Describe cambios propuestos."""
        if not technical_requirements:
            return "- Add new feature with minimal architectural impact\n"

        changes = ""
        for req in technical_requirements[:5]:
            changes += f"- {req}\n"
        return changes

    def _identify_components(self, technical_requirements: List[str]) -> str:
        """Identifica componentes principales."""
        return """
### Backend Components
- Django Views/ViewSets for API endpoints
- Service layer for business logic
- Models for data persistence
- Serializers for data validation

### Frontend Components
- React components for UI
- Redux/Context for state management
- API client for backend communication
"""

    def _describe_data_flow(self, technical_requirements: List[str]) -> str:
        """Describe flujo de datos."""
        return """
1. User interacts with React frontend
2. Frontend dispatches action to Redux/Context
3. API client sends HTTP request to Django backend
4. Django view validates request
5. Service layer processes business logic
6. Models interact with MySQL/PostgreSQL
7. Response sent back through layers
8. Frontend updates UI with new state
"""

    def _identify_external_interfaces(self, technical_requirements: List[str]) -> str:
        """Identifica interfaces externas."""
        return """
- REST API endpoints (JSON)
- WebSocket connections (if real-time needed)
- Database connections (MySQL, PostgreSQL)
- Internal message system (for notifications)
"""

    def _identify_key_decisions(self, technical_requirements: List[str]) -> str:
        """Identifica decisiones clave."""
        return """
1. Use MySQL for sessions (RNF-002 compliance)
2. Use InternalMessage for notifications (no email)
3. Implement server-side validation with Django
4. Use Django ORM for database abstraction
5. Follow RESTful API design principles
"""

    def _identify_tradeoffs(self, technical_requirements: List[str]) -> str:
        """Identifica trade-offs."""
        return """
1. MySQL sessions vs Redis: Chose MySQL for compliance (RNF-002)
   - Pro: Complies with constraints
   - Con: Requires periodic cleanup

2. Monolithic vs Microservices: Chose monolithic
   - Pro: Simpler deployment, lower overhead
   - Con: Harder to scale individual components
"""

    def _generate_module_breakdown(self, technical_requirements: List[str]) -> str:
        """Genera breakdown de modulos."""
        return """
### Module: Feature Module

**Responsibilities**:
- Handle user requests
- Validate input data
- Process business logic
- Persist data to database
- Return responses

**Components**:
- models.py: Data models
- views.py: API endpoints
- serializers.py: Data validation
- services.py: Business logic
- tests/: Unit and integration tests
"""

    def _design_database_schema(self, technical_requirements: List[str]) -> str:
        """Disena schema de base de datos."""
        return """
```sql
CREATE TABLE feature_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    data TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

CREATE INDEX idx_feature_user ON feature_table(user_id);
CREATE INDEX idx_feature_created ON feature_table(created_at);
```
"""

    def _design_api_endpoints(self, technical_requirements: List[str]) -> str:
        """Disena API endpoints."""
        return """
### POST /api/feature/
Create new feature record
- Auth: Required
- Body: JSON with feature data
- Response: 201 Created

### GET /api/feature/:id/
Retrieve feature record
- Auth: Required
- Response: 200 OK

### PUT /api/feature/:id/
Update feature record
- Auth: Required
- Body: JSON with updated data
- Response: 200 OK

### DELETE /api/feature/:id/
Delete feature record
- Auth: Required
- Response: 204 No Content

### GET /api/feature/
List feature records
- Auth: Required
- Query params: ?page=1&page_size=20
- Response: 200 OK with pagination
"""

    def _generate_model_code(self, technical_requirements: List[str]) -> str:
        """Genera codigo de modelos."""
        return """
from django.db import models
from django.contrib.auth.models import User

class FeatureModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feature_table'
        ordering = ['-created_at']

    def __str__(self):
        return f"Feature {self.id} - {self.user.username}"
"""

    def _generate_service_code(self, technical_requirements: List[str]) -> str:
        """Genera codigo de servicios."""
        return """
class FeatureService:
    @staticmethod
    def create_feature(user, data):
        # Validate data
        if not data:
            raise ValueError("Data cannot be empty")

        # Create feature
        feature = FeatureModel.objects.create(user=user, data=data)
        return feature

    @staticmethod
    def get_feature(feature_id):
        return FeatureModel.objects.get(id=feature_id)

    @staticmethod
    def list_features(user):
        return FeatureModel.objects.filter(user=user)
"""

    def _design_frontend_components(self, technical_requirements: List[str]) -> str:
        """Disena componentes frontend."""
        return """
### Container: FeatureContainer
- Connects to Redux store
- Handles data fetching
- Passes data to presentation components

### Component: FeatureList
- Displays list of features
- Handles pagination
- Renders FeatureItem for each feature

### Component: FeatureForm
- Handles user input
- Client-side validation
- Submits data to API
"""

    def _design_state_management(self, technical_requirements: List[str]) -> str:
        """Disena state management."""
        return """
```javascript
// Redux slice: featureSlice.js
const featureSlice = createSlice({
    name: 'feature',
    initialState: {
        items: [],
        loading: false,
        error: null
    },
    reducers: {
        fetchFeaturesStart(state) {
            state.loading = true;
        },
        fetchFeaturesSuccess(state, action) {
            state.items = action.payload;
            state.loading = false;
        },
        fetchFeaturesFailure(state, action) {
            state.error = action.payload;
            state.loading = false;
        }
    }
});
```
"""

    def _define_validation_rules(self, technical_requirements: List[str]) -> str:
        """Define reglas de validacion."""
        return """
1. Required fields: user, data
2. Data length: max 10000 characters
3. User must be authenticated
4. User can only access own features
"""

    def _define_error_codes(self, technical_requirements: List[str]) -> str:
        """Define codigos de error."""
        return """
- 400: Bad Request (validation failed)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (not owner)
- 404: Not Found (feature doesn't exist)
- 500: Internal Server Error
"""

    def _has_significant_architecture_decision(self, technical_requirements: List[str]) -> bool:
        """Detecta si hay decisiones arquitectonicas significativas."""
        keywords = ["session", "cache", "database", "architecture", "integration"]
        tech_reqs_str = " ".join(technical_requirements).lower()
        return any(keyword in tech_reqs_str for keyword in keywords)

    # LLM Integration Methods

    def _generate_architecture_with_llm(
        self,
        issue: Dict[str, Any],
        project_context: str = ""
    ) -> Dict[str, Any]:
        """Genera recomendaciones de arquitectura usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            # Fallback to heuristics
            return {
                "components": [],
                "data_flow": "",
                "technology_recommendations": {}
            }

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])
            acceptance_criteria = issue.get("acceptance_criteria", [])

            prompt = f"""Analiza y genera recomendaciones de arquitectura para el siguiente feature del proyecto IACT.

**Feature**: {title}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Criterios de Aceptación**:
{chr(10).join(f"- {crit}" for crit in acceptance_criteria)}

**Contexto del Proyecto**: {project_context}

**Restricciones IACT**:
- NO Redis (usar MySQL para sesiones/cache)
- NO Email/SMTP (usar InternalMessage)
- Stack: Django 4.2+, React 18+, MySQL/PostgreSQL

Genera recomendaciones de arquitectura considerando:
1. Componentes principales del sistema
2. Flujo de datos entre componentes
3. Tecnologías recomendadas que cumplan restricciones IACT
4. Integraciones necesarias

Responde en formato JSON:
{{
  "components": ["lista de componentes principales"],
  "data_flow": "descripción del flujo de datos",
  "technology_recommendations": {{
    "backend": "recomendaciones backend",
    "frontend": "recomendaciones frontend",
    "database": "recomendaciones database"
  }}
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_architecture(llm_response)

        except Exception as e:
            self.logger.warning(f"LLM architecture generation failed: {e}, using fallback")
            return {
                "components": [],
                "data_flow": "",
                "technology_recommendations": {}
            }

    def _parse_llm_architecture(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response para extraer recomendaciones de arquitectura."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                # Validate and normalize
                architecture = {
                    "components": result.get("components", []),
                    "data_flow": result.get("data_flow", ""),
                    "technology_recommendations": result.get("technology_recommendations", {})
                }

                # Ensure components is a list
                if not isinstance(architecture["components"], list):
                    architecture["components"] = []

                return architecture

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM architecture as JSON: {e}")

        # Fallback: parse as text
        architecture = {
            "components": [],
            "data_flow": "",
            "technology_recommendations": {}
        }

        # Extract components from text
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('-') or line.startswith('*'):
                # Extract component name
                component = line.lstrip('-*').strip()
                if component and len(component) < 100:
                    architecture["components"].append(component)

        # Extract data flow
        if "flow" in llm_response.lower() or "flujo" in llm_response.lower():
            for i, line in enumerate(lines):
                if "flow" in line.lower() or "flujo" in line.lower():
                    # Get next few lines as data flow
                    if i + 1 < len(lines):
                        architecture["data_flow"] = lines[i + 1].strip()
                    break

        return architecture

    def _recommend_patterns_with_llm(
        self,
        issue: Dict[str, Any],
        architecture: str = ""
    ) -> Dict[str, Any]:
        """Recomienda patrones de diseño usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            # Fallback to heuristics
            return {"patterns": []}

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])

            prompt = f"""Recomienda patrones de diseño apropiados para el siguiente feature.

**Feature**: {title}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Arquitectura Propuesta**: {architecture[:500]}

**Stack**: Django 4.2+, React 18+, MySQL/PostgreSQL

Recomienda patrones de diseño considerando:
1. Patrones arquitectónicos (Repository, Service Layer, etc.)
2. Patrones de diseño apropiados (Strategy, Factory, Observer, etc.)
3. Aplicabilidad específica al feature
4. Justificación de cada patrón

Responde en formato JSON:
{{
  "patterns": [
    {{
      "name": "nombre del patrón",
      "rationale": "por qué es apropiado",
      "applicability": "dónde aplicarlo"
    }}
  ]
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_patterns(llm_response)

        except Exception as e:
            self.logger.warning(f"LLM pattern recommendation failed: {e}, using fallback")
            return {"patterns": []}

    def _parse_llm_patterns(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response para extraer patrones de diseño recomendados."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                # Validate and normalize
                patterns = {
                    "patterns": result.get("patterns", [])
                }

                # Ensure patterns is a list
                if not isinstance(patterns["patterns"], list):
                    patterns["patterns"] = []

                # Validate each pattern has required fields
                validated_patterns = []
                for pattern in patterns["patterns"]:
                    if isinstance(pattern, dict) and "name" in pattern:
                        validated_pattern = {
                            "name": pattern.get("name", "Unknown Pattern"),
                            "rationale": pattern.get("rationale", ""),
                            "applicability": pattern.get("applicability", "")
                        }
                        validated_patterns.append(validated_pattern)

                patterns["patterns"] = validated_patterns
                return patterns

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM patterns as JSON: {e}")

        # Fallback: parse as text
        patterns = {"patterns": []}

        # Extract patterns from text
        lines = llm_response.split('\n')
        current_pattern = None

        for line in lines:
            line = line.strip()

            # Detect pattern names
            if "pattern" in line.lower() and (":" in line or "-" in line):
                if current_pattern:
                    patterns["patterns"].append(current_pattern)

                # Extract pattern name
                pattern_name = line.split(':')[-1].split('-')[-1].strip()
                current_pattern = {
                    "name": pattern_name,
                    "rationale": "",
                    "applicability": ""
                }
            elif current_pattern:
                # Add to rationale or applicability
                if "rationale" in line.lower() or "justif" in line.lower():
                    current_pattern["rationale"] = line
                elif "applicability" in line.lower() or "aplicable" in line.lower():
                    current_pattern["applicability"] = line

        if current_pattern:
            patterns["patterns"].append(current_pattern)

        return patterns

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Guardrails especificos para Design phase."""
        errors = []

        # Validar que se genero HLD
        if "hld" not in output_data or not output_data["hld"]:
            errors.append("No se genero HLD (High-Level Design)")

        # Validar que se genero LLD
        if "lld" not in output_data or not output_data["lld"]:
            errors.append("No se genero LLD (Low-Level Design)")

        # Validar que se generaron diagramas
        if "diagrams" not in output_data or not output_data["diagrams"]:
            errors.append("No se generaron diagrams (diagrams)")

        # Validar que HLD menciona restricciones IACT
        if "hld" in output_data:
            hld_content = output_data["hld"].lower()
            if "redis" in hld_content and "no redis" not in hld_content:
                errors.append("HLD menciona Redis sin aclarar que esta prohibido (RNF-002)")

        return errors
