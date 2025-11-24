# Contributing to AI Agents Framework

Thank you for your interest in contributing to the AI Agents Framework! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal or political attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of AI agents, planning systems, or protocol design

### Find an Issue

1. Browse the [issue tracker](https://github.com/2-Coatl/IACT---project/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to let others know you're working on it
4. Wait for maintainer approval before starting significant work

### Types of Contributions

We welcome:
- **Bug fixes**: Fix issues reported in the issue tracker
- **New features**: Implement new capabilities (discuss first in an issue)
- **Documentation**: Improve or expand documentation
- **Tests**: Add or improve test coverage
- **Examples**: Add new usage examples
- **Performance**: Optimize existing code
- **Refactoring**: Improve code quality

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/IACT---project.git
cd IACT---project
```

### 2. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip install pydantic pytest pytest-cov

# Install development dependencies
pip install ruff mypy bandit pre-commit
```

### 4. Set Up Python Path

```bash
# Add project root to PYTHONPATH
export PYTHONPATH=/path/to/IACT---project:$PYTHONPATH

# Or add to your shell profile (~/.bashrc, ~/.zshrc)
echo 'export PYTHONPATH=/path/to/IACT---project:$PYTHONPATH' >> ~/.bashrc
```

### 5. Verify Setup

```bash
# Run tests to ensure everything works
PYTHONPATH=/path/to/IACT---project python3 -m pytest scripts/coding/tests/test_agents/ -v

# Should see: 140 passed in ~0.5s
```

## How to Contribute

### Working on an Issue

1. **Comment on the issue** to claim it
2. **Wait for approval** from a maintainer
3. **Create a branch** for your work
4. **Make your changes** following coding standards
5. **Write tests** for new functionality
6. **Update documentation** as needed
7. **Run tests** to ensure everything passes
8. **Submit a pull request**

### Reporting Bugs

When reporting bugs, include:

```markdown
**Description**: Clear description of the bug

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- Python version: 3.11
- OS: Ubuntu 22.04
- Framework version: 1.0.0

**Additional Context**: Any other relevant information
```

### Suggesting Features

When suggesting features, include:

```markdown
**Feature Description**: Clear description of the feature

**Use Case**: Why is this needed?

**Proposed Implementation**: How could this work?

**Alternatives Considered**: Other approaches you've thought about

**Additional Context**: Any other relevant information
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Absolute imports preferred
- **Type hints**: Required for all public methods
- **Docstrings**: Required for all public classes and methods

### Code Formatting

We use **Ruff** for linting and formatting:

```bash
# Check code style
ruff check scripts/coding/ai/agents/

# Format code
ruff format scripts/coding/ai/agents/
```

### Type Checking

We use **MyPy** for type checking:

```bash
# Run type checker
mypy scripts/coding/ai/agents/ --show-error-codes --pretty
```

### Security Scanning

We use **Bandit** for security checks:

```bash
# Run security scanner
bandit -r scripts/coding/ai/agents/
```

### Example: Well-Formatted Code

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MyClass(BaseModel):
    """
    Brief description of the class.

    Attributes:
        field_name: Description of field
        another_field: Description of another field
    """

    field_name: str
    another_field: int = Field(default=0, ge=0)

    def my_method(
        self,
        param1: str,
        param2: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Brief description of method.

        Args:
            param1: Description of param1
            param2: Description of param2 (optional)

        Returns:
            Dictionary containing results

        Raises:
            ValueError: If param1 is empty
        """
        if not param1:
            raise ValueError("param1 cannot be empty")

        return {"param1": param1, "param2": param2 or 0}
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `GoalParser`, `MCPServer`)
- **Functions/Methods**: `snake_case` (e.g., `parse_goal`, `invoke_tool`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Private methods**: `_snake_case` (e.g., `_internal_method`)
- **Module names**: `snake_case` (e.g., `goal_parser.py`, `mcp.py`)

### Import Organization

```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Third-party imports
from pydantic import BaseModel, Field

# Local imports
from scripts.coding.ai.agents.planning.models import Goal, Plan
from scripts.coding.ai.agents.security.threat_detector import ThreatDetector
```

## Testing Guidelines

### Test Requirements

- **All new code must have tests**
- **Minimum 90% coverage** for new modules
- **Tests must be independent** (no shared state)
- **Tests must be fast** (<1s for unit tests)
- **Use descriptive test names**

### Test Structure

```python
def test_descriptive_name_of_what_is_being_tested():
    """
    Test description explaining what this verifies.
    """
    # Arrange: Set up test data
    parser = GoalParser()
    user_input = "Book a flight to Paris"

    # Act: Execute the code being tested
    result = parser.parse(user_input)

    # Assert: Verify the results
    assert result.goal_type == GoalType.SIMPLE
    assert result.description == user_input
    assert len(result.constraints) == 0
```

### Running Tests

```bash
# Run all tests
PYTHONPATH=/path/to/IACT---project python3 -m pytest scripts/coding/tests/test_agents/ -v

# Run specific module tests
python3 -m pytest scripts/coding/tests/test_agents/test_planning/ -v

# Run with coverage
python3 -m pytest scripts/coding/tests/test_agents/ --cov=scripts/coding/ai/agents --cov-report=term

# Run specific test
python3 -m pytest scripts/coding/tests/test_agents/test_planning/test_task_decomposition.py::test_parse_simple_goal -v
```

### Test Categories

**Unit Tests**: Test individual functions/methods
```python
def test_parse_simple_goal():
    parser = GoalParser()
    goal = parser.parse("Simple goal")
    assert goal.goal_type == GoalType.SIMPLE
```

**Integration Tests**: Test multiple components together
```python
def test_complete_planning_workflow():
    parser = GoalParser()
    decomposer = TaskDecomposer()

    goal = parser.parse("Complex goal")
    plan = decomposer.decompose(goal)

    assert plan.goal_id == goal.goal_id
    assert len(plan.subtasks) > 0
```

**Performance Tests**: Verify performance requirements
```python
def test_parsing_performance():
    parser = GoalParser()
    start = time.time()

    for _ in range(100):
        parser.parse("Test goal")

    duration = (time.time() - start) / 100 * 1000
    assert duration < 10  # <10ms requirement
```

### Test File Organization

```
scripts/coding/tests/test_agents/
├── test_planning/
│   ├── __init__.py
│   ├── test_task_decomposition.py
│   └── test_iterative_planning.py
├── test_protocols/
│   ├── __init__.py
│   ├── test_mcp.py
│   ├── test_a2a.py
│   └── test_nlweb.py
└── test_security/
    ├── __init__.py
    └── test_threat_detector.py
```

## Documentation

### Documentation Requirements

- **All public APIs must be documented**
- **Examples required for complex features**
- **Update README.md** when adding features
- **Update API_REFERENCE.md** for new APIs
- **Add to EXAMPLES.md** for new patterns

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief one-line description.

    More detailed description if needed. Explain what the function
    does, any important behavior, and edge cases.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is negative

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        True
    """
    pass
```

### Documentation Files to Update

1. **README.md**: Main documentation
   - Update "Quick Start" if adding new entry points
   - Update "Module Documentation" for new modules
   - Update "Testing" section for new test requirements

2. **API_REFERENCE.md**: API documentation
   - Add new classes, methods, and parameters
   - Include type signatures and examples

3. **EXAMPLES.md**: Usage examples
   - Add runnable examples for new features
   - Show common use cases

4. **INTEGRATION.md**: Integration patterns
   - Add integration examples for new protocols
   - Show deployment patterns

5. **CHANGELOG.md**: Version history
   - Add entries under [Unreleased]
   - Follow Keep a Changelog format

## Pull Request Process

### Before Submitting

1. **Run all tests**
   ```bash
   PYTHONPATH=/path/to/IACT---project python3 -m pytest scripts/coding/tests/test_agents/ -v
   ```

2. **Check code style**
   ```bash
   ruff check scripts/coding/ai/agents/
   ruff format --check scripts/coding/ai/agents/
   ```

3. **Run type checker**
   ```bash
   mypy scripts/coding/ai/agents/ --show-error-codes
   ```

4. **Check security**
   ```bash
   bandit -r scripts/coding/ai/agents/
   ```

5. **Verify coverage**
   ```bash
   python3 -m pytest scripts/coding/tests/test_agents/ --cov=scripts/coding/ai/agents --cov-report=term
   ```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Related Issue
Fixes #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Coverage is above 90%

## Documentation
- [ ] Updated README.md
- [ ] Updated API_REFERENCE.md
- [ ] Updated EXAMPLES.md
- [ ] Updated CHANGELOG.md

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Documentation updated
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **At least one maintainer** must review
3. **All conversations** must be resolved
4. **No merge conflicts**
5. **Squash commits** before merging (if needed)

### After PR is Merged

1. **Delete your branch** (if no longer needed)
2. **Update your fork** to sync with main repository
3. **Close related issues** (if applicable)

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update CHANGELOG.md**
   - Move items from [Unreleased] to new version
   - Add release date

2. **Update version numbers**
   - In relevant files (if applicable)

3. **Run full test suite**
   - All 140 tests must pass
   - Coverage must be >90%

4. **Create release branch**
   ```bash
   git checkout -b release/v1.1.0
   ```

5. **Tag the release**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

6. **Create GitHub release**
   - Use CHANGELOG.md content for release notes
   - Attach any relevant artifacts

## Getting Help

- **Documentation**: Check [README.md](README.md), [API_REFERENCE.md](API_REFERENCE.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Issues**: Search existing [issues](https://github.com/2-Coatl/IACT---project/issues)
- **Discussions**: Start a [discussion](https://github.com/2-Coatl/IACT---project/discussions)

## Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Mentioned in release notes
- Added to a CONTRIBUTORS file (if significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to the AI Agents Framework!** 🎉

Your contributions help make this project better for everyone.
