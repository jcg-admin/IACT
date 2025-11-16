# Backend API Documentation Index

**Dominio:** Backend
**Ubicacion:** /api/callcentersite/
**Framework:** Django REST Framework
**Fecha ultima actualizacion:** 2025-11-16

---

## Overview

Este directorio contiene la documentacion de todas las APIs REST del backend del proyecto IACT.

**Stack tecnologico:**
- Django 4.x
- Django REST Framework
- PostgreSQL / Cassandra
- Redis (cache)

---

## APIs Principales

### 1. DORA Metrics API

**Descripcion:** API para metricas DevOps Research and Assessment

**Ubicacion codigo:** `/api/callcentersite/dora_metrics/`

**Endpoints:**
- [Ver especificacion completa](./dora_metrics_api.md)

**Documentos relacionados:**
- OpenAPI spec: [openapi_dora_metrics.yaml](./openapi_dora_metrics.yaml) (pendiente)
- Requisitos: [../../requisitos/REQ-DORA-001.md](../../requisitos/) (buscar DORA)

---

### 2. Data Centralization API

**Descripcion:** API para centralizacion de datos

**Ubicacion codigo:** `/api/callcentersite/data_centralization/`

**Endpoints:**
- [Ver especificacion completa](./data_centralization_api.md)

**Documentos relacionados:**
- Tarea: `TASK-011-data-centralization-layer.md`
- ADR: Buscar en gobernanza/adr/

---

### 3. Politicas API

**Descripcion:** Gestion de politicas del call center

**Ubicacion codigo:** `/api/callcentersite/callcentersite/apps/politicas/`

**Archivos:**
- views.py
- serializers.py
- urls.py

**Endpoints:**
- [Ver especificacion completa](./politicas_api.md)

**OpenAPI spec:**
- [openapi_prioridad_02.yaml](./openapi_prioridad_02.yaml) (existente)

---

### 4. Alertas API

**Descripcion:** Sistema de alertas y notificaciones

**Ubicacion codigo:** `/api/callcentersite/callcentersite/apps/alertas/`

**Archivos:**
- views.py
- serializers.py
- urls.py

**Endpoints:**
- [Ver especificacion completa](./alertas_api.md)

---

### 5. Configuracion API

**Descripcion:** Configuracion del sistema

**Ubicacion codigo:** `/api/callcentersite/callcentersite/apps/configuracion/`

**Archivos:**
- views.py
- serializers.py
- urls.py

**Endpoints:**
- [Ver especificacion completa](./configuracion_api.md)

---

### 6. Metricas API

**Descripcion:** Metricas operacionales del call center

**Ubicacion codigo:** `/api/callcentersite/callcentersite/apps/metricas/`

**Archivos:**
- views.py
- serializers.py
- urls.py

**Endpoints:**
- [Ver especificacion completa](./metricas_api.md)

---

### 7. Horarios API

**Descripcion:** Gestion de horarios de atencion

**Ubicacion codigo:** `/api/callcentersite/callcentersite/apps/horarios/`

**Archivos:**
- views.py
- serializers.py
- urls.py

**Endpoints:**
- [Ver especificacion completa](./horarios_api.md)

---

## OpenAPI Specifications

Especificaciones OpenAPI 3.0 existentes:

```
docs/backend/api/
├── openapi_permisos.yaml           (Existente - Sistema de permisos)
├── openapi_prioridad_02.yaml       (Existente - Politicas)
├── openapi_dora_metrics.yaml       (Pendiente - DORA)
├── openapi_data_centralization.yaml (Pendiente - Centralizacion)
├── openapi_alertas.yaml            (Pendiente - Alertas)
├── openapi_configuracion.yaml      (Pendiente - Config)
├── openapi_metricas.yaml           (Pendiente - Metricas)
└── openapi_horarios.yaml           (Pendiente - Horarios)
```

---

## Autenticacion y Autorizacion

**Sistema de permisos:** Basado en Django REST Framework permissions

**Documentacion:**
- Sistema de permisos: [../permisos/](../permisos/)
- OpenAPI permisos: [openapi_permisos.yaml](./openapi_permisos.yaml)

**Tipos de autenticacion:**
- Session Authentication (Django)
- Token Authentication (DRF)
- JWT (pendiente evaluacion)

---

## Versionado de APIs

**Estrategia:** URL versioning

```
/api/v1/dora-metrics/
/api/v1/data-centralization/
/api/v1/politicas/
...
```

**Versionamiento:**
- v1: Version actual en produccion
- v2: Planificado para Q1 2026

---

## Rate Limiting

**Configuracion actual:**
- Anonimo: 100 requests/hour
- Autenticado: 1000 requests/hour
- Admin: Sin limite

**Implementacion:** Django REST Framework throttling

---

## Documentacion Tecnica por API

### Como documentar una nueva API

1. Crear archivo `{nombre}_api.md` en este directorio
2. Seguir template: [TEMPLATE_API_DOC.md](./TEMPLATE_API_DOC.md)
3. Generar OpenAPI spec: `{nombre}_openapi.yaml`
4. Actualizar este INDEX.md
5. Agregar tests de API en `/api/callcentersite/tests/`

### Template API Documentation

```markdown
# {Nombre} API

## Overview
[Descripcion breve]

## Endpoints

### GET /api/v1/{resource}/
[Descripcion]

**Parametros:**
- param1 (tipo): descripcion
- param2 (tipo): descripcion

**Respuesta exitosa (200):**
```json
{
  "field1": "value",
  "field2": 123
}
```

**Errores:**
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found

## Modelos

### {NombreModelo}

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| id | integer | ID unico |
| name | string | Nombre |

## Ejemplos

```bash
# Listar recursos
curl -X GET http://localhost:8000/api/v1/{resource}/ \
  -H "Authorization: Token {token}"
```
```

---

## Testing

**Ubicacion tests:** `/api/callcentersite/tests/`

**Ejecutar tests:**
```bash
cd api/callcentersite
python manage.py test
```

**Coverage esperado:** >80%

---

## Changelog

**v1.0.0** (2025-11-16)
- Creacion de INDEX.md
- Catalogacion de 7 APIs principales
- Identificacion de specs OpenAPI faltantes

---

## Tareas Pendientes

- [ ] Generar OpenAPI specs para APIs sin especificacion
- [ ] Documentar endpoints de cada API
- [ ] Agregar ejemplos de uso con curl
- [ ] Generar Postman collections
- [ ] Documentar esquemas de autenticacion
- [ ] Agregar diagramas de flujo de datos
- [ ] Documentar estrategia de cache

---

## Referencias

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [OpenAPI 3.0 Spec](https://swagger.io/specification/)
- [Backend Architecture](../arquitectura/)
- [Sistema de Permisos](../permisos/)

---

**Mantenido por:** Equipo Backend
**Owner:** Ver [CODEOWNERS](../../../.github/CODEOWNERS)
**Ultima revision:** 2025-11-16
