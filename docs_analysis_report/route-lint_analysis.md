# Analysis Report: route-lint.md

**Domain**: Backend
**Overall Score**: 49.6/100
**Analysis Time**: 0.01s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 47.5/100 |
| Quality | 55.0/100 |
| Constitution | 50.0/100 |
| Traceability | 25.0/100 |
| Links | 75.0/100 |

## Issues

- [HIGH] Missing H1 title
- [HIGH] Found 1 emojis (Principle 2 violation)
- [HIGH] Broken internal link: ../../../arquitectura/ADR-012-sistema-permisos-sin-roles-jerarquicos.md
- [LOW] 26 code blocks missing language identifier
- [LOW] Possibly malformed tables detected
- [MEDIUM] Invalid heading hierarchy
- [MEDIUM] No issue links found

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Ensure tables have proper | separators
- Remove all emojis from documentation
- Add links to related issues (FEATURE-*, BUG-*, etc.)
- Fix path or create missing file
