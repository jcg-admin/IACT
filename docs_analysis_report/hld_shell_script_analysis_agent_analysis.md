# Analysis Report: hld_shell_script_analysis_agent.md

**Domain**: AI Agent
**Overall Score**: 60.6/100
**Analysis Time**: 0.00s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 47.5/100 |
| Quality | 63.3/100 |
| Constitution | 50.0/100 |
| Traceability | 65.0/100 |
| Links | 100.0/100 |

## Issues

- [CRITICAL] Possible api_key exposure detected (Principle 7)
- [HIGH] Missing H1 title
- [LOW] 29 code blocks missing language identifier
- [LOW] Possibly malformed tables detected
- [MEDIUM] Invalid heading hierarchy

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Ensure tables have proper | separators
- Remove api_key, use environment variables
