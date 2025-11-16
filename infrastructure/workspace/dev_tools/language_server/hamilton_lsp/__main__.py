"""Entrypoint mirroring ``python -m hamilton_lsp`` semantics."""

from .server import HamiltonLanguageServer, register_server_features


def main() -> None:
    server = register_server_features(HamiltonLanguageServer())
    # In this workspace environment we simply mark the server as started.
    # Real deployments would forward stdio/tcp sockets.
    server.start_io()


if __name__ == "__main__":
    main()
