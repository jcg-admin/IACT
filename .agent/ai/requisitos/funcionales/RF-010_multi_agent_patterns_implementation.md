---
id: RF-010
tipo: requisito_funcional
relacionado: [UC-SYS-005, ADR-053, RT-011, RT-012]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# RF-010: Multi-Agent Patterns Implementation

## Especificación

El sistema DEBE implementar 3 multi-agent patterns: Group Chat, Hand-off, y Collaborative Filtering para diferentes use cases.

## Criterios de Aceptación

### Pattern 1: Group Chat

#### Escenario 1: Group Chat Creation

```gherkin
Given user request = "What stock should I buy?"
  And 3 expert agents available:
    - IndustryExpertAgent (tech sector)
    - TechnicalAnalysisAgent (chart patterns)
    - FundamentalAnalysisAgent (financials)
When GroupChatPattern.create_group(
    agents=[industry_expert, technical_analyst, fundamental_analyst],
    query="What stock should I buy?"
)
Then group chat created with:
  - group_id assigned
  - 3 agents registered
  - message_history initialized (empty)
  - group status = ACTIVE
```

#### Escenario 2: Broadcast Query to Group

```gherkin
Given group chat with 3 expert agents
  And user_query = "Recommend a tech stock"
When GroupChatPattern.broadcast_to_group(query=user_query)
Then query broadcasted to all 3 agents
  And each agent receives:
    - message_type = BROADCAST
    - from_agent = "user"
    - content = {"query": "Recommend a tech stock"}
  And broadcast latency < 50ms
  And message added to group history
```

#### Escenario 3: Agents Contribute to Group

```gherkin
Given group chat active
  And query broadcasted
When each agent analyzes and responds:
  - IndustryExpert: "AAPL strong in tech sector"
  - TechnicalAnalyst: "AAPL shows bullish pattern (RSI=65)"
  - FundamentalAnalyst: "AAPL P/E ratio attractive (P/E=28)"
Then all 3 responses added to group history
  And each agent sees all responses (shared context)
  And response timestamps recorded
  And total response time < 10s (all agents)
```

#### Escenario 4: Aggregate Group Responses

```gherkin
Given group chat with 3 agent responses:
    - IndustryExpert: "Buy AAPL"
    - TechnicalAnalyst: "Buy AAPL"
    - FundamentalAnalyst: "Buy AAPL"
When GroupChatPattern.aggregate_responses()
Then aggregation result:
  - consensus = "Buy AAPL"
  - confidence = HIGH (3/3 unanimous)
  - reasoning = [all 3 agent reasons]
  - recommendation = "Buy AAPL (unanimous expert consensus)"
```

#### Escenario 5: Group Chat with Disagreement

```gherkin
Given group chat with conflicting responses:
    - Agent A: "Buy AAPL" (confidence: 0.8)
    - Agent B: "Buy MSFT" (confidence: 0.9)
    - Agent C: "Buy GOOGL" (confidence: 0.7)
When GroupChatPattern.aggregate_responses()
Then aggregation uses weighted voting:
  - AAPL score: 0.8
  - MSFT score: 0.9 (winner)
  - GOOGL score: 0.7
  And recommendation = "Buy MSFT (highest confidence)"
  And note = "Disagreement detected: 3 different stocks recommended"
```

### Pattern 2: Hand-off (Linear Workflow)

#### Escenario 6: Hand-off Workflow Creation

```gherkin
Given refund process requires 4 sequential agents
When HandOffPattern.create_workflow(
    agents=[
        CustomerAgent,
        SellerAgent,
        PaymentAgent,
        NotificationAgent
    ]
)
Then linear workflow created:
  - step 1: CustomerAgent
  - step 2: SellerAgent
  - step 3: PaymentAgent
  - step 4: NotificationAgent
  And workflow_id assigned
  And current_step = 0 (not started)
```

#### Escenario 7: Execute Hand-off Workflow

```gherkin
Given refund workflow with 4 agents
  And initial_task = "Process refund for order #12345"
When HandOffPattern.execute_workflow(task=initial_task)
Then workflow executes sequentially:
  - Step 1: CustomerAgent validates → APPROVED
  - Handoff 1: CustomerAgent → SellerAgent
  - Step 2: SellerAgent reviews → APPROVED
  - Handoff 2: SellerAgent → PaymentAgent
  - Step 3: PaymentAgent refunds $50 → SUCCESS
  - Handoff 3: PaymentAgent → NotificationAgent
  - Step 4: NotificationAgent sends email → SENT
  And total workflow duration < 20s
  And all handoffs logged (RT-012)
```

#### Escenario 8: Hand-off with Context Accumulation

```gherkin
Given refund workflow executing
  And CustomerAgent result = {"order_id": "12345", "eligible": True}
  And SellerAgent result = {"approved": True, "reason": "defective"}
When PaymentAgent receives handoff
Then PaymentAgent context includes:
  - previous_results: [customer_result, seller_result]
  - accumulated_context: {
      "order_id": "12345",
      "eligible": True,
      "approved": True,
      "reason": "defective"
    }
  And PaymentAgent uses accumulated context for decision
```

#### Escenario 9: Conditional Hand-off

```gherkin
Given SellerAgent reviewing refund
  And review_result = "REJECTED"
When SellerAgent.decide_next_agent(result=review_result)
Then conditional logic:
  - IF result == "APPROVED":
      Next agent = PaymentAgent
  - ELSE:
      Next agent = NotificationAgent (skip payment)
  And SellerAgent hands off to NotificationAgent (rejection path)
  And workflow skips PaymentAgent step
  And customer notified of rejection
```

#### Escenario 10: Hand-off Chain Interruption

```gherkin
Given hand-off workflow executing
  And current_step = 2 (PaymentAgent)
  And PaymentAgent encounters error: "Payment failed"
When PaymentAgent.handle_error(error="Payment failed")
Then workflow interrupted:
  - status = FAILED
  - failed_at_step = 2 (PaymentAgent)
  - error_reason = "Payment failed"
  And NotificationAgent receives error handoff
  And customer notified: "Refund failed - payment error"
  And workflow trace shows failure point (RT-012)
```

### Pattern 3: Collaborative Filtering

#### Escenario 11: Collaborative Filtering Setup

```gherkin
Given hotel recommendation system
  And 4 specialized agents:
    - PriceAgent (focuses on price)
    - QualityAgent (focuses on quality/rating)
    - LocationAgent (focuses on location)
    - ReviewsAgent (focuses on user reviews)
When CollaborativeFilteringPattern.create(
    agents=[price_agent, quality_agent, location_agent, reviews_agent],
    weights={
        "price": 0.2,
        "quality": 0.4,
        "location": 0.3,
        "reviews": 0.1
    }
)
Then collaborative system created
  And 4 agents registered
  And weights sum to 1.0 ✓
  And aggregator initialized with weights
```

#### Escenario 12: Parallel Recommendations

```gherkin
Given collaborative filtering system
  And query = "Hotel in Paris near Eiffel Tower"
When CollaborativeFilteringPattern.get_recommendation(query)
Then all 4 agents analyze in parallel:
  - PriceAgent scores hotels by price
  - QualityAgent scores hotels by rating
  - LocationAgent scores hotels by proximity
  - ReviewsAgent scores hotels by review sentiment
  And parallel execution duration = max(agent durations)
  And total latency < 5s
```

#### Escenario 13: Weighted Aggregation

```gherkin
Given 4 agents provide scores for 3 hotels:
    | Hotel   | PriceAgent | QualityAgent | LocationAgent | ReviewsAgent |
    | Hotel A | 0.9        | 0.7          | 0.8           | 0.6          |
    | Hotel B | 0.6        | 0.9          | 0.8           | 0.9          |
    | Hotel C | 0.5        | 0.6          | 0.9           | 0.7          |
  And weights = {price: 0.2, quality: 0.4, location: 0.3, reviews: 0.1}
When CollaborativeFilteringPattern.aggregate(scores, weights)
Then weighted scores calculated:
  - Hotel A: (0.9×0.2 + 0.7×0.4 + 0.8×0.3 + 0.6×0.1) = 0.76
  - Hotel B: (0.6×0.2 + 0.9×0.4 + 0.8×0.3 + 0.9×0.1) = 0.81 (winner)
  - Hotel C: (0.5×0.2 + 0.6×0.4 + 0.9×0.3 + 0.7×0.1) = 0.68
  And recommendation = Hotel B (highest weighted score)
```

#### Escenario 14: Confidence-Based Weighting

```gherkin
Given agents provide recommendations with confidence:
    | Agent         | Recommendation | Confidence |
    | PriceAgent    | Hotel A        | 0.9        |
    | QualityAgent  | Hotel B        | 0.95       |
    | LocationAgent | Hotel A        | 0.8        |
    | ReviewsAgent  | Hotel C        | 0.6        |
When CollaborativeFilteringPattern.aggregate_with_confidence()
Then confidence used as additional weight:
  - Hotel A votes: 2 (Price: 0.9, Location: 0.8) → avg confidence: 0.85
  - Hotel B votes: 1 (Quality: 0.95) → avg confidence: 0.95
  - Hotel C votes: 1 (Reviews: 0.6) → avg confidence: 0.6
  And recommendation = Hotel B (highest confidence despite fewer votes)
```

#### Escenario 15: Tie-Breaking

```gherkin
Given collaborative filtering with tie:
    | Hotel   | Total Score |
    | Hotel A | 0.82        |
    | Hotel B | 0.82        |
When CollaborativeFilteringPattern.break_tie([Hotel A, Hotel B])
Then tie-breaker strategies applied in order:
  1. Highest individual agent score → Hotel B wins (quality: 0.9 > 0.7)
  2. If still tied: Most agent votes → count votes
  3. If still tied: Random selection → pick randomly
  And winner selected deterministically
```

### Pattern Integration and Orchestration

#### Escenario 16: Orchestrator Routes to Pattern

```gherkin
Given Orchestrator receives user request
  And request_type = "stock_recommendation"
When Orchestrator.determine_pattern(request_type)
Then pattern selected = GROUP_CHAT
  And reason = "Multiple expert opinions needed"
  And GroupChatPattern instantiated
  And request routed to group chat
```

#### Escenario 17: Pattern Switching Mid-Workflow

```gherkin
Given workflow starts with HAND_OFF pattern (refund)
  And at step 2, decision requires expert consensus
When workflow detects need for GROUP_CHAT
Then pattern switches:
  - Pause HAND_OFF at step 2
  - Create GROUP_CHAT with 3 approval agents
  - Aggregate group decision
  - Resume HAND_OFF with group result
  And pattern switch logged (RT-012)
  And total latency impact < 2s
```

#### Escenario 18: Parallel Patterns

```gherkin
Given complex task requiring both patterns simultaneously
When Orchestrator.execute_parallel_patterns(
    patterns=[
        CollaborativeFiltering(task="find hotel"),
        CollaborativeFiltering(task="find flight")
    ]
)
Then both patterns execute in parallel:
  - Hotel recommendation (4 agents)
  - Flight recommendation (3 agents)
  And total duration = max(hotel_time, flight_time)
  And results aggregated from both patterns
```

### Observability and Debugging

#### Escenario 19: Pattern Tracing

```gherkin
Given GROUP_CHAT pattern executing
  And workflow_id = "wf_stock_rec_123"
When pattern creates spans for tracing
Then trace includes:
  - span: "group_chat.broadcast" (broadcast query)
  - span: "industry_expert.analyze" (agent 1)
  - span: "technical_analyst.analyze" (agent 2)
  - span: "fundamental_analyst.analyze" (agent 3)
  - span: "group_chat.aggregate" (aggregate responses)
  And trace visualized in dashboard (RT-012)
  And critical path identified
```

#### Escenario 20: Pattern Performance Metrics

```gherkin
Given system operates for 1 day
  And 100 GROUP_CHAT patterns executed
  And 200 HAND_OFF patterns executed
  And 150 COLLABORATIVE_FILTERING patterns executed
When metrics collected
Then pattern-specific metrics:
  - group_chat.duration_avg = 8.5s
  - group_chat.consensus_rate = 0.75 (75% unanimous)
  - hand_off.duration_avg = 12.3s
  - hand_off.completion_rate = 0.98 (98% complete)
  - collaborative_filtering.duration_avg = 4.2s
  - collaborative_filtering.accuracy = 0.87 (user satisfaction)
  And metrics exported to dashboard
```

## Implementación

Archivo: `scripts/coding/ai/multi_agent/patterns/group_chat.py`

```python
class GroupChatPattern:
    """
    RF-010: Group chat pattern for collaborative problem-solving.
    All agents see all messages.
    """

    def __init__(self, agents: List[Agent]):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.group_id = str(uuid.uuid4())
        self.message_history: List[Message] = []
        self.status = GroupStatus.ACTIVE

    def broadcast_to_group(self, query: str, from_agent: str = "user"):
        """
        RF-010: Broadcast query to all agents in group.
        """
        message = Message(
            from_agent=from_agent,
            to_agent="group",
            message_type=MessageType.BROADCAST,
            content={"query": query}
        )

        # Add to history
        self.message_history.append(message)

        # Broadcast to all agents
        for agent_id, agent in self.agents.items():
            agent.receive_message(message)

        logger.info(
            f"Group {self.group_id}: Broadcasted query to {len(self.agents)} agents"
        )

    def collect_responses(self, timeout_seconds: int = 10) -> List[Dict]:
        """
        RF-010: Collect responses from all agents.

        Returns:
            List of agent responses
        """
        responses = []
        start_time = time.time()

        # Wait for all agents to respond (or timeout)
        while len(responses) < len(self.agents):
            if time.time() - start_time > timeout_seconds:
                logger.warning(
                    f"Group {self.group_id}: Timeout waiting for responses. "
                    f"Received {len(responses)}/{len(self.agents)}"
                )
                break

            # Check for new responses
            for agent_id, agent in self.agents.items():
                if agent.has_response() and agent_id not in [r["agent_id"] for r in responses]:
                    response = agent.get_response()
                    responses.append({
                        "agent_id": agent_id,
                        "recommendation": response["recommendation"],
                        "confidence": response.get("confidence", 0.5),
                        "reasoning": response.get("reasoning", "")
                    })

                    # Add to group history (all agents see this)
                    self.message_history.append(
                        Message(
                            from_agent=agent_id,
                            to_agent="group",
                            message_type=MessageType.RESPONSE,
                            content=response
                        )
                    )

            time.sleep(0.1)  # Poll interval

        return responses

    def aggregate_responses(
        self,
        responses: List[Dict],
        strategy: str = "consensus"
    ) -> Dict:
        """
        RF-010: Aggregate agent responses.

        Args:
            responses: List of agent responses
            strategy: "consensus", "weighted_voting", "highest_confidence"

        Returns:
            Aggregated recommendation
        """
        if strategy == "consensus":
            # Check if all agents agree
            recommendations = [r["recommendation"] for r in responses]
            if len(set(recommendations)) == 1:
                # Unanimous
                return {
                    "consensus": recommendations[0],
                    "confidence": "HIGH",
                    "reasoning": [r["reasoning"] for r in responses],
                    "recommendation": f"{recommendations[0]} (unanimous consensus)"
                }
            else:
                # Disagreement - use weighted voting
                return self._weighted_voting(responses)

        elif strategy == "weighted_voting":
            return self._weighted_voting(responses)

        elif strategy == "highest_confidence":
            # Return recommendation with highest confidence
            best = max(responses, key=lambda r: r["confidence"])
            return {
                "recommendation": best["recommendation"],
                "confidence": best["confidence"],
                "reasoning": best["reasoning"],
                "note": "Selected based on highest confidence"
            }

    def _weighted_voting(self, responses: List[Dict]) -> Dict:
        """Weighted voting based on confidence."""
        votes = {}

        for response in responses:
            rec = response["recommendation"]
            conf = response["confidence"]

            if rec not in votes:
                votes[rec] = 0

            votes[rec] += conf

        # Winner
        winner = max(votes, key=votes.get)

        return {
            "recommendation": winner,
            "score": votes[winner],
            "votes": votes,
            "note": f"Disagreement detected: {len(votes)} different recommendations"
        }
```

Archivo: `scripts/coding/ai/multi_agent/patterns/hand_off.py`

```python
class HandOffPattern:
    """
    RF-010: Hand-off pattern for sequential workflows.
    Agent A → Agent B → Agent C
    """

    def __init__(self, agents: List[Agent]):
        self.workflow = agents  # Ordered list
        self.workflow_id = str(uuid.uuid4())
        self.current_step = 0
        self.accumulated_context = {}

    def execute_workflow(self, initial_task: Task) -> Result:
        """
        RF-010: Execute workflow with hand-offs.

        Returns:
            Final result from last agent
        """
        task = initial_task
        result = None

        for step, agent in enumerate(self.workflow):
            logger.info(
                f"Workflow {self.workflow_id}: Step {step + 1}/{len(self.workflow)} "
                f"- {agent.agent_id}"
            )

            # Execute agent
            result = agent.execute(task)

            # Accumulate context (RF-010 Scenario 8)
            self.accumulated_context.update(result.data)

            # Check if should handoff
            if step < len(self.workflow) - 1:  # Not last agent
                next_agent = self.workflow[step + 1]

                # Conditional handoff (RF-010 Scenario 9)
                if result.should_handoff:
                    # Hand off to next agent
                    self._handoff(
                        from_agent=agent,
                        to_agent=next_agent,
                        result=result
                    )

                    # Create task for next agent
                    task = Task(
                        description=result.next_task_description,
                        context=self.accumulated_context
                    )
                else:
                    # Workflow interrupted (RF-010 Scenario 10)
                    logger.warning(
                        f"Workflow {self.workflow_id}: Interrupted at step {step + 1}"
                    )
                    break

            self.current_step = step + 1

        return result

    def _handoff(self, from_agent: Agent, to_agent: Agent, result: AgentResult):
        """Execute handoff between agents."""
        handoff_manager.handoff(
            from_agent=from_agent,
            to_agent=to_agent,
            task_description=result.next_task_description,
            context=self.accumulated_context,
            previous_result=result.data
        )
```

Archivo: `scripts/coding/ai/multi_agent/patterns/collaborative_filtering.py`

```python
class CollaborativeFilteringPattern:
    """
    RF-010: Collaborative filtering pattern.
    Multiple agents provide independent recommendations,
    aggregated with weighted scoring.
    """

    def __init__(self, agents: List[Agent], weights: Dict[str, float]):
        self.agents = agents
        self.weights = weights
        self.validate_weights()

    def validate_weights(self):
        """Ensure weights sum to 1.0."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def get_recommendation(self, query: str) -> Recommendation:
        """
        RF-010: Get collaborative recommendation.

        Returns:
            Aggregated recommendation with weighted scores
        """
        # Get recommendations from all agents (in parallel)
        recommendations = []

        for agent in self.agents:
            rec = agent.recommend(query)
            recommendations.append({
                "agent": agent.agent_id,
                "recommendation": rec,
                "score": rec.score,
                "confidence": rec.confidence
            })

        # Aggregate with weighted scores (RF-010 Scenario 13)
        final_recommendation = self.aggregate(recommendations)

        return final_recommendation

    def aggregate(self, recommendations: List[Dict]) -> Recommendation:
        """
        RF-010: Weighted aggregation of recommendations.
        """
        # Collect all unique options
        all_options = set()
        for rec in recommendations:
            all_options.add(rec["recommendation"].option)

        # Calculate weighted score for each option
        option_scores = {}

        for option in all_options:
            weighted_score = 0

            for rec in recommendations:
                if rec["recommendation"].option == option:
                    agent_type = self._get_agent_type(rec["agent"])
                    weight = self.weights.get(agent_type, 0)
                    agent_score = rec["score"]

                    weighted_score += weight * agent_score

            option_scores[option] = weighted_score

        # Select winner
        winner = max(option_scores, key=option_scores.get)

        return Recommendation(
            option=winner,
            score=option_scores[winner],
            method="weighted_collaborative_filtering",
            breakdown=option_scores
        )
```

## Tests

Archivo: `scripts/coding/tests/ai/test_multi_agent_patterns.py`

```python
class TestGroupChatPattern:
    def test_group_chat_broadcast(self):
        """RF-010 Scenario 2: Broadcast query to group."""
        agents = [
            MockAgent("IndustryExpert"),
            MockAgent("TechnicalAnalyst"),
            MockAgent("FundamentalAnalyst")
        ]

        group = GroupChatPattern(agents=agents)

        start = time.perf_counter()
        group.broadcast_to_group("What stock should I buy?")
        latency_ms = (time.perf_counter() - start) * 1000

        assert latency_ms < 50
        assert len(group.message_history) == 1
        # Verify all agents received
        for agent in agents:
            assert agent.received_messages_count() == 1

    def test_group_chat_consensus(self):
        """RF-010 Scenario 4: Aggregate with consensus."""
        agents = [
            MockAgent("Agent1", response={"recommendation": "Buy AAPL"}),
            MockAgent("Agent2", response={"recommendation": "Buy AAPL"}),
            MockAgent("Agent3", response={"recommendation": "Buy AAPL"})
        ]

        group = GroupChatPattern(agents=agents)
        group.broadcast_to_group("Stock recommendation?")
        responses = group.collect_responses()

        result = group.aggregate_responses(responses, strategy="consensus")

        assert result["consensus"] == "Buy AAPL"
        assert result["confidence"] == "HIGH"


class TestHandOffPattern:
    def test_handoff_workflow_execution(self):
        """RF-010 Scenario 7: Execute hand-off workflow."""
        agents = [
            MockAgent("CustomerAgent"),
            MockAgent("SellerAgent"),
            MockAgent("PaymentAgent"),
            MockAgent("NotificationAgent")
        ]

        workflow = HandOffPattern(agents=agents)

        task = Task(description="Process refund for order #12345")

        result = workflow.execute_workflow(task)

        assert result is not None
        assert workflow.current_step == 4  # All 4 steps completed


class TestCollaborativeFiltering:
    def test_weighted_aggregation(self):
        """RF-010 Scenario 13: Weighted aggregation."""
        agents = [
            MockAgent("PriceAgent"),
            MockAgent("QualityAgent"),
            MockAgent("LocationAgent"),
            MockAgent("ReviewsAgent")
        ]

        weights = {"price": 0.2, "quality": 0.4, "location": 0.3, "reviews": 0.1}

        cf = CollaborativeFilteringPattern(agents=agents, weights=weights)

        # Mock scores for Hotel B
        # Expected: (0.6×0.2 + 0.9×0.4 + 0.8×0.3 + 0.9×0.1) = 0.81

        recommendation = cf.get_recommendation("Hotel in Paris")

        assert recommendation.option == "Hotel B"
        assert abs(recommendation.score - 0.81) < 0.01
```

Resultado esperado: `20 passed in 0.35s`

## Métricas

- Group chat consensus rate: > 75%
- Group chat duration avg: < 10s
- Hand-off completion rate: > 98%
- Hand-off duration avg: < 15s
- Collaborative filtering accuracy: > 85%
- Pattern execution latency p95: < 20s

## Referencias

- UC-SYS-005: Multi-Agent Orchestration
- ADR-053: Multi-Agent Design Patterns
- RT-011: Multi-Agent Communication and Coordination
- RT-012: Multi-Agent Performance and Observability

---

**Requisito**: Sistema implementa 3 multi-agent patterns con observability completa.
**Verificación**: Gherkin scenarios + pattern-specific metrics + TDD tests.
