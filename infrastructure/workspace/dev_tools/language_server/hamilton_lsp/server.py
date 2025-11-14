"""Hamilton language-server primitives without external dependencies."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Sequence

__all__ = [
    "CompletionItem",
    "CompletionItemKind",
    "CompletionItemLabelDetails",
    "CompletionList",
    "CompletionParams",
    "DidChangeTextDocumentParams",
    "DidOpenTextDocumentParams",
    "DocumentSymbolParams",
    "HamiltonLanguageServer",
    "Location",
    "Position",
    "Range",
    "SymbolInformation",
    "SymbolKind",
    "TextDocumentIdentifier",
    "TextDocumentItem",
    "VersionedTextDocumentIdentifier",
    "register_server_features",
]

TEXT_DOCUMENT_DID_CHANGE = "textDocument/didChange"
TEXT_DOCUMENT_DID_OPEN = "textDocument/didOpen"
TEXT_DOCUMENT_COMPLETION = "textDocument/completion"
TEXT_DOCUMENT_DOCUMENT_SYMBOL = "textDocument/documentSymbol"


@dataclass
class Position:
    line: int
    character: int


@dataclass
class Range:
    start: Position
    end: Position


@dataclass
class Location:
    uri: str
    range: Range


class CompletionItemKind:
    """Subset of LSP completion item kinds."""

    Function = 3


@dataclass
class CompletionItemLabelDetails:
    detail: str
    description: str


@dataclass
class CompletionItem:
    label: str
    label_details: CompletionItemLabelDetails
    kind: int
    documentation: str
    insert_text: str


@dataclass
class CompletionList:
    items: List[CompletionItem]
    is_incomplete: bool = False


class SymbolKind:
    """Subset of LSP symbol kinds."""

    Function = 12
    Field = 5


@dataclass
class SymbolInformation:
    name: str
    kind: int
    location: Location
    container_name: str


@dataclass
class TextDocumentItem:
    uri: str
    text: str
    version: int = 0


@dataclass
class VersionedTextDocumentIdentifier:
    uri: str
    version: int


@dataclass
class TextDocumentIdentifier:
    uri: str


@dataclass
class DidOpenTextDocumentParams:
    text_document: TextDocumentItem


@dataclass
class DidChangeTextDocumentParams:
    text_document: VersionedTextDocumentIdentifier
    content_changes: Sequence[str] | None = None


@dataclass
class DocumentSymbolParams:
    text_document: TextDocumentIdentifier


@dataclass
class CompletionParams:
    text_document: TextDocumentIdentifier


@dataclass
class Document:
    uri: str
    text: str
    version: int = 0

    @property
    def source(self) -> str:
        return self.text


class Workspace:
    """Minimal document registry for the in-repo language server."""

    def __init__(self) -> None:
        self._documents: Dict[str, Document] = {}

    def put_document(self, item: TextDocumentItem) -> None:
        self._documents[item.uri] = Document(uri=item.uri, text=item.text, version=item.version)

    def update_document(self, identifier: VersionedTextDocumentIdentifier, new_text: str | None) -> None:
        document = self._documents.get(identifier.uri)
        if document is None:
            raise KeyError(f"Document {identifier.uri} is not registered")
        if new_text is not None:
            document.text = new_text
        document.version = identifier.version

    def get_document(self, uri: str) -> Document:
        document = self._documents.get(uri)
        if document is None:
            raise KeyError(f"Document {uri} is not registered")
        return document


@dataclass
class DataflowNode:
    name: str
    type: str
    documentation: str
    dependencies: Sequence[str]
    is_external_input: bool
    originating_functions: Sequence[Callable[..., Any]] = field(default_factory=list)


class FunctionGraph:
    """Simplified container mirroring :class:`hamilton.graph.FunctionGraph`."""

    def __init__(self, nodes: Mapping[str, DataflowNode]):
        self._nodes: Dict[str, DataflowNode] = dict(nodes)

    @classmethod
    def empty(cls) -> "FunctionGraph":
        return cls({})

    @classmethod
    def from_modules(
        cls, modules: ModuleType | Iterable[ModuleType], config: Mapping[str, Any] | None = None
    ) -> "FunctionGraph":
        modules_iterable: Iterable[ModuleType]
        if isinstance(modules, ModuleType):
            modules_iterable = [modules]
        else:
            modules_iterable = list(modules)

        graph_nodes: Dict[str, DataflowNode] = {}
        external_nodes: Dict[str, DataflowNode] = {}
        for module in modules_iterable:
            module_nodes, module_externals = _build_nodes_from_module(module)
            graph_nodes.update(module_nodes)
            for name, ext in module_externals.items():
                if name not in graph_nodes and name not in external_nodes:
                    external_nodes[name] = ext

        graph_nodes.update(external_nodes)
        return cls(graph_nodes)

    def get_nodes(self) -> List[DataflowNode]:
        return list(self._nodes.values())


class HamiltonGraph:
    """Very small stand-in for :class:`hamilton.graph_types.HamiltonGraph`."""

    def __init__(self, nodes: Sequence[DataflowNode]):
        self.nodes = list(nodes)
        self.version = self._compute_version()

    @classmethod
    def from_graph(cls, graph: FunctionGraph) -> "HamiltonGraph":
        return cls(graph.get_nodes())

    def _compute_version(self) -> str:
        fingerprint = tuple(sorted((node.name, tuple(sorted(node.dependencies))) for node in self.nodes))
        return str(hash(fingerprint))


class _GraphvizGraph:
    def __init__(self, source: str):
        self.source = source


def create_graphviz_graph(
    *,
    nodes: Iterable[DataflowNode],
    comment: str,
    node_modifiers: MutableMapping[str, Any],
    strictly_display_only_nodes_passed_in: bool,
    graphviz_kwargs: Mapping[str, Any],
    orient: str,
    config: Mapping[str, Any],
) -> _GraphvizGraph:
    """Return a DOT graph representing the dependencies between nodes."""

    del node_modifiers, strictly_display_only_nodes_passed_in, graphviz_kwargs, config

    unique_nodes: Dict[str, DataflowNode] = {node.name: node for node in nodes}
    lines = [f'digraph "{comment}" {{', f"  rankdir={orient};"]
    for node in unique_nodes.values():
        shape = "box" if node.is_external_input else "ellipse"
        lines.append(f'  "{node.name}" [shape={shape}];')
    edges: set[tuple[str, str]] = set()
    for node in unique_nodes.values():
        for dependency in node.dependencies:
            edges.add((dependency, node.name))
    for src, dst in sorted(edges):
        lines.append(f'  "{src}" -> "{dst}";')
    lines.append("}")
    return _GraphvizGraph("\n".join(lines))


class HamiltonLanguageServer:
    CMD_VIEW_REQUEST = "lsp-view-request"
    CMD_VIEW_RESPONSE = "lsp-view-response"

    def __init__(self, server: str = "HamiltonServer", version: str | None = None, loop: Any | None = None):
        del loop
        self.server = server
        self.version = version or "0.1.0"
        self.workspace = Workspace()
        self.feature_handlers: Dict[str, List[Callable[..., Any]]] = {}
        self.command_handlers: Dict[str, Callable[..., Any]] = {}
        self.notifications: List[Dict[str, Any]] = []
        self.active_uri: str = ""
        self.active_version: str = ""
        self.orientation: str = "LR"
        self.node_locations: Dict[str, Location] = {}
        self.fn_graph: FunctionGraph = FunctionGraph.empty()
        self.h_graph: HamiltonGraph = HamiltonGraph.from_graph(self.fn_graph)
        self._started = False

    def feature(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.feature_handlers.setdefault(name, []).append(func)
            return func

        return decorator

    def command(self, name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.command_handlers[name] = func
            return func

        return decorator

    def thread(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            return func

        return decorator

    def start_io(self) -> None:
        self._started = True

    def send_notification(self, name: str, payload: Mapping[str, Any]) -> None:
        message = {"command": name, **dict(payload)}
        self.notifications.append(message)


def module_from_source(source: str, module_name: str = "hamilton_lsp_document") -> ModuleType:
    module = ModuleType(module_name)
    exec(compile(source, module_name, "exec"), module.__dict__)
    return module


def _annotation_to_string(annotation: Any) -> str:
    if annotation is inspect.Signature.empty:
        return "typing.Any"
    if isinstance(annotation, str):
        return annotation
    module = getattr(annotation, "__module__", "builtins")
    name = getattr(annotation, "__qualname__", repr(annotation))
    if module == "builtins":
        return name
    return f"{module}.{name}"


def _build_nodes_from_module(module: ModuleType) -> tuple[Dict[str, DataflowNode], Dict[str, DataflowNode]]:
    nodes: Dict[str, DataflowNode] = {}
    externals: Dict[str, DataflowNode] = {}
    for name, candidate in inspect.getmembers(module, inspect.isfunction):
        signature = inspect.signature(candidate)
        dependencies = [parameter.name for parameter in signature.parameters.values()]
        node = DataflowNode(
            name=name,
            type=_annotation_to_string(signature.return_annotation),
            documentation=inspect.getdoc(candidate) or "",
            dependencies=dependencies,
            is_external_input=False,
            originating_functions=[candidate],
        )
        nodes[name] = node

    for node in list(nodes.values()):
        for dependency in node.dependencies:
            if dependency in nodes or dependency in externals:
                continue
            externals[dependency] = DataflowNode(
                name=dependency,
                type="typing.Any",
                documentation="",
                dependencies=[],
                is_external_input=True,
                originating_functions=[],
            )
    return nodes, externals


def register_server_features(ls: HamiltonLanguageServer) -> HamiltonLanguageServer:
    @ls.feature(TEXT_DOCUMENT_DID_CHANGE)
    def did_change(server: HamiltonLanguageServer, params: DidChangeTextDocumentParams) -> None:
        document = server.workspace.get_document(params.text_document.uri)
        if params.content_changes:
            document.text = params.content_changes[-1]
        document.version = params.text_document.version
        server.active_uri = document.uri

        try:
            module = module_from_source(document.source)
            fn_graph = FunctionGraph.from_modules(module)
            h_graph = HamiltonGraph.from_graph(fn_graph)
        except Exception:  # pragma: no cover - invalid source should not crash server
            return

        server.fn_graph = fn_graph
        server.h_graph = h_graph
        if server.active_version != server.h_graph.version:
            server.active_version = server.h_graph.version
            hamilton_view(server, [{}])

    @ls.feature(TEXT_DOCUMENT_DID_OPEN)
    def did_open(server: HamiltonLanguageServer, params: DidOpenTextDocumentParams) -> None:
        server.workspace.put_document(params.text_document)
        did_change(
            server,
            DidChangeTextDocumentParams(
                text_document=VersionedTextDocumentIdentifier(
                    uri=params.text_document.uri, version=params.text_document.version
                ),
                content_changes=[params.text_document.text],
            ),
        )

    @ls.feature(TEXT_DOCUMENT_COMPLETION)
    def on_completion(server: HamiltonLanguageServer, params: CompletionParams) -> CompletionList:
        document = server.workspace.get_document(params.text_document.uri)
        if document.uri != server.active_uri:
            did_change(
                server,
                DidChangeTextDocumentParams(
                    text_document=VersionedTextDocumentIdentifier(uri=document.uri, version=document.version),
                    content_changes=[document.text],
                ),
            )

        items: List[CompletionItem] = []
        for node in server.h_graph.nodes:
            if node.is_external_input:
                continue
            items.append(
                CompletionItem(
                    label=node.name,
                    label_details=CompletionItemLabelDetails(detail=f" {node.type}", description="Node"),
                    kind=CompletionItemKind.Function,
                    documentation=node.documentation,
                    insert_text=f"{node.name}: {node.type}",
                )
            )
        return CompletionList(items=items, is_incomplete=False)

    @ls.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
    def document_symbols(server: HamiltonLanguageServer, params: DocumentSymbolParams) -> List[SymbolInformation]:
        symbols: List[SymbolInformation] = []
        document = server.workspace.get_document(params.text_document.uri)
        if document.uri != server.active_uri:
            did_change(
                server,
                DidChangeTextDocumentParams(
                    text_document=VersionedTextDocumentIdentifier(uri=document.uri, version=document.version),
                    content_changes=[document.text],
                ),
            )

        for node in server.h_graph.nodes:
            if node.originating_functions:
                origin = node.originating_functions[0]
                start_line = max(origin.__code__.co_firstlineno - 1, 0)
            else:
                start_line = 0
            node_kind = SymbolKind.Field if node.is_external_input else SymbolKind.Function
            location = Location(
                uri=params.text_document.uri,
                range=Range(
                    start=Position(line=start_line, character=0),
                    end=Position(line=start_line + 1, character=0),
                ),
            )
            server.node_locations[node.name] = location
            symbols.append(
                SymbolInformation(
                    name=node.name,
                    kind=node_kind,
                    location=location,
                    container_name="Hamilton",
                )
            )
        return symbols

    @ls.thread()
    @ls.command(HamiltonLanguageServer.CMD_VIEW_REQUEST)
    def hamilton_view(server: HamiltonLanguageServer, args: List[Dict[str, Any]]) -> None:
        params = args[0] if args else {}
        if params.get("rotate"):
            server.orientation = "TB" if server.orientation == "LR" else "LR"

        graph = create_graphviz_graph(
            nodes=server.fn_graph.get_nodes(),
            comment="hamilton-language-server",
            node_modifiers={},
            strictly_display_only_nodes_passed_in=True,
            graphviz_kwargs={},
            orient=server.orientation,
            config={},
        )
        server.send_notification(
            HamiltonLanguageServer.CMD_VIEW_RESPONSE,
            {"uri": server.active_uri, "dot": graph.source},
        )

    return ls
