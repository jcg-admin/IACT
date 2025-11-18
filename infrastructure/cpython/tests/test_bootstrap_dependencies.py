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


def extract_function_body(script_text: str, function_name: str) -> str:
    pattern = re.compile(rf"{re.escape(function_name)}\(\)\s*{{", re.MULTILINE)
    match = pattern.search(script_text)
    if not match:
        raise AssertionError(f"Function {function_name} not found in bootstrap.sh")

    start = match.end()
    depth = 1
    index = start

    while index < len(script_text) and depth > 0:
        char = script_text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        index += 1

    if depth != 0:
        raise AssertionError(f"Could not parse body for {function_name}")

    return script_text[start:index - 1]


def test_refresh_package_metadata_function_declared():
    script_text = BOOTSTRAP_PATH.read_text(encoding="utf-8")
    body = extract_function_body(script_text, "refresh_package_metadata")

    assert "apt-get update" in body
    assert "configure_old_releases_mirror" in body


def test_old_releases_fallback_is_documented():
    script_text = BOOTSTRAP_PATH.read_text(encoding="utf-8")

    assert "old-releases.ubuntu.com" in script_text


def test_update_system_uses_metadata_refresh():
    script_text = BOOTSTRAP_PATH.read_text(encoding="utf-8")
    body = extract_function_body(script_text, "update_system")

    assert "refresh_package_metadata" in body


def test_install_dependencies_refreshes_metadata():
    script_text = BOOTSTRAP_PATH.read_text(encoding="utf-8")
    body = extract_function_body(script_text, "install_build_dependencies")

    assert "refresh_package_metadata" in body
