"""Compatibility layer for SDLC agent base classes.

This module exposes the same public API expected by legacy imports that
referenced :mod:`scripts.ai.sdlc.sdlc_base`.  The concrete implementation
resides in :mod:`scripts.ai.sdlc.base_agent`, which in turn leverages the
shared agent abstractions defined under :mod:`scripts.ai.shared`.
"""

from .base_agent import SDLCAgent, SDLCPipeline, SDLCPhaseResult

__all__ = ["SDLCAgent", "SDLCPipeline", "SDLCPhaseResult"]
