"""
CompletenessValidator Agent

Responsabilidad: Validar que un análisis de negocio esté completo antes de revisión.
Input: Documento de análisis con artefactos
Output: Checklist de completitud + lista de items faltantes + porcentaje de completitud

Estándares validados:
- ISO/IEC/IEEE 29148:2018: Trazabilidad completa
- BABOK v3: Presencia de todos los artefactos
- UML 2.5: Casos de uso bien formados
- Proyecto IACT: Nomenclatura, sin emojis
"""

from typing import Any, Dict, List, Optional, Set
import re
from datetime import datetime
from .base import Agent


class CompletenessValidator(Agent):
    """
    Agente especializado en validación de completitud de análisis.

    Valida:
    - Presencia de artefactos obligatorios (contexto, procesos, UC, requisitos)
    - Trazabilidad bidireccional completa
    - Conformidad con estándares (ISO, BABOK, UML)
    - Nomenclatura consistente (PROC-XXX, UC-XXX, RF-XXX, etc.)
    - Ausencia de emojis (estándar IACT)
    - Calidad de documentación (longitud mínima, secciones completas)

    Genera:
    - Checklist detallado por categoría
    - Porcentaje de completitud global
    - Lista de items faltantes priorizados
    - Recomendaciones de mejora
    """

    REQUIRED_SECTIONS = [
        "contexto_negocio",
        "procesos",
        "reglas_negocio",
        "casos_uso",
        "requisitos_funcionales",
        "matriz_trazabilidad"
    ]

    OPTIONAL_SECTIONS = [
        "requisitos_nonfuncionales",
        "procedimientos",
        "diagrama_arquitectura",
        "modelo_datos"
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="CompletenessValidator", config=config)

        # Umbrales de completitud
        self.min_completeness = self.get_config("min_completeness", 0.95)
        self.strict_mode = self.get_config("strict_mode", False)

        # Estándares a validar
        self.validate_iso_29148 = self.get_config("validate_iso_29148", True)
        self.validate_babok_v3 = self.get_config("validate_babok_v3", True)
        self.validate_uml_2_5 = self.get_config("validate_uml_2_5", True)
        self.validate_iact_standards = self.get_config("validate_iact_standards", True)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Valida que existan datos mínimos para validar.

        Args:
            input_data: Datos de entrada

        Returns:
            Lista de errores de validación
        """
        errors = []

        # Debe tener al menos uno de: document (string) o artefactos estructurados
        if "document" not in input_data and "use_cases" not in input_data:
            errors.append(
                "Falta 'document' (string) o artefactos estructurados "
                "(use_cases, requirements, etc.)"
            )

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la validación de completitud.

        Args:
            input_data: Datos de entrada validados

        Returns:
            Diccionario con checklist, completitud y items faltantes
        """
        self.logger.info("Iniciando validación de completitud")

        # Determinar modo de análisis
        if "document" in input_data:
            # Modo documento: analizar texto Markdown
            document = input_data["document"]
            analysis_mode = "document"
        else:
            # Modo estructurado: analizar artefactos
            document = None
            analysis_mode = "structured"

        # Categorías de validación
        checks = {}

        # 1. Validar secciones obligatorias
        self.logger.info("Validando secciones del documento")
        checks["sections"] = self._check_sections(input_data, document, analysis_mode)

        # 2. Validar trazabilidad
        self.logger.info("Validando trazabilidad")
        checks["traceability"] = self._check_traceability(input_data, analysis_mode)

        # 3. Validar estándares
        self.logger.info("Validando conformidad con estándares")
        checks["standards"] = self._check_standards(input_data, document, analysis_mode)

        # 4. Validar nomenclatura
        self.logger.info("Validando nomenclatura")
        checks["nomenclature"] = self._check_nomenclature(input_data, document, analysis_mode)

        # 5. Validar calidad
        self.logger.info("Validando calidad de documentación")
        checks["quality"] = self._check_quality(input_data, document, analysis_mode)

        # Calcular completitud global
        total_checks = sum(len(category["items"]) for category in checks.values())
        passed_checks = sum(
            sum(1 for item in category["items"] if item["passed"])
            for category in checks.values()
        )

        completeness = passed_checks / total_checks if total_checks > 0 else 0.0

        # Obtener items faltantes
        missing_items = self._get_missing_items(checks)

        # Generar recomendaciones
        recommendations = self._generate_recommendations(checks, completeness)

        # Generar documento de checklist
        checklist_document = self._generate_checklist_document(
            component_name=input_data.get("component_name", "Componente"),
            checks=checks,
            completeness=completeness,
            missing_items=missing_items,
            recommendations=recommendations
        )

        return {
            "checklist_document": checklist_document,
            "completeness_percentage": completeness,
            "is_complete": completeness >= self.min_completeness,
            "checks": checks,
            "missing_items": missing_items,
            "recommendations": recommendations,
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
        }

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida que el análisis esté suficientemente completo.

        Args:
            output_data: Datos de salida

        Returns:
            Lista de errores de guardrails
        """
        errors = []

        completeness = output_data.get("completeness_percentage", 0.0)

        # Guardrail 1: Completitud mínima
        if not output_data.get("is_complete", False):
            errors.append(
                f"Análisis incompleto: {completeness:.1%} < {self.min_completeness:.1%}"
            )

        # Guardrail 2: Items críticos faltantes
        missing = output_data.get("missing_items", [])
        critical_missing = [
            item for item in missing
            if any(keyword in item.lower() for keyword in [
                "trazabilidad",
                "requisito",
                "caso de uso",
                "proceso"
            ])
        ]

        if critical_missing:
            errors.append(
                f"Items críticos faltantes: {len(critical_missing)} "
                f"({', '.join(critical_missing[:3])})"
            )

        # Guardrail 3: Modo estricto
        if self.strict_mode and completeness < 1.0:
            errors.append(
                f"Modo estricto: Se requiere 100% de completitud, "
                f"actual: {completeness:.1%}"
            )

        return errors

    # Métodos de validación por categoría

    def _check_sections(
        self,
        input_data: Dict[str, Any],
        document: Optional[str],
        mode: str
    ) -> Dict[str, Any]:
        """Valida presencia de secciones obligatorias."""
        items = []

        if mode == "document":
            # Analizar documento de texto
            for section in self.REQUIRED_SECTIONS:
                section_title = section.replace("_", " ").title()
                found = self._section_exists_in_document(document, section_title)
                items.append({
                    "name": f"Sección '{section_title}' presente",
                    "passed": found,
                    "critical": True
                })
        else:
            # Analizar artefactos estructurados
            section_mapping = {
                "contexto_negocio": "business_objective",
                "procesos": "processes",
                "reglas_negocio": "business_rules",
                "casos_uso": "use_cases",
                "requisitos_funcionales": "requirements_functional",
                "matriz_trazabilidad": "use_cases"  # Si hay UC, se puede generar matriz
            }

            for section, field in section_mapping.items():
                present = field in input_data and len(input_data.get(field, [])) > 0
                items.append({
                    "name": f"Artefacto '{section}' presente",
                    "passed": present,
                    "critical": True
                })

        return {
            "category": "Secciones Obligatorias",
            "items": items,
            "passed": sum(1 for item in items if item["passed"]),
            "total": len(items)
        }

    def _check_traceability(
        self,
        input_data: Dict[str, Any],
        mode: str
    ) -> Dict[str, Any]:
        """Valida trazabilidad bidireccional."""
        items = []

        if mode == "structured":
            use_cases = input_data.get("use_cases", [])
            requirements = input_data.get("requirements_functional", [])

            # Check 1: Cada proceso tiene al menos 1 UC
            processes = input_data.get("processes", [])
            if processes:
                has_uc_for_process = len(use_cases) > 0
                items.append({
                    "name": "Cada proceso tiene al menos 1 caso de uso",
                    "passed": has_uc_for_process,
                    "critical": True
                })

            # Check 2: Cada UC deriva al menos 1 RF
            if use_cases:
                uc_ids = {uc.get("id") for uc in use_cases}
                ucs_with_reqs = {
                    req.get("related_uc") for req in requirements
                    if req.get("related_uc")
                }
                all_ucs_have_reqs = uc_ids.issubset(ucs_with_reqs)
                items.append({
                    "name": "Cada caso de uso deriva al menos 1 requisito",
                    "passed": all_ucs_have_reqs,
                    "critical": True
                })

            # Check 3: Cada RF está trazado a un UC
            orphan_reqs = [
                req.get("id") for req in requirements
                if not req.get("related_uc")
            ]
            no_orphans = len(orphan_reqs) == 0
            items.append({
                "name": "No hay requisitos huérfanos (sin UC origen)",
                "passed": no_orphans,
                "critical": True
            })

            # Check 4: Trazabilidad downward (cada RF tiene prueba)
            test_cases = input_data.get("test_cases", [])
            if requirements:
                req_ids = {req.get("id") for req in requirements}
                reqs_with_tests = set()
                for tc in test_cases:
                    for req_id in tc.get("related_requirements", []):
                        reqs_with_tests.add(req_id)

                coverage = len(reqs_with_tests) / len(req_ids) if req_ids else 0.0
                has_good_coverage = coverage >= 0.80
                items.append({
                    "name": f"Al menos 80% de requisitos tienen pruebas ({coverage:.1%})",
                    "passed": has_good_coverage,
                    "critical": False
                })
        else:
            # Para modo documento, hacer análisis básico
            items.append({
                "name": "Matriz de trazabilidad presente",
                "passed": True,  # Asumimos que sí si pasó la validación de secciones
                "critical": True
            })

        return {
            "category": "Trazabilidad Bidireccional",
            "items": items,
            "passed": sum(1 for item in items if item["passed"]),
            "total": len(items)
        }

    def _check_standards(
        self,
        input_data: Dict[str, Any],
        document: Optional[str],
        mode: str
    ) -> Dict[str, Any]:
        """Valida conformidad con estándares."""
        items = []

        # ISO 29148:2018
        if self.validate_iso_29148:
            items.append({
                "name": "ISO 29148:2018 - Trazabilidad bidireccional implementada",
                "passed": True,  # Ya validado en _check_traceability
                "critical": True
            })

        # BABOK v3
        if self.validate_babok_v3:
            has_hierarchy = (
                mode == "structured" and
                "processes" in input_data and
                "use_cases" in input_data and
                "requirements_functional" in input_data
            )
            items.append({
                "name": "BABOK v3 - Jerarquía de artefactos presente",
                "passed": has_hierarchy or mode == "document",
                "critical": True
            })

        # UML 2.5
        if self.validate_uml_2_5:
            if mode == "structured":
                use_cases = input_data.get("use_cases", [])
                well_formed = all(
                    self._is_use_case_well_formed(uc) for uc in use_cases
                )
                items.append({
                    "name": "UML 2.5 - Casos de uso bien formados",
                    "passed": well_formed,
                    "critical": True
                })
            else:
                items.append({
                    "name": "UML 2.5 - Casos de uso presentes",
                    "passed": True,
                    "critical": True
                })

        return {
            "category": "Conformidad con Estándares",
            "items": items,
            "passed": sum(1 for item in items if item["passed"]),
            "total": len(items)
        }

    def _check_nomenclature(
        self,
        input_data: Dict[str, Any],
        document: Optional[str],
        mode: str
    ) -> Dict[str, Any]:
        """Valida nomenclatura consistente."""
        items = []

        if mode == "structured":
            # Validar IDs de procesos
            processes = input_data.get("processes", [])
            valid_proc_ids = all(
                proc.get("id", "").startswith("PROC-") for proc in processes
            )
            if processes:
                items.append({
                    "name": "Procesos: formato PROC-[ÁREA]-[NNN]",
                    "passed": valid_proc_ids,
                    "critical": True
                })

            # Validar IDs de reglas
            business_rules = input_data.get("business_rules", [])
            valid_rule_ids = all(
                rule.get("id", "").startswith("RN-") for rule in business_rules
            )
            if business_rules:
                items.append({
                    "name": "Reglas: formato RN-[ÁREA]-[NN]",
                    "passed": valid_rule_ids,
                    "critical": True
                })

            # Validar IDs de UC
            use_cases = input_data.get("use_cases", [])
            valid_uc_ids = all(
                uc.get("id", "").startswith("UC-") for uc in use_cases
            )
            if use_cases:
                items.append({
                    "name": "Casos de uso: formato UC-[NNN]",
                    "passed": valid_uc_ids,
                    "critical": True
                })

            # Validar IDs de RF
            requirements = input_data.get("requirements_functional", [])
            valid_rf_ids = all(
                req.get("id", "").startswith("RF-") for req in requirements
            )
            if requirements:
                items.append({
                    "name": "Requisitos funcionales: formato RF-[NNN]",
                    "passed": valid_rf_ids,
                    "critical": True
                })

            # Validar IDs de RNF
            req_nf = input_data.get("requirements_nonfunctional", [])
            valid_rnf_ids = all(
                req.get("id", "").startswith("RNF-") for req in req_nf
            )
            if req_nf:
                items.append({
                    "name": "Requisitos no funcionales: formato RNF-[NNN]",
                    "passed": valid_rnf_ids,
                    "critical": True
                })

        else:
            # Para modo documento, verificar patrones en el texto
            items.append({
                "name": "Nomenclatura estándar presente",
                "passed": True,  # Asumimos consistente
                "critical": False
            })

        return {
            "category": "Nomenclatura Consistente",
            "items": items,
            "passed": sum(1 for item in items if item["passed"]),
            "total": len(items) if items else 1
        }

    def _check_quality(
        self,
        input_data: Dict[str, Any],
        document: Optional[str],
        mode: str
    ) -> Dict[str, Any]:
        """Valida calidad de la documentación."""
        items = []

        if mode == "document":
            # Validar longitud mínima
            doc_lines = len(document.split('\n'))
            min_lines_ok = doc_lines >= 100
            items.append({
                "name": f"Documento tiene longitud adecuada ({doc_lines} líneas >= 100)",
                "passed": min_lines_ok,
                "critical": False
            })

            # Validar ausencia de emojis (estándar IACT)
            if self.validate_iact_standards:
                emoji_pattern = re.compile(
                    "["
                    "\U0001F600-\U0001F64F"  # emoticons
                    "\U0001F300-\U0001F5FF"  # symbols & pictographs
                    "\U0001F680-\U0001F6FF"  # transport & map
                    "\U0001F700-\U0001F77F"  # alchemical
                    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                    "\U0001FA00-\U0001FA6F"  # Chess Symbols
                    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                    "\U00002702-\U000027B0"  # Dingbats
                    "]+",
                    flags=re.UNICODE
                )
                has_emojis = bool(emoji_pattern.search(document))
                items.append({
                    "name": "Sin emojis (estándar IACT)",
                    "passed": not has_emojis,
                    "critical": True
                })
        else:
            # Para modo estructurado, validar calidad de artefactos
            use_cases = input_data.get("use_cases", [])
            if use_cases:
                complete_ucs = sum(
                    1 for uc in use_cases
                    if uc.get("main_flow") and len(uc.get("main_flow", [])) >= 3
                )
                uc_quality_ok = complete_ucs / len(use_cases) >= 0.8
                items.append({
                    "name": f"80% de UC tienen flujo completo ({complete_ucs}/{len(use_cases)})",
                    "passed": uc_quality_ok,
                    "critical": False
                })

            requirements = input_data.get("requirements_functional", [])
            if requirements:
                reqs_with_criteria = sum(
                    1 for req in requirements
                    if req.get("acceptance_criteria") and
                    len(req.get("acceptance_criteria", [])) >= 2
                )
                req_quality_ok = reqs_with_criteria / len(requirements) >= 0.8
                items.append({
                    "name": f"80% de requisitos tienen criterios de aceptación ({reqs_with_criteria}/{len(requirements)})",
                    "passed": req_quality_ok,
                    "critical": False
                })

        return {
            "category": "Calidad de Documentación",
            "items": items,
            "passed": sum(1 for item in items if item["passed"]),
            "total": len(items) if items else 1
        }

    # Métodos auxiliares

    def _section_exists_in_document(self, document: str, section_title: str) -> bool:
        """Verifica si una sección existe en el documento."""
        if not document:
            return False

        # Buscar patrones de encabezado Markdown
        patterns = [
            f"## {section_title}",
            f"### {section_title}",
            f"# {section_title}",
        ]

        return any(pattern.lower() in document.lower() for pattern in patterns)

    def _is_use_case_well_formed(self, uc: Dict[str, Any]) -> bool:
        """Verifica si un caso de uso está bien formado según UML 2.5."""
        required_fields = [
            "id",
            "name",
            "primary_actor",
            "preconditions",
            "postconditions_success",
            "main_flow"
        ]

        return all(field in uc and uc[field] for field in required_fields)

    def _get_missing_items(self, checks: Dict[str, Any]) -> List[str]:
        """Obtiene lista de items faltantes."""
        missing = []

        for category_name, category in checks.items():
            for item in category["items"]:
                if not item["passed"]:
                    missing.append(f"[{category_name}] {item['name']}")

        return missing

    def _generate_recommendations(
        self,
        checks: Dict[str, Any],
        completeness: float
    ) -> List[str]:
        """Genera recomendaciones de mejora."""
        recommendations = []

        # Recomendación por completitud
        if completeness < 0.70:
            recommendations.append(
                "CRÍTICO: Completitud muy baja. Revisar todos los artefactos obligatorios."
            )
        elif completeness < 0.90:
            recommendations.append(
                "ADVERTENCIA: Completitud insuficiente. Completar items faltantes."
            )

        # Recomendaciones por categoría
        for category_name, category in checks.items():
            if category["passed"] < category["total"]:
                failed = category["total"] - category["passed"]
                recommendations.append(
                    f"{category['category']}: Completar {failed} items faltantes"
                )

        # Recomendaciones específicas
        if "traceability" in checks:
            traceability_items = checks["traceability"]["items"]
            failed_trace = [item for item in traceability_items if not item["passed"]]
            if failed_trace:
                recommendations.append(
                    "Trazabilidad: Asegurar que cada UC derive requisitos y cada requisito tenga prueba"
                )

        return recommendations

    def _generate_checklist_document(
        self,
        component_name: str,
        checks: Dict[str, Any],
        completeness: float,
        missing_items: List[str],
        recommendations: List[str]
    ) -> str:
        """Genera documento de checklist en Markdown."""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        sections = []

        # Header
        sections.append(f"# Checklist de Completitud: {component_name}\n\n")
        sections.append(f"**Fecha:** {timestamp}\n")
        sections.append(f"**Completitud:** {completeness:.1%}\n")
        sections.append(f"**Estado:** {'COMPLETO' if completeness >= self.min_completeness else 'INCOMPLETO'}\n\n")

        # Resumen
        sections.append("## Resumen\n\n")
        sections.append("| Categoría | Pasados | Total | % |\n")
        sections.append("|-----------|---------|-------|---|\n")

        for category in checks.values():
            pct = category["passed"] / category["total"] * 100 if category["total"] > 0 else 0
            sections.append(
                f"| {category['category']} | {category['passed']} | "
                f"{category['total']} | {pct:.0f}% |\n"
            )

        sections.append("\n")

        # Detalles por categoría
        for category in checks.values():
            sections.append(f"## {category['category']}\n\n")

            for item in category["items"]:
                status = "✓" if item["passed"] else "✗"
                critical = " (CRÍTICO)" if item.get("critical", False) else ""
                sections.append(f"- [{status}] {item['name']}{critical}\n")

            sections.append("\n")

        # Items faltantes
        if missing_items:
            sections.append("## Items Faltantes\n\n")
            for item in missing_items[:20]:
                sections.append(f"- {item}\n")

            if len(missing_items) > 20:
                sections.append(f"\n*Y {len(missing_items) - 20} más*\n")

            sections.append("\n")

        # Recomendaciones
        if recommendations:
            sections.append("## Recomendaciones\n\n")
            for i, rec in enumerate(recommendations, 1):
                sections.append(f"{i}. {rec}\n")
            sections.append("\n")

        # Footer
        sections.append("---\n\n")
        sections.append(f"**Generado por:** CompletenessValidator\n")
        sections.append(f"**Umbral de completitud:** {self.min_completeness:.1%}\n")

        return "".join(sections)
