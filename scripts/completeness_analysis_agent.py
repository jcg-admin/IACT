#!/usr/bin/env python3
"""
CompletenessAnalysisAgent
=========================

Automated agent for analyzing completeness of documentation reorganization.

This agent performs the following analyses:
1. Verify directory structure completeness for all domains
2. Check README coverage in all critical directories
3. Verify governance framework references are present
4. Analyze file distribution and identify orphaned files
5. Sample check for broken internal links
6. Verify traceability files exist where needed
7. Generate comprehensive gap analysis report

Author: Claude (claude-sonnet-4-5-20250929)
Date: 2025-11-13
Domain: ai
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple

class CompletenessAnalysisAgent:
    """Agent for analyzing documentation reorganization completeness."""

    def __init__(self, base_path: str = "/home/user/IACT---project/docs"):
        self.base_path = Path(base_path)
        self.domains = ["ai", "backend", "frontend", "infraestructura"]

        # Expected governance frameworks
        self.governance_frameworks = [
            "gobernanza/marco_integrado/marco_reglas_negocio.md",
            "gobernanza/marco_integrado/marco_casos_uso.md"
        ]

        # Expected 5-level hierarchy subdirectories
        self.requisitos_structure = {
            "reglas_negocio": {
                "files": ["hechos.md", "restricciones.md", "desencadenadores.md",
                         "inferencias.md", "calculos.md"]
            },
            "requerimientos_negocio": {},
            "requerimientos_usuario": {
                "subdirs": ["casos_uso", "escenarios", "historias_usuario"],
                "files": ["actores.md", "perfiles_usuario.md"]
            },
            "requerimientos_usuario/casos_uso": {
                "subdirs": ["diagramas_uml", "diagramas_actividad"],
                "files": []
            },
            "requerimientos_usuario/escenarios": {
                "subdirs": ["happy_path", "alternos", "excepciones"]
            },
            "requerimientos_usuario/historias_usuario": {
                "subdirs": ["sprint_01", "backlog"]
            },
            "requerimientos_funcionales": {
                "subdirs": ["features"]
            },
            "atributos_calidad": {},
            "analisis_negocio": {
                "subdirs": ["marco_integrado"]
            }
        }

        # Files that should stay in docs/ root
        self.root_files = {
            "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "SETUP.md",
            "ONBOARDING.md", "INDEX.md", "INDICE.md",
            "CATALOGO_TODOS_PENDIENTES.md", "RESUMEN_REMEDIACION_CRITICA_DOCS.md"
        }

        # Directories that should stay in docs/ root
        self.root_dirs = {
            "anexos", "scripts", "guias", "analisis", "plans",
            "features", "operaciones", "gobernanza", "dora"
        }

        # Results storage
        self.results = {
            "structure_completeness": {},
            "readme_coverage": {},
            "governance_references": {},
            "orphaned_files": {},
            "broken_links": [],
            "traceability_files": {},
            "statistics": {}
        }

    def run_full_analysis(self) -> Dict:
        """Run all analysis tasks and return comprehensive results."""
        print("Starting Completeness Analysis...")
        print("=" * 80)

        # Task 1: Verify directory structure
        print("\n[1/7] Verifying directory structure completeness...")
        self.verify_directory_structure()

        # Task 2: Check README coverage
        print("\n[2/7] Checking README coverage...")
        self.check_readme_coverage()

        # Task 3: Verify governance framework references
        print("\n[3/7] Verifying governance framework references...")
        self.verify_governance_references()

        # Task 4: Analyze file distribution
        print("\n[4/7] Analyzing file distribution and orphaned files...")
        self.analyze_file_distribution()

        # Task 5: Check for broken links
        print("\n[5/7] Checking for broken internal links...")
        self.check_broken_links()

        # Task 6: Verify traceability files
        print("\n[6/7] Verifying traceability files...")
        self.verify_traceability_files()

        # Task 7: Generate statistics
        print("\n[7/7] Generating statistics...")
        self.generate_statistics()

        print("\n" + "=" * 80)
        print("Analysis complete!")

        return self.results

    def verify_directory_structure(self):
        """Verify that all domains have the complete 5-level hierarchy."""
        for domain in self.domains:
            domain_path = self.base_path / domain

            if not domain_path.exists():
                self.results["structure_completeness"][domain] = {
                    "status": "MISSING",
                    "missing_dirs": ["entire domain"]
                }
                continue

            missing_dirs = []
            existing_dirs = []

            # Check requisitos structure
            requisitos_path = domain_path / "requisitos"
            if not requisitos_path.exists():
                missing_dirs.append("requisitos/")
            else:
                for subdir, config in self.requisitos_structure.items():
                    subdir_path = requisitos_path / subdir
                    if not subdir_path.exists():
                        missing_dirs.append(f"requisitos/{subdir}/")
                    else:
                        existing_dirs.append(f"requisitos/{subdir}/")

                        # Check subdirectories if defined
                        if "subdirs" in config:
                            for subsub in config["subdirs"]:
                                subsub_path = subdir_path / subsub
                                if not subsub_path.exists():
                                    missing_dirs.append(f"requisitos/{subdir}/{subsub}/")
                                else:
                                    existing_dirs.append(f"requisitos/{subdir}/{subsub}/")

            self.results["structure_completeness"][domain] = {
                "status": "COMPLETE" if not missing_dirs else "INCOMPLETE",
                "existing_dirs": existing_dirs,
                "missing_dirs": missing_dirs,
                "completeness_pct": len(existing_dirs) / (len(existing_dirs) + len(missing_dirs)) * 100
                    if (existing_dirs or missing_dirs) else 0
            }

    def check_readme_coverage(self):
        """Check for README files in critical directories."""
        critical_readme_paths = [
            "requisitos/README.md",
            "requisitos/reglas_negocio/README.md",
            "requisitos/requerimientos_usuario/README.md",
            "requisitos/requerimientos_usuario/casos_uso/README.md"
        ]

        for domain in self.domains:
            domain_path = self.base_path / domain

            if not domain_path.exists():
                self.results["readme_coverage"][domain] = {
                    "status": "DOMAIN_MISSING",
                    "found": [],
                    "missing": critical_readme_paths
                }
                continue

            found = []
            missing = []

            for readme_path in critical_readme_paths:
                full_path = domain_path / readme_path
                if full_path.exists():
                    found.append(readme_path)
                else:
                    missing.append(readme_path)

            # Find all other READMEs
            all_readmes = list(domain_path.rglob("README.md"))

            self.results["readme_coverage"][domain] = {
                "status": "COMPLETE" if not missing else "INCOMPLETE",
                "found": found,
                "missing": missing,
                "total_readmes": len(all_readmes),
                "coverage_pct": len(found) / len(critical_readme_paths) * 100
            }

    def verify_governance_references(self):
        """Verify that READMEs reference governance frameworks correctly."""
        reference_patterns = [
            r"docs/gobernanza/marco_integrado/marco_reglas_negocio\.md",
            r"docs/gobernanza/marco_integrado/marco_casos_uso\.md"
        ]

        for domain in self.domains:
            domain_path = self.base_path / domain

            if not domain_path.exists():
                self.results["governance_references"][domain] = {
                    "status": "DOMAIN_MISSING"
                }
                continue

            # Check READMEs for references
            readmes_to_check = [
                "requisitos/README.md",
                "requisitos/reglas_negocio/README.md",
                "requisitos/requerimientos_usuario/README.md",
                "requisitos/requerimientos_usuario/casos_uso/README.md"
            ]

            references_found = defaultdict(list)

            for readme_path in readmes_to_check:
                full_path = domain_path / readme_path
                if full_path.exists():
                    content = full_path.read_text()
                    for pattern in reference_patterns:
                        if re.search(pattern, content):
                            references_found[readme_path].append(pattern)

            self.results["governance_references"][domain] = {
                "status": "COMPLETE" if references_found else "NO_REFERENCES",
                "references_found": dict(references_found),
                "total_references": sum(len(refs) for refs in references_found.values())
            }

    def analyze_file_distribution(self):
        """Analyze file distribution and identify orphaned files."""
        # Count files in each domain
        domain_file_counts = {}
        for domain in self.domains:
            domain_path = self.base_path / domain
            if domain_path.exists():
                files = list(domain_path.rglob("*"))
                file_count = sum(1 for f in files if f.is_file())
                domain_file_counts[domain] = file_count

        # Find orphaned directories
        orphaned_dirs = {}

        for item in self.base_path.iterdir():
            if not item.is_dir():
                continue

            dir_name = item.name

            # Skip if it's a domain or allowed root directory
            if dir_name in self.domains or dir_name in self.root_dirs:
                continue

            # Skip hidden directories
            if dir_name.startswith("."):
                continue

            # This is an orphaned directory
            files = list(item.rglob("*"))
            file_count = sum(1 for f in files if f.is_file())

            if file_count > 0:
                orphaned_dirs[dir_name] = {
                    "file_count": file_count,
                    "path": str(item.relative_to(self.base_path))
                }

        self.results["orphaned_files"] = {
            "domain_file_counts": domain_file_counts,
            "orphaned_directories": orphaned_dirs,
            "total_orphaned_files": sum(d["file_count"] for d in orphaned_dirs.values()),
            "orphaned_dir_count": len(orphaned_dirs)
        }

    def check_broken_links(self):
        """Check for broken internal links in markdown files."""
        broken_link_patterns = [
            (r"\.\./\.\./requisitos/", "Old root requisitos reference"),
            (r"docs/infrastructure/", "Old infrastructure path"),
            (r"docs/agent/", "Old agent path")
        ]

        broken_links_found = []

        # Check all markdown files in domains
        for domain in self.domains:
            domain_path = self.base_path / domain
            if not domain_path.exists():
                continue

            md_files = domain_path.rglob("*.md")

            for md_file in md_files:
                try:
                    content = md_file.read_text()

                    for pattern, description in broken_link_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Get line number
                            line_num = content[:match.start()].count('\n') + 1

                            broken_links_found.append({
                                "file": str(md_file.relative_to(self.base_path)),
                                "line": line_num,
                                "pattern": pattern,
                                "description": description,
                                "match": match.group()
                            })
                except Exception as e:
                    pass  # Skip files that can't be read

        # Also check governance and other important directories
        for check_dir in ["gobernanza", "scripts"]:
            check_path = self.base_path / check_dir
            if not check_path.exists():
                continue

            md_files = check_path.rglob("*.md")

            for md_file in md_files:
                try:
                    content = md_file.read_text()

                    for pattern, description in broken_link_patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1

                            broken_links_found.append({
                                "file": str(md_file.relative_to(self.base_path)),
                                "line": line_num,
                                "pattern": pattern,
                                "description": description,
                                "match": match.group()
                            })
                except Exception as e:
                    pass

        self.results["broken_links"] = broken_links_found

    def verify_traceability_files(self):
        """Verify that traceability files exist where needed."""
        traceability_patterns = ["*trazabilidad*", "*traceability*"]

        for domain in self.domains:
            domain_path = self.base_path / domain

            if not domain_path.exists():
                self.results["traceability_files"][domain] = {
                    "status": "DOMAIN_MISSING",
                    "files": []
                }
                continue

            found_files = []

            for pattern in traceability_patterns:
                matches = domain_path.rglob(pattern)
                found_files.extend([str(f.relative_to(domain_path)) for f in matches if f.is_file()])

            self.results["traceability_files"][domain] = {
                "status": "FOUND" if found_files else "MISSING",
                "files": found_files,
                "count": len(found_files)
            }

    def generate_statistics(self):
        """Generate overall statistics."""
        stats = {}

        # Structure completeness
        structure_complete = sum(
            1 for d in self.results["structure_completeness"].values()
            if d.get("status") == "COMPLETE"
        )
        stats["structure_completeness_pct"] = structure_complete / len(self.domains) * 100

        # README coverage
        readme_complete = sum(
            1 for d in self.results["readme_coverage"].values()
            if d.get("status") == "COMPLETE"
        )
        stats["readme_coverage_pct"] = readme_complete / len(self.domains) * 100

        # Governance references
        gov_ref_complete = sum(
            1 for d in self.results["governance_references"].values()
            if d.get("status") == "COMPLETE"
        )
        stats["governance_ref_pct"] = gov_ref_complete / len(self.domains) * 100

        # Broken links
        stats["broken_links_count"] = len(self.results["broken_links"])

        # Orphaned files
        stats["orphaned_files_count"] = self.results["orphaned_files"]["total_orphaned_files"]
        stats["orphaned_dirs_count"] = self.results["orphaned_files"]["orphaned_dir_count"]

        # Traceability
        trace_complete = sum(
            1 for d in self.results["traceability_files"].values()
            if d.get("status") == "FOUND"
        )
        stats["traceability_coverage_pct"] = trace_complete / len(self.domains) * 100

        # Overall health score (weighted average)
        weights = {
            "structure": 0.25,
            "readme": 0.15,
            "governance": 0.15,
            "orphaned": 0.20,  # Penalty for orphaned files
            "broken_links": 0.15,  # Penalty for broken links
            "traceability": 0.10
        }

        # Calculate penalties
        total_files = sum(self.results["orphaned_files"]["domain_file_counts"].values())
        orphaned_penalty = (stats["orphaned_files_count"] / (total_files + 1)) * 100 if total_files else 0

        # Estimate total links (rough approximation)
        estimated_total_links = 500  # Conservative estimate
        broken_links_penalty = (stats["broken_links_count"] / estimated_total_links) * 100

        overall_score = (
            weights["structure"] * stats["structure_completeness_pct"] +
            weights["readme"] * stats["readme_coverage_pct"] +
            weights["governance"] * stats["governance_ref_pct"] +
            weights["orphaned"] * max(0, 100 - orphaned_penalty * 2) +
            weights["broken_links"] * max(0, 100 - broken_links_penalty * 2) +
            weights["traceability"] * stats["traceability_coverage_pct"]
        )

        stats["overall_health_score"] = round(overall_score, 2)

        self.results["statistics"] = stats

    def print_summary(self):
        """Print a human-readable summary of results."""
        print("\n" + "=" * 80)
        print("COMPLETENESS ANALYSIS SUMMARY")
        print("=" * 80)

        stats = self.results["statistics"]

        print(f"\nOverall Health Score: {stats['overall_health_score']:.2f}%")
        print("\nDetailed Metrics:")
        print(f"  - Structure Completeness: {stats['structure_completeness_pct']:.1f}%")
        print(f"  - README Coverage: {stats['readme_coverage_pct']:.1f}%")
        print(f"  - Governance References: {stats['governance_ref_pct']:.1f}%")
        print(f"  - Traceability Coverage: {stats['traceability_coverage_pct']:.1f}%")
        print(f"  - Broken Links Found: {stats['broken_links_count']}")
        print(f"  - Orphaned Files: {stats['orphaned_files_count']} in {stats['orphaned_dirs_count']} directories")

        print("\n" + "-" * 80)
        print("DOMAIN-LEVEL DETAILS")
        print("-" * 80)

        for domain in self.domains:
            print(f"\n[{domain.upper()}]")

            # Structure
            struct = self.results["structure_completeness"].get(domain, {})
            print(f"  Structure: {struct.get('status', 'UNKNOWN')} " +
                  f"({struct.get('completeness_pct', 0):.1f}%)")

            # READMEs
            readme = self.results["readme_coverage"].get(domain, {})
            print(f"  READMEs: {readme.get('status', 'UNKNOWN')} " +
                  f"({readme.get('total_readmes', 0)} total, {readme.get('coverage_pct', 0):.1f}% critical)")

            # Governance
            gov = self.results["governance_references"].get(domain, {})
            print(f"  Governance Refs: {gov.get('status', 'UNKNOWN')} " +
                  f"({gov.get('total_references', 0)} references)")

            # Traceability
            trace = self.results["traceability_files"].get(domain, {})
            print(f"  Traceability: {trace.get('status', 'UNKNOWN')} " +
                  f"({trace.get('count', 0)} files)")

        if stats['orphaned_files_count'] > 0:
            print("\n" + "-" * 80)
            print("ORPHANED DIRECTORIES")
            print("-" * 80)

            for dir_name, info in self.results["orphaned_files"]["orphaned_directories"].items():
                print(f"  - {dir_name}/: {info['file_count']} files")

        if stats['broken_links_count'] > 0:
            print("\n" + "-" * 80)
            print(f"BROKEN LINKS (showing first 10 of {stats['broken_links_count']})")
            print("-" * 80)

            for link in self.results["broken_links"][:10]:
                print(f"  - {link['file']}:{link['line']} - {link['description']}")

        print("\n" + "=" * 80)

    def save_report(self, output_path: str = None):
        """Save results to JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/completeness_analysis_{timestamp}.json"

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        report = {
            "metadata": {
                "agent": "CompletenessAnalysisAgent",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "base_path": str(self.base_path)
            },
            "results": self.results
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nReport saved to: {output_file}")
        return str(output_file)


def main():
    """Main entry point."""
    import sys

    # Parse command line arguments
    base_path = sys.argv[1] if len(sys.argv) > 1 else "/home/user/IACT---project/docs"
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Create and run agent
    agent = CompletenessAnalysisAgent(base_path)
    agent.run_full_analysis()
    agent.print_summary()
    agent.save_report(output_path)


if __name__ == "__main__":
    main()
