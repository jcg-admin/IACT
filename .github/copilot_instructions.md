# Copilot Instructions for IACT Project

## Repository Overview

This is the IACT (Intelligent Autonomous Coding Toolkit) project repository. Currently in its initial stages, this repository serves as the foundation for building intelligent coding automation tools and workflows.

## Big Picture Architecture

### Current State
The repository is in its early stages with a minimal structure:
- **Repository Root**: Contains core documentation and configuration files
- **Documentation**: README.md provides the project overview

### Architectural Vision
As this project evolves, it is expected to follow these architectural principles:

1. **Modularity**: Components should be loosely coupled and highly cohesive
2. **Extensibility**: New features and tools should be easy to add without modifying existing code
3. **Automation-First**: All repetitive tasks should be automated where possible
4. **Documentation-Driven**: Changes should be documented before or alongside implementation

## Project Structure

```
IACT---project/
├── .github/                    # GitHub-specific configurations
│   ├── copilot_instructions.md # This file - AI agent guidance
│   ├── workflows/              # (Future) CI/CD workflows
│   └── CODEOWNERS             # (Future) Code ownership definitions
├── README.md                   # Project documentation
└── (Additional directories as project grows)
```

### Expected Future Structure
As the project develops, expect these directories:

- **src/** or **lib/**: Core application/library code
- **tests/** or **test/**: Test suites
- **docs/**: Detailed documentation
- **scripts/**: Utility and automation scripts
- **config/**: Configuration files
- **examples/**: Usage examples and demonstrations

## Development Guidelines

### Code Organization
- Keep related functionality together
- Use clear, descriptive naming conventions
- Maintain separation of concerns
- Document complex logic with comments
- Follow the DRY (Don't Repeat Yourself) principle

### File Naming Conventions
- Use kebab-case for file names (e.g., `my-component.js`)
- Use descriptive names that reflect the file's purpose
- Group related files in appropriate directories

### Documentation Standards
- Update README.md when adding new features or changing architecture
- Add inline comments for complex algorithms or non-obvious code
- Document all public APIs and interfaces
- Keep documentation in sync with code changes

### Git Workflow
- Use descriptive commit messages following conventional commits format
- Create feature branches for new work
- Keep commits atomic and focused
- Write meaningful PR descriptions

### Testing Philosophy
- Write tests for all new functionality
- Aim for high test coverage, especially for critical paths
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern in tests

## Key Patterns and Conventions

### When Adding New Features
1. **Plan First**: Understand the requirement fully before coding
2. **Start Small**: Begin with a minimal implementation
3. **Test Early**: Write tests as you develop
4. **Document**: Add relevant documentation
5. **Review**: Self-review your changes before submitting

### When Refactoring
1. **Understand Existing Code**: Read and comprehend before changing
2. **Preserve Behavior**: Ensure refactoring doesn't change functionality
3. **Test Coverage**: Ensure tests exist before refactoring
4. **Incremental Changes**: Make small, reviewable changes
5. **Verify**: Run all tests after refactoring

### When Fixing Bugs
1. **Reproduce**: Understand and reproduce the bug first
2. **Write Test**: Create a failing test that captures the bug
3. **Fix**: Implement the minimal fix
4. **Verify**: Ensure the test passes and no regressions occur
5. **Document**: Add comments explaining the fix if non-obvious

## AI Agent Best Practices

### Understanding the Codebase
- Always start by exploring the repository structure
- Read README.md and any existing documentation first
- Check for configuration files (package.json, requirements.txt, etc.)
- Look for existing patterns in the codebase before implementing new features
- Review recent commit history to understand development patterns

### Making Changes
- **Minimal Changes**: Make the smallest possible changes to achieve the goal
- **Consistency**: Follow existing code style and patterns
- **Testing**: Run existing tests before and after changes
- **Documentation**: Update docs when changing functionality
- **Verification**: Manually verify changes work as expected

### Problem-Solving Approach
1. **Analyze**: Understand the problem and its context
2. **Research**: Check existing code for similar solutions
3. **Plan**: Outline the approach before implementing
4. **Implement**: Write clean, well-structured code
5. **Test**: Verify the solution works correctly
6. **Document**: Explain what was done and why

### Common Pitfalls to Avoid
- Don't assume the project structure without exploring first
- Don't add dependencies without checking existing ones
- Don't remove or modify code you don't understand
- Don't skip testing after making changes
- Don't leave debug code or commented-out code in commits
- Don't make unrelated changes in the same commit

### Security Considerations
- Never commit secrets, API keys, or credentials
- Validate all inputs
- Follow security best practices for the technology stack
- Keep dependencies up to date
- Review security implications of changes

## Technology Stack

### Current
- Git for version control
- GitHub for repository hosting and collaboration
- Markdown for documentation

### Future Considerations
When adding new technologies:
- Choose well-maintained, popular libraries
- Consider the learning curve for contributors
- Ensure compatibility with existing stack
- Document setup and usage clearly
- Add to this instructions file

## Communication and Collaboration

### For AI Agents
- Be explicit about what you're doing and why
- Report progress frequently
- Ask for clarification when requirements are unclear
- Provide context in commit messages and PR descriptions
- Highlight any assumptions made during implementation

### Code Review Expectations
- Explain the reasoning behind your approach
- Highlight any trade-offs or limitations
- Call out areas where you need feedback
- Respond to review comments constructively
- Be open to alternative solutions

## Maintenance and Evolution

### As the Project Grows
This instructions file should be updated when:
- New architectural patterns are introduced
- Technology stack changes
- New conventions are established
- Common issues are identified
- Best practices evolve

### Keeping This Document Useful
- Keep it concise but comprehensive
- Focus on what's unique to this project
- Remove outdated information promptly
- Organize information logically
- Use examples where helpful

## Quick Reference

### First Time Setup
```bash
# Clone the repository
git clone https://github.com/2-Coatl/IACT---project.git
cd IACT---project

# (Future) Install dependencies
# npm install  or  pip install -r requirements.txt  or similar
```

### Common Commands
```bash
# Check repository status
git status

# Create a new branch
git checkout -b feature/my-feature

# (Future) Run tests
# npm test  or  pytest  or similar

# (Future) Build the project
# npm run build  or  make  or similar
```

## Resources

### Internal Documentation
- README.md - Project overview and getting started
- (Future) Architecture diagrams and detailed design docs

### External Resources
- GitHub Docs: https://docs.github.com
- Git Best Practices: https://git-scm.com/doc
- Conventional Commits: https://www.conventionalcommits.org

---

**Last Updated**: 2025-10-27
**Maintainers**: IACT Project Team

This document is a living guide - update it as the project evolves to keep it relevant and useful for all contributors, human and AI alike.
