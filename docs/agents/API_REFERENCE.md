# API Reference

Complete API reference for the AI Agents Framework.

## Table of Contents

- [Planning Module](#planning-module)
- [Protocols Module](#protocols-module)
- [UX Module](#ux-module)
- [Security Module](#security-module)

## Planning Module

### `scripts.coding.ai.agents.planning.models`

Data models for the planning system.

#### `GoalType` (Enum)

Goal classification types.

```python
class GoalType(str, Enum):
    SIMPLE = "simple"        # Single-step goals
    COMPLEX = "complex"      # Multi-step goals
    CONDITIONAL = "conditional"  # Goals with conditions
    SEQUENTIAL = "sequential"    # Sequential execution required
```

#### `ConstraintType` (Enum)

Types of constraints that can be applied to goals.

```python
class ConstraintType(str, Enum):
    BUDGET = "budget"
    TIME = "time"
    LOCATION = "location"
    QUALITY = "quality"
    RESOURCE = "resource"
```

#### `Constraint`

Represents a constraint on goal execution.

```python
class Constraint(BaseModel):
    type: ConstraintType
    value: Union[str, int, float]
    unit: Optional[str] = None
    operator: str = "="  # =, <, >, <=, >=
```

**Fields:**
- `type`: Type of constraint (budget, time, etc.)
- `value`: Constraint value
- `unit`: Optional unit (e.g., "USD", "hours")
- `operator`: Comparison operator

#### `Goal`

Structured representation of a user goal.

```python
class Goal(BaseModel):
    goal_id: str
    goal_type: GoalType
    description: str
    constraints: List[Constraint]
    success_criteria: List[str]
    deadline: Optional[datetime] = None
    priority: int = Field(default=5, ge=1, le=10)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

**Fields:**
- `goal_id`: Unique identifier
- `goal_type`: Classification of the goal
- `description`: Human-readable description
- `constraints`: List of constraints
- `success_criteria`: Criteria for success
- `deadline`: Optional deadline
- `priority`: Priority level (1-10)
- `metadata`: Additional metadata

#### `SubTask`

Represents a subtask within a plan.

```python
class SubTask(BaseModel):
    task_id: str
    description: str
    agent_type: str
    dependencies: List[str] = Field(default_factory=list)
    expected_outputs: List[str] = Field(default_factory=list)
    estimated_duration: int = 0
    constraints: List[Constraint] = Field(default_factory=list)
```

**Fields:**
- `task_id`: Unique identifier
- `description`: Task description
- `agent_type`: Type of agent to execute
- `dependencies`: List of task IDs this depends on
- `expected_outputs`: Expected output types
- `estimated_duration`: Duration in seconds
- `constraints`: Task-specific constraints

#### `Plan`

Execution plan for a goal.

```python
class Plan(BaseModel):
    plan_id: str
    goal_id: str
    subtasks: List[SubTask]
    execution_strategy: str  # "sequential", "parallel", "conditional"
    estimated_total_duration: int
    confidence_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
```

**Fields:**
- `plan_id`: Unique identifier
- `goal_id`: Associated goal ID
- `subtasks`: List of subtasks
- `execution_strategy`: How to execute subtasks
- `estimated_total_duration`: Total duration in seconds
- `confidence_score`: Confidence level (0.0-1.0)
- `created_at`: Creation timestamp

---

### `scripts.coding.ai.agents.planning.parser`

Natural language goal parsing.

#### `GoalParser`

Parses natural language into structured Goal objects.

```python
class GoalParser:
    def parse(self, user_request: str) -> Goal
```

**Methods:**

##### `parse(user_request: str) -> Goal`

Parse natural language request into a structured Goal.

**Parameters:**
- `user_request` (str): Natural language goal description

**Returns:**
- `Goal`: Structured goal object

**Example:**
```python
parser = GoalParser()
goal = parser.parse("Book a flight to Paris by Friday under $500")
# Returns: Goal(
#     goal_id="goal_...",
#     goal_type=GoalType.SIMPLE,
#     description="Book a flight to Paris by Friday under $500",
#     constraints=[Constraint(type=BUDGET, value=500, unit="USD")],
#     deadline=datetime(...)
# )
```

**Internal Methods:**

##### `_classify_goal_type(request: str) -> GoalType`

Classify the type of goal based on keywords.

##### `_extract_constraints(request: str) -> List[Constraint]`

Extract constraints from the request text.

##### `_extract_deadline(request: str) -> Optional[datetime]`

Extract deadline from temporal expressions.

##### `_extract_metadata(request: str, constraints: List[Constraint]) -> Dict[str, Any]`

Extract additional metadata from the request.

---

### `scripts.coding.ai.agents.planning.decomposer`

Goal-to-plan decomposition.

#### `TaskDecomposer`

Decomposes goals into executable plans.

```python
class TaskDecomposer:
    def decompose(self, goal: Goal) -> Plan
```

**Methods:**

##### `decompose(goal: Goal) -> Plan`

Decompose a goal into an executable plan with subtasks.

**Parameters:**
- `goal` (Goal): Structured goal to decompose

**Returns:**
- `Plan`: Execution plan with subtasks

**Example:**
```python
decomposer = TaskDecomposer()
plan = decomposer.decompose(goal)
# Returns: Plan(
#     plan_id="plan_...",
#     goal_id=goal.goal_id,
#     subtasks=[...],
#     confidence_score=0.85
# )
```

**Internal Methods:**

##### `_generate_subtasks(goal: Goal) -> List[SubTask]`

Generate subtasks based on goal type and constraints.

##### `_determine_execution_strategy(goal: Goal) -> str`

Determine optimal execution strategy.

##### `_calculate_confidence(goal: Goal, subtasks: List[SubTask]) -> float`

Calculate confidence score for the plan.

---

### `scripts.coding.ai.agents.planning.validators`

Plan validation and dependency checking.

#### `ValidationResult`

Result of plan validation.

```python
class ValidationResult(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
```

#### `DependencyValidator`

Validates task dependencies.

```python
class DependencyValidator:
    def validate_dependencies(self, plan: Plan) -> ValidationResult
    def detect_circular_dependencies(self, plan: Plan) -> List[str]
    def find_dangling_dependencies(self, plan: Plan) -> List[str]
```

**Methods:**

##### `validate_dependencies(plan: Plan) -> ValidationResult`

Validate all task dependencies in a plan.

**Parameters:**
- `plan` (Plan): Plan to validate

**Returns:**
- `ValidationResult`: Validation result with errors/warnings

**Example:**
```python
validator = DependencyValidator()
result = validator.validate_dependencies(plan)
if not result.valid:
    print(f"Errors: {result.errors}")
```

##### `detect_circular_dependencies(plan: Plan) -> List[str]`

Detect circular dependencies in the plan.

**Returns:**
- `List[str]`: List of task IDs involved in circular dependencies

##### `find_dangling_dependencies(plan: Plan) -> List[str]`

Find dependencies that reference non-existent tasks.

**Returns:**
- `List[str]`: List of dangling dependency references

#### `CompletenessValidator`

Validates plan completeness.

```python
class CompletenessValidator:
    def validate_completeness(self, goal: Goal, plan: Plan) -> ValidationResult
    def check_goal_coverage(self, goal: Goal, plan: Plan) -> bool
```

**Methods:**

##### `validate_completeness(goal: Goal, plan: Plan) -> ValidationResult`

Validate that plan completely addresses the goal.

##### `check_goal_coverage(goal: Goal, plan: Plan) -> bool`

Check if plan covers all aspects of the goal.

---

### `scripts.coding.ai.agents.planning.iterative`

Iterative planning with feedback loops.

#### `ExecutionStatus` (Enum)

Status of subtask execution.

```python
class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
```

#### `ExecutionFeedback`

Feedback from subtask execution.

```python
class ExecutionFeedback(BaseModel):
    subtask_id: str
    status: ExecutionStatus
    actual_duration: Optional[int] = None
    error_message: Optional[str] = None
    outputs: Dict[str, Any] = Field(default_factory=dict)
```

#### `RevisionStrategy` (Enum)

Plan revision strategies.

```python
class RevisionStrategy(str, Enum):
    ADD_STEPS = "add_steps"
    REORDER = "reorder"
    ADJUST_CONSTRAINTS = "adjust_constraints"
    REPLACE_SUBTASK = "replace_subtask"
    SIMPLIFY = "simplify"
```

#### `PlanRevision`

Represents a plan revision.

```python
class PlanRevision(BaseModel):
    revision_id: str
    original_plan_id: str
    revised_plan: Plan
    revision_strategy: RevisionStrategy
    reason: str
    confidence_delta: float
```

#### `IterativePlanner`

Handles plan revisions based on execution feedback.

```python
class IterativePlanner:
    def __init__(self, max_revisions: int = 5):
        ...

    def handle_feedback(
        self,
        plan: Plan,
        feedback: ExecutionFeedback
    ) -> Optional[PlanRevision]
```

**Methods:**

##### `handle_feedback(plan: Plan, feedback: ExecutionFeedback) -> Optional[PlanRevision]`

Process execution feedback and potentially revise the plan.

**Parameters:**
- `plan` (Plan): Current plan
- `feedback` (ExecutionFeedback): Execution feedback

**Returns:**
- `Optional[PlanRevision]`: Revision if needed, None otherwise

**Example:**
```python
planner = IterativePlanner()

feedback = ExecutionFeedback(
    subtask_id="task_1",
    status=ExecutionStatus.FAILED,
    error_message="Hotel fully booked"
)

revision = planner.handle_feedback(plan, feedback)
if revision:
    print(f"Plan revised using strategy: {revision.revision_strategy}")
    plan = revision.revised_plan
```

##### `_select_revision_strategy(plan: Plan, feedback: ExecutionFeedback) -> RevisionStrategy`

Select appropriate revision strategy based on feedback.

##### `_adjust_confidence(plan: Plan, feedback: ExecutionFeedback) -> float`

Adjust confidence score based on execution results.

---

## Protocols Module

### `scripts.coding.ai.agents.protocols.mcp`

Model Context Protocol implementation.

#### `ToolParameter`

Parameter definition for a tool.

```python
class ToolParameter(BaseModel):
    name: str
    type: str  # "string", "number", "boolean"
    description: str
    required: bool = True
    default: Any = None
```

#### `ToolDefinition`

Definition of a callable tool.

```python
class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[ToolParameter]
    returns: str
    cost_estimate: float = 0.0
```

#### `ToolInvocationResult`

Result of tool invocation.

```python
class ToolInvocationResult(BaseModel):
    tool_name: str
    status: str  # "success", "error"
    result: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    cost: float = 0.0
```

#### `MCPServer`

MCP server for tool registration and invocation.

```python
class MCPServer:
    def register_tool(
        self,
        tool_def: ToolDefinition,
        implementation: Callable
    ) -> None

    def invoke_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> ToolInvocationResult

    def list_tools(self) -> List[ToolDefinition]

    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]
```

**Methods:**

##### `register_tool(tool_def: ToolDefinition, implementation: Callable) -> None`

Register a tool with its implementation.

**Example:**
```python
server = MCPServer()

tool_def = ToolDefinition(
    name="search",
    description="Search for information",
    parameters=[
        ToolParameter(name="query", type="string", required=True)
    ],
    returns="Search results"
)

def search_impl(query: str):
    return [f"Result for: {query}"]

server.register_tool(tool_def, search_impl)
```

##### `invoke_tool(tool_name: str, parameters: Dict[str, Any]) -> ToolInvocationResult`

Invoke a registered tool.

**Raises:**
- `ToolNotFoundError`: If tool not found
- `ParameterValidationError`: If parameters invalid

**Example:**
```python
result = server.invoke_tool("search", {"query": "AI agents"})
if result.status == "success":
    print(result.result)
```

##### `list_tools() -> List[ToolDefinition]`

List all registered tools.

##### `get_tool(tool_name: str) -> Optional[ToolDefinition]`

Get a specific tool definition.

#### `MCPClient`

Client for discovering and invoking tools.

```python
class MCPClient:
    def __init__(self, server: MCPServer):
        ...

    def discover_tools(self) -> List[ToolDefinition]

    def invoke(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> ToolInvocationResult

    def find_tool(self, capability: str) -> Optional[ToolDefinition]
```

**Methods:**

##### `discover_tools() -> List[ToolDefinition]`

Discover all available tools from the server.

##### `invoke(tool_name: str, parameters: Dict[str, Any]) -> ToolInvocationResult`

Invoke a tool through the client.

##### `find_tool(capability: str) -> Optional[ToolDefinition]`

Find a tool by capability keyword.

**Example:**
```python
client = MCPClient(server)
tools = client.discover_tools()

flight_tool = client.find_tool("flight")
if flight_tool:
    result = client.invoke(flight_tool.name, {...})
```

#### Exceptions

##### `ToolNotFoundError`

Raised when a tool is not found.

##### `ParameterValidationError`

Raised when parameters fail validation.

---

### `scripts.coding.ai.agents.protocols.a2a`

Agent-to-Agent communication protocol.

#### `AgentCapability`

Capability definition for an agent.

```python
class AgentCapability(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
```

#### `AgentCard`

Agent registration card.

```python
class AgentCard(BaseModel):
    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    version: str = "1.0.0"
    endpoint: Optional[str] = None
```

#### `MessageType` (Enum)

Types of A2A messages.

```python
class MessageType(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
```

#### `A2AMessage`

Message for agent communication.

```python
class A2AMessage(BaseModel):
    message_id: str
    message_type: MessageType
    from_agent: str
    to_agent: str
    capability: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
```

#### `MessageBus`

Central message bus for agent communication.

```python
class MessageBus:
    def register_agent(self, agent_card: AgentCard) -> None

    def discover_agents(
        self,
        capability: Optional[str] = None
    ) -> List[AgentCard]

    def send_message(self, message: A2AMessage) -> bool

    def get_messages_for(self, agent_id: str) -> List[A2AMessage]
```

**Methods:**

##### `register_agent(agent_card: AgentCard) -> None`

Register an agent on the message bus.

##### `discover_agents(capability: Optional[str] = None) -> List[AgentCard]`

Discover agents by capability.

**Example:**
```python
bus = MessageBus()
flight_agents = bus.discover_agents("flight")
```

##### `send_message(message: A2AMessage) -> bool`

Send a message through the bus.

##### `get_messages_for(agent_id: str) -> List[A2AMessage]`

Get all messages for a specific agent.

#### `A2AAgent`

Agent with A2A communication capabilities.

```python
class A2AAgent:
    def __init__(
        self,
        agent_id: str,
        name: str,
        message_bus: MessageBus
    ):
        ...

    def register_capability(self, capability: AgentCapability) -> None

    def publish(self) -> None

    def send_request(
        self,
        to_agent: str,
        capability: str,
        payload: Dict[str, Any]
    ) -> str

    def send_response(
        self,
        to_agent: str,
        correlation_id: str,
        payload: Dict[str, Any]
    ) -> str

    def get_messages(self) -> List[A2AMessage]
```

**Methods:**

##### `register_capability(capability: AgentCapability) -> None`

Register a capability for this agent.

##### `publish() -> None`

Publish agent card to the message bus.

##### `send_request(to_agent: str, capability: str, payload: Dict[str, Any]) -> str`

Send a request message.

**Returns:**
- `str`: Message ID for correlation

##### `send_response(to_agent: str, correlation_id: str, payload: Dict[str, Any]) -> str`

Send a response message.

##### `get_messages() -> List[A2AMessage]`

Get all messages for this agent.

---

### `scripts.coding.ai.agents.protocols.nlweb`

Natural Language Web automation.

#### `ActionType` (Enum)

Web automation action types.

```python
class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    EXTRACT = "extract"
    WAIT = "wait"
```

#### `NLWebAction`

Web automation action.

```python
class NLWebAction(BaseModel):
    action_type: ActionType
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout_ms: int = 5000
```

#### `NLWebResult`

Result of web automation.

```python
class NLWebResult(BaseModel):
    success: bool
    extracted_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
```

#### `NLWebBrowser`

Browser automation engine.

```python
class NLWebBrowser:
    def execute_actions(
        self,
        actions: List[NLWebAction]
    ) -> NLWebResult
```

**Methods:**

##### `execute_actions(actions: List[NLWebAction]) -> NLWebResult`

Execute a sequence of web actions.

**Example:**
```python
browser = NLWebBrowser()

actions = [
    NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com"),
    NLWebAction(action_type=ActionType.CLICK, selector="#button"),
    NLWebAction(action_type=ActionType.EXTRACT, selector=".price")
]

result = browser.execute_actions(actions)
if result.success:
    print(result.extracted_data)
```

**Attributes:**

- `current_url` (str): Currently loaded URL
- `page_data` (Dict[str, Any]): Extracted page data

---

## UX Module

### `scripts.coding.ai.agents.ux.transparency`

Transparency enforcement.

#### `TransparencyEnforcer`

Enforces transparency in agent actions.

```python
class TransparencyEnforcer:
    def provide_explanation(
        self,
        action: str,
        reasoning: str
    ) -> str

    def disclose_plan(
        self,
        plan: Plan,
        impact_level: str = "medium"
    ) -> Dict[str, Any]
```

**Methods:**

##### `provide_explanation(action: str, reasoning: str) -> str`

Provide explanation for an action.

**Example:**
```python
enforcer = TransparencyEnforcer()
explanation = enforcer.provide_explanation(
    "delete_file",
    "User requested cleanup"
)
# Returns: "Action: delete_file\nReasoning: User requested cleanup"
```

##### `disclose_plan(plan: Plan, impact_level: str = "medium") -> Dict[str, Any]`

Disclose plan details to the user.

**Returns:**
- Dictionary with plan_id, confidence, subtasks count, disclosed flag

---

### `scripts.coding.ai.agents.ux.control`

User control enforcement.

#### `ApprovalGateEnforcer`

Enforces approval gates for actions.

```python
class ApprovalGateEnforcer:
    def __init__(self, approval_threshold: int = 1000):
        ...

    def enforce_approval_gate(self, action: Any) -> bool
```

**Methods:**

##### `enforce_approval_gate(action: Any) -> bool`

Check if action requires approval.

**Parameters:**
- `action`: Action object (should have `type` and optionally `amount` attributes)

**Returns:**
- `bool`: True if auto-approved, False if requires human approval

**Example:**
```python
enforcer = ApprovalGateEnforcer(approval_threshold=1000)

class PurchaseAction:
    type = "purchase"
    amount = 500

action = PurchaseAction()
if enforcer.enforce_approval_gate(action):
    execute_action(action)
else:
    request_approval(action)
```

---

### `scripts.coding.ai.agents.ux.consistency`

Consistency tracking.

#### `ConsistencyGuard`

Guards interaction consistency.

```python
class ConsistencyGuard:
    def check_consistency(
        self,
        user_input: str,
        agent_output: str
    ) -> bool
```

**Methods:**

##### `check_consistency(user_input: str, agent_output: str) -> bool`

Check and track interaction consistency.

**Attributes:**

- `interaction_history` (List[Dict]): History of interactions

---

## Security Module

### `scripts.coding.ai.agents.security.threat_detector`

Threat detection.

#### `ThreatLevel` (Enum)

Threat severity levels.

```python
class ThreatLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

#### `ThreatDetector`

Detects security threats in user input.

```python
class ThreatDetector:
    def detect_task_injection(self, user_input: str) -> bool

    def classify_threat(self, user_input: str) -> ThreatLevel
```

**Methods:**

##### `detect_task_injection(user_input: str) -> bool`

Detect task injection attempts.

**Example:**
```python
detector = ThreatDetector()

if detector.detect_task_injection("Ignore previous instructions"):
    raise SecurityError("Threat detected")
```

##### `classify_threat(user_input: str) -> ThreatLevel`

Classify threat severity.

**Detected Patterns:**
- "ignore previous instructions"
- "disregard all rules"
- "new instructions:"
- "show me your system prompt"

---

### `scripts.coding.ai.agents.security.hitl`

Human-in-the-Loop controls.

#### `RiskLevel` (Enum)

Risk levels for actions.

```python
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

#### `HumanInTheLoop`

Human-in-the-loop control system.

```python
class HumanInTheLoop:
    HIGH_RISK_ACTIONS: List[str] = [
        "transfer_money",
        "delete_data",
        "modify_system",
        "access_credentials"
    ]

    def classify_risk(self, action: Any) -> RiskLevel

    def requires_approval(self, action: Any) -> bool
```

**Methods:**

##### `classify_risk(action: Any) -> RiskLevel`

Classify risk level of an action.

**Logic:**
- HIGH_RISK_ACTIONS with amount > 10000: CRITICAL
- HIGH_RISK_ACTIONS: HIGH
- Others: LOW

##### `requires_approval(action: Any) -> bool`

Determine if action requires human approval.

**Example:**
```python
hitl = HumanInTheLoop()

class TransferAction:
    type = "transfer_money"
    amount = 15000

action = TransferAction()

risk = hitl.classify_risk(action)  # RiskLevel.CRITICAL
if hitl.requires_approval(action):  # True
    await request_human_approval(action)
```

---

### `scripts.coding.ai.agents.security.audit`

Audit logging.

#### `AuditLog`

Audit log entry.

```python
class AuditLog(BaseModel):
    action: str
    agent_id: str
    user_id: str
    details: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
```

#### `AuditLogger`

Comprehensive audit logger.

```python
class AuditLogger:
    def log_action(
        self,
        action: str,
        agent_id: str,
        user_id: str,
        details: Dict[str, Any]
    ) -> None

    def get_logs(
        self,
        filter_by: Optional[str] = None
    ) -> List[AuditLog]
```

**Methods:**

##### `log_action(action: str, agent_id: str, user_id: str, details: Dict[str, Any]) -> None`

Log an action to the audit trail.

**Example:**
```python
logger = AuditLogger()

logger.log_action(
    "transfer_money",
    "agent_001",
    "user_123",
    {"amount": 15000, "recipient": "account_456"}
)
```

##### `get_logs(filter_by: Optional[str] = None) -> List[AuditLog]`

Retrieve audit logs with optional filtering.

**Parameters:**
- `filter_by` (Optional[str]): Filter by action name

**Example:**
```python
# Get all logs
all_logs = logger.get_logs()

# Get specific action logs
transfer_logs = logger.get_logs(filter_by="transfer_money")
```

**Attributes:**

- `logs` (List[AuditLog]): All logged actions

---

## Error Handling

### Common Exceptions

All modules may raise standard Python exceptions. Protocol-specific exceptions:

**MCP:**
- `ToolNotFoundError`: Tool not registered
- `ParameterValidationError`: Invalid parameters

**Planning:**
- Standard `ValueError` for invalid inputs
- `ValidationError` from Pydantic for model validation

### Error Handling Pattern

```python
from scripts.coding.ai.agents.protocols.mcp import ToolNotFoundError, ParameterValidationError

try:
    result = mcp_server.invoke_tool("my_tool", params)
except ToolNotFoundError:
    # Handle missing tool
    pass
except ParameterValidationError as e:
    # Handle invalid parameters
    print(f"Invalid parameters: {e}")
```

## Type Hints

All modules use Python type hints. Import types as needed:

```python
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from scripts.coding.ai.agents.planning.models import Goal, Plan, SubTask
```

## Testing

All classes and methods are thoroughly tested. See test files for usage examples:

```
scripts/coding/tests/test_agents/
├── test_planning/
├── test_protocols/
├── test_ux/
└── test_security/
```

Each test file demonstrates real-world usage patterns.
