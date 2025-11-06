---
id: N-001
tipo: necesidad
titulo: Prevenir accesos fraudulentos mediante autenticacion robusta
dominio: backend
owner: equipo-seguridad
prioridad: critica
estado: aprobado
fecha_creacion: 2025-11-06
fecha_aprobacion: 2025-11-06
sponsor: director-operaciones
stakeholders:
  - gerente-seguridad
  - auditoria-interna
  - usuarios-finales
  - director-operaciones
babok_knowledge_area: "Business Analysis Planning and Monitoring"
iso29148_clause: "6.2"
valor_negocio: alto
urgencia: critica
---

# N-001: Prevenir accesos fraudulentos mediante autenticacion robusta

## 1. Descripcion de la Necesidad

### 1.1 Problema u Oportunidad

El sistema IACT maneja informacion critica de operaciones de call center, incluyendo metricas de negocio, datos de clientes y configuraciones operativas sensibles. Actualmente, el sistema de autenticacion presenta vulnerabilidades que exponen a la organizacion a:

- Ataques de fuerza bruta contra credenciales de usuario
- Accesos no autorizados mediante robo de credenciales
- Suplantacion de identidad sin deteccion oportuna
- Sesiones concurrentes que facilitan compartir credenciales
- Falta de trazabilidad completa de intentos de acceso fallidos

En los ultimos 6 meses se han registrado:
- 847 intentos de acceso con credenciales invalidas
- 23 cuentas bloqueadas manualmente por actividad sospechosa
- 12 incidentes de sesiones compartidas entre usuarios
- Tiempo promedio de deteccion de acceso no autorizado: 48 horas

El impacto en el negocio incluye:
- Riesgo de exposicion de metricas confidenciales de negocio
- Perdida de confianza de clientes por incidentes de seguridad
- Incumplimiento de politicas de seguridad corporativas
- 15-20 horas/mes de trabajo manual en investigacion de incidentes

### 1.2 Situacion Actual (As-Is)

**Proceso actual:**
- Autenticacion basica username/password sin controles de intentos fallidos robustos
- No hay bloqueo automatico tras multiples intentos fallidos
- Usuarios pueden mantener multiples sesiones simultaneas
- Tokens JWT con duracion fija sin renovacion automatica
- Logs de autenticacion dispersos sin centralizacion
- Sin notificaciones proactivas de intentos de acceso sospechosos

**Impacto negativo:**
- Vulnerabilidad a ataques de fuerza bruta (sin rate limiting efectivo)
- Imposibilidad de detectar patrones de acceso anomalos en tiempo real
- Comparticion de credenciales sin mecanismos de prevencion
- Investigacion manual de incidentes consume 20 horas/mes
- Sin capacidad de respuesta automatizada ante intentos maliciosos

**Frecuencia del problema:**
- Intentos de acceso fallidos: 140-150/mes en promedio
- Incidentes de seguridad reportados: 3-5/trimestre
- Tiempo de respuesta ante incidentes: 24-48 horas

### 1.3 Situacion Deseada (To-Be)

**Proceso objetivo:**
- Sistema de autenticacion con bloqueo automatico tras intentos fallidos
- Deteccion de patrones de acceso anomalos (horarios, ubicaciones, dispositivos)
- Sesion unica por usuario con cierre automatico de sesiones previas
- Tokens JWT con renovacion automatica y revocacion inmediata
- Trazabilidad completa e inmutable de todos los intentos de acceso
- Notificaciones automaticas via buzon interno ante actividades sospechosas

**Beneficios esperados:**
- Reduccion de 95% en intentos de acceso fraudulentos exitosos
- Deteccion de actividad sospechosa en menos de 5 minutos
- Reduccion de 80% en tiempo de investigacion de incidentes (de 20h a 4h/mes)
- Bloqueo automatico de cuentas comprometidas sin intervencion manual
- Cumplimiento con estandares de seguridad ISO 27001

**Criterios de exito:**
- 100% de intentos de acceso registrados y auditados
- Bloqueo automatico tras 5 intentos fallidos en ventana de 5 minutos
- Tiempo de deteccion de actividad anomala menor a 5 minutos
- Zero sesiones concurrentes por usuario (sesion unica estricta)
- Notificacion automatica al usuario ante cierre de sesion por nueva autenticacion

---

## 2. Justificacion de Negocio

### 2.1 Impacto en el Negocio

| Dimension | Impacto Actual | Impacto Esperado |
|-----------|----------------|-------------------|
| Financiero | $48K/anual en investigacion manual de incidentes | $10K/anual (reduccion 79%) |
| Operacional | 20 horas/mes en investigacion de seguridad | 4 horas/mes (reduccion 80%) |
| Cliente | Riesgo reputacional por exposicion de datos | Mejora en trust score +30% |
| Estrategico | Incumplimiento parcial ISO 27001 | Compliance total con ISO 27001 |

### 2.2 Costo de No Hacer Nada

**Cuantificacion del riesgo:**
- Costo anual estimado: $150K - $500K
  - Investigacion manual de incidentes: $48K/anual
  - Costo promedio de incidente de seguridad: $80K (Ponemon Institute)
  - Perdida de clientes por incidentes: $200K+ potencial
  - Multas por incumplimiento normativo: $50K+ potencial

**Riesgos asociados:**
- Brecha de seguridad por acceso no autorizado (probabilidad: 25% anual)
- Perdida de certificaciones de seguridad requeridas por clientes
- Demandas legales por exposicion de datos de clientes
- Dano reputacional irreparable en sector corporativo

**Oportunidades perdidas:**
- Imposibilidad de ganar licitaciones que exigen controles de seguridad estrictos
- Rechazo de clientes enterprise que auditan seguridad
- Costos adicionales de seguros ciberneticos por controles inadecuados

---

## 3. Alcance

### 3.1 En Alcance

- Sistema de autenticacion con username/password y validacion robusta
- Generacion de tokens JWT (access 15 minutos, refresh 7 dias)
- Bloqueo automatico tras intentos fallidos (5 intentos/5 minutos)
- Desbloqueo automatico tras periodo de tiempo (15 minutos)
- Sesion unica por usuario con cierre de sesiones previas
- Logout manual con invalidacion de tokens
- Cierre automatico de sesion por inactividad (30 minutos)
- Recuperacion de contrasena sin email (3 preguntas de seguridad)
- Cambio de contrasena con validacion de fortaleza
- Gestion de sesiones en base de datos MySQL (NO Redis)
- Auditoria completa de eventos de autenticacion
- Notificaciones via buzon interno (NO email)

### 3.2 Fuera de Alcance

- Multi-Factor Authentication (MFA) - planificado para Fase 2
- Autenticacion con proveedores externos (LDAP, OAuth, SAML)
- Autenticacion biometrica
- Single Sign-On (SSO) corporativo
- Sistema de deteccion de anomalias con Machine Learning
- Notificaciones por email (restriccion IACT)
- Almacenamiento de sesiones en Redis (restriccion IACT)

### 3.3 Supuestos

1. Base de datos MySQL soporta almacenamiento de sesiones
2. Infraestructura actual soporta algoritmo bcrypt con cost factor 12
3. Equipo de desarrollo tiene 2 FTE durante 6 semanas
4. Usuarios aceptan politica de sesion unica (training requerido)
5. Buzon interno soporta notificaciones automaticas
6. Apps authentication/ y users/ ya existen en codebase

### 3.4 Restricciones

1. Presupuesto: Maximo $60K para implementacion (2 FTE × 6 semanas)
2. Tiempo: Implementacion completa en 6 semanas (Q4 2025)
3. Recursos: 2 developers backend + 1 developer frontend + 0.5 QA
4. Tecnologia: Django 4.2 + MySQL + djangorestframework-simplejwt
5. CRITICO: NO usar email - solo buzon interno (InternalMessage model)
6. CRITICO: Sesiones en MySQL, NO Redis
7. CRITICO: BD IVR readonly - zero escritura en BD legacy

---

## 4. Stakeholders Afectados

| Stakeholder | Rol | Interes | Impacto | Influencia |
|-------------|-----|---------|---------|------------|
| Director Operaciones | Sponsor ejecutivo | alto | positivo | alta |
| Gerente Seguridad | Owner funcional | alto | positivo | alta |
| Auditoria Interna | Validador compliance | alto | positivo | media |
| Usuarios Finales | Usuario del sistema | medio | neutro | baja |
| Administradores Sistema | Gestionan cuentas | alto | positivo | media |
| Legal | Validador normativo | medio | positivo | media |
| Soporte Tecnico | Resuelven incidentes | medio | positivo | baja |

---

## 5. Criterios de Exito

### 5.1 Metricas de Exito (KPIs)

| KPI | Baseline Actual | Target | Metodo de Medicion |
|-----|-----------------|--------|--------------------|
| Tiempo deteccion acceso no autorizado | 48 horas | menor 5 minutos | Dashboard auditoria tiempo real |
| Intentos fraudulentos exitosos | 3-5/trimestre | 0-1/trimestre | Analisis logs auditoria |
| Tiempo investigacion incidentes | 20 horas/mes | 4 horas/mes | Timesheet equipo seguridad |
| Sesiones concurrentes por usuario | Ilimitadas | 1 (sesion unica) | Query base de datos |
| Cobertura auditoria eventos auth | 60% | 100% | Analisis logs vs eventos sistema |

### 5.2 Criterios de Aceptacion del Negocio

1. **Bloqueo automatico**: Cuenta bloqueada tras 5 intentos fallidos en ventana de 5 minutos
2. **Sesion unica**: Usuario con sesion activa cierra sesion previa al iniciar nueva
3. **Auditoria completa**: 100% de login, logout, intentos fallidos, bloqueos registrados
4. **Notificaciones**: Usuario recibe notificacion en buzon interno ante cierre de sesion
5. **Performance**: Login completo (validacion + token generation) en menos de 2 segundos (P95)

---

## 6. Analisis de Alternativas

### 6.1 Opciones Evaluadas

#### Opcion 1: Desarrollo interno con modulos Django existentes
- Descripcion: Extender apps authentication/ y users/ existentes con nuevas features
- Pros: Control total, integracion nativa con stack, aprovecha codigo existente
- Contras: Requiere 6 semanas desarrollo, requiere expertise en seguridad
- Costo estimado: $60K (desarrollo) + $8K/anual (mantenimiento)
- Tiempo estimado: 6 semanas

#### Opcion 2: Libreria externa Django (django-axes + django-defender)
- Descripcion: Integrar librerias especializadas en proteccion de autenticacion
- Pros: Implementacion rapida (2-3 semanas), features probadas, mantenimiento externo
- Contras: Menor flexibilidad, posible overhead, curva de aprendizaje
- Costo estimado: $25K (integracion) + $5K/anual (upgrades)
- Tiempo estimado: 3 semanas

#### Opcion 3: Solucion SaaS (Auth0, AWS Cognito)
- Descripcion: Delegar autenticacion a proveedor externo
- Pros: Implementacion muy rapida (1-2 semanas), features avanzados, escalabilidad
- Contras: Costo recurrente alto, lock-in vendor, datos en terceros, no cumple restricciones IACT
- Costo estimado: $30K/anual (licencias) + $15K (integracion)
- Tiempo estimado: 2 semanas

### 6.2 Recomendacion

**Opcion seleccionada**: Opcion 1 - Desarrollo interno

**Justificacion:**
1. **Valor**: ROI positivo en 12 meses ($60K vs alternativas recurrentes)
2. **Viabilidad**: Codigo base authentication/ ya existe, solo requiere extension
3. **Riesgo**: Control total de datos sensibles, cumple restricciones IACT (NO email, sesiones en BD)
4. **Estrategico**: Capacidad de customizacion total segun necesidades futuras
5. **Compliance**: Alineado con arquitectura existente y restricciones tecnicas

---

## 7. Roadmap de Implementacion

### 7.1 Fases Propuestas

| Fase | Descripcion | Duracion | Dependencias |
|------|-------------|----------|--------------|
| Fase 1 | Login con JWT + bloqueo intentos fallidos | 2 semanas | ninguna |
| Fase 2 | Sesion unica + recuperacion password | 2 semanas | Fase 1 |
| Fase 3 | Cierre por inactividad + auditoria completa | 1 semana | Fase 2 |
| Fase 4 | Frontend + notificaciones buzon interno | 1 semana | Fase 3 |

### 7.2 Hitos Principales

- Hito 1: Login con JWT y bloqueo funcionando en DEV - 2025-11-20
- Hito 2: Sesion unica validada en STAGING - 2025-12-04
- Hito 3: Auditoria completa verificada en STAGING - 2025-12-11
- Hito 4: Sistema completo en PRODUCCION - 2025-12-18

---

## 8. Derivacion a Requisitos

Esta necesidad se descompone en los siguientes requisitos:

### 8.1 Requisitos de Negocio (Business Requirements)

- RN-001: Sistema de autenticacion seguro con prevencion de fraude

### 8.2 Requisitos de Stakeholders

- RS-001: Auditoria requiere trazabilidad completa de accesos
- RS-002: Usuarios requieren acceso rapido (menor 2 segundos)

### 8.3 Requisitos Funcionales

Backend:
- RF-001: Login con credenciales username/password
- RF-002: Generacion de tokens JWT (access 15min, refresh 7dias)
- RF-003: Bloqueo automatico tras 5 intentos fallidos en 5 minutos
- RF-004: Sesion unica con cierre de sesiones previas
- RF-005: Logout manual con invalidacion de tokens
- RF-006: Recuperacion de password sin email (3 preguntas seguridad)

Frontend:
- RF-010: Pantalla de login con validaciones
- RF-011: Pantalla de cambio de password

Infrastructure:
- RF-020: CPython 3.12.6 precompilado en Dev Container

### 8.4 Requisitos No Funcionales

Backend:
- RNF-001: Tiempo de respuesta login menor 2 segundos (P95)
- RNF-002: Sesiones almacenadas en MySQL (NO Redis)

Infrastructure:
- RNF-020: Disponibilidad del sistema 99.9% uptime

---

## 9. Trazabilidad

### 9.1 Trazabilidad Upward (Origen)

Esta necesidad esta alineada con:

- Objetivo estrategico: OE-2025-SEC - Fortalecer seguridad de plataformas criticas
- Iniciativa corporativa: INIT-SECURITY-2025 - Programa de ciberseguridad
- Business case: BC-AUTH-001 - Inversion en autenticacion robusta

### 9.2 Trazabilidad Downward (Derivados)

Esta necesidad genera:

- Requisitos de negocio: RN-001
- Requisitos de stakeholders: RS-001, RS-002
- Requisitos funcionales: RF-001, RF-002, RF-003, RF-004, RF-005, RF-006, RF-010, RF-011, RF-020
- Requisitos no funcionales: RNF-001, RNF-002, RNF-020
- Proyectos/Iniciativas: PROJ-AUTH-2025 - Implementacion autenticacion robusta
- Entregables: Sistema autenticacion, UI login, Notificaciones buzon interno

---

## 10. Riesgos Identificados

| ID | Riesgo | Probabilidad | Impacto | Mitigacion |
|----|--------|--------------|---------|------------|
| R-01 | Usuarios rechazan sesion unica por cambio de habitos | media | medio | Training proactivo + comunicacion clara + periodo de adaptacion |
| R-02 | Performance degradada por validaciones adicionales | baja | alto | Arquitectura async, caching estrategico, benchmarking continuo |
| R-03 | Bloqueos falsos positivos por comparticion legitima | media | medio | Mecanismo de desbloqueo admin + notificaciones proactivas |
| R-04 | Equipo no tiene expertise en seguridad avanzada | media | medio | Consultoria externa para revision + training interno |

---

## 11. Aprobaciones

| Rol | Nombre | Fecha | Firma/Aprobacion |
|-----|--------|-------|------------------|
| Sponsor | Director Operaciones | 2025-11-06 | Aprobado |
| BA Lead | Business Analyst Lead | 2025-11-06 | Aprobado |
| PMO | PMO Manager | 2025-11-06 | Aprobado |
| Tech Lead | Backend Tech Lead | 2025-11-06 | Revisado |

---

## 12. Referencias

### 12.1 Documentos Relacionados

- Codigo existente: api/callcentersite/callcentersite/apps/authentication/
- Codigo existente: api/callcentersite/callcentersite/apps/users/
- Restricciones IACT: implementacion/backend/requisitos/restricciones_y_lineamientos.md

### 12.2 Estandares Aplicados

- BABOK v3: Knowledge Area - Business Analysis Planning and Monitoring
- ISO/IEC/IEEE 29148:2018: Clause 6.2 - Business Analysis Process
- PMBOK Guide 7th Ed: Principle-Based Approach to Project Management
- OWASP ASVS v4.0: Authentication Verification Requirements
- ISO/IEC 27001:2013: Information Security Management

---

## Control de Cambios

| Version | Fecha | Autor | Descripcion del Cambio |
|---------|-------|-------|------------------------|
| 1.0 | 2025-11-06 | BA Team | Creacion inicial basada en codigo authentication/ existente |

---

Notas:
- Esta necesidad se basa en codigo REAL en api/callcentersite/callcentersite/apps/authentication/
- Cumple TODAS las restricciones IACT (NO email, sesiones en MySQL, BD IVR readonly)
- Derivacion completa a requisitos de negocio, stakeholders, funcionales y no funcionales
- Trazabilidad bidireccional completa
