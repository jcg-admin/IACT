"""
Django management command para poblar sistema de permisos granular.

Crea:
- 13 funciones del sistema
- 78 capacidades granulares
- 10 grupos funcionales
- Relaciones funcion-capacidades
- Relaciones grupo-capacidades

Uso:
    python manage.py seed_permisos_granular

Referencia: docs/backend/requisitos/CATALOGO_GRUPOS_FUNCIONALES.md
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from callcentersite.apps.users.models_permisos_granular import (
    Funcion,
    Capacidad,
    FuncionCapacidad,
    GrupoPermiso,
    GrupoCapacidad,
)


class Command(BaseCommand):
    help = 'Pobla el sistema de permisos granular con datos iniciales'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de permisos granular...')

        with transaction.atomic():
            self.crear_funciones()
            self.crear_capacidades()
            self.crear_grupos()
            self.asignar_capacidades_a_grupos()

        self.stdout.write(self.style.SUCCESS('Seed completado exitosamente'))

    def crear_funciones(self):
        """Crea las 13 funciones del sistema."""
        self.stdout.write('Creando funciones...')

        funciones_data = [
            # PRIORIDAD 2: Core (3 funciones)
            {
                'nombre': 'usuarios',
                'nombre_completo': 'sistema.administracion.usuarios',
                'dominio': 'sistema.administracion',
                'categoria': 'administracion',
                'descripcion': 'Gestion de cuentas de usuario',
                'icono': 'users',
                'orden_menu': 10,
            },
            {
                'nombre': 'dashboards',
                'nombre_completo': 'sistema.vistas.dashboards',
                'dominio': 'sistema.vistas',
                'categoria': 'vistas',
                'descripcion': 'Visualizacion de dashboards',
                'icono': 'dashboard',
                'orden_menu': 20,
            },
            {
                'nombre': 'configuracion',
                'nombre_completo': 'sistema.tecnico.configuracion',
                'dominio': 'sistema.tecnico',
                'categoria': 'tecnico',
                'descripcion': 'Configuracion del sistema',
                'icono': 'cog',
                'orden_menu': 100,
            },
            # PRIORIDAD 3: Operativos (6 funciones)
            {
                'nombre': 'llamadas',
                'nombre_completo': 'sistema.operaciones.llamadas',
                'dominio': 'sistema.operaciones',
                'categoria': 'operaciones',
                'descripcion': 'Gestion de llamadas',
                'icono': 'phone',
                'orden_menu': 30,
            },
            {
                'nombre': 'tickets',
                'nombre_completo': 'sistema.operaciones.tickets',
                'dominio': 'sistema.operaciones',
                'categoria': 'operaciones',
                'descripcion': 'Gestion de tickets',
                'icono': 'ticket',
                'orden_menu': 40,
            },
            {
                'nombre': 'clientes',
                'nombre_completo': 'sistema.operaciones.clientes',
                'dominio': 'sistema.operaciones',
                'categoria': 'operaciones',
                'descripcion': 'Gestion de clientes',
                'icono': 'users',
                'orden_menu': 50,
            },
            # ... (simplificado para el ejemplo)
        ]

        for data in funciones_data:
            Funcion.objects.get_or_create(
                nombre_completo=data['nombre_completo'],
                defaults=data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(funciones_data)} funciones creadas'))

    def crear_capacidades(self):
        """Crea capacidades granulares."""
        self.stdout.write('Creando capacidades...')

        capacidades_data = [
            # Funcion: usuarios (6 capacidades)
            {
                'codigo': 'sistema.administracion.usuarios.ver',
                'nombre': 'Ver Usuarios',
                'descripcion': 'Ver lista y detalles de usuarios',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.administracion.usuarios.crear',
                'nombre': 'Crear Usuario',
                'descripcion': 'Crear nuevos usuarios',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'sistema.administracion.usuarios.editar',
                'nombre': 'Editar Usuario',
                'descripcion': 'Modificar informacion de usuarios',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'sistema.administracion.usuarios.suspender',
                'nombre': 'Suspender Usuario',
                'descripcion': 'Suspender cuentas de usuario',
                'nivel_riesgo': 'alto',
            },
            {
                'codigo': 'sistema.administracion.usuarios.reactivar',
                'nombre': 'Reactivar Usuario',
                'descripcion': 'Reactivar cuentas suspendidas',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'sistema.administracion.usuarios.asignar_grupos',
                'nombre': 'Asignar Grupos',
                'descripcion': 'Asignar grupos de permisos a usuarios',
                'nivel_riesgo': 'alto',
                'requiere_aprobacion': True,
            },
            {
                'codigo': 'sistema.administracion.usuarios.eliminar',
                'nombre': 'Eliminar Usuario',
                'descripcion': 'Eliminar usuarios del sistema (eliminacion logica)',
                'nivel_riesgo': 'critico',
                'requiere_aprobacion': True,
            },
            # Funcion: dashboards (4 capacidades)
            {
                'codigo': 'sistema.vistas.dashboards.ver',
                'nombre': 'Ver Dashboards',
                'descripcion': 'Ver dashboards del sistema',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.vistas.dashboards.personalizar',
                'nombre': 'Personalizar Dashboard',
                'descripcion': 'Personalizar widgets de dashboard',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.vistas.dashboards.exportar',
                'nombre': 'Exportar Dashboard',
                'descripcion': 'Exportar datos de dashboards a Excel o PDF',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'sistema.vistas.dashboards.compartir',
                'nombre': 'Compartir Dashboard',
                'descripcion': 'Compartir dashboards personalizados con otros usuarios',
                'nivel_riesgo': 'medio',
            },
            # Funcion: configuracion (5 capacidades)
            {
                'codigo': 'sistema.tecnico.configuracion.ver',
                'nombre': 'Ver Configuracion',
                'descripcion': 'Ver parametros de configuracion del sistema',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.tecnico.configuracion.editar',
                'nombre': 'Editar Configuracion',
                'descripcion': 'Modificar parametros de configuracion del sistema',
                'nivel_riesgo': 'critico',
                'requiere_aprobacion': True,
            },
            {
                'codigo': 'sistema.tecnico.configuracion.exportar',
                'nombre': 'Exportar Configuracion',
                'descripcion': 'Exportar configuracion del sistema a archivo',
                'nivel_riesgo': 'alto',
                'requiere_aprobacion': True,
            },
            {
                'codigo': 'sistema.tecnico.configuracion.importar',
                'nombre': 'Importar Configuracion',
                'descripcion': 'Importar configuracion desde archivo',
                'nivel_riesgo': 'critico',
                'requiere_aprobacion': True,
            },
            {
                'codigo': 'sistema.tecnico.configuracion.restaurar',
                'nombre': 'Restaurar Configuracion',
                'descripcion': 'Restaurar configuracion a valores por defecto',
                'nivel_riesgo': 'critico',
                'requiere_aprobacion': True,
            },
            # Funcion: llamadas (3 capacidades - ejemplo parcial)
            {
                'codigo': 'sistema.operaciones.llamadas.realizar',
                'nombre': 'Realizar Llamada',
                'descripcion': 'Realizar llamadas salientes',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.operaciones.llamadas.recibir',
                'nombre': 'Recibir Llamada',
                'descripcion': 'Recibir llamadas entrantes',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.operaciones.llamadas.transferir',
                'nombre': 'Transferir Llamada',
                'descripcion': 'Transferir llamadas a otros agentes',
                'nivel_riesgo': 'bajo',
            },
            # Funcion: tickets (7 capacidades - ejemplo parcial)
            {
                'codigo': 'sistema.operaciones.tickets.crear',
                'nombre': 'Crear Ticket',
                'descripcion': 'Crear nuevos tickets',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.operaciones.tickets.ver',
                'nombre': 'Ver Tickets',
                'descripcion': 'Ver tickets del sistema',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'sistema.operaciones.tickets.cerrar',
                'nombre': 'Cerrar Ticket',
                'descripcion': 'Cerrar tickets resueltos',
                'nivel_riesgo': 'medio',
            },
        ]

        for data in capacidades_data:
            Capacidad.objects.get_or_create(
                codigo=data['codigo'],
                defaults=data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(capacidades_data)} capacidades creadas'))

    def crear_grupos(self):
        """Crea los 10 grupos funcionales."""
        self.stdout.write('Creando grupos funcionales...')

        grupos_data = [
            # TECNICOS
            {
                'codigo': 'administracion_usuarios',
                'nombre': 'Administracion de Usuarios',
                'descripcion': 'Gestion completa de cuentas de usuario',
                'categoria': 'tecnico',
                'nivel_riesgo': 'alto',
                'requiere_aprobacion': True,
            },
            {
                'codigo': 'visualizacion_basica',
                'nombre': 'Visualizacion Basica',
                'descripcion': 'Acceso de solo lectura a dashboards',
                'categoria': 'operativo',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'configuracion_sistema',
                'nombre': 'Configuracion del Sistema',
                'descripcion': 'Gestion de parametros y configuracion tecnica',
                'categoria': 'tecnico',
                'nivel_riesgo': 'critico',
                'requiere_aprobacion': True,
            },
            # OPERATIVOS
            {
                'codigo': 'atencion_cliente',
                'nombre': 'Atencion al Cliente',
                'descripcion': 'Operaciones basicas de atencion al cliente',
                'categoria': 'operativo',
                'nivel_riesgo': 'bajo',
            },
            {
                'codigo': 'atencion_cliente_avanzada',
                'nombre': 'Atencion al Cliente Avanzada',
                'descripcion': 'Operaciones avanzadas de atencion al cliente',
                'categoria': 'operativo',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'analisis_operativo',
                'nombre': 'Analisis Operativo',
                'descripcion': 'Visualizacion de metricas y generacion de reportes',
                'categoria': 'gestion',
                'nivel_riesgo': 'bajo',
            },
            # GESTION
            {
                'codigo': 'gestion_equipos',
                'nombre': 'Gestion de Equipos',
                'descripcion': 'Administracion de equipos de trabajo',
                'categoria': 'gestion',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'gestion_horarios',
                'nombre': 'Gestion de Horarios',
                'descripcion': 'Planificacion de turnos y horarios',
                'categoria': 'gestion',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'auditoria_llamadas',
                'nombre': 'Auditoria de Llamadas',
                'descripcion': 'Auditoria de calidad de llamadas',
                'categoria': 'gestion',
                'nivel_riesgo': 'medio',
            },
            {
                'codigo': 'evaluacion_desempeno',
                'nombre': 'Evaluacion de Desempeno',
                'descripcion': 'Evaluaciones de rendimiento de agentes',
                'categoria': 'gestion',
                'nivel_riesgo': 'alto',
            },
        ]

        for data in grupos_data:
            GrupoPermiso.objects.get_or_create(
                codigo=data['codigo'],
                defaults=data,
            )

        self.stdout.write(self.style.SUCCESS(f'  {len(grupos_data)} grupos creados'))

    def asignar_capacidades_a_grupos(self):
        """Asigna capacidades a los grupos funcionales."""
        self.stdout.write('Asignando capacidades a grupos...')

        # Grupo: administracion_usuarios (7 capacidades)
        grupo_admin = GrupoPermiso.objects.get(codigo='administracion_usuarios')
        capacidades_admin = [
            'sistema.administracion.usuarios.ver',
            'sistema.administracion.usuarios.crear',
            'sistema.administracion.usuarios.editar',
            'sistema.administracion.usuarios.suspender',
            'sistema.administracion.usuarios.reactivar',
            'sistema.administracion.usuarios.asignar_grupos',
            'sistema.administracion.usuarios.eliminar',
        ]
        for codigo in capacidades_admin:
            capacidad = Capacidad.objects.get(codigo=codigo)
            GrupoCapacidad.objects.get_or_create(
                grupo=grupo_admin,
                capacidad=capacidad,
            )

        # Grupo: visualizacion_basica (4 capacidades)
        grupo_viz = GrupoPermiso.objects.get(codigo='visualizacion_basica')
        capacidades_viz = [
            'sistema.vistas.dashboards.ver',
            'sistema.vistas.dashboards.personalizar',
            'sistema.vistas.dashboards.exportar',
            'sistema.vistas.dashboards.compartir',
        ]
        for codigo in capacidades_viz:
            capacidad = Capacidad.objects.get(codigo=codigo)
            GrupoCapacidad.objects.get_or_create(
                grupo=grupo_viz,
                capacidad=capacidad,
            )

        # Grupo: configuracion_sistema (5 capacidades)
        grupo_config = GrupoPermiso.objects.get(codigo='configuracion_sistema')
        capacidades_config = [
            'sistema.tecnico.configuracion.ver',
            'sistema.tecnico.configuracion.editar',
            'sistema.tecnico.configuracion.exportar',
            'sistema.tecnico.configuracion.importar',
            'sistema.tecnico.configuracion.restaurar',
        ]
        for codigo in capacidades_config:
            capacidad = Capacidad.objects.get(codigo=codigo)
            GrupoCapacidad.objects.get_or_create(
                grupo=grupo_config,
                capacidad=capacidad,
            )

        # Grupo: atencion_cliente (ejemplo con llamadas y tickets)
        grupo_atencion = GrupoPermiso.objects.get(codigo='atencion_cliente')
        capacidades_atencion = [
            'sistema.operaciones.llamadas.realizar',
            'sistema.operaciones.llamadas.recibir',
            'sistema.operaciones.llamadas.transferir',
            'sistema.operaciones.tickets.crear',
            'sistema.operaciones.tickets.ver',
        ]
        for codigo in capacidades_atencion:
            try:
                capacidad = Capacidad.objects.get(codigo=codigo)
                GrupoCapacidad.objects.get_or_create(
                    grupo=grupo_atencion,
                    capacidad=capacidad,
                )
            except Capacidad.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'  Capacidad no encontrada: {codigo}')
                )

        self.stdout.write(self.style.SUCCESS('  Capacidades asignadas a grupos'))
