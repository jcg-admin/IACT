import textwrap

import pytest


@pytest.fixture()
def server_module():
    import importlib

    return importlib.import_module(
        "infrastructure.workspace.dev_tools.language_server.hamilton_lsp.server"
    )


def sample_source() -> str:
    return textwrap.dedent(
        '''
        from typing import Dict

        def raw_data() -> Dict[str, int]:
            """Source information feeding a Hamilton graph."""
            return {"ideas": 3, "experiments": 1}

        def prompt_template(raw_data: Dict[str, int]) -> str:
            """Formats a prompt that references upstream values."""
            return f"Use {raw_data['ideas']} ideas"

        def llm_prompt(prompt_template: str) -> str:
            return prompt_template + " pronto"

        def llm_response(llm_prompt: str) -> str:
            return llm_prompt.upper()
        '''
    )


def test_registers_lsp_features(server_module):
    server = server_module.HamiltonLanguageServer()
    server = server_module.register_server_features(server)

    assert server_module.TEXT_DOCUMENT_DID_OPEN in server.feature_handlers
    assert server_module.TEXT_DOCUMENT_DID_CHANGE in server.feature_handlers
    assert server_module.TEXT_DOCUMENT_COMPLETION in server.feature_handlers
    assert server_module.TEXT_DOCUMENT_DOCUMENT_SYMBOL in server.feature_handlers
    assert server_module.HamiltonLanguageServer.CMD_VIEW_REQUEST in server.command_handlers


def test_builds_graph_on_document_open(server_module):
    server = server_module.register_server_features(server_module.HamiltonLanguageServer())

    document = server_module.TextDocumentItem(
        uri="file:///tmp/example.py",
        text=sample_source(),
        version=1,
    )
    params = server_module.DidOpenTextDocumentParams(text_document=document)
    handler = server.feature_handlers[server_module.TEXT_DOCUMENT_DID_OPEN][0]
    handler(server, params)

    node_names = {node.name for node in server.h_graph.nodes}
    assert {"raw_data", "prompt_template", "llm_prompt", "llm_response"}.issubset(node_names)


def test_completion_items_reflect_annotations(server_module):
    server = server_module.register_server_features(server_module.HamiltonLanguageServer())
    document = server_module.TextDocumentItem(
        uri="file:///tmp/example.py",
        text=sample_source(),
        version=1,
    )
    open_handler = server.feature_handlers[server_module.TEXT_DOCUMENT_DID_OPEN][0]
    open_handler(server, server_module.DidOpenTextDocumentParams(text_document=document))

    completion_handler = server.feature_handlers[server_module.TEXT_DOCUMENT_COMPLETION][0]
    completions = completion_handler(
        server,
        server_module.CompletionParams(
            text_document=server_module.TextDocumentIdentifier(uri=document.uri)
        ),
    )

    labels = {item.label for item in completions.items}
    assert "prompt_template" in labels
    prompt_item = next(item for item in completions.items if item.label == "prompt_template")
    assert "str" in prompt_item.label_details.detail


def test_hamilton_view_command_emits_dot_notification(server_module):
    server = server_module.register_server_features(server_module.HamiltonLanguageServer())
    document = server_module.TextDocumentItem(
        uri="file:///tmp/example.py",
        text=sample_source(),
        version=1,
    )
    open_handler = server.feature_handlers[server_module.TEXT_DOCUMENT_DID_OPEN][0]
    open_handler(server, server_module.DidOpenTextDocumentParams(text_document=document))

    view_command = server.command_handlers[server_module.HamiltonLanguageServer.CMD_VIEW_REQUEST]
    server.notifications.clear()
    view_command(server, [{}])
    assert server.notifications
    payload = server.notifications[-1]
    assert payload["uri"] == document.uri
    assert "prompt_template" in payload["dot"]

    view_command(server, [{"rotate": True}])
    assert server.orientation == "TB"


def test_document_symbols_register_node_locations(server_module):
    server = server_module.register_server_features(server_module.HamiltonLanguageServer())
    document = server_module.TextDocumentItem(
        uri="file:///tmp/example.py",
        text=sample_source(),
        version=1,
    )
    open_handler = server.feature_handlers[server_module.TEXT_DOCUMENT_DID_OPEN][0]
    open_handler(server, server_module.DidOpenTextDocumentParams(text_document=document))

    symbol_handler = server.feature_handlers[server_module.TEXT_DOCUMENT_DOCUMENT_SYMBOL][0]
    symbols = symbol_handler(
        server,
        server_module.DocumentSymbolParams(text_document=server_module.TextDocumentIdentifier(uri=document.uri)),
    )

    assert any(symbol.name == "llm_response" for symbol in symbols)
    assert "llm_response" in server.node_locations
    location = server.node_locations["llm_response"]
    assert location.uri == document.uri
    assert location.range.start.line >= 0
