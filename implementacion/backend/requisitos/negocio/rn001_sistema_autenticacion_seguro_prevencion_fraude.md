---
id: RN-001
tipo: negocio
titulo: Sistema de autenticacion seguro con prevencion de fraude
dominio: backend
owner: equipo-producto
prioridad: critica
estado: aprobado
fecha_creacion: 2025-11-06
fecha_aprobacion: 2025-11-06
sponsor: director-operaciones

# Trazabilidad Upward
trazabilidad_upward:
  - N-001  # Prevenir accesos fraudulentos mediante autenticacion robusta

# Trazabilidad Downward
trazabilidad_downward:
  - RS-001  # Auditoria requiere trazabilidad completa
  - RS-002  # Usuarios requieren acceso rapido
  - RF-001  # Login con credenciales
  - RF-002  # Tokens JWT
  - RF-003  # Bloqueo intentos fallidos
  - RF-004  # Sesion unica
  - RF-005  # Logout manual
  - RF-006  # Recuperacion password sin email
  - RNF-001 # Tiempo respuesta login
  - RNF-002 # Sesiones en BD MySQL

# Stakeholders
stakeholders:
  - director-operaciones
  - gerente-seguridad
  - auditoria-interna
  - usuarios-finales
  - administradores-sistema

# Alineacion estrategica
objetivo_estrategico: OE-2025-SEC - Fortalecer seguridad de plataformas criticas
kpi_negocio: Reduccion de incidentes de seguridad en 80%

# Conformidad ISO 29148
iso29148_clause: "9.3"  # Business Requirements Specification
babok_knowledge_area: "Requirements Analysis and Design Definition"
verificacion_metodo: inspection

# Impacto en el negocio
impacto_financiero: alto
impacto_operacional: alto
urgencia: critica
---

# RN-001: Sistema de autenticacion seguro con prevencion de fraude

## 1. Descripcion del Requisito de Negocio

### 1.1 Declaracion del Requisito

**El negocio NECESITA** un sistema de autenticacion robusta que prevenga accesos fraudulentos, detecte patrones anomalos, y garantice que solo usuarios autorizados accedan a informacion critica del sistema IACT, reduciendo incidentes de seguridad en 80% y cumpliendo con estandares ISO 27001.

### 1.2 Contexto de Negocio

**Situacion actual:**
El sistema IACT actualmente gestiona operaciones criticas de call center con controles de autenticacion basicos que no cumplen con estandares corporativos de seguridad. La organizacion ha experimentado 3-5 incidentes de seguridad por trimestre relacionados con accesos no autorizados, consumiendo 20 horas/mes en investigacion manual.

**Problema u oportunidad:**
La falta de controles de autenticacion robustos expone a la organizacion a:
- Riesgo de brechas de seguridad con impacto financiero ($80K+ por incidente)
- Incumplimiento de politicas corporativas de seguridad
- Perdida de confianza de clientes que auditan seguridad
- Costos operativos elevados en investigacion de incidentes

**Justificacion:**
Implementar autenticacion robusta es critico para:
- Proteger informacion confidencial de metricas de negocio
- Cumplir con certificaciones de seguridad requeridas por clientes enterprise
- Reducir costos operativos de investigacion de incidentes
- Habilitar crecimiento comercial en segmento enterprise que exige controles estrictos

---

## 2. Objetivos de Negocio

### 2.1 Objetivo Principal

**Reducir incidentes de seguridad relacionados con accesos no autorizados en 80% mediante implementacion de autenticacion robusta con controles preventivos, detectivos y correctivos**

- Metrica de exito: Incidentes de seguridad mensual
- Target cuantitativo: De 1.5 incidentes/mes a 0.3 incidentes/mes
- Plazo: 6 meses post-implementacion (Q2 2026)

### 2.2 Objetivos Secundarios

1. **Objetivo secundario 1**: Reducir tiempo de investigacion de incidentes de seguridad
   - Metrica: Horas/mes investigacion equipo seguridad
   - Target: De 20 horas/mes a 4 horas/mes (reduccion 80%)

2. **Objetivo secundario 2**: Mejorar tiempo de deteccion de accesos anomalos
   - Metrica: Tiempo desde intento hasta deteccion
   - Target: De 48 horas a menos de 5 minutos

3. **Objetivo secundario 3**: Cumplir con controles de autenticacion ISO 27001
   - Metrica: Score auditoria ISO 27001 en controles de autenticacion
   - Target: 95%+ compliance (actualmente 60%)

---

## 3. Alcance de Negocio

### 3.1 Areas de Negocio Impactadas

| Area de Negocio | Tipo de Impacto | Nivel de Cambio | Stakeholder Responsable |
|-----------------|-----------------|-----------------|-------------------------|
| Seguridad Corporativa | Procesos | Alto | Gerente Seguridad |
| Operaciones Call Center | Tecnologia | Medio | Director Operaciones |
| Auditoria Interna | Procesos | Medio | Auditor Interno |
| Soporte Tecnico | Personas | Bajo | Jefe Soporte |

### 3.2 Procesos de Negocio Afectados

- **Proceso 1**: Acceso al sistema IACT
  - Cambio: Usuarios deben autenticarse con controles mas estrictos (bloqueo automatico, sesion unica)
  - Documentacion actual: Manual de usuario IACT v2.3

- **Proceso 2**: Investigacion de incidentes de seguridad
  - Cambio: Auditoria automatica reduce investigacion manual de 20h a 4h/mes
  - Documentacion actual: Runbook investigacion incidentes SEC-001

- **Proceso 3**: Recuperacion de acceso (password reset)
  - Cambio: Nuevo flujo con 3 preguntas de seguridad (NO email)
  - Documentacion actual: Procedimiento IT-RESET-001

### 3.3 Limitaciones de Alcance

**En alcance:**
- Autenticacion local username/password
- Bloqueo automatico tras intentos fallidos
- Sesion unica por usuario
- Recuperacion de password sin email
- Auditoria completa de eventos de autenticacion

**Fuera de alcance:**
- Multi-Factor Authentication (MFA) - planificado Fase 2
- Autenticacion con proveedores externos (LDAP, OAuth)
- Single Sign-On (SSO) corporativo
- Notificaciones por email (restriccion IACT)

---

## 4. Beneficios Esperados

### 4.1 Beneficios Cuantificables

| Categoria | Beneficio | Baseline Actual | Target | Timeline | ROI Estimado |
|-----------|-----------|-----------------|--------|----------|--------------|
| Financiero | Reduccion costo incidentes | $240K/anual | $48K/anual | Q2 2026 | 320% |
| Operacional | Reduccion tiempo investigacion | 20 horas/mes | 4 horas/mes | Q2 2026 | 80% reduccion |
| Cliente | Mejora trust score clientes | 6.5/10 | 8.5/10 | Q3 2026 | +30% |

**Detalle ROI:**
- Inversion inicial: $60K (desarrollo 6 semanas)
- Ahorro anual: $192K ($240K - $48K incidentes)
- Payback period: 3.75 meses
- ROI 3 anos: 860%

### 4.2 Beneficios Intangibles

- **Mejora en la satisfaccion del cliente**: Clientes enterprise valoran controles de seguridad robustos
- **Mejora en la moral de empleados**: Reduccion de estres por incidentes de seguridad frecuentes
- **Mejor posicionamiento competitivo**: Habilitador para ganar licitaciones que exigen ISO 27001
- **Cumplimiento regulatorio**: Alineacion con ISO 27001, reduciendo riesgo de multas

---

## 5. Metricas y KPIs

### 5.1 Key Performance Indicators (KPIs)

| KPI | Definicion | Formula de Calculo | Baseline | Target | Frecuencia de Medicion |
|-----|------------|-------------------|----------|--------|------------------------|
| Incidentes de seguridad auth | Incidentes relacionados con autenticacion | COUNT(incidentes WHERE categoria='autenticacion') | 1.5/mes | 0.3/mes | Mensual |
| Tiempo deteccion anomalias | Minutos desde intento hasta deteccion | AVG(timestamp_deteccion - timestamp_intento) | 2880 min | menor 5 min | Diaria |
| Intentos fraudulentos bloqueados | Intentos bloqueados automaticamente | COUNT(intentos WHERE bloqueado=TRUE) / COUNT(intentos) | 0% | 95%+ | Semanal |
| Cobertura auditoria | Eventos auditados vs eventos totales | COUNT(eventos_auditados) / COUNT(eventos_sistema) | 60% | 100% | Mensual |

### 5.2 Metricas de Seguimiento

| Metrica | Proposito | Responsable | Herramienta/Sistema |
|---------|-----------|-------------|---------------------|
| Login exitosos/dia | Monitorear operacion normal | Ops Manager | Dashboard IACT |
| Login fallidos/dia | Detectar patrones anomalos | Seguridad | Dashboard Auditoria |
| Cuentas bloqueadas/dia | Monitorear bloqueos automaticos | Soporte | Dashboard Admin |
| Tiempo promedio login | Verificar performance | Tech Lead | APM Monitoring |

---

## 6. Criterios de Exito del Negocio

### 6.1 Criterios de Aceptacion del Negocio

El requisito se considerara exitoso cuando:

1. **Reduccion de incidentes**: Incidentes de seguridad relacionados con autenticacion reducidos de 1.5/mes a 0.3/mes (80% reduccion)
   - Metodo de verificacion: Analisis de incidentes reportados en sistema de tickets
   - Responsable de verificacion: Gerente Seguridad

2. **Deteccion rapida**: 95%+ de intentos anomalos detectados en menos de 5 minutos
   - Metodo de verificacion: Analisis de logs de auditoria con timestamps
   - Responsable de verificacion: Auditor Interno

3. **Cumplimiento ISO 27001**: Score de compliance en controles de autenticacion mayor a 95%
   - Metodo de verificacion: Auditoria interna ISO 27001
   - Responsable de verificacion: Compliance Officer

4. **Reduccion de costos**: Tiempo de investigacion de incidentes reducido de 20h/mes a 4h/mes
   - Metodo de verificacion: Timesheet equipo seguridad
   - Responsable de verificacion: Gerente Seguridad

### 6.2 Umbrales Criticos

| Umbral | Valor Minimo Aceptable | Valor Objetivo | Valor Aspiracional |
|--------|------------------------|----------------|-------------------|
| Incidentes de seguridad | menor 1/mes | menor 0.5/mes | 0/mes |
| Tiempo deteccion | menor 15 min | menor 5 min | menor 1 min |
| Cobertura auditoria | 90%+ | 100% | 100% |
| Performance login | menor 3 seg | menor 2 seg | menor 1 seg |

---

## 7. Stakeholders y Roles

### 7.1 Matriz de Stakeholders

| Stakeholder | Rol/Posicion | Interes | Influencia | Expectativas | Necesidades |
|-------------|--------------|---------|------------|--------------|-------------|
| Director Operaciones | Sponsor | Alto | Alta | Sistema seguro sin impacto operacional | ROI positivo, cumplimiento ISO |
| Gerente Seguridad | Owner funcional | Alto | Alta | Controles robustos, auditoria completa | Deteccion temprana, trazabilidad |
| Auditor Interno | Validador | Alto | Media | Compliance ISO 27001 | Logs inmutables, reportes automaticos |
| Usuarios Finales | Usuario sistema | Medio | Baja | Acceso rapido sin friccion | Login menor 2 seg, password recovery facil |
| Administradores Sistema | Gestor cuentas | Alto | Media | Herramientas admin eficientes | Dashboard admin, desbloqueo facil |

### 7.2 RACI del Requisito

| Actividad | Responsable (R) | Accountable (A) | Consultado (C) | Informado (I) |
|-----------|-----------------|-----------------|----------------|---------------|
| Definicion del requisito | BA Lead | Director Operaciones | Gerente Seguridad, Auditoria | Equipos tecnicos |
| Aprobacion del requisito | Director Operaciones | CTO | Legal, Compliance | Todos stakeholders |
| Implementacion | Tech Lead Backend | PMO | BA, Arquitecto | Stakeholders |
| Verificacion | QA Lead | Product Owner | BA, Gerente Seguridad | Todos stakeholders |

---

## 8. Restricciones y Supuestos

### 8.1 Restricciones de Negocio

| ID | Restriccion | Tipo | Impacto | Mitigation |
|----|-------------|------|---------|------------|
| C-01 | Presupuesto maximo $60K | Presupuesto | Alto | Desarrollo interno vs SaaS externo |
| C-02 | Timeline maximo 6 semanas | Tiempo | Alto | Scope control estricto, MVP approach |
| C-03 | NO usar email para notificaciones | Tecnologia | Medio | Usar buzon interno InternalMessage |
| C-04 | Sesiones en MySQL NO Redis | Tecnologia | Medio | Arquitectura existente ya usa MySQL sessions |

### 8.2 Supuestos de Negocio

| ID | Supuesto | Validacion | Riesgo si es Falso |
|----|----------|------------|--------------------|
| A-01 | Usuarios aceptan sesion unica | Training + comunicacion | Resistencia al cambio, requiere change management |
| A-02 | Infraestructura soporta bcrypt cost 12 | Benchmark performance | Performance degradada, requiere optimizacion |
| A-03 | Equipo desarrollo tiene 2 FTE × 6 sem | Confirmacion PMO | Timeline extendido, requiere replanificacion |
| A-04 | Buzon interno soporta notificaciones | Validacion tecnica | Requiere desarrollo adicional de InternalMessage |

---

## 9. Derivacion a Requisitos de Nivel Inferior

### 9.1 Requisitos de Stakeholders Derivados

Este requisito de negocio se descompone en los siguientes requisitos de stakeholders:

- **RS-001**: Auditoria requiere trazabilidad completa de accesos
  - Stakeholder afectado: Auditor Interno
  - Link: [../stakeholders/rs001_auditoria_requiere_trazabilidad.md]

- **RS-002**: Usuarios requieren acceso rapido menor 2 segundos
  - Stakeholder afectado: Usuario Final
  - Link: [../stakeholders/rs002_usuarios_requieren_acceso_rapido.md]

### 9.2 Requisitos Funcionales Derivados

- **RF-001**: Login con credenciales username/password - [Dominio: backend]
- **RF-002**: Generacion de tokens JWT (access 15min, refresh 7dias) - [Dominio: backend]
- **RF-003**: Bloqueo automatico tras 5 intentos fallidos en 5 minutos - [Dominio: backend]
- **RF-004**: Sesion unica con cierre de sesiones previas - [Dominio: backend]
- **RF-005**: Logout manual con invalidacion de tokens - [Dominio: backend]
- **RF-006**: Recuperacion de password sin email mediante 3 preguntas seguridad - [Dominio: backend]

### 9.3 Requisitos No Funcionales Derivados

- **RNF-001**: Tiempo de respuesta login menor 2 segundos P95 - [Performance]
- **RNF-002**: Sesiones almacenadas en MySQL (NO Redis) - [Technical constraint]

---

## 10. Analisis de Impacto

### 10.1 Analisis Financiero

| Concepto | Ano 1 | Ano 2 | Ano 3 | Total 3 anos |
|----------|-------|-------|-------|--------------|
| **Costos** |
| Desarrollo | $60K | $0 | $0 | $60K |
| Mantenimiento | $0 | $8K | $8K | $16K |
| Capacitacion | $5K | $0 | $0 | $5K |
| **Total Costos** | **$65K** | **$8K** | **$8K** | **$81K** |
| **Beneficios** |
| Reduccion costo incidentes | $192K | $192K | $192K | $576K |
| Reduccion tiempo investigacion | $48K | $48K | $48K | $144K |
| **Total Beneficios** | **$240K** | **$240K** | **$240K** | **$720K** |
| **Beneficio Neto** | **$175K** | **$232K** | **$232K** | **$639K** |
| **ROI Acumulado** | 269% | 590% | 889% | **789%** |
| **Payback Period** | | | | **3.25 meses** |

### 10.2 Analisis de Riesgos de Negocio

| ID | Riesgo | Probabilidad | Impacto | Exposicion | Estrategia | Owner |
|----|--------|--------------|---------|------------|------------|-------|
| R-01 | Usuarios rechazan sesion unica | Media | Medio | Media | Mitigar: Training proactivo + comunicacion | Gerente Seguridad |
| R-02 | Performance degradada por controles | Baja | Alto | Media | Mitigar: Benchmarking continuo + optimizacion | Tech Lead |
| R-03 | Bloqueos falsos positivos | Media | Bajo | Baja | Aceptar: Mecanismo desbloqueo admin rapido | Soporte |
| R-04 | Timeline extendido por complejidad | Media | Medio | Media | Mitigar: MVP approach + scope control | PMO |

---

## 11. Cambio Organizacional

### 11.1 Gestion del Cambio

**Nivel de cambio organizacional**: Medio

**Areas de impacto:**

| Dimension | Impacto | Descripcion | Plan de Gestion |
|-----------|---------|-------------|-----------------|
| **Procesos** | Medio | Usuarios deben adaptarse a sesion unica y bloqueos automaticos | Training online + comunicacion proactiva |
| **Personas** | Bajo | Sin cambios en roles ni responsabilidades | Comunicacion de beneficios de seguridad |
| **Tecnologia** | Alto | Nueva arquitectura de autenticacion con controles robustos | Documentacion tecnica + runbooks operativos |
| **Cultura** | Medio | Mayor consciencia de seguridad en uso del sistema | Campaña de concientizacion en seguridad |

### 11.2 Plan de Capacitacion

- **Grupo 1**: Usuarios Finales (200 usuarios)
  - Capacitacion requerida: Nuevos controles de autenticacion, sesion unica, recovery password
  - Duracion: 1 hora (webinar grabado)
  - Fecha objetivo: 2025-12-15

- **Grupo 2**: Administradores Sistema (5 usuarios)
  - Capacitacion requerida: Dashboard admin, desbloqueo de cuentas, gestion de incidentes
  - Duracion: 4 horas (hands-on training)
  - Fecha objetivo: 2025-12-10

- **Grupo 3**: Soporte Tecnico (10 usuarios)
  - Capacitacion requerida: Troubleshooting autenticacion, escalacion de incidentes
  - Duracion: 2 horas (workshop)
  - Fecha objetivo: 2025-12-12

---

## 12. Trazabilidad

### 12.1 Trazabilidad Upward (Origen)

Este requisito de negocio deriva de:

| Tipo | ID | Titulo | Justificacion |
|------|----|----|---------------|
| Necesidad | [N-001](../necesidades/n001_autenticacion_robusta_prevenir_fraude.md) | Prevenir accesos fraudulentos mediante autenticacion robusta | RN-001 satisface necesidad implementando controles preventivos, detectivos y correctivos |
| Objetivo Estrategico | OE-2025-SEC | Fortalecer seguridad de plataformas criticas | Alineacion directa con objetivo corporativo de ciberseguridad |

### 12.2 Trazabilidad Downward (Derivados)

Este requisito genera:

**Requisitos de Stakeholders:**
- [RS-001](../stakeholders/rs001_auditoria_requiere_trazabilidad.md) - Auditoria requiere trazabilidad completa
- [RS-002](../stakeholders/rs002_usuarios_requieren_acceso_rapido.md) - Usuarios requieren acceso rapido

**Requisitos de Solucion:**
- [RF-001](../funcionales/rf001_login_credenciales.md) - Login con credenciales
- [RF-002](../funcionales/rf002_jwt_tokens.md) - Tokens JWT
- [RF-003](../funcionales/rf003_bloqueo_intentos_fallidos.md) - Bloqueo intentos fallidos
- [RF-004](../funcionales/rf004_sesion_unica.md) - Sesion unica
- [RF-005](../funcionales/rf005_logout.md) - Logout manual
- [RF-006](../funcionales/rf006_recuperacion_sin_email.md) - Recuperacion password sin email
- [RNF-001](../no_funcionales/rnf001_tiempo_respuesta_login.md) - Performance login
- [RNF-002](../no_funcionales/rnf002_sesiones_en_bd.md) - Sesiones en MySQL

**Proyectos/Iniciativas:**
- PROJ-AUTH-2025 - Implementacion autenticacion robusta

---

## 13. Verificacion y Validacion

### 13.1 Metodo de Verificacion

**Metodo**: Inspection

**Criterios de verificacion:**
- Requisito esta correctamente derivado de necesidad N-001
- Requisito es medible y tiene KPIs asociados (4 KPIs definidos)
- Stakeholders han sido identificados y consultados (5 stakeholders principales)
- Beneficios estan cuantificados (ROI 789% a 3 anos)
- Riesgos han sido identificados y mitigados (4 riesgos principales)

### 13.2 Plan de Validacion con el Negocio

| Hito | Actividad de Validacion | Stakeholders Involucrados | Fecha Objetivo | Estado |
|------|-------------------------|---------------------------|----------------|--------|
| Hito 1 | Demo sistema autenticacion en DEV | Director Operaciones, Gerente Seguridad | 2025-11-20 | Pendiente |
| Hito 2 | Validacion auditoria completa | Auditor Interno | 2025-12-04 | Pendiente |
| Hito 3 | UAT con usuarios finales | 10 usuarios piloto | 2025-12-11 | Pendiente |
| Hito 4 | Aprobacion go-live produccion | Director Operaciones, CTO | 2025-12-18 | Pendiente |

---

## 14. Aprobaciones

| Rol | Nombre | Fecha | Firma/Estado |
|-----|--------|-------|--------------|
| **Sponsor Ejecutivo** | Director Operaciones | 2025-11-06 | Aprobado |
| **Business Owner** | Gerente Seguridad | 2025-11-06 | Aprobado |
| **PMO** | PMO Manager | 2025-11-06 | Aprobado |
| **Finance** | Finance Manager | 2025-11-06 | Revisado |
| **Legal/Compliance** | Compliance Officer | 2025-11-06 | Revisado |
| **BA Lead** | BA Team Lead | 2025-11-06 | Revisado |

---

## 15. Referencias

### 15.1 Documentos Relacionados

- [Necesidad N-001](../necesidades/n001_autenticacion_robusta_prevenir_fraude.md)
- Codigo existente: api/callcentersite/callcentersite/apps/authentication/
- Restricciones IACT: restricciones_y_lineamientos.md

### 15.2 Estándares Aplicados

- ISO/IEC/IEEE 29148:2018: Clause 9.3 - Business Requirements Specification (BRS)
- BABOK v3: Requirements Analysis and Design Definition
- PMBOK Guide 7th Ed: Value Delivery Components
- ISO/IEC 27001:2013: Information Security Management
- OWASP ASVS v4.0: Authentication Verification Requirements

---

## Control de Cambios

| Version | Fecha | Autor | Descripcion del Cambio | Impacto | Aprobado Por |
|---------|-------|-------|------------------------|---------|--------------|
| 1.0 | 2025-11-06 | BA Team | Creacion inicial derivada de N-001 | Alto | Director Operaciones |

---

Notas:
- Requisito de negocio expresa RESULTADOS de negocio, no soluciones tecnicas
- Beneficios cuantificados: ROI 789% a 3 anos, payback 3.25 meses
- Trazabilidad bidireccional completa: upward a N-001, downward a RS y RF
- Cumple restricciones IACT: NO email, sesiones en MySQL, BD IVR readonly
