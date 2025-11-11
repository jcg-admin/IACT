#!/usr/bin/env python3
"""
Knowledge and Context Techniques

Implements: Generated Knowledge, RAG, ReAct, and Automatic Reasoning and Tool-use
for knowledge-enhanced prompting.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any, Tuple
from enum import Enum
import json


class KnowledgeSource(Enum):
    """Source of knowledge."""
    GENERATED = "generated"
    RETRIEVED = "retrieved"
    COMPUTED = "computed"
    OBSERVED = "observed"


class ActionStatus(Enum):
    """Status of an action."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class KnowledgeItem:
    """Single piece of knowledge."""
    content: str
    source: KnowledgeSource
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReActStep:
    """Single step in ReAct cycle."""
    thought: str
    action: str
    observation: str
    step_number: int


@dataclass
class Tool:
    """Tool available for use."""
    name: str
    description: str
    parameters: Dict[str, Any]
    executor: Callable


class GeneratedKnowledgePrompting:
    """
    Generated Knowledge Prompting: Generate relevant knowledge before main task.

    Usage: Tasks requiring specific knowledge not explicitly provided.
    """

    def __init__(self):
        """Initialize knowledge prompting."""
        self.generated_knowledge: List[KnowledgeItem] = []

    def create_knowledge_generation_prompt(
        self,
        domain: str,
        specific_topics: List[str],
        knowledge_depth: str = "comprehensive"
    ) -> str:
        """
        Create prompt to generate domain knowledge.

        Args:
            domain: Knowledge domain
            specific_topics: Specific topics to cover
            knowledge_depth: Level of detail (basic/comprehensive/expert)

        Returns:
            Knowledge generation prompt
        """
        prompt_parts = []

        prompt_parts.append(f"KNOWLEDGE GENERATION TASK")
        prompt_parts.append(f"Domain: {domain}")
        prompt_parts.append(f"Depth Level: {knowledge_depth}\n")

        prompt_parts.append("Generate knowledge on the following topics:")
        for i, topic in enumerate(specific_topics, 1):
            prompt_parts.append(f"{i}. {topic}")

        prompt_parts.append("\nFor each topic, provide:")
        prompt_parts.append("- Key principles and concepts")
        prompt_parts.append("- Best practices")
        prompt_parts.append("- Common pitfalls to avoid")
        prompt_parts.append("- Relevant examples or patterns")

        prompt_parts.append("\nVALIDATION:")
        prompt_parts.append("- Base knowledge on established principles")
        prompt_parts.append("- Cite sources when referencing specific standards")
        prompt_parts.append("- Indicate confidence level for each statement")

        return "\n".join(prompt_parts)

    def create_application_prompt(
        self,
        task: str,
        generated_knowledge: List[str],
        specific_requirements: Optional[List[str]] = None
    ) -> str:
        """
        Create prompt applying generated knowledge to task.

        Args:
            task: The task to perform
            generated_knowledge: Previously generated knowledge
            specific_requirements: Optional specific requirements

        Returns:
            Application prompt with knowledge context
        """
        prompt_parts = []

        prompt_parts.append("KNOWLEDGE-ENHANCED TASK\n")

        # Include generated knowledge
        prompt_parts.append("RELEVANT KNOWLEDGE:")
        for i, knowledge in enumerate(generated_knowledge, 1):
            prompt_parts.append(f"\n{i}. {knowledge}")

        # Add the task
        prompt_parts.append(f"\n\nTASK:\n{task}")

        # Add requirements if provided
        if specific_requirements:
            prompt_parts.append("\n\nREQUIREMENTS:")
            for req in specific_requirements:
                prompt_parts.append(f"- {req}")

        prompt_parts.append("\n\nINSTRUCTIONS:")
        prompt_parts.append("Apply the knowledge provided to complete the task")
        prompt_parts.append("Reference specific principles when making decisions")
        prompt_parts.append("Explain your reasoning based on the knowledge")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_two_phase_prompt(
        domain: str,
        topics: List[str],
        task: str
    ) -> Tuple[str, str]:
        """
        Create two-phase prompts: knowledge generation + application.

        Args:
            domain: Knowledge domain
            topics: Topics to generate knowledge about
            task: Task to apply knowledge to

        Returns:
            Tuple of (generation_prompt, application_prompt_template)
        """
        gen_prompt = GeneratedKnowledgePrompting().create_knowledge_generation_prompt(
            domain, topics
        )

        app_template = """KNOWLEDGE-ENHANCED TASK

RELEVANT KNOWLEDGE:
{generated_knowledge}

TASK:
{task}

Apply the knowledge to complete this task effectively.
"""

        return gen_prompt, app_template.format(task=task, generated_knowledge="{generated_knowledge}")


class RetrievalAugmentedGeneration:
    """
    RAG: Combine information retrieval with generation.

    Usage: Tasks requiring specific, up-to-date, or specialized information.
    """

    def __init__(
        self,
        retriever: Optional[Callable[[str], List[Dict]]] = None
    ):
        """
        Initialize RAG.

        Args:
            retriever: Function that retrieves relevant documents
        """
        self.retriever = retriever
        self.retrieved_docs: List[Dict] = []

    def create_prompt_with_retrieval(
        self,
        query: str,
        retrieved_documents: List[Dict[str, Any]],
        task: str,
        max_docs: int = 5
    ) -> str:
        """
        Create prompt with retrieved context.

        Args:
            query: Search query used
            retrieved_documents: Documents retrieved
            task: Task to perform
            max_docs: Maximum documents to include

        Returns:
            RAG-enhanced prompt
        """
        prompt_parts = []

        prompt_parts.append("RETRIEVAL-AUGMENTED TASK\n")
        prompt_parts.append(f"Query: {query}\n")

        # Add retrieved documents
        prompt_parts.append("RETRIEVED INFORMATION:")
        for i, doc in enumerate(retrieved_documents[:max_docs], 1):
            prompt_parts.append(f"\n[Document {i}]")
            prompt_parts.append(f"Source: {doc.get('source', 'Unknown')}")
            if 'relevance_score' in doc:
                prompt_parts.append(f"Relevance: {doc['relevance_score']:.2f}")
            prompt_parts.append(f"Content: {doc.get('content', '')}")

        # Add the task
        prompt_parts.append(f"\n\nTASK:\n{task}")

        # Add instructions
        prompt_parts.append("\n\nINSTRUCTIONS:")
        prompt_parts.append("- Base your answer on the retrieved information")
        prompt_parts.append("- Cite specific sources when referencing information")
        prompt_parts.append("- If information is missing, state what is needed")
        prompt_parts.append("- Do not fabricate information not in the documents")

        return "\n".join(prompt_parts)

    @staticmethod
    def format_retrieved_context(documents: List[Dict]) -> str:
        """
        Format retrieved documents for inclusion in prompts.

        Args:
            documents: List of retrieved documents

        Returns:
            Formatted context string
        """
        formatted_parts = []

        for i, doc in enumerate(documents, 1):
            formatted_parts.append(f"Document {i}:")
            formatted_parts.append(f"  Source: {doc.get('source', 'N/A')}")
            formatted_parts.append(f"  Content: {doc.get('content', 'N/A')}")
            if 'metadata' in doc:
                formatted_parts.append(f"  Metadata: {json.dumps(doc['metadata'])}")
            formatted_parts.append("")

        return "\n".join(formatted_parts)


class ReActPrompting:
    """
    ReAct: Reasoning + Acting in interleaved sequence.

    Usage: Tasks requiring interaction with tools or external systems.
    """

    def __init__(self):
        """Initialize ReAct prompting."""
        self.steps: List[ReActStep] = []

    def create_react_prompt(
        self,
        task: str,
        available_actions: List[str],
        context: Optional[str] = None
    ) -> str:
        """
        Create ReAct prompt.

        Args:
            task: Task to accomplish
            available_actions: Actions that can be taken
            context: Optional context information

        Returns:
            ReAct-structured prompt
        """
        prompt_parts = []

        prompt_parts.append("ReAct PROBLEM SOLVING\n")

        if context:
            prompt_parts.append(f"CONTEXT:\n{context}\n")

        prompt_parts.append(f"TASK:\n{task}\n")

        prompt_parts.append("AVAILABLE ACTIONS:")
        for action in available_actions:
            prompt_parts.append(f"- {action}")

        prompt_parts.append("\n\nREACT CYCLE:")
        prompt_parts.append("Follow this pattern for each step:\n")
        prompt_parts.append("Thought: [Your reasoning about what to do next]")
        prompt_parts.append("Action: [The action to take from available actions]")
        prompt_parts.append("Observation: [Result of the action]\n")

        prompt_parts.append("Continue Thought-Action-Observation cycles until task is complete.")
        prompt_parts.append("\nWhen done, state:")
        prompt_parts.append("Thought: Task completed")
        prompt_parts.append("Answer: [Final answer]")

        return "\n".join(prompt_parts)

    def format_react_execution(
        self,
        steps: List[Dict[str, str]]
    ) -> str:
        """
        Format ReAct execution steps.

        Args:
            steps: List of thought-action-observation dicts

        Returns:
            Formatted execution log
        """
        formatted_parts = []

        for i, step in enumerate(steps, 1):
            formatted_parts.append(f"Step {i}:")
            formatted_parts.append(f"Thought: {step.get('thought', '')}")
            formatted_parts.append(f"Action: {step.get('action', '')}")
            formatted_parts.append(f"Observation: {step.get('observation', '')}")
            formatted_parts.append("")

        return "\n".join(formatted_parts)

    @staticmethod
    def create_database_react_prompt(problem: str) -> str:
        """
        Factory method for database analysis ReAct prompts.

        Args:
            problem: Database problem to solve

        Returns:
            Database-specific ReAct prompt
        """
        actions = [
            "EXPLAIN PLAN: Analyze query execution plan",
            "CHECK STATS: View table statistics",
            "LIST INDEXES: Show current indexes",
            "ANALYZE TABLE: Update table statistics",
            "SHOW LOCKS: Check for blocking locks",
            "VIEW CONNECTIONS: Show active connections"
        ]

        return ReActPrompting().create_react_prompt(
            task=problem,
            available_actions=actions,
            context="Production database with performance issues"
        )


class AutomaticReasoningAndToolUse:
    """
    Automatic Reasoning and Tool-use: Autonomous selection and use of tools.

    Usage: Complex tasks requiring calculations, data access, or verification.
    """

    def __init__(self):
        """Initialize tool-use system."""
        self.available_tools: Dict[str, Tool] = {}
        self.execution_log: List[Dict] = []

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        executor: Callable
    ):
        """
        Register a tool for use.

        Args:
            name: Tool name
            description: What the tool does
            parameters: Parameter specifications
            executor: Function that executes the tool
        """
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            executor=executor
        )
        self.available_tools[name] = tool

    def create_tool_use_prompt(
        self,
        task: str,
        reasoning_context: Optional[str] = None
    ) -> str:
        """
        Create prompt with tool descriptions.

        Args:
            task: Task to accomplish
            reasoning_context: Optional reasoning context

        Returns:
            Tool-use prompt
        """
        prompt_parts = []

        prompt_parts.append("TASK WITH TOOL ACCESS\n")

        if reasoning_context:
            prompt_parts.append(f"CONTEXT:\n{reasoning_context}\n")

        prompt_parts.append(f"TASK:\n{task}\n")

        prompt_parts.append("AVAILABLE TOOLS:\n")
        for name, tool in self.available_tools.items():
            prompt_parts.append(f"Tool: {name}")
            prompt_parts.append(f"  Description: {tool.description}")
            prompt_parts.append(f"  Parameters: {json.dumps(tool.parameters, indent=4)}")
            prompt_parts.append("")

        prompt_parts.append("INSTRUCTIONS:")
        prompt_parts.append("1. Analyze which tools are needed")
        prompt_parts.append("2. Plan the sequence of tool uses")
        prompt_parts.append("3. For each tool use, specify:")
        prompt_parts.append("   - Tool name")
        prompt_parts.append("   - Parameters with values")
        prompt_parts.append("   - Expected result")
        prompt_parts.append("4. Integrate results into final answer")

        prompt_parts.append("\nFORMAT:")
        prompt_parts.append("Step 1: [Reasoning about what tool to use]")
        prompt_parts.append("Tool Call: tool_name(param1=value1, param2=value2)")
        prompt_parts.append("Expected: [What you expect to get]")

        return "\n".join(prompt_parts)

    @staticmethod
    def create_analysis_tools() -> 'AutomaticReasoningAndToolUse':
        """
        Factory method with common analysis tools.

        Returns:
            Instance with analysis tools registered
        """
        system = AutomaticReasoningAndToolUse()

        # SQL EXPLAIN tool
        system.register_tool(
            name="sql_explain",
            description="Analyze SQL query execution plan",
            parameters={
                "query": "string - SQL query to analyze",
                "database": "string - target database"
            },
            executor=lambda **kwargs: f"EXPLAIN output for {kwargs.get('query', 'N/A')}"
        )

        # Performance calculator
        system.register_tool(
            name="calculate_cost",
            description="Calculate estimated performance cost",
            parameters={
                "operation": "string - operation type",
                "data_size": "int - amount of data",
                "complexity": "string - algorithm complexity (O notation)"
            },
            executor=lambda **kwargs: f"Estimated cost: {kwargs.get('complexity', 'N/A')}"
        )

        # Metadata retriever
        system.register_tool(
            name="get_metadata",
            description="Retrieve table or index metadata",
            parameters={
                "object_name": "string - table or index name",
                "metadata_type": "string - type of metadata (stats, structure, etc.)"
            },
            executor=lambda **kwargs: f"Metadata for {kwargs.get('object_name', 'N/A')}"
        )

        return system


def main():
    """Example usage of knowledge techniques."""
    print("Knowledge and Context Techniques - Examples\n")
    print("=" * 70)

    # Example 1: Generated Knowledge
    print("\n[Example 1] Generated Knowledge Prompting\n")

    gk = GeneratedKnowledgePrompting()
    gen_prompt = gk.create_knowledge_generation_prompt(
        domain="REST API Design",
        specific_topics=[
            "HTTP methods and their semantics",
            "Status code selection",
            "URL structure best practices",
            "Error response formatting"
        ],
        knowledge_depth="comprehensive"
    )

    print(gen_prompt[:400] + "...\n")

    # Example 2: RAG
    print("=" * 70)
    print("\n[Example 2] Retrieval-Augmented Generation\n")

    rag = RetrievalAugmentedGeneration()

    # Mock retrieved documents
    docs = [
        {
            "source": "Django Documentation v4.2",
            "relevance_score": 0.95,
            "content": "Django ORM provides QuerySet.select_related() for SQL JOIN optimization..."
        },
        {
            "source": "Performance Best Practices",
            "relevance_score": 0.87,
            "content": "Use prefetch_related() for many-to-many and reverse foreign key relations..."
        }
    ]

    prompt = rag.create_prompt_with_retrieval(
        query="Django ORM performance optimization",
        retrieved_documents=docs,
        task="Optimize this Django queryset: User.objects.filter(is_active=True).all()",
        max_docs=5
    )

    print(prompt[:500] + "...\n")

    # Example 3: ReAct
    print("=" * 70)
    print("\n[Example 3] ReAct Prompting\n")

    react_prompt = ReActPrompting.create_database_react_prompt(
        "Query taking 3+ seconds to execute on production database"
    )

    print(react_prompt[:500] + "...\n")

    # Example 4: Automatic Tool Use
    print("=" * 70)
    print("\n[Example 4] Automatic Reasoning and Tool Use\n")

    tool_system = AutomaticReasoningAndToolUse.create_analysis_tools()
    print(f"Registered {len(tool_system.available_tools)} tools:")
    for name in tool_system.available_tools:
        print(f"  - {name}")
    print()

    prompt = tool_system.create_tool_use_prompt(
        task="Optimize this SQL query for a table with 1M rows",
        reasoning_context="E-commerce database, peak load: 1000 queries/sec"
    )

    print(prompt[:500] + "...\n")

    print("=" * 70)


if __name__ == "__main__":
    main()
