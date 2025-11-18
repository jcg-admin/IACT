-- Script de validacion: Grupos de permisos creados
-- Valida que los grupos tienen las capacidades correctas asignadas
--
-- Referencia: docs/PLAN_MAESTRO_PRIORIDAD_02.md (Tarea 87)
--
-- Uso: psql -d iact_analytics -f scripts/validacion/validar_grupos.sql

\echo '============================================'
\echo 'VALIDACION: Grupos de Permisos'
\echo '============================================'
\echo ''

-- 1. Listar grupos con conteo de capacidades
\echo '1. Grupos creados con conteo de capacidades:'
\echo '   Esperado:'
\echo '     - administracion_usuarios (7 caps)'
\echo '     - visualizacion_basica (4 caps)'
\echo '     - configuracion_sistema (5 caps)'
\echo ''

SELECT
    gp.codigo AS grupo_codigo,
    gp.nombre AS grupo_nombre,
    gp.categoria,
    gp.nivel_riesgo,
    COUNT(gc.id) AS total_capacidades,
    CASE
        WHEN gp.codigo = 'administracion_usuarios' THEN 7
        WHEN gp.codigo = 'visualizacion_basica' THEN 4
        WHEN gp.codigo = 'configuracion_sistema' THEN 5
        ELSE 0
    END AS capacidades_esperadas,
    CASE
        WHEN gp.codigo = 'administracion_usuarios' AND COUNT(gc.id) = 7 THEN 'OK ✓'
        WHEN gp.codigo = 'visualizacion_basica' AND COUNT(gc.id) = 4 THEN 'OK ✓'
        WHEN gp.codigo = 'configuracion_sistema' AND COUNT(gc.id) = 5 THEN 'OK ✓'
        WHEN gp.codigo IN ('administracion_usuarios', 'visualizacion_basica', 'configuracion_sistema') THEN 'ERROR ✗'
        ELSE 'N/A'
    END AS estado
FROM grupos_permisos gp
LEFT JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
GROUP BY gp.id, gp.codigo, gp.nombre, gp.categoria, gp.nivel_riesgo
ORDER BY gp.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 2. Detalle de capacidades por grupo: administracion_usuarios
\echo '2. Capacidades del grupo ADMINISTRACION_USUARIOS (7):'
\echo ''

SELECT
    c.codigo,
    c.nombre,
    c.nivel_riesgo
FROM grupos_permisos gp
JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
JOIN capacidades c ON gc.capacidad_id = c.id
WHERE gp.codigo = 'administracion_usuarios'
ORDER BY c.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 3. Detalle de capacidades por grupo: visualizacion_basica
\echo '3. Capacidades del grupo VISUALIZACION_BASICA (4):'
\echo ''

SELECT
    c.codigo,
    c.nombre,
    c.nivel_riesgo
FROM grupos_permisos gp
JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
JOIN capacidades c ON gc.capacidad_id = c.id
WHERE gp.codigo = 'visualizacion_basica'
ORDER BY c.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 4. Detalle de capacidades por grupo: configuracion_sistema
\echo '4. Capacidades del grupo CONFIGURACION_SISTEMA (5):'
\echo ''

SELECT
    c.codigo,
    c.nombre,
    c.nivel_riesgo
FROM grupos_permisos gp
JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
JOIN capacidades c ON gc.capacidad_id = c.id
WHERE gp.codigo = 'configuracion_sistema'
ORDER BY c.codigo;

\echo ''
\echo '--------------------------------------------'
\echo ''

-- 5. Validar que no hay duplicados
\echo '5. Validar duplicados en asignaciones grupo-capacidad:'
\echo ''

SELECT
    gp.codigo AS grupo,
    c.codigo AS capacidad,
    COUNT(*) AS veces_asignada
FROM grupos_permisos gp
JOIN grupo_capacidades gc ON gp.id = gc.grupo_id
JOIN capacidades c ON gc.capacidad_id = c.id
GROUP BY gp.codigo, c.codigo
HAVING COUNT(*) > 1;

\echo ''
\echo '   (Si no hay resultados, no hay duplicados - OK)'
\echo ''

\echo '--------------------------------------------'
\echo ''

-- 6. Listar todos los grupos con sus categorias
\echo '6. Todos los grupos funcionales del sistema:'
\echo ''

SELECT
    codigo,
    nombre,
    categoria,
    nivel_riesgo,
    activo
FROM grupos_permisos
ORDER BY categoria, codigo;

\echo ''
\echo '============================================'
\echo 'FIN DE VALIDACION'
\echo '============================================'
