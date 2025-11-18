"""Tests de API para autenticación y refresco de tokens.

Validan los endpoints documentados en docs/backend para login
(`POST /api/v1/auth/login/`) y rotación de tokens
(`POST /api/v1/auth/refresh/`).
"""

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_login_endpoint_emite_tokens() -> None:
    """RF-005: el endpoint de login devuelve tokens JWT y metadatos."""

    client = APIClient()
    from callcentersite.apps.users.models import User

    user = User.objects.create_user(
        username="api.user",
        password="SecureP@ss123",
        email="api.user@example.com",
        status="ACTIVO",
    )

    response = client.post(
        "/api/v1/auth/login/",
        {"username": user.username, "password": "SecureP@ss123"},
        format="json",
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "Bearer"
    assert payload["expires_in"] == 900
    assert "access_token" in payload and payload["access_token"]
    assert "refresh_token" in payload and payload["refresh_token"]


@pytest.mark.django_db
def test_refresh_endpoint_rota_y_blacklistea_refresh_tokens() -> None:
    """RF-006: rotación de tokens con blacklist del refresh previo."""

    client = APIClient()
    from callcentersite.apps.users.models import User
    from callcentersite.apps.authentication.services import TokenService

    user = User.objects.create_user(
        username="refresh.user",
        password="SecureP@ss123",
        email="refresh.user@example.com",
    )

    tokens = TokenService.generate_jwt_tokens(user)

    response = client.post(
        "/api/v1/auth/refresh/",
        {"refresh": tokens["refresh"]},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access"] != tokens["access"]
    assert data["refresh"] != tokens["refresh"]

