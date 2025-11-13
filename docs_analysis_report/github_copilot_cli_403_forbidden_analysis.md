# Analysis Report: github_copilot_cli_403_forbidden.md

**Domain**: Infrastructure
**Overall Score**: 51.5/100
**Analysis Time**: 0.17s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 47.5/100 |
| Quality | 55.0/100 |
| Constitution | 50.0/100 |
| Traceability | 25.0/100 |
| Links | 94.1/100 |

## Issues

- [CRITICAL] Possible token exposure detected (Principle 7)
- [HIGH] Missing H1 title
- [LOW] 29 code blocks missing language identifier
- [LOW] Possibly malformed tables detected
- [MEDIUM] Invalid heading hierarchy
- [MEDIUM] No issue links found
- [MEDIUM] Broken external link: https://docs.github.com/en/copilot/managing-copilot/managing-policies-and-features-for-copilot-in-your-organization

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Ensure tables have proper | separators
- Remove token, use environment variables
- Add links to related issues (FEATURE-*, BUG-*, etc.)
- Update or remove broken link
