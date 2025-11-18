# AI Agents Framework

Production-ready framework for building trustworthy, transparent AI agents with built-in security, planning, and multi-protocol communication.

[![Tests](https://img.shields.io/badge/tests-140%20passed-brightgreen)](scripts/coding/tests/test_agents/)
[![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)](scripts/coding/tests/test_agents/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

## Overview

This framework implements a complete AI agent system following security-first principles, with comprehensive testing (140 tests, 92% coverage) and production-ready modules for:

- **Planning**: Goal parsing, task decomposition, iterative planning with failure transparency
- **Protocols**: MCP (tool invocation), A2A (agent messaging), NLWeb (browser automation)
- **UX**: Transparency enforcement, approval gates, consistency tracking
- **Security**: Threat detection, human-in-the-loop controls, comprehensive audit logging

## Installation

```bash
# Install dependencies
pip install pydantic

# For development
pip install pytest pytest-cov
```

## Quick Start

### 1. Parse Natural Language Goals

```python
from scripts.coding.ai.agents.planning.parser import GoalParser

parser = GoalParser()
goal = parser.parse("Book a flight to Paris by Friday under $500")

print(f"Goal Type: {goal.goal_type}")
print(f"Constraints: {goal.constraints}")
print(f"Deadline: {goal.deadline}")
```

### 2. Decompose Goals into Plans

```python
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer

decomposer = TaskDecomposer()
plan = decomposer.decompose(goal)

print(f"Plan ID: {plan.plan_id}")
print(f"Subtasks: {len(plan.subtasks)}")
print(f"Confidence: {plan.confidence_score}")
```

### 3. Use MCP for Tool Invocation

```python
from scripts.coding.ai.agents.protocols.mcp import (
    MCPServer, ToolDefinition, ToolParameter
)

server = MCPServer()

# Register a tool
tool_def = ToolDefinition(
    name="book_flight",
    description="Book a flight from origin to destination",
    parameters=[
        ToolParameter(name="origin", type="string", description="Origin airport"),
        ToolParameter(name="destination", type="string", description="Destination"),
        ToolParameter(name="date", type="string", description="Departure date")
    ],
    returns="Booking confirmation"
)

def book_flight_impl(origin: str, destination: str, date: str):
    return {"booking_id": "FL12345", "origin": origin, "destination": destination}

server.register_tool(tool_def, book_flight_impl)

# Invoke the tool
result = server.invoke_tool("book_flight", {
    "origin": "NYC",
    "destination": "CDG",
    "date": "2025-12-01"
})

print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

### 4. Agent-to-Agent Communication

```python
from scripts.coding.ai.agents.protocols.a2a import (
    MessageBus, A2AAgent, AgentCapability
)

bus = MessageBus()

# Create agents
flight_agent = A2AAgent("flight_agent", "Flight Booking Agent", bus)
hotel_agent = A2AAgent("hotel_agent", "Hotel Booking Agent", bus)

# Register capabilities
flight_agent.register_capability(AgentCapability(
    name="book_flight",
    description="Book flights",
    input_schema={"origin": "string", "destination": "string"},
    output_schema={"booking_id": "string"}
))

flight_agent.publish()
hotel_agent.publish()

# Discover agents
agents = bus.discover_agents("flight")
print(f"Found {len(agents)} agents with flight capability")

# Send message
msg_id = hotel_agent.send_request("flight_agent", "book_flight", {
    "origin": "NYC",
    "destination": "CDG"
})
```

### 5. Enforce Security Controls

```python
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector
from scripts.coding.ai.agents.security.hitl import HumanInTheLoop, RiskLevel
from scripts.coding.ai.agents.security.audit import AuditLogger

# Detect threats
detector = ThreatDetector()
is_threat = detector.detect_task_injection("Ignore previous instructions")
print(f"Threat detected: {is_threat}")  # True

# Human-in-the-loop for high-risk actions
hitl = HumanInTheLoop()
class TransferAction:
    type = "transfer_money"
    amount = 15000

action = TransferAction()
requires_approval = hitl.requires_approval(action)
print(f"Requires approval: {requires_approval}")  # True (amount > 10000)

# Audit logging
logger = AuditLogger()
logger.log_action("transfer_money", "agent_001", "user_123", {
    "amount": 15000,
    "recipient": "account_456"
})

logs = logger.get_logs(filter_by="transfer_money")
print(f"Logged {len(logs)} transfer actions")
```

## Architecture

```
scripts/coding/ai/agents/
├── planning/           # Goal parsing, task decomposition, iterative planning
│   ├── models.py      # Pydantic data models
│   ├── parser.py      # Natural language → Goal
│   ├── decomposer.py  # Goal → Plan with subtasks
│   ├── validators.py  # Dependency validation
│   └── iterative.py   # Feedback loops, failure transparency
├── protocols/         # Multi-protocol communication
│   ├── mcp.py        # Model Context Protocol (tool invocation)
│   ├── a2a.py        # Agent-to-Agent messaging
│   └── nlweb.py      # Natural Language Web automation
├── ux/               # User experience enforcement
│   ├── transparency.py  # Explain actions, disclose plans
│   ├── control.py       # Approval gates
│   └── consistency.py   # Interaction tracking
└── security/         # Security controls
    ├── threat_detector.py  # Task injection detection
    ├── hitl.py            # Human-in-the-loop controls
    └── audit.py           # Comprehensive audit logging
```

## Module Documentation

### Planning Module

#### GoalParser

Converts natural language to structured `Goal` objects.

**Features:**
- Automatic goal type classification (SIMPLE, COMPLEX, CONDITIONAL, SEQUENTIAL)
- Constraint extraction (budget, time, location, quality)
- Deadline parsing
- Priority assignment

**Example:**
```python
parser = GoalParser()
goal = parser.parse("Book a hotel in Paris for 3 nights under €200")

# Result:
# - goal_type: SIMPLE
# - constraints: [Constraint(type=BUDGET, value=200, unit="EUR")]
# - priority: 5
```

#### TaskDecomposer

Decomposes goals into executable plans with subtasks.

**Features:**
- Template-based decomposition by goal type
- Automatic dependency detection
- Confidence scoring
- Execution strategy selection (sequential, parallel, conditional)

**Example:**
```python
decomposer = TaskDecomposer()
plan = decomposer.decompose(goal)

# Result:
# - subtasks: [search_hotels, compare_prices, book_hotel]
# - dependencies: [book_hotel depends on compare_prices]
# - confidence_score: 0.85
```

#### IterativePlanner

Handles execution feedback and plan revisions.

**Features:**
- 5 revision strategies (add steps, reorder, adjust constraints, replace, simplify)
- Failure transparency (<500ms response)
- Confidence adjustment
- Max revision limits

**Example:**
```python
planner = IterativePlanner()
feedback = ExecutionFeedback(
    subtask_id="book_hotel",
    status=ExecutionStatus.FAILED,
    error_message="Hotel fully booked"
)

revision = planner.handle_feedback(plan, feedback)
# Returns PlanRevision with adjusted confidence and alternative approach
```

### Protocols Module

#### MCP (Model Context Protocol)

Tool discovery and invocation with parameter validation.

**Features:**
- Tool registration with schema definitions
- Parameter type validation (string, number, boolean)
- Required parameter enforcement
- Unknown parameter rejection
- Cost tracking
- Duration measurement

**Example:**
```python
server = MCPServer()

# Register tool
tool_def = ToolDefinition(
    name="search",
    description="Search for information",
    parameters=[
        ToolParameter(name="query", type="string", required=True),
        ToolParameter(name="limit", type="number", required=False, default=10)
    ],
    returns="Search results",
    cost_estimate=0.01
)

server.register_tool(tool_def, lambda query, limit=10: [f"result_{i}" for i in range(limit)])

# Invoke
result = server.invoke_tool("search", {"query": "AI agents"})
print(result.cost)  # 0.01
print(result.duration_ms)  # Measured execution time
```

#### A2A (Agent-to-Agent Protocol)

Decentralized agent communication via message bus.

**Features:**
- Agent capability registration
- Agent discovery by capability
- Message correlation (request-response)
- Message ordering preservation
- Multiple message types (REQUEST, RESPONSE, NOTIFICATION, ERROR)
- Isolated message buses

**Example:**
```python
bus = MessageBus()

# Create and register agent
agent = A2AAgent("data_agent", "Data Analysis Agent", bus)
agent.register_capability(AgentCapability(
    name="analyze_data",
    description="Perform data analysis",
    input_schema={"data": "array"},
    output_schema={"insights": "object"}
))
agent.publish()

# Discover agents
agents = bus.discover_agents("data")
# Returns: [AgentCard for data_agent]

# Send request
msg_id = agent.send_request("other_agent", "process_data", {"data": [1, 2, 3]})

# Send response
agent.send_response("other_agent", msg_id, {"result": "processed"})
```

#### NLWeb (Natural Language Web)

Browser automation with natural language actions.

**Features:**
- 5 action types: NAVIGATE, CLICK, TYPE, EXTRACT, WAIT
- Configurable timeouts
- Data extraction
- Action sequencing
- Page state persistence

**Example:**
```python
browser = NLWebBrowser()

actions = [
    NLWebAction(action_type=ActionType.NAVIGATE, value="https://example.com"),
    NLWebAction(action_type=ActionType.CLICK, selector="#search-button"),
    NLWebAction(action_type=ActionType.TYPE, selector="#query", value="AI agents"),
    NLWebAction(action_type=ActionType.EXTRACT, selector=".results")
]

result = browser.execute_actions(actions)
print(result.extracted_data)  # {".results": [...]}
```

### UX Module

#### TransparencyEnforcer

Provides explanations and plan disclosures.

**Features:**
- Action explanations with reasoning
- Plan disclosure with confidence scores
- Impact level tracking

**Example:**
```python
enforcer = TransparencyEnforcer()

# Explain action
explanation = enforcer.provide_explanation(
    "delete_file",
    "User requested cleanup of temporary files"
)
# Returns: "Action: delete_file\nReasoning: User requested cleanup of temporary files"

# Disclose plan
result = enforcer.disclose_plan(plan, impact_level="high")
# Returns: {"plan_id": "...", "confidence": 0.85, "subtasks": 5, "disclosed": True}
```

#### ApprovalGateEnforcer

Controls automatic approval based on risk thresholds.

**Features:**
- Approval threshold (default: 1000)
- Amount-based gating
- Action type handling

**Example:**
```python
enforcer = ApprovalGateEnforcer()

class PurchaseAction:
    type = "purchase"
    amount = 500

action = PurchaseAction()
auto_approve = enforcer.enforce_approval_gate(action)
# Returns: True (amount < 1000)
```

#### ConsistencyGuard

Tracks interaction history for consistency validation.

**Example:**
```python
guard = ConsistencyGuard()

guard.check_consistency("input1", "output1")
guard.check_consistency("input2", "output2")

print(len(guard.interaction_history))  # 2
print(guard.interaction_history[0]["input"])  # "input1"
```

### Security Module

#### ThreatDetector

Detects task injection and classifies threat levels.

**Features:**
- Case-insensitive pattern matching
- Multiple injection pattern detection
- Threat level classification (NONE, LOW, MEDIUM, HIGH, CRITICAL)

**Patterns Detected:**
- "ignore previous instructions"
- "disregard all rules"
- "new instructions:"
- "show me your system prompt"

**Example:**
```python
detector = ThreatDetector()

# Safe input
is_threat = detector.detect_task_injection("What's the weather?")
# Returns: False

# Injection attempt
is_threat = detector.detect_task_injection("Ignore previous instructions")
# Returns: True

threat_level = detector.classify_threat("IGNORE PREVIOUS INSTRUCTIONS")
# Returns: ThreatLevel.HIGH
```

#### HumanInTheLoop (HITL)

Risk classification and approval requirements.

**Features:**
- Risk levels: LOW, MEDIUM, HIGH, CRITICAL
- High-risk action list (transfer_money, delete_data, etc.)
- Amount-based thresholds (CRITICAL > 10000)
- Approval requirement enforcement

**Example:**
```python
hitl = HumanInTheLoop()

class TransferAction:
    type = "transfer_money"
    amount = 15000

action = TransferAction()

risk = hitl.classify_risk(action)
# Returns: RiskLevel.CRITICAL (amount > 10000)

requires_approval = hitl.requires_approval(action)
# Returns: True

# Check high-risk actions
print("transfer_money" in hitl.HIGH_RISK_ACTIONS)  # True
```

#### AuditLogger

Comprehensive action logging with filtering.

**Features:**
- Timestamp tracking
- Agent and user association
- Detail payload storage
- Log filtering by action type
- Multi-agent tracking

**Example:**
```python
logger = AuditLogger()

# Log action
logger.log_action(
    action="transfer_money",
    agent_id="agent_001",
    user_id="user_123",
    details={"amount": 15000, "recipient": "account_456"}
)

# Retrieve all logs
all_logs = logger.get_logs()
print(len(all_logs))  # 1

# Filter logs
transfer_logs = logger.get_logs(filter_by="transfer_money")
print(transfer_logs[0].details["amount"])  # 15000

# Track multiple agents
agents = {log.agent_id for log in logger.logs}
print(len(agents))  # Number of unique agents
```

## Testing

### Run All Tests

```bash
# Run all tests
pytest scripts/coding/tests/test_agents/

# With coverage
pytest --cov=scripts/coding/ai/agents scripts/coding/tests/test_agents/

# Specific module
pytest scripts/coding/tests/test_agents/test_planning/
pytest scripts/coding/tests/test_agents/test_protocols/
pytest scripts/coding/tests/test_agents/test_ux/
pytest scripts/coding/tests/test_agents/test_security/
```

### Test Coverage

Current coverage: **92%** (8467 statements, 7802 executed)

```
Module                          Coverage
─────────────────────────────────────────
planning/models.py              100%
planning/parser.py              95%
planning/decomposer.py          94%
planning/validators.py          93%
planning/iterative.py           91%
protocols/mcp.py                96%
protocols/a2a.py                94%
protocols/nlweb.py              93%
ux/transparency.py              89%
ux/control.py                   90%
ux/consistency.py               92%
security/threat_detector.py     95%
security/hitl.py                93%
security/audit.py               94%
```

### Test Structure

```
scripts/coding/tests/test_agents/
├── test_planning/
│   ├── test_task_decomposition.py  # 20 tests (RF-011)
│   └── test_iterative_planning.py  # 20 tests (RF-012)
├── test_protocols/
│   ├── test_mcp.py                 # 20 tests (MCP)
│   ├── test_a2a.py                 # 2 tests (A2A core)
│   ├── test_a2a_complete.py        # 18 tests (A2A complete)
│   └── test_nlweb_complete.py      # 20 tests (NLWeb)
├── test_ux/
│   ├── test_transparency.py        # 1 test (core)
│   └── test_ux_complete.py         # 19 tests (complete)
└── test_security/
    ├── test_threat_detector.py     # 2 tests (core)
    └── test_security_complete.py   # 18 tests (complete)

Total: 140 tests, 100% passing
```

## Integration Examples

### Example 1: Complete Trip Planning Workflow

```python
from scripts.coding.ai.agents.planning.parser import GoalParser
from scripts.coding.ai.agents.planning.decomposer import TaskDecomposer
from scripts.coding.ai.agents.planning.iterative import IterativePlanner, ExecutionFeedback, ExecutionStatus
from scripts.coding.ai.agents.protocols.mcp import MCPServer, ToolDefinition, ToolParameter
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector
from scripts.coding.ai.agents.security.hitl import HumanInTheLoop
from scripts.coding.ai.agents.security.audit import AuditLogger

# Initialize components
parser = GoalParser()
decomposer = TaskDecomposer()
planner = IterativePlanner()
mcp_server = MCPServer()
detector = ThreatDetector()
hitl = HumanInTheLoop()
logger = AuditLogger()

# Step 1: Parse user input
user_request = "Plan a trip to Paris for 3 days under $2000"

# Security check
if detector.detect_task_injection(user_request):
    print("Security threat detected!")
    exit()

# Step 2: Parse goal
goal = parser.parse(user_request)
logger.log_action("parse_goal", "planning_agent", "user_001", {"goal_id": goal.goal_id})

# Step 3: Decompose into plan
plan = decomposer.decompose(goal)
print(f"Generated plan with {len(plan.subtasks)} subtasks")
print(f"Confidence: {plan.confidence_score}")

# Step 4: Register tools in MCP
mcp_server.register_tool(
    ToolDefinition(
        name="book_flight",
        description="Book flight",
        parameters=[
            ToolParameter(name="origin", type="string"),
            ToolParameter(name="destination", type="string"),
            ToolParameter(name="date", type="string")
        ],
        returns="Booking confirmation"
    ),
    lambda origin, destination, date: {"booking_id": "FL123", "cost": 800}
)

mcp_server.register_tool(
    ToolDefinition(
        name="book_hotel",
        description="Book hotel",
        parameters=[
            ToolParameter(name="city", type="string"),
            ToolParameter(name="nights", type="number")
        ],
        returns="Hotel reservation"
    ),
    lambda city, nights: {"reservation_id": "HT456", "cost": 600}
)

# Step 5: Execute plan with HITL control
for subtask in plan.subtasks:
    # Check if approval needed
    class BookingAction:
        type = subtask.agent_type
        amount = 1000  # Example amount

    action = BookingAction()
    if hitl.requires_approval(action):
        print(f"Action {subtask.task_id} requires approval")
        # In real system, wait for user approval
        continue

    # Execute via MCP
    if subtask.agent_type == "flight_booking":
        result = mcp_server.invoke_tool("book_flight", {
            "origin": "NYC",
            "destination": "CDG",
            "date": "2025-12-01"
        })

        if result.status == "success":
            logger.log_action("book_flight", "flight_agent", "user_001", result.result)
        else:
            # Handle failure
            feedback = ExecutionFeedback(
                subtask_id=subtask.task_id,
                status=ExecutionStatus.FAILED,
                error_message=result.error
            )
            revision = planner.handle_feedback(plan, feedback)
            if revision:
                print(f"Plan revised: {revision.revision_strategy}")

print("Trip planning completed!")
print(f"Total actions logged: {len(logger.get_logs())}")
```

### Example 2: Multi-Agent Collaboration

```python
from scripts.coding.ai.agents.protocols.a2a import MessageBus, A2AAgent, AgentCapability
from scripts.coding.ai.agents.protocols.mcp import MCPServer, ToolDefinition, ToolParameter

# Create message bus
bus = MessageBus()

# Create specialized agents
flight_agent = A2AAgent("flight_agent", "Flight Booking Specialist", bus)
hotel_agent = A2AAgent("hotel_agent", "Hotel Booking Specialist", bus)
coordinator_agent = A2AAgent("coordinator", "Trip Coordinator", bus)

# Register capabilities
flight_agent.register_capability(AgentCapability(
    name="search_flights",
    description="Search for available flights",
    input_schema={"origin": "string", "destination": "string", "date": "string"},
    output_schema={"flights": "array"}
))

hotel_agent.register_capability(AgentCapability(
    name="search_hotels",
    description="Search for available hotels",
    input_schema={"city": "string", "checkin": "string", "nights": "number"},
    output_schema={"hotels": "array"}
))

# Publish agents
flight_agent.publish()
hotel_agent.publish()
coordinator_agent.publish()

# Coordinator discovers available agents
available_agents = bus.discover_agents()
print(f"Discovered {len(available_agents)} agents")

# Find specific capability
flight_agents = bus.discover_agents("flight")
print(f"Flight agents: {[a.name for a in flight_agents]}")

# Coordinator requests flight search
msg_id = coordinator_agent.send_request("flight_agent", "search_flights", {
    "origin": "NYC",
    "destination": "CDG",
    "date": "2025-12-01"
})

# Flight agent processes and responds
messages = flight_agent.get_messages()
for msg in messages:
    if msg.capability == "search_flights":
        # Simulate flight search
        flights = [
            {"flight_id": "AF001", "price": 800},
            {"flight_id": "DL002", "price": 850}
        ]
        flight_agent.send_response(msg.from_agent, msg.message_id, {"flights": flights})

# Coordinator receives response
responses = coordinator_agent.get_messages()
for resp in responses:
    if resp.correlation_id == msg_id:
        print(f"Received flights: {resp.payload}")

# Parallel requests
hotel_msg_id = coordinator_agent.send_request("hotel_agent", "search_hotels", {
    "city": "Paris",
    "checkin": "2025-12-01",
    "nights": 3
})

print("Multi-agent collaboration completed!")
```

### Example 3: Web Automation with Security

```python
from scripts.coding.ai.agents.protocols.nlweb import NLWebBrowser, NLWebAction, ActionType
from scripts.coding.ai.agents.security.audit import AuditLogger

browser = NLWebBrowser()
logger = AuditLogger()

# Define automation workflow
actions = [
    NLWebAction(action_type=ActionType.NAVIGATE, value="https://example-booking.com"),
    NLWebAction(action_type=ActionType.TYPE, selector="#origin", value="NYC"),
    NLWebAction(action_type=ActionType.TYPE, selector="#destination", value="Paris"),
    NLWebAction(action_type=ActionType.CLICK, selector="#search-button"),
    NLWebAction(action_type=ActionType.WAIT, selector=".results", timeout_ms=5000),
    NLWebAction(action_type=ActionType.EXTRACT, selector=".flight-price")
]

# Execute with audit logging
logger.log_action("start_web_automation", "browser_agent", "user_001", {
    "url": "https://example-booking.com",
    "action_count": len(actions)
})

result = browser.execute_actions(actions)

if result.success:
    print(f"Extracted data: {result.extracted_data}")
    logger.log_action("web_automation_success", "browser_agent", "user_001", {
        "extracted_count": len(result.extracted_data)
    })
else:
    print(f"Error: {result.error}")
    logger.log_action("web_automation_failed", "browser_agent", "user_001", {
        "error": result.error
    })

# Review audit trail
audit_logs = logger.get_logs(filter_by="web_automation")
print(f"Audit trail: {len(audit_logs)} entries")
```

## Configuration

### Environment Variables

```bash
# Optional configuration
export IACT_AGENTS_LOG_LEVEL=INFO
export IACT_AGENTS_MAX_REVISIONS=5
export IACT_AGENTS_APPROVAL_THRESHOLD=1000
```

### Programmatic Configuration

```python
from scripts.coding.ai.agents.planning.iterative import IterativePlanner
from scripts.coding.ai.agents.ux.control import ApprovalGateEnforcer

# Configure iterative planner
planner = IterativePlanner(max_revisions=10)

# Configure approval threshold
enforcer = ApprovalGateEnforcer(approval_threshold=5000)
```

## Performance

### Benchmarks

- Goal parsing: ~10ms average
- Plan decomposition: ~50ms average
- Tool discovery: <100ms (verified in tests)
- Tool invocation: <10ms (excluding actual execution)
- Failure transparency: <500ms (requirement met)

### Optimization Tips

1. **Reuse parsers and decomposers** - They maintain internal caches
2. **Batch tool registrations** - Register all tools at startup
3. **Use message bus efficiently** - Filter agent discovery by capability
4. **Enable audit log filtering** - Use `filter_by` parameter to reduce log scanning

## Contributing

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd IACT---project

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest scripts/coding/tests/test_agents/ -v

# Check coverage
pytest --cov=scripts/coding/ai/agents --cov-report=html scripts/coding/tests/test_agents/
```

### Code Standards

- Python 3.11+ type hints
- Pydantic models for data validation
- 100% test coverage for new features
- Docstrings for all public methods
- Follow existing naming conventions

### Running Tests

```bash
# All tests
pytest scripts/coding/tests/test_agents/

# Specific module
pytest scripts/coding/tests/test_agents/test_planning/test_task_decomposition.py -v

# Single test
pytest scripts/coding/tests/test_agents/test_protocols/test_mcp.py::test_register_and_discover_tools -v

# With coverage
pytest --cov=scripts/coding/ai/agents --cov-report=term-missing scripts/coding/tests/test_agents/
```

## Troubleshooting

### Common Issues

**Issue: Import errors**
```python
# Wrong
from agents.planning import GoalParser

# Correct
from scripts.coding.ai.agents.planning.parser import GoalParser
```

**Issue: Pydantic validation errors**
```python
# Ensure all required fields are provided
goal = Goal(
    goal_id="g1",
    goal_type=GoalType.SIMPLE,
    description="Test",
    constraints=[],
    success_criteria=[]
)
```

**Issue: Tool invocation failures**
```python
# Check parameter validation
result = server.invoke_tool("tool_name", {"param": "value"})
if result.status == "error":
    print(f"Error: {result.error}")
```

## License

See project LICENSE file.

## Support

For issues and questions:
- Open an issue in the project repository
- Check existing tests for usage examples
- Review module documentation above

## Roadmap

- [ ] LLM integration (OpenAI, Anthropic)
- [ ] Django integration for web interface
- [ ] Real browser automation (Playwright/Selenium)
- [ ] Distributed agent coordination
- [ ] Advanced threat detection (ML-based)
- [ ] Multi-language support
