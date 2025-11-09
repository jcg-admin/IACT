#!/usr/bin/env python3
"""
Benchmark: ORM vs SQL para sistema de permisos granular.

Compara performance de:
1. ORM Django (services_permisos_granular.py)
2. Vistas SQL (vista_capacidades_usuario)
3. Funciones SQL (usuario_tiene_permiso, obtener_menu_usuario)

Uso:
    python scripts/benchmarks/benchmark_permisos_orm_vs_sql.py

Referencia: docs/adr/adr_2025_010_orm_sql_hybrid_permissions.md
"""

import os
import sys
import time
import json
import statistics
from typing import List, Dict, Callable

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../api/callcentersite'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'callcentersite.settings.base')

import django
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from callcentersite.apps.users.services_permisos_granular import UserManagementService
from callcentersite.apps.users.models_permisos_granular import (
    Capacidad,
    GrupoPermiso,
)

User = get_user_model()


# =============================================================================
# BENCHMARK UTILITIES
# =============================================================================

def measure_time(func: Callable, iterations: int = 100) -> Dict[str, float]:
    """
    Mide tiempo de ejecución de función.

    Args:
        func: Función a medir
        iterations: Número de iteraciones

    Returns:
        Dict con estadísticas (min, max, mean, median, p95, p99)
    """
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return {
        'min': min(times),
        'max': max(times),
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'p95': statistics.quantiles(times, n=20)[18],  # 95th percentile
        'p99': statistics.quantiles(times, n=100)[98],  # 99th percentile
        'iterations': iterations,
    }


def print_results(name: str, stats: Dict[str, float]):
    """Imprime resultados formateados."""
    print(f"\n{name}")
    print("=" * 60)
    print(f"Iterations: {stats['iterations']}")
    print(f"Min:        {stats['min']:.2f} ms")
    print(f"Max:        {stats['max']:.2f} ms")
    print(f"Mean:       {stats['mean']:.2f} ms")
    print(f"Median:     {stats['median']:.2f} ms")
    print(f"P95:        {stats['p95']:.2f} ms")
    print(f"P99:        {stats['p99']:.2f} ms")


def compare_results(name1: str, stats1: Dict, name2: str, stats2: Dict):
    """Compara dos resultados."""
    speedup_mean = stats1['mean'] / stats2['mean']
    speedup_p95 = stats1['p95'] / stats2['p95']

    print(f"\n{name1} vs {name2}")
    print("=" * 60)
    print(f"Mean speedup: {speedup_mean:.2f}x")
    print(f"P95 speedup:  {speedup_p95:.2f}x")

    if speedup_mean > 1:
        print(f"✓ {name2} is {speedup_mean:.2f}x FASTER (mean)")
    else:
        print(f"✓ {name1} is {1/speedup_mean:.2f}x FASTER (mean)")


# =============================================================================
# BENCHMARK 1: usuario_tiene_permiso()
# =============================================================================

def setup_test_data():
    """Setup datos de prueba."""
    # Obtener usuario de prueba (asume que existe)
    try:
        user = User.objects.first()
        if not user:
            print("ERROR: No hay usuarios en la base de datos")
            print("Ejecuta: python manage.py seed_permisos_granular primero")
            sys.exit(1)

        capacidad = Capacidad.objects.first()
        if not capacidad:
            print("ERROR: No hay capacidades en la base de datos")
            sys.exit(1)

        return user.id, capacidad.codigo
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


def benchmark_usuario_tiene_permiso_orm(usuario_id: int, capacidad_codigo: str):
    """Benchmark ORM."""
    def test():
        UserManagementService.usuario_tiene_permiso(
            usuario_id,
            capacidad_codigo,
            auditar=False  # Disable auditing for fair comparison
        )

    return measure_time(test)


def benchmark_usuario_tiene_permiso_sql(usuario_id: int, capacidad_codigo: str):
    """Benchmark SQL function."""
    def test():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT usuario_tiene_permiso(%s, %s)",
                [usuario_id, capacidad_codigo]
            )
            cursor.fetchone()

    return measure_time(test)


# =============================================================================
# BENCHMARK 2: obtener_capacidades()
# =============================================================================

def benchmark_obtener_capacidades_orm(usuario_id: int):
    """Benchmark ORM para obtener capacidades."""
    def test():
        UserManagementService.obtener_capacidades_de_usuario(usuario_id)

    return measure_time(test, iterations=50)  # Slower, reduce iterations


def benchmark_obtener_capacidades_vista_sql(usuario_id: int):
    """Benchmark Vista SQL para obtener capacidades."""
    def test():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT capacidad_codigo
                FROM vista_capacidades_usuario
                WHERE usuario_id = %s
            """, [usuario_id])
            cursor.fetchall()

    return measure_time(test, iterations=50)


def benchmark_obtener_capacidades_funcion_sql(usuario_id: int):
    """Benchmark Función SQL para obtener capacidades."""
    def test():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT obtener_capacidades_usuario(%s)",
                [usuario_id]
            )
            cursor.fetchone()

    return measure_time(test, iterations=50)


# =============================================================================
# BENCHMARK 3: obtener_menu()
# =============================================================================

def benchmark_obtener_menu_orm(usuario_id: int):
    """Benchmark ORM para generar menú (simulado)."""
    def test():
        # Simular generación de menú con ORM
        capacidades = UserManagementService.obtener_capacidades_de_usuario(usuario_id)

        menu = {}
        for cap in capacidades:
            parts = cap.codigo.split('.')
            if len(parts) >= 3:
                dominio = parts[1]
                recurso = parts[2]

                if dominio not in menu:
                    menu[dominio] = {}
                if recurso not in menu[dominio]:
                    menu[dominio][recurso] = []

                menu[dominio][recurso].append(cap.codigo)

        return menu

    return measure_time(test, iterations=20)  # Very slow


def benchmark_obtener_menu_funcion_sql(usuario_id: int):
    """Benchmark Función SQL para generar menú."""
    def test():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT obtener_menu_usuario(%s)",
                [usuario_id]
            )
            cursor.fetchone()

    return measure_time(test, iterations=20)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ejecutar todos los benchmarks."""
    print("\n" + "=" * 60)
    print("BENCHMARK: ORM vs SQL - Sistema de Permisos Granular")
    print("=" * 60)

    # Setup
    usuario_id, capacidad_codigo = setup_test_data()
    print(f"\nUsuario ID: {usuario_id}")
    print(f"Capacidad: {capacidad_codigo}")

    # Benchmark 1: usuario_tiene_permiso
    print("\n\n" + "=" * 60)
    print("BENCHMARK 1: usuario_tiene_permiso()")
    print("=" * 60)

    stats_orm = benchmark_usuario_tiene_permiso_orm(usuario_id, capacidad_codigo)
    print_results("ORM (UserManagementService)", stats_orm)

    stats_sql = benchmark_usuario_tiene_permiso_sql(usuario_id, capacidad_codigo)
    print_results("SQL Function", stats_sql)

    compare_results("ORM", stats_orm, "SQL", stats_sql)

    # Benchmark 2: obtener_capacidades
    print("\n\n" + "=" * 60)
    print("BENCHMARK 2: obtener_capacidades()")
    print("=" * 60)

    stats_orm = benchmark_obtener_capacidades_orm(usuario_id)
    print_results("ORM (Service)", stats_orm)

    stats_vista = benchmark_obtener_capacidades_vista_sql(usuario_id)
    print_results("Vista SQL", stats_vista)

    stats_funcion = benchmark_obtener_capacidades_funcion_sql(usuario_id)
    print_results("Función SQL", stats_funcion)

    compare_results("ORM", stats_orm, "Vista SQL", stats_vista)
    compare_results("ORM", stats_orm, "Función SQL", stats_funcion)

    # Benchmark 3: obtener_menu
    print("\n\n" + "=" * 60)
    print("BENCHMARK 3: obtener_menu()")
    print("=" * 60)

    stats_orm = benchmark_obtener_menu_orm(usuario_id)
    print_results("ORM (Simulated)", stats_orm)

    stats_funcion = benchmark_obtener_menu_funcion_sql(usuario_id)
    print_results("Función SQL", stats_funcion)

    compare_results("ORM", stats_orm, "SQL", stats_funcion)

    # Summary
    print("\n\n" + "=" * 60)
    print("RESUMEN Y RECOMENDACIONES")
    print("=" * 60)
    print("\n✓ Usar ORM para:")
    print("  - Desarrollo y prototiping")
    print("  - Testing (fácil mocking)")
    print("  - Admin/CRUD operations")
    print("  - Queries < 50ms son aceptables")
    print("\n✓ Usar Vistas SQL para:")
    print("  - Queries de lectura frecuentes")
    print("  - Agregaciones complejas")
    print("  - Reportes y analítica")
    print("\n✓ Usar Funciones SQL para:")
    print("  - Verificación de permisos (hot path)")
    print("  - Generación de menú")
    print("  - Operaciones atómicas")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
