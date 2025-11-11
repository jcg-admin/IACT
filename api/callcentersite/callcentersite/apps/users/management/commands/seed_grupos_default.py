"""
Management command para crear grupos de permisos por defecto.

Crea 4 grupos con permisos típicos de un call center:
1. Agentes Nivel 1 - Permisos básicos de visualización
2. Agentes Nivel 2 - Agentes con más permisos
3. Coordinadores - Gestión de equipos y reportes
4. Administradores - Permisos completos del sistema

Uso:
    python manage.py seed_grupos_default
    python manage.py seed_grupos_default --reset

Idempotente: Se puede ejecutar múltiples veces.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from callcentersite.apps.users.models_permisos_granular import (
    GrupoPermiso,
    Capacidad,
)


class Command(BaseCommand):
    help = 'Crea grupos de permisos por defecto del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina grupos existentes antes de crear',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options['reset']

        if reset:
            self.stdout.write(self.style.WARNING('Eliminando grupos existentes...'))
            GrupoPermiso.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Grupos eliminados'))

        self.stdout.write('Creando grupos por defecto...')

        grupos_creados = 0
        grupos_creados += self._crear_grupo_agentes_nivel_1()
        grupos_creados += self._crear_grupo_agentes_nivel_2()
        grupos_creados += self._crear_grupo_coordinadores()
        grupos_creados += self._crear_grupo_administradores()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Grupos creados: {grupos_creados}\n'
            )
        )

    def _crear_grupo_agentes_nivel_1(self):
        """Crea grupo de Agentes Nivel 1 con permisos básicos."""
        grupo, created = GrupoPermiso.objects.get_or_create(
            codigo='agentes_nivel_1',
            defaults={
                'nombre': 'Agentes Nivel 1',
                'descripcion': 'Agentes con permisos básicos de visualización',
                'activo': True,
            }
        )

        if not created:
            self.stdout.write(f'  - Grupo ya existe: {grupo.codigo}')
            return 0

        # Capacidades para agentes nivel 1
        capacidades_codigos = [
            'sistema.vistas.dashboards.ver',
            'sistema.vistas.reportes.ver',
        ]

        capacidades = Capacidad.objects.filter(
            codigo__in=capacidades_codigos,
            activa=True
        )

        grupo.capacidades.set(capacidades)

        self.stdout.write(
            self.style.SUCCESS(
                f'  + Grupo creado: {grupo.nombre} ({capacidades.count()} capacidades)'
            )
        )
        return 1

    def _crear_grupo_agentes_nivel_2(self):
        """Crea grupo de Agentes Nivel 2 con más permisos."""
        grupo, created = GrupoPermiso.objects.get_or_create(
            codigo='agentes_nivel_2',
            defaults={
                'nombre': 'Agentes Nivel 2',
                'descripcion': 'Agentes con permisos ampliados (crear reportes, exportar)',
                'activo': True,
            }
        )

        if not created:
            self.stdout.write(f'  - Grupo ya existe: {grupo.codigo}')
            return 0

        capacidades_codigos = [
            # Todo lo de Nivel 1
            'sistema.vistas.dashboards.ver',
            'sistema.vistas.reportes.ver',
            # Adicionales
            'sistema.vistas.reportes.crear',
            'sistema.vistas.reportes.exportar',
            'sistema.vistas.analisis.ver',
        ]

        capacidades = Capacidad.objects.filter(
            codigo__in=capacidades_codigos,
            activa=True
        )

        grupo.capacidades.set(capacidades)

        self.stdout.write(
            self.style.SUCCESS(
                f'  + Grupo creado: {grupo.nombre} ({capacidades.count()} capacidades)'
            )
        )
        return 1

    def _crear_grupo_coordinadores(self):
        """Crea grupo de Coordinadores con permisos de gestión."""
        grupo, created = GrupoPermiso.objects.get_or_create(
            codigo='coordinadores',
            defaults={
                'nombre': 'Coordinadores',
                'descripcion': 'Coordinadores con gestión de equipos, calidad y reportes completos',
                'activo': True,
            }
        )

        if not created:
            self.stdout.write(f'  - Grupo ya existe: {grupo.codigo}')
            return 0

        capacidades_codigos = [
            # Dashboards
            'sistema.vistas.dashboards.ver',
            'sistema.vistas.dashboards.editar',
            'sistema.vistas.dashboards.compartir',
            # Reportes completos
            'sistema.vistas.reportes.ver',
            'sistema.vistas.reportes.crear',
            'sistema.vistas.reportes.editar',
            'sistema.vistas.reportes.eliminar',
            'sistema.vistas.reportes.exportar',
            # Calidad
            'sistema.vistas.calidad.ver',
            'sistema.vistas.calidad.evaluar',
            'sistema.vistas.calidad.aprobar',
            # Equipos
            'sistema.vistas.equipos.ver',
            'sistema.vistas.equipos.gestionar',
            # Análisis
            'sistema.vistas.analisis.ver',
            'sistema.vistas.analisis.avanzados',
        ]

        capacidades = Capacidad.objects.filter(
            codigo__in=capacidades_codigos,
            activa=True
        )

        grupo.capacidades.set(capacidades)

        self.stdout.write(
            self.style.SUCCESS(
                f'  + Grupo creado: {grupo.nombre} ({capacidades.count()} capacidades)'
            )
        )
        return 1

    def _crear_grupo_administradores(self):
        """Crea grupo de Administradores con TODOS los permisos."""
        grupo, created = GrupoPermiso.objects.get_or_create(
            codigo='administradores',
            defaults={
                'nombre': 'Administradores',
                'descripcion': 'Administradores del sistema con acceso completo',
                'activo': True,
            }
        )

        if not created:
            self.stdout.write(f'  - Grupo ya existe: {grupo.codigo}')
            return 0

        # Administradores tienen TODAS las capacidades
        capacidades = Capacidad.objects.filter(activa=True)

        grupo.capacidades.set(capacidades)

        self.stdout.write(
            self.style.SUCCESS(
                f'  + Grupo creado: {grupo.nombre} ({capacidades.count()} capacidades - TODAS)'
            )
        )
        return 1
