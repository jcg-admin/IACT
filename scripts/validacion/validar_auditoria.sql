-- Script de validacion: Verificar que auditoria se registra correctamente
-- Valida que todas las acciones criticas se auditan
--
-- Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 89)
--
-- Uso: psql -d iact_analytics -f scripts/validacion/validar_auditoria.sql

\echo '============================================'
\echo 'VALIDACION: Sistema de Auditoria'
\echo '============================================'
\echo ''

-- 1. Resumen de registros de auditoria
\echo '1. Resumen de registros de auditoria por resultado:'
\echo ''

SELECT
    resultado,
    COUNT(*) AS total_registros,
    COUNT(DISTINCT usuario_id) AS usuarios_unicos,
    COUNT(DISTINCT capacidad_codigo) AS capacidades_usadas
FROM auditoria_permisos
GROUP BY resultado
ORDER BY resultado;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 2. Top 10 acciones mas auditadas
\echo '2. Top 10 acciones mas auditadas:'
\echo ''

SELECT
    accion,
    COUNT(*) AS total,
    COUNT(CASE WHEN resultado = 'permitido' THEN 1 END) AS permitidas,
    COUNT(CASE WHEN resultado = 'denegado' THEN 1 END) AS denegadas
FROM auditoria_permisos
GROUP BY accion
ORDER BY total DESC
LIMIT 10;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 3. Top 10 capacidades mas utilizadas
\echo '3. Top 10 capacidades mas utilizadas:'
\echo ''

SELECT
    capacidad_codigo,
    COUNT(*) AS total_usos,
    COUNT(CASE WHEN resultado = 'permitido' THEN 1 END) AS permitidos,
    COUNT(CASE WHEN resultado = 'denegado' THEN 1 END) AS denegados,
    ROUND(100.0 * COUNT(CASE WHEN resultado = 'permitido' THEN 1 END) / COUNT(*), 2) AS porcentaje_exito
FROM auditoria_permisos
WHERE capacidad_codigo IS NOT NULL
GROUP BY capacidad_codigo
ORDER BY total_usos DESC
LIMIT 10;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 4. Validar que acciones de creacion se auditan
\echo '4. Acciones de creacion de usuarios (debe tener registros):'
\echo ''

SELECT
    usuario_id,
    capacidad_codigo,
    accion,
    resultado,
    timestamp,
    SUBSTRING(detalles, 1, 50) AS detalles_preview
FROM auditoria_permisos
WHERE capacidad_codigo = 'sistema.administracion.usuarios.crear'
  AND accion = 'crear'
ORDER BY timestamp DESC
LIMIT 10;

\echo ''
\echo '   Total de auditorias de creacion de usuarios:'

SELECT COUNT(*) AS total
FROM auditoria_permisos
WHERE capacidad_codigo = 'sistema.administracion.usuarios.crear'
  AND accion = 'crear';

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 5. Validar que acciones de suspension se auditan
\echo '5. Acciones de suspension de usuarios (debe tener registros):'
\echo ''

SELECT
    usuario_id,
    capacidad_codigo,
    accion,
    resultado,
    timestamp,
    SUBSTRING(detalles, 1, 50) AS detalles_preview
FROM auditoria_permisos
WHERE capacidad_codigo = 'sistema.administracion.usuarios.suspender'
  AND accion = 'suspender'
ORDER BY timestamp DESC
LIMIT 10;

\echo ''
\echo '   Total de auditorias de suspension:'

SELECT COUNT(*) AS total
FROM auditoria_permisos
WHERE capacidad_codigo = 'sistema.administracion.usuarios.suspender';

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 6. Validar que acciones denegadas se auditan
\echo '6. Acciones denegadas (intentos sin permiso):'
\echo ''

SELECT
    usuario_id,
    capacidad_codigo,
    accion,
    recurso_tipo,
    timestamp,
    SUBSTRING(razon, 1, 60) AS razon_preview
FROM auditoria_permisos
WHERE resultado = 'denegado'
ORDER BY timestamp DESC
LIMIT 10;

\echo ''
\echo '   Total de acciones denegadas:'

SELECT COUNT(*) AS total
FROM auditoria_permisos
WHERE resultado = 'denegado';

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 7. Ultimos 20 registros de auditoria
\echo '7. Ultimos 20 registros de auditoria:'
\echo ''

SELECT
    timestamp,
    usuario_id,
    capacidad_codigo,
    accion,
    resultado,
    recurso_tipo,
    recurso_id
FROM auditoria_permisos
ORDER BY timestamp DESC
LIMIT 20;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 8. Validar tipos de recursos auditados
\echo '8. Tipos de recursos auditados:'
\echo ''

SELECT
    recurso_tipo,
    COUNT(*) AS total_registros,
    COUNT(DISTINCT recurso_id) AS recursos_unicos
FROM auditoria_permisos
WHERE recurso_tipo IS NOT NULL
GROUP BY recurso_tipo
ORDER BY total_registros DESC;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 9. Estadisticas por usuario
\echo '9. Top 5 usuarios con mas actividad auditada:'
\echo ''

SELECT
    usuario_id,
    COUNT(*) AS total_acciones,
    COUNT(CASE WHEN resultado = 'permitido' THEN 1 END) AS exitosas,
    COUNT(CASE WHEN resultado = 'denegado' THEN 1 END) AS denegadas,
    MIN(timestamp) AS primera_accion,
    MAX(timestamp) AS ultima_accion
FROM auditoria_permisos
GROUP BY usuario_id
ORDER BY total_acciones DESC
LIMIT 5;

\echo ''
\echo '============================================'
\echo 'FIN DE VALIDACION'
\echo '============================================'
