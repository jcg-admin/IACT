"""Pruebas para asegurar la configuración básica del proyecto Django."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_module(module_name: str, relative_path: Path) -> ModuleType:
    """Carga un módulo desde ``relative_path`` con el nombre ``module_name``."""

    spec = importlib.util.spec_from_file_location(module_name, relative_path)
    if spec is None or spec.loader is None:  # pragma: no cover - seguridad
        raise RuntimeError(f'No fue posible cargar el módulo {module_name}.')

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_manage_usa_callcentersite_como_modulo_de_configuracion(monkeypatch):
    """``manage.py`` debe apuntar a ``callcentersite.settings`` por omisión."""

    manage_module = _load_module('manage_module', PROJECT_ROOT / 'manage.py')

    # Garantizar que partimos sin variable configurada.
    monkeypatch.delenv('DJANGO_SETTINGS_MODULE', raising=False)

    # Configuramos un ``django.core.management`` mínimo para evitar dependencias.
    fake_management = ModuleType('django.core.management')
    ejecuciones: dict[str, Any] = {}

    def _fake_execute_from_command_line(argv: list[str]) -> None:
        ejecuciones['argv'] = argv

    fake_management.execute_from_command_line = _fake_execute_from_command_line  # type: ignore[attr-defined]

    django_module = ModuleType('django')
    django_core_module = ModuleType('django.core')
    django_core_module.management = fake_management  # type: ignore[attr-defined]
    mail_module = ModuleType('django.core.mail')
    mail_module.outbox = []  # type: ignore[attr-defined]
    django_core_module.mail = mail_module  # type: ignore[attr-defined]
    django_module.core = django_core_module  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, 'django', django_module)
    monkeypatch.setitem(sys.modules, 'django.core', django_core_module)
    monkeypatch.setitem(sys.modules, 'django.core.mail', mail_module)
    monkeypatch.setitem(sys.modules, 'django.core.management', fake_management)
    monkeypatch.setattr(sys, 'argv', ['manage.py', 'check'], raising=False)

    manage_module.main()

    assert os.environ['DJANGO_SETTINGS_MODULE'] == 'callcentersite.settings'
    assert ejecuciones['argv'] == ['manage.py', 'check']


def test_wsgi_expone_la_aplicacion_con_la_configuracion_correcta(monkeypatch):
    """El módulo WSGI debe cargar ``callcentersite.settings`` y exponer la aplicación."""

    monkeypatch.delenv('DJANGO_SETTINGS_MODULE', raising=False)

    fake_wsgi = ModuleType('django.core.wsgi')
    aplicacion_sentinel = object()

    def _fake_get_wsgi_application():
        fake_wsgi.llamado = True  # type: ignore[attr-defined]
        return aplicacion_sentinel

    fake_wsgi.get_wsgi_application = _fake_get_wsgi_application  # type: ignore[attr-defined]

    django_module = ModuleType('django')
    django_core_module = ModuleType('django.core')
    django_core_module.wsgi = fake_wsgi  # type: ignore[attr-defined]
    mail_module = ModuleType('django.core.mail')
    mail_module.outbox = []  # type: ignore[attr-defined]
    django_core_module.mail = mail_module  # type: ignore[attr-defined]
    django_module.core = django_core_module  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, 'django', django_module)
    monkeypatch.setitem(sys.modules, 'django.core', django_core_module)
    monkeypatch.setitem(sys.modules, 'django.core.mail', mail_module)
    monkeypatch.setitem(sys.modules, 'django.core.wsgi', fake_wsgi)

    wsgi_module = _load_module(
        'callcentersite.wsgi_test', PROJECT_ROOT / 'callcentersite' / 'wsgi.py'
    )

    assert os.environ['DJANGO_SETTINGS_MODULE'] == 'callcentersite.settings'
    assert getattr(fake_wsgi, 'llamado') is True
    assert wsgi_module.application is aplicacion_sentinel


def test_settings_referencia_los_componentes_del_paquete_callcentersite(monkeypatch):
    """Las rutas internas deben apuntar al paquete renombrado ``callcentersite``."""

    stub_dj_database_url = ModuleType('dj_database_url')

    def _fake_config(**kwargs: Any) -> dict[str, str]:  # pragma: no cover - simple
        return {'ENGINE': 'django.db.backends.sqlite3'}

    stub_dj_database_url.config = _fake_config  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, 'dj_database_url', stub_dj_database_url)

    django_module = ModuleType('django')
    django_core_module = ModuleType('django.core')
    mail_module = ModuleType('django.core.mail')
    mail_module.outbox = []  # type: ignore[attr-defined]
    django_core_module.mail = mail_module  # type: ignore[attr-defined]
    django_module.core = django_core_module  # type: ignore[attr-defined]

    monkeypatch.setitem(sys.modules, 'django', django_module)
    monkeypatch.setitem(sys.modules, 'django.core', django_core_module)
    monkeypatch.setitem(sys.modules, 'django.core.mail', mail_module)

    settings_module = _load_module(
        'callcentersite.settings_test', PROJECT_ROOT / 'callcentersite' / 'settings.py'
    )

    assert settings_module.ROOT_URLCONF == 'callcentersite.urls'
    assert settings_module.WSGI_APPLICATION == 'callcentersite.wsgi.application'
