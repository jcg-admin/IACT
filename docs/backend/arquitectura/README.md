# Arquitectura del Backend IACT

**Proposito**: Documentacion de arquitectura de software del backend Django
**Ultima actualizacion**: 2025-11-07

## Contenido

- Decisiones de Arquitectura (ADRs)
- Diagramas de arquitectura
- Patrones de diseño
- HLD y LLD por modulo
- Database schema y ERDs

## Principios IACT

1. Separacion de concerns
2. Testabilidad (>= 80% coverage)
3. Mantenibilidad
4. Escalabilidad horizontal
5. Seguridad (OWASP Top 10)

## Restricciones Criticas

- RNF-002: NO Redis (sesiones en MySQL)
- Multi-database: MySQL + PostgreSQL + Cassandra
- NO emojis/iconos en codigo

## Ownership

Maintainer: Arquitecto Senior
Review: Tech Lead + Arquitecto
