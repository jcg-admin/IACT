"""Middleware para reforzar seguridad de sesiones."""

from __future__ import annotations

from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse

SESSION_IP_KEY = "session_ip"
SESSION_UA_KEY = "session_user_agent"


def _extract_client_ip(request: HttpRequest) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _extract_user_agent(request: HttpRequest) -> str:
    return request.META.get("HTTP_USER_AGENT", "")


class SessionSecurityMiddleware:
    """Invalida sesiones cuando cambia IP o user agent."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            session = request.session
            client_ip = _extract_client_ip(request)
            user_agent = _extract_user_agent(request)

            stored_ip = session.get(SESSION_IP_KEY)
            stored_user_agent = session.get(SESSION_UA_KEY)

            if stored_ip is None:
                session[SESSION_IP_KEY] = client_ip
            if stored_user_agent is None:
                session[SESSION_UA_KEY] = user_agent

            invalid_session = False

            if stored_ip and stored_ip != client_ip:
                invalid_session = True
            elif stored_user_agent and stored_user_agent != user_agent:
                invalid_session = True

            if invalid_session:
                logout(request)
                request.session.flush()
                response = HttpResponse(status=401)
                response["Cache-Control"] = "no-store"
                response["WWW-Authenticate"] = "Bearer"
                return response

        response = self.get_response(request)
        return response
