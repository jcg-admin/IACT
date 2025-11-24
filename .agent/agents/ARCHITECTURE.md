# Architecture Overview

Comprehensive architecture documentation for the AI Agents Framework.

## Table of Contents

- [System Overview](#system-overview)
- [Module Architecture](#module-architecture)
- [Data Flow](#data-flow)
- [Component Diagrams](#component-diagrams)
- [Sequence Diagrams](#sequence-diagrams)
- [Design Patterns](#design-patterns)
- [Security Architecture](#security-architecture)

## System Overview

The AI Agents Framework is a modular, security-first system for building trustworthy AI agents with comprehensive planning, multi-protocol communication, and built-in security controls.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agents Framework                       │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌─────────┐  ┌──────────┐ │
│  │  Planning  │  │ Protocols  │  │   UX    │  │ Security │ │
│  │  Module    │  │  Module    │  │ Module  │  │  Module  │ │
│  └────────────┘  └────────────┘  └─────────┘  └──────────┘ │
│       │               │                │             │       │
│       └───────────────┴────────────────┴─────────────┘       │
│                         │                                     │
│                   Core Framework                              │
└─────────────────────────────────────────────────────────────┘
```

### Module Breakdown

```
scripts/coding/ai/agents/
├── planning/           # Goal parsing, task decomposition, iterative planning
│   ├── models.py       # Pydantic data models
│   ├── parser.py       # Natural language → Goal
│   ├── decomposer.py   # Goal → Plan with subtasks
│   ├── validators.py   # Dependency and completeness validation
│   └── iterative.py    # Feedback loops, plan revisions
│
├── protocols/          # Multi-protocol communication
│   ├── mcp.py          # Model Context Protocol (tool invocation)
│   ├── a2a.py          # Agent-to-Agent messaging
│   └── nlweb.py        # Natural Language Web automation
│
├── ux/                 # User experience enforcement
│   ├── transparency.py # Action explanations, plan disclosure
│   ├── control.py      # Approval gates
│   └── consistency.py  # Interaction tracking
│
└── security/           # Security controls
    ├── threat_detector.py  # Task injection detection
    ├── hitl.py             # Human-in-the-loop controls
    └── audit.py            # Comprehensive audit logging
```

## Module Architecture

### Planning Module Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Planning Module                          │
│                                                                │
│  User Request                                                  │
│       │                                                        │
│       ▼                                                        │
│  ┌──────────┐    ┌──────────────┐                            │
│  │  Parser  │───▶│ GoalParser   │                            │
│  └──────────┘    └──────────────┘                            │
│                         │                                      │
│                         ▼                                      │
│                   ┌──────────┐                                │
│                   │   Goal   │  (Pydantic Model)              │
│                   └──────────┘                                │
│                         │                                      │
│                         ▼                                      │
│  ┌──────────────┐  ┌─────────────┐                           │
│  │ Decomposer   │─▶│TaskDecomposer                           │
│  └──────────────┘  └─────────────┘                           │
│                         │                                      │
│                         ▼                                      │
│                   ┌──────────┐                                │
│                   │   Plan   │  (with SubTasks)               │
│                   └──────────┘                                │
│                         │                                      │
│                    ┌────┴─────┐                               │
│                    ▼          ▼                                │
│            ┌──────────────┐  ┌──────────────────┐            │
│            │ Validators   │  │ IterativePlanner  │            │
│            └──────────────┘  └──────────────────┘            │
│                    │                  │                        │
│                    ▼                  ▼                        │
│            ValidationResult    PlanRevision (if needed)       │
└──────────────────────────────────────────────────────────────┘
```

**Flow:**
1. User request → GoalParser → structured Goal
2. Goal → TaskDecomposer → Plan with SubTasks
3. Plan → Validators → ValidationResult
4. Execution feedback → IterativePlanner → Optional PlanRevision

### Protocols Module Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Protocols Module                            │
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │      MCP        │  │       A2A        │  │     NLWeb      │ │
│  │ (Tool Protocol) │  │ (Agent Protocol) │  │(Web Protocol)  │ │
│  └─────────────────┘  └──────────────────┘  └────────────────┘ │
│          │                     │                      │          │
│          ▼                     ▼                      ▼          │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ MCPServer   │      │ MessageBus   │      │ NLWebBrowser │  │
│  │ MCPClient   │      │ A2AAgent     │      │              │  │
│  └─────────────┘      └──────────────┘      └──────────────┘  │
│          │                     │                      │          │
│          ▼                     ▼                      ▼          │
│  Tool Invocation      Agent Messages        Web Actions         │
└─────────────────────────────────────────────────────────────────┘
```

#### MCP (Model Context Protocol)

```
┌─────────────────────────────────────────────────┐
│                  MCP Server                      │
│                                                   │
│  ┌──────────────────────────────────────────┐  │
│  │       Tool Registry                       │  │
│  │  ┌────────────┐  ┌────────────┐         │  │
│  │  │  Tool 1    │  │  Tool 2    │  ...    │  │
│  │  │  - name    │  │  - name    │         │  │
│  │  │  - params  │  │  - params  │         │  │
│  │  │  - impl    │  │  - impl    │         │  │
│  │  └────────────┘  └────────────┘         │  │
│  └──────────────────────────────────────────┘  │
│                                                   │
│  invoke_tool(name, params)                       │
│       │                                           │
│       ├─▶ Validate parameters                    │
│       ├─▶ Execute implementation                 │
│       ├─▶ Measure duration & cost                │
│       └─▶ Return ToolInvocationResult            │
└─────────────────────────────────────────────────┘
```

#### A2A (Agent-to-Agent Protocol)

```
┌───────────────────────────────────────────────────────────┐
│                      Message Bus                           │
│                                                             │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐        │
│  │ Agent A  │      │ Agent B  │      │ Agent C  │        │
│  │          │      │          │      │          │        │
│  │ [Cap1]   │      │ [Cap2]   │      │ [Cap3]   │        │
│  │ [Cap2]   │      │ [Cap3]   │      │ [Cap1]   │        │
│  └─────┬────┘      └────┬─────┘      └────┬─────┘        │
│        │                │                 │                │
│        └────────┬───────┴─────────────────┘                │
│                 │                                           │
│         ┌───────▼──────────┐                               │
│         │  Message Queue   │                               │
│         │  - Requests      │                               │
│         │  - Responses     │                               │
│         │  - Notifications │                               │
│         └──────────────────┘                               │
│                                                             │
│  Agent Discovery: discover_agents(capability)               │
│  Message Routing: send_message(to_agent, msg)              │
│  Correlation: match requests with responses                 │
└───────────────────────────────────────────────────────────┘
```

#### NLWeb (Natural Language Web)

```
┌────────────────────────────────────────────────┐
│              NLWeb Browser                      │
│                                                  │
│  Action Sequence:                                │
│    ┌────────┐  ┌────────┐  ┌────────┐          │
│    │Navigate│─▶│ Type   │─▶│ Click  │─▶ ...    │
│    └────────┘  └────────┘  └────────┘          │
│                                                  │
│  Page State:                                     │
│    ┌──────────────┐                             │
│    │ current_url  │                             │
│    │ page_data    │                             │
│    │ extracted    │                             │
│    └──────────────┘                             │
│                                                  │
│  Results:                                        │
│    ┌──────────────┐                             │
│    │ success      │                             │
│    │ extracted    │                             │
│    │ error        │                             │
│    └──────────────┘                             │
└────────────────────────────────────────────────┘
```

### UX Module Architecture

```
┌──────────────────────────────────────────────────────┐
│                    UX Module                          │
│                                                        │
│  ┌──────────────────┐  ┌──────────────────┐         │
│  │  Transparency    │  │     Control      │         │
│  │  Enforcer        │  │  (Approval Gates)│         │
│  └──────────────────┘  └──────────────────┘         │
│          │                      │                     │
│          ▼                      ▼                     │
│  Explain Actions         Check Amount                │
│  Disclose Plans         Enforce Gates                │
│                                                        │
│  ┌──────────────────┐                                │
│  │   Consistency    │                                │
│  │     Guard        │                                │
│  └──────────────────┘                                │
│          │                                             │
│          ▼                                             │
│  Track Interactions                                   │
│  Validate Consistency                                 │
└──────────────────────────────────────────────────────┘
```

### Security Module Architecture

```
┌───────────────────────────────────────────────────────┐
│                  Security Module                       │
│                                                         │
│  User Input                                             │
│       │                                                 │
│       ▼                                                 │
│  ┌──────────────┐                                      │
│  │   Threat     │  Check for:                          │
│  │  Detector    │  - Task injection                    │
│  └──────────────┘  - Pattern matching                  │
│       │             - Threat classification             │
│       │                                                 │
│       ├─ Safe ────────────────────────────┐            │
│       │                                    │            │
│       └─ Threat → Block & Log             │            │
│                                            │            │
│  ┌──────────────┐                         │            │
│  │    HITL      │  Action                 │            │
│  │ (Human-in-   │  Validation             │            │
│  │  the-Loop)   │                         │            │
│  └──────────────┘                         │            │
│       │                                    │            │
│       ├─ Low Risk → Execute               │            │
│       └─ High Risk → Request Approval     │            │
│                                            │            │
│  ┌──────────────┐                         │            │
│  │    Audit     │◀────────────────────────┘            │
│  │   Logger     │  Log all actions                     │
│  └──────────────┘  with details                        │
└───────────────────────────────────────────────────────┘
```

## Data Flow

### Complete Request Flow

```
┌────────────────────────────────────────────────────────────────┐
│                      Complete Request Flow                      │
│                                                                  │
│  1. User Request                                                │
│     "Book a flight to Paris under $500"                         │
│                                                                  │
│  2. Security Check                                              │
│     ┌──────────────┐                                           │
│     │  Threat      │  ✓ No injection detected                  │
│     │  Detector    │                                            │
│     └──────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│  3. Goal Parsing                                                │
│     ┌──────────────┐                                           │
│     │ GoalParser   │  → Goal(                                  │
│     └──────────────┘      type=SIMPLE,                         │
│                           constraints=[BUDGET(500, USD)]        │
│                         )                                       │
│            │                                                     │
│            ▼                                                     │
│  4. Plan Creation                                               │
│     ┌──────────────┐                                           │
│     │TaskDecomposer│  → Plan(                                  │
│     └──────────────┘      subtasks=[                           │
│                             search_flights,                     │
│                             compare_prices,                     │
│                             book_flight                         │
│                           ]                                     │
│                         )                                       │
│            │                                                     │
│            ▼                                                     │
│  5. Transparency                                                │
│     ┌──────────────┐                                           │
│     │Transparency  │  Disclose plan to user                    │
│     │  Enforcer    │  Confidence: 85%                          │
│     └──────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│  6. Approval Check                                              │
│     ┌──────────────┐                                           │
│     │    HITL      │  Amount < 1000 → Auto-approve             │
│     └──────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│  7. Execution (via MCP)                                         │
│     ┌──────────────┐                                           │
│     │  MCP Server  │  invoke_tool("search_flights", ...)       │
│     └──────────────┘  invoke_tool("book_flight", ...)          │
│            │                                                     │
│            ▼                                                     │
│  8. Audit Logging                                               │
│     ┌──────────────┐                                           │
│     │    Audit     │  Log: goal_parsed, plan_created,          │
│     │   Logger     │       flight_booked                        │
│     └──────────────┘                                           │
│            │                                                     │
│            ▼                                                     │
│  9. Result                                                      │
│     {booking_id: "FL123", price: 450, confirmed: true}         │
└────────────────────────────────────────────────────────────────┘
```

### Iterative Planning Flow

```
┌──────────────────────────────────────────────────────┐
│            Iterative Planning with Feedback           │
│                                                        │
│  Initial Plan                                          │
│       │                                                │
│       ▼                                                │
│  Execute Subtask 1  ──────┐                          │
│       │                    │                           │
│       ├─ Success ─────────┤                           │
│       │                    │                           │
│       └─ Failure           │                           │
│           │                │                           │
│           ▼                │                           │
│     ┌──────────────────┐  │                          │
│     │ExecutionFeedback │  │                          │
│     │  - status: FAILED│  │                          │
│     │  - error_message │  │                          │
│     └──────────────────┘  │                          │
│           │                │                           │
│           ▼                │                           │
│     ┌──────────────────┐  │                          │
│     │IterativePlanner  │  │                          │
│     │  handle_feedback │  │                          │
│     └──────────────────┘  │                          │
│           │                │                           │
│           ▼                │                           │
│     Select Strategy:       │                           │
│      - ADD_STEPS          │                           │
│      - REORDER            │                           │
│      - ADJUST_CONSTRAINTS │                           │
│      - REPLACE_SUBTASK    │                           │
│      - SIMPLIFY           │                           │
│           │                │                           │
│           ▼                │                           │
│     Revised Plan           │                           │
│       │                    │                           │
│       └────────────────────┘                          │
│       │                                                │
│       ▼                                                │
│  Continue Execution                                    │
└──────────────────────────────────────────────────────┘
```

### Multi-Agent Collaboration Flow

```
┌───────────────────────────────────────────────────────────┐
│              Multi-Agent Collaboration                     │
│                                                             │
│  ┌────────────┐        ┌──────────────┐                   │
│  │Coordinator │        │ Message Bus  │                   │
│  │   Agent    │        └──────────────┘                   │
│  └────────────┘              │                             │
│        │                     │                             │
│        │ 1. discover_agents() │                           │
│        ├────────────────────▶│                             │
│        │                     │                             │
│        │ 2. [Agent List]     │                             │
│        │◀────────────────────┤                             │
│        │                     │                             │
│        │ 3. send_request()   │                             │
│        │    to: flight_agent │                             │
│        ├────────────────────▶│                             │
│        │                     │                             │
│        │                     │  4. Route message           │
│        │                     ├──────────────┐              │
│        │                     │              │              │
│        │                     │        ┌─────▼──────┐       │
│        │                     │        │   Flight   │       │
│        │                     │        │   Agent    │       │
│        │                     │        └─────┬──────┘       │
│        │                     │              │              │
│        │                     │ 5. Process   │              │
│        │                     │    request   │              │
│        │                     │◀─────────────┘              │
│        │                     │                             │
│        │                     │ 6. send_response()          │
│        │ 7. Deliver response │                             │
│        │◀────────────────────┤                             │
│        │                     │                             │
│        ▼                     ▼                             │
│  Process result         Log interaction                    │
└───────────────────────────────────────────────────────────┘
```

## Component Diagrams

### Planning Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                   Planning Components                    │
│                                                           │
│  ┌──────────┐                                            │
│  │  models  │◀───────────────────┐                       │
│  │          │                    │                       │
│  │ - Goal   │                    │                       │
│  │ - Plan   │                    │                       │
│  │ - SubTask│                    │                       │
│  └────┬─────┘                    │                       │
│       │                          │                       │
│       │ uses                     │ returns               │
│       │                          │                       │
│  ┌────▼─────┐     ┌──────────┐  │                       │
│  │  parser  │────▶│decomposer│──┘                       │
│  │          │     │          │                           │
│  │ parse()  │     │decompose()                          │
│  └──────────┘     └────┬─────┘                          │
│                        │                                  │
│                        │ validates                        │
│                        │                                  │
│                   ┌────▼─────┐                           │
│                   │validators│                           │
│                   │          │                           │
│                   │ validate_│                           │
│                   │dependencies()                        │
│                   └──────────┘                           │
│                                                           │
│  ┌──────────┐                                            │
│  │iterative │  handles feedback                          │
│  │          │  revises plans                             │
│  │ handle_  │                                            │
│  │ feedback()                                            │
│  └──────────┘                                            │
└─────────────────────────────────────────────────────────┘
```

### Protocol Component Relationships

```
┌─────────────────────────────────────────────────────────┐
│                  Protocol Components                     │
│                                                           │
│  MCP:                                                     │
│  ┌──────────┐        ┌──────────┐                       │
│  │MCPServer │◀──────▶│MCPClient │                       │
│  │          │        │          │                       │
│  │ - tools  │        │ discover()                       │
│  │ - invoke()│        │ invoke()  │                       │
│  └──────────┘        └──────────┘                       │
│                                                           │
│  A2A:                                                     │
│  ┌──────────┐        ┌──────────┐                       │
│  │MessageBus│◀──────▶│A2AAgent  │                       │
│  │          │        │          │                       │
│  │ - agents │        │ - caps   │                       │
│  │ - messages│        │ send()   │                       │
│  │ route()  │        │ receive()│                       │
│  └──────────┘        └──────────┘                       │
│                                                           │
│  NLWeb:                                                   │
│  ┌──────────┐                                            │
│  │NLWebBrowser                                           │
│  │          │                                            │
│  │ - state  │                                            │
│  │ execute()│                                            │
│  └──────────┘                                            │
└─────────────────────────────────────────────────────────┘
```

## Sequence Diagrams

### Goal to Execution Sequence

```
User    Security  Parser  Decomposer  Transparency  HITL  MCP    Audit
 │          │        │        │            │         │     │       │
 │ Request  │        │        │            │         │     │       │
 ├─────────▶│        │        │            │         │     │       │
 │          │ Check  │        │            │         │     │       │
 │          ├───✓───▶│        │            │         │     │       │
 │          │        │ Parse  │            │         │     │       │
 │          │        ├───────▶│            │         │     │       │
 │          │        │        │ Decompose  │         │     │       │
 │          │        │        ├───────────▶│         │     │       │
 │          │        │        │            │ Disclose│     │       │
 │          │        │        │            │◀────────┤     │       │
 │          │        │        │            │         │Check│       │
 │          │        │        │            │         ├────▶│       │
 │          │        │        │            │         │  ✓  │       │
 │          │        │        │            │         │     │Execute│
 │          │        │        │            │         │     ├──────▶│
 │          │        │        │            │         │     │       │Log
 │          │        │        │            │         │     │◀──────┤
 │◀─────────────────────────────────────────────────────────Result─┤
 │          │        │        │            │         │     │       │
```

## Design Patterns

### 1. Strategy Pattern (Revision Strategies)

```python
class RevisionStrategy(Enum):
    ADD_STEPS = "add_steps"
    REORDER = "reorder"
    ADJUST_CONSTRAINTS = "adjust_constraints"
    REPLACE_SUBTASK = "replace_subtask"
    SIMPLIFY = "simplify"

# Strategy selection based on feedback
def _select_revision_strategy(feedback):
    if "not found" in feedback.error_message:
        return RevisionStrategy.ADD_STEPS
    elif "timeout" in feedback.error_message:
        return RevisionStrategy.REORDER
    # ...
```

### 2. Factory Pattern (Agent Creation)

```python
class AgentFactory:
    def create_flight_agent(self) -> A2AAgent:
        agent = A2AAgent("flight_agent", "Flight Specialist", bus)
        agent.register_capability(...)
        agent.publish()
        return agent
```

### 3. Observer Pattern (Audit Logging)

```python
class AuditLogger:
    def log_action(self, action, agent_id, user_id, details):
        # All actions are observed and logged
        log = AuditLog(action, agent_id, user_id, details, timestamp)
        self.logs.append(log)
```

### 4. Chain of Responsibility (Validation)

```python
# Validation chain
validators = [
    DependencyValidator(),
    CompletenessValidator()
]

for validator in validators:
    result = validator.validate(plan)
    if not result.valid:
        return result
```

### 5. Facade Pattern (Service Layer)

```python
class AgentService:
    def __init__(self):
        self.parser = GoalParser()
        self.decomposer = TaskDecomposer()
        self.detector = ThreatDetector()
        # ... other components

    def process_request(self, user_id, request):
        # Facade hiding complexity
        goal = self.parser.parse(request)
        plan = self.decomposer.decompose(goal)
        return plan
```

## Security Architecture

### Defense in Depth

```
┌────────────────────────────────────────────────────┐
│              Security Layers                        │
│                                                      │
│  Layer 1: Input Validation                          │
│  ┌──────────────────────────────────────────────┐  │
│  │ Threat Detector                               │  │
│  │  - Task injection detection                   │  │
│  │  - Pattern matching                           │  │
│  │  - Threat classification                      │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Layer 2: Parameter Validation                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ MCP Parameter Validation                      │  │
│  │  - Type checking                              │  │
│  │  - Required field enforcement                 │  │
│  │  - Unknown parameter rejection                │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Layer 3: Authorization                             │
│  ┌──────────────────────────────────────────────┐  │
│  │ HITL (Human-in-the-Loop)                      │  │
│  │  - Risk classification                        │  │
│  │  - Approval requirements                      │  │
│  │  - High-risk action gating                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Layer 4: Transparency                              │
│  ┌──────────────────────────────────────────────┐  │
│  │ UX Transparency Enforcer                      │  │
│  │  - Action explanations                        │  │
│  │  - Plan disclosure                            │  │
│  │  - User awareness                             │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  Layer 5: Audit Trail                               │
│  ┌──────────────────────────────────────────────┐  │
│  │ Audit Logger                                  │  │
│  │  - Complete action logging                    │  │
│  │  - Timestamp tracking                         │  │
│  │  - User/Agent association                     │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### Security Flow

```
Request → Threat Detection → Parameter Validation → HITL Check → Audit Log → Execute
           ↓ block                ↓ reject            ↓ require      ↓ log
         Denied                 Error              Approval       Success
```

## Performance Characteristics

### Latency Targets

```
┌──────────────────────────────────────────┐
│         Component Latencies               │
│                                            │
│  Goal Parsing:         <10ms   ✓          │
│  Plan Decomposition:   <50ms   ✓          │
│  Tool Discovery:       <100ms  ✓          │
│  Tool Invocation:      <10ms*  ✓          │
│  Failure Transparency: <500ms  ✓          │
│                                            │
│  * Excluding actual tool execution time   │
└──────────────────────────────────────────┘
```

### Scalability

- **Horizontal scaling**: Stateless components support load balancing
- **Message bus**: Can be distributed across multiple nodes
- **Tool registry**: Supports distributed tool catalogs
- **Audit logs**: Can be offloaded to external systems

## Extension Points

The framework is designed for extensibility:

1. **New goal types**: Extend `GoalType` enum and add decomposition templates
2. **New protocols**: Add to `protocols/` directory
3. **New security checks**: Extend `ThreatDetector` with new patterns
4. **New revision strategies**: Add to `RevisionStrategy` enum
5. **New validation rules**: Implement new validator classes

## References

- [README.md](README.md) - User guide
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [INTEGRATION.md](INTEGRATION.md) - Integration patterns
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
