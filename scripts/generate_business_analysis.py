#!/usr/bin/env python3
"""
Script de ejemplo: Generación de Análisis de Negocio

Demuestra el uso del BusinessAnalysisPipeline para generar
documentación completa de análisis de negocio.

Uso:
    python scripts/generate_business_analysis.py

Salida:
    - Documento de análisis completo
    - Matriz de trazabilidad (RTM)
    - Checklist de completitud
    - Módulos divididos (si aplica)
    - Plantillas (si se solicita)
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ai.agents.business_analysis_pipeline import create_business_analysis_pipeline


def example_password_recovery_system():
    """
    Ejemplo: Sistema de Recuperación de Contraseña

    Genera análisis completo para un componente de seguridad.
    """
    print("\n" + "="*60)
    print("  Ejemplo: Sistema de Recuperación de Contraseña")
    print("="*60 + "\n")

    # Configuración del pipeline
    config = {
        "generator": {
            "domain": "Seguridad",
            "include_procedures": True,
            "include_nfr": True
        },
        "traceability": {
            "min_traceability_index": 0.95,
            "min_coverage_index": 0.90
        },
        "validator": {
            "min_completeness": 0.95,
            "strict_mode": False
        },
        "split_large_docs": True,
        "splitter": {
            "max_lines": 1000,
            "min_lines": 200
        },
        "generate_templates": False
    }

    # Crear pipeline
    pipeline = create_business_analysis_pipeline(
        output_dir=Path("output/analisis_password_recovery"),
        config=config
    )

    # Datos de entrada
    input_data = {
        "component_name": "Sistema de Recuperación de Contraseña",
        "domain": "Seguridad",
        "business_objective": (
            "Permitir a usuarios recuperar acceso a su cuenta cuando olvidan "
            "su contraseña, de forma segura y trazable"
        ),
        "stakeholders": [
            {
                "rol": "Usuario",
                "interes": "Recuperar acceso de forma rápida y simple"
            },
            {
                "rol": "Administrador de Seguridad",
                "interes": "Garantizar seguridad y trazabilidad del proceso"
            },
            {
                "rol": "Auditor",
                "interes": "Verificar cumplimiento de políticas de seguridad"
            }
        ],
        "scope": {
            "includes": [
                "Solicitud de recuperación vía email",
                "Generación de token temporal",
                "Validación de token",
                "Establecimiento de nueva contraseña"
            ],
            "excludes": [
                "Recuperación vía SMS",
                "Preguntas de seguridad",
                "Recuperación con código QR"
            ]
        },
        "critical": True  # Sistema crítico, genera RNF de disponibilidad
    }

    # Ejecutar pipeline
    result = pipeline.execute(input_data)

    return result


def example_user_management_system():
    """
    Ejemplo: Sistema de Gestión de Usuarios

    Genera análisis para un componente de administración.
    """
    print("\n" + "="*60)
    print("  Ejemplo: Sistema de Gestión de Usuarios")
    print("="*60 + "\n")

    config = {
        "generator": {
            "domain": "Administración",
            "include_procedures": True,
            "include_nfr": False  # Sin RNF para este ejemplo
        },
        "traceability": {
            "min_traceability_index": 0.90,
            "min_coverage_index": 0.85
        },
        "validator": {
            "min_completeness": 0.90,
            "strict_mode": False
        },
        "split_large_docs": False,  # No dividir
        "generate_templates": False
    }

    pipeline = create_business_analysis_pipeline(
        output_dir=Path("output/analisis_user_management"),
        config=config
    )

    input_data = {
        "component_name": "Sistema de Gestión de Usuarios",
        "domain": "Administración",
        "business_objective": (
            "Permitir a administradores crear, modificar y eliminar usuarios del sistema"
        ),
        "stakeholders": [
            {
                "rol": "Administrador",
                "interes": "Gestionar usuarios de forma eficiente"
            },
            {
                "rol": "Usuario Final",
                "interes": "Tener cuenta activa y permisos correctos"
            }
        ],
        "scope": {
            "includes": [
                "Crear usuario",
                "Modificar usuario",
                "Eliminar usuario",
                "Asignar roles y permisos"
            ],
            "excludes": [
                "Auto-registro de usuarios",
                "Integración con Active Directory"
            ]
        }
    }

    result = pipeline.execute(input_data)

    return result


def example_template_generation():
    """
    Ejemplo: Generación de Plantillas

    Genera plantillas personalizadas para futuros análisis.
    """
    print("\n" + "="*60)
    print("  Ejemplo: Generación de Plantillas")
    print("="*60 + "\n")

    config = {
        "generate_templates": True,
        "templates": {
            "include_examples": True,
            "include_instructions": True
        }
    }

    # Solo ejecutar TemplateGenerator
    from scripts.ai.agents.template_generator import TemplateGenerator

    output_dir = Path("output/plantillas")
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = TemplateGenerator(config=config["templates"])

    # Generar plantilla de documento maestro
    result_master = generator.execute({
        "template_type": "master_document",
        "parameters": {
            "component_name": "[Mi Componente]",
            "domain": "[Mi Dominio]"
        }
    })

    if result_master.is_success():
        template_path = output_dir / "plantilla_documento_maestro.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(result_master.data["template_content"])
        print(f"✓ Plantilla guardada: {template_path}")

    # Generar plantilla de caso de uso
    result_uc = generator.execute({
        "template_type": "use_case",
        "parameters": {
            "uc_id": "UC-001"
        }
    })

    if result_uc.is_success():
        template_path = output_dir / "plantilla_caso_de_uso.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(result_uc.data["template_content"])
        print(f"✓ Plantilla guardada: {template_path}")

    # Generar plantilla de requisito
    result_req = generator.execute({
        "template_type": "requirement_spec",
        "parameters": {
            "req_id": "RF-001"
        }
    })

    if result_req.is_success():
        template_path = output_dir / "plantilla_requisito.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(result_req.data["template_content"])
        print(f"✓ Plantilla guardada: {template_path}")

    print(f"\nTodas las plantillas guardadas en: {output_dir}")


def main():
    """Función principal."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         Business Analysis Pipeline - Ejemplos de Uso        ║
║                                                              ║
║  Genera documentación completa de análisis de negocio       ║
║  siguiendo estándares ISO 29148, BABOK v3 y UML 2.5         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Menú de ejemplos
    print("\nEjemplos disponibles:")
    print("  1. Sistema de Recuperación de Contraseña (completo)")
    print("  2. Sistema de Gestión de Usuarios (básico)")
    print("  3. Generación de Plantillas")
    print("  4. Ejecutar todos los ejemplos")
    print("  0. Salir")

    try:
        choice = input("\nSelecciona un ejemplo (0-4): ").strip()

        if choice == "1":
            result = example_password_recovery_system()
            if result["status"] == "success":
                print("\n✓ Análisis completado exitosamente")
                print(f"  Ver resultados en: output/analisis_password_recovery/")

        elif choice == "2":
            result = example_user_management_system()
            if result["status"] == "success":
                print("\n✓ Análisis completado exitosamente")
                print(f"  Ver resultados en: output/analisis_user_management/")

        elif choice == "3":
            example_template_generation()

        elif choice == "4":
            print("\nEjecutando todos los ejemplos...\n")
            example_password_recovery_system()
            example_user_management_system()
            example_template_generation()
            print("\n✓ Todos los ejemplos completados")

        elif choice == "0":
            print("\nSaliendo...")
            sys.exit(0)

        else:
            print("\nOpción inválida")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
