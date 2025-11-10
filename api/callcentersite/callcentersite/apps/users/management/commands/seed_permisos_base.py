"""
Management command para crear funciones y capacidades base del sistema.

Uso:
    python manage.py seed_permisos_base
    python manage.py seed_permisos_base --reset  # Elimina y recrea

Idempotente: Se puede ejecutar múltiples veces sin duplicar datos.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from callcentersite.apps.users.models_permisos_granular import Funcion, Capacidad


class Command(BaseCommand):
    help = 'Crea funciones y capacidades base del sistema de permisos granulares'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina capacidades y funciones existentes antes de crear',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options['reset']

        if reset:
            self.stdout.write(self.style.WARNING('Eliminando funciones y capacidades existentes...'))
            Capacidad.objects.all().delete()
            Funcion.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Datos eliminados'))

        self.stdout.write('Creando funciones base...')
        funciones_creadas = self._crear_funciones()

        self.stdout.write('Creando capacidades base...')
        capacidades_creadas = self._crear_capacidades()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Seeding completado:\n'
                f'  - Funciones: {funciones_creadas}\n'
                f'  - Capacidades: {capacidades_creadas}'
            )
        )

    def _crear_funciones(self):
        """Crea funciones base del sistema."""
        funciones_data = [
            # VISTAS
            {
                'codigo': 'vistas.dashboards',
                'nombre': 'Dashboards',
                'descripcion': 'Visualización de paneles de control e indicadores',
                'dominio': 'vistas',
            },
            {
                'codigo': 'vistas.reportes',
                'nombre': 'Reportes',
                'descripcion': 'Generación y visualización de reportes',
                'dominio': 'vistas',
            },
            {
                'codigo': 'vistas.calidad',
                'nombre': 'Calidad',
                'descripcion': 'Evaluación y gestión de calidad de llamadas',
                'dominio': 'vistas',
            },
            {
                'codigo': 'vistas.equipos',
                'nombre': 'Equipos',
                'descripcion': 'Gestión y visualización de equipos de trabajo',
                'dominio': 'vistas',
            },
            {
                'codigo': 'vistas.analisis',
                'nombre': 'Análisis',
                'descripcion': 'Análisis avanzados y métricas',
                'dominio': 'vistas',
            },
            # ADMINISTRACIÓN
            {
                'codigo': 'administracion.usuarios',
                'nombre': 'Gestión de Usuarios',
                'descripcion': 'Administración completa de usuarios del sistema',
                'dominio': 'administracion',
            },
            {
                'codigo': 'administracion.grupos',
                'nombre': 'Gestión de Grupos',
                'descripcion': 'Administración de grupos de permisos',
                'dominio': 'administracion',
            },
            {
                'codigo': 'administracion.permisos',
                'nombre': 'Gestión de Permisos',
                'descripcion': 'Administración de capacidades y permisos excepcionales',
                'dominio': 'administracion',
            },
            {
                'codigo': 'administracion.auditoria',
                'nombre': 'Auditoría',
                'descripcion': 'Consulta de logs y auditoría del sistema',
                'dominio': 'administracion',
            },
            {
                'codigo': 'administracion.configuracion',
                'nombre': 'Configuración',
                'descripcion': 'Configuración general del sistema',
                'dominio': 'administracion',
            },
        ]

        creadas = 0
        for func_data in funciones_data:
            funcion, created = Funcion.objects.get_or_create(
                codigo=func_data['codigo'],
                defaults={
                    'nombre': func_data['nombre'],
                    'descripcion': func_data['descripcion'],
                    'dominio': func_data['dominio'],
                    'activa': True,
                }
            )
            if created:
                creadas += 1
                self.stdout.write(f'  + Función creada: {funcion.codigo}')
            else:
                self.stdout.write(f'  - Función ya existe: {funcion.codigo}')

        return creadas

    def _crear_capacidades(self):
        """Crea capacidades base asociadas a funciones."""
        capacidades_data = [
            # DASHBOARDS
            ('sistema.vistas.dashboards.ver', 'Ver Dashboards', 'vistas.dashboards'),
            ('sistema.vistas.dashboards.editar', 'Editar Dashboards', 'vistas.dashboards'),
            ('sistema.vistas.dashboards.compartir', 'Compartir Dashboards', 'vistas.dashboards'),

            # REPORTES
            ('sistema.vistas.reportes.ver', 'Ver Reportes', 'vistas.reportes'),
            ('sistema.vistas.reportes.crear', 'Crear Reportes', 'vistas.reportes'),
            ('sistema.vistas.reportes.editar', 'Editar Reportes', 'vistas.reportes'),
            ('sistema.vistas.reportes.eliminar', 'Eliminar Reportes', 'vistas.reportes'),
            ('sistema.vistas.reportes.exportar', 'Exportar Reportes', 'vistas.reportes'),

            # CALIDAD
            ('sistema.vistas.calidad.ver', 'Ver Evaluaciones de Calidad', 'vistas.calidad'),
            ('sistema.vistas.calidad.evaluar', 'Realizar Evaluaciones', 'vistas.calidad'),
            ('sistema.vistas.calidad.aprobar', 'Aprobar Evaluaciones', 'vistas.calidad'),

            # EQUIPOS
            ('sistema.vistas.equipos.ver', 'Ver Equipos', 'vistas.equipos'),
            ('sistema.vistas.equipos.gestionar', 'Gestionar Equipos', 'vistas.equipos'),

            # ANÁLISIS
            ('sistema.vistas.analisis.ver', 'Ver Análisis', 'vistas.analisis'),
            ('sistema.vistas.analisis.avanzados', 'Análisis Avanzados', 'vistas.analisis'),

            # USUARIOS
            ('sistema.administracion.usuarios.ver', 'Ver Usuarios', 'administracion.usuarios'),
            ('sistema.administracion.usuarios.crear', 'Crear Usuarios', 'administracion.usuarios'),
            ('sistema.administracion.usuarios.editar', 'Editar Usuarios', 'administracion.usuarios'),
            ('sistema.administracion.usuarios.eliminar', 'Eliminar Usuarios', 'administracion.usuarios'),
            ('sistema.administracion.usuarios.restablecer_password', 'Restablecer Contraseñas', 'administracion.usuarios'),

            # GRUPOS
            ('sistema.administracion.grupos.ver', 'Ver Grupos', 'administracion.grupos'),
            ('sistema.administracion.grupos.crear', 'Crear Grupos', 'administracion.grupos'),
            ('sistema.administracion.grupos.editar', 'Editar Grupos', 'administracion.grupos'),
            ('sistema.administracion.grupos.eliminar', 'Eliminar Grupos', 'administracion.grupos'),

            # PERMISOS
            ('sistema.administracion.permisos.ver', 'Ver Permisos', 'administracion.permisos'),
            ('sistema.administracion.permisos.excepcionales.conceder', 'Conceder Permisos Excepcionales', 'administracion.permisos'),
            ('sistema.administracion.permisos.excepcionales.revocar', 'Revocar Permisos Excepcionales', 'administracion.permisos'),

            # AUDITORÍA
            ('sistema.administracion.auditoria.ver', 'Ver Auditoría', 'administracion.auditoria'),
            ('sistema.administracion.auditoria.exportar', 'Exportar Auditoría', 'administracion.auditoria'),

            # CONFIGURACIÓN
            ('sistema.administracion.configuracion.ver', 'Ver Configuración', 'administracion.configuracion'),
            ('sistema.administracion.configuracion.editar', 'Editar Configuración', 'administracion.configuracion'),
        ]

        creadas = 0
        for codigo, nombre, funcion_codigo in capacidades_data:
            try:
                funcion = Funcion.objects.get(codigo=funcion_codigo)
            except Funcion.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ! Función no encontrada: {funcion_codigo}')
                )
                continue

            capacidad, created = Capacidad.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': f'Capacidad para {nombre.lower()}',
                    'activa': True,
                }
            )

            if created:
                # Asociar capacidad a función
                funcion.capacidades.add(capacidad)
                creadas += 1
                self.stdout.write(f'  + Capacidad creada: {capacidad.codigo}')
            else:
                # Asegurar asociación
                if not funcion.capacidades.filter(id=capacidad.id).exists():
                    funcion.capacidades.add(capacidad)
                self.stdout.write(f'  - Capacidad ya existe: {capacidad.codigo}')

        return creadas
