#!/usr/bin/env python3
"""
Script ejecutor del DocumentationSyncAgent

Este script ejecuta el pipeline completo:
1. Reorganiza docs/ automáticamente (si es necesario)
2. Planner: Inspecciona código y planifica
3. Editor: Genera/actualiza documentación
4. Verifier: Verifica consistencia
5. Reporter: Genera reporte

Uso:
    python scripts/sync_documentation.py [--dry-run] [--reorganize] [--domains api,ui,infraestructura]

Opciones:
    --dry-run       No escribe archivos, solo simula
    --reorganize    Ejecuta reorganización de docs/ primero
    --domains       Dominios a sincronizar (default: api,ui,infraestructura)
    --report-only   Solo genera reporte sin modificar nada
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Importar agente directamente sin pasar por __init__.py
import importlib.util
agent_path = Path(__file__).parent / "ai" / "agents" / "documentation_sync_agent.py"
spec = importlib.util.spec_from_file_location("documentation_sync_agent", agent_path)
doc_sync_module = importlib.util.module_from_spec(spec)
sys.modules['documentation_sync_agent'] = doc_sync_module
spec.loader.exec_module(doc_sync_module)

create_documentation_sync_pipeline = doc_sync_module.create_documentation_sync_pipeline


def run_reorganization(dry_run: bool = True) -> bool:
    """
    Ejecuta el script de reorganización de docs/.

    Args:
        dry_run: Si True, ejecuta en modo dry-run

    Returns:
        True si exitoso, False si falló
    """
    script_path = Path(__file__).parent / "reorganizar_docs_por_dominio.sh"

    if not script_path.exists():
        print(f"ERROR: Script no encontrado: {script_path}")
        return False

    print("\n" + "="*50)
    print("FASE 0: Reorganización de docs/")
    print("="*50 + "\n")

    cmd = [str(script_path)]
    if dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Reorganización falló: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sincronizar código con documentación")
    parser.add_argument("--dry-run", action="store_true",
                        help="No escribir archivos, solo simular")
    parser.add_argument("--reorganize", action="store_true",
                        help="Ejecutar reorganización de docs/ primero")
    parser.add_argument("--domains", type=str, default="api,ui,infraestructura",
                        help="Dominios a sincronizar (separados por coma)")
    parser.add_argument("--report-only", action="store_true",
                        help="Solo generar reporte sin modificar")
    parser.add_argument("--no-report", action="store_true",
                        help="No guardar reporte en archivo")

    args = parser.parse_args()

    # Parsear dominios
    domains = [d.strip() for d in args.domains.split(",")]

    # Configurar project root
    project_root = Path(__file__).parent.parent
    print(f"Project root: {project_root}")
    print(f"Dominios a analizar: {', '.join(domains)}")
    print(f"Modo: {'DRY-RUN' if args.dry_run or args.report_only else 'ESCRITURA REAL'}")
    print("")

    # Fase 0: Reorganización (opcional)
    if args.reorganize:
        success = run_reorganization(dry_run=args.dry_run)
        if not success:
            print("WARNING: Reorganización falló, continuando de todos modos...")
        print("")

    # Crear pipeline
    print("="*50)
    print("Creando pipeline de sincronización")
    print("="*50 + "\n")

    pipeline = create_documentation_sync_pipeline(
        project_root=str(project_root),
        dry_run=args.dry_run or args.report_only,
        domains=domains
    )

    # Ejecutar pipeline
    print("="*50)
    print("Ejecutando pipeline: Planner → Editor → Verifier → Reporter")
    print("="*50 + "\n")

    initial_data = {
        "domains": domains,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

    result = pipeline.execute(initial_data)

    # Mostrar resultado
    print("\n" + "="*50)
    print("RESULTADO FINAL")
    print("="*50 + "\n")

    if result["status"] == "success":
        print("OK: Pipeline completado exitosamente\n")

        # Extraer data final
        final_data = result.get("data", {})

        # Estadísticas
        stats = final_data.get("stats", {})
        print(f"Componentes totales: {stats.get('total_components', 0)}")
        print(f"Documentación faltante: {stats.get('missing_docs', 0)}")
        print(f"Documentación creada: {len(final_data.get('created_docs', []))}")
        print(f"Documentación actualizada: {len(final_data.get('updated_docs', []))}")
        print("")

        # Verificación
        if final_data.get("verification_passed", True):
            print("OK: Verificación de consistencia pasó")
        else:
            print(f"WARNING: {len(final_data.get('inconsistencies', []))} inconsistencias encontradas")

        print("")

        # Reporte
        if not args.no_report and "report_path" in final_data:
            print(f"Reporte guardado en: {final_data['report_path']}")
            print("")
            print("Para ver el reporte completo:")
            print(f"  cat {final_data['report_path']}")
        elif "report_markdown" in final_data:
            print("Reporte generado (no guardado en archivo):")
            print("")
            print(final_data["report_markdown"])

    elif result["status"] == "failed":
        print(f"ERROR: Pipeline falló en agente {result.get('failed_agent')}")
        print(f"Errores: {result.get('errors')}")
        return 1

    elif result["status"] == "blocked":
        print(f"BLOQUEADO: Pipeline bloqueado en agente {result.get('blocked_agent')}")
        print(f"Razones: {result.get('errors')}")
        return 1

    print("")
    print("="*50)
    print("PRÓXIMOS PASOS")
    print("="*50 + "\n")

    if args.dry_run or args.report_only:
        print("1. Revisar el reporte generado")
        print("2. Si todo se ve bien, ejecutar sin --dry-run:")
        print(f"   python {Path(__file__).name} --domains {args.domains}")
        print("")
    else:
        print("1. Revisar documentación generada en docs/implementacion/")
        print("2. Completar detalles específicos en cada documento")
        print("3. Commitear cambios:")
        print("   git add docs/")
        print("   git commit -m 'docs: actualizar documentación con sync agent'")
        print("4. Ejecutar sincronización periódicamente")
        print("")

    return 0


if __name__ == "__main__":
    sys.exit(main())
