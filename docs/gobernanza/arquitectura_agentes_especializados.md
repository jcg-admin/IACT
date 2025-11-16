---
id: DOC-DEV-AGENTES-SPEC
tipo: documentacion
categoria: desarrollo-avanzado
version: 1.0.0
fecha_creacion: 2025-11-04
propietario: equipo-desarrollo
relacionados: ["DOC-DEV-AGENTES", "DOC-GOB-ESTANDARES"]
---
# Arquitectura de Agentes Especializados

## Propósito

Documentar la arquitectura correcta de agentes: **múltiples agentes especializados** en lugar de un solo agente monolítico.

**Principio fundamental**: Un agente = Una responsabilidad (Single Responsibility Principle)

---

## Por Qué Separar en N Agentes

### Problema: Agente Monolítico

```
┌─────────────────────────────────────────┐
│     AGENTE MONOLÍTICO (MALO)            │
├─────────────────────────────────────────┤
│  - Planifica                            │
│  - Edita                                │
│  - Verifica                             │
│  - Reporta                              │
│  - Maneja errores                       │
│  - Rollback                             │
│  - Logging                              │
│  - Notificaciones                       │
└─────────────────────────────────────────┘

Problemas:
❌ Difícil de mantener
❌ Imposible de testear unitariamente
❌ No reusable
❌ Puntos de falla ocultos
❌ Difícil de debuggear
❌ Acoplamiento alto
```

### Solución: Agentes Especializados

```
┌────────────────────────────────────────────────────────────┐
│              ARQUITECTURA DE AGENTES (BUENA)               │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   SCANNER   │───▶│   PLANNER   │───▶│   EDITOR    │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│         │                  │                  │            │
│         ▼                  ▼                  ▼            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  ANALYZER   │    │  VALIDATOR  │    │  VERIFIER   │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                           │                                │
│                           ▼                                │
│                    ┌─────────────┐                         │
│                    │  REPORTER   │                         │
│                    └─────────────┘                         │
│                           │                                │
│                           ▼                                │
│                    ┌─────────────┐                         │
│                    │ ORCHESTRATOR│                         │
│                    └─────────────┘                         │
│                                                             │
└────────────────────────────────────────────────────────────┘

Beneficios:
✓ Mantenible
✓ Testeable
✓ Reusable
✓ Composable
✓ Debuggeable
✓ Bajo acoplamiento
```

---

## Arquitectura de Agentes para Remoción de Emojis

### Implementación Correcta (N Agentes)

```python
# scripts/agents/emoji_removal_pipeline.py

from dataclasses import dataclass
from typing import List, Dict, Set
from pathlib import Path

# ============================================================================
# AGENTE 1: SCANNER (Escaneo de archivos)
# ============================================================================
@dataclass
class ScanResult:
    """Resultado del escaneo"""
    files_with_emojis: List[Path]
    emoji_count: Dict[Path, int]
    total_emojis: int
    scan_time: float

class EmojiScanner:
    """
    Responsabilidad: Escanear repositorio y encontrar archivos con emojis

    Input: Directorio raíz
    Output: ScanResult
    """

    EMOJI_PATTERN = r"[\\x{1F300}-\\x{1FAD6}]|✅|❌|⚠️|🔴|🟡|🟢"

    def scan(self, root_dir: Path) -> ScanResult:
        """Escanea directorio buscando emojis"""
        # Usa herramientas: Glob, Grep
        pass

    def is_ignored(self, path: Path) -> bool:
        """Verifica si archivo debe ignorarse (.git, node_modules, etc)"""
        pass

# ============================================================================
# AGENTE 2: ANALYZER (Análisis de patrones)
# ============================================================================
@dataclass
class AnalysisResult:
    """Resultado del análisis"""
    emoji_types: Dict[str, int]  # ✅ → 50, ❌ → 30, etc
    file_categories: Dict[str, List[Path]]  # "tables" → [file1, file2]
    transformation_rules: Dict[str, str]  # ✅ → "OK"
    complexity_score: Dict[Path, int]  # archivo → score

class EmojiAnalyzer:
    """
    Responsabilidad: Analizar patrones de emojis y contexto

    Input: ScanResult
    Output: AnalysisResult
    """

    def analyze(self, scan_result: ScanResult) -> AnalysisResult:
        """Analiza patrones de uso de emojis"""
        # Identifica contexto (tablas, títulos, listas, etc)
        pass

    def categorize_files(self, files: List[Path]) -> Dict[str, List[Path]]:
        """Categoriza archivos por complejidad"""
        # "simple" → pocos emojis, patrones claros
        # "complex" → muchos emojis, patrones variados
        # "critical" → archivos importantes (README, docs principales)
        pass

# ============================================================================
# AGENTE 3: PLANNER (Planificación de estrategia)
# ============================================================================
@dataclass
class ExecutionPlan:
    """Plan de ejecución"""
    strategy: str  # "manual", "script", "hybrid"
    manual_files: List[Path]
    script_files: List[Path]
    estimated_time: float
    risks: List[str]

class ExecutionPlanner:
    """
    Responsabilidad: Decidir estrategia óptima de ejecución

    Input: AnalysisResult
    Output: ExecutionPlan
    """

    MANUAL_THRESHOLD = 10  # Archivos con >10 emojis complejos → manual

    def plan(self, analysis: AnalysisResult) -> ExecutionPlan:
        """Genera plan de ejecución óptimo"""
        # Decide qué archivos manejar manualmente
        # Decide qué archivos procesar con script
        # Estima tiempo
        # Identifica riesgos
        pass

# ============================================================================
# AGENTE 4: EDITOR (Ejecución de transformaciones)
# ============================================================================
@dataclass
class EditResult:
    """Resultado de edición"""
    files_modified: List[Path]
    transformations_applied: int
    errors: List[Dict]
    rollback_info: Dict

class EmojiEditor:
    """
    Responsabilidad: Ejecutar transformaciones de emojis

    Input: ExecutionPlan, AnalysisResult
    Output: EditResult
    """

    def edit_manual(self, files: List[Path], rules: Dict[str, str]) -> EditResult:
        """Edita archivos manualmente con Edit tool"""
        pass

    def edit_script(self, files: List[Path], rules: Dict[str, str]) -> EditResult:
        """Edita archivos con script bash/sed"""
        pass

    def create_backup(self, files: List[Path]) -> Path:
        """Crea backup antes de modificar"""
        pass

# ============================================================================
# AGENTE 5: VALIDATOR (Validación de reglas)
# ============================================================================
@dataclass
class ValidationResult:
    """Resultado de validación"""
    is_valid: bool
    violations: List[str]
    warnings: List[str]

class TransformationValidator:
    """
    Responsabilidad: Validar que transformaciones siguen reglas

    Input: EditResult, reglas del proyecto
    Output: ValidationResult
    """

    def validate(self, edit_result: EditResult) -> ValidationResult:
        """Valida transformaciones contra reglas"""
        # Verifica que checkboxes estén intactos
        # Verifica que código no fue modificado
        # Verifica que contenido no fue eliminado
        pass

    def check_checkboxes_intact(self, file: Path) -> bool:
        """Verifica que checkboxes no fueron modificados"""
        pass

    def check_code_blocks_preserved(self, file: Path) -> bool:
        """Verifica que bloques de código están intactos"""
        pass

# ============================================================================
# AGENTE 6: VERIFIER (Verificación de resultado)
# ============================================================================
@dataclass
class VerificationResult:
    """Resultado de verificación"""
    emojis_remaining: int
    files_with_emojis: List[Path]
    is_complete: bool
    confidence_score: float

class ResultVerifier:
    """
    Responsabilidad: Verificar que no quedan emojis

    Input: EditResult
    Output: VerificationResult
    """

    def verify(self, edit_result: EditResult) -> VerificationResult:
        """Verifica ausencia de emojis"""
        # Ejecuta grep exhaustivo
        # Cuenta emojis remanentes
        # Calcula confidence score
        pass

    def deep_scan(self, files: List[Path]) -> int:
        """Escaneo profundo de emojis"""
        pass

# ============================================================================
# AGENTE 7: REPORTER (Generación de reportes)
# ============================================================================
@dataclass
class Report:
    """Reporte final"""
    summary: str
    files_processed: int
    transformations: int
    time_taken: float
    success: bool
    details: Dict

class ReportGenerator:
    """
    Responsabilidad: Generar reportes detallados

    Input: Todos los resultados anteriores
    Output: Report
    """

    def generate(
        self,
        scan: ScanResult,
        analysis: AnalysisResult,
        plan: ExecutionPlan,
        edit: EditResult,
        validation: ValidationResult,
        verification: VerificationResult
    ) -> Report:
        """Genera reporte completo"""
        pass

    def generate_markdown(self, report: Report) -> str:
        """Genera reporte en markdown"""
        pass

    def generate_json(self, report: Report) -> str:
        """Genera reporte en JSON para CI/CD"""
        pass

# ============================================================================
# AGENTE 8: ORCHESTRATOR (Coordinación)
# ============================================================================
class PipelineOrchestrator:
    """
    Responsabilidad: Coordinar ejecución de todos los agentes

    Input: Configuración
    Output: Report final
    """

    def __init__(self):
        self.scanner = EmojiScanner()
        self.analyzer = EmojiAnalyzer()
        self.planner = ExecutionPlanner()
        self.editor = EmojiEditor()
        self.validator = TransformationValidator()
        self.verifier = ResultVerifier()
        self.reporter = ReportGenerator()

    def execute(self, root_dir: Path) -> Report:
        """Ejecuta pipeline completo"""

        # 1. Escaneo
        scan_result = self.scanner.scan(root_dir)
        if scan_result.total_emojis == 0:
            return self.reporter.generate_early_exit("No emojis found")

        # 2. Análisis
        analysis_result = self.analyzer.analyze(scan_result)

        # 3. Planificación
        plan = self.planner.plan(analysis_result)

        # 4. Ejecución
        edit_result = self.editor.execute(plan, analysis_result)

        # 5. Validación
        validation = self.validator.validate(edit_result)
        if not validation.is_valid:
            self.editor.rollback(edit_result)
            raise ValidationError(validation.violations)

        # 6. Verificación
        verification = self.verifier.verify(edit_result)
        if not verification.is_complete:
            # Retry con archivos que fallaron
            retry_result = self.retry_failed(verification.files_with_emojis)
            verification = self.verifier.verify(retry_result)

        # 7. Reporte
        report = self.reporter.generate(
            scan_result,
            analysis_result,
            plan,
            edit_result,
            validation,
            verification
        )

        return report

    def retry_failed(self, files: List[Path]) -> EditResult:
        """Reintenta archivos que fallaron"""
        pass

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================
def main():
    """Ejecuta pipeline de remoción de emojis"""
    orchestrator = PipelineOrchestrator()

    report = orchestrator.execute(Path("."))

    print(report.summary)

    # Guardar reporte
    Path("reports/emoji_removal_report.json").write_text(
        orchestrator.reporter.generate_json(report)
    )

    # Exit code
    exit(0 if report.success else 1)

if __name__ == "__main__":
    main()
```

---

## Beneficios de N Agentes Especializados

### 1. Mantenibilidad

**Antes (1 agente)**:
```python
# Modificar comportamiento de verificación
# → Hay que entender TODO el agente (500 líneas)
# → Riesgo de romper otras partes
```

**Después (N agentes)**:
```python
# Modificar comportamiento de verificación
# → Solo editar ResultVerifier (50 líneas)
# → Cero riesgo de afectar otras partes
```

### 2. Testeabilidad

**Antes**:
```python
# Test del agente monolítico
def test_emoji_removal():
    # Necesita setup completo de:
    # - Sistema de archivos
    # - Git
    # - Herramientas externas
    # - Mock de 10 funciones
    pass  # Pesadilla de mantener
```

**Después**:
```python
# Test de agente individual
def test_scanner():
    scanner = EmojiScanner()
    result = scanner.scan(Path("test_data"))
    assert result.total_emojis == 5
    # Simple, rápido, confiable

def test_analyzer():
    analysis = EmojiAnalyzer()
    result = analysis.analyze(mock_scan_result)
    assert result.emoji_types["✅"] == 10
    # Independiente del scanner

def test_planner():
    planner = ExecutionPlanner()
    plan = planner.plan(mock_analysis_result)
    assert plan.strategy == "hybrid"
    # Solo lógica de negocio
```

### 3. Reusabilidad

**Antes**:
```python
# Necesito escanear emojis en otro contexto
# → Tengo que copiar código del agente monolítico
# → O ejecutar TODO el agente (overhead)
```

**Después**:
```python
# Necesito escanear emojis en otro contexto
scanner = EmojiScanner()
result = scanner.scan(Path("./docs"))
# Listo! Solo uso lo que necesito
```

### 4. Composabilidad

**Antes**:
```python
# Quiero cambiar estrategia de edición
# → Modificar agente monolítico (riesgoso)
```

**Después**:
```python
# Quiero cambiar estrategia de edición
class FastEditor(EmojiEditor):
    """Editor optimizado para velocidad"""
    pass

orchestrator.editor = FastEditor()
# Plug and play!
```

### 5. Debuggeabilidad

**Antes**:
```python
# Error en línea 350 del agente monolítico
# → ¿En qué fase falló?
# → ¿Scanner? ¿Editor? ¿Verifier?
# → Difícil de saber
```

**Después**:
```python
# Error en ResultVerifier.verify()
# → Inmediatamente sé que es problema de verificación
# → Log específico del agente
# → Fácil de reproducir aisladamente
```

---

## Patrones de Comunicación entre Agentes

### 1. Pipeline Lineal (Simple)

```
Scanner → Analyzer → Planner → Editor → Verifier → Reporter
```

**Uso**: Cuando cada agente depende del anterior secuencialmente

**Ventajas**:
- Simple de entender
- Fácil de debuggear
- Predecible

**Desventajas**:
- No hay paralelización
- Un fallo bloquea todo

### 2. Pipeline con Validación (Recomendado)

```
Scanner → Analyzer → Planner → Editor → Validator
                                    ↓           ↓
                                    ├──────────→ Verifier → Reporter
                                    │
                                    └→ Rollback (si falla)
```

**Uso**: Cuando necesitas validación con rollback

**Ventajas**:
- Safe by default
- Recuperación automática

### 3. Pipeline Paralelo (Avanzado)

```
         ┌→ Analyzer 1 ┐
Scanner ─┼→ Analyzer 2 ┼→ Aggregator → Planner → ...
         └→ Analyzer 3 ┘
```

**Uso**: Cuando múltiples análisis independientes

**Ventajas**:
- Velocidad (parallel)
- Escalable

**Desventajas**:
- Complejidad de coordinación

### 4. Pipeline con Retry (Robusto)

```
Editor → Verifier ─→ Success → Reporter
           ↓
         Failure
           ↓
      Retry Strategy
           ↓
      Editor (retry)
```

**Uso**: Cuando hay operaciones que pueden fallar temporalmente

---

## Interfaz entre Agentes

### Contrato de Datos

Cada agente tiene:
- **Input**: Tipo de dato específico
- **Output**: Tipo de dato específico
- **Errores**: Excepciones bien definidas

```python
from typing import Protocol

class Agent(Protocol):
    """Interfaz de agente"""

    def execute(self, input_data: Any) -> Any:
        """Ejecuta el agente"""
        ...

    def validate_input(self, input_data: Any) -> bool:
        """Valida input antes de procesar"""
        ...

    def handle_error(self, error: Exception) -> None:
        """Maneja errores"""
        ...

# Ejemplo: Scanner
class EmojiScanner(Agent):
    def execute(self, root_dir: Path) -> ScanResult:
        self.validate_input(root_dir)
        # ... lógica
        return ScanResult(...)

    def validate_input(self, root_dir: Path) -> bool:
        if not root_dir.exists():
            raise ValueError(f"Directory not found: {root_dir}")
        return True
```

---

## Implementación en Claude Code

### Cómo Usar el Task Tool Correctamente

**INCORRECTO** (1 agente hace todo):
```python
Task(
    description="Remove all emojis",
    prompt="""
    1. Scan for emojis
    2. Analyze patterns
    3. Plan strategy
    4. Edit files
    5. Verify result
    6. Generate report
    """,
    subagent_type="general-purpose"
)
# Problema: Agente monolítico
```

**CORRECTO** (N agentes especializados):
```python
# Agente 1: Scanner
scan_result = Task(
    description="Scan for emojis",
    prompt="""
    Escanea el repositorio y encuentra todos los archivos con emojis.

    Usa:
    - Glob para encontrar archivos .md
    - Grep para buscar patrón de emojis

    Retorna:
    - Lista de archivos con emojis
    - Count de emojis por archivo
    """,
    subagent_type="Explore"
)

# Agente 2: Analyzer
analysis = Task(
    description="Analyze emoji patterns",
    prompt=f"""
    Analiza los archivos encontrados: {scan_result}

    Identifica:
    - Tipo de emojis (✅, ❌, etc)
    - Contexto (tablas, títulos, listas)
    - Complejidad de cada archivo

    Retorna:
    - Categorización de archivos
    - Reglas de transformación
    """,
    subagent_type="general-purpose"
)

# Agente 3: Editor (simple)
edit_result_simple = Task(
    description="Edit simple files",
    prompt=f"""
    Edita los archivos simples: {analysis['simple_files']}

    Reglas: {analysis['transformation_rules']}

    Usa Edit tool con find/replace.

    Retorna:
    - Archivos modificados
    - Errores si los hay
    """,
    subagent_type="general-purpose"
)

# Agente 4: Editor (complex)
edit_result_complex = Task(
    description="Edit complex files",
    prompt=f"""
    Edita los archivos complejos: {analysis['complex_files']}

    Reglas: {analysis['transformation_rules']}

    Crea un script bash/sed para procesar en batch.

    Retorna:
    - Script generado
    - Archivos procesados
    """,
    subagent_type="general-purpose"
)

# Agente 5: Verifier
verification = Task(
    description="Verify no emojis remain",
    prompt="""
    Verifica que no queden emojis en el repositorio.

    Usa grep exhaustivo con todos los patrones de emoji.

    Retorna:
    - Count de emojis encontrados
    - Archivos con emojis si los hay
    - Confidence score
    """,
    subagent_type="Explore"
)

# Agente 6: Reporter
report = Task(
    description="Generate final report",
    prompt=f"""
    Genera reporte final con:

    - Scan result: {scan_result}
    - Analysis: {analysis}
    - Edit results: {edit_result_simple}, {edit_result_complex}
    - Verification: {verification}

    Formato:
    - Archivos procesados
    - Transformaciones aplicadas
    - Confirmación de 0 emojis
    """,
    subagent_type="general-purpose"
)
```

**Beneficios**:
- Cada agente es pequeño y enfocado
- Fácil de debuggear (sabes qué agente falló)
- Reusable (puedes usar Scanner en otro contexto)
- Testeable (puedes testear cada paso)

---

## Ejecución Paralela de Agentes

Cuando los agentes son independientes, ejecutar en paralelo:

```python
# Claude Code permite múltiples Task en un solo mensaje

# PARALELO (más rápido)
results = [
    Task(description="Scan docs/", prompt="...", subagent_type="Explore"),
    Task(description="Scan api/", prompt="...", subagent_type="Explore"),
    Task(description="Scan scripts/", prompt="...", subagent_type="Explore"),
]
# Los 3 agentes corren simultáneamente

# SECUENCIAL (cuando hay dependencias)
scan = Task(description="Scan", prompt="...", subagent_type="Explore")
# Esperar resultado
analysis = Task(description="Analyze", prompt=f"Analiza {scan}", ...)
```

---

## Ejemplo Real: Pipeline de Validación de Restricciones

### Arquitectura Multi-Agente

```python
# Agente 1: Security Scanner
security_scan = Task(
    description="Scan security issues",
    prompt="""
    Escanea el código en api/ buscando:
    - Uso de email (prohibido)
    - Uso de Sentry (prohibido)
    - Uso de Redis para sesiones (prohibido)
    - Código peligroso (eval, exec, pickle)

    Retorna:
    - Violaciones encontradas
    - Archivos afectados
    """,
    subagent_type="Explore"
)

# Agente 2: Config Validator
config_validation = Task(
    description="Validate Django config",
    prompt="""
    Valida configuración en api/callcentersite/settings/:
    - DEBUG = False en producción
    - SECRET_KEY desde env
    - SESSION_ENGINE configurado
    - JWT settings correctos

    Retorna:
    - Config OK/FAIL
    - Items faltantes
    """,
    subagent_type="Explore"
)

# Agente 3: Database Router Tester
db_test = Task(
    description="Test database router",
    prompt="""
    Crea y ejecuta tests para database_router.py:
    - Test de lectura (debe ir a ivr_readonly)
    - Test de escritura (debe lanzar ValueError)
    - Test de migraciones (debe bloquearse en IVR)

    Retorna:
    - Tests pasados/fallidos
    - Evidencia
    """,
    subagent_type="general-purpose"
)

# Agente 4: Report Aggregator
final_report = Task(
    description="Aggregate validation report",
    prompt=f"""
    Agrega resultados:

    Security: {security_scan}
    Config: {config_validation}
    DB Router: {db_test}

    Genera:
    - Score global
    - Lista de bloqueadores
    - Recomendaciones
    """,
    subagent_type="general-purpose"
)
```

---

## Mejores Prácticas

### 1. Un Agente = Una Responsabilidad

BIEN:
```python
class EmojiScanner:
    """Solo escanea, no modifica"""

class EmojiEditor:
    """Solo edita, no verifica"""

class ResultVerifier:
    """Solo verifica, no edita"""
```

MAL:
```python
class EmojiProcessor:
    """Escanea, edita, verifica, reporta"""  # Hace demasiado
```

### 2. Interfaces Claras

```python
# Input/Output explícitos
def scan(root_dir: Path) -> ScanResult:
    """
    Input: Path del directorio
    Output: ScanResult con archivos encontrados
    Raises: FileNotFoundError si directorio no existe
    """
    pass
```

### 3. Idempotencia

```python
# Agente debe ser idempotente
scanner = EmojiScanner()
result1 = scanner.scan(path)
result2 = scanner.scan(path)
assert result1 == result2  # Mismo resultado
```

### 4. Sin Estado Compartido

MAL:
```python
class EmojiProcessor:
    def __init__(self):
        self.state = {}  # Estado compartido (peligroso)
```

BIEN:
```python
class EmojiScanner:
    def scan(self, path: Path) -> ScanResult:
        # Sin estado, solo puro input → output
        pass
```

### 5. Logging Estructurado

```python
class EmojiEditor:
    def edit(self, files: List[Path]) -> EditResult:
        logger.info(
            "Starting edit",
            extra={
                "agent": "EmojiEditor",
                "files_count": len(files),
                "timestamp": datetime.now()
            }
        )
        # ...
        logger.info(
            "Edit complete",
            extra={
                "agent": "EmojiEditor",
                "files_modified": len(result.files_modified),
                "errors": len(result.errors)
            }
        )
```

---

## Comparación: 1 Agente vs N Agentes

| Aspecto | 1 Agente Monolítico | N Agentes Especializados |
|---------|---------------------|--------------------------|
| **Complejidad individual** | Alta (500+ líneas) | Baja (50-100 líneas) |
| **Tiempo de desarrollo inicial** | Rápido | Más lento |
| **Mantenibilidad** | Difícil | Fácil |
| **Testeabilidad** | Complicada | Simple |
| **Reusabilidad** | Baja | Alta |
| **Debuggeabilidad** | Difícil | Fácil |
| **Paralelización** | Imposible | Natural |
| **Acoplamiento** | Alto | Bajo |
| **Riesgo de regresión** | Alto | Bajo |
| **Curva de aprendizaje** | Empinada | Gradual |

**Conclusión**: N agentes especializados es SIEMPRE mejor a largo plazo.

---

## Cuándo Usar Qué Tipo de Agente

| Tipo | Uso | Ejemplo |
|------|-----|---------|
| **Explore** | Búsqueda y navegación de código | Scanner, Verifier |
| **general-purpose** | Transformaciones y lógica compleja | Editor, Planner, Reporter |
| **Múltiples en paralelo** | Operaciones independientes | Escanear múltiples directorios |
| **Secuencial con dependencias** | Pipeline con estado | Scan → Analyze → Edit |

---

## Conclusión

**Arquitectura correcta**:
```
NO: 1 agente monolítico que hace todo
SÍ: N agentes especializados coordinados por orchestrator
```

**Regla de oro**:
```
Si un agente tiene más de 100 líneas de lógica,
probablemente debería ser 2+ agentes.
```

**Beneficios principales**:
1. Mantenibilidad (fácil de modificar)
2. Testeabilidad (fácil de probar)
3. Reusabilidad (composable)
4. Debuggeabilidad (fácil encontrar bugs)
5. Escalabilidad (paralelizable)

**Costo**:
- Más tiempo de setup inicial
- Más archivos/clases
- Necesita orchestrator

**Veredicto**: Vale TOTALMENTE la pena. Es la diferencia entre código amateur y código profesional.

---

**Última actualización**: 2025-11-04
**Autor**: Equipo de Desarrollo
**Basado en**: Experiencia real de remoción de emojis en IACT
