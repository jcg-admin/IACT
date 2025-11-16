---
title: Changelog
date: 2025-11-13
domain: general
status: active
---

# Changelog

## [2025-11-12] - Documentación Tareas Críticas Sprint 1

### Agregado

- Documentación completa para TASK-001: Ejecutar Suite Completa de Tests (docs/qa/)
- Documentación completa para TASK-002: Validar Restricciones Críticas (docs/qa/)
- Documentación completa para TASK-003: Verificar SESSION_ENGINE en Settings (docs/qa/)
- Documentación completa para TASK-004: Tests de Auditoría Inmutable (docs/qa/)
- Documentación completa para TASK-005: Sistema de Metrics Interno MySQL (docs/arquitectura/)
- Documentación completa para TASK-006: Validar Estructura de Docs (docs/proyecto/)
- Agente de documentación de tareas siguiendo patrones de scripts/coding/ai/agents/

### Mejorado

- Cobertura de documentación de tareas del PLAN: 65.7% → 82.9%
- Total archivos TASK-*.md: 32 → 38
- 100% de tareas P0 críticas del Sprint 1 documentadas

### Estadísticas

- 6 archivos nuevos
- 414 líneas de documentación agregadas
- 15 Story Points de Sprint 1 documentados
- Frontmatter YAML estandarizado en todos los archivos TASK


Todos los cambios notables de este repositorio se documentarán en este archivo siguiendo el formato de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y el versionado semántico cuando aplique.

## [Unreleased]

### Fixed
- `infrastructure/cpython/bootstrap.sh` repara automáticamente el toolchain cuando detecta que `gcc` o `make` faltan después de un `vagrant up`, evitando reprovisionamientos manuales.

## [2025-11-08]
### Added
- Se documentó en el README el flujo completo para generar, validar y consumir el artefacto de CPython producido por `infrastructure/cpython`.
- Se creó este changelog para centralizar el historial público de cambios del repositorio.

### Changed
- Se enlazó la documentación del builder y el changelog específico de infraestructura para mantener coherencia con el pipeline de devcontainer.
