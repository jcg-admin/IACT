"""Pruebas TDD para el middleware de seguridad de sesiones."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory

from callcentersite.middleware.session_security import (
    SESSION_IP_KEY,
    SESSION_UA_KEY,
    SessionSecurityMiddleware,
)


@pytest.fixture
def rf() -> RequestFactory:
    """Factory de requests para simplificar la creación de peticiones."""

    return RequestFactory()


def _prepare_request(request, user, ip: str, user_agent: str) -> None:
    """Configura sesión y metadatos mínimos para las pruebas."""

    session_middleware = SessionMiddleware(lambda req: HttpResponse())
    session_middleware.process_request(request)
    request.session.save()

    request.user = user
    request.META["REMOTE_ADDR"] = ip
    request.META["HTTP_USER_AGENT"] = user_agent


@pytest.mark.django_db
def test_middleware_guarda_ip_y_user_agent_iniciales(rf: RequestFactory) -> None:
    """Cuando no existen valores previos, el middleware los registra."""

    user = get_user_model().objects.create_user(
        username="middleware-user",
        password="segura123",
        email="middleware@example.com",
    )
    request = rf.get("/recurso/")
    _prepare_request(request, user, "10.0.0.1", "Mozilla/5.0")

    captured = {"called": False}

    def get_response(req):
        captured["called"] = True
        return HttpResponse(status=200)

    response = SessionSecurityMiddleware(get_response)(request)

    assert response.status_code == 200
    assert captured["called"] is True
    assert request.session[SESSION_IP_KEY] == "10.0.0.1"
    assert request.session[SESSION_UA_KEY] == "Mozilla/5.0"


@pytest.mark.django_db
def test_middleware_invalida_sesion_si_cambia_ip(rf: RequestFactory) -> None:
    """Un cambio de IP provoca cierre de sesión inmediato con 401."""

    user = get_user_model().objects.create_user(
        username="middleware-ip",
        password="segura123",
        email="middleware-ip@example.com",
    )
    request = rf.get("/recurso/")
    _prepare_request(request, user, "10.0.0.1", "Mozilla/5.0")
    request.session[SESSION_IP_KEY] = "10.0.0.1"
    request.session[SESSION_UA_KEY] = "Mozilla/5.0"
    request.META["REMOTE_ADDR"] = "10.0.0.2"

    called = {"executed": False}

    def get_response(req):
        called["executed"] = True
        return HttpResponse(status=200)

    response = SessionSecurityMiddleware(get_response)(request)

    assert response.status_code == 401
    assert called["executed"] is False
    assert request.user.is_authenticated is False
    assert SESSION_IP_KEY not in request.session
    assert SESSION_UA_KEY not in request.session


@pytest.mark.django_db
def test_middleware_invalida_sesion_si_cambia_user_agent(rf: RequestFactory) -> None:
    """Un cambio de agente de usuario también invalida la sesión."""

    user = get_user_model().objects.create_user(
        username="middleware-ua",
        password="segura123",
        email="middleware-ua@example.com",
    )
    request = rf.get("/recurso/")
    _prepare_request(request, user, "10.0.0.1", "Mozilla/5.0")
    request.session[SESSION_IP_KEY] = "10.0.0.1"
    request.session[SESSION_UA_KEY] = "Mozilla/5.0"
    request.META["HTTP_USER_AGENT"] = "Mozilla/6.0"

    invoked = {"executed": False}

    def get_response(req):
        invoked["executed"] = True
        return HttpResponse(status=200)

    response = SessionSecurityMiddleware(get_response)(request)

    assert response.status_code == 401
    assert invoked["executed"] is False
    assert request.user.is_authenticated is False
    assert SESSION_IP_KEY not in request.session
    assert SESSION_UA_KEY not in request.session
