"""
API Rate Limiting - Django REST Framework Throttling

Limites por usuario/IP para prevenir abuso de APIs.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstRateThrottle(AnonRateThrottle):
    """Short-term burst limiting (100/min)."""
    scope = 'burst'
    rate = '100/min'


class SustainedRateThrottle(AnonRateThrottle):
    """Long-term sustained limiting (1000/hour)."""
    scope = 'sustained'
    rate = '1000/hour'


class UserBurstRateThrottle(UserRateThrottle):
    """Authenticated users burst (200/min)."""
    scope = 'user_burst'
    rate = '200/min'


class UserSustainedRateThrottle(UserRateThrottle):
    """Authenticated users sustained (5000/hour)."""
    scope = 'user_sustained'
    rate = '5000/hour'
