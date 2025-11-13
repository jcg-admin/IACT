# Analysis Report: procedimiento_qa.md

**Domain**: Governance
**Overall Score**: 51.5/100
**Analysis Time**: 0.92s

## Scores

| Component | Score |
|-----------|-------|
| Structure | 55.0/100 |
| Quality | 63.3/100 |
| Constitution | 50.0/100 |
| Traceability | 25.0/100 |
| Links | 50.0/100 |

## Issues

- [CRITICAL] Possible password exposure detected (Principle 7)
- [HIGH] Missing H1 title
- [HIGH] Broken internal link: ../qa/estrategia_qa.md
- [LOW] 13 code blocks missing language identifier
- [LOW] Possibly malformed tables detected
- [MEDIUM] Invalid heading hierarchy
- [MEDIUM] No issue links found
- [MEDIUM] Broken external link: https://docs.pytest.org/
- [MEDIUM] Broken external link: https://docs.djangoproject.com/en/stable/topics/testing/
- [MEDIUM] Broken external link: https://martinfowler.com/articles/practical-test-pyramid.html

## Recommendations

- Add single H1 title at document top
- Ensure headings follow H1→H2→H3 order
- Add language: ```python, ```bash, etc.
- Ensure tables have proper | separators
- Remove password, use environment variables
- Add links to related issues (FEATURE-*, BUG-*, etc.)
- Fix path or create missing file
- Update or remove broken link
- Update or remove broken link
- Update or remove broken link
