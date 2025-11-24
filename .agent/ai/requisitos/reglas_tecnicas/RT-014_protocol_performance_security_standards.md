# RT-014: Protocol Performance and Security Standards

**Estado**: Activo
**Fecha**: 2025-11-16
**Contexto**: AI Agent System - Agent Protocols
**Relación**:
- Implementa [ADR-055: Agent Protocols Architecture](../../../gobernanza/adr/ADR-055-agent-protocols-architecture.md)
- Relacionado con [RT-013: Planning Performance and Quality Standards](./RT-013_planning_performance_quality_standards.md)

---

## Propósito

Define performance targets, security requirements, and operational standards for the three agent protocols (MCP, A2A, NLWeb) to ensure secure, efficient, and reliable inter-agent and tool communication.

---

## Performance Standards

### MCP (Model Context Protocol)

| Operation | Target Latency | Target Throughput | Enforcement |
|-----------|----------------|-------------------|-------------|
| Tool Discovery (list_tools) | < 100ms | ≥ 100 requests/sec | Caching + timeout |
| Tool Invocation (simple) | < 500ms | ≥ 50 calls/sec | Timeout decorator |
| Tool Invocation (complex) | < 2s | ≥ 10 calls/sec | Timeout + retry |
| Schema Validation | < 50ms | ≥ 200 validations/sec | Pydantic caching |

**Enforcement**:
```python
from functools import lru_cache
import time

class MCPPerformanceMonitor:
    LATENCY_TARGETS = {
        "list_tools": 0.1,
        "invoke_tool_simple": 0.5,
        "invoke_tool_complex": 2.0,
        "validate_schema": 0.05
    }

    @staticmethod
    def enforce_latency(operation: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                result = func(*args, **kwargs)
                duration = time.time() - start

                target = MCPPerformanceMonitor.LATENCY_TARGETS.get(operation, 1.0)
                if duration > target:
                    logger.warning(f"{operation} took {duration:.2f}s (target: {target}s)")

                return result
            return wrapper
        return decorator

# Usage
class MCPServer:
    @lru_cache(maxsize=100)  # Cache tool list
    @MCPPerformanceMonitor.enforce_latency("list_tools")
    def list_tools(self) -> List[ToolDefinition]:
        return list(self.tools.values())
```

### A2A (Agent-to-Agent Protocol)

| Operation | Target Latency | Target Throughput | Enforcement |
|-----------|----------------|-------------------|-------------|
| Send Message | < 50ms | ≥ 200 messages/sec | Non-blocking send |
| Receive Message | < 100ms | ≥ 100 messages/sec | Queue-based |
| Agent Discovery | < 200ms | ≥ 50 queries/sec | Registry caching |
| Artifact Creation | < 100ms | ≥ 100 artifacts/sec | Async storage |
| Capability Invocation | < 1s | ≥ 20 calls/sec | Timeout + circuit breaker |

**Enforcement**:
```python
import asyncio
from collections import deque

class A2AMessageQueue:
    def __init__(self, max_size: int = 10000):
        self.queue = deque(maxlen=max_size)
        self.latency_stats = []

    async def send_message(self, message: A2AMessage):
        """Non-blocking message send."""
        start = time.time()

        # Add to queue (non-blocking)
        self.queue.append(message)

        duration = time.time() - start
        self.latency_stats.append(duration)

        if duration > 0.05:  # 50ms target
            logger.warning(f"Message send took {duration:.3f}s")

        return message.message_id

    async def receive_message(self, timeout: float = 0.1):
        """Non-blocking message receive."""
        start = time.time()

        try:
            message = self.queue.popleft()
            duration = time.time() - start

            if duration > 0.1:  # 100ms target
                logger.warning(f"Message receive took {duration:.3f}s")

            return message
        except IndexError:
            return None
```

### NLWeb (Natural Language Web)

| Operation | Target Latency | Target Throughput | Enforcement |
|-----------|----------------|-------------------|-------------|
| Browser Launch | < 2s | N/A (persistent) | Reuse browser sessions |
| Page Navigation | < 3s | ≥ 20 pages/min | Timeout + parallel browsers |
| Action Execution | < 1s per action | ≥ 30 actions/min | Timeout per action |
| Data Extraction | < 2s | ≥ 20 extractions/min | Optimized selectors |
| Full Action Sequence | < 10s | ≥ 6 sequences/min | Total timeout |

**Enforcement**:
```python
class NLWebPerformanceMonitor:
    MAX_BROWSER_LIFETIME = 300  # 5 minutes, then restart

    def __init__(self):
        self.browser_start_time = None
        self.action_latencies = []

    def execute_with_timeout(self, action: NLWebAction, page: Page, timeout: float):
        """Execute action with performance monitoring."""
        start = time.time()

        try:
            if action.action_type == ActionType.NAVIGATE:
                page.goto(action.value, timeout=timeout * 1000)
            elif action.action_type == ActionType.CLICK:
                page.click(action.selector, timeout=timeout * 1000)
            # ... other actions

            duration = time.time() - start
            self.action_latencies.append(duration)

            return True
        except TimeoutError:
            logger.error(f"Action {action.action_type} timed out after {timeout}s")
            return False

    def should_restart_browser(self) -> bool:
        """Check if browser should be restarted for performance."""
        if not self.browser_start_time:
            return False

        lifetime = time.time() - self.browser_start_time
        return lifetime > self.MAX_BROWSER_LIFETIME
```

---

## Security Standards

### MCP Security

**Authentication**:
```python
from typing import Optional
import hmac
import hashlib

class MCPSecurityManager:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def authenticate_client(self, client_id: str, signature: str, timestamp: str) -> bool:
        """
        Authenticate MCP client using HMAC signature.

        Args:
            client_id: Client identifier
            signature: HMAC signature
            timestamp: Request timestamp

        Returns:
            True if authenticated
        """
        # Verify timestamp (prevent replay attacks)
        request_time = int(timestamp)
        current_time = int(time.time())

        if abs(current_time - request_time) > 300:  # 5 minute window
            logger.warning(f"Request timestamp too old: {timestamp}")
            return False

        # Verify HMAC signature
        message = f"{client_id}:{timestamp}"
        expected_signature = hmac.new(
            self.api_key.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def authorize_tool_access(self, client_id: str, tool_name: str) -> bool:
        """
        Authorize client access to specific tool.

        Args:
            client_id: Client identifier
            tool_name: Tool to access

        Returns:
            True if authorized
        """
        # Implement access control logic
        # Example: Check against ACL database
        allowed_tools = self._get_client_permissions(client_id)
        return tool_name in allowed_tools
```

**Input Validation**:
```python
class MCPInputValidator:
    MAX_PARAM_LENGTH = 10000  # Max parameter string length
    MAX_PARAMS_COUNT = 50  # Max number of parameters

    def validate_tool_invocation(self, tool_def: ToolDefinition, parameters: Dict[str, Any]):
        """
        Validate tool invocation parameters.

        Raises:
            ValidationError: If validation fails
        """
        # 1. Check parameter count
        if len(parameters) > self.MAX_PARAMS_COUNT:
            raise ValidationError(f"Too many parameters: {len(parameters)}")

        # 2. Check parameter sizes
        for key, value in parameters.items():
            if isinstance(value, str) and len(value) > self.MAX_PARAM_LENGTH:
                raise ValidationError(f"Parameter '{key}' too long: {len(value)} chars")

        # 3. Validate against schema
        for param_def in tool_def.parameters:
            if param_def.required and param_def.name not in parameters:
                raise ValidationError(f"Missing required parameter: {param_def.name}")

            if param_def.name in parameters:
                value = parameters[param_def.name]

                # Type validation
                if not self._validate_type(value, param_def.type):
                    raise ValidationError(
                        f"Parameter '{param_def.name}' has invalid type. "
                        f"Expected {param_def.type}, got {type(value).__name__}"
                    )

                # Enum validation
                if param_def.enum and value not in param_def.enum:
                    raise ValidationError(
                        f"Parameter '{param_def.name}' must be one of {param_def.enum}"
                    )

    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type matches expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }

        expected_python_type = type_map.get(expected_type)
        if not expected_python_type:
            return True  # Unknown type, skip validation

        return isinstance(value, expected_python_type)
```

**Rate Limiting**:
```python
from collections import defaultdict
from datetime import datetime, timedelta

class MCPRateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_history: Dict[str, List[datetime]] = defaultdict(list)

    def allow_request(self, client_id: str) -> bool:
        """
        Check if request should be allowed based on rate limit.

        Args:
            client_id: Client making the request

        Returns:
            True if request allowed, False if rate limit exceeded
        """
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)

        # Clean up old requests
        self.request_history[client_id] = [
            req_time for req_time in self.request_history[client_id]
            if req_time > one_minute_ago
        ]

        # Check rate limit
        if len(self.request_history[client_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            return False

        # Record this request
        self.request_history[client_id].append(now)
        return True
```

### A2A Security

**Message Encryption**:
```python
from cryptography.fernet import Fernet

class A2AEncryption:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)

    def encrypt_message(self, message: A2AMessage) -> bytes:
        """Encrypt A2A message."""
        message_json = message.model_dump_json()
        encrypted = self.cipher.encrypt(message_json.encode())
        return encrypted

    def decrypt_message(self, encrypted_data: bytes) -> A2AMessage:
        """Decrypt A2A message."""
        decrypted = self.cipher.decrypt(encrypted_data)
        message_json = decrypted.decode()
        return A2AMessage.model_validate_json(message_json)
```

**Agent Identity Verification**:
```python
class A2AIdentityVerifier:
    def __init__(self):
        self.trusted_agents: Dict[str, str] = {}  # agent_id → public_key

    def register_agent(self, agent_id: str, public_key: str):
        """Register trusted agent with public key."""
        self.trusted_agents[agent_id] = public_key

    def verify_message_signature(self, message: A2AMessage, signature: str) -> bool:
        """
        Verify message was sent by claimed agent.

        Args:
            message: The message
            signature: Digital signature

        Returns:
            True if signature valid
        """
        if message.from_agent not in self.trusted_agents:
            logger.warning(f"Unknown agent: {message.from_agent}")
            return False

        public_key = self.trusted_agents[message.from_agent]

        # Verify signature using public key cryptography
        # (Implementation depends on crypto library)
        message_hash = hashlib.sha256(message.model_dump_json().encode()).hexdigest()
        # ... verify signature matches hash with public key

        return True  # Simplified
```

### NLWeb Security

**Sandboxing**:
```python
class NLWebSandbox:
    ALLOWED_DOMAINS = [
        "airline.com",
        "hotel.com",
        "booking.com"
    ]

    def validate_url(self, url: str) -> bool:
        """
        Validate URL is allowed.

        Args:
            url: URL to validate

        Returns:
            True if URL is in allowed domains
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        domain = parsed.netloc

        # Check if domain is in allowed list
        for allowed_domain in self.ALLOWED_DOMAINS:
            if domain.endswith(allowed_domain):
                return True

        logger.warning(f"Blocked navigation to untrusted domain: {domain}")
        return False

    def execute_with_sandbox(self, executor: NLWebExecutor, action: NLWebAction):
        """Execute action with security sandbox."""

        # Validate URL before navigation
        if action.action_type == ActionType.NAVIGATE:
            if not self.validate_url(action.value):
                raise SecurityError(f"Navigation to {action.value} blocked")

        # Disable dangerous features
        executor.page.context.set_extra_http_headers({
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'"
        })

        # Execute action
        return executor._execute_single_action(action)
```

---

## Monitoring and Alerts

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge

# MCP Metrics
mcp_tool_invocations = Counter(
    'mcp_tool_invocations_total',
    'Total MCP tool invocations',
    ['tool_name', 'status']
)

mcp_latency = Histogram(
    'mcp_operation_latency_seconds',
    'MCP operation latency',
    ['operation'],
    buckets=[0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

# A2A Metrics
a2a_messages_sent = Counter(
    'a2a_messages_sent_total',
    'Total A2A messages sent',
    ['from_agent', 'to_agent', 'message_type']
)

a2a_queue_depth = Gauge(
    'a2a_message_queue_depth',
    'Current A2A message queue depth',
    ['agent_id']
)

# NLWeb Metrics
nlweb_actions_executed = Counter(
    'nlweb_actions_total',
    'Total NLWeb actions executed',
    ['action_type', 'status']
)

nlweb_browser_restarts = Counter(
    'nlweb_browser_restarts_total',
    'Total browser restarts'
)
```

### Alerts Configuration

```yaml
alerts:
  - name: "MCP High Latency"
    condition: mcp_operation_latency_seconds{quantile="0.95"} > 2.0
    severity: warning
    message: "MCP operations slow (p95 > 2s)"

  - name: "A2A Queue Backlog"
    condition: a2a_message_queue_depth > 5000
    severity: critical
    message: "A2A message queue backlog critical"

  - name: "NLWeb Frequent Restarts"
    condition: rate(nlweb_browser_restarts_total[5m]) > 5
    severity: warning
    message: "NLWeb browser restarting too frequently"

  - name: "Authentication Failures"
    condition: rate(mcp_auth_failures_total[1m]) > 10
    severity: critical
    message: "High rate of authentication failures - possible attack"
```

---

## Cost Standards

| Protocol | Operation | Target Cost | Budget |
|----------|-----------|-------------|--------|
| MCP | Tool invocation | Variable | $0.10 per 100 calls |
| A2A | Message passing | $0 (internal) | N/A |
| NLWeb | Action sequence | $0.02 per sequence | $1 per 50 sequences |

---

## Referencias

1. [ADR-055: Agent Protocols Architecture](../../../gobernanza/adr/ADR-055-agent-protocols-architecture.md)
2. [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
3. [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

**Versión**: 1.0
**Última actualización**: 2025-11-16
