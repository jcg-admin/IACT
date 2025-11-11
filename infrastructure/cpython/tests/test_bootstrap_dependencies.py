import pathlib
import re


BOOTSTRAP_PATH = pathlib.Path(__file__).resolve().parents[1] / "bootstrap.sh"


def extract_package_list(script_text: str) -> list[str]:
    match = re.search(r"local packages=\((.*?)\)", script_text, re.DOTALL)
    if not match:
        raise AssertionError("Package list not found in bootstrap.sh")
    body = match.group(1)
    tokens = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens.extend(stripped.split())
    return [token.rstrip("\\") for token in tokens]


def test_build_dependency_package_list_matches_expected():
    script_text = BOOTSTRAP_PATH.read_text(encoding="utf-8")
    packages = extract_package_list(script_text)

    expected_packages = [
        "build-essential",
        "gdb",
        "lcov",
        "pkg-config",
        "libbz2-dev",
        "libffi-dev",
        "libgdbm-dev",
        "libgdbm-compat-dev",
        "liblzma-dev",
        "libncurses-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "libssl-dev",
        "tk-dev",
        "uuid-dev",
        "zlib1g-dev",
        "wget",
        "curl",
        "ca-certificates",
        "xz-utils",
    ]

    assert packages == expected_packages, f"Unexpected package list: {packages}"
