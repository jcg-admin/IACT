import re
from pathlib import Path


def test_vagrant_synced_folder_allows_executables():
    vagrantfile = Path("infrastructure/cpython/Vagrantfile").read_text()
    match = re.search(
        r'config\.vm\.synced_folder\s+"\."\s*,\s*"/vagrant"[\s\S]*?mount_options:\s*\[(?P<options>[^\]]+)\]',
        vagrantfile,
    )
    assert match, "Vagrantfile is missing the /vagrant synced folder configuration"
    options = match.group("options")
    assert "fmode=" in options, "Synced folder mount options must explicitly set fmode"
    assert "fmode=775" in options, (
        "Synced folder mount options must grant execute permissions (fmode=775) "
        "so scripts remain runnable inside the VM"
    )
