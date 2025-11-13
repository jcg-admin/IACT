"""Minimal Hamilton-like driver for executing declarative dataflows.

The real Hamilton framework provides a rich micro-orchestration engine. For the
purposes of the repository we build a tiny subset that resolves dependencies by
function name and executes only the nodes required to produce requested targets.
"""

from __future__ import annotations

import inspect
from types import ModuleType
from typing import Any, Dict, Iterable, Mapping, Sequence


class MissingDependencyError(RuntimeError):
    """Raised when a dependency required by a node is not available."""


class HamiltonDriver:
    """Execute declarative functions registered from one or more modules.

    Functions are registered by name and resolved lazily. Inputs provided via
    ``execute`` act as seed values, mirroring Hamilton's configuration
    dictionary. Each execution resets the cache and produces a log of executed
    nodes so tests can assert on evaluation order.
    """

    def __init__(self, modules: Iterable[ModuleType]):
        self._functions: Dict[str, Any] = {}
        self.execution_log: list[str] = []
        for module in modules:
            self._register_module(module)

    def _register_module(self, module: ModuleType) -> None:
        for name, candidate in vars(module).items():
            if inspect.isfunction(candidate):
                self._functions[name] = candidate

    def execute(self, targets: Sequence[str], inputs: Mapping[str, Any]) -> Dict[str, Any]:
        cache: Dict[str, Any] = {}
        context: Dict[str, Any] = dict(inputs)
        self.execution_log = []

        def resolve(name: str) -> Any:
            if name in cache:
                return cache[name]
            if name in context:
                return context[name]

            func = self._functions.get(name)
            if func is None:
                raise MissingDependencyError(f"No data or function available for '{name}'")

            signature = inspect.signature(func)
            kwargs: Dict[str, Any] = {}
            for parameter in signature.parameters.values():
                if parameter.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                    raise MissingDependencyError(
                        f"Unsupported parameter kind for '{func.__name__}': {parameter.kind}"
                    )
                dependency_name = parameter.name
                try:
                    kwargs[dependency_name] = resolve(dependency_name)
                except MissingDependencyError as exc:  # pragma: no cover - rephrase message
                    raise MissingDependencyError(
                        f"Function '{func.__name__}' requires missing dependency '{dependency_name}'"
                    ) from exc

            value = func(**kwargs)
            cache[name] = value
            context[name] = value
            self.execution_log.append(name)
            return value

        results = {target: resolve(target) for target in targets}
        return results


__all__ = ["HamiltonDriver", "MissingDependencyError"]
