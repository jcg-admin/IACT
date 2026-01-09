"""Configuración del admin para el modelo User."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para el modelo User."""

    list_display = (
        'username',
        'email',
        'is_active',
        'status',
        'is_locked',
        'is_deleted',
        'created_at',
    )
    list_filter = (
        'is_active',
        'status',
        'is_locked',
        'is_deleted',
        'is_staff',
        'is_superuser',
        'created_at',
    )
    search_fields = ('username', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'last_login_at')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('email', 'segment')}),
        (
            _('Permisos'),
            {
                'fields': (
                    'is_active',
                    'status',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            _('Seguridad y bloqueo'),
            {
                'fields': (
                    'is_locked',
                    'locked_until',
                    'lock_reason',
                    'failed_login_attempts',
                    'last_failed_login_at',
                    'last_login_ip',
                    'last_login_at',
                )
            },
        ),
        (
            _('Borrado lógico'),
            {
                'fields': ('is_deleted', 'deleted_at')
            },
        ),
        (
            _('Fechas importantes'),
            {
                'fields': ('created_at', 'updated_at')
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'is_active',
                    'status',
                    'is_staff',
                    'is_superuser',
                ),
            },
        ),
    )

    autocomplete_fields = []  # User no tiene relaciones que necesiten autocomplete
