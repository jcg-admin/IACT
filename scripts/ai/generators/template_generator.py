"""
TemplateGenerator Agent

Responsabilidad: Generar plantillas reutilizables personalizadas para análisis de negocio.
Input: Tipo de plantilla + parámetros de personalización
Output: Plantilla en formato Markdown lista para usar

Tipos de plantillas soportadas:
- master_document: Documento Maestro de Análisis Integrado
- rtm_matrix: Matriz de Trazabilidad de Requisitos (RTM)
- completeness_checklist: Checklist de Completitud
- business_rule: Regla de Negocio Individual
- use_case: Caso de Uso Detallado
- requirement_spec: Especificación de Requisito Funcional
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import Agent


class TemplateGenerator(Agent):
    """
    Agente especializado en generación de plantillas.

    Genera plantillas personalizables para:
    - Documentos maestros de análisis
    - Matrices de trazabilidad (RTM)
    - Checklists de completitud
    - Reglas de negocio
    - Casos de uso
    - Especificaciones de requisitos

    Características:
    - Plantillas conformes a estándares (ISO 29148, BABOK v3, UML 2.5)
    - Personalizables con parámetros
    - Formato Markdown
    - Sin emojis (estándar IACT)
    - Secciones marcadas con placeholders [COMPLETAR]
    """

    TEMPLATE_TYPES = [
        "master_document",
        "rtm_matrix",
        "completeness_checklist",
        "business_rule",
        "use_case",
        "requirement_spec"
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="TemplateGenerator", config=config)

        self.include_examples = self.get_config("include_examples", True)
        self.include_instructions = self.get_config("include_instructions", True)

    def validate_input(self, input_data: Dict[str, Any]) -> List[str]:
        """
        Valida el tipo de plantilla solicitada.

        Args:
            input_data: Datos de entrada

        Returns:
            Lista de errores de validación
        """
        errors = []

        template_type = input_data.get("template_type")

        if not template_type:
            errors.append("Campo obligatorio faltante: 'template_type'")
        elif template_type not in self.TEMPLATE_TYPES:
            errors.append(
                f"Tipo de plantilla inválido: '{template_type}'. "
                f"Opciones válidas: {', '.join(self.TEMPLATE_TYPES)}"
            )

        return errors

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la generación de plantilla.

        Args:
            input_data: Datos de entrada validados

        Returns:
            Diccionario con plantilla generada y metadatos
        """
        template_type = input_data["template_type"]
        params = input_data.get("parameters", {})

        self.logger.info(f"Generando plantilla: {template_type}")

        # Mapeo de tipos a métodos generadores
        generators = {
            "master_document": self._generate_master_document_template,
            "rtm_matrix": self._generate_rtm_template,
            "completeness_checklist": self._generate_checklist_template,
            "business_rule": self._generate_business_rule_template,
            "use_case": self._generate_use_case_template,
            "requirement_spec": self._generate_requirement_template
        }

        # Generar plantilla
        template_content = generators[template_type](params)

        # Calcular métricas
        line_count = len(template_content.split('\n'))
        placeholder_count = template_content.count('[COMPLETAR]')

        return {
            "template_type": template_type,
            "template_content": template_content,
            "size_bytes": len(template_content),
            "line_count": line_count,
            "placeholder_count": placeholder_count,
            "parameters_used": params,
        }

    def apply_guardrails(self, output_data: Dict[str, Any]) -> List[str]:
        """
        Valida que la plantilla generada sea válida.

        Args:
            output_data: Datos de salida

        Returns:
            Lista de errores de guardrails
        """
        errors = []

        template_content = output_data.get("template_content", "")

        # Guardrail 1: Plantilla no puede estar vacía
        if not template_content or len(template_content) < 50:
            errors.append("Plantilla generada está vacía o muy corta")

        # Guardrail 2: Debe tener al menos un placeholder
        if self.include_instructions and '[COMPLETAR]' not in template_content:
            errors.append("Plantilla no tiene placeholders [COMPLETAR]")

        # Guardrail 3: No debe contener emojis
        emoji_chars = ["🔥", "✅", "❌", "📝", "🎯"]
        if any(emoji in template_content for emoji in emoji_chars):
            errors.append("Plantilla contiene emojis (violación estándar IACT)")

        return errors

    # Generadores de plantillas específicas

    def _generate_master_document_template(self, params: Dict[str, Any]) -> str:
        """Genera plantilla de Documento Maestro de Análisis."""
        component_name = params.get("component_name", "[COMPLETAR: Nombre del Componente]")
        domain = params.get("domain", "[COMPLETAR: Dominio]")

        template = f"""# Análisis Integrado: {component_name}

**Versión:** 1.0
**Fecha:** {datetime.now().strftime("%Y-%m-%d")}
**Estado:** Borrador
**Área:** {domain}

## 1. Contexto de Negocio

### 1.1 Objetivo

[COMPLETAR: Descripción del objetivo de negocio que motiva este componente]

### 1.2 Stakeholders

| Rol | Interés | Nivel de Influencia |
|-----|---------|-------------------|
| [COMPLETAR] | [COMPLETAR] | Alto / Medio / Bajo |

### 1.3 Alcance

**Incluye:**
- [COMPLETAR: Elemento 1]
- [COMPLETAR: Elemento 2]

**Excluye:**
- [COMPLETAR: Elemento 1]
- [COMPLETAR: Elemento 2]

---

## 2. Procesos de Negocio

### PROC-[ÁREA]-[NNN]: [Nombre del Proceso]

**Descripción:**
[COMPLETAR: Descripción narrativa del proceso]

**Actores:**
- [COMPLETAR: Actor 1]
- [COMPLETAR: Actor 2]

**Pasos:**

1. [COMPLETAR: Paso 1]
2. [COMPLETAR: Paso 2]
3. [COMPLETAR: Paso 3]

---

## 3. Reglas de Negocio

### RN-[ÁREA]-[NN]: [Nombre de la Regla]

**Tipo:** Restricción / Hecho / Desencadenador / Inferencia / Cálculo
**Categoría:** [COMPLETAR: Categoría específica]

**Descripción:**
[COMPLETAR: Descripción detallada de la regla]

**Expresión:**
```
SI [COMPLETAR: condición]
ENTONCES [COMPLETAR: acción]
```

---

## 4. Casos de Uso

### UC-[NNN]: [VERBO + OBJETO]

| Campo | Valor |
|-------|-------|
| **Actor Principal** | [COMPLETAR] |
| **Precondiciones** | [COMPLETAR] |
| **Postcondiciones Éxito** | [COMPLETAR] |

**Flujo Principal:**

| Paso | Acción del Actor | Respuesta del Sistema |
|------|-----------------|----------------------|
| 1 | [COMPLETAR] | [COMPLETAR] |
| 2 | [COMPLETAR] | [COMPLETAR] |

---

## 5. Requisitos Funcionales

### RF-[NNN]: [Título del Requisito]

**Prioridad:** MUST / SHOULD / COULD / WON'T
**Categoría:** [COMPLETAR]

**Descripción:**
[COMPLETAR: Descripción detallada]

**Criterios de Aceptación:**
1. [COMPLETAR]
2. [COMPLETAR]
3. [COMPLETAR]

**Trazabilidad:**
- Proceso: [PROC-XXX]
- Caso de Uso: [UC-XXX]
- Reglas: [RN-XXX]

---

## 6. Matriz de Trazabilidad

| Proceso | UC | Requisito | Regla |
|---------|----|-----------| ------|
| [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | [COMPLETAR] |

---

**Generado con:** TemplateGenerator
**Estándares:** ISO 29148:2018, BABOK v3, UML 2.5
"""
        return template

    def _generate_rtm_template(self, params: Dict[str, Any]) -> str:
        """Genera plantilla de Matriz de Trazabilidad (RTM)."""
        component_name = params.get("component_name", "[COMPLETAR: Componente]")

        template = f"""# Matriz de Trazabilidad de Requisitos (RTM): {component_name}

**Versión:** 1.0
**Fecha:** {datetime.now().strftime("%Y-%m-%d")}
**Estándar:** ISO/IEC/IEEE 29148:2018

## 1. Resumen de Trazabilidad

| Métrica | Cantidad |
|---------|----------|
| Procesos | [COMPLETAR] |
| Casos de Uso | [COMPLETAR] |
| Requisitos Funcionales | [COMPLETAR] |
| Casos de Prueba | [COMPLETAR] |
| Índice de Trazabilidad | [COMPLETAR]% |

## 2. Matriz Principal

| Proceso | UC | Requisito | Prioridad | Prueba | Estado |
|---------|----|-----------|-----------| -------|--------|
| [COMPLETAR] | [COMPLETAR] | [COMPLETAR] | MUST/SHOULD | [COMPLETAR] | Pendiente/Completo |

## 3. Análisis de Gaps

### 3.1 Requisitos Sin Caso de Uso (Huérfanos)

- [COMPLETAR: RF-XXX]

### 3.2 Casos de Uso Sin Requisitos

- [COMPLETAR: UC-XXX]

### 3.3 Requisitos Sin Pruebas

- [COMPLETAR: RF-XXX]

## 4. Métricas de Calidad

```
Índice de Trazabilidad = (Requisitos con trazabilidad completa / Total) * 100
Valor actual: [COMPLETAR]%
Meta: >= 95%
```

---

**Generado con:** TemplateGenerator
"""
        return template

    def _generate_checklist_template(self, params: Dict[str, Any]) -> str:
        """Genera plantilla de Checklist de Completitud."""
        template = f"""# Checklist de Completitud del Análisis

**Componente:** [COMPLETAR]
**Fecha:** {datetime.now().strftime("%Y-%m-%d")}

## Instrucciones

Marcar con [X] cada ítem completado.

---

## 1. Contexto de Negocio

- [ ] Objetivo de negocio claramente definido
- [ ] Stakeholders listados con roles e intereses
- [ ] Alcance definido (incluye y excluye)
- [ ] Restricciones documentadas
- [ ] Supuestos explicitados

---

## 2. Procesos de Negocio

- [ ] Al menos 1 proceso principal identificado
- [ ] Proceso tiene ID único (PROC-[ÁREA]-[NNN])
- [ ] Descripción narrativa del proceso
- [ ] Actores identificados
- [ ] Entradas y salidas definidas
- [ ] Diagrama de flujo o BPMN presente

---

## 3. Reglas de Negocio

- [ ] Todas las reglas identificadas
- [ ] Cada regla tiene ID único (RN-[ÁREA]-[NN])
- [ ] Tipo clasificado (Hecho, Restricción, etc.)
- [ ] Descripción detallada
- [ ] Expresión formal (SI-ENTONCES)
- [ ] Impacto documentado

---

## 4. Casos de Uso

- [ ] Todos los UC identificados
- [ ] Cada UC tiene ID único (UC-[NNN])
- [ ] Nombre en formato VERBO + OBJETO
- [ ] Actor principal identificado
- [ ] Precondiciones y postcondiciones definidas
- [ ] Flujo principal documentado
- [ ] Flujos alternativos identificados

---

## 5. Requisitos

- [ ] Todos los RF derivados de UC
- [ ] Cada RF tiene ID único (RF-[NNN])
- [ ] Prioridad definida (MoSCoW)
- [ ] Criterios de aceptación (mín 3)
- [ ] Trazabilidad completa
- [ ] RNF identificados si aplica

---

## 6. Trazabilidad

- [ ] Matriz de trazabilidad completa
- [ ] Cada RF trazado a UC
- [ ] Cada UC trazado a Proceso
- [ ] No hay requisitos huérfanos
- [ ] Trazabilidad bidireccional verificada

---

## 7. Estándares

- [ ] ISO 29148:2018 - Trazabilidad
- [ ] BABOK v3 - Jerarquía
- [ ] UML 2.5 - Casos de uso
- [ ] Sin emojis (estándar IACT)
- [ ] Nomenclatura consistente

---

## Resumen

**Completitud:** [COMPLETAR]%
**Estado:** COMPLETO / INCOMPLETO
**Acción Requerida:** [COMPLETAR]

---

**Generado con:** TemplateGenerator
"""
        return template

    def _generate_business_rule_template(self, params: Dict[str, Any]) -> str:
        """Genera plantilla de Regla de Negocio."""
        rule_id = params.get("rule_id", "RN-[ÁREA]-[NN]")

        template = f"""# Regla de Negocio: [COMPLETAR: Nombre]

**ID:** {rule_id}
**Versión:** 1.0
**Fecha:** {datetime.now().strftime("%Y-%m-%d")}
**Estado:** Borrador

---

## Clasificación

**Tipo:** Hecho / Restricción / Desencadenador / Inferencia / Cálculo
**Categoría:** [COMPLETAR: Categoría específica]
**Criticidad:** Alta / Media / Baja

---

## Descripción

[COMPLETAR: Descripción en lenguaje natural de la regla de negocio]

---

## Expresión Formal

```
SI [COMPLETAR: condición]
ENTONCES [COMPLETAR: acción/resultado]
SI NO [COMPLETAR: acción alternativa]
```

**Ejemplo:**

```
SI edad_usuario >= 18
ENTONCES permitir_registro()
SI NO rechazar_con_mensaje("Debes tener al menos 18 años")
```

---

## Origen

**Fuente:** [COMPLETAR: De dónde proviene]
- [ ] Regulación legal/normativa
- [ ] Política de la empresa
- [ ] Lógica de negocio
- [ ] Restricción técnica

**Referencia:** [COMPLETAR: Número de ley, política, documento]

---

## Validación

**¿Cómo se valida?**
[COMPLETAR: Descripción de cómo el sistema valida que la regla se cumple]

**Momento:**
- [ ] Frontend (entrada de datos)
- [ ] Backend (procesamiento)
- [ ] Base de datos (persistencia)
- [ ] Post-procesamiento (auditoría)

---

## Excepciones

**¿Casos donde NO aplica?**
- [COMPLETAR: Excepción 1]
- [COMPLETAR: Excepción 2]

---

## Impacto

**Procesos Afectados:**
- [COMPLETAR: PROC-XXX]

**Casos de Uso:**
- [COMPLETAR: UC-XXX]

**Requisitos:**
- [COMPLETAR: RF-XXX]

---

## Sanción

**¿Qué ocurre si se viola?**
[COMPLETAR: Descripción de la consecuencia]

**Mensaje al Usuario:**
"[COMPLETAR: Mensaje mostrado]"

---

**Aprobado por:** [COMPLETAR]
**Fecha:** [COMPLETAR]
"""
        return template

    def _generate_use_case_template(self, params: Dict[str, Any]) -> str:
        """Genera plantilla de Caso de Uso."""
        uc_id = params.get("uc_id", "UC-[NNN]")

        template = f"""# Caso de Uso: [COMPLETAR: VERBO + OBJETO]

**ID:** {uc_id}
**Versión:** 1.0
**Fecha:** {datetime.now().strftime("%Y-%m-%d")}

---

## Especificación

| Campo | Valor |
|-------|-------|
| **Actor Principal** | [COMPLETAR] |
| **Stakeholders** | - [COMPLETAR: Rol]: [Interés]<br>- [COMPLETAR: Rol]: [Interés] |
| **Precondiciones** | - [COMPLETAR]<br>- [COMPLETAR] |
| **Postcondiciones Éxito** | - [COMPLETAR]<br>- [COMPLETAR] |
| **Postcondiciones Fallo** | - [COMPLETAR]<br>- [COMPLETAR] |
| **Disparador** | [COMPLETAR: Evento que inicia el UC] |

---

## Flujo Principal

| Paso | Acción del Actor | Respuesta del Sistema |
|------|-----------------|----------------------|
| 1 | [COMPLETAR] | [COMPLETAR] |
| 2 | [COMPLETAR] | [COMPLETAR] |
| 3 | [COMPLETAR] | [COMPLETAR] |
| 4 | - | [COMPLETAR: Acción del sistema] |

---

## Flujos Alternativos

### FA-1: [Nombre del Flujo]

| Paso | Condición | Acción del Sistema |
|------|-----------|-------------------|
| 3a | [COMPLETAR: Condición que dispara] | [COMPLETAR: Acción] |
| 3b | - | Retorna a paso [N] o FIN |

---

## Flujos de Excepción

### FE-1: [Nombre de la Excepción]

| Paso | Error | Acción del Sistema |
|------|-------|-------------------|
| *a | [COMPLETAR: Error en cualquier momento] | [COMPLETAR: Recuperación] |

---

## Requisitos Especiales

**Rendimiento:**
[COMPLETAR: Requisito específico]

**Seguridad:**
[COMPLETAR: Requisito específico]

**Usabilidad:**
[COMPLETAR: Requisito específico]

---

## Trazabilidad

- **Proceso:** [PROC-XXX]
- **Reglas:** [RN-XXX], [RN-YYY]
- **Requisitos derivados:** [RF-XXX], [RF-YYY]

---

**Aprobado por:** [COMPLETAR]
**Fecha:** [COMPLETAR]
"""
        return template

    def _generate_requirement_template(self, params: Dict[str, Any]) -> str:
        """Genera plantilla de Especificación de Requisito."""
        req_id = params.get("req_id", "RF-[NNN]")

        template = f"""# Requisito Funcional: [COMPLETAR: Título]

**ID:** {req_id}
**Versión:** 1.0
**Fecha:** {datetime.now().strftime("%Y-%m-%d")}
**Estado:** Borrador

---

## Especificación

**Prioridad:** MUST / SHOULD / COULD / WON'T (MoSCoW)
**Categoría:** [COMPLETAR: Categoría específica]

**Descripción:**
[COMPLETAR: Descripción detallada del requisito funcional]

---

## Criterios de Aceptación

1. [COMPLETAR: Criterio 1]
2. [COMPLETAR: Criterio 2]
3. [COMPLETAR: Criterio 3]

---

## Entrada/Salida

**Entrada:**
- parámetro1: tipo (descripción)
- parámetro2: tipo (descripción)

**Salida:**
- resultado: tipo (descripción)

---

## Proceso

[COMPLETAR: Descripción paso a paso del proceso que implementa el requisito]

1. [COMPLETAR: Paso 1]
2. [COMPLETAR: Paso 2]
3. [COMPLETAR: Paso 3]

---

## Reglas de Negocio Aplicables

- **RN-[XXX]:** [Nombre]
- **RN-[YYY]:** [Nombre]

---

## Validaciones

- [COMPLETAR: Validación 1]
- [COMPLETAR: Validación 2]

---

## Manejo de Errores

| Error | Acción |
|-------|--------|
| [COMPLETAR: Error 1] | [COMPLETAR: Acción] |
| [COMPLETAR: Error 2] | [COMPLETAR: Acción] |

---

## Trazabilidad

- **Proceso:** [PROC-XXX]
- **Caso de Uso:** [UC-XXX] (paso [N])
- **Prueba:** [TS-RF-XXX-001]

---

## Referencias

- [COMPLETAR: Ruta al documento detallado]
- [COMPLETAR: Regulación o estándar aplicable]

---

**Aprobado por:** [COMPLETAR]
**Fecha:** [COMPLETAR]
"""
        return template
