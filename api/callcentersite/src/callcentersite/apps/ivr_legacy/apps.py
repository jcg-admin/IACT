"""Configuración de la app ivr_legacy."""

from django.apps import AppConfig


class IVRLegacyConfig(AppConfig):
    """App que representa datos read-only del IVR."""

    name = "callcentersite.apps.ivr_legacy"
    verbose_name = "IVR Legacy"
