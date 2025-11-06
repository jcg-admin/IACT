---
id: RS-001
tipo: stakeholder
titulo: Dashboard de seguridad para monitoreo continuo
dominio: backend
owner: equipo-ba
prioridad: alta
estado: aprobado
fecha_creacion: 2025-11-06
fecha_aprobacion: 2025-11-06

stakeholder_primario: ciso
stakeholder_tipo: gerente

trazabilidad_upward:
  - N-001
  - RN-001

trazabilidad_downward:
  - RF-010
  - RNF-001

stakeholders_secundarios:
  - security-team
  - gerente-ti

contexto_uso: Monitoreo diario de eventos de seguridad
frecuencia_uso: diaria
criticidad_operacional: alta

iso29148_clause: "9.4"
babok_knowledge_area: "Requirements Analysis and Design Definition"
verificacion_metodo: demonstration

categoria_ux: usabilidad
impacto_experiencia: alto
---

# RS-001: Dashboard de seguridad para monitoreo continuo

## 1. Descripción del Requisito de Stakeholder

### 1.1 Declaración del Requisito

**Como** CISO (Chief Information Security Officer),
**Necesito** un dashboard de seguridad en tiempo real que muestre intentos de login fallidos, acciones sospechosas y métricas de seguridad clave,
**Para** poder detectar y responder a incidentes de seguridad en <5 minutos y demostrar postura de seguridad en auditorías.

### 1.2 Descripción Narrativa

El CISO necesita visibilidad continua del estado de seguridad del sistema de call center. Actualmente, no existe un mecanismo centralizado para monitorear eventos de seguridad, lo que impide la detección temprana de intentos de acceso malicioso y dificulta la demostración de compliance en auditorías.

**¿Qué necesita el stakeholder?**
Un dashboard web que muestre en tiempo real:
- Intentos de login fallidos (últimas 24 horas)
- Usuarios con múltiples intentos fallidos (indicador de brute-force)
- Acciones críticas realizadas (modificaciones en datos sensibles)
- Métricas clave: total de accesos, acciones auditadas, alertas activas
- Timeline de eventos de seguridad

**¿Por qué lo necesita?**
- Detección proactiva de intentos de acceso malicioso
- Respuesta rápida a incidentes (<5 minutos vs. horas/días)
- Evidencia visual para auditorías y reportes ejecutivos
- Monitoreo continuo de compliance

**¿Cuándo y dónde lo necesita?**
- Acceso diario desde oficina (desktop) o remoto (laptop)
- Revisión matinal (15 minutos) para detectar eventos nocturnos
- Acceso bajo demanda durante incidentes

---

## 2. Perfil del Stakeholder

### 2.1 Información del Stakeholder

| Atributo | Valor |
|----------|-------|
| Nombre/Rol | CISO (Chief Information Security Officer) |
| Departamento/Área | Seguridad TI |
| Nivel jerárquico | Ejecutivo |
| Experiencia técnica | Alta |
| Frecuencia de interacción con sistema | Diaria |
| Canales de acceso | Desktop, Laptop |
| Idioma preferido | Español |
| Necesidades de accesibilidad | No |

### 2.2 Contexto de Trabajo del Stakeholder

**Entorno de trabajo:**
Oficina con múltiples monitores, necesita vista rápida de estado de seguridad mientras gestiona otras responsabilidades.

**Flujo de trabajo típico:**
1. Ingreso a oficina (8:00 AM)
2. Revisar dashboard de seguridad (15 minutos)
3. Identificar alertas o anomalías
4. Investigar eventos sospechosos si existen
5. Revisiones periódicas durante el día

**Herramientas que usa actualmente:**
- SIEM básico (logs de firewall)
- Email alerts (configurado manualmente)
- Excel para análisis manual de logs

**Puntos de dolor actuales:**
- Sin vista consolidada de eventos de seguridad
- Análisis manual de logs consume 2-3 horas/día
- Detección de incidentes es reactiva (post-facto)

---

## 3. Criterios de Aceptación del Stakeholder

### 3.1 Criterios en Formato Gherkin

#### Escenario 1: Visualización de intentos de login fallidos

```gherkin
Given soy CISO autenticado en el sistema
  And existen intentos de login fallidos en las últimas 24 horas
When accedo al dashboard de seguridad
Then veo una tabla con intentos de login fallidos ordenados por timestamp
  And cada fila muestra: timestamp, username, IP address, user agent, razón de fallo
  And veo un resumen: total de intentos fallidos y usuarios únicos afectados
  And puedo filtrar por username o rango de fechas
```

#### Escenario 2: Detección de brute-force attack

```gherkin
Given soy CISO en el dashboard de seguridad
  And un usuario tiene ≥5 intentos fallidos en últimos 30 minutos
When el sistema detecta el patrón de brute-force
Then veo una alerta visual destacada en el dashboard
  And la alerta muestra: username afectado, cantidad de intentos, última IP
  And puedo hacer click para ver detalles completos
```

#### Escenario 3: Visualización de métricas clave

```gherkin
Given soy CISO en el dashboard de seguridad
When la página carga
Then veo 4 widgets con métricas clave:
  - Total de logins exitosos (últimas 24h)
  - Total de intentos fallidos (últimas 24h)
  - Acciones auditadas (últimas 24h)
  - Alertas activas (requieren atención)
And cada widget muestra tendencia (↑↓ respecto a ayer)
```

### 3.2 Criterios de Satisfacción del Stakeholder

El stakeholder considerará este requisito satisfactorio cuando:

- Dashboard carga en <3 segundos
- Información se actualiza automáticamente cada 30 segundos
- Puede identificar intentos de brute-force en <1 minuto de revisión
- Dashboard es accesible 24/7 desde cualquier ubicación

---

## 4. Valor para el Stakeholder

### 4.1 Beneficios Directos

| Beneficio | Descripción | Impacto | Medición |
|-----------|-------------|---------|----------|
| Detección proactiva | Identificar intentos maliciosos en tiempo real | Alto | Tiempo de detección <5 min |
| Ahorro de tiempo | Eliminar análisis manual de logs | Alto | -2 horas/día (80% reducción) |
| Evidencia visual | Demostrar postura de seguridad en auditorías | Alto | Satisfacción auditor 9/10 |

### 4.2 Impacto en el Trabajo del Stakeholder

**Antes (sin este requisito):**
- Tiempo invertido: 2-3 horas/día en análisis manual de logs dispersos
- Errores: Incidentes no detectados hasta post-facto
- Frustración: Imposibilidad de demostrar compliance visual

**Después (con este requisito):**
- Tiempo invertido: 15 minutos/día en revisión de dashboard
- Errores: Detección proactiva en <5 minutos
- Satisfacción: Vista consolidada, evidencia visual para auditorías

### 4.3 Costo de NO tener este Requisito

**Para el stakeholder:**
- 2-3 horas/día perdidas en análisis manual ($50K/año en costo CISO)
- Incidentes detectados tarde (riesgo de propagación)

**Para el negocio:**
- Riesgo de incidentes no detectados ($150K promedio por incidente)
- Imposibilidad de demostrar monitoreo continuo en auditorías

---

## 5. Escenarios de Uso

### 5.1 Escenario Principal de Uso

**Título:** Revisión matinal de eventos de seguridad

**Actor:** CISO

**Precondiciones:**
- CISO autenticado en el sistema
- Dashboard de seguridad implementado

**Flujo Principal:**
1. CISO accede a URL del dashboard de seguridad
2. Sistema muestra vista general con 4 widgets de métricas clave
3. CISO identifica alerta de brute-force (usuario "admin" con 8 intentos fallidos)
4. CISO hace click en la alerta para ver detalles
5. Sistema muestra timeline completo de intentos con IPs y user agents
6. CISO decide bloquear IP origen y notificar al equipo de seguridad

**Postcondiciones:**
- CISO tiene visibilidad completa de eventos nocturnos
- Incidente detectado y escalado en <5 minutos

**Frecuencia de uso:** 1-2 veces por día (mañana y tarde)

---

## 6. Requisitos de Información

### 6.1 Información que el Stakeholder Necesita Ver

| Dato/Información | Propósito | Formato Preferido | Frecuencia de Actualización |
|------------------|-----------|-------------------|----------------------------|
| Intentos login fallidos | Detectar brute-force | Tabla con paginación | Tiempo real (30s) |
| Métricas resumen | Vista general estado seguridad | Widgets numéricos con íconos | Tiempo real (30s) |
| Alertas activas | Priorizar respuesta | Lista destacada | Tiempo real (30s) |
| Timeline eventos | Contexto temporal | Gráfico de línea temporal | Tiempo real (30s) |

### 6.2 Información que el Stakeholder Debe Proporcionar

| Dato/Input | Propósito | Formato | Validaciones Requeridas |
|------------|-----------|---------|------------------------|
| Rango de fechas (filtro) | Filtrar eventos históricos | Date picker | fecha_inicio ≤ fecha_fin |
| Username (filtro) | Buscar eventos de usuario específico | Text input | Alfanumérico |

---

## 7. Derivación a Requisitos de Sistema/Software

### 7.1 Requisitos Funcionales Derivados

Este requisito de stakeholder se implementa mediante:

- **RF-010**: Dashboard de seguridad en tiempo real (frontend)
  - Dominio: frontend
  - Link: ../../frontend/requisitos/funcionales/rf010_dashboard_seguridad_tiempo_real.md
  - Relación: RF-010 implementa la interfaz visual para RS-001

- **RF-002**: Auditoría inmutable de acciones críticas (backend)
  - Dominio: backend
  - Link: ../funcionales/rf002_auditoria_inmutable_acciones_criticas.md
  - Relación: RF-002 proporciona los datos que RS-001 visualiza

### 7.2 Requisitos No Funcionales Derivados

- **RNF-001**: Performance - dashboard carga en <3s, actualizaciones cada 30s
- **RNF-020**: Disponibilidad - dashboard accesible 24/7 (99.5% uptime)

---

## 8. Validación con el Stakeholder

### 8.1 Plan de Validación

| Hito | Actividad de Validación | Método | Stakeholder(s) | Fecha | Estado |
|------|-------------------------|--------|----------------|-------|--------|
| Hito 1 | Revisión de wireframes | Mockup review | CISO, Security Team | 2025-11-20 | Pendiente |
| Hito 2 | Demo de dashboard funcional | Prototipo | CISO | 2025-12-18 | Pendiente |
| Hito 3 | UAT en staging | User Acceptance Test | CISO, Security Team | 2026-01-08 | Pendiente |

### 8.2 Criterios de Validación

El stakeholder confirmará que el requisito está correcto cuando:

- Comprensión: CISO confirma que dashboard muestra información que necesita
- Completitud: No faltan métricas o vistas críticas para monitoreo
- Viabilidad: CISO puede usar dashboard en workflow diario sin fricción
- Valor: CISO confirma ahorro de ≥2 horas/día en monitoreo manual

---

## 9. Trazabilidad

### 9.1 Trazabilidad Upward (Origen)

Este requisito de stakeholder deriva de:

| Tipo | ID | Título | Justificación |
|------|----|----|---------------|
| Necesidad | N-001 | Garantizar seguridad operacional y cumplimiento normativo | RS-001 aborda necesidad mediante visibilidad continua para CISO |
| Req. Negocio | RN-001 | Sistema de seguridad y auditoría conforme a ISO 27001 | RS-001 es componente clave para monitoreo (ISO 27001 A.12.4) |

### 9.2 Trazabilidad Downward (Implementación)

Este requisito se implementa mediante:

**Requisitos Funcionales:**
- RF-010 (frontend): Dashboard de seguridad en tiempo real
- RF-002 (backend): Auditoría inmutable de acciones críticas

**Requisitos No Funcionales:**
- RNF-001: Performance dashboard <3s carga
- RNF-020: Disponibilidad 99.5%

---

## 10. Aprobaciones

| Rol | Nombre | Fecha | Firma/Estado |
|-----|--------|-------|--------------|
| Stakeholder Primario | CISO | 2025-11-06 | Aprobado |
| Product Owner | Product Manager | 2025-11-06 | Aprobado |
| Business Analyst | BA Lead | 2025-11-06 | Documentado |
| UX Designer | UX Lead | 2025-11-06 | Revisado |

---

## 11. Referencias

### 11.1 Documentos Relacionados

- Necesidad origen: ../necesidades/n001_garantizar_seguridad_cumplimiento_normativo.md
- Requisito negocio: ../negocio/rn001_sistema_seguridad_auditoria_conforme_iso27001.md
- Código existente: api/callcentersite/callcentersite/apps/dashboard/

### 11.2 Estándares Aplicados

- ISO/IEC/IEEE 29148:2018: Clause 9.4 - Stakeholder Requirements Specification (StRS)
- BABOK v3: Requirements Analysis and Design Definition
- ISO 27001:2013: A.12.4 - Logging and Monitoring

---

## Control de Cambios

| Versión | Fecha | Autor | Descripción del Cambio | Stakeholder Notificado |
|---------|-------|-------|------------------------|------------------------|
| 1.0 | 2025-11-06 | BA Team | Creación inicial derivado de RN-001 | Sí |
