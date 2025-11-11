#!/usr/bin/env python
"""
Script de validacion: Probar funcion usuario_tiene_permiso con datos reales.

Casos de prueba:
1. Usuario con grupo visualizacion_basica PUEDE ver dashboards
2. Usuario con grupo visualizacion_basica NO PUEDE crear usuarios
3. Usuario con grupo admin_usuarios PUEDE crear usuarios

Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 88)

Uso:
    cd api/callcentersite
    python manage.py shell < scripts/validacion/test_permisos.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from callcentersite.apps.users.services_permisos_granular import (
    UserManagementService,
)
from callcentersite.apps.users.models_permisos_granular import (
    GrupoPermiso,
    UsuarioGrupo,
)

User = get_user_model()


def print_header(title):
    """Imprime un header formateado."""
    print('\n' + '=' * 60)
    print(title)
    print('=' * 60 + '\n')


def print_result(test_name, expected, actual):
    """Imprime el resultado de un test."""
    status = 'OK ✓' if expected == actual else 'ERROR ✗'
    print(f'{test_name}:')
    print(f'  Esperado: {expected}')
    print(f'  Resultado: {actual}')
    print(f'  Estado: {status}\n')
    return expected == actual


def main():
    """Ejecuta los tests de permisos."""
    print_header('VALIDACION: Funcion usuario_tiene_permiso')

    # Verificar que existen los grupos necesarios
    print('Verificando grupos necesarios...')
    try:
        grupo_viz = GrupoPermiso.objects.get(codigo='visualizacion_basica')
        grupo_admin = GrupoPermiso.objects.get(codigo='administracion_usuarios')
        print(f'  ✓ Grupo visualizacion_basica: {grupo_viz.nombre}')
        print(f'  ✓ Grupo administracion_usuarios: {grupo_admin.nombre}')
    except GrupoPermiso.DoesNotExist as e:
        print(f'  ✗ ERROR: {e}')
        print('  Ejecutar primero: python manage.py seed_permisos_granular')
        return False

    # Crear usuarios de prueba
    print('\nCreando usuarios de prueba...')

    # Limpiar usuarios existentes de prueba
    User.objects.filter(email__in=[
        'test_visualizacion@test.com',
        'test_admin@test.com',
    ]).delete()

    user_viz = User.objects.create_user(
        email='test_visualizacion@test.com',
        password='test123',
        first_name='Test',
        last_name='Visualizacion',
    )
    print(f'  ✓ Usuario creado: {user_viz.email} (ID: {user_viz.id})')

    user_admin = User.objects.create_user(
        email='test_admin@test.com',
        password='test123',
        first_name='Test',
        last_name='Admin',
    )
    print(f'  ✓ Usuario creado: {user_admin.email} (ID: {user_admin.id})')

    # Asignar grupos
    print('\nAsignando grupos...')

    UserManagementService.asignar_grupo_a_usuario(
        usuario_id=user_viz.id,
        grupo_codigo='visualizacion_basica',
        asignado_por_id=user_admin.id,
    )
    print(f'  ✓ Grupo visualizacion_basica asignado a {user_viz.email}')

    UserManagementService.asignar_grupo_a_usuario(
        usuario_id=user_admin.id,
        grupo_codigo='administracion_usuarios',
        asignado_por_id=user_admin.id,
    )
    print(f'  ✓ Grupo administracion_usuarios asignado a {user_admin.email}')

    # Ejecutar tests
    print_header('TESTS DE PERMISOS')

    all_passed = True

    # Test 1: Usuario con visualizacion_basica PUEDE ver dashboards
    resultado = UserManagementService.usuario_tiene_permiso(
        usuario_id=user_viz.id,
        capacidad_codigo='sistema.vistas.dashboards.ver',
    )
    passed = print_result(
        'Test 1: Usuario con visualizacion_basica PUEDE ver dashboards',
        expected=True,
        actual=resultado
    )
    all_passed = all_passed and passed

    # Test 2: Usuario con visualizacion_basica NO PUEDE crear usuarios
    resultado = UserManagementService.usuario_tiene_permiso(
        usuario_id=user_viz.id,
        capacidad_codigo='sistema.administracion.usuarios.crear',
    )
    passed = print_result(
        'Test 2: Usuario con visualizacion_basica NO PUEDE crear usuarios',
        expected=False,
        actual=resultado
    )
    all_passed = all_passed and passed

    # Test 3: Usuario con admin_usuarios PUEDE crear usuarios
    resultado = UserManagementService.usuario_tiene_permiso(
        usuario_id=user_admin.id,
        capacidad_codigo='sistema.administracion.usuarios.crear',
    )
    passed = print_result(
        'Test 3: Usuario con admin_usuarios PUEDE crear usuarios',
        expected=True,
        actual=resultado
    )
    all_passed = all_passed and passed

    # Test 4: Usuario con admin_usuarios NO PUEDE editar configuracion
    resultado = UserManagementService.usuario_tiene_permiso(
        usuario_id=user_admin.id,
        capacidad_codigo='sistema.tecnico.configuracion.editar',
    )
    passed = print_result(
        'Test 4: Usuario con admin_usuarios NO PUEDE editar configuracion',
        expected=False,
        actual=resultado
    )
    all_passed = all_passed and passed

    # Test 5: Verificar capacidades del usuario de visualizacion
    print('Test 5: Listar capacidades de usuario visualizacion_basica')
    capacidades = UserManagementService.obtener_capacidades_usuario(
        usuario_id=user_viz.id
    )
    print(f'  Capacidades encontradas: {len(capacidades)}')
    for cap in capacidades:
        print(f'    - {cap}')
    print()

    # Resumen
    print_header('RESUMEN DE VALIDACION')
    if all_passed:
        print('✓ TODOS LOS TESTS PASARON')
        print('\nLa funcion usuario_tiene_permiso funciona correctamente.')
    else:
        print('✗ ALGUNOS TESTS FALLARON')
        print('\nRevisar la implementacion de usuario_tiene_permiso.')

    # Limpiar usuarios de prueba
    print('\nLimpiando usuarios de prueba...')
    user_viz.delete()
    user_admin.delete()
    print('  ✓ Usuarios de prueba eliminados')

    print_header('FIN DE VALIDACION')

    return all_passed


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f'\n✗ ERROR INESPERADO: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
