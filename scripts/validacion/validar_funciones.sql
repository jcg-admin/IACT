-- Script de validacion: Funciones y capacidades insertadas
-- Valida que todas las funciones de PRIORIDAD 2 estan insertadas
-- con el numero correcto de capacidades
--
-- Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 86)
--
-- Uso: psql -d iact_analytics -f scripts/validacion/validar_funciones.sql

\echo '============================================'
\echo 'VALIDACION: Funciones y Capacidades'
\echo '============================================'
\echo ''

-- 1. Listar funciones con conteo de capacidades
\echo '1. Funciones insertadas con conteo de capacidades:'
\echo '   Esperado: usuarios (7), dashboards (4), configuracion (5)'
\echo ''

SELECT
    f.nombre AS funcion,
    f.nombre_completo,
    COUNT(DISTINCT c.id) AS total_capacidades,
    STRING_AGG(DISTINCT c.codigo, ', ' ORDER BY c.codigo) AS capacidades
FROM funciones f
LEFT JOIN funcion_capacidades fc ON f.id = fc.funcion_id
LEFT JOIN capacidades c ON fc.capacidad_id = c.id
WHERE f.nombre IN ('usuarios', 'dashboards', 'configuracion')
GROUP BY f.id, f.nombre, f.nombre_completo
ORDER BY f.nombre;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 2. Validar capacidades especificas de usuarios
\echo '2. Capacidades de funcion USUARIOS (debe tener 7):'
\echo ''

SELECT
    c.codigo,
    c.nombre,
    c.nivel_riesgo,
    c.requiere_aprobacion
FROM capacidades c
WHERE c.codigo LIKE 'sistema.administracion.usuarios.%'
ORDER BY c.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 3. Validar capacidades especificas de dashboards
\echo '3. Capacidades de funcion DASHBOARDS (debe tener 4):'
\echo ''

SELECT
    c.codigo,
    c.nombre,
    c.nivel_riesgo,
    c.requiere_aprobacion
FROM capacidades c
WHERE c.codigo LIKE 'sistema.vistas.dashboards.%'
ORDER BY c.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 4. Validar capacidades especificas de configuracion
\echo '4. Capacidades de funcion CONFIGURACION (debe tener 5):'
\echo ''

SELECT
    c.codigo,
    c.nombre,
    c.nivel_riesgo,
    c.requiere_aprobacion
FROM capacidades c
WHERE c.codigo LIKE 'sistema.tecnico.configuracion.%'
ORDER BY c.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 5. Resumen de validacion
\echo '5. Resumen de validacion:'
\echo ''

WITH conteos AS (
    SELECT
        CASE
            WHEN c.codigo LIKE 'sistema.administracion.usuarios.%' THEN 'usuarios'
            WHEN c.codigo LIKE 'sistema.vistas.dashboards.%' THEN 'dashboards'
            WHEN c.codigo LIKE 'sistema.tecnico.configuracion.%' THEN 'configuracion'
        END AS funcion,
        COUNT(*) AS total
    FROM capacidades c
    WHERE c.codigo LIKE 'sistema.administracion.usuarios.%'
       OR c.codigo LIKE 'sistema.vistas.dashboards.%'
       OR c.codigo LIKE 'sistema.tecnico.configuracion.%'
    GROUP BY funcion
)
SELECT
    funcion,
    total AS capacidades_encontradas,
    CASE funcion
        WHEN 'usuarios' THEN 7
        WHEN 'dashboards' THEN 4
        WHEN 'configuracion' THEN 5
    END AS capacidades_esperadas,
    CASE
        WHEN funcion = 'usuarios' AND total = 7 THEN 'OK ✓'
        WHEN funcion = 'dashboards' AND total = 4 THEN 'OK ✓'
        WHEN funcion = 'configuracion' AND total = 5 THEN 'OK ✓'
        ELSE 'ERROR ✗'
    END AS estado
FROM conteos
ORDER BY funcion;

\echo ''
\echo '============================================'
\echo 'FIN DE VALIDACION'
\echo '============================================'
