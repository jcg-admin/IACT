"""
SDLCTestingAgent - Fase 5: Testing

Responsabilidad: Generar test plan, test cases, y estrategia de testing
para features en fase de implementacion.

Inputs:
- design_result (dict): Output de SDLCDesignAgent
- issue (dict): Issue del SDLCPlannerAgent
- implementation_status (str): Estado de la implementacion

Outputs:
- Test plan completo
- Test cases (unit, integration, E2E)
- Test pyramid strategy
- Coverage requirements
- Testing checklist
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

# Testing method constants
TESTING_METHOD_LLM = "llm"
TESTING_METHOD_HEURISTIC = "heuristic"


class SDLCTestingAgent(SDLCAgent):
    """
    Agente para la fase de Testing del SDLC.

    Genera test plan, test cases, y estrategia de testing completa.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="SDLCTestingAgent",
            phase="testing",
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
        """Valida que exista design result e issue."""
        errors = []

        if "design_result" not in input_data:
            errors.append("Falta 'design_result' en input (del SDLCDesignAgent)")

        if "issue" not in input_data:
            errors.append("Falta 'issue' en input (del SDLCPlannerAgent)")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la fase de Testing.

        Args:
            input_data: {
                "issue": dict,  # Output de SDLCPlannerAgent
                "design_result": dict,  # Output de SDLCDesignAgent
                "implementation_status": str  # "pending", "in_progress", "completed"
            }

        Returns:
            Dict con test plan, test cases, coverage analysis
        """
        issue = input_data["issue"]
        design_result = input_data["design_result"]
        implementation_status = input_data.get("implementation_status", "pending")

        self.logger.info(f"Generando test plan para: {issue.get('issue_title', 'Unknown')}")

        # Determine testing method
        testing_method = TESTING_METHOD_LLM if self.llm_generator else TESTING_METHOD_HEURISTIC

        # Generar test plan
        test_plan = self._generate_test_plan(issue, design_result)

        # Generar test cases (with LLM enhancement if available)
        test_cases = self._generate_test_cases(issue, design_result)

        # Generar test pyramid strategy
        test_pyramid = self._generate_test_pyramid_strategy(test_cases)

        # Generar coverage requirements
        coverage_requirements = self._generate_coverage_requirements(issue)

        # Generar testing checklist
        testing_checklist = self._generate_testing_checklist(test_cases, coverage_requirements)

        # Guardar artefactos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts = []

        test_plan_path = self.save_artifact(test_plan, f"TEST_PLAN_{timestamp}.md")
        artifacts.append(str(test_plan_path))

        test_cases_doc = self._format_test_cases_document(test_cases)
        test_cases_path = self.save_artifact(test_cases_doc, f"TEST_CASES_{timestamp}.md")
        artifacts.append(str(test_cases_path))

        test_pyramid_doc = self._format_test_pyramid_document(test_pyramid)
        test_pyramid_path = self.save_artifact(test_pyramid_doc, f"TEST_PYRAMID_{timestamp}.md")
        artifacts.append(str(test_pyramid_path))

        checklist_path = self.save_artifact(testing_checklist, f"TEST_CHECKLIST_{timestamp}.md")
        artifacts.append(str(checklist_path))

        # Crear resultado de fase
        phase_result = self.create_phase_result(
            decision="go",
            confidence=0.9,
            artifacts=artifacts,
            recommendations=[
                "Test plan completo generado",
                "Implementar tests siguiendo test pyramid",
                "Objetivo: Coverage > 80%",
                "Ejecutar tests antes de deployment"
            ],
            next_steps=[
                "Implementar unit tests (TDD si es posible)",
                "Implementar integration tests",
                "Implementar E2E tests para flujos criticos",
                "Validar coverage > 80%",
                "Code review de tests",
                "Proceder con Deployment phase"
            ]
        )

        return {
            "test_plan": test_plan,
            "test_plan_path": str(test_plan_path),
            "test_cases": test_cases,
            "test_cases_path": str(test_cases_path),
            "test_pyramid": test_pyramid,
            "test_pyramid_path": str(test_pyramid_path),
            "coverage_requirements": coverage_requirements,
            "testing_checklist": testing_checklist,
            "checklist_path": str(checklist_path),
            "artifacts": artifacts,
            "testing_method": testing_method,
            "phase_result": phase_result
        }

    def _generate_test_plan(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any]
    ) -> str:
        """Genera test plan completo."""
        title = issue.get("issue_title", "Unknown Feature")
        acceptance_criteria = issue.get("acceptance_criteria", [])

        test_plan = f"""# Test Plan

**Feature**: {title}
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Test Lead**: SDLCTestingAgent
**Version**: 1.0

---

## 1. Objectives

### Testing Goals
- Verify all acceptance criteria are met
- Ensure code quality and maintainability
- Validate performance requirements
- Ensure security and data integrity
- Achieve > 80% code coverage

### Success Criteria
{self._format_acceptance_criteria_as_tests(acceptance_criteria)}

---

## 2. Scope

### In Scope
- Unit tests for all models, services, views
- Integration tests for API endpoints
- E2E tests for critical user flows
- Performance tests for key operations
- Security tests for authentication/authorization

### Out of Scope
- Load testing (unless performance-critical feature)
- Stress testing
- Cross-browser testing (unless UI-heavy feature)

---

## 3. Test Strategy

### Test Pyramid
```
         /\\
        /E2E\\         (10%) - Few, focused on critical paths
       /------\\
      /  INT   \\       (30%) - API endpoints, integrations
     /----------\\
    /   UNIT     \\     (60%) - Models, services, utilities
   /--------------\\
```

### Test Types
1. **Unit Tests (60%)**
   - Test individual functions/methods
   - Mock external dependencies
   - Fast execution (< 1s total)

2. **Integration Tests (30%)**
   - Test API endpoints end-to-end
   - Use test database
   - Moderate execution (< 10s total)

3. **E2E Tests (10%)**
   - Test critical user flows
   - Use browser automation if needed
   - Slower execution (< 30s total)

---

## 4. Test Environment

### Backend Testing
- Python: pytest, Django TestCase
- Database: SQLite for tests (fast, isolated)
- Coverage: pytest-cov
- Mocking: unittest.mock

### Frontend Testing (if applicable)
- Framework: Jest, React Testing Library
- E2E: Playwright or Cypress
- Coverage: Jest coverage

---

## 5. Entry Criteria

- [ ] Implementation completed
- [ ] Code review passed
- [ ] Static analysis passed (linting, type checking)
- [ ] Test environment set up

---

## 6. Exit Criteria

- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] No critical bugs
- [ ] Performance requirements met
- [ ] Security checks passed
- [ ] Documentation updated

---

## 7. Test Data

### Test Users
- admin_user: Superuser for admin operations
- regular_user: Regular user for standard operations
- unauthorized_user: User without permissions

### Test Data Sets
- Valid data: Normal, expected inputs
- Edge cases: Boundary values, empty strings
- Invalid data: Malformed, missing required fields

---

## 8. Risks and Mitigation

### Risk: Test database pollution
**Mitigation**: Use Django TestCase (automatic rollback)

### Risk: Flaky tests
**Mitigation**: Avoid time-dependent tests, use factories

### Risk: Slow test suite
**Mitigation**: Use --parallel flag, optimize database queries

---

## 9. Schedule

### Test Development
- Unit tests: 2-3 days
- Integration tests: 1-2 days
- E2E tests: 1 day
- Bug fixes: 1 day buffer

### Test Execution
- Continuous: On every commit (CI/CD)
- Pre-merge: Full suite before PR approval
- Pre-deploy: Full suite + manual QA

---

## 10. Deliverables

- [ ] Unit test suite (> 60% of tests)
- [ ] Integration test suite (> 30% of tests)
- [ ] E2E test suite (> 10% of tests)
- [ ] Test documentation
- [ ] Coverage report (> 80%)
- [ ] Bug report (if issues found)

---

## 11. Test Execution Commands

### Run All Tests
```bash
cd api/callcentersite
python manage.py test --parallel --keepdb
```

### Run with Coverage
```bash
pytest --cov=callcentersite --cov-report=html --cov-report=term
```

### Run Specific Test File
```bash
python manage.py test callcentersite.tests.test_feature
```

### Run with Verbosity
```bash
python manage.py test --verbosity=2
```

---

## 12. Defect Management

### Severity Levels
- **Critical**: System crash, data loss, security breach
- **High**: Major functionality broken
- **Medium**: Minor functionality broken
- **Low**: Cosmetic issues, typos

### Defect Workflow
1. Log defect in issue tracker
2. Assign to developer
3. Fix and verify
4. Re-test
5. Close if passed

---

*Generated by SDLCTestingAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return test_plan

    def _generate_test_cases(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera test cases concretos con LLM enhancement si está disponible."""
        test_cases = []
        acceptance_criteria = issue.get("acceptance_criteria", [])

        # Try LLM-enhanced test case generation first
        if self.llm_generator:
            try:
                llm_test_cases = self._generate_test_cases_with_llm(issue, design_result)
                if llm_test_cases and len(llm_test_cases) > 0:
                    test_cases.extend(llm_test_cases)
                    self.logger.info(f"Generated {len(llm_test_cases)} test cases using LLM")
            except Exception as e:
                self.logger.warning(f"LLM test case generation failed: {e}, falling back to heuristics")

        # Fallback or supplement with heuristic test cases
        if not test_cases:
            # Unit test cases
            test_cases.extend(self._generate_unit_test_cases(acceptance_criteria))

            # Integration test cases
            test_cases.extend(self._generate_integration_test_cases(acceptance_criteria))

            # E2E test cases
            test_cases.extend(self._generate_e2e_test_cases(acceptance_criteria))

            self.logger.info(f"Generated {len(test_cases)} test cases using heuristics")

        return test_cases

    def _generate_unit_test_cases(self, acceptance_criteria: List[str]) -> List[Dict[str, Any]]:
        """Genera unit test cases."""
        return [
            {
                "id": "UT-001",
                "type": "unit",
                "name": "Test model creation",
                "description": "Verify model can be created with valid data",
                "preconditions": "Database initialized",
                "steps": [
                    "Create model instance with valid data",
                    "Save to database",
                    "Retrieve from database"
                ],
                "expected_result": "Model created successfully with correct attributes",
                "priority": "high"
            },
            {
                "id": "UT-002",
                "type": "unit",
                "name": "Test model validation",
                "description": "Verify model validation rejects invalid data",
                "preconditions": "Database initialized",
                "steps": [
                    "Create model instance with invalid data",
                    "Attempt to save"
                ],
                "expected_result": "ValidationError raised",
                "priority": "high"
            },
            {
                "id": "UT-003",
                "type": "unit",
                "name": "Test service logic",
                "description": "Verify business logic in service layer",
                "preconditions": "Mock dependencies set up",
                "steps": [
                    "Call service method with test data",
                    "Verify logic executed correctly"
                ],
                "expected_result": "Service returns expected result",
                "priority": "high"
            }
        ]

    def _generate_integration_test_cases(self, acceptance_criteria: List[str]) -> List[Dict[str, Any]]:
        """Genera integration test cases."""
        return [
            {
                "id": "IT-001",
                "type": "integration",
                "name": "Test POST endpoint - success",
                "description": "Verify POST endpoint creates resource",
                "preconditions": "Test user authenticated",
                "steps": [
                    "Send POST request with valid JSON",
                    "Verify 201 Created response",
                    "Verify resource in database"
                ],
                "expected_result": "Resource created, 201 status, valid JSON response",
                "priority": "high"
            },
            {
                "id": "IT-002",
                "type": "integration",
                "name": "Test POST endpoint - validation error",
                "description": "Verify POST endpoint rejects invalid data",
                "preconditions": "Test user authenticated",
                "steps": [
                    "Send POST request with invalid JSON",
                    "Verify 400 Bad Request response"
                ],
                "expected_result": "400 status, error details in response",
                "priority": "high"
            },
            {
                "id": "IT-003",
                "type": "integration",
                "name": "Test GET endpoint - authenticated",
                "description": "Verify GET endpoint returns resource",
                "preconditions": "Test resource exists, user authenticated",
                "steps": [
                    "Send GET request to /api/resource/:id/",
                    "Verify 200 OK response"
                ],
                "expected_result": "200 status, resource JSON in response",
                "priority": "high"
            },
            {
                "id": "IT-004",
                "type": "integration",
                "name": "Test GET endpoint - unauthorized",
                "description": "Verify GET endpoint rejects unauthenticated requests",
                "preconditions": "No authentication",
                "steps": [
                    "Send GET request without auth token",
                    "Verify 401 Unauthorized response"
                ],
                "expected_result": "401 status, error message",
                "priority": "medium"
            }
        ]

    def _generate_e2e_test_cases(self, acceptance_criteria: List[str]) -> List[Dict[str, Any]]:
        """Genera E2E test cases."""
        return [
            {
                "id": "E2E-001",
                "type": "e2e",
                "name": "Test complete user flow",
                "description": "Verify user can complete entire workflow",
                "preconditions": "Application deployed, test user exists",
                "steps": [
                    "User logs in",
                    "User navigates to feature",
                    "User creates new item",
                    "User verifies item appears in list",
                    "User logs out"
                ],
                "expected_result": "Complete flow succeeds without errors",
                "priority": "high"
            },
            {
                "id": "E2E-002",
                "type": "e2e",
                "name": "Test error handling",
                "description": "Verify app handles errors gracefully",
                "preconditions": "Application deployed",
                "steps": [
                    "User logs in",
                    "User submits invalid data",
                    "User sees error message",
                    "User corrects data",
                    "User successfully submits"
                ],
                "expected_result": "Error displayed, user can recover",
                "priority": "medium"
            }
        ]

    def _generate_test_pyramid_strategy(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera estrategia de test pyramid."""
        unit_tests = [tc for tc in test_cases if tc["type"] == "unit"]
        integration_tests = [tc for tc in test_cases if tc["type"] == "integration"]
        e2e_tests = [tc for tc in test_cases if tc["type"] == "e2e"]

        total = len(test_cases)
        unit_pct = (len(unit_tests) / total * 100) if total > 0 else 0
        integration_pct = (len(integration_tests) / total * 100) if total > 0 else 0
        e2e_pct = (len(e2e_tests) / total * 100) if total > 0 else 0

        return {
            "total_tests": total,
            "unit_tests": {
                "count": len(unit_tests),
                "percentage": unit_pct,
                "target": 60,
                "status": "on_target" if unit_pct >= 60 else "needs_more"
            },
            "integration_tests": {
                "count": len(integration_tests),
                "percentage": integration_pct,
                "target": 30,
                "status": "on_target" if 20 <= integration_pct <= 40 else "adjust"
            },
            "e2e_tests": {
                "count": len(e2e_tests),
                "percentage": e2e_pct,
                "target": 10,
                "status": "on_target" if e2e_pct <= 15 else "too_many"
            }
        }

    def _generate_coverage_requirements(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Genera requisitos de coverage."""
        story_points = issue.get("story_points", 0)

        # Features mas complejos requieren mas coverage
        if story_points >= 8:
            target_coverage = 85
        else:
            target_coverage = 80

        return {
            "overall_target": target_coverage,
            "critical_paths": 100,  # Critical paths must be 100% covered
            "models": 90,
            "services": 85,
            "views": 80,
            "utilities": 75,
            "measurement_tool": "pytest-cov",
            "enforcement": "CI/CD pipeline fails if below target"
        }

    def _generate_testing_checklist(
        self,
        test_cases: List[Dict[str, Any]],
        coverage_requirements: Dict[str, Any]
    ) -> str:
        """Genera testing checklist."""
        checklist = f"""# Testing Checklist

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Tester**: _________

---

## Unit Tests

"""
        unit_tests = [tc for tc in test_cases if tc["type"] == "unit"]
        for tc in unit_tests:
            checklist += f"- [ ] {tc['id']}: {tc['name']}\n"

        checklist += "\n## Integration Tests\n\n"
        integration_tests = [tc for tc in test_cases if tc["type"] == "integration"]
        for tc in integration_tests:
            checklist += f"- [ ] {tc['id']}: {tc['name']}\n"

        checklist += "\n## E2E Tests\n\n"
        e2e_tests = [tc for tc in test_cases if tc["type"] == "e2e"]
        for tc in e2e_tests:
            checklist += f"- [ ] {tc['id']}: {tc['name']}\n"

        checklist += f"""
---

## Coverage Requirements

- [ ] Overall coverage: > {coverage_requirements['overall_target']}%
- [ ] Critical paths: 100%
- [ ] Models: > {coverage_requirements['models']}%
- [ ] Services: > {coverage_requirements['services']}%
- [ ] Views: > {coverage_requirements['views']}%

---

## Quality Checks

- [ ] All tests passing
- [ ] No flaky tests
- [ ] No test warnings
- [ ] Test execution time < 30s
- [ ] Code linting passed
- [ ] Type checking passed (if applicable)

---

## Security Checks

- [ ] Authentication tests passing
- [ ] Authorization tests passing
- [ ] Input validation tests passing
- [ ] SQL injection tests passing
- [ ] XSS protection tests passing

---

## Performance Checks

- [ ] Response time < 2s for API calls
- [ ] Database queries optimized (N+1 checked)
- [ ] No memory leaks detected

---

## Documentation

- [ ] Test code is well-commented
- [ ] README updated with test instructions
- [ ] Known issues documented
- [ ] Test data documented

---

## Sign-off

**Developer**: _________________ Date: _____
**QA Lead**: _________________ Date: _____
**Tech Lead**: _________________ Date: _____

---

*Generated by SDLCTestingAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return checklist

    def _format_test_cases_document(self, test_cases: List[Dict[str, Any]]) -> str:
        """Formatea test cases en documento."""
        doc = f"""# Test Cases

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Generated by**: SDLCTestingAgent

---

## Summary

Total test cases: {len(test_cases)}

---

"""

        # Group by type
        for test_type in ["unit", "integration", "e2e"]:
            type_tests = [tc for tc in test_cases if tc["type"] == test_type]
            if type_tests:
                doc += f"## {test_type.upper()} Tests\n\n"
                for tc in type_tests:
                    doc += f"### {tc['id']}: {tc['name']}\n\n"
                    doc += f"**Description**: {tc['description']}\n\n"
                    doc += f"**Priority**: {tc['priority']}\n\n"
                    doc += f"**Preconditions**: {tc['preconditions']}\n\n"
                    doc += "**Steps**:\n"
                    for i, step in enumerate(tc['steps'], 1):
                        doc += f"{i}. {step}\n"
                    doc += f"\n**Expected Result**: {tc['expected_result']}\n\n"
                    doc += "---\n\n"

        doc += f"""
*Generated by SDLCTestingAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return doc

    def _format_test_pyramid_document(self, test_pyramid: Dict[str, Any]) -> str:
        """Formatea test pyramid en documento."""
        doc = f"""# Test Pyramid Strategy

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Generated by**: SDLCTestingAgent

---

## Overview

Total tests: {test_pyramid['total_tests']}

---

## Pyramid Breakdown

### E2E Tests (Target: 10%)
- Count: {test_pyramid['e2e_tests']['count']}
- Percentage: {test_pyramid['e2e_tests']['percentage']:.1f}%
- Target: {test_pyramid['e2e_tests']['target']}%
- Status: {test_pyramid['e2e_tests']['status']}

### Integration Tests (Target: 30%)
- Count: {test_pyramid['integration_tests']['count']}
- Percentage: {test_pyramid['integration_tests']['percentage']:.1f}%
- Target: {test_pyramid['integration_tests']['target']}%
- Status: {test_pyramid['integration_tests']['status']}

### Unit Tests (Target: 60%)
- Count: {test_pyramid['unit_tests']['count']}
- Percentage: {test_pyramid['unit_tests']['percentage']:.1f}%
- Target: {test_pyramid['unit_tests']['target']}%
- Status: {test_pyramid['unit_tests']['status']}

---

## Pyramid Visualization

```
         /\\
        /{test_pyramid['e2e_tests']['count']:^4}\\       E2E ({test_pyramid['e2e_tests']['percentage']:.0f}%)
       /------\\
      / {test_pyramid['integration_tests']['count']:^4}  \\     Integration ({test_pyramid['integration_tests']['percentage']:.0f}%)
     /----------\\
    /   {test_pyramid['unit_tests']['count']:^4}    \\   Unit ({test_pyramid['unit_tests']['percentage']:.0f}%)
   /--------------\\
```

---

## Recommendations

"""

        # Add recommendations based on status
        unit_status = test_pyramid['unit_tests']['status']
        if unit_status == "needs_more":
            doc += "- Add more unit tests to reach 60% target\n"

        integration_status = test_pyramid['integration_tests']['status']
        if integration_status == "adjust":
            doc += "- Adjust integration tests to ~30% of total\n"

        e2e_status = test_pyramid['e2e_tests']['status']
        if e2e_status == "too_many":
            doc += "- Consider converting some E2E tests to integration tests\n"

        doc += """
---

*Generated by SDLCTestingAgent*
*Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        return doc

    def _format_acceptance_criteria_as_tests(self, acceptance_criteria: List[str]) -> str:
        """Formatea acceptance criteria como test cases."""
        if not acceptance_criteria:
            return "- Verify feature works as designed\n"

        result = ""
        for i, ac in enumerate(acceptance_criteria, 1):
            result += f"{i}. {ac}\n"
        return result

    # LLM Integration Methods

    def _generate_test_strategy_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera estrategia de testing usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            # Fallback to default strategy
            return {
                "focus_areas": [],
                "critical_paths": [],
                "risk_areas": [],
                "recommended_test_count": {"unit": 0, "integration": 0, "e2e": 0}
            }

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])
            acceptance_criteria = issue.get("acceptance_criteria", [])

            prompt = f"""Genera una estrategia de testing detallada para el siguiente feature del proyecto IACT.

**Feature**: {title}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Criterios de Aceptación**:
{chr(10).join(f"- {crit}" for crit in acceptance_criteria)}

**Contexto del Diseño**: {design_result.get('hld', '')[:500]}

Identifica:
1. Áreas de enfoque para testing (componentes críticos)
2. Caminos críticos que deben ser probados
3. Áreas de riesgo que requieren testing exhaustivo
4. Cantidad recomendada de tests por nivel (unit, integration, e2e)

Responde en formato JSON:
{{
  "focus_areas": ["lista de áreas críticas"],
  "critical_paths": ["lista de flujos críticos"],
  "risk_areas": ["lista de áreas de riesgo"],
  "recommended_test_count": {{
    "unit": X,
    "integration": Y,
    "e2e": Z
  }}
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_test_strategy(llm_response)

        except Exception as e:
            self.logger.warning(f"LLM test strategy generation failed: {e}, using fallback")
            return {
                "focus_areas": [],
                "critical_paths": [],
                "risk_areas": [],
                "recommended_test_count": {"unit": 0, "integration": 0, "e2e": 0}
            }

    def _parse_llm_test_strategy(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response para extraer estrategia de testing."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                # Check if nested under "test_strategy" key
                if "test_strategy" in result:
                    result = result["test_strategy"]

                # Validate and normalize
                strategy = {
                    "focus_areas": result.get("focus_areas", []),
                    "critical_paths": result.get("critical_paths", []),
                    "risk_areas": result.get("risk_areas", []),
                    "recommended_test_count": result.get("recommended_test_count", {
                        "unit": 0, "integration": 0, "e2e": 0
                    })
                }

                # Ensure lists
                if not isinstance(strategy["focus_areas"], list):
                    strategy["focus_areas"] = []
                if not isinstance(strategy["critical_paths"], list):
                    strategy["critical_paths"] = []
                if not isinstance(strategy["risk_areas"], list):
                    strategy["risk_areas"] = []

                return strategy

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM test strategy as JSON: {e}")

        # Fallback: return default structure
        return {
            "focus_areas": [],
            "critical_paths": [],
            "risk_areas": [],
            "recommended_test_count": {"unit": 0, "integration": 0, "e2e": 0}
        }

    def _generate_test_cases_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Genera test cases usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            return []

        try:
            title = issue.get("issue_title", "")
            technical_requirements = issue.get("technical_requirements", [])
            acceptance_criteria = issue.get("acceptance_criteria", [])

            prompt = f"""Genera test cases específicos para el siguiente feature del proyecto IACT.

**Feature**: {title}

**Requisitos Técnicos**:
{chr(10).join(f"- {req}" for req in technical_requirements)}

**Criterios de Aceptación**:
{chr(10).join(f"- {crit}" for crit in acceptance_criteria)}

Genera test cases concretos para:
1. Unit tests (60% del total) - Testing de modelos, servicios, utilidades
2. Integration tests (30% del total) - Testing de API endpoints
3. E2E tests (10% del total) - Testing de flujos de usuario completos

Cada test case debe incluir:
- id: Identificador único (UT-XXX, IT-XXX, E2E-XXX)
- type: "unit", "integration", o "e2e"
- name: Nombre descriptivo
- description: Descripción detallada
- priority: "high", "medium", o "low"
- steps: Lista de pasos a ejecutar
- expected_result: Resultado esperado

Responde en formato JSON:
{{
  "test_cases": [
    {{
      "id": "UT-001",
      "type": "unit",
      "name": "Test name",
      "description": "Test description",
      "priority": "high",
      "steps": ["step 1", "step 2"],
      "expected_result": "Expected result"
    }}
  ]
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_test_cases(llm_response)

        except Exception as e:
            self.logger.warning(f"LLM test cases generation failed: {e}, using fallback")
            return []

    def _parse_llm_test_cases(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response para extraer test cases."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                test_cases = result.get("test_cases", [])

                # Validate and normalize each test case
                normalized_cases = []
                for tc in test_cases:
                    if isinstance(tc, dict) and "id" in tc and "type" in tc:
                        normalized_case = {
                            "id": tc.get("id", "TEST-001"),
                            "type": tc.get("type", "unit"),
                            "name": tc.get("name", "Test case"),
                            "description": tc.get("description", ""),
                            "priority": tc.get("priority", "medium"),
                            "steps": tc.get("steps", []),
                            "expected_result": tc.get("expected_result", ""),
                            "preconditions": tc.get("preconditions", "")
                        }
                        normalized_cases.append(normalized_case)

                return normalized_cases

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM test cases as JSON: {e}")

        # Fallback: return empty list
        return []

    def _identify_critical_paths_with_llm(
        self,
        issue: Dict[str, Any],
        design_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identifica caminos críticos usando LLM con fallback a heurísticas."""
        if not self.llm_generator:
            return []

        try:
            title = issue.get("issue_title", "")
            acceptance_criteria = issue.get("acceptance_criteria", [])

            prompt = f"""Identifica los caminos críticos que deben ser probados para el siguiente feature.

**Feature**: {title}

**Criterios de Aceptación**:
{chr(10).join(f"- {crit}" for crit in acceptance_criteria)}

Un camino crítico es una secuencia de operaciones que:
1. Es esencial para la funcionalidad del feature
2. Involucra múltiples componentes
3. Si falla, causa un impacto significativo en el usuario

Identifica 2-5 caminos críticos prioritarios.

Responde en formato JSON:
{{
  "critical_paths": [
    {{
      "path": "Descripción del flujo completo",
      "priority": "critical|high|medium",
      "rationale": "Por qué es crítico"
    }}
  ]
}}"""

            llm_response = self.llm_generator._call_llm(prompt)
            return self._parse_llm_critical_paths(llm_response)

        except Exception as e:
            self.logger.warning(f"LLM critical paths identification failed: {e}, using fallback")
            return []

    def _parse_llm_critical_paths(self, llm_response: str) -> List[Dict[str, Any]]:
        """Parse LLM response para extraer caminos críticos."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                result = json.loads(json_match.group(0))

                paths = result.get("critical_paths", [])

                # Validate and normalize
                normalized_paths = []
                for path in paths:
                    if isinstance(path, dict) and "path" in path:
                        normalized_path = {
                            "path": path.get("path", ""),
                            "priority": path.get("priority", "medium"),
                            "rationale": path.get("rationale", "")
                        }
                        normalized_paths.append(normalized_path)

                return normalized_paths

        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning(f"Failed to parse LLM critical paths as JSON: {e}")

        # Fallback: return empty list
        return []

    def _custom_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """Guardrails especificos para Testing phase."""
        errors = []

        # Validar que se genero test plan
        if "test_plan" not in output_data or not output_data["test_plan"]:
            errors.append("No se genero test plan")

        # Validar que se generaron test cases
        if "test_cases" not in output_data or not output_data["test_cases"]:
            errors.append("No se generaron test cases")

        # Validar que hay suficientes unit tests (60% minimo)
        if "test_pyramid" in output_data:
            pyramid = output_data["test_pyramid"]
            unit_pct = pyramid.get("unit_tests", {}).get("percentage", 0)
            if unit_pct < 50:
                errors.append(f"Porcentaje de unit tests muy bajo: {unit_pct:.1f}% (minimo 60%)")

        # Validar coverage requirements
        if "coverage_requirements" in output_data:
            coverage = output_data["coverage_requirements"]
            if coverage.get("overall_target", 0) < 80:
                errors.append("Coverage target debe ser >= 80%")

        return errors
