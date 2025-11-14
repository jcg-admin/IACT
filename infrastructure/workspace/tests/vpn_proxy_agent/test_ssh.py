"""Tests for SSH key utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def test_generate_keypair_creates_files(monkeypatch, tmp_path: Path) -> None:
    from infrastructure.workspace.vpn_proxy_agent.ssh import keys

    fake_key = type(
        "FakeKey",
        (),
        {
            "write_private_key_file": lambda self, path: Path(path).write_text("PRIVATE"),
            "get_name": lambda self: "ssh-ed25519",
            "public_blob": b"PUBLIC",
        },
    )()

    def fake_generate_key(key_type: str) -> Any:
        assert key_type == "ed25519"
        return fake_key

    monkeypatch.setattr(keys, "_generate_paramiko_key", fake_generate_key)

    result = keys.generate_keypair(base_dir=tmp_path, key_name="vpn_key", key_type="ed25519")

    assert result.private_key_path.read_text() == "PRIVATE"
    assert result.public_key_path.read_text().startswith("ssh-ed25519")
