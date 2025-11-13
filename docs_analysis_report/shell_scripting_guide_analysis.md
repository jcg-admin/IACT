# Analysis Report: shell_scripting_guide.md

**Domain**: Governance
**Overall Score**: 52.9/100
**Analysis Time**: 0.01s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 55.0/100 |
| Quality | 55.0/100 |
| Constitution | 50.0/100 |
| Traceability | 25.0/100 |
| Links | 89.5/100 |

## Issues

- [CRITICAL] Possible password exposure detected (Principle 7)
- [CRITICAL] Possible api_key exposure detected (Principle 7)
- [HIGH] Missing H1 title
- [HIGH] Broken internal link: readme.md
- [HIGH] Broken internal link: ../../scripts/requisitos/README.md
- [LOW] 22 code blocks missing language identifier
- [LOW] Possibly malformed tables detected
- [MEDIUM] Invalid heading hierarchy
- [MEDIUM] No issue links found

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Ensure tables have proper | separators
- Remove password, use environment variables
- Remove api_key, use environment variables
- Add links to related issues (FEATURE-*, BUG-*, etc.)
- Fix path or create missing file
- Fix path or create missing file
