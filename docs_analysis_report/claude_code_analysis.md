# Analysis Report: claude_code.md

**Domain**: Other
**Overall Score**: 44.0/100
**Analysis Time**: 1.25s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 55.0/100 |
| Quality | 55.0/100 |
| Constitution | 50.0/100 |
| Traceability | 25.0/100 |
| Links | 0.0/100 |

## Issues

- [CRITICAL] Possible token exposure detected (Principle 7)
- [HIGH] Missing H1 title
- [HIGH] Broken internal link: ../contenedores_devcontainer.md
- [LOW] 34 code blocks missing language identifier
- [LOW] Possibly malformed tables detected
- [MEDIUM] Invalid heading hierarchy
- [MEDIUM] No issue links found
- [MEDIUM] Broken external link: https://docs.claude.com/en/docs/claude-code
- [MEDIUM] Broken external link: https://cli.github.com/manual/
- [MEDIUM] Broken external link: https://git-scm.com/doc

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Ensure tables have proper | separators
- Remove token, use environment variables
- Add links to related issues (FEATURE-*, BUG-*, etc.)
- Update or remove broken link
- Update or remove broken link
- Fix path or create missing file
- Update or remove broken link
