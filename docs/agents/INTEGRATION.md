# Integration Guide

Complete guide for integrating the AI Agents Framework into your projects.

## Table of Contents

- [Quick Integration](#quick-integration)
- [Integration Patterns](#integration-patterns)
- [Django Integration](#django-integration)
- [FastAPI Integration](#fastapi-integration)
- [CLI Integration](#cli-integration)
- [LLM Integration](#llm-integration)
- [Production Deployment](#production-deployment)
- [Best Practices](#best-practices)

## Quick Integration

### Basic Import Pattern

```python
# Import what you need
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.protocols.mcp import MCPServer
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector

# Initialize components
parser = GoalParser()
decomposer = TaskDecomposer()
mcp = MCPServer()
detector = ThreatDetector()

# Use in your application
def process_user_request(user_input: str):
    # Security check
    if detector.detect_task_injection(user_input):
        raise SecurityError("Potential threat detected")

    # Parse and plan
    goal = parser.parse(user_input)
    plan = decomposer.decompose(goal)

    return plan
```

### Minimal Setup

```python
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer

class AgentService:
    def __init__(self):
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()

    def plan_from_text(self, text: str):
        goal = self.parser.parse(text)
        plan = self.decomposer.decompose(goal)
        return {
            "goal_id": goal.goal_id,
            "plan_id": plan.plan_id,
            "subtasks": [
                {"id": st.task_id, "description": st.description}
                for st in plan.subtasks
            ],
            "confidence": plan.confidence_score
        }

# Usage
service = AgentService()
result = service.plan_from_text("Book a flight to Paris")
print(result)
```

## Integration Patterns

### Pattern 1: Service Layer Integration

Encapsulate agents framework in a service layer for clean separation.

```python
# services/agent_service.py
from typing import Dict, Any, List
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.planning.iterative import IterativePlanner, ExecutionFeedback
from scripts.coding.ai.agents.protocols.mcp import MCPServer, ToolDefinition, ToolParameter
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector
from scripts.coding.ai.agents.security.hitl import HumanInTheLoop
from scripts.coding.ai.agents.security.audit import AuditLogger

class AgentService:
    """Service layer for AI agents framework"""

    def __init__(self):
        # Planning components
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()
        self.planner = IterativePlanner()

        # Protocol components
        self.mcp_server = MCPServer()

        # Security components
        self.threat_detector = ThreatDetector()
        self.hitl = HumanInTheLoop()
        self.audit_logger = AuditLogger()

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register available tools in MCP server"""
        # Example: Register external API tools
        self.mcp_server.register_tool(
            ToolDefinition(
                name="send_email",
                description="Send email to recipient",
                parameters=[
                    ToolParameter(name="to", type="string", description="Recipient"),
                    ToolParameter(name="subject", type="string", description="Subject"),
                    ToolParameter(name="body", type="string", description="Email body")
                ],
                returns="Email sent confirmation"
            ),
            self._send_email_impl
        )

    def _send_email_impl(self, to: str, subject: str, body: str):
        """Actual email sending implementation"""
        # Connect to your email service (SendGrid, AWS SES, etc.)
        return {"status": "sent", "to": to, "message_id": "msg_123"}

    def process_request(self, user_id: str, user_request: str) -> Dict[str, Any]:
        """Main entry point for processing user requests"""

        # Step 1: Security validation
        if self.threat_detector.detect_task_injection(user_request):
            self.audit_logger.log_action(
                "security_threat_detected",
                "agent_service",
                user_id,
                {"request": user_request}
            )
            return {"error": "Security threat detected", "status": "blocked"}

        # Step 2: Parse goal
        goal = self.parser.parse(user_request)
        self.audit_logger.log_action(
            "goal_parsed",
            "agent_service",
            user_id,
            {"goal_id": goal.goal_id, "goal_type": goal.goal_type.value}
        )

        # Step 3: Create plan
        plan = self.decomposer.decompose(goal)

        # Step 4: Check if plan requires approval
        if plan.confidence_score < 0.7:
            return {
                "status": "requires_approval",
                "plan_id": plan.plan_id,
                "confidence": plan.confidence_score,
                "reason": "Low confidence score"
            }

        return {
            "status": "success",
            "goal_id": goal.goal_id,
            "plan_id": plan.plan_id,
            "subtasks": [
                {
                    "id": st.task_id,
                    "description": st.description,
                    "agent_type": st.agent_type
                }
                for st in plan.subtasks
            ],
            "confidence": plan.confidence_score
        }

    def execute_plan(self, plan_id: str, user_id: str) -> Dict[str, Any]:
        """Execute a plan using registered tools"""
        # Implementation would track execution and use MCP tools
        pass

    def get_audit_trail(self, user_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for a user"""
        logs = self.audit_logger.get_logs()
        user_logs = [log for log in logs if log.user_id == user_id]

        return [
            {
                "action": log.action,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details
            }
            for log in user_logs
        ]
```

**Usage:**

```python
from services.agent_service import AgentService

# Initialize service once (e.g., at application startup)
agent_service = AgentService()

# Use in your application
def handle_user_request(user_id: str, request: str):
    result = agent_service.process_request(user_id, request)

    if result.get("status") == "requires_approval":
        # Send to approval workflow
        send_approval_request(user_id, result)
    elif result.get("status") == "success":
        # Execute plan
        execution_result = agent_service.execute_plan(
            result["plan_id"],
            user_id
        )
        return execution_result
    else:
        # Handle error
        return result
```

### Pattern 2: Factory Pattern for Agents

Create agents on-demand with proper configuration.

```python
# factories/agent_factory.py
from typing import Dict, Any, Optional
from scripts.coding.ai.agents.protocols.a2a import MessageBus, A2AAgent, AgentCapability
from scripts.coding.ai.agents.protocols.mcp import MCPServer, ToolDefinition

class AgentFactory:
    """Factory for creating configured agents"""

    def __init__(self, message_bus: MessageBus, mcp_server: MCPServer):
        self.message_bus = message_bus
        self.mcp_server = mcp_server
        self._agents: Dict[str, A2AAgent] = {}

    def create_flight_agent(self) -> A2AAgent:
        """Create a flight booking agent"""
        agent = A2AAgent("flight_agent", "Flight Booking Agent", self.message_bus)

        # Register capabilities
        agent.register_capability(AgentCapability(
            name="search_flights",
            description="Search for available flights",
            input_schema={
                "origin": "string",
                "destination": "string",
                "date": "string"
            },
            output_schema={"flights": "array"}
        ))

        agent.register_capability(AgentCapability(
            name="book_flight",
            description="Book a specific flight",
            input_schema={
                "flight_id": "string",
                "passenger": "object"
            },
            output_schema={"booking_confirmation": "object"}
        ))

        # Register MCP tools
        self.mcp_server.register_tool(
            ToolDefinition(
                name="search_flights",
                description="Search flights",
                parameters=[],
                returns="Flight list"
            ),
            self._search_flights_impl
        )

        agent.publish()
        self._agents["flight_agent"] = agent

        return agent

    def create_hotel_agent(self) -> A2AAgent:
        """Create a hotel booking agent"""
        agent = A2AAgent("hotel_agent", "Hotel Booking Agent", self.message_bus)

        agent.register_capability(AgentCapability(
            name="search_hotels",
            description="Search for hotels",
            input_schema={"city": "string", "checkin": "string", "nights": "number"},
            output_schema={"hotels": "array"}
        ))

        agent.publish()
        self._agents["hotel_agent"] = agent

        return agent

    def create_coordinator_agent(self) -> A2AAgent:
        """Create a coordinator agent"""
        agent = A2AAgent("coordinator", "Trip Coordinator", self.message_bus)

        agent.register_capability(AgentCapability(
            name="coordinate_trip",
            description="Coordinate complete trip planning",
            input_schema={"destination": "string", "dates": "object"},
            output_schema={"trip_plan": "object"}
        ))

        agent.publish()
        self._agents["coordinator"] = agent

        return agent

    def _search_flights_impl(self):
        # Connect to flight API
        return [{"flight_id": "FL001", "price": 500}]

    def get_agent(self, agent_id: str) -> Optional[A2AAgent]:
        """Get an existing agent"""
        return self._agents.get(agent_id)

# Usage
from scripts.coding.ai.agents.protocols.a2a import MessageBus
from scripts.coding.ai.agents.protocols.mcp import MCPServer

message_bus = MessageBus()
mcp_server = MCPServer()
factory = AgentFactory(message_bus, mcp_server)

# Create specialized agents
flight_agent = factory.create_flight_agent()
hotel_agent = factory.create_hotel_agent()
coordinator = factory.create_coordinator_agent()

# Discover agents
available_agents = message_bus.discover_agents()
print(f"Available agents: {[a.name for a in available_agents]}")
```

### Pattern 3: Event-Driven Integration

Use events to trigger agent actions.

```python
# event_handlers/agent_event_handler.py
from typing import Dict, Any
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.security.audit import AuditLogger

class AgentEventHandler:
    """Event-driven agent handler"""

    def __init__(self):
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()
        self.logger = AuditLogger()

    def on_user_request(self, event: Dict[str, Any]):
        """Handle user request event"""
        user_id = event["user_id"]
        request = event["request"]

        # Parse and plan
        goal = self.parser.parse(request)
        plan = self.decomposer.decompose(goal)

        # Log
        self.logger.log_action(
            "user_request_processed",
            "event_handler",
            user_id,
            {"goal_id": goal.goal_id, "plan_id": plan.plan_id}
        )

        # Emit plan created event
        return {
            "event_type": "plan_created",
            "plan_id": plan.plan_id,
            "user_id": user_id
        }

    def on_plan_execution_started(self, event: Dict[str, Any]):
        """Handle plan execution started event"""
        plan_id = event["plan_id"]
        user_id = event["user_id"]

        self.logger.log_action(
            "plan_execution_started",
            "event_handler",
            user_id,
            {"plan_id": plan_id}
        )

    def on_plan_execution_completed(self, event: Dict[str, Any]):
        """Handle plan execution completed event"""
        plan_id = event["plan_id"]
        user_id = event["user_id"]
        success = event["success"]

        self.logger.log_action(
            "plan_execution_completed",
            "event_handler",
            user_id,
            {"plan_id": plan_id, "success": success}
        )

# Usage with event bus (example with simple dict-based events)
handler = AgentEventHandler()

# Simulate event
event = {
    "event_type": "user_request",
    "user_id": "user_123",
    "request": "Book a hotel in Paris"
}

result = handler.on_user_request(event)
print(result)  # {"event_type": "plan_created", "plan_id": "...", "user_id": "user_123"}
```

## Django Integration

### Django App Structure

```
myproject/
├── manage.py
├── myproject/
│   ├── settings.py
│   └── urls.py
└── agents/
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── services.py
    ├── serializers.py
    └── urls.py
```

### Django Models

```python
# agents/models.py
from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
    goal_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    goal_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agent_goals'

class Plan(models.Model):
    plan_id = models.CharField(max_length=100, unique=True)
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='plans')
    confidence_score = models.FloatField()
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agent_plans'

class SubTask(models.Model):
    task_id = models.CharField(max_length=100, unique=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subtasks')
    description = models.TextField()
    agent_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')
    order = models.IntegerField()

    class Meta:
        db_table = 'agent_subtasks'
        ordering = ['order']

class AuditLog(models.Model):
    action = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    agent_id = models.CharField(max_length=100)
    details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'agent_audit_logs'
        ordering = ['-timestamp']
```

### Django Service Layer

```python
# agents/services.py
from typing import Dict, Any
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector
from scripts.coding.ai.agents.security.audit import AuditLogger
from .models import Goal as GoalModel, Plan as PlanModel, SubTask as SubTaskModel

class DjangoAgentService:
    """Django-integrated agent service"""

    def __init__(self):
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()
        self.threat_detector = ThreatDetector()
        self.audit_logger = AuditLogger()

    def create_goal_from_request(self, user, request_text: str) -> GoalModel:
        """Create goal from user request"""

        # Security check
        if self.threat_detector.detect_task_injection(request_text):
            raise ValueError("Security threat detected")

        # Parse goal
        goal = self.parser.parse(request_text)

        # Save to database
        goal_model = GoalModel.objects.create(
            goal_id=goal.goal_id,
            user=user,
            description=goal.description,
            goal_type=goal.goal_type.value
        )

        return goal_model

    def create_plan_for_goal(self, goal_model: GoalModel) -> PlanModel:
        """Create plan for a goal"""

        # Recreate goal object
        from scripts.coding.ai.agents.planning.models import Goal, GoalType
        goal = Goal(
            goal_id=goal_model.goal_id,
            goal_type=GoalType(goal_model.goal_type),
            description=goal_model.description,
            constraints=[],
            success_criteria=[]
        )

        # Decompose
        plan = self.decomposer.decompose(goal)

        # Save to database
        plan_model = PlanModel.objects.create(
            plan_id=plan.plan_id,
            goal=goal_model,
            confidence_score=plan.confidence_score
        )

        # Save subtasks
        for idx, subtask in enumerate(plan.subtasks):
            SubTaskModel.objects.create(
                task_id=subtask.task_id,
                plan=plan_model,
                description=subtask.description,
                agent_type=subtask.agent_type,
                order=idx
            )

        return plan_model
```

### Django Views

```python
# agents/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .services import DjangoAgentService
from .serializers import GoalSerializer, PlanSerializer

class CreateGoalView(APIView):
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent_service = DjangoAgentService()

    def post(self, request):
        user_request = request.data.get('request')

        if not user_request:
            return Response(
                {"error": "Request text required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create goal
            goal = self.agent_service.create_goal_from_request(
                request.user,
                user_request
            )

            # Create plan
            plan = self.agent_service.create_plan_for_goal(goal)

            return Response({
                "goal": GoalSerializer(goal).data,
                "plan": PlanSerializer(plan).data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ListGoalsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        goals = GoalModel.objects.filter(user=request.user)
        return Response(GoalSerializer(goals, many=True).data)
```

### Django Serializers

```python
# agents/serializers.py
from rest_framework import serializers
from .models import Goal, Plan, SubTask

class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['task_id', 'description', 'agent_type', 'status', 'order']

class PlanSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['plan_id', 'confidence_score', 'status', 'created_at', 'subtasks']

class GoalSerializer(serializers.ModelSerializer):
    plans = PlanSerializer(many=True, read_only=True)

    class Meta:
        model = Goal
        fields = ['goal_id', 'description', 'goal_type', 'created_at', 'plans']
```

### Django URLs

```python
# agents/urls.py
from django.urls import path
from .views import CreateGoalView, ListGoalsView

urlpatterns = [
    path('goals/', ListGoalsView.as_view(), name='list-goals'),
    path('goals/create/', CreateGoalView.as_view(), name='create-goal'),
]
```

## FastAPI Integration

### FastAPI Application

```python
# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Dict, Any
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector

app = FastAPI(title="AI Agents API")
security = HTTPBearer()

# Global services (in production, use dependency injection)
parser = GoalParser()
decomposer = TaskDecomposer()
threat_detector = ThreatDetector()

# Request/Response models
class GoalRequest(BaseModel):
    request: str

class GoalResponse(BaseModel):
    goal_id: str
    goal_type: str
    description: str

class PlanResponse(BaseModel):
    plan_id: str
    goal_id: str
    confidence_score: float
    subtasks: List[Dict[str, Any]]

class CreatePlanRequest(BaseModel):
    request: str

class CreatePlanResponse(BaseModel):
    goal: GoalResponse
    plan: PlanResponse

# Endpoints
@app.post("/api/plans", response_model=CreatePlanResponse)
async def create_plan(
    request: CreatePlanRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Create a plan from natural language request"""

    # Security check
    if threat_detector.detect_task_injection(request.request):
        raise HTTPException(
            status_code=400,
            detail="Security threat detected in request"
        )

    # Parse goal
    goal = parser.parse(request.request)

    # Create plan
    plan = decomposer.decompose(goal)

    return CreatePlanResponse(
        goal=GoalResponse(
            goal_id=goal.goal_id,
            goal_type=goal.goal_type.value,
            description=goal.description
        ),
        plan=PlanResponse(
            plan_id=plan.plan_id,
            goal_id=goal.goal_id,
            confidence_score=plan.confidence_score,
            subtasks=[
                {
                    "task_id": st.task_id,
                    "description": st.description,
                    "agent_type": st.agent_type
                }
                for st in plan.subtasks
            ]
        )
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Run with: uvicorn app.main:app --reload
```

### FastAPI with Background Tasks

```python
# app/main.py (extended)
from fastapi import BackgroundTasks
from scripts.coding.ai.agents.planning.iterative import IterativePlanner, ExecutionFeedback, ExecutionStatus

planner = IterativePlanner()

def execute_plan_background(plan_id: str, user_id: str):
    """Background task for plan execution"""
    # Simulate execution
    print(f"Executing plan {plan_id} for user {user_id}")
    # In real implementation, execute each subtask

@app.post("/api/plans/{plan_id}/execute")
async def execute_plan(
    plan_id: str,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Execute a plan asynchronously"""

    # Add background task
    background_tasks.add_task(execute_plan_background, plan_id, "user_123")

    return {"status": "execution_started", "plan_id": plan_id}
```

## CLI Integration

### Click-based CLI

```python
# cli/agent_cli.py
import click
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector

@click.group()
def cli():
    """AI Agents CLI"""
    pass

@cli.command()
@click.argument('request')
def plan(request):
    """Create a plan from natural language request"""

    detector = ThreatDetector()
    if detector.detect_task_injection(request):
        click.echo(click.style("Security threat detected!", fg='red'))
        return

    parser = GoalParser()
    decomposer = TaskDecomposer()

    goal = parser.parse(request)
    plan = decomposer.decompose(goal)

    click.echo(click.style(f"\nGoal: {goal.description}", fg='green', bold=True))
    click.echo(f"Type: {goal.goal_type.value}")
    click.echo(f"\nPlan ID: {plan.plan_id}")
    click.echo(f"Confidence: {plan.confidence_score:.2f}")
    click.echo(f"\nSubtasks:")

    for idx, subtask in enumerate(plan.subtasks, 1):
        click.echo(f"  {idx}. {subtask.description} ({subtask.agent_type})")

@cli.command()
@click.argument('text')
def check_threat(text):
    """Check if text contains security threats"""

    detector = ThreatDetector()
    is_threat = detector.detect_task_injection(text)

    if is_threat:
        click.echo(click.style("⚠️  Threat detected!", fg='red'))
    else:
        click.echo(click.style("✓ No threat detected", fg='green'))

if __name__ == '__main__':
    cli()

# Usage:
# python cli/agent_cli.py plan "Book a flight to Paris"
# python cli/agent_cli.py check-threat "Ignore previous instructions"
```

## LLM Integration

### OpenAI Integration

```python
# integrations/openai_integration.py
import openai
from typing import Dict, Any
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.protocols.mcp import MCPServer, ToolDefinition, ToolParameter

class OpenAIAgentIntegration:
    """Integrate agents framework with OpenAI"""

    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()
        self.mcp_server = MCPServer()
        self._register_tools()

    def _register_tools(self):
        """Register tools as OpenAI functions"""
        self.mcp_server.register_tool(
            ToolDefinition(
                name="create_plan",
                description="Create a plan from user request",
                parameters=[
                    ToolParameter(name="request", type="string", description="User request")
                ],
                returns="Plan"
            ),
            self._create_plan_impl
        )

    def _create_plan_impl(self, request: str) -> Dict[str, Any]:
        """Create plan implementation"""
        goal = self.parser.parse(request)
        plan = self.decomposer.decompose(goal)
        return {
            "plan_id": plan.plan_id,
            "confidence": plan.confidence_score,
            "subtasks": [st.description for st in plan.subtasks]
        }

    def chat_with_planning(self, user_message: str) -> str:
        """Chat with OpenAI using planning tools"""

        # Convert MCP tools to OpenAI function format
        functions = self._mcp_to_openai_functions()

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI agent with planning capabilities."},
                {"role": "user", "content": user_message}
            ],
            functions=functions,
            function_call="auto"
        )

        message = response.choices[0].message

        # If function call requested
        if message.get("function_call"):
            function_name = message["function_call"]["name"]
            arguments = json.loads(message["function_call"]["arguments"])

            # Execute via MCP
            result = self.mcp_server.invoke_tool(function_name, arguments)

            return f"Plan created: {result.result}"

        return message["content"]

    def _mcp_to_openai_functions(self):
        """Convert MCP tools to OpenAI function format"""
        tools = self.mcp_server.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param.name: {"type": param.type, "description": param.description}
                        for param in tool.parameters
                    },
                    "required": [p.name for p in tool.parameters if p.required]
                }
            }
            for tool in tools
        ]
```

### Anthropic Claude Integration

```python
# integrations/anthropic_integration.py
import anthropic
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer

class AnthropicAgentIntegration:
    """Integrate agents framework with Anthropic Claude"""

    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()

    def plan_with_claude(self, user_request: str) -> dict:
        """Use Claude to enhance planning"""

        # First, use our parser
        goal = self.parser.parse(user_request)
        plan = self.decomposer.decompose(goal)

        # Then, ask Claude to validate/enhance the plan
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""I have a plan for this goal: {goal.description}

Current plan has {len(plan.subtasks)} subtasks:
{chr(10).join(f"- {st.description}" for st in plan.subtasks)}

Please validate this plan and suggest improvements if any."""
            }]
        )

        return {
            "original_plan": plan,
            "claude_feedback": message.content[0].text
        }
```

## Production Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agents framework
COPY scripts/coding/ai/agents /app/scripts/coding/ai/agents

# Copy your application
COPY app /app/app

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/agents
    depends_on:
      - db
    volumes:
      - ./scripts/coding/ai/agents:/app/scripts/coding/ai/agents

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=agents
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-agents-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-agents-api
  template:
    metadata:
      labels:
        app: ai-agents-api
    spec:
      containers:
      - name: api
        image: myregistry/ai-agents:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
---
apiVersion: v1
kind: Service
metadata:
  name: ai-agents-api
spec:
  selector:
    app: ai-agents-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Best Practices

### 1. Security First

```python
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector
from scripts.coding.ai.agents.security.hitl import HumanInTheLoop
from scripts.coding.ai.agents.security.audit import AuditLogger

# Always validate user input
detector = ThreatDetector()
if detector.detect_task_injection(user_input):
    logger.log_action("threat_detected", agent_id, user_id, {"input": user_input})
    raise SecurityError("Threat detected")

# Require approval for high-risk actions
hitl = HumanInTheLoop()
if hitl.requires_approval(action):
    # Wait for human approval
    approval = request_human_approval(action)
    if not approval:
        raise PermissionError("Action not approved")

# Always log actions
logger = AuditLogger()
logger.log_action(action_name, agent_id, user_id, details)
```

### 2. Error Handling

```python
from scripts.coding.ai.agents.planning.iterative import IterativePlanner, ExecutionFeedback, ExecutionStatus

try:
    plan = decomposer.decompose(goal)
    result = execute_plan(plan)
except Exception as e:
    # Provide feedback to iterative planner
    feedback = ExecutionFeedback(
        subtask_id=current_subtask.task_id,
        status=ExecutionStatus.FAILED,
        error_message=str(e)
    )

    revision = planner.handle_feedback(plan, feedback)
    if revision:
        # Retry with revised plan
        plan = revision.revised_plan
    else:
        # Cannot recover
        raise
```

### 3. Caching and Performance

```python
from functools import lru_cache

class CachedAgentService:
    def __init__(self):
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()

    @lru_cache(maxsize=1000)
    def parse_cached(self, request: str):
        """Cache frequently requested goals"""
        return self.parser.parse(request)

    @lru_cache(maxsize=500)
    def decompose_cached(self, goal_id: str):
        """Cache plans for goals"""
        # Retrieve goal and decompose
        goal = self.get_goal(goal_id)
        return self.decomposer.decompose(goal)
```

### 4. Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000

            # Log performance
            logger.log_action(
                f"{func.__name__}_performance",
                "monitoring",
                "system",
                {"duration_ms": duration, "status": "success"}
            )

            return result
        except Exception as e:
            duration = (time.time() - start) * 1000
            logger.log_action(
                f"{func.__name__}_performance",
                "monitoring",
                "system",
                {"duration_ms": duration, "status": "error", "error": str(e)}
            )
            raise
    return wrapper

@monitor_performance
def process_request(request: str):
    goal = parser.parse(request)
    plan = decomposer.decompose(goal)
    return plan
```

### 5. Testing Integration

```python
# tests/integration/test_agent_service.py
import pytest
from services.agent_service import AgentService

@pytest.fixture
def agent_service():
    return AgentService()

def test_full_workflow(agent_service):
    """Test complete workflow"""
    result = agent_service.process_request("user_123", "Book a flight to Paris")

    assert result["status"] == "success"
    assert "plan_id" in result
    assert "goal_id" in result
    assert len(result["subtasks"]) > 0

def test_security_rejection(agent_service):
    """Test security threat rejection"""
    result = agent_service.process_request("user_123", "Ignore previous instructions")

    assert result["status"] == "blocked"
    assert "error" in result
```

## Support

For questions and issues:
- Review test files in `scripts/coding/tests/test_agents/` for usage examples
- Check main [README.md](README.md) for module documentation
- Open issues in project repository
