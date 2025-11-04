---
id: DOC-ARQ-PATRONES
titulo: Patrones Arquitectónicos del Backend
estado: activo
fecha_creacion: 2025-11-04
ultima_actualizacion: 2025-11-04
autores: ["Equipo Backend"]
revisores: []
version: 1.0
relacionados: ["DOC-SOL-SC02", "DOC-ARQ-BACKEND"]
---

# Patrones Arquitectónicos del Backend

## NOTA Índice

1. [Introducción](#introducción)
2. [Filosofía de Diseño](#filosofía-de-diseño)
3. [Patrones Identificados](#patrones-identificados)
   - [Service Layer Pattern](#service-layer-pattern)
   - [Adapter Pattern](#adapter-pattern)
   - [Strategy Pattern](#strategy-pattern)
   - [ETL Pipeline Pattern](#etl-pipeline-pattern)
   - [Active Record Pattern](#active-record-pattern)
   - [Registry Pattern](#registry-pattern)
4. [Guía de Decisión](#guía-de-decisión)
5. [Anti-Patrones a Evitar](#anti-patrones-a-evitar)
6. [Referencias](#referencias)

---

## Introducción

Este documento describe los **patrones arquitectónicos utilizados en el backend** del proyecto IACT. A diferencia de proyectos que imponen un único patrón de forma rígida, nuestro backend utiliza **múltiples patrones de forma pragmática**, eligiendo el patrón más apropiado según la función de cada aplicación Django.

### Objetivo del documento

1. **Documentar patrones existentes** con ejemplos reales del código
2. **Explicar las decisiones de diseño**: ¿Por qué se eligió cada patrón?
3. **Proporcionar guías de decisión**: ¿Cuándo usar cada patrón?
4. **Facilitar el onboarding**: Nuevos desarrolladores entenderán el diseño
5. **Mantener consistencia**: Pero sin caer en dogmatismo

### Contexto arquitectónico

El backend es un **monolito modular Django** con 10 aplicaciones:

```
api/callcentersite/callcentersite/apps/
├── analytics/         -> Data sink (almacenamiento de métricas)
├── audit/            -> Sistema de auditoría inmutable
├── authentication/   -> Autenticación y seguridad
├── common/           -> Utilidades compartidas
├── dashboard/        -> Orquestación de widgets
├── etl/              -> Pipeline de datos IVR -> Analytics
├── ivr_legacy/       -> Integración con BD legacy (read-only)
├── notifications/    -> Mensajería interna
├── reports/          -> Generación de reportes
└── users/            -> Sistema custom de permisos
```

Cada app tiene **diferentes responsabilidades** y por lo tanto usa **diferentes patrones arquitectónicos**.

---

## Filosofía de Diseño

### Principios guía

Nuestro diseño sigue estos principios (en orden de prioridad):

1. **Pragmatismo sobre dogmatismo**
   - No aplicar "mejores prácticas" sin contexto
   - Evaluar cada caso por sus méritos
   - Preferir simplicidad sobre "pureza" arquitectónica

2. **Explícito es mejor que implícito** (Zen of Python)
   - El código debe revelar su intención
   - Preferir claridad sobre "inteligencia"

3. **Simple es mejor que complejo**
   - No crear abstracciones hasta que sean necesarias
   - YAGNI (You Aren't Gonna Need It)
   - Evitar over-engineering

4. **Separación de responsabilidades**
   - Cada componente tiene una responsabilidad clara
   - Pero sin caer en micro-servicios internos

5. **Open/Closed Principle**
   - Abierto a extensión
   - Cerrado a modificación
   - Usar patrones que faciliten extensión

### ¿Por qué NO un patrón único?

**Ejemplo de lo que NO hacemos**:
```python
# NO ANTI-PATRÓN: Service layer innecesario
class AnalyticsService:
    """Servicio que solo hace CRUD básico."""

    @staticmethod
    def create_call_analytics(call_id, duration, queue_time):
        return CallAnalytics.objects.create(
            call_id=call_id,
            duration=duration,
            queue_time=queue_time
        )
```

**Problema**: Este "service" no añade valor, solo añade indirección.

**Solución correcta**: Usar directamente el modelo para operaciones simples.

---

## Patrones Identificados

### Service Layer Pattern

#### INFO Definición

El **Service Layer** define el límite de la aplicación y encapsula la lógica de negocio. Coordina operaciones complejas que involucran múltiples modelos o sistemas externos.

#### OBJETIVO Cuándo usarlo

Usar Service Layer cuando:
- OK La operación involucra múltiples modelos
- OK Hay lógica de negocio compleja
- OK Se coordina con sistemas externos
- OK La operación requiere transacciones
- OK Se quiere reutilizar lógica desde múltiples puntos

**NO usar cuando**:
- NO Solo se hace CRUD básico
- NO La lógica es trivial (1-2 líneas)
- NO El modelo puede manejar su propia lógica

#### 💻 Implementación en el proyecto

##### Ejemplo 1: `audit.services.AuditService`

**Contexto**: Sistema de auditoría que debe ser usado desde múltiples apps.

**Implementación**:
```python
# api/callcentersite/callcentersite/apps/audit/services.py

class AuditService:
    """Centraliza el registro de auditoría del sistema."""

    @staticmethod
    def log(
        action: str,
        user: User,
        resource: str,
        resource_id: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Registra una acción en el log de auditoría."""
        AuditLog.objects.create(
            user=user,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
```

**Modelo inmutable**:
```python
# api/callcentersite/callcentersite/apps/audit/models.py

class AuditLog(models.Model):
    # ... campos ...

    def save(self, *args, **kwargs):
        if self.pk:
            raise RuntimeError(
                "Los registros de auditoría son inmutables. "
                "No se permiten actualizaciones."
            )
        super().save(*args, **kwargs)
```

**Uso desde otras apps**:
```python
# En cualquier app
from callcentersite.apps.audit.services import AuditService

def some_view(request):
    # ... hacer algo importante ...

    AuditService.log(
        action="user_login",
        user=request.user,
        resource="authentication",
        ip_address=request.META.get("REMOTE_ADDR"),
    )
```

**¿Por qué Service Layer aquí?**
- OK Usado desde múltiples apps (centralización)
- OK Desacopla el "cómo se registra" del "qué se registra"
- OK Permite cambiar implementación sin afectar consumidores
- OK API clara y simple: `AuditService.log(...)`

---

##### Ejemplo 2: `dashboard.services.DashboardService`

**Contexto**: Dashboard que orquesta múltiples widgets de diferentes apps.

**Implementación**:
```python
# api/callcentersite/callcentersite/apps/dashboard/services.py

class DashboardService:
    """Orquesta la construcción del dashboard."""

    @staticmethod
    def overview() -> Dict[str, object]:
        """Construye la vista general del dashboard."""
        now = timezone.now()

        return {
            "last_update": now.isoformat(),
            "widgets": [
                widget.__dict__
                for widget in DashboardService.available_widgets()
            ],
        }

    @staticmethod
    def available_widgets() -> List[Widget]:
        """Obtiene todos los widgets disponibles."""
        from .widgets import WIDGET_REGISTRY

        widgets = []
        for widget_class in WIDGET_REGISTRY.values():
            widget = widget_class()
            if widget.is_available():
                widgets.append(widget)

        return widgets
```

**Vista REST que usa el servicio**:
```python
# api/callcentersite/callcentersite/apps/dashboard/views.py

from rest_framework.views import APIView
from rest_framework.response import Response

class DashboardOverviewView(APIView):
    """Endpoint REST para el dashboard."""

    def get(self, request):
        data = DashboardService.overview()
        return Response(data)
```

**¿Por qué Service Layer aquí?**
- OK Orquesta múltiples componentes (widgets)
- OK Lógica de negocio (¿qué widgets mostrar?)
- OK Desacopla la vista del "cómo" construir el dashboard
- OK Reutilizable (podría usarse en reportes, emails, etc.)

---

##### Ejemplo 3: `users.services.PermissionService`

**Contexto**: Sistema custom de permisos con precedencia compleja.

**Implementación**:
```python
# api/callcentersite/callcentersite/apps/users/services.py

class PermissionService:
    """Evalúa permisos según precedencia definida."""

    @staticmethod
    def has_permission(user: User, permission_codename: str) -> bool:
        """
        Evalúa si el usuario tiene el permiso solicitado.

        Precedencia:
        1. Permisos directos (más alta prioridad)
        2. Permisos por rol
        3. Permisos por segmento (más baja prioridad)
        """
        if not user.is_authenticated:
            return False

        # 1. Permisos directos
        if PermissionService._has_direct_permission(user, permission_codename):
            return True

        # 2. Permisos por rol
        if PermissionService._has_role_permission(user, permission_codename):
            return True

        # 3. Permisos por segmento
        return PermissionService._has_segment_permission(user, permission_codename)

    @staticmethod
    def _has_direct_permission(user: User, permission_codename: str) -> bool:
        return models.UserPermission.objects.has_permission(user, permission_codename)

    @staticmethod
    def _has_role_permission(user: User, permission_codename: str) -> bool:
        for role in models.RoleAssignment.objects.roles_for_user(user):
            if role.permissions.has_codename(permission_codename):
                return True
        return False

    @staticmethod
    def _has_segment_permission(user: User, permission_codename: str) -> bool:
        for segment in models.Segment.objects.with_permission(permission_codename):
            if segment.matches(user):
                return True
        return False
```

**¿Por qué Service Layer aquí?**
- OK Lógica compleja de evaluación de permisos
- OK Orquesta 3 fuentes diferentes de permisos
- OK Define reglas de precedencia (negocio)
- OK Sin service, esta lógica estaría duplicada en views

---

#### OK Ventajas del Service Layer

1. **Centralización**: Lógica en un solo lugar
2. **Reutilización**: Múltiples consumidores usan el mismo código
3. **Testabilidad**: Fácil probar lógica de negocio aislada
4. **Desacoplamiento**: Views delgadas, lógica en services
5. **Transacciones**: Fácil manejar transacciones complejas

#### WARNING Desventajas (si se usa mal)

1. **Over-engineering**: Si solo hace CRUD básico
2. **Indirección innecesaria**: Añade capas sin valor
3. **Código verboso**: Más líneas de código
4. **Mantenimiento**: Más archivos que mantener

---

### Adapter Pattern

#### INFO Definición

El **Adapter Pattern** permite que interfaces incompatibles trabajen juntas. Encapsula el acceso a sistemas externos con una interfaz limpia.

#### OBJETIVO Cuándo usarlo

Usar Adapter cuando:
- OK Integras con sistema externo/legacy
- OK No controlas la interfaz del sistema externo
- OK Quieres aislar el código de cambios externos
- OK Necesitas traducir entre interfaces incompatibles

**NO usar cuando**:
- NO Tienes control total del sistema
- NO La interfaz ya es compatible
- NO Es una simple operación CRUD interna

#### 💻 Implementación en el proyecto

##### Ejemplo: `ivr_legacy.adapters.IVRDataAdapter`

**Contexto**: Base de datos IVR legacy (MariaDB) que no podemos modificar.

**Arquitectura**:
```
┌─────────────┐
│  ETL Job    │  -> Necesita datos de IVR
└──────┬──────┘
       │
       │ usa
       ↓
┌─────────────────┐
│ IVRDataAdapter  │  -> Interfaz limpia
└──────┬──────────┘
       │
       │ encapsula
       ↓
┌─────────────────┐
│ IVRCall model   │  -> Modelo read-only (managed=False)
└──────┬──────────┘
       │
       │ mapea a
       ↓
┌─────────────────┐
│ MariaDB Legacy  │  -> Base de datos externa
└─────────────────┘
```

**Implementación del Adapter**:
```python
# api/callcentersite/callcentersite/apps/ivr_legacy/adapters.py

class IVRDataAdapter:
    """
    Encapsula la lectura de datos de la BD IVR en modo read-only.

    Este adapter:
    - Proporciona una interfaz limpia para acceder a datos IVR
    - Aísla el resto del código de cambios en la BD IVR
    - Maneja la conexión a la base de datos read-only
    """

    def get_calls(self, start_date: datetime, end_date: datetime):
        """Obtiene llamadas en un rango de fechas."""
        return models.IVRCall.objects.using("ivr_readonly").filter(
            call_date__range=(start_date, end_date)
        )

    def get_client(self, client_id: str):
        """Obtiene información de un cliente por ID."""
        return models.IVRClient.objects.using("ivr_readonly").get(
            client_id=client_id
        )
```

**Modelos read-only**:
```python
# api/callcentersite/callcentersite/apps/ivr_legacy/models.py

class IVRCall(models.Model):
    """Mapeo de la tabla 'calls' en la BD IVR."""

    call_id = models.CharField(max_length=50, primary_key=True)
    call_date = models.DateTimeField()
    duration = models.IntegerField()
    # ... más campos ...

    class Meta:
        managed = False  # -> Django NO gestiona esta tabla
        db_table = "calls"  # -> Nombre exacto en BD externa
```

**Protección read-only**:
```python
# api/callcentersite/callcentersite/database_router.py

class IVRReadOnlyRouter:
    """Router que previene escrituras accidentales a la BD IVR."""

    def db_for_write(self, model, **hints):
        if model._meta.app_label.startswith("ivr_legacy"):
            raise ValueError(
                "CRITICAL RESTRICTION VIOLATED: Attempted write operation on IVR "
                "database. IVR database is READ-ONLY."
            )
        return None
```

**Uso desde ETL**:
```python
# api/callcentersite/callcentersite/apps/etl/extractors.py

class IVRDataExtractor:
    """Extrae llamadas desde la BD IVR."""

    def __init__(self) -> None:
        self.adapter = IVRDataAdapter()  # -> Usa el adapter

    def extract_calls(self, start_date: datetime, end_date: datetime):
        # Interfaz limpia, sin preocuparse por detalles de BD
        return self.adapter.get_calls(start_date, end_date)
```

**¿Por qué Adapter Pattern aquí?**
- OK Sistema externo que no controlamos
- OK Aísla cambios en la BD IVR
- OK Interfaz limpia para el ETL
- OK Maneja configuración de base de datos
- OK Previene escrituras accidentales

---

#### OK Ventajas del Adapter Pattern

1. **Aislamiento**: Cambios externos no afectan código interno
2. **Interfaz limpia**: API simple para consumidores
3. **Testabilidad**: Fácil mockear el adapter
4. **Protección**: Encapsula restricciones (read-only)
5. **Documentación**: El adapter documenta el sistema externo

#### WARNING Cuándo NO usarlo

- Sistema interno que controlas completamente
- Operaciones simples que no justifican la abstracción
- Cuando añade complejidad sin beneficio

---

### Strategy Pattern

#### INFO Definición

El **Strategy Pattern** define una familia de algoritmos, encapsula cada uno y los hace intercambiables. Permite que el algoritmo varíe independientemente de los clientes que lo usan.

#### OBJETIVO Cuándo usarlo

Usar Strategy cuando:
- OK Múltiples variantes de un algoritmo
- OK Comportamiento debe elegirse en runtime
- OK Quieres añadir nuevas estrategias sin modificar código existente
- OK Lógica compleja con muchos condicionales

**NO usar cuando**:
- NO Solo existe una implementación
- NO El comportamiento no varía
- NO La lógica es simple

#### 💻 Implementación en el proyecto

##### Ejemplo: `reports.generators.BaseReportGenerator`

**Contexto**: Sistema de reportes que soporta múltiples formatos (CSV, Excel, PDF).

**Arquitectura**:
```
┌──────────────────┐
│ ReportTemplate   │  -> Configuración del reporte
└────────┬─────────┘
         │
         │ usa estrategia según "format"
         ↓
┌──────────────────────┐
│ BaseReportGenerator  │  -> Interfaz abstracta
└──────────┬───────────┘
           │
           │ implementaciones concretas
           ├─────────────┬──────────────┬────────────┐
           ↓             ↓              ↓            ↓
    ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌──────────┐
    │   CSV    │  │   Excel   │  │   PDF   │  │  Custom  │
    └──────────┘  └───────────┘  └─────────┘  └──────────┘
```

**Interfaz abstracta**:
```python
# api/callcentersite/callcentersite/apps/reports/generators/base.py

from abc import ABC, abstractmethod
from django.db.models import QuerySet

class BaseReportGenerator(ABC):
    """Interfaz para generadores de reportes."""

    @abstractmethod
    def generate(self, queryset: QuerySet, parameters: dict) -> str:
        """
        Genera un archivo y retorna la ruta resultante.

        Args:
            queryset: Datos a incluir en el reporte
            parameters: Parámetros de configuración

        Returns:
            Ruta al archivo generado
        """
        pass
```

**Estrategia concreta: CSV**:
```python
# api/callcentersite/callcentersite/apps/reports/generators/csv_generator.py

import csv
from pathlib import Path
from .base import BaseReportGenerator

class CSVReportGenerator(BaseReportGenerator):
    """Genera reportes en formato CSV."""

    def generate(self, queryset: QuerySet, parameters: dict) -> str:
        output_path = Path(parameters["output_dir"]) / f"report_{timezone.now():%Y%m%d}.csv"

        with output_path.open("w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Headers
            if queryset:
                writer.writerow(queryset[0].__dict__.keys())

            # Data
            for record in queryset:
                writer.writerow(record.__dict__.values())

        return str(output_path)
```

**Estrategia concreta: Excel** (ejemplo):
```python
# api/callcentersite/callcentersite/apps/reports/generators/excel_generator.py

import openpyxl
from .base import BaseReportGenerator

class ExcelReportGenerator(BaseReportGenerator):
    """Genera reportes en formato Excel."""

    def generate(self, queryset: QuerySet, parameters: dict) -> str:
        workbook = openpyxl.Workbook()
        sheet = workbook.active

        # ... lógica de generación Excel ...

        output_path = Path(parameters["output_dir"]) / f"report_{timezone.now():%Y%m%d}.xlsx"
        workbook.save(output_path)

        return str(output_path)
```

**Registro de estrategias**:
```python
# api/callcentersite/callcentersite/apps/reports/generators/__init__.py

GENERATOR_REGISTRY = {
    "csv": CSVReportGenerator,
    "excel": ExcelReportGenerator,
    "pdf": PDFReportGenerator,
}

def get_generator(format: str) -> BaseReportGenerator:
    """Factory para obtener el generador apropiado."""
    generator_class = GENERATOR_REGISTRY.get(format)
    if not generator_class:
        raise ValueError(f"Formato no soportado: {format}")
    return generator_class()
```

**Uso**:
```python
# En el servicio de reportes
from reports.generators import get_generator

def generate_report(template: ReportTemplate):
    # Obtener datos
    queryset = get_queryset_from_template(template)

    # Elegir estrategia según formato
    generator = get_generator(template.format)

    # Generar reporte
    file_path = generator.generate(queryset, template.parameters)

    # Guardar metadata
    GeneratedReport.objects.create(
        template=template,
        file_path=file_path,
        status="completed",
    )
```

**¿Por qué Strategy Pattern aquí?**
- OK Múltiples formatos (CSV, Excel, PDF)
- OK Fácil añadir nuevos formatos sin modificar código existente
- OK Cada generador tiene su propia lógica compleja
- OK El formato se elige en runtime
- OK Open/Closed Principle

---

#### OK Ventajas del Strategy Pattern

1. **Extensibilidad**: Añadir estrategias sin modificar código
2. **Encapsulación**: Cada algoritmo está aislado
3. **Eliminación de condicionales**: No más `if format == "csv"...`
4. **Testabilidad**: Probar cada estrategia independientemente
5. **Principio Open/Closed**: Abierto a extensión, cerrado a modificación

#### WARNING Cuándo NO usarlo

- Solo una implementación (no hay variantes)
- Lógica simple que no justifica abstracción
- Estrategias comparten mucho código (considerar Template Method)

---

### ETL Pipeline Pattern

#### INFO Definición

El **ETL Pipeline Pattern** estructura el procesamiento de datos en tres fases claramente separadas:
1. **Extract**: Extracción de datos desde fuentes
2. **Transform**: Transformación y limpieza de datos
3. **Load**: Carga de datos al destino

#### OBJETIVO Cuándo usarlo

Usar ETL Pipeline cuando:
- OK Procesas datos de fuentes externas
- OK Necesitas transformar/limpiar datos
- OK Los datos vienen de sistemas legacy
- OK Hay múltiples fuentes o destinos
- OK El pipeline se ejecuta periódicamente

**NO usar cuando**:
- NO Operaciones en tiempo real (usa streaming)
- NO No hay transformación significativa
- NO Los datos ya están en el formato correcto

#### 💻 Implementación en el proyecto

##### Estructura del ETL

```
api/callcentersite/callcentersite/apps/etl/
├── extractors.py     -> EXTRACT: Obtiene datos de fuentes
├── transformers.py   -> TRANSFORM: Limpia y transforma datos
├── loaders.py        -> LOAD: Carga datos al destino
├── jobs.py           -> Orquestación del pipeline completo
└── scheduler.py      -> Automatización con APScheduler
```

**Flujo de datos**:
```
┌─────────────────┐
│  MariaDB IVR    │  (Base de datos legacy)
│   (read-only)   │
└────────┬────────┘
         │
         │ EXTRACT
         ↓
┌─────────────────┐
│ IVRDataExtractor│  -> Obtiene llamadas crudas
└────────┬────────┘
         │
         │ raw_calls (List[IVRCall])
         ↓
┌──────────────────┐
│CallDataTransformer│  -> Limpia, valida, enriquece
└────────┬─────────┘
         │
         │ transformed_calls (List[dict])
         ↓
┌──────────────────┐
│AnalyticsDataLoader│  -> Inserta en PostgreSQL
└────────┬─────────┘
         │
         ↓
┌─────────────────┐
│  PostgreSQL     │  (analytics app)
│  CallAnalytics  │
└─────────────────┘
```

**EXTRACT: Extractor**:
```python
# api/callcentersite/callcentersite/apps/etl/extractors.py

from datetime import datetime
from callcentersite.apps.ivr_legacy.adapters import IVRDataAdapter

class IVRDataExtractor:
    """Extrae llamadas desde la BD IVR."""

    def __init__(self) -> None:
        self.adapter = IVRDataAdapter()

    def extract_calls(self, start_date: datetime, end_date: datetime):
        """
        Extrae llamadas en un rango de fechas.

        Returns:
            QuerySet de IVRCall (datos crudos)
        """
        return self.adapter.get_calls(start_date, end_date)
```

**TRANSFORM: Transformer**:
```python
# api/callcentersite/callcentersite/apps/etl/transformers.py

from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class CallDataTransformer:
    """Transforma datos crudos de IVR a formato de analytics."""

    def transform(self, raw_calls) -> List[Dict]:
        """
        Transforma y limpia datos de llamadas.

        Operaciones:
        - Valida datos requeridos
        - Normaliza formatos
        - Calcula métricas derivadas
        - Filtra registros inválidos
        """
        transformed = []

        for call in raw_calls:
            try:
                # Validación
                if not self._is_valid_call(call):
                    logger.warning(f"Llamada inválida: {call.call_id}")
                    continue

                # Transformación
                transformed_call = {
                    "call_id": call.call_id,
                    "duration": call.duration,
                    "queue_time": call.queue_time or 0,
                    "call_date": call.call_date,
                    # Métricas derivadas
                    "total_time": call.duration + (call.queue_time or 0),
                    "is_abandoned": call.duration == 0,
                }

                transformed.append(transformed_call)

            except Exception as e:
                logger.error(f"Error transformando {call.call_id}: {e}")
                continue

        return transformed

    def _is_valid_call(self, call) -> bool:
        """Valida que la llamada tenga datos requeridos."""
        return (
            call.call_id and
            call.call_date and
            call.duration is not None
        )
```

**LOAD: Loader**:
```python
# api/callcentersite/callcentersite/apps/etl/loaders.py

from typing import List, Dict
from django.db import transaction
from callcentersite.apps.analytics.models import CallAnalytics
import logging

logger = logging.getLogger(__name__)

class AnalyticsDataLoader:
    """Carga datos transformados en la BD de analytics."""

    @transaction.atomic
    def load(self, transformed_calls: List[Dict]) -> int:
        """
        Carga llamadas en analytics.

        Returns:
            Número de registros cargados
        """
        loaded_count = 0

        for call_data in transformed_calls:
            try:
                CallAnalytics.objects.update_or_create(
                    call_id=call_data["call_id"],
                    defaults=call_data,
                )
                loaded_count += 1

            except Exception as e:
                logger.error(f"Error cargando {call_data['call_id']}: {e}")
                # Continuar con los demás (no fallar todo el batch)
                continue

        logger.info(f"Cargados {loaded_count}/{len(transformed_calls)} registros")
        return loaded_count
```

**ORQUESTACIÓN: Job**:
```python
# api/callcentersite/callcentersite/apps/etl/jobs.py

import logging
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from .extractors import IVRDataExtractor
from .transformers import CallDataTransformer
from .loaders import AnalyticsDataLoader

logger = logging.getLogger(__name__)

def run_etl() -> None:
    """
    Ejecuta el flujo ETL completo.

    Fases:
    1. EXTRACT: Obtener llamadas desde IVR
    2. TRANSFORM: Limpiar y transformar datos
    3. LOAD: Cargar en analytics
    """
    # Definir ventana de tiempo
    end = timezone.now()
    start = end - timedelta(hours=getattr(settings, "ETL_FREQUENCY_HOURS", 6))

    logger.info(f"Iniciando ETL: {start} a {end}")

    # EXTRACT
    extractor = IVRDataExtractor()
    raw_calls = extractor.extract_calls(start, end)
    logger.info(f"Extraídas {raw_calls.count()} llamadas")

    # TRANSFORM
    transformer = CallDataTransformer()
    transformed = transformer.transform(raw_calls)
    logger.info(f"Transformadas {len(transformed)} llamadas")

    # LOAD
    loader = AnalyticsDataLoader()
    loaded = loader.load(transformed)
    logger.info(f"Cargadas {loaded} llamadas")

    logger.info("ETL finalizado", extra={"registros": loaded})
```

**AUTOMATIZACIÓN: Scheduler**:
```python
# api/callcentersite/callcentersite/apps/etl/scheduler.py

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

from .jobs import run_etl

logger = logging.getLogger(__name__)

# Scheduler global
scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)

@scheduler.scheduled_job("interval", hours=settings.ETL_FREQUENCY_HOURS)
def scheduled_etl() -> None:
    """Ejecuta el proceso ETL según frecuencia configurada."""
    logger.info("Iniciando job ETL programado")
    run_etl()
```

**¿Por qué ETL Pipeline Pattern aquí?**
- OK Datos de sistema externo (IVR legacy)
- OK Necesita transformación (validación, limpieza)
- OK Separación clara de responsabilidades
- OK Fácil debuggear cada fase
- OK Reutilizable (extractors, transformers, loaders independientes)

---

#### OK Ventajas del ETL Pipeline Pattern

1. **Separación de responsabilidades**: Cada fase tiene un propósito claro
2. **Testabilidad**: Probar extractors, transformers, loaders independientemente
3. **Reutilización**: Componentes pueden usarse en otros pipelines
4. **Mantenibilidad**: Fácil entender y modificar cada fase
5. **Monitoreo**: Medir rendimiento de cada fase
6. **Escalabilidad**: Paralelizar transformaciones si es necesario

#### WARNING Desventajas

- No apropiado para streaming en tiempo real
- Latencia entre extract y load
- Requiere storage temporal para datos intermedios

---

### Active Record Pattern

#### INFO Definición

El **Active Record Pattern** combina datos y comportamiento en el mismo objeto. Los modelos Django naturalmente siguen este patrón.

#### OBJETIVO Cuándo usarlo

Usar Active Record cuando:
- OK Lógica está fuertemente acoplada al modelo
- OK Operación afecta solo a ese modelo
- OK Lógica es simple (1-3 líneas)
- OK Es comportamiento del "objeto"

**NO usar cuando**:
- NO Lógica involucra múltiples modelos
- NO Hay lógica de negocio compleja
- NO Se necesita coordinar transacciones

#### 💻 Implementación en el proyecto

##### Ejemplo 1: `authentication.models.SecurityQuestion`

**Contexto**: Preguntas de seguridad con hash/verify.

```python
# api/callcentersite/callcentersite/apps/authentication/models.py

from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class SecurityQuestion(models.Model):
    """Pregunta de seguridad para recuperación de cuenta."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    answer_hash = models.CharField(max_length=255)

    def set_answer(self, answer: str) -> None:
        """
        Establece la respuesta hasheada.

        La respuesta nunca se almacena en texto plano.
        """
        self.answer_hash = make_password(answer.lower().strip())

    def verify_answer(self, answer: str) -> bool:
        """
        Verifica si la respuesta es correcta.

        Returns:
            True si la respuesta coincide
        """
        return check_password(answer.lower().strip(), self.answer_hash)
```

**Uso**:
```python
# Crear pregunta de seguridad
question = SecurityQuestion(
    user=user,
    question="¿Cuál es tu color favorito?"
)
question.set_answer("azul")
question.save()

# Verificar respuesta
if question.verify_answer("azul"):
    # Permitir recuperación de cuenta
    pass
```

**¿Por qué Active Record aquí?**
- OK Lógica acoplada al modelo (hash de SU respuesta)
- OK No involucra otros modelos
- OK Es comportamiento del objeto SecurityQuestion
- OK Simple y claro

---

##### Ejemplo 2: `notifications.models.InternalMessage`

**Contexto**: Mensajes con mark_as_read().

```python
# api/callcentersite/callcentersite/apps/notifications/models.py

from django.db import models
from django.utils import timezone

class InternalMessage(models.Model):
    """Mensaje interno del sistema."""

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    subject = models.CharField(max_length=200)
    body = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def mark_as_read(self) -> None:
        """
        Marca el mensaje como leído.

        Actualiza is_read y read_at si aún no está marcado.
        """
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
```

**Uso**:
```python
# Vista de notificaciones
def mark_notification_read(request, message_id):
    message = InternalMessage.objects.get(id=message_id, recipient=request.user)
    message.mark_as_read()  # -> Método del modelo
    return redirect("notifications")
```

**¿Por qué Active Record aquí?**
- OK Operación simple sobre el mismo objeto
- OK Solo afecta a este modelo
- OK 3 líneas de lógica (no justifica service)
- OK Clara semántica: "message.mark_as_read()"

**NO Lo que NO haríamos (over-engineering)**:
```python
# ANTI-PATRÓN: Service innecesario
class NotificationService:
    @staticmethod
    def mark_as_read(message: InternalMessage) -> None:
        message.is_read = True
        message.read_at = timezone.now()
        message.save(update_fields=["is_read", "read_at"])
```
Esto no añade valor, solo añade indirección.

---

#### OK Ventajas del Active Record Pattern

1. **Simplicidad**: Datos y comportamiento juntos
2. **Encapsulación**: El modelo conoce su propia lógica
3. **Menos archivos**: No necesitas services.py para todo
4. **Natural en Django**: Los modelos Django son Active Record
5. **Claridad**: `obj.method()` es claro

#### WARNING Cuándo NO usarlo

- Lógica compleja que involucra múltiples modelos
- Coordinación de transacciones
- Lógica de negocio que debe reutilizarse desde múltiples lugares

---

### Registry Pattern

#### INFO Definición

El **Registry Pattern** mantiene un registro de objetos disponibles, permitiendo descubrimiento y extensión dinámica.

#### OBJETIVO Cuándo usarlo

Usar Registry cuando:
- OK Tienes componentes pluggeables
- OK Quieres descubrir componentes en runtime
- OK Necesitas extensión sin modificar código core
- OK Múltiples implementaciones de una interfaz

**NO usar cuando**:
- NO Conjunto fijo de componentes conocidos en compile-time
- NO No hay necesidad de extensión dinámica

#### 💻 Implementación en el proyecto

##### Ejemplo: `dashboard.widgets.WIDGET_REGISTRY`

**Contexto**: Dashboard con widgets extensibles.

```python
# api/callcentersite/callcentersite/apps/dashboard/widgets.py

from typing import Dict, Type

# Registry global de widgets
WIDGET_REGISTRY: Dict[str, Type['Widget']] = {}

def register_widget(widget_class: Type['Widget']) -> Type['Widget']:
    """Decorator para registrar widgets."""
    WIDGET_REGISTRY[widget_class.widget_id] = widget_class
    return widget_class

class Widget:
    """Clase base para widgets del dashboard."""

    widget_id: str = None
    title: str = None

    def is_available(self) -> bool:
        """¿Este widget debe mostrarse?"""
        return True

    def get_data(self) -> dict:
        """Obtiene datos del widget."""
        raise NotImplementedError

# ===== Widgets concretos =====

@register_widget
class CallMetricsWidget(Widget):
    """Widget de métricas de llamadas."""

    widget_id = "call_metrics"
    title = "Métricas de Llamadas"

    def get_data(self) -> dict:
        from callcentersite.apps.analytics.models import DailyMetrics

        today = timezone.now().date()
        metrics = DailyMetrics.objects.filter(date=today).first()

        return {
            "total_calls": metrics.total_calls if metrics else 0,
            "avg_duration": metrics.avg_duration if metrics else 0,
        }

@register_widget
class UnreadMessagesWidget(Widget):
    """Widget de mensajes no leídos."""

    widget_id = "unread_messages"
    title = "Mensajes No Leídos"

    def get_data(self) -> dict:
        from callcentersite.apps.notifications.models import InternalMessage

        # Este widget solo se muestra si hay user en contexto
        return {
            "count": 0,  # Se llenará en runtime con el user
        }

    def is_available(self) -> bool:
        # Solo mostrar si el módulo de notificaciones está activo
        return True

@register_widget
class PendingReportsWidget(Widget):
    """Widget de reportes pendientes."""

    widget_id = "pending_reports"
    title = "Reportes Pendientes"

    def get_data(self) -> dict:
        from callcentersite.apps.reports.models import GeneratedReport

        pending = GeneratedReport.objects.filter(status="pending").count()
        return {"count": pending}
```

**Uso en el servicio**:
```python
# api/callcentersite/callcentersite/apps/dashboard/services.py

from .widgets import WIDGET_REGISTRY

class DashboardService:
    @staticmethod
    def available_widgets() -> List[Widget]:
        """Obtiene todos los widgets disponibles."""
        widgets = []

        # Descubrir widgets dinámicamente del registry
        for widget_class in WIDGET_REGISTRY.values():
            widget = widget_class()
            if widget.is_available():
                widgets.append(widget)

        return widgets
```

**Añadir nuevo widget (extensión sin modificar código)**:
```python
# En cualquier lugar
from callcentersite.apps.dashboard.widgets import register_widget, Widget

@register_widget
class CustomWidget(Widget):
    """Mi widget custom."""

    widget_id = "custom_widget"
    title = "Mi Widget"

    def get_data(self) -> dict:
        return {"custom_data": "value"}

# -> Se registra automáticamente, aparecerá en el dashboard
```

**¿Por qué Registry Pattern aquí?**
- OK Widgets pluggeables (fácil añadir nuevos)
- OK Descubrimiento dinámico en runtime
- OK No hay que modificar código core para añadir widgets
- OK Open/Closed Principle

---

#### OK Ventajas del Registry Pattern

1. **Extensibilidad**: Añadir componentes sin modificar código
2. **Descubrimiento**: Encontrar componentes en runtime
3. **Desacoplamiento**: Core no conoce implementaciones específicas
4. **Plugin Architecture**: Base para sistema de plugins

#### WARNING Desventajas

- Más complejo que lista hardcoded
- Debugging puede ser más difícil (¿de dónde salió este widget?)
- Puede ser over-engineering si no hay necesidad de extensión

---

## Guía de Decisión

### Árbol de decisión para elegir patrón

```
¿Estoy integrando con un sistema externo/legacy?
├─ SÍ -> ADAPTER PATTERN
│         (ivr_legacy.adapters.IVRDataAdapter)
│
└─ NO -> ¿Es un pipeline de procesamiento de datos?
    ├─ SÍ -> ETL PIPELINE PATTERN
    │         (etl/extractors, transformers, loaders)
    │
    └─ NO -> ¿Tengo múltiples variantes de un algoritmo?
        ├─ SÍ -> STRATEGY PATTERN
        │         (reports.generators)
        │
        └─ NO -> ¿Necesito componentes pluggeables/extensibles?
            ├─ SÍ -> REGISTRY PATTERN
            │         (dashboard.widgets)
            │
            └─ NO -> ¿La lógica involucra múltiples modelos o es compleja?
                ├─ SÍ -> SERVICE LAYER PATTERN
                │         (audit, dashboard, users)
                │
                └─ NO -> ACTIVE RECORD PATTERN
                          (notifications, authentication)
```

### Matriz de decisión

| Característica | Service Layer | Adapter | Strategy | ETL Pipeline | Active Record | Registry |
|----------------|---------------|---------|----------|--------------|---------------|----------|
| **Lógica simple (1-3 líneas)** | NO | NO | NO | NO | OK | NO |
| **Lógica compleja o multi-modelo** | OK | WARNING | WARNING | WARNING | NO | NO |
| **Integración externa** | WARNING | OK | NO | WARNING | NO | NO |
| **Múltiples variantes** | NO | NO | OK | NO | NO | WARNING |
| **Pipeline de datos** | NO | WARNING | NO | OK | NO | NO |
| **Componentes extensibles** | NO | NO | WARNING | NO | NO | OK |
| **Reutilización desde múltiples lugares** | OK | OK | OK | WARNING | WARNING | OK |

**Leyenda**: OK Ideal | WARNING Posible | NO No apropiado

---

## Anti-Patrones a Evitar

### 1. Service Layer innecesario

**NO Mal**:
```python
class AnalyticsService:
    """Service que solo hace CRUD."""

    @staticmethod
    def create_call_analytics(call_id, duration):
        return CallAnalytics.objects.create(
            call_id=call_id,
            duration=duration
        )
```

**OK Bien**:
```python
# Usar directamente el modelo
CallAnalytics.objects.create(call_id=call_id, duration=duration)
```

**Razón**: El "service" no añade valor, solo añade indirección.

---

### 2. Lógica de negocio en las vistas

**NO Mal**:
```python
def dashboard_view(request):
    # 50 líneas de lógica de negocio aquí
    widget1_data = ...
    widget2_data = ...
    # ...
    return render(request, "dashboard.html", context)
```

**OK Bien**:
```python
def dashboard_view(request):
    data = DashboardService.overview()  # Lógica en service
    return render(request, "dashboard.html", {"data": data})
```

**Razón**: Views deben ser delgadas, solo coordinación.

---

### 3. God Object (modelo que hace todo)

**NO Mal**:
```python
class Report(models.Model):
    # ... campos ...

    def generate_csv(self): ...
    def generate_excel(self): ...
    def generate_pdf(self): ...
    def send_email(self): ...
    def upload_to_s3(self): ...
    # 500 líneas de métodos
```

**OK Bien**:
```python
class Report(models.Model):
    # Solo datos y lógica simple

# Lógica compleja en Strategy Pattern
class CSVGenerator: ...
class ExcelGenerator: ...
```

**Razón**: Single Responsibility Principle.

---

### 4. Tight coupling a sistema externo

**NO Mal**:
```python
def process_calls():
    # Directamente contra BD externa
    calls = IVRCall.objects.using("ivr_db").filter(...)
    # Lógica esparcida por todo el código
```

**OK Bien**:
```python
def process_calls():
    adapter = IVRDataAdapter()  # Aislamiento
    calls = adapter.get_calls(start, end)
```

**Razón**: Cambios en BD externa no deben romper todo el código.

---

### 5. Duplicación de lógica

**NO Mal**:
```python
# En view1
if user.permissions.filter(codename="perm").exists():
    ...

# En view2 (duplicado)
if user.permissions.filter(codename="perm").exists():
    ...
```

**OK Bien**:
```python
# Centralizado en service
if PermissionService.has_permission(user, "perm"):
    ...
```

**Razón**: DRY (Don't Repeat Yourself).

---

## Referencias

### Documentos relacionados

- [Análisis Funcional de Apps](../../solicitudes/sc02/analisis_funcion_real_apps.md)
- [Análisis Estructural de API](../../solicitudes/sc02/analisis_estructura_api.md)
- [Solicitud SC02](../../solicitudes/sc02/readme.md)

### Libros y recursos

- **"Patterns of Enterprise Application Architecture"** - Martin Fowler
  - Service Layer (capítulo 9)
  - Active Record (capítulo 10)

- **"Design Patterns: Elements of Reusable Object-Oriented Software"** - Gang of Four
  - Adapter Pattern
  - Strategy Pattern

- **"Django Design Patterns and Best Practices"** - Arun Ravindran
  - Django-specific patterns

### Código fuente

Todos los ejemplos en este documento vienen del código real en:
```
api/callcentersite/callcentersite/apps/
├── audit/services.py
├── dashboard/services.py, widgets.py
├── etl/extractors.py, transformers.py, loaders.py
├── ivr_legacy/adapters.py
├── reports/generators/
└── users/services.py
```

---

## Changelog

| Fecha | Versión | Cambios | Autor |
|-------|---------|---------|-------|
| 2025-11-04 | 1.0 | Creación inicial del documento | Equipo Backend |

---

**Nota final**: Este documento es un "living document". A medida que el proyecto evoluciona y se identifican nuevos patrones o mejores prácticas, este documento debe actualizarse para reflejar la realidad del código.
