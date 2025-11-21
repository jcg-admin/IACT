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
                'nombre_completo': 'sistema.vistas.dashboards',
                'nombre': 'Dashboards',
                'descripcion': 'Visualización de paneles de control e indicadores',
                'dominio': 'vistas',
                'categoria': 'vistas',
            },
            {
                'nombre_completo': 'sistema.vistas.reportes',
                'nombre': 'Reportes',
                'descripcion': 'Generación y visualización de reportes',
                'dominio': 'vistas',
                'categoria': 'vistas',
            },
            {
                'nombre_completo': 'sistema.vistas.calidad',
                'nombre': 'Calidad',
                'descripcion': 'Evaluación y gestión de calidad de llamadas',
                'dominio': 'vistas',
                'categoria': 'vistas',
            },
            {
                'nombre_completo': 'sistema.vistas.equipos',
                'nombre': 'Equipos',
                'descripcion': 'Gestión y visualización de equipos de trabajo',
                'dominio': 'vistas',
                'categoria': 'vistas',
            },
            {
                'nombre_completo': 'sistema.vistas.analisis',
                'nombre': 'Análisis',
                'descripcion': 'Análisis avanzados y métricas',
                'dominio': 'vistas',
                'categoria': 'vistas',
            },
            # ADMINISTRACIÓN
            {
                'nombre_completo': 'sistema.administracion.usuarios',
                'nombre': 'Gestión de Usuarios',
                'descripcion': 'Administración completa de usuarios del sistema',
                'dominio': 'administracion',
                'categoria': 'administracion',
            },
            {
                'nombre_completo': 'sistema.administracion.grupos',
                'nombre': 'Gestión de Grupos',
                'descripcion': 'Administración de grupos de permisos',
                'dominio': 'administracion',
                'categoria': 'administracion',
            },
            {
                'nombre_completo': 'sistema.administracion.permisos',
                'nombre': 'Gestión de Permisos',
                'descripcion': 'Administración de capacidades y permisos excepcionales',
                'dominio': 'administracion',
                'categoria': 'administracion',
            },
            {
                'nombre_completo': 'sistema.administracion.auditoria',
                'nombre': 'Auditoría',
                'descripcion': 'Consulta de logs y auditoría del sistema',
                'dominio': 'administracion',
                'categoria': 'administracion',
            },
            {
                'nombre_completo': 'sistema.administracion.configuracion',
                'nombre': 'Configuración',
                'descripcion': 'Configuración general del sistema',
                'dominio': 'administracion',
                'categoria': 'administracion',
            },
        ]

        creadas = 0
        for func_data in funciones_data:
            funcion, created = Funcion.objects.get_or_create(
                nombre_completo=func_data['nombre_completo'],
                defaults={
                    'nombre': func_data['nombre'],
                    'descripcion': func_data['descripcion'],
                    'dominio': func_data['dominio'],
                    'categoria': func_data['categoria'],
                    'activa': True,
                }
            )
            if created:
                creadas += 1
                self.stdout.write(f'  + Función creada: {funcion.nombre_completo}')
            else:
                self.stdout.write(f'  - Función ya existe: {funcion.nombre_completo}')

        return creadas

    def _crear_capacidades(self):
        """Crea capacidades base asociadas a funciones."""
        capacidades_data = [
            # DASHBOARDS
            ('sistema.vistas.dashboards.ver', 'Ver Dashboards', 'sistema.vistas.dashboards'),
            ('sistema.vistas.dashboards.editar', 'Editar Dashboards', 'sistema.vistas.dashboards'),
            ('sistema.vistas.dashboards.compartir', 'Compartir Dashboards', 'sistema.vistas.dashboards'),

            # REPORTES
            ('sistema.vistas.reportes.ver', 'Ver Reportes', 'sistema.vistas.reportes'),
            ('sistema.vistas.reportes.crear', 'Crear Reportes', 'sistema.vistas.reportes'),
            ('sistema.vistas.reportes.editar', 'Editar Reportes', 'sistema.vistas.reportes'),
            ('sistema.vistas.reportes.eliminar', 'Eliminar Reportes', 'sistema.vistas.reportes'),
            ('sistema.vistas.reportes.exportar', 'Exportar Reportes', 'sistema.vistas.reportes'),

            # CALIDAD
            ('sistema.vistas.calidad.ver', 'Ver Evaluaciones de Calidad', 'sistema.vistas.calidad'),
            ('sistema.vistas.calidad.evaluar', 'Realizar Evaluaciones', 'sistema.vistas.calidad'),
            ('sistema.vistas.calidad.aprobar', 'Aprobar Evaluaciones', 'sistema.vistas.calidad'),

            # EQUIPOS
            ('sistema.vistas.equipos.ver', 'Ver Equipos', 'sistema.vistas.equipos'),
            ('sistema.vistas.equipos.gestionar', 'Gestionar Equipos', 'sistema.vistas.equipos'),

            # ANÁLISIS
            ('sistema.vistas.analisis.ver', 'Ver Análisis', 'sistema.vistas.analisis'),
            ('sistema.vistas.analisis.avanzados', 'Análisis Avanzados', 'sistema.vistas.analisis'),

            # USUARIOS
            ('sistema.administracion.usuarios.ver', 'Ver Usuarios', 'sistema.administracion.usuarios'),
            ('sistema.administracion.usuarios.crear', 'Crear Usuarios', 'sistema.administracion.usuarios'),
            ('sistema.administracion.usuarios.editar', 'Editar Usuarios', 'sistema.administracion.usuarios'),
            ('sistema.administracion.usuarios.eliminar', 'Eliminar Usuarios', 'sistema.administracion.usuarios'),
            ('sistema.administracion.usuarios.restablecer_password', 'Restablecer Contraseñas', 'sistema.administracion.usuarios'),

            # GRUPOS
            ('sistema.administracion.grupos.ver', 'Ver Grupos', 'sistema.administracion.grupos'),
            ('sistema.administracion.grupos.crear', 'Crear Grupos', 'sistema.administracion.grupos'),
            ('sistema.administracion.grupos.editar', 'Editar Grupos', 'sistema.administracion.grupos'),
            ('sistema.administracion.grupos.eliminar', 'Eliminar Grupos', 'sistema.administracion.grupos'),

            # PERMISOS
            ('sistema.administracion.permisos.ver', 'Ver Permisos', 'sistema.administracion.permisos'),
            ('sistema.administracion.permisos.excepcionales.conceder', 'Conceder Permisos Excepcionales', 'sistema.administracion.permisos'),
            ('sistema.administracion.permisos.excepcionales.revocar', 'Revocar Permisos Excepcionales', 'sistema.administracion.permisos'),

            # AUDITORÍA
            ('sistema.administracion.auditoria.ver', 'Ver Auditoría', 'sistema.administracion.auditoria'),
            ('sistema.administracion.auditoria.exportar', 'Exportar Auditoría', 'sistema.administracion.auditoria'),

            # CONFIGURACIÓN
            ('sistema.administracion.configuracion.ver', 'Ver Configuración', 'sistema.administracion.configuracion'),
            ('sistema.administracion.configuracion.editar', 'Editar Configuración', 'sistema.administracion.configuracion'),
        ]

        creadas = 0
        for codigo, nombre, funcion_nombre_completo in capacidades_data:
            try:
                funcion = Funcion.objects.get(nombre_completo=funcion_nombre_completo)
            except Funcion.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  ! Función no encontrada: {funcion_nombre_completo}')
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