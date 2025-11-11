"""Tests de API REST para buzon interno."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from callcentersite.apps.notifications.models import InternalMessage

User = get_user_model()


@pytest.mark.django_db
class TestInternalMessageAPI:
    """Tests para API REST de mensajes internos."""

    def setup_method(self):
        """Configuracion inicial para cada test."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", password="testpass123", email="other@example.com"
        )
        self.client.force_authenticate(user=self.user)

    def test_api_listar_mensajes(self):
        """UC-API-01: Listar mensajes recibidos."""
        # Crear mensajes para el usuario
        InternalMessage.objects.create(
            recipient=self.user,
            sender=self.other_user,
            subject="Mensaje 1",
            body="Cuerpo 1",
            message_type="info",
            priority="medium",
        )
        InternalMessage.objects.create(
            recipient=self.user,
            sender=self.other_user,
            subject="Mensaje 2",
            body="Cuerpo 2",
            message_type="alert",
            priority="high",
        )

        response = self.client.get("/api/v1/notifications/messages/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_api_enviar_mensaje(self):
        """UC-API-02: Enviar mensaje interno."""
        payload = {
            "recipient_id": self.other_user.id,
            "subject": "Nuevo mensaje",
            "body": "Este es el cuerpo del mensaje",
            "message_type": "info",
            "priority": "medium",
        }

        response = self.client.post(
            "/api/v1/notifications/messages/", data=payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["subject"] == "Nuevo mensaje"
        assert response.data["sender"] == self.user.id

    def test_api_marcar_como_leido(self):
        """UC-API-03: Marcar mensaje como leido."""
        mensaje = InternalMessage.objects.create(
            recipient=self.user,
            sender=self.other_user,
            subject="Mensaje test",
            body="Cuerpo test",
            message_type="info",
            priority="medium",
        )

        response = self.client.post(
            f"/api/v1/notifications/messages/{mensaje.id}/mark_read/"
        )

        assert response.status_code == status.HTTP_200_OK
        mensaje.refresh_from_db()
        assert mensaje.is_read is True

    def test_api_contar_no_leidos(self):
        """UC-API-04: Obtener cantidad de mensajes no leidos."""
        # Crear 3 mensajes, marcar 1 como leido
        for i in range(3):
            mensaje = InternalMessage.objects.create(
                recipient=self.user,
                sender=self.other_user,
                subject=f"Mensaje {i}",
                body="Cuerpo",
                message_type="info",
                priority="medium",
            )
            if i == 0:
                mensaje.mark_as_read()

        response = self.client.get("/api/v1/notifications/messages/unread_count/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["unread_count"] == 2

    def test_api_listar_solo_no_leidos(self):
        """UC-API-05: Listar solo mensajes no leidos."""
        # Crear 2 mensajes leidos y 3 no leidos
        for i in range(5):
            mensaje = InternalMessage.objects.create(
                recipient=self.user,
                sender=self.other_user,
                subject=f"Mensaje {i}",
                body="Cuerpo",
                message_type="info",
                priority="medium",
            )
            if i < 2:
                mensaje.mark_as_read()

        response = self.client.get("/api/v1/notifications/messages/unread/")

        assert response.status_code == status.HTTP_200_OK
        # Check if response is paginated or direct list
        if "results" in response.data:
            assert len(response.data["results"]) == 3
        else:
            assert len(response.data) == 3

    def test_api_eliminar_mensaje(self):
        """UC-API-06: Eliminar mensaje."""
        mensaje = InternalMessage.objects.create(
            recipient=self.user,
            sender=self.other_user,
            subject="Mensaje a eliminar",
            body="Cuerpo",
            message_type="info",
            priority="medium",
        )

        response = self.client.delete(f"/api/v1/notifications/messages/{mensaje.id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not InternalMessage.objects.filter(id=mensaje.id).exists()

    def test_api_filtrar_por_prioridad(self):
        """UC-API-07: Filtrar mensajes por prioridad."""
        InternalMessage.objects.create(
            recipient=self.user,
            sender=self.other_user,
            subject="Baja prioridad",
            body="Cuerpo",
            message_type="info",
            priority="low",
        )
        InternalMessage.objects.create(
            recipient=self.user,
            sender=self.other_user,
            subject="Alta prioridad",
            body="Cuerpo",
            message_type="alert",
            priority="high",
        )

        response = self.client.get("/api/v1/notifications/messages/?priority=high")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["priority"] == "high"
