# Changelog

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
