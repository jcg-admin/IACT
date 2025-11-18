"""Self-contained Hamilton language-server implementation for the workspace."""

__version__ = "0.1.0"

from .server import HamiltonLanguageServer, register_server_features

__all__ = ("HamiltonLanguageServer", "register_server_features", "__version__")
