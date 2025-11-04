---
id: DOC-ARQ-GUIA-PATRONES
titulo: Guía Rápida de Decisión de Patrones
estado: activo
fecha_creacion: 2025-11-04
version: 1.0
relacionados: ["DOC-ARQ-PATRONES"]
---

# Guía Rápida de Decisión de Patrones

## 🎯 Propósito

Esta guía te ayuda a **decidir rápidamente qué patrón usar** cuando escribes código nuevo o refactorizas código existente.

**Documento completo**: [patrones_arquitectonicos.md](patrones_arquitectonicos.md)

---

## ⚡ Decision Tree (5 Preguntas)

### Pregunta 1: ¿Estoy integrando con un sistema externo que no controlo?

**SÍ** → Usa **ADAPTER PATTERN**

```python
# ✅ Ejemplo: ivr_legacy/adapters.py
class IVRDataAdapter:
    def get_calls(self, start_date, end_date):
        return models.IVRCall.objects.using("ivr_readonly").filter(...)
```

**Cuándo**:
- BD legacy/externa
- API de terceros
- Sistema que puede cambiar

**Beneficios**:
- Aísla cambios externos
- Interfaz limpia
- Fácil mockear en tests

---

### Pregunta 2: ¿Es un pipeline de procesamiento de datos por lotes?

**SÍ** → Usa **ETL PIPELINE PATTERN**

```python
# ✅ Ejemplo: etl/
extractors.py   # EXTRACT: Obtener datos
transformers.py # TRANSFORM: Limpiar/validar
loaders.py      # LOAD: Insertar destino
jobs.py         # Orquestación
```

**Cuándo**:
- Datos de fuentes externas
- Transformación/limpieza necesaria
- Ejecución periódica (cron/scheduler)

**Beneficios**:
- Separación clara de fases
- Fácil debuggear
- Componentes reutilizables

---

### Pregunta 3: ¿Tengo múltiples variantes de un algoritmo que se eligen en runtime?

**SÍ** → Usa **STRATEGY PATTERN**

```python
# ✅ Ejemplo: reports/generators/
class BaseReportGenerator(ABC):
    @abstractmethod
    def generate(self, queryset, parameters) -> str:
        pass

class CSVGenerator(BaseReportGenerator): ...
class ExcelGenerator(BaseReportGenerator): ...
class PDFGenerator(BaseReportGenerator): ...

# Factory
def get_generator(format: str) -> BaseReportGenerator:
    return GENERATOR_REGISTRY[format]()
```

**Cuándo**:
- Múltiples formatos (CSV, Excel, PDF)
- Múltiples algoritmos (sort, filter, etc.)
- Comportamiento elegido en runtime

**Beneficios**:
- Fácil añadir nuevas estrategias
- Elimina condicionales largos
- Open/Closed Principle

---

### Pregunta 4: ¿Necesito componentes pluggeables/extensibles?

**SÍ** → Usa **REGISTRY PATTERN**

```python
# ✅ Ejemplo: dashboard/widgets.py
WIDGET_REGISTRY = {}

def register_widget(widget_class):
    WIDGET_REGISTRY[widget_class.widget_id] = widget_class
    return widget_class

@register_widget
class CallMetricsWidget(Widget):
    widget_id = "call_metrics"
    # ...
```

**Cuándo**:
- Sistema de plugins
- Componentes descubiertos en runtime
- Extensión sin modificar core

**Beneficios**:
- Extensibilidad
- Descubrimiento dinámico
- Desacoplamiento

---

### Pregunta 5: ¿La lógica involucra múltiples modelos o es compleja?

#### **SÍ** → Usa **SERVICE LAYER PATTERN**

```python
# ✅ Ejemplo: audit/services.py
class AuditService:
    @staticmethod
    def log(action: str, user: User, resource: str, ...):
        AuditLog.objects.create(...)
```

**Cuándo**:
- Operación con múltiples modelos
- Lógica de negocio compleja
- Coordinación con sistemas externos
- Transacciones
- Reutilización desde múltiples lugares

**Beneficios**:
- Centralización
- Reutilización
- Testabilidad
- Desacoplamiento

#### **NO** → Usa **ACTIVE RECORD PATTERN**

```python
# ✅ Ejemplo: notifications/models.py
class InternalMessage(models.Model):
    # ... campos ...

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
```

**Cuándo**:
- Lógica simple (1-5 líneas)
- Solo afecta a este modelo
- No hay coordinación con otros modelos

**Beneficios**:
- Simplicidad
- Encapsulación
- Natural en Django

---

## 📊 Tabla Comparativa Rápida

| Pregunta | Patrón | Apps que lo usan | Cuándo usarlo |
|----------|--------|-------------------|---------------|
| ¿Sistema externo? | **Adapter** | ivr_legacy | Integración con legacy/APIs |
| ¿Pipeline de datos? | **ETL Pipeline** | etl | Procesamiento por lotes |
| ¿Múltiples variantes? | **Strategy** | reports | CSV, Excel, PDF, etc. |
| ¿Extensible/Plugins? | **Registry** | dashboard | Widgets, plugins |
| ¿Lógica compleja? | **Service Layer** | audit, dashboard, users | Multi-modelo, orchestration |
| ¿Lógica simple? | **Active Record** | notifications, authentication | Solo este modelo |

---

## 🚫 Cuándo NO Usar Service Layer

**❌ NO USAR** si la operación es:

### 1. CRUD básico
```python
# ❌ MAL: Service innecesario
class AnalyticsService:
    @staticmethod
    def create_analytics(call_id, duration):
        return CallAnalytics.objects.create(call_id=call_id, duration=duration)

# ✅ BIEN: Usar directamente el modelo
CallAnalytics.objects.create(call_id=call_id, duration=duration)
```

### 2. Lógica trivial (1-3 líneas)
```python
# ❌ MAL: Service para lógica trivial
class NotificationService:
    @staticmethod
    def mark_as_read(message):
        message.is_read = True
        message.save()

# ✅ BIEN: Método en el modelo
class InternalMessage(models.Model):
    def mark_as_read(self):
        self.is_read = True
        self.save()
```

### 3. Solo se usa en un lugar
```python
# ❌ MAL: Service que solo se usa una vez
class ReportService:
    @staticmethod
    def build_title(report):
        return f"{report.name} - {report.date}"

# ✅ BIEN: Propiedad del modelo
class Report(models.Model):
    @property
    def full_title(self):
        return f"{self.name} - {self.date}"
```

---

## ✅ Cuándo SÍ Usar Service Layer

**✅ USAR** si cumple al menos 2 de estos criterios:

1. ✅ Involucra **múltiples modelos**
   ```python
   # Dashboard agrega datos de analytics, reports, notifications
   ```

2. ✅ Tiene **lógica de negocio compleja**
   ```python
   # PermissionService evalúa precedencia (directo > rol > segmento)
   ```

3. ✅ Se **reutiliza desde múltiples lugares**
   ```python
   # AuditService.log() se llama desde todas las apps
   ```

4. ✅ Coordina con **sistemas externos**
   ```python
   # EmailService envía emails, registra en BD, notifica
   ```

5. ✅ Requiere **transacciones complejas**
   ```python
   # OrderService crea orden, reserva inventario, cobra, notifica
   ```

---

## 📝 Ejemplos Reales del Proyecto

### Ejemplo 1: ¿Dónde poner lógica de reportes?

**Contexto**: Necesito generar reportes en múltiples formatos.

**Decision Tree**:
- ¿Sistema externo? NO
- ¿Pipeline datos? NO
- ¿Múltiples variantes? **SÍ** (CSV, Excel, PDF)

**✅ Solución**: **Strategy Pattern**
```python
reports/
├── generators/
│   ├── base.py         # BaseReportGenerator (interfaz)
│   ├── csv_generator.py
│   ├── excel_generator.py
│   └── pdf_generator.py
└── models.py           # ReportTemplate (configuración)
```

---

### Ejemplo 2: ¿Dónde poner lógica de permisos?

**Contexto**: Evaluar permisos con precedencia compleja.

**Decision Tree**:
- ¿Sistema externo? NO
- ¿Pipeline datos? NO
- ¿Múltiples variantes? NO
- ¿Extensible? NO
- ¿Lógica compleja? **SÍ** (evalúa 3 fuentes con precedencia)

**✅ Solución**: **Service Layer**
```python
users/
├── models.py    # Permission, Role, Segment
└── services.py  # PermissionService.has_permission()
```

---

### Ejemplo 3: ¿Dónde poner mark_as_read()?

**Contexto**: Marcar mensaje como leído.

**Decision Tree**:
- ¿Sistema externo? NO
- ¿Pipeline datos? NO
- ¿Múltiples variantes? NO
- ¿Extensible? NO
- ¿Lógica compleja? NO (3 líneas simples)

**✅ Solución**: **Active Record**
```python
notifications/
└── models.py
    class InternalMessage(models.Model):
        def mark_as_read(self):
            # 3 líneas simples
```

---

### Ejemplo 4: ¿Dónde poner acceso a IVR legacy?

**Contexto**: Leer datos de BD MariaDB legacy (read-only).

**Decision Tree**:
- ¿Sistema externo? **SÍ** (BD legacy que no controlamos)

**✅ Solución**: **Adapter Pattern**
```python
ivr_legacy/
├── models.py    # IVRCall (managed=False)
└── adapters.py  # IVRDataAdapter
```

---

## 🎓 Reglas de Oro

### 1. Empieza simple, refactoriza cuando sea necesario

```
Primera iteración: Lógica en el modelo (Active Record)
                   ↓
Si crece o se reutiliza: Mover a Service Layer
                   ↓
Si hay múltiples variantes: Refactorizar a Strategy
```

### 2. No todos los modelos necesitan un service

```
✅ CORRECTO: Mezclar patrones según la necesidad
- analytics/: Solo modelos (data sink)
- audit/: Service Layer (centralización)
- etl/: ETL Pipeline (procesamiento)
- ivr_legacy/: Adapter (integración)
```

### 3. Pregúntate: "¿Esto añade valor?"

```python
# ❌ Si el service solo envuelve un .create() → NO AÑADE VALOR
# ✅ Si el service orquesta múltiples operaciones → AÑADE VALOR
```

### 4. Pragmatismo sobre dogmatismo

```
❌ "Todas las apps deben tener services.py"
✅ "Cada app usa el patrón apropiado para su función"
```

### 5. YAGNI (You Aren't Gonna Need It)

```python
# No crear abstracciones hasta que sean necesarias
# Empezar simple, añadir complejidad cuando se justifique
```

---

## 🔍 Checklist de Decisión

Antes de crear un nuevo service/adapter/strategy, pregúntate:

- [ ] ¿La lógica involucra múltiples modelos? → Service Layer
- [ ] ¿Se va a reutilizar desde múltiples lugares? → Service Layer
- [ ] ¿Integro con sistema externo? → Adapter
- [ ] ¿Tengo múltiples variantes del algoritmo? → Strategy
- [ ] ¿Necesito extensibilidad/plugins? → Registry
- [ ] ¿Es lógica simple de un solo modelo? → Active Record
- [ ] ¿Es un pipeline de datos? → ETL Pipeline

**Si todas son NO**: Probablemente es lógica simple que va en el modelo o la vista.

---

## 📚 Referencias

- **Documento completo**: [patrones_arquitectonicos.md](patrones_arquitectonicos.md)
- **Análisis funcional**: [../../solicitudes/sc02/analisis_funcion_real_apps.md](../../solicitudes/sc02/analisis_funcion_real_apps.md)
- **Código fuente**: `api/callcentersite/callcentersite/apps/`

---

## 💡 Tips Finales

1. **Cuando dudes, empieza simple**: Es más fácil refactorizar a un patrón complejo que simplificar un over-engineering.

2. **Mira ejemplos existentes**: Antes de crear algo nuevo, busca en el proyecto si ya existe un patrón similar.

3. **Pregunta al equipo**: Si no estás seguro, discute el diseño antes de implementar.

4. **Documenta tu decisión**: Añade un comentario explicando por qué elegiste ese patrón.

5. **Refactoriza cuando sea apropiado**: El código evoluciona. Lo que empezó como Active Record puede necesitar Service Layer después.

---

**Última actualización**: 2025-11-04
