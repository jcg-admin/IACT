"""Hamilton-style micro-orchestration utilities used by the LLM example.

The real `hamilton` package published at https://github.com/apache/hamilton
exposes a :class:`Builder` that wires modules, configuration and result
adapters into a :class:`Driver`. The implementation below keeps the repository
self-contained (no third-party dependency) while mirroring the public surface
of the Apache project closely enough for educational purposes. Tests interact
with :class:`Builder`, :class:`Driver` and :class:`DictResult` exactly as they
would with the official library, making it straightforward to swap this shim
for the actual package when the environment allows installing extra
dependencies.
"""

from __future__ import annotations

import inspect
from importlib import import_module
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, Mapping, Sequence


def _vpn_modules() -> Iterable[str]:
    return (
        "infrastructure.workspace.hamilton_llm.dataflow",
        "infrastructure.workspace.vpn_proxy_agent.hamilton_nodes",
    )


async def execute_vpn_workflow(
    *,
    tunnel_manager,
    diagnostics,
    connectivity_tester,
    llm_client,
    idea: str,
    domain_data: Mapping[str, Any],
    edge_cases: Sequence[str],
    pricing_policy: Mapping[str, float],
    proxy_url: str | None = None,
    api_urls: Sequence[str] | None = None,
    timeout: float = 5.0,
) -> Mapping[str, Any]:
    statuses = await connectivity_tester(
        proxy_url=proxy_url,
        api_urls=list(api_urls or []),
        timeout=timeout,
    )
    tunnel_snapshot = await tunnel_manager.status()
    system_report = diagnostics.collect()

    builder = Builder().with_modules(*_vpn_modules()).with_adapters(DictResult())
    driver = builder.build()
    outputs = driver.execute(
        [
            "business_value",
            "cost_estimate",
            "connectivity_matrix",
            "tunnel_status",
            "system_health_summary",
        ],
        inputs={
            "idea": idea,
            "domain_data": dict(domain_data),
            "edge_cases": list(edge_cases),
            "llm_client": llm_client,
            "pricing_policy": dict(pricing_policy),
            "statuses": statuses,
            "status": tunnel_snapshot,
            "report": system_report,
        },
    )

    return outputs

AdapterCallable = Callable[[Mapping[str, Any]], Any]


class MissingDependencyError(RuntimeError):
    """Raised when a dependency required by a node is not available."""


class DictResult:
    """Adapter that mirrors ``hamilton.base.DictResult``.

    In Apache Hamilton an adapter converts the internal dictionary of computed
    values into the preferred representation (for example, a pandas DataFrame).
    Our example keeps everything as dictionaries, so the adapter is the
    identity. It remains configurable so that tests can validate adapter
    chaining.
    """

    def __call__(self, results: Mapping[str, Any]) -> Mapping[str, Any]:
        return dict(results)


class _ExecutionEngine:
    """Internal dependency resolver supporting the public :class:`Driver`."""

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

        return {target: resolve(target) for target in targets}


class Driver:
    """High-level API compatible with :mod:`hamilton.driver`.

    Parameters configured through :class:`Builder` are preserved across
    executions. Runtime ``execute`` inputs override builder-level configuration
    so that tests can demonstrate the Hamilton concept of layering environments
    (defaults + overrides).
    """

    def __init__(
        self,
        modules: Iterable[ModuleType],
        adapters: Iterable[AdapterCallable] | None = None,
        config: Mapping[str, Any] | None = None,
    ) -> None:
        module_list = list(modules)
        if not module_list:
            raise ValueError("Driver requires at least one module with declarative functions")
        self._engine = _ExecutionEngine(module_list)
        self._adapters: list[AdapterCallable] = list(adapters or [DictResult()])
        self._config: Dict[str, Any] = dict(config or {})
        self.execution_log: list[str] = []

    def execute(
        self,
        targets: Sequence[str],
        inputs: Mapping[str, Any] | None = None,
    ) -> Any:
        runtime_inputs: Dict[str, Any] = dict(self._config)
        if inputs:
            runtime_inputs.update(inputs)

        results = self._engine.execute(targets, runtime_inputs)
        self.execution_log = list(self._engine.execution_log)

        adapted: Any = results
        for adapter in self._adapters:
            adapted = adapter(adapted)
        return adapted


class Builder:
    """Mirror of :class:`hamilton.driver.Builder` with a minimal feature set."""

    def __init__(self) -> None:
        self._modules: list[ModuleType] = []
        self._config: Dict[str, Any] = {}
        self._adapters: list[AdapterCallable] = []

    def with_modules(self, *modules: ModuleType | str) -> "Builder":
        for module in modules:
            if isinstance(module, str):
                module = import_module(module)
            if not isinstance(module, ModuleType):
                raise TypeError("Builder.with_modules expects module objects or import paths")
            self._modules.append(module)
        return self

    def with_config(self, config: Mapping[str, Any]) -> "Builder":
        self._config.update(dict(config))
        return self

    def with_adapters(self, *adapters: AdapterCallable) -> "Builder":
        self._adapters.extend(adapters)
        return self

    def build(self) -> Driver:
        if not self._modules:
            raise ValueError("Builder requires modules before building a Driver")
        return Driver(self._modules, adapters=self._adapters, config=self._config)


__all__ = ["Builder", "DictResult", "Driver", "MissingDependencyError", "execute_vpn_workflow"]
