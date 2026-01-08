"""
Management command maestro que ejecuta todos los seeders en orden correcto.

Ejecuta en secuencia:
1. seed_permisos_base - Crea funciones y capacidades
2. seed_grupos_default - Crea grupos con capacidades asignadas
3. seed_usuarios_demo - Crea usuarios con grupos asignados

Uso:
    python manage.py seed_permisos_completo
    python manage.py seed_permisos_completo --reset  # Elimina todo y recrea
    python manage.py seed_permisos_completo --skip-usuarios  # Solo permisos y grupos

Este comando es ideal para:
- Inicialización rápida de desarrollo
- Restaurar datos de prueba
- Demos del sistema
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Ejecuta todos los seeders de permisos en orden correcto'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina todos los datos existentes antes de crear',
        )
        parser.add_argument(
            '--skip-usuarios',
            action='store_true',
            help='No crear usuarios demo',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='demo123456',
            help='Password para usuarios demo (default: demo123456)',
        )

    def handle(self, *args, **options):
        reset = options['reset']
        skip_usuarios = options['skip_usuarios']
        password = options['password']

        self.stdout.write(
            self.style.SUCCESS(
                '\n'
                '================================================================\n'
                '  SEEDING COMPLETO - SISTEMA DE PERMISOS GRANULARES\n'
                '================================================================\n'
            )
        )

        # FASE 1: Funciones y Capacidades Base
        self.stdout.write('\n[1/3] Creando funciones y capacidades base...\n')
        try:
            if reset:
                call_command('seed_permisos_base', '--reset', verbosity=1)
            else:
                call_command('seed_permisos_base', verbosity=1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n[FAIL] Error en seed_permisos_base: {e}')
            )
            return

        # FASE 2: Grupos por Defecto
        self.stdout.write('\n[2/3] Creando grupos de permisos por defecto...\n')
        try:
            if reset:
                call_command('seed_grupos_default', '--reset', verbosity=1)
            else:
                call_command('seed_grupos_default', verbosity=1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n[FAIL] Error en seed_grupos_default: {e}')
            )
            return

        # FASE 3: Usuarios Demo (opcional)
        if not skip_usuarios:
            self.stdout.write('\n[3/3] Creando usuarios de demostración...\n')
            try:
                if reset:
                    call_command('seed_usuarios_demo', '--reset', '--password', password, verbosity=1)
                else:
                    call_command('seed_usuarios_demo', '--password', password, verbosity=1)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'\n[FAIL] Error en seed_usuarios_demo: {e}')
                )
                return
        else:
            self.stdout.write(
                self.style.WARNING('\n[3/3] OMITIDO: Usuarios demo (--skip-usuarios)\n')
            )

        # RESUMEN FINAL
        self.stdout.write(
            self.style.SUCCESS(
                '\n'
                '================================================================\n'
                '  [OK] SEEDING COMPLETADO EXITOSAMENTE\n'
                '================================================================\n'
                '\n'
                'Sistema de Permisos Granulares inicializado con:\n'
                '\n'
                '  FUNCIONES:\n'
                '    • sistema.vistas.dashboards\n'
                '    • sistema.vistas.reportes\n'
                '    • sistema.vistas.calidad\n'
                '    • sistema.vistas.equipos\n'
                '    • sistema.vistas.analisis\n'
                '    • sistema.administracion.usuarios\n'
                '    • sistema.administracion.grupos\n'
                '    • sistema.administracion.permisos\n'
                '    • sistema.administracion.auditoria\n'
                '    • sistema.administracion.configuracion\n'
                '\n'
                '  CAPACIDADES: ~32 capacidades base\n'
                '\n'
                '  GRUPOS:\n'
                '    • agentes_nivel_1 (2 capacidades)\n'
                '    • agentes_nivel_2 (5 capacidades)\n'
                '    • coordinadores (14+ capacidades)\n'
                '    • administradores (TODAS las capacidades)\n'
            )
        )

        if not skip_usuarios:
            self.stdout.write(
                self.style.SUCCESS(
                    '\n'
                    '  USUARIOS DEMO:\n'
                    f'    • admin_demo / {password} (Administrador)\n'
                    f'    • coord1_demo / {password} (Coordinador)\n'
                    f'    • agente1_demo / {password} (Agente Nivel 1)\n'
                    f'    • agente2_demo / {password} (Agente Nivel 2)\n'
                    f'    • analista1_demo / {password} (Analista Calidad)\n'
                    '\n'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                'PRÓXIMOS PASOS:\n'
                '\n'
                '  1. Verificar datos creados:\n'
                '     python manage.py shell\n'
                '     >>> from callcentersite.apps.users.models_permisos_granular import *\n'
                '     >>> GrupoPermiso.objects.count()  # Debe ser 4\n'
                '     >>> Capacidad.objects.count()  # Debe ser ~32\n'
                '\n'
                '  2. Probar API:\n'
                '     curl -X POST http://localhost:8000/api/v1/auth/login/ \\\n'
                '       -d "username=admin_demo&password=' + password + '"\n'
                '\n'
                '  3. Probar verificación de permisos:\n'
                '     python manage.py shell\n'
                '     >>> from django.contrib.auth import get_user_model\n'
                '     >>> user = get_user_model().objects.get(username="agente1_demo")\n'
                '     >>> from callcentersite.apps.users.services_permisos_granular import *\n'
                '     >>> UserManagementService.usuario_tiene_permiso(\n'
                '     ...     user.id, "sistema.vistas.dashboards.ver")\n'
                '     True\n'
                '\n'
                '================================================================\n'
            )
        )
