"""
Tests TDD para Casos de Uso del modulo de Buzon Interno (Notifications).

Sistema de mensajeria interna sin correo electronico.
"""

import pytest
from datetime import date, timedelta, datetime
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestEnviarMensajeInterno:
    """Enviar mensaje interno a usuario."""

    def test_enviar_mensaje_basico(self):
        """
        UC-MENSAJE-01: Enviar mensaje interno basico.

        Given dos usuarios en el sistema
        When usuario A envia mensaje a usuario B
        Then mensaje se crea correctamente
        """
        from callcentersite.apps.notifications.services import NotificationService

        # Arrange
        usuario_a = User.objects.create_user(
            username="usuarioA", password="pass", email="a@test.com"
        )
        usuario_b = User.objects.create_user(
            username="usuarioB", password="pass", email="b@test.com"
        )

        # Act
        mensaje = NotificationService.enviar_mensaje(
            sender_id=usuario_a.id,
            recipient_id=usuario_b.id,
            subject="Reunion importante",
            body="Por favor asiste a la reunion del viernes",
            message_type="info",
            priority="medium",
        )

        # Assert
        assert mensaje is not None
        assert mensaje.sender.id == usuario_a.id
        assert mensaje.recipient.id == usuario_b.id
        assert mensaje.subject == "Reunion importante"
        assert mensaje.is_read is False

    def test_enviar_mensaje_con_expiracion(self):
        """
        UC-MENSAJE-02: Enviar mensaje con fecha de expiracion.

        Given mensaje con expires_at
        When se crea el mensaje
        Then mensaje tiene fecha de expiracion configurada
        """
        from callcentersite.apps.notifications.services import NotificationService

        # Arrange
        usuario_a = User.objects.create_user(
            username="usuarioA", password="pass", email="a@test.com"
        )
        usuario_b = User.objects.create_user(
            username="usuarioB", password="pass", email="b@test.com"
        )
        expira_en = timezone.now() + timedelta(days=7)

        # Act
        mensaje = NotificationService.enviar_mensaje(
            sender_id=usuario_a.id,
            recipient_id=usuario_b.id,
            subject="Alerta temporal",
            body="Esta alerta expira en 7 dias",
            message_type="alert",
            priority="high",
            expires_at=expira_en,
        )

        # Assert
        assert mensaje.expires_at is not None
        assert mensaje.expires_at == expira_en


@pytest.mark.django_db
class TestListarMensajes:
    """Listar mensajes recibidos por usuario."""

    def test_listar_mensajes_recibidos(self):
        """
        UC-MENSAJE-03: Listar todos los mensajes recibidos.

        Given usuario con mensajes recibidos
        When se listan mensajes
        Then retorna todos los mensajes del usuario
        """
        from callcentersite.apps.notifications.services import NotificationService
        from callcentersite.apps.notifications.models import InternalMessage

        # Arrange
        usuario = User.objects.create_user(
            username="usuario", password="pass", email="user@test.com"
        )
        otro_usuario = User.objects.create_user(
            username="otro", password="pass", email="otro@test.com"
        )

        # Crear 3 mensajes para el usuario
        for i in range(3):
            InternalMessage.objects.create(
                recipient=usuario,
                sender=otro_usuario,
                subject=f"Mensaje {i+1}",
                body="Cuerpo del mensaje",
                message_type="info",
                priority="medium",
            )

        # Act
        mensajes = NotificationService.listar_mensajes(user_id=usuario.id)

        # Assert
        assert len(mensajes) == 3

    def test_filtrar_mensajes_no_leidos(self):
        """
        UC-MENSAJE-04: Filtrar mensajes no leidos.

        Given usuario con mensajes leidos y no leidos
        When se filtran por is_read=False
        Then retorna solo mensajes no leidos
        """
        from callcentersite.apps.notifications.services import NotificationService
        from callcentersite.apps.notifications.models import InternalMessage

        # Arrange
        usuario = User.objects.create_user(
            username="usuario", password="pass", email="user@test.com"
        )

        # Crear 2 mensajes leidos y 3 no leidos
        for i in range(5):
            mensaje = InternalMessage.objects.create(
                recipient=usuario,
                subject=f"Mensaje {i+1}",
                body="Cuerpo",
                message_type="info",
                priority="medium",
            )
            if i < 2:
                mensaje.mark_as_read()

        # Act
        mensajes = NotificationService.listar_mensajes(
            user_id=usuario.id, is_read=False
        )

        # Assert
        assert len(mensajes) == 3


@pytest.mark.django_db
class TestMarcarComoLeido:
    """Marcar mensaje como leido."""

    def test_marcar_mensaje_como_leido(self):
        """
        UC-MENSAJE-05: Marcar mensaje como leido.

        Given mensaje no leido
        When se marca como leido
        Then is_read=True y read_at tiene fecha
        """
        from callcentersite.apps.notifications.services import NotificationService
        from callcentersite.apps.notifications.models import InternalMessage

        # Arrange
        usuario = User.objects.create_user(
            username="usuario", password="pass", email="user@test.com"
        )
        mensaje = InternalMessage.objects.create(
            recipient=usuario,
            subject="Test",
            body="Cuerpo",
            message_type="info",
            priority="medium",
        )

        # Act
        NotificationService.marcar_como_leido(mensaje_id=mensaje.id)

        # Assert
        mensaje.refresh_from_db()
        assert mensaje.is_read is True
        assert mensaje.read_at is not None


@pytest.mark.django_db
class TestMensajesSistema:
    """Mensajes generados automaticamente por el sistema."""

    def test_crear_mensaje_sistema(self):
        """
        UC-MENSAJE-06: Crear mensaje generado por sistema.

        Given notificacion automatica
        When sistema genera mensaje
        Then created_by_system=True y sender=None
        """
        from callcentersite.apps.notifications.services import NotificationService

        # Arrange
        usuario = User.objects.create_user(
            username="usuario", password="pass", email="user@test.com"
        )

        # Act
        mensaje = NotificationService.crear_mensaje_sistema(
            recipient_id=usuario.id,
            subject="Alerta de sistema",
            body="El sistema detecto una anomalia",
            message_type="system",
            priority="critical",
        )

        # Assert
        assert mensaje.created_by_system is True
        assert mensaje.sender is None
        assert mensaje.message_type == "system"


@pytest.mark.django_db
class TestEliminarMensajes:
    """Eliminar mensajes."""

    def test_eliminar_mensaje(self):
        """
        UC-MENSAJE-07: Eliminar mensaje.

        Given mensaje existente
        When se elimina
        Then mensaje ya no existe en BD
        """
        from callcentersite.apps.notifications.services import NotificationService
        from callcentersite.apps.notifications.models import InternalMessage

        # Arrange
        usuario = User.objects.create_user(
            username="usuario", password="pass", email="user@test.com"
        )
        mensaje = InternalMessage.objects.create(
            recipient=usuario,
            subject="Test",
            body="Cuerpo",
            message_type="info",
            priority="medium",
        )
        mensaje_id = mensaje.id

        # Act
        NotificationService.eliminar_mensaje(mensaje_id=mensaje_id)

        # Assert
        assert not InternalMessage.objects.filter(id=mensaje_id).exists()


@pytest.mark.django_db
class TestFiltrosPrioridad:
    """Filtrar mensajes por prioridad y tipo."""

    def test_filtrar_por_prioridad_alta(self):
        """
        UC-MENSAJE-08: Filtrar mensajes de prioridad alta.

        Given mensajes con diferentes prioridades
        When se filtra por priority=high
        Then retorna solo mensajes de alta prioridad
        """
        from callcentersite.apps.notifications.services import NotificationService
        from callcentersite.apps.notifications.models import InternalMessage

        # Arrange
        usuario = User.objects.create_user(
            username="usuario", password="pass", email="user@test.com"
        )

        # Crear mensajes con diferentes prioridades
        for priority in ["low", "medium", "high", "critical"]:
            InternalMessage.objects.create(
                recipient=usuario,
                subject=f"Mensaje {priority}",
                body="Cuerpo",
                message_type="info",
                priority=priority,
            )

        # Act
        mensajes = NotificationService.listar_mensajes(
            user_id=usuario.id, priority="high"
        )

        # Assert
        assert len(mensajes) == 1
        assert mensajes[0].priority == "high"
