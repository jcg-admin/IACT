"""Pruebas para utilidades definidas en ``tests.conftest``."""

from __future__ import annotations

import sys
from types import ModuleType

import tests.conftest as conftest


class TestSafeResetInMemoryRegistry:
    """Validaciones sobre el restablecimiento resiliente del registro."""

    def test_no_falla_sin_modulo_de_usuarios(self) -> None:
        """Debe ignorar la ausencia de ``callcentersite.apps.users``."""

        originales: dict[str, ModuleType] = {}
        claves_relacionadas = [nombre for nombre in sys.modules if nombre.startswith("callcentersite")]
        for nombre in claves_relacionadas:
            originales[nombre] = sys.modules.pop(nombre)

        sys.modules["callcentersite"] = ModuleType("callcentersite")

        try:
            conftest.safe_reset_in_memory_registry()
        finally:
            sys.modules.pop("callcentersite", None)
            sys.modules.update(originales)
