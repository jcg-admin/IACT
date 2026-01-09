"""
Management command para crear usuarios de demostración con grupos asignados.

Crea 5 usuarios de ejemplo:
1. admin - Administrador del sistema
2. coord1 - Coordinador de equipo
3. agente1 - Agente nivel 1
4. agente2 - Agente nivel 2
5. analista1 - Analista de calidad (coordinador)

Todos con password: "demo123456"

Uso:
    python manage.py seed_usuarios_demo
    python manage.py seed_usuarios_demo --reset
    python manage.py seed_usuarios_demo --password "custom123"

Idempotente: Se puede ejecutar múltiples veces.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from callcentersite.apps.users.models_permisos_granular import (
    GrupoPermiso,
    UsuarioGrupo,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea usuarios de demostración con grupos asignados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina usuarios demo existentes antes de crear',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='demo123456',
            help='Password para todos los usuarios demo (default: demo123456)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options['reset']
        password = options['password']

        if reset:
            self.stdout.write(self.style.WARNING('Eliminando usuarios demo existentes...'))
            User.objects.filter(username__in=[
                'admin_demo',
                'coord1_demo',
                'agente1_demo',
                'agente2_demo',
                'analista1_demo',
            ]).delete()
            self.stdout.write(self.style.SUCCESS('Usuarios eliminados'))

        self.stdout.write(f'Creando usuarios demo (password: {password})...')

        usuarios_creados = 0

        # Obtener o crear un admin base para asignar grupos
        admin_asignador, _ = User.objects.get_or_create(
            username='system_admin',
            defaults={
                'email': 'system@callcenter.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if not admin_asignador.has_usable_password():
            admin_asignador.set_password('admin')
            admin_asignador.save()

        usuarios_creados += self._crear_usuario_admin(password, admin_asignador)
        usuarios_creados += self._crear_usuario_coordinador(password, admin_asignador)
        usuarios_creados += self._crear_usuario_agente_1(password, admin_asignador)
        usuarios_creados += self._crear_usuario_agente_2(password, admin_asignador)
        usuarios_creados += self._crear_usuario_analista(password, admin_asignador)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Usuarios demo creados: {usuarios_creados}\n\n'
                f'Credenciales:\n'
                f'  - admin_demo / {password} (Administrador)\n'
                f'  - coord1_demo / {password} (Coordinador)\n'
                f'  - agente1_demo / {password} (Agente Nivel 1)\n'
                f'  - agente2_demo / {password} (Agente Nivel 2)\n'
                f'  - analista1_demo / {password} (Analista Calidad)\n'
            )
        )

    def _crear_usuario_admin(self, password, asignador):
        """Crea usuario administrador demo."""
        user, created = User.objects.get_or_create(
            username='admin_demo',
            defaults={
                'email': 'admin@demo.com',
                'is_staff': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  + Usuario creado: {user.username}')
        else:
            self.stdout.write(f'  - Usuario ya existe: {user.username}')
            return 0

        # Asignar grupo Administradores
        try:
            grupo = GrupoPermiso.objects.get(codigo='administradores')
            UsuarioGrupo.objects.get_or_create(
                usuario=user,
                grupo=grupo,
                defaults={
                    'asignado_por': asignador,
                    'activo': True,
                    'motivo': 'Usuario demo - Administrador del sistema',
                }
            )
            self.stdout.write(f'    → Asignado al grupo: {grupo.nombre}')
        except GrupoPermiso.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f'    ! Grupo "administradores" no encontrado. '
                    f'Ejecuta: python manage.py seed_grupos_default'
                )
            )

        return 1

    def _crear_usuario_coordinador(self, password, asignador):
        """Crea usuario coordinador demo."""
        user, created = User.objects.get_or_create(
            username='coord1_demo',
            defaults={
                'email': 'coord1@demo.com',
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  + Usuario creado: {user.username}')
        else:
            self.stdout.write(f'  - Usuario ya existe: {user.username}')
            return 0

        try:
            grupo = GrupoPermiso.objects.get(codigo='coordinadores')
            UsuarioGrupo.objects.get_or_create(
                usuario=user,
                grupo=grupo,
                defaults={
                    'asignado_por': asignador,
                    'activo': True,
                    'motivo': 'Usuario demo - Coordinador de equipo',
                }
            )
            self.stdout.write(f'    → Asignado al grupo: {grupo.nombre}')
        except GrupoPermiso.DoesNotExist:
            self.stdout.write(self.style.WARNING('    ! Grupo "coordinadores" no encontrado'))

        return 1

    def _crear_usuario_agente_1(self, password, asignador):
        """Crea usuario agente nivel 1 demo."""
        user, created = User.objects.get_or_create(
            username='agente1_demo',
            defaults={
                'email': 'agente1@demo.com',
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  + Usuario creado: {user.username}')
        else:
            self.stdout.write(f'  - Usuario ya existe: {user.username}')
            return 0

        try:
            grupo = GrupoPermiso.objects.get(codigo='agentes_nivel_1')
            UsuarioGrupo.objects.get_or_create(
                usuario=user,
                grupo=grupo,
                defaults={
                    'asignado_por': asignador,
                    'activo': True,
                    'motivo': 'Usuario demo - Agente de atención básico',
                }
            )
            self.stdout.write(f'    → Asignado al grupo: {grupo.nombre}')
        except GrupoPermiso.DoesNotExist:
            self.stdout.write(self.style.WARNING('    ! Grupo "agentes_nivel_1" no encontrado'))

        return 1

    def _crear_usuario_agente_2(self, password, asignador):
        """Crea usuario agente nivel 2 demo."""
        user, created = User.objects.get_or_create(
            username='agente2_demo',
            defaults={
                'email': 'agente2@demo.com',
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  + Usuario creado: {user.username}')
        else:
            self.stdout.write(f'  - Usuario ya existe: {user.username}')
            return 0

        try:
            grupo = GrupoPermiso.objects.get(codigo='agentes_nivel_2')
            UsuarioGrupo.objects.get_or_create(
                usuario=user,
                grupo=grupo,
                defaults={
                    'asignado_por': asignador,
                    'activo': True,
                    'motivo': 'Usuario demo - Agente con permisos ampliados',
                }
            )
            self.stdout.write(f'    → Asignado al grupo: {grupo.nombre}')
        except GrupoPermiso.DoesNotExist:
            self.stdout.write(self.style.WARNING('    ! Grupo "agentes_nivel_2" no encontrado'))

        return 1

    def _crear_usuario_analista(self, password, asignador):
        """Crea usuario analista de calidad demo."""
        user, created = User.objects.get_or_create(
            username='analista1_demo',
            defaults={
                'email': 'analista1@demo.com',
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'  + Usuario creado: {user.username}')
        else:
            self.stdout.write(f'  - Usuario ya existe: {user.username}')
            return 0

        try:
            grupo = GrupoPermiso.objects.get(codigo='coordinadores')
            UsuarioGrupo.objects.get_or_create(
                usuario=user,
                grupo=grupo,
                defaults={
                    'asignado_por': asignador,
                    'activo': True,
                    'motivo': 'Usuario demo - Analista de calidad',
                }
            )
            self.stdout.write(f'    → Asignado al grupo: {grupo.nombre}')
        except GrupoPermiso.DoesNotExist:
            self.stdout.write(self.style.WARNING('    ! Grupo "coordinadores" no encontrado'))

        return 1
