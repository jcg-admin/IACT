"""SSH key helpers used by the VPN agent."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_KEY_TYPES = {"ed25519", "rsa"}


@dataclass
class GeneratedKeyPair:
    private_key_path: Path
    public_key_path: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "private_key_path": str(self.private_key_path),
            "public_key_path": str(self.public_key_path),
        }


def _generate_paramiko_key(key_type: str) -> Any:
    import paramiko

    if key_type == "ed25519":
        return paramiko.Ed25519Key.generate()
    if key_type == "rsa":
        return paramiko.RSAKey.generate(bits=4096)
    raise ValueError(f"Unsupported key type: {key_type}")


def _public_key_line(key: Any) -> str:
    if hasattr(key, "get_name") and hasattr(key, "get_base64"):
        return f"{key.get_name()} {key.get_base64()}"
    if hasattr(key, "get_name") and hasattr(key, "public_blob"):
        blob = getattr(key, "public_blob")
        if isinstance(blob, bytes):
            encoded = base64.b64encode(blob).decode("utf-8")
        else:  # pragma: no cover - defensive
            encoded = str(blob)
        return f"{key.get_name()} {encoded}"
    raise TypeError("Key does not expose public material")


def generate_keypair(*, base_dir: Path, key_name: str, key_type: str = "ed25519") -> GeneratedKeyPair:
    if key_type not in SUPPORTED_KEY_TYPES:
        raise ValueError(f"Unsupported key type '{key_type}'. Expected one of {sorted(SUPPORTED_KEY_TYPES)}")

    base_dir.mkdir(parents=True, exist_ok=True)
    key = _generate_paramiko_key(key_type)

    private_key_path = base_dir / key_name
    public_key_path = base_dir / f"{key_name}.pub"

    key.write_private_key_file(str(private_key_path))
    public_key_path.write_text(_public_key_line(key) + "\n")

    return GeneratedKeyPair(private_key_path=private_key_path, public_key_path=public_key_path)


__all__ = ["GeneratedKeyPair", "generate_keypair", "SUPPORTED_KEY_TYPES"]
