---
id: DOC-VISION-ALCANCE
tipo: vision
estado: activo
propietario: equipo-producto
ultima_actualizacion: 2025-11-06
---
# Vision y Alcance - Proyecto IACT

## Vision del Proyecto

IACT (IVR Analytics & Customer Tracking) es un sistema de analytics para call center que proporciona visibilidad de metricas operativas del IVR en tiempo casi real.

## Proposito del Sistema

Reducir el lag de datos de 12-24 horas a 6-12 horas mediante un sistema ETL batch que alimenta un dashboard con 10 widgets clave.

## Problema de Negocio

### Situacion Actual
- Datos IVR retrasados 12-24 horas
- Reportes manuales requieren 10-15 horas/semana
- Deteccion de problemas en 8-12 horas
- Toma de decisiones sin datos actuales

### Impacto
- Perdida de oportunidades de correccion temprana
- Tiempo desperdiciado en reporteo manual
- Decisiones basadas en datos obsoletos

## Solucion Propuesta

### Sistema IACT
Dashboard operativo con:
- ETL batch cada 6-12 horas
- 10 widgets de metricas clave
- Reportes automatizados (CSV/Excel/PDF)
- Sistema de alertas via inbox interno
- Base de datos IVR read-only (cero escrituras)

### Beneficios Esperados
- 80% reduccion en tiempo de reporteo manual
- Deteccion de problemas <1 hora
- Datos actualizados 2x dia
- Toma de decisiones basada en datos frescos

## Alcance del Proyecto

### Dentro del Alcance (In Scope)

#### Backend
- API REST Django + DRF
- ETL batch (Python)
- Base de datos Analytics (MySQL)
- Consultas read-only a BD IVR
- Sistema de autenticacion local (sin LDAP)
- Sesiones en MySQL (sin Redis)

#### Frontend
- Dashboard React con 10 widgets
- Reportes descargables (CSV/Excel/PDF)
- Alertas via inbox interno
- Responsive design

#### Infrastructure
- DevContainer con CPython precompilado
- CI/CD basico
- Vagrant para build systems

### Fuera del Alcance (Out of Scope)

- Email notifications (usar inbox interno)
- Tiempo real (<1 minuto lag)
- Escrituras a BD IVR
- Integracion LDAP/Active Directory
- Redis para cache/sessions
- Analisis predictivo avanzado
- Machine learning
- Aplicacion movil nativa

## Stakeholders

### Primarios
- Gerentes de call center
- Supervisores operativos
- Analistas de metricas

### Secundarios
- Equipo IT
- Equipo desarrollo
- Auditoria

## Restricciones IACT

1. Sin emojis en codigo/documentacion
2. Python para scripts (NO JavaScript excepto frontend)
3. Sin Redis (sesiones en MySQL)
4. Sin email (solo inbox interno)
5. BD IVR read-only (cero escrituras)
6. ETL batch cada 6-12h (NO tiempo real)

## Metricas de Exito

| Metrica | Baseline | Target |
|---------|----------|--------|
| Lag de datos | 12-24h | 6-12h |
| Tiempo reporteo manual | 10-15h/semana | <3h/semana |
| Deteccion problemas | 8-12h | <1h |
| Disponibilidad sistema | N/A | >99% |

## Cronograma Alto Nivel

- Fase 1: Infraestructura (COMPLETADO)
- Fase 2: Backend API (En progreso)
- Fase 3: Frontend Dashboard (En progreso)
- Fase 4: ETL y Reportes (Pendiente)
- Fase 5: Testing y QA (Pendiente)
- Fase 6: Deployment (Pendiente)

## Referencias

- docs/implementacion/backend/requisitos/necesidades/n001_visibilidad_metricas_ivr_tiempo_real.md
- ADR_010: Organizacion por Dominio
- ISO/IEC/IEEE 29148:2018
