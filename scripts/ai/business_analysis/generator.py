"""
BusinessAnalysisGenerator Agent

Responsabilidad: Generar documentación completa de análisis de negocio integrado.
Input: Especificación de componente/funcionalidad
Output: Documento maestro de análisis (Proceso → UC → Requisitos → Procedimientos)

Estándares:
- ISO/IEC/IEEE 29148:2018 (Requirements Engineering)
- BABOK v3 (Business Analysis Body of Knowledge)
- UML 2.5 (Use Case Modeling)
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import Agent


class BusinessAnalysisGenerator(Agent):
    """
    Agente especializado en generación de análisis de negocio.

    Genera documentación completa incluyendo:
    - Procesos de negocio (BPMN textual)
    - Reglas de negocio (RN-XXX) clasificadas por tipo
    - Casos de uso (UC-XXX) con flujos completos
    - Requisitos funcionales (RF-XXX) con criterios de aceptación
    - Requisitos no funcionales (RNF-XXX) con métricas
    - Procedimientos operacionales (PROC-XXX)
    - Matrices de trazabilidad (RTM)

    Conformidad:
    - ISO 29148:2018: Trazabilidad bidireccional
    - BABOK v3: Jerarquía de artefactos
    - UML 2.5: Casos de uso estándar
    - Proyecto IACT: Sin emojis, nomenclatura consistente
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="BusinessAnalysisGenerator", config=config)

        # Estándares aplicables
        self.standards = {
            "iso_29148": self.get_config("iso_29148", True),
            "babok_v3": self.get_config("babok_v3", True),
            "uml_2_5": self.get_config("uml_2_5", True),
        }

        # Configuración
        self.domain = self.get_config("domain", "general")
        self.include_procedures = self.get_config("include_procedures", True)
        self.include_nfr = self.get_config("include_nfr", True)

        # Contadores para IDs únicos
        self.process_counter = 0
        self.rule_counter = 0
        self.uc_counter = 0
        self.rf_counter = 0
        self.rnf_counter = 0

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Valida la especificación de entrada.

        Args:
            input_data: Datos de entrada a validar

        Returns:
            Lista de errores de validación (vacía si válido)
        """
        errors = []

        # Campos obligatorios
        required_fields = [
            "component_name",      # Nombre del componente
            "domain",              # Dominio del sistema (ej: "Seguridad", "Gestión")
            "business_objective",  # Objetivo de negocio
            "stakeholders",        # Lista de stakeholders
        ]

        for field in required_fields:
            if field not in input_data:
                errors.append(f"Campo obligatorio faltante: '{field}'")
            elif not input_data[field]:
                errors.append(f"Campo obligatorio vacío: '{field}'")

        # Validar estructura de stakeholders
        if "stakeholders" in input_data:
            if not isinstance(input_data["stakeholders"], list):
                errors.append("'stakeholders' debe ser una lista")
            elif len(input_data["stakeholders"]) == 0:
                errors.append("'stakeholders' no puede estar vacía")
            else:
                for i, sh in enumerate(input_data["stakeholders"]):
                    if not isinstance(sh, dict):
                        errors.append(f"stakeholder[{i}] debe ser un diccionario")
                    elif "rol" not in sh or "interes" not in sh:
                        errors.append(
                            f"stakeholder[{i}] debe tener 'rol' e 'interes'"
                        )

        # Validar scope si está presente
        if "scope" in input_data:
            scope = input_data["scope"]
            if not isinstance(scope, dict):
                errors.append("'scope' debe ser un diccionario")
            elif "includes" not in scope and "excludes" not in scope:
                errors.append("'scope' debe tener 'includes' o 'excludes'")

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la generación del análisis de negocio completo.

        Args:
            input_data: Datos de entrada validados

        Returns:
            Diccionario con documento generado y métricas
        """
        component_name = input_data["component_name"]
        domain = input_data["domain"]

        self.logger.info(f"Generando análisis para: {component_name}")

        # Paso 1: Identificar procesos de negocio
        self.logger.info("Paso 1/7: Identificando procesos de negocio")
        processes = self._identify_processes(input_data)

        # Paso 2: Derivar reglas de negocio
        self.logger.info("Paso 2/7: Derivando reglas de negocio")
        business_rules = self._derive_business_rules(processes, input_data)

        # Paso 3: Generar casos de uso
        self.logger.info("Paso 3/7: Generando casos de uso")
        use_cases = self._generate_use_cases(processes, business_rules, input_data)

        # Paso 4: Derivar requisitos funcionales
        self.logger.info("Paso 4/7: Derivando requisitos funcionales")
        requirements_functional = self._derive_requirements_functional(
            use_cases, business_rules
        )

        # Paso 5: Derivar requisitos no funcionales
        self.logger.info("Paso 5/7: Derivando requisitos no funcionales")
        requirements_nonfunctional = []
        if self.include_nfr:
            requirements_nonfunctional = self._derive_requirements_nonfunctional(
                use_cases, input_data
            )

        # Paso 6: Crear procedimientos operacionales
        self.logger.info("Paso 6/7: Creando procedimientos operacionales")
        procedures = []
        if self.include_procedures:
            procedures = self._create_procedures(use_cases, input_data)

        # Paso 7: Generar documento maestro
        self.logger.info("Paso 7/7: Generando documento maestro")
        master_document = self._generate_master_document(
            component_name=component_name,
            domain=domain,
            input_data=input_data,
            processes=processes,
            business_rules=business_rules,
            use_cases=use_cases,
            requirements_functional=requirements_functional,
            requirements_nonfunctional=requirements_nonfunctional,
            procedures=procedures
        )

        # Calcular métricas
        metrics = {
            "processes_count": len(processes),
            "business_rules_count": len(business_rules),
            "use_cases_count": len(use_cases),
            "requirements_functional_count": len(requirements_functional),
            "requirements_nonfunctional_count": len(requirements_nonfunctional),
            "procedures_count": len(procedures),
            "document_size_bytes": len(master_document),
            "document_lines": len(master_document.split('\n')),
        }

        self.logger.info(f"Análisis generado: {metrics['document_lines']} líneas")

        return {
            "document": master_document,
            "component_name": component_name,
            "domain": domain,
            "processes": processes,
            "business_rules": business_rules,
            "use_cases": use_cases,
            "requirements_functional": requirements_functional,
            "requirements_nonfunctional": requirements_nonfunctional,
            "procedures": procedures,
            "metrics": metrics,
            "standards_compliance": self.standards.copy()
        }

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Aplica guardrails a la documentación generada.

        Args:
            output_data: Datos de salida a validar

        Returns:
            Lista de errores de guardrails (vacía si pasa)
        """
        errors = []

        # Guardrail 1: Verificar que se generaron artefactos mínimos
        metrics = output_data.get("metrics", {})

        if metrics.get("processes_count", 0) == 0:
            errors.append("No se generó ningún proceso de negocio")

        if metrics.get("use_cases_count", 0) == 0:
            errors.append("No se generó ningún caso de uso")

        if metrics.get("requirements_functional_count", 0) == 0:
            errors.append("No se generó ningún requisito funcional")

        # Guardrail 2: Verificar que cada UC tiene al menos 1 RF
        ucs = metrics.get("use_cases_count", 0)
        rfs = metrics.get("requirements_functional_count", 0)
        if ucs > 0 and rfs < ucs:
            errors.append(
                f"Insuficientes requisitos: {rfs} RF para {ucs} UC "
                f"(se espera al menos 1 RF por UC)"
            )

        # Guardrail 3: Verificar que no hay emojis (estándar IACT)
        document = output_data.get("document", "")
        emoji_chars = ["🔥", "✅", "❌", "📝", "🎯", "⚡", "🚀", "💡", "🔒", "⭐"]
        found_emojis = [emoji for emoji in emoji_chars if emoji in document]
        if found_emojis:
            errors.append(
                f"Documento contiene emojis (violación estándar IACT): "
                f"{', '.join(found_emojis)}"
            )

        # Guardrail 4: Verificar tamaño mínimo del documento
        doc_lines = metrics.get("document_lines", 0)
        if doc_lines < 100:
            errors.append(
                f"Documento muy corto: {doc_lines} líneas "
                f"(se esperan al menos 100 líneas)"
            )

        # Guardrail 5: Verificar nomenclatura estándar
        processes = output_data.get("processes", [])
        for proc in processes:
            if not proc.get("id", "").startswith("PROC-"):
                errors.append(
                    f"Proceso con ID inválido: {proc.get('id')} "
                    f"(debe empezar con 'PROC-')"
                )

        use_cases = output_data.get("use_cases", [])
        for uc in use_cases:
            if not uc.get("id", "").startswith("UC-"):
                errors.append(
                    f"Caso de uso con ID inválido: {uc.get('id')} "
                    f"(debe empezar con 'UC-')"
                )

        return errors

    # Métodos internos de generación

    def _identify_processes(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identifica procesos de negocio a partir de la especificación.

        Args:
            input_data: Datos de entrada

        Returns:
            Lista de procesos identificados
        """
        processes = []

        # Si se proporcionaron procesos explícitamente, usarlos
        if "processes" in input_data:
            return input_data["processes"]

        # Si no, generar proceso principal automáticamente
        self.process_counter += 1
        component_name = input_data["component_name"]
        domain = input_data["domain"]
        objective = input_data["business_objective"]

        # Generar ID de proceso
        domain_abbr = self._get_domain_abbreviation(domain)
        process_id = f"PROC-{domain_abbr}-{self.process_counter:03d}"

        # Construir proceso básico
        process = {
            "id": process_id,
            "name": f"Proceso de {component_name}",
            "description": objective,
            "actors": self._extract_actors_from_stakeholders(
                input_data.get("stakeholders", [])
            ),
            "inputs": input_data.get("inputs", []),
            "outputs": input_data.get("outputs", []),
            "steps": self._generate_process_steps(component_name, objective),
        }

        processes.append(process)

        return processes

    def _derive_business_rules(
        self,
        processes: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Deriva reglas de negocio de los procesos.

        Args:
            processes: Lista de procesos
            input_data: Datos de entrada

        Returns:
            Lista de reglas de negocio
        """
        business_rules = []

        # Si se proporcionaron reglas explícitamente, usarlas
        if "business_rules" in input_data:
            return input_data["business_rules"]

        # Si no, generar reglas básicas automáticamente
        domain = input_data["domain"]
        domain_abbr = self._get_domain_abbreviation(domain)

        # Generar al menos una regla de restricción básica
        self.rule_counter += 1
        rule = {
            "id": f"RN-{domain_abbr}-{self.rule_counter:02d}",
            "name": f"Validación de Entrada para {input_data['component_name']}",
            "type": "Restricción",
            "category": "Validación",
            "description": "Los datos de entrada deben cumplir con el formato esperado",
            "expression": "SI datos_entrada.validos ENTONCES continuar SINO rechazar",
            "impact": {
                "processes": [p["id"] for p in processes],
                "severity": "Alta"
            }
        }

        business_rules.append(rule)

        return business_rules

    def _generate_use_cases(
        self,
        processes: List[Dict[str, Any]],
        business_rules: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Genera casos de uso a partir de procesos.

        Args:
            processes: Lista de procesos
            business_rules: Lista de reglas de negocio
            input_data: Datos de entrada

        Returns:
            Lista de casos de uso
        """
        use_cases = []

        # Si se proporcionaron UC explícitamente, usarlos
        if "use_cases" in input_data:
            return input_data["use_cases"]

        # Generar UC principal automáticamente
        self.uc_counter += 1
        component_name = input_data["component_name"]

        # Extraer verbo del nombre del componente o usar uno genérico
        verb = self._extract_verb_from_component_name(component_name)

        uc = {
            "id": f"UC-{self.uc_counter:03d}",
            "name": f"{verb} {component_name}",
            "primary_actor": input_data.get("stakeholders", [{}])[0].get("rol", "Usuario"),
            "stakeholders": input_data.get("stakeholders", []),
            "preconditions": self._generate_preconditions(input_data),
            "postconditions_success": self._generate_postconditions_success(input_data),
            "postconditions_failure": self._generate_postconditions_failure(input_data),
            "main_flow": self._generate_main_flow(component_name, processes),
            "alternative_flows": self._generate_alternative_flows(business_rules),
            "related_rules": [r["id"] for r in business_rules],
        }

        use_cases.append(uc)

        return use_cases

    def _derive_requirements_functional(
        self,
        use_cases: List[Dict[str, Any]],
        business_rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deriva requisitos funcionales de casos de uso.

        Args:
            use_cases: Lista de casos de uso
            business_rules: Lista de reglas de negocio

        Returns:
            Lista de requisitos funcionales
        """
        requirements = []

        # Generar al menos 1 RF por caso de uso
        for uc in use_cases:
            self.rf_counter += 1

            req = {
                "id": f"RF-{self.rf_counter:03d}",
                "title": f"Implementar {uc['name']}",
                "priority": "MUST",
                "category": "Funcional Principal",
                "description": f"El sistema debe permitir {uc['name'].lower()}",
                "acceptance_criteria": self._generate_acceptance_criteria(uc),
                "related_uc": uc["id"],
                "related_rules": uc.get("related_rules", []),
            }

            requirements.append(req)

        return requirements

    def _derive_requirements_nonfunctional(
        self,
        use_cases: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Deriva requisitos no funcionales.

        Args:
            use_cases: Lista de casos de uso
            input_data: Datos de entrada

        Returns:
            Lista de requisitos no funcionales
        """
        requirements = []

        # RNF de rendimiento
        self.rnf_counter += 1
        req_performance = {
            "id": f"RNF-{self.rnf_counter:03d}",
            "title": "Tiempo de Respuesta",
            "category": "Rendimiento",
            "description": "El sistema debe responder en tiempo aceptable",
            "metric": "P95 <= 500ms",
            "related_uc": [uc["id"] for uc in use_cases],
        }
        requirements.append(req_performance)

        # RNF de disponibilidad (si es crítico)
        if input_data.get("critical", False):
            self.rnf_counter += 1
            req_availability = {
                "id": f"RNF-{self.rnf_counter:03d}",
                "title": "Disponibilidad del Servicio",
                "category": "Disponibilidad",
                "description": "El servicio debe estar disponible 24/7",
                "metric": "SLA >= 99.5% uptime mensual",
                "related_uc": [uc["id"] for uc in use_cases],
            }
            requirements.append(req_availability)

        return requirements

    def _create_procedures(
        self,
        use_cases: List[Dict[str, Any]],
        input_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Crea procedimientos operacionales.

        Args:
            use_cases: Lista de casos de uso
            input_data: Datos de entrada

        Returns:
            Lista de procedimientos
        """
        procedures = []

        # Generar procedimiento para UC principal
        if use_cases:
            uc = use_cases[0]

            proc = {
                "id": f"PROC-{uc['name'].replace(' ', '-').upper()}-001",
                "name": f"Procedimiento: {uc['name']}",
                "objective": f"Guiar al usuario en {uc['name'].lower()}",
                "responsible": uc["primary_actor"],
                "frequency": "Según necesidad",
                "steps": self._generate_procedure_steps(uc),
            }

            procedures.append(proc)

        return procedures

    def _generate_master_document(
        self,
        component_name: str,
        domain: str,
        input_data: Dict[str, Any],
        processes: List[Dict[str, Any]],
        business_rules: List[Dict[str, Any]],
        use_cases: List[Dict[str, Any]],
        requirements_functional: List[Dict[str, Any]],
        requirements_nonfunctional: List[Dict[str, Any]],
        procedures: List[Dict[str, Any]]
    ) -> str:
        """
        Genera el documento maestro en formato Markdown.

        Args:
            component_name: Nombre del componente
            domain: Dominio del sistema
            input_data: Datos de entrada
            processes: Lista de procesos
            business_rules: Lista de reglas
            use_cases: Lista de casos de uso
            requirements_functional: Lista de RF
            requirements_nonfunctional: Lista de RNF
            procedures: Lista de procedimientos

        Returns:
            Documento en formato Markdown
        """
        timestamp = datetime.now().strftime("%Y-%m-%d")

        doc_sections = []

        # Header
        doc_sections.append(f"# Análisis Integrado: {component_name}\n")
        doc_sections.append(f"**Versión:** 1.0\n")
        doc_sections.append(f"**Fecha:** {timestamp}\n")
        doc_sections.append(f"**Estado:** Borrador\n")
        doc_sections.append(f"**Área:** {domain}\n\n")

        # Contexto
        doc_sections.append("## 1. Contexto de Negocio\n\n")
        doc_sections.append("### 1.1 Objetivo\n\n")
        doc_sections.append(f"{input_data['business_objective']}\n\n")

        doc_sections.append("### 1.2 Stakeholders\n\n")
        doc_sections.append("| Rol | Interés |\n")
        doc_sections.append("|-----|--------|\n")
        for sh in input_data.get("stakeholders", []):
            doc_sections.append(f"| {sh.get('rol', 'N/A')} | {sh.get('interes', 'N/A')} |\n")
        doc_sections.append("\n")

        # Alcance
        if "scope" in input_data:
            doc_sections.append("### 1.3 Alcance\n\n")
            scope = input_data["scope"]
            if "includes" in scope:
                doc_sections.append("**Incluye:**\n")
                for item in scope["includes"]:
                    doc_sections.append(f"- {item}\n")
                doc_sections.append("\n")
            if "excludes" in scope:
                doc_sections.append("**Excluye:**\n")
                for item in scope["excludes"]:
                    doc_sections.append(f"- {item}\n")
                doc_sections.append("\n")

        # Procesos
        doc_sections.append("## 2. Procesos de Negocio\n\n")
        for proc in processes:
            doc_sections.append(f"### {proc['id']}: {proc['name']}\n\n")
            doc_sections.append(f"**Descripción:** {proc['description']}\n\n")
            doc_sections.append(f"**Actores:** {', '.join(proc.get('actors', []))}\n\n")

            if proc.get("steps"):
                doc_sections.append("**Pasos:**\n\n")
                for i, step in enumerate(proc["steps"], 1):
                    doc_sections.append(f"{i}. {step}\n")
                doc_sections.append("\n")

        # Reglas de Negocio
        doc_sections.append("## 3. Reglas de Negocio\n\n")
        for rule in business_rules:
            doc_sections.append(f"### {rule['id']}: {rule['name']}\n\n")
            doc_sections.append(f"**Tipo:** {rule['type']}\n\n")
            doc_sections.append(f"**Categoría:** {rule['category']}\n\n")
            doc_sections.append(f"**Descripción:** {rule['description']}\n\n")
            if rule.get("expression"):
                doc_sections.append(f"**Expresión:** {rule['expression']}\n\n")

        # Casos de Uso
        doc_sections.append("## 4. Casos de Uso\n\n")
        for uc in use_cases:
            doc_sections.append(f"### {uc['id']}: {uc['name']}\n\n")
            doc_sections.append("| Campo | Valor |\n")
            doc_sections.append("|-------|-------|\n")
            doc_sections.append(f"| **Actor Principal** | {uc['primary_actor']} |\n")
            doc_sections.append(f"| **Precondiciones** | {', '.join(uc.get('preconditions', []))} |\n")
            doc_sections.append(f"| **Postcondiciones Éxito** | {', '.join(uc.get('postconditions_success', []))} |\n")
            doc_sections.append("\n")

            if uc.get("main_flow"):
                doc_sections.append("**Flujo Principal:**\n\n")
                doc_sections.append("| Paso | Acción |\n")
                doc_sections.append("|------|--------|\n")
                for i, step in enumerate(uc["main_flow"], 1):
                    doc_sections.append(f"| {i} | {step} |\n")
                doc_sections.append("\n")

        # Requisitos Funcionales
        doc_sections.append("## 5. Requisitos Funcionales\n\n")
        for req in requirements_functional:
            doc_sections.append(f"### {req['id']}: {req['title']}\n\n")
            doc_sections.append(f"**Prioridad:** {req['priority']}\n\n")
            doc_sections.append(f"**Descripción:** {req['description']}\n\n")

            if req.get("acceptance_criteria"):
                doc_sections.append("**Criterios de Aceptación:**\n\n")
                for i, criterion in enumerate(req["acceptance_criteria"], 1):
                    doc_sections.append(f"{i}. {criterion}\n")
                doc_sections.append("\n")

            doc_sections.append(f"**Trazabilidad:** UC: {req.get('related_uc', 'N/A')}\n\n")

        # Requisitos No Funcionales
        if requirements_nonfunctional:
            doc_sections.append("## 6. Requisitos No Funcionales\n\n")
            for req in requirements_nonfunctional:
                doc_sections.append(f"### {req['id']}: {req['title']}\n\n")
                doc_sections.append(f"**Categoría:** {req['category']}\n\n")
                doc_sections.append(f"**Descripción:** {req['description']}\n\n")
                doc_sections.append(f"**Métrica:** {req.get('metric', 'N/A')}\n\n")

        # Procedimientos
        if procedures:
            doc_sections.append("## 7. Procedimientos Operacionales\n\n")
            for proc in procedures:
                doc_sections.append(f"### {proc['id']}: {proc['name']}\n\n")
                doc_sections.append(f"**Objetivo:** {proc['objective']}\n\n")
                doc_sections.append(f"**Responsable:** {proc['responsible']}\n\n")

                if proc.get("steps"):
                    doc_sections.append("**Pasos:**\n\n")
                    doc_sections.append("| Paso | Acción |\n")
                    doc_sections.append("|------|--------|\n")
                    for i, step in enumerate(proc["steps"], 1):
                        doc_sections.append(f"| {i} | {step} |\n")
                    doc_sections.append("\n")

        # Matriz de Trazabilidad
        doc_sections.append("## 8. Matriz de Trazabilidad\n\n")
        doc_sections.append("| Proceso | Caso de Uso | Requisito Funcional | Regla de Negocio |\n")
        doc_sections.append("|---------|-------------|---------------------|------------------|\n")

        for proc in processes:
            for uc in use_cases:
                for req in requirements_functional:
                    if req.get("related_uc") == uc["id"]:
                        rules = ", ".join(req.get("related_rules", []))
                        doc_sections.append(
                            f"| {proc['id']} | {uc['id']} | {req['id']} | {rules if rules else 'N/A'} |\n"
                        )

        doc_sections.append("\n")

        # Footer
        doc_sections.append("---\n\n")
        doc_sections.append(f"**Generado automáticamente por:** BusinessAnalysisGenerator\n")
        doc_sections.append(f"**Fecha de generación:** {timestamp}\n")
        doc_sections.append(f"**Estándares aplicados:** ISO 29148:2018, BABOK v3, UML 2.5\n")

        return "".join(doc_sections)

    # Métodos auxiliares

    def _get_domain_abbreviation(self, domain: str) -> str:
        """Obtiene abreviación del dominio."""
        abbreviations = {
            "Seguridad": "SEC",
            "Autenticación": "AUTH",
            "Autorización": "AUTHZ",
            "Auditoría": "AUD",
            "Gestión": "GEST",
            "Operaciones": "OPS",
            "Reportes": "REP",
            "Configuración": "CONF",
        }
        return abbreviations.get(domain, domain[:4].upper())

    def _extract_actors_from_stakeholders(
        self,
        stakeholders: List[Dict[str, Any]]
    ) -> List[str]:
        """Extrae actores de la lista de stakeholders."""
        return [sh.get("rol", "Usuario") for sh in stakeholders]

    def _generate_process_steps(self, component_name: str, objective: str) -> List[str]:
        """Genera pasos básicos de un proceso."""
        return [
            f"Usuario inicia {component_name.lower()}",
            "Sistema valida entrada",
            "Sistema procesa solicitud",
            "Sistema retorna resultado",
        ]

    def _extract_verb_from_component_name(self, component_name: str) -> str:
        """Extrae verbo del nombre del componente."""
        common_verbs = {
            "recuperación": "Recuperar",
            "autenticación": "Autenticar",
            "validación": "Validar",
            "gestión": "Gestionar",
            "registro": "Registrar",
            "creación": "Crear",
            "actualización": "Actualizar",
            "eliminación": "Eliminar",
        }

        name_lower = component_name.lower()
        for keyword, verb in common_verbs.items():
            if keyword in name_lower:
                return verb

        return "Ejecutar"

    def _generate_preconditions(self, input_data: Dict[str, Any]) -> List[str]:
        """Genera precondiciones básicas."""
        return [
            "Usuario autenticado en el sistema",
            "Sistema operativo",
        ]

    def _generate_postconditions_success(self, input_data: Dict[str, Any]) -> List[str]:
        """Genera postcondiciones de éxito."""
        return [
            "Operación completada exitosamente",
            "Evento registrado en auditoría",
        ]

    def _generate_postconditions_failure(self, input_data: Dict[str, Any]) -> List[str]:
        """Genera postcondiciones de fallo."""
        return [
            "Error registrado",
            "Usuario notificado del fallo",
        ]

    def _generate_main_flow(
        self,
        component_name: str,
        processes: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera flujo principal del caso de uso."""
        return [
            f"Usuario solicita {component_name.lower()}",
            "Sistema valida permisos",
            "Sistema procesa solicitud",
            "Sistema retorna resultado exitoso",
        ]

    def _generate_alternative_flows(
        self,
        business_rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Genera flujos alternativos."""
        flows = []

        if business_rules:
            flows.append({
                "id": "FA-1",
                "name": "Validación Falla",
                "trigger": "Datos de entrada inválidos",
                "steps": [
                    "Sistema detecta datos inválidos",
                    "Sistema muestra mensaje de error",
                    "Retorna a paso 1",
                ]
            })

        return flows

    def _generate_acceptance_criteria(self, uc: Dict[str, Any]) -> List[str]:
        """Genera criterios de aceptación para un requisito."""
        return [
            f"El sistema debe implementar {uc['name'].lower()}",
            "La operación debe completarse en menos de 2 segundos",
            "El sistema debe registrar el evento en auditoría",
        ]

    def _generate_procedure_steps(self, uc: Dict[str, Any]) -> List[str]:
        """Genera pasos de procedimiento operacional."""
        return [
            "Acceder al sistema",
            f"Navegar a {uc['name']}",
            "Completar formulario de entrada",
            "Confirmar operación",
            "Verificar resultado",
        ]
