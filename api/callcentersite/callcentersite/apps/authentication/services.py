"""Servicios de autenticación."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LoginAttempt
from callcentersite.apps.audit.models import AuditLog
from callcentersite.apps.notifications.models import InternalMessage
from callcentersite.apps.users.models import UserSession

if TYPE_CHECKING:
    from django.http import HttpRequest

User = get_user_model()


class LoginAttemptService:
    """Gestiona intentos de inicio de sesión."""

    @staticmethod
    def register_attempt(
        username: str,
        ip_address: str,
        user_agent: str,
        success: bool,
        reason: str | None = None,
    ) -> None:
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            reason=reason,
        )

    @staticmethod
    def count_recent_failures(username: str, window: timedelta) -> int:
        threshold = timezone.now() - window
        return LoginAttempt.objects.filter(
            username=username, success=False, timestamp__gte=threshold
        ).count()


class AuthenticationService:
    """
    Servicio de autenticación con gestión de sesiones y seguridad.

    Implementa RF-005: Login con Credenciales Locales
    """

    MAX_FAILED_ATTEMPTS = 3
    LOCK_DURATION_MINUTES = 15

    @staticmethod
    def login(
        username: str,
        password: str,
        request: HttpRequest,
    ) -> dict:
        """
        UC-013: Autenticar usuario con credenciales locales.

        Args:
            username: Nombre de usuario
            password: Contraseña
            request: HttpRequest para obtener IP y user agent

        Returns:
            Dict con tokens JWT:
            {
                'access_token': str,
                'refresh_token': str,
                'token_type': 'Bearer',
                'expires_in': 900  # segundos
            }

        Raises:
            PermissionDenied: Si usuario está bloqueado o inactivo
            Exception: Si credenciales son inválidas

        Ejemplo:
            >>> result = AuthenticationService.login(
            ...     username='juan.perez',
            ...     password='SecureP@ss123',
            ...     request=request
            ... )
            >>> print(result['access_token'])
        """
        # Obtener IP y user agent del request
        ip_address = _get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # 1. Intentar obtener usuario (sin revelar si existe o no)
        try:
            user = User.objects.get(username=username)
            user_exists = True
        except User.DoesNotExist:
            user_exists = False
            user = None

        # 2. Si usuario no existe, retornar error genérico
        if not user_exists:
            AuditLog.objects.create(
                user=None,
                event_type='LOGIN_FAILURE',
                result='FAILURE',
                ip_address=ip_address,
                user_agent=user_agent,
                details={'username': username, 'reason': 'usuario_inexistente'}
            )
            raise Exception('Credenciales inválidas')

        # 3. Verificar si usuario está activo
        if user.status != 'ACTIVO':
            AuditLog.objects.create(
                user=user,
                event_type='LOGIN_FAILURE',
                result='FAILURE',
                ip_address=ip_address,
                user_agent=user_agent,
                details={'reason': 'usuario_inactivo'}
            )
            raise PermissionDenied('Usuario inactivo')

        # 4. Verificar si usuario está bloqueado
        if user.is_locked:
            # Verificar si el bloqueo ya expiró (desbloqueo automático)
            if user.locked_until and user.locked_until < timezone.now():
                # Desbloquear automáticamente
                user.is_locked = False
                user.locked_until = None
                user.failed_login_attempts = 0
                user.lock_reason = ''
                user.save(update_fields=[
                    'is_locked', 'locked_until', 'failed_login_attempts', 'lock_reason'
                ])

                # Auditar desbloqueo automático
                AuditLog.objects.create(
                    user=user,
                    event_type='USER_UNLOCKED',
                    result='SUCCESS',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'reason': 'automatic_timeout'}
                )
            else:
                # Usuario sigue bloqueado
                minutes_remaining = int(
                    (user.locked_until - timezone.now()).total_seconds() / 60
                ) if user.locked_until else 0

                AuditLog.objects.create(
                    user=user,
                    event_type='LOGIN_FAILURE',
                    result='FAILURE',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'reason': 'cuenta_bloqueada', 'minutes_remaining': minutes_remaining}
                )
                raise PermissionDenied(f'Cuenta bloqueada. Tiempo restante: {minutes_remaining} minutos')

        # 5. Verificar contraseña
        if not check_password(password, user.password):
            # Contraseña incorrecta - incrementar contador
            user.failed_login_attempts += 1
            user.last_failed_login_at = timezone.now()

            # Verificar si se alcanzó el límite de intentos
            if user.failed_login_attempts >= AuthenticationService.MAX_FAILED_ATTEMPTS:
                # Bloquear usuario
                user.is_locked = True
                user.locked_until = timezone.now() + timedelta(
                    minutes=AuthenticationService.LOCK_DURATION_MINUTES
                )
                user.lock_reason = 'MAX_FAILED_ATTEMPTS'

                user.save(update_fields=[
                    'failed_login_attempts',
                    'last_failed_login_at',
                    'is_locked',
                    'locked_until',
                    'lock_reason'
                ])

                # Auditar bloqueo
                AuditLog.objects.create(
                    user=user,
                    event_type='USER_LOCKED',
                    result='SUCCESS',
                    ip_address=ip_address,
                    user_agent=user_agent,
                    details={'reason': 'max_failed_attempts', 'attempts': user.failed_login_attempts}
                )

                # Enviar notificación al buzón interno
                InternalMessage.objects.create(
                    recipient=user,
                    sender=None,
                    subject='Cuenta bloqueada por seguridad',
                    body=f'Tu cuenta ha sido bloqueada temporalmente por {AuthenticationService.LOCK_DURATION_MINUTES} minutos debido a múltiples intentos fallidos de inicio de sesión.',
                    message_type='alert',
                    priority='high',
                    created_by_system=True
                )

                raise Exception('Cuenta bloqueada por múltiples intentos fallidos')
            else:
                # Solo incrementar contador
                user.save(update_fields=['failed_login_attempts', 'last_failed_login_at'])

            # Auditar intento fallido
            AuditLog.objects.create(
                user=user,
                event_type='LOGIN_FAILURE',
                result='FAILURE',
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'reason': 'credenciales_invalidas',
                    'attempts': user.failed_login_attempts,
                    'attempts_remaining': AuthenticationService.MAX_FAILED_ATTEMPTS - user.failed_login_attempts
                }
            )

            raise Exception('Credenciales inválidas')

        # 6. Credenciales válidas - Login exitoso

        # Cerrar sesiones previas (sesión única)
        previous_sessions = UserSession.objects.filter(user=user, is_active=True)
        for session in previous_sessions:
            session.close(reason='NEW_SESSION')

            # Auditar cierre de sesión previa
            AuditLog.objects.create(
                user=user,
                event_type='SESSION_CLOSED',
                result='SUCCESS',
                ip_address=ip_address,
                user_agent=user_agent,
                details={'reason': 'new_session', 'old_session': session.session_key[:8]}
            )

            # Notificar sobre nueva sesión
            InternalMessage.objects.create(
                recipient=user,
                sender=None,
                subject='Nueva sesión iniciada',
                body=f'Se ha iniciado una nueva sesión en tu cuenta. Si no fuiste tú, contacta al administrador.',
                message_type='info',
                priority='medium',
                created_by_system=True
            )

        # Resetear contador de intentos fallidos
        user.failed_login_attempts = 0
        user.last_failed_login_at = None
        user.last_login_at = timezone.now()
        user.last_login_ip = ip_address
        user.save(update_fields=[
            'failed_login_attempts',
            'last_failed_login_at',
            'last_login_at',
            'last_login_ip'
        ])

        # Crear nueva sesión
        # Manejar request.session que puede no existir en tests
        if hasattr(request, 'session') and request.session:
            session_key = request.session.get('session_key', '') or f'session_{user.id}_{timezone.now().timestamp()}'
        else:
            session_key = f'session_{user.id}_{timezone.now().timestamp()}'

        UserSession.objects.create(
            user=user,
            session_key=session_key,
            is_active=True,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Auditar login exitoso
        AuditLog.objects.create(
            user=user,
            event_type='LOGIN_SUCCESS',
            result='SUCCESS',
            ip_address=ip_address,
            user_agent=user_agent,
            details={'session_key': session_key[:8]}
        )

        # Retornar tokens
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 900  # 15 minutos en segundos
        }


def _get_client_ip(request: HttpRequest) -> str:
    """Extrae la IP del cliente desde el request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
