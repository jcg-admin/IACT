import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_RELATIVE_PATH = Path("infrastructure/devcontainer/scripts/init_host.sh")


class InitHostScriptTests(unittest.TestCase):
    """Pruebas para el script init_host.sh."""

    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.tmpdir.name)
        self._bootstrap_project_tree()

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _bootstrap_project_tree(self) -> None:
        """Crea el arbol minimo requerido por el script."""

        scripts_dir = self.project_root / "infrastructure" / "devcontainer" / "scripts"
        scripts_dir.mkdir(parents=True)

        script_contents = SCRIPT_RELATIVE_PATH.read_text(encoding="utf-8")
        (scripts_dir / "init_host.sh").write_text(script_contents, encoding="utf-8")
        os.chmod(scripts_dir / "init_host.sh", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        required_scripts = [
            "on_create.sh",
            "update_content.sh",
            "post_create.sh",
            "post_start.sh",
        ]
        for idx, script_name in enumerate(required_scripts):
            script_path = scripts_dir / script_name
            script_path.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            if idx != 0:
                os.chmod(script_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        devcontainer_dir = self.project_root / ".devcontainer"
        devcontainer_dir.mkdir()
        for filename in ("docker-compose.yml", "dockerfile", "devcontainer.json"):
            (devcontainer_dir / filename).write_text("{}\n", encoding="utf-8")

        api_dir = self.project_root / "api" / "callcentersite"
        api_dir.mkdir(parents=True)
        (api_dir / "manage.py").write_text("print('hola')\n", encoding="utf-8")

        requirements_dir = api_dir / "requirements"
        requirements_dir.mkdir()
        for filename in ("base.txt", "dev.txt", "test.txt"):
            (requirements_dir / filename).write_text("django==5.0\n", encoding="utf-8")

        (api_dir / "env.example").write_text("SECRET_KEY=dev\n", encoding="utf-8")

    def test_script_continues_after_fixing_permissions(self) -> None:
        """El script debe completar la ejecucion aun cuando encuentre advertencias."""

        result = subprocess.run(
            ["bash", str(SCRIPT_RELATIVE_PATH)],
            cwd=self.project_root,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            result.returncode,
            0,
            msg=textwrap.dedent(
                f"""\
                El script termino con codigo {result.returncode}.
                Stdout:\n{result.stdout}\n
                Stderr:\n{result.stderr}
                """
            ),
        )
        self.assertIn("[WARN] Script not executable", result.stdout)
        self.assertIn("Validating critical files", result.stdout)

    def test_log_counters_use_posix_arithmetic(self) -> None:
        """Los contadores deben incrementarse usando aritmetica POSIX."""

        script_text = SCRIPT_RELATIVE_PATH.read_text(encoding="utf-8")

        self.assertNotIn("((WARNINGS +=", script_text)
        self.assertNotIn("((ERRORS +=", script_text)
        self.assertIn("WARNINGS=$((WARNINGS + 1))", script_text)
        self.assertIn("ERRORS=$((ERRORS + 1))", script_text)


if __name__ == "__main__":
    unittest.main()
