"""
TraceabilityMatrixGenerator Agent

Responsabilidad: Generar matrices de trazabilidad (RTM) conformes a ISO 29148:2018.
Input: Artefactos de análisis (Procesos, UC, Requisitos, Pruebas, Implementación)
Output: Matrices RTM completas + análisis de gaps + métricas de trazabilidad

Estándares:
- ISO/IEC/IEEE 29148:2018: Requirements Engineering Process
- Trazabilidad bidireccional: Upward (hacia necesidades) y Downward (hacia implementación)
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from .base import Agent


class TraceabilityMatrixGenerator(Agent):
    """
    Agente especializado en generación de matrices de trazabilidad.

    Genera:
    - Matriz Principal: Necesidad → Proceso → UC → Requisito → Prueba → Implementación
    - Matriz Proceso-UC-Requisito
    - Matriz UC-Requisito-Prueba
    - Matriz Reglas-Impacto
    - Análisis de gaps (huérfanos, sin cobertura)
    - Métricas de completitud y cobertura

    Análisis de Gaps:
    - Requisitos huérfanos (sin UC origen)
    - UC sin requisitos derivados
    - Requisitos sin pruebas
    - Requisitos sin implementación
    - Reglas de negocio sin aplicación

    Métricas:
    - Índice de trazabilidad: % de requisitos con trazabilidad completa
    - Índice de cobertura de pruebas: % de requisitos con pruebas
    - Índice de implementación: % de requisitos implementados
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="TraceabilityMatrixGenerator", config=config)

        # Configuración de umbrales
        self.min_traceability_index = self.get_config("min_traceability_index", 0.95)
        self.min_coverage_index = self.get_config("min_coverage_index", 0.90)
        self.include_implementation_status = self.get_config(
            "include_implementation_status", True
        )

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Valida que existan artefactos mínimos para generar matrices.

        Args:
            input_data: Datos de entrada a validar

        Returns:
            Lista de errores de validación (vacía si válido)
        """
        errors = []

        # Artefactos mínimos obligatorios
        required_artifacts = [
            "use_cases",           # Lista de casos de uso
            "requirements_functional",  # Lista de requisitos funcionales
        ]

        for artifact in required_artifacts:
            if artifact not in input_data:
                errors.append(f"Artefacto obligatorio faltante: '{artifact}'")
            elif not isinstance(input_data[artifact], list):
                errors.append(f"'{artifact}' debe ser una lista")
            elif len(input_data[artifact]) == 0:
                errors.append(f"'{artifact}' está vacía")

        # Validar estructura de UC
        if "use_cases" in input_data and isinstance(input_data["use_cases"], list):
            for i, uc in enumerate(input_data["use_cases"]):
                if not isinstance(uc, dict):
                    errors.append(f"use_cases[{i}] debe ser un diccionario")
                elif "id" not in uc:
                    errors.append(f"use_cases[{i}] debe tener 'id'")

        # Validar estructura de requisitos
        if "requirements_functional" in input_data:
            if isinstance(input_data["requirements_functional"], list):
                for i, req in enumerate(input_data["requirements_functional"]):
                    if not isinstance(req, dict):
                        errors.append(
                            f"requirements_functional[{i}] debe ser un diccionario"
                        )
                    elif "id" not in req:
                        errors.append(f"requirements_functional[{i}] debe tener 'id'")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la generación de matrices de trazabilidad.

        Args:
            input_data: Datos de entrada validados

        Returns:
            Diccionario con matrices, gaps y métricas
        """
        self.logger.info("Generando matrices de trazabilidad")

        # Extraer artefactos
        processes = input_data.get("processes", [])
        business_rules = input_data.get("business_rules", [])
        use_cases = input_data["use_cases"]
        requirements_functional = input_data["requirements_functional"]
        requirements_nonfunctional = input_data.get("requirements_nonfunctional", [])
        test_cases = input_data.get("test_cases", [])
        implementations = input_data.get("implementations", [])

        # Combinar todos los requisitos
        all_requirements = requirements_functional + requirements_nonfunctional

        # Matriz Principal
        self.logger.info("Generando matriz principal")
        main_matrix = self._create_main_matrix(
            processes=processes,
            use_cases=use_cases,
            requirements=all_requirements,
            test_cases=test_cases,
            implementations=implementations
        )

        # Matriz Proceso-UC-Requisito
        self.logger.info("Generando matriz Proceso-UC-Requisito")
        process_uc_req_matrix = self._create_process_uc_req_matrix(
            processes=processes,
            use_cases=use_cases,
            requirements=all_requirements
        )

        # Matriz UC-Requisito-Prueba
        self.logger.info("Generando matriz UC-Requisito-Prueba")
        uc_req_test_matrix = self._create_uc_req_test_matrix(
            use_cases=use_cases,
            requirements=all_requirements,
            test_cases=test_cases
        )

        # Matriz Reglas-Impacto
        self.logger.info("Generando matriz Reglas-Impacto")
        rules_impact_matrix = self._create_rules_impact_matrix(
            business_rules=business_rules,
            processes=processes,
            use_cases=use_cases,
            requirements=all_requirements
        )

        # Análisis de Gaps
        self.logger.info("Analizando gaps de trazabilidad")
        gaps = self._analyze_gaps(
            use_cases=use_cases,
            requirements=all_requirements,
            test_cases=test_cases,
            implementations=implementations,
            business_rules=business_rules
        )

        # Calcular Métricas
        self.logger.info("Calculando métricas de trazabilidad")
        metrics = self._calculate_metrics(
            use_cases=use_cases,
            requirements=all_requirements,
            test_cases=test_cases,
            implementations=implementations,
            gaps=gaps
        )

        # Generar documento RTM
        rtm_document = self._generate_rtm_document(
            component_name=input_data.get("component_name", "Componente"),
            main_matrix=main_matrix,
            process_uc_req_matrix=process_uc_req_matrix,
            uc_req_test_matrix=uc_req_test_matrix,
            rules_impact_matrix=rules_impact_matrix,
            gaps=gaps,
            metrics=metrics
        )

        return {
            "rtm_document": rtm_document,
            "main_matrix": main_matrix,
            "process_uc_req_matrix": process_uc_req_matrix,
            "uc_req_test_matrix": uc_req_test_matrix,
            "rules_impact_matrix": rules_impact_matrix,
            "gaps": gaps,
            "metrics": metrics,
            "traceability_index": metrics["traceability_index"],
            "coverage_index": metrics["coverage_index"],
            "implementation_index": metrics.get("implementation_index", 0.0),
        }

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida que las matrices cumplan con estándares de calidad.

        Args:
            output_data: Datos de salida a validar

        Returns:
            Lista de errores de guardrails (vacía si pasa)
        """
        errors = []

        metrics = output_data.get("metrics", {})

        # Guardrail 1: Índice de trazabilidad >= umbral configurado
        traceability_index = metrics.get("traceability_index", 0.0)
        if traceability_index < self.min_traceability_index:
            errors.append(
                f"Índice de trazabilidad bajo: {traceability_index:.1%} "
                f"< {self.min_traceability_index:.1%}"
            )

        # Guardrail 2: Índice de cobertura >= umbral configurado
        coverage_index = metrics.get("coverage_index", 0.0)
        if coverage_index < self.min_coverage_index:
            errors.append(
                f"Índice de cobertura bajo: {coverage_index:.1%} "
                f"< {self.min_coverage_index:.1%}"
            )

        # Guardrail 3: No debe haber requisitos huérfanos
        gaps = output_data.get("gaps", {})
        orphan_reqs = gaps.get("orphan_requirements", [])
        if orphan_reqs:
            errors.append(
                f"Requisitos huérfanos encontrados: {len(orphan_reqs)} "
                f"({', '.join(orphan_reqs[:3])}...)"
            )

        # Guardrail 4: No debe haber UC sin requisitos
        ucs_without_reqs = gaps.get("use_cases_without_requirements", [])
        if ucs_without_reqs:
            errors.append(
                f"Casos de uso sin requisitos: {len(ucs_without_reqs)} "
                f"({', '.join(ucs_without_reqs[:3])}...)"
            )

        # Guardrail 5: Advertencia sobre requisitos sin pruebas (warning, no error)
        reqs_without_tests = gaps.get("requirements_without_tests", [])
        if len(reqs_without_tests) > len(output_data.get("main_matrix", [])) * 0.2:
            # Más del 20% sin pruebas es preocupante
            errors.append(
                f"Muchos requisitos sin pruebas: {len(reqs_without_tests)} "
                f"({len(reqs_without_tests) / len(output_data.get('main_matrix', [1])) * 100:.0f}%)"
            )

        return errors

    # Métodos de generación de matrices

    def _create_main_matrix(
        self,
        processes: List[Dict],
        use_cases: List[Dict],
        requirements: List[Dict],
        test_cases: List[Dict],
        implementations: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Crea la matriz principal de trazabilidad.

        Estructura: Proceso → UC → Requisito → Prueba → Implementación

        Args:
            processes: Lista de procesos
            use_cases: Lista de casos de uso
            requirements: Lista de requisitos
            test_cases: Lista de casos de prueba
            implementations: Lista de implementaciones

        Returns:
            Lista de filas de la matriz
        """
        matrix_rows = []

        for req in requirements:
            # Buscar UC relacionado
            related_uc_id = req.get("related_uc")
            related_uc = next(
                (uc for uc in use_cases if uc.get("id") == related_uc_id),
                None
            )

            # Buscar proceso relacionado (a través del UC)
            related_process = None
            if related_uc and processes:
                # Asumir que el primer proceso está relacionado con todos los UC
                # (esto se puede mejorar con lógica más sofisticada)
                related_process = processes[0] if processes else None

            # Buscar pruebas relacionadas
            related_tests = [
                tc.get("id") for tc in test_cases
                if req.get("id") in tc.get("related_requirements", [])
            ]

            # Buscar implementaciones relacionadas
            related_impls = [
                impl.get("id") for impl in implementations
                if req.get("id") in impl.get("implements_requirements", [])
            ]

            row = {
                "process_id": related_process.get("id") if related_process else "N/A",
                "uc_id": related_uc_id if related_uc_id else "N/A",
                "requirement_id": req.get("id"),
                "requirement_type": "RF" if req.get("id", "").startswith("RF-") else "RNF",
                "priority": req.get("priority", "N/A"),
                "test_ids": related_tests,
                "implementation_ids": related_impls,
                "has_traceability_upward": related_uc_id is not None,
                "has_traceability_downward": len(related_tests) > 0,
                "is_complete": (
                    related_uc_id is not None and
                    len(related_tests) > 0
                ),
            }

            matrix_rows.append(row)

        return matrix_rows

    def _create_process_uc_req_matrix(
        self,
        processes: List[Dict],
        use_cases: List[Dict],
        requirements: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Crea matriz Proceso-UC-Requisito.

        Args:
            processes: Lista de procesos
            use_cases: Lista de casos de uso
            requirements: Lista de requisitos

        Returns:
            Lista de filas de la matriz
        """
        matrix_rows = []

        for proc in processes:
            proc_id = proc.get("id")

            for uc in use_cases:
                uc_id = uc.get("id")

                # Buscar requisitos relacionados con este UC
                related_reqs = [
                    req for req in requirements
                    if req.get("related_uc") == uc_id
                ]

                for req in related_reqs:
                    row = {
                        "process_id": proc_id,
                        "uc_id": uc_id,
                        "requirement_id": req.get("id"),
                        "business_rules": req.get("related_rules", []),
                    }
                    matrix_rows.append(row)

        return matrix_rows

    def _create_uc_req_test_matrix(
        self,
        use_cases: List[Dict],
        requirements: List[Dict],
        test_cases: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Crea matriz UC-Requisito-Prueba.

        Args:
            use_cases: Lista de casos de uso
            requirements: Lista de requisitos
            test_cases: Lista de casos de prueba

        Returns:
            Lista de filas de la matriz
        """
        matrix_rows = []

        for uc in use_cases:
            uc_id = uc.get("id")

            # Requisitos de este UC
            related_reqs = [
                req for req in requirements
                if req.get("related_uc") == uc_id
            ]

            for req in related_reqs:
                req_id = req.get("id")

                # Pruebas de este requisito
                related_tests = [
                    tc for tc in test_cases
                    if req_id in tc.get("related_requirements", [])
                ]

                if related_tests:
                    for test in related_tests:
                        row = {
                            "uc_id": uc_id,
                            "requirement_id": req_id,
                            "test_id": test.get("id"),
                            "test_status": test.get("status", "Pendiente"),
                        }
                        matrix_rows.append(row)
                else:
                    # Requisito sin prueba
                    row = {
                        "uc_id": uc_id,
                        "requirement_id": req_id,
                        "test_id": "N/A",
                        "test_status": "Sin prueba",
                    }
                    matrix_rows.append(row)

        return matrix_rows

    def _create_rules_impact_matrix(
        self,
        business_rules: List[Dict],
        processes: List[Dict],
        use_cases: List[Dict],
        requirements: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Crea matriz de impacto de reglas de negocio.

        Args:
            business_rules: Lista de reglas de negocio
            processes: Lista de procesos
            use_cases: Lista de casos de uso
            requirements: Lista de requisitos

        Returns:
            Lista de filas de la matriz
        """
        matrix_rows = []

        for rule in business_rules:
            rule_id = rule.get("id")

            # Buscar procesos impactados
            impacted_processes = rule.get("impact", {}).get("processes", [])

            # Buscar UC impactados (UC que referencian esta regla)
            impacted_ucs = [
                uc.get("id") for uc in use_cases
                if rule_id in uc.get("related_rules", [])
            ]

            # Buscar requisitos impactados (requisitos que referencian esta regla)
            impacted_reqs = [
                req.get("id") for req in requirements
                if rule_id in req.get("related_rules", [])
            ]

            row = {
                "rule_id": rule_id,
                "rule_type": rule.get("type", "N/A"),
                "rule_name": rule.get("name", "N/A"),
                "impacted_processes": impacted_processes,
                "impacted_use_cases": impacted_ucs,
                "impacted_requirements": impacted_reqs,
                "total_impact": (
                    len(impacted_processes) +
                    len(impacted_ucs) +
                    len(impacted_reqs)
                ),
            }

            matrix_rows.append(row)

        return matrix_rows

    # Métodos de análisis de gaps

    def _analyze_gaps(
        self,
        use_cases: List[Dict],
        requirements: List[Dict],
        test_cases: List[Dict],
        implementations: List[Dict],
        business_rules: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Analiza gaps en la trazabilidad.

        Args:
            use_cases: Lista de casos de uso
            requirements: Lista de requisitos
            test_cases: Lista de casos de prueba
            implementations: Lista de implementaciones
            business_rules: Lista de reglas de negocio

        Returns:
            Diccionario con listas de IDs con gaps
        """
        gaps = {}

        # Gap 1: Requisitos huérfanos (sin UC origen)
        orphan_requirements = [
            req.get("id") for req in requirements
            if not req.get("related_uc")
        ]
        gaps["orphan_requirements"] = orphan_requirements

        # Gap 2: UC sin requisitos derivados
        uc_ids = {uc.get("id") for uc in use_cases}
        uc_with_reqs = {req.get("related_uc") for req in requirements if req.get("related_uc")}
        use_cases_without_requirements = list(uc_ids - uc_with_reqs)
        gaps["use_cases_without_requirements"] = use_cases_without_requirements

        # Gap 3: Requisitos sin pruebas
        req_ids = {req.get("id") for req in requirements}
        reqs_with_tests = set()
        for tc in test_cases:
            for req_id in tc.get("related_requirements", []):
                reqs_with_tests.add(req_id)

        requirements_without_tests = list(req_ids - reqs_with_tests)
        gaps["requirements_without_tests"] = requirements_without_tests

        # Gap 4: Requisitos sin implementación
        reqs_with_impl = set()
        for impl in implementations:
            for req_id in impl.get("implements_requirements", []):
                reqs_with_impl.add(req_id)

        requirements_without_implementation = list(req_ids - reqs_with_impl)
        gaps["requirements_without_implementation"] = requirements_without_implementation

        # Gap 5: Reglas de negocio sin aplicación
        rule_ids = {rule.get("id") for rule in business_rules}
        rules_applied = set()
        for req in requirements:
            for rule_id in req.get("related_rules", []):
                rules_applied.add(rule_id)
        for uc in use_cases:
            for rule_id in uc.get("related_rules", []):
                rules_applied.add(rule_id)

        unapplied_business_rules = list(rule_ids - rules_applied)
        gaps["unapplied_business_rules"] = unapplied_business_rules

        return gaps

    def _calculate_metrics(
        self,
        use_cases: List[Dict],
        requirements: List[Dict],
        test_cases: List[Dict],
        implementations: List[Dict],
        gaps: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Calcula métricas de trazabilidad.

        Args:
            use_cases: Lista de casos de uso
            requirements: Lista de requisitos
            test_cases: Lista de casos de prueba
            implementations: Lista de implementaciones
            gaps: Diccionario de gaps

        Returns:
            Diccionario con métricas
        """
        total_requirements = len(requirements)

        if total_requirements == 0:
            return {
                "traceability_index": 0.0,
                "coverage_index": 0.0,
                "implementation_index": 0.0,
            }

        # Índice de trazabilidad: % de requisitos con trazabilidad completa
        # (tienen UC origen Y tienen prueba)
        reqs_with_complete_traceability = total_requirements - len(
            set(gaps["orphan_requirements"]) | set(gaps["requirements_without_tests"])
        )
        traceability_index = reqs_with_complete_traceability / total_requirements

        # Índice de cobertura: % de requisitos con pruebas
        reqs_with_tests = total_requirements - len(gaps["requirements_without_tests"])
        coverage_index = reqs_with_tests / total_requirements

        # Índice de implementación: % de requisitos implementados
        reqs_implemented = total_requirements - len(
            gaps["requirements_without_implementation"]
        )
        implementation_index = reqs_implemented / total_requirements

        return {
            "total_use_cases": len(use_cases),
            "total_requirements": total_requirements,
            "total_test_cases": len(test_cases),
            "total_implementations": len(implementations),
            "requirements_with_complete_traceability": reqs_with_complete_traceability,
            "requirements_with_tests": reqs_with_tests,
            "requirements_implemented": reqs_implemented,
            "traceability_index": traceability_index,
            "coverage_index": coverage_index,
            "implementation_index": implementation_index,
            "gaps_count": {
                "orphan_requirements": len(gaps["orphan_requirements"]),
                "use_cases_without_requirements": len(
                    gaps["use_cases_without_requirements"]
                ),
                "requirements_without_tests": len(gaps["requirements_without_tests"]),
                "requirements_without_implementation": len(
                    gaps["requirements_without_implementation"]
                ),
                "unapplied_business_rules": len(gaps.get("unapplied_business_rules", [])),
            },
        }

    def _generate_rtm_document(
        self,
        component_name: str,
        main_matrix: List[Dict],
        process_uc_req_matrix: List[Dict],
        uc_req_test_matrix: List[Dict],
        rules_impact_matrix: List[Dict],
        gaps: Dict[str, List[str]],
        metrics: Dict[str, Any]
    ) -> str:
        """
        Genera documento RTM en formato Markdown.

        Args:
            component_name: Nombre del componente
            main_matrix: Matriz principal
            process_uc_req_matrix: Matriz Proceso-UC-Req
            uc_req_test_matrix: Matriz UC-Req-Test
            rules_impact_matrix: Matriz Reglas-Impacto
            gaps: Análisis de gaps
            metrics: Métricas calculadas

        Returns:
            Documento RTM en Markdown
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")

        sections = []

        # Header
        sections.append(f"# Matriz de Trazabilidad de Requisitos (RTM): {component_name}\n\n")
        sections.append(f"**Versión:** 1.0\n")
        sections.append(f"**Fecha:** {timestamp}\n")
        sections.append(f"**Estándar:** ISO/IEC/IEEE 29148:2018\n\n")

        # Resumen de métricas
        sections.append("## 1. Resumen de Trazabilidad\n\n")
        sections.append("| Métrica | Cantidad |\n")
        sections.append("|---------|----------|\n")
        sections.append(f"| Casos de Uso | {metrics['total_use_cases']} |\n")
        sections.append(f"| Requisitos Totales | {metrics['total_requirements']} |\n")
        sections.append(f"| Casos de Prueba | {metrics['total_test_cases']} |\n")
        sections.append(f"| Implementaciones | {metrics['total_implementations']} |\n")
        sections.append(f"| Índice de Trazabilidad | {metrics['traceability_index']:.1%} |\n")
        sections.append(f"| Índice de Cobertura | {metrics['coverage_index']:.1%} |\n")
        sections.append(f"| Índice de Implementación | {metrics['implementation_index']:.1%} |\n")
        sections.append("\n")

        # Matriz Principal
        sections.append("## 2. Matriz Principal de Trazabilidad\n\n")
        sections.append("| Proceso | UC | Requisito | Tipo | Prioridad | Pruebas | Implementación | Completo |\n")
        sections.append("|---------|----|-----------| -----|-----------|---------|----------------|----------|\n")

        for row in main_matrix[:20]:  # Limitar a 20 filas para legibilidad
            tests = ", ".join(row["test_ids"][:2]) if row["test_ids"] else "N/A"
            impls = ", ".join(row["implementation_ids"][:2]) if row["implementation_ids"] else "N/A"
            complete = "Si" if row["is_complete"] else "No"

            sections.append(
                f"| {row['process_id']} | {row['uc_id']} | {row['requirement_id']} | "
                f"{row['requirement_type']} | {row['priority']} | {tests} | {impls} | {complete} |\n"
            )

        if len(main_matrix) > 20:
            sections.append(f"\n*Mostrando 20 de {len(main_matrix)} filas*\n")

        sections.append("\n")

        # Matriz UC-Requisito-Prueba
        sections.append("## 3. Matriz UC-Requisito-Prueba\n\n")
        sections.append("| UC | Requisito | Prueba | Estado |\n")
        sections.append("|----|-----------|--------|--------|\n")

        for row in uc_req_test_matrix[:15]:
            sections.append(
                f"| {row['uc_id']} | {row['requirement_id']} | "
                f"{row['test_id']} | {row['test_status']} |\n"
            )

        if len(uc_req_test_matrix) > 15:
            sections.append(f"\n*Mostrando 15 de {len(uc_req_test_matrix)} filas*\n")

        sections.append("\n")

        # Análisis de Gaps
        sections.append("## 4. Análisis de Gaps\n\n")

        sections.append("### 4.1 Requisitos Huérfanos\n\n")
        if gaps["orphan_requirements"]:
            sections.append("Requisitos sin caso de uso origen:\n\n")
            for req_id in gaps["orphan_requirements"]:
                sections.append(f"- {req_id}\n")
            sections.append("\n")
        else:
            sections.append("No se encontraron requisitos huérfanos.\n\n")

        sections.append("### 4.2 Casos de Uso Sin Requisitos\n\n")
        if gaps["use_cases_without_requirements"]:
            sections.append("Casos de uso que no derivaron requisitos:\n\n")
            for uc_id in gaps["use_cases_without_requirements"]:
                sections.append(f"- {uc_id}\n")
            sections.append("\n")
        else:
            sections.append("Todos los casos de uso tienen requisitos derivados.\n\n")

        sections.append("### 4.3 Requisitos Sin Pruebas\n\n")
        if gaps["requirements_without_tests"]:
            sections.append("Requisitos que necesitan casos de prueba:\n\n")
            for req_id in gaps["requirements_without_tests"][:10]:
                sections.append(f"- {req_id}\n")
            if len(gaps["requirements_without_tests"]) > 10:
                remaining = len(gaps["requirements_without_tests"]) - 10
                sections.append(f"\n*Y {remaining} más*\n")
            sections.append("\n")
        else:
            sections.append("Todos los requisitos tienen cobertura de pruebas.\n\n")

        # Footer
        sections.append("---\n\n")
        sections.append(f"**Generado por:** TraceabilityMatrixGenerator\n")
        sections.append(f"**Fecha:** {timestamp}\n")
        sections.append(f"**Estándar:** ISO/IEC/IEEE 29148:2018\n")

        return "".join(sections)
