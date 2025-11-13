# Analysis Report: CLI-SDLC-AGENTS.md

**Domain**: Backend
**Overall Score**: 56.0/100
**Analysis Time**: 0.00s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 47.5/100 |
| Quality | 67.8/100 |
| Constitution | 50.0/100 |
| Traceability | 25.0/100 |
| Links | 100.0/100 |

## Issues

- [CRITICAL] Possible api_key exposure detected (Principle 7)
- [HIGH] Missing H1 title
- [LOW] 33 code blocks missing language identifier
- [MEDIUM] Invalid heading hierarchy
- [MEDIUM] No issue links found

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Remove api_key, use environment variables
- Add links to related issues (FEATURE-*, BUG-*, etc.)
